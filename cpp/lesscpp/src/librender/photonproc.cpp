
#include <mitsuba/core/statistics.h>
#include <mitsuba/render/photonproc.h>
#include <mitsuba/render/medium.h>
#include <mitsuba/render/phase.h>
#include <mitsuba/render/range.h>

MTS_NAMESPACE_BEGIN

PhotonProcess::PhotonProcess(EMode mode, size_t workCount, size_t granularity,
	const std::string &progressText, const void *progressReporterPayload)
	: m_mode(mode), m_workCount(workCount), m_numGenerated(0),
	m_granularity(granularity), m_receivedResultCount(0) {

	/* Choose a suitable work unit granularity if none was specified */
	if (m_granularity == 0)
		m_granularity = std::max((size_t)1, workCount /
		(16 * Scheduler::getInstance()->getWorkerCount()));

	/* Create a visual progress reporter */
	m_progress = new ProgressReporter(progressText, workCount,
		progressReporterPayload);
	m_resultMutex = new Mutex();
}

PhotonProcess::~PhotonProcess() {
	delete m_progress;
}

PhotonProcess::EStatus PhotonProcess::generateWork(WorkUnit *unit, int worker) {
	RangeWorkUnit *range = static_cast<RangeWorkUnit*>(unit);
	size_t workUnitSize;
	if (m_mode == ETrace) {
		if (m_numGenerated == m_workCount)
			return EFailure;
		workUnitSize = std::min(m_granularity, m_workCount - m_numGenerated);
	}
	else {
		if (m_receivedResultCount >= m_workCount)
			return EFailure;
		workUnitSize = m_granularity;
	}
	range->setRange(m_numGenerated, m_numGenerated + workUnitSize - 1);
	m_numGenerated += workUnitSize;
	return ESuccess;
}

void PhotonProcess::increaseResultCount(size_t resultCount) {
	LockGuard lock(m_resultMutex);
	m_receivedResultCount += resultCount;
	m_progress->update(m_receivedResultCount);
}


PhotonTracer::PhotonTracer(int maxDepth, int rrDepth, bool emissionEvents)
	: m_maxDepth(maxDepth), m_rrDepth(rrDepth), m_emissionEvents(emissionEvents) { }

PhotonTracer::PhotonTracer(Stream *stream, InstanceManager *manager)
	: WorkProcessor(stream, manager) {

	m_maxDepth = stream->readInt();
	m_rrDepth = stream->readInt();
	m_emissionEvents = stream->readBool();
}

void PhotonTracer::serialize(Stream *stream, InstanceManager *manager) const {
	stream->writeInt(m_maxDepth);
	stream->writeInt(m_rrDepth);
	stream->writeBool(m_emissionEvents);
}

ref<WorkUnit> PhotonTracer::createWorkUnit() const {
	return new RangeWorkUnit();
}

void PhotonTracer::prepare() {
	Scene *scene = static_cast<Scene *>(getResource("scene"));
	m_scene = new Scene(scene);
	m_sampler = static_cast<Sampler *>(getResource("sampler"));
	Sensor *newSensor = static_cast<Sensor *>(getResource("sensor"));
	m_scene->removeSensor(scene->getSensor());
	m_scene->addSensor(newSensor);
	m_scene->setSensor(newSensor);
	m_scene->initializeBidirectional();
}

//采用随机分布
void PhotonTracer::process(const WorkUnit *workUnit, WorkResult *workResult,
	const bool &stop) {

	const RangeWorkUnit *range = static_cast<const RangeWorkUnit *>(workUnit);
	Intersection its;
	ref<Sensor> sensor = m_scene->getSensor();
	PositionSamplingRecord pRec(sensor->getShutterOpen()
		+ 0.5f * sensor->getShutterOpenTime());
	m_sampler->generate(Point2i(0));
	//std::ofstream out("out.txt", std::ios::app);
	for (size_t index = range->getRangeStart(); index <= range->getRangeEnd() && !stop; ++index) {
		m_sampler->setSampleIndex(index);

		const Emitter *emitter = NULL;
		const Medium *medium;
		Spectrum power;
		Ray ray;
		power = m_scene->sampleEmitterRay(ray, emitter,
			m_sampler->next2D(), m_sampler->next2D(), pRec.time);
		medium = emitter->getMedium();
	//	out << ray.o.x << " " << ray.o.z << " " << ray.o.y << endl;

		int depth = 1, nullInteractions = 0;
		bool delta = false;
		Point previousPoint = Point(std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity());

		Spectrum throughput(1.0f); // unitless path throughput (used for russian roulette)
		while (!throughput.isZero() && (depth <= m_maxDepth || m_maxDepth < 0)) {
			m_scene->rayIntersect(ray, its);

			
			if (its.t == std::numeric_limits<Float>::infinity()) {
				/* There is no surface in this direction */
				//Float near, far;
				//aabb.rayIntersect(ray, near, far);
				//Point farPoint = ray.o + far*ray.d;
				//if (farPoint.y < aabb.max.y && farPoint.y > aabb.min.y) {

				//}
				handleSurfaceInteractionExt(depth, nullInteractions, delta, its, previousPoint, medium, throughput*power);
				break;
			}
			else {
				//处理BRDF
				const BSDF *bsdf = its.getBSDF();
				BSDFSamplingRecord bRec(its, m_sampler, EImportance);
				Spectrum bsdfWeight = bsdf->sample(bRec, m_sampler->next2D()); //bsdfWeight: 方向反射率

				if (bsdfWeight == Spectrum(-1)) {// -1表示碰撞点位于单面材质的背面
					if (depth == 1) {
						break;
					}
					else {//多次散射时，如果碰到了底面，则停止
						its.t = std::numeric_limits<Float>::infinity();
						handleSurfaceInteractionExt(depth, nullInteractions, delta, its, previousPoint, medium, throughput*power);
						break;
					}
				}
				handleSurfaceInteractionExt(depth, nullInteractions, delta, its, previousPoint, medium, throughput*power);

				if (bsdfWeight.isZero()) {
					break;
				}
					
				throughput *= bsdfWeight;
				Vector wo = its.toWorld(bRec.wo);
				ray.setOrigin(its.p);
				ray.setDirection(wo);
				ray.mint = Epsilon;

				previousPoint = its.p;

				if (depth++ >= m_rrDepth) { //当深度超过了设置的最小深度时，采用Russian roulette方法决定是否停止
					Float q = std::min(throughput.max(), (Float) 0.95f);
					if (m_sampler->next1D() >= q)
						break;
					throughput /= q;
				}
			}
		}
	}

	//out.close();

}

#ifdef _SHOW_
//主要处理过程 执行光子跟踪
void PhotonTracer::process(const WorkUnit *workUnit, WorkResult *workResult,
	const bool &stop) {

	const RangeWorkUnit *range = static_cast<const RangeWorkUnit *>(workUnit);
	Intersection its;
	ref<Sensor> sensor = m_scene->getSensor();
	PositionSamplingRecord pRec(sensor->getShutterOpen()
		+ 0.5f * sensor->getShutterOpenTime());
	m_sampler->generate(Point2i(0));

	Float sunRayResolution = m_scene->getIntegrator()->getProperties().getFloat("sunRayResolution", 0.05);

	Float invert_resolutin = 1 / sunRayResolution;
	AABB aabb = m_scene->getKDTree()->getAABB();
	Point2 scene_min = Point2(aabb.min.x >= 0 ? std::ceil(aabb.min.x) : std::floor(aabb.min.x),
		aabb.min.z >= 0 ? std::ceil(aabb.min.z) : std::floor(aabb.min.z));
	Point2 scene_max = Point2(aabb.max.x >= 0 ? std::ceil(aabb.max.x) : std::floor(aabb.max.x),
		aabb.max.z >= 0 ? std::ceil(aabb.max.z) : std::floor(aabb.max.z));
	Vector2 extent = scene_max - scene_min;
	size_t N = static_cast<size_t>(invert_resolutin *invert_resolutin * extent.x*extent.y);
	size_t w = static_cast<size_t>(extent.x * invert_resolutin);
	size_t h = static_cast<size_t>(extent.y * invert_resolutin);

	Ray ray;
	const Emitter *emitter = NULL;
	m_scene->sampleEmitterRay(ray, emitter,Point2(-1), Point2(-1), pRec.time);
	Float distance = aabb.getExtents().y/dot(ray.d, Vector(0, -1, 0));
	Vector displacementVec = -ray.d*distance;

	for (size_t index = range->getRangeStart(); index <= range->getRangeEnd() && !stop; ++index) {
		m_sampler->setSampleIndex(index);

		size_t row = index / w;
		size_t col = index - row*w;

		const Emitter *emitter = NULL;
		const Medium *medium;
		Spectrum power;
		Ray ray;
		power = m_scene->sampleEmitterRay(ray, emitter,
			m_sampler->next2D(), m_sampler->next2D(), pRec.time);

		ray.o.z = scene_max.y - (row + 0.5)*sunRayResolution + displacementVec.z;
		ray.o.x = scene_max.x - (col + 0.5)*sunRayResolution + displacementVec.x;

		medium = emitter->getMedium();

		int depth = 1, nullInteractions = 0;
		bool delta = false;
		Spectrum throughput(1.0f); // unitless path throughput (used for russian roulette)
		m_scene->rayIntersectAll(ray, its);
		if (its.t == std::numeric_limits<Float>::infinity()) {
			/* There is no surface in this direction */
			Float near, far;
			aabb.rayIntersect(ray, near, far);
			Point farPoint = ray.o + far*ray.d;
			if (farPoint.y < aabb.max.y && farPoint.y > aabb.min.y) {

			}
		}
		else {
			/* Forward the surface scattering event to the attached handler */
			handleSurfaceInteraction(depth, nullInteractions, delta, its, medium, throughput*power);
			
		}
		
	}

}
#endif

void PhotonTracer::handleEmission(const PositionSamplingRecord &pRec,
	const Medium *medium, const Spectrum &weight) { }

void PhotonTracer::handleNewParticle() { }

void PhotonTracer::handleSurfaceInteraction(int depth, int nullInteractions,
	bool delta, const Intersection &its, const Medium *medium,
	const Spectrum &weight) {
}

void PhotonTracer::handleSurfaceInteractionExt(int depth, int nullInteractions,
	bool delta, const Intersection &its, Point &previousPoint, const Medium *medium,
	const Spectrum &weight) {};

void PhotonTracer::handleMediumInteraction(int depth, int nullInteractions,
	bool delta, const MediumSamplingRecord &mRec, const Medium *medium,
	const Vector &wi, const Spectrum &weight) { }

//MTS_IMPLEMENT_CLASS(RangeWorkUnit, false, WorkUnit) //在Particleproc.cpp中已经实现了，所以此处不需要重复定义了
MTS_IMPLEMENT_CLASS(PhotonProcess, true, ParallelProcess)
MTS_IMPLEMENT_CLASS(PhotonTracer, true, WorkProcessor)

MTS_NAMESPACE_END

