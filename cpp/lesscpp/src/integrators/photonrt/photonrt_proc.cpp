
#include "photonrt_proc.h"
#include <mitsuba/core/plugin.h>

MTS_NAMESPACE_BEGIN
/* ==================================================================== */
/*                           Work result impl.                          */
/* ==================================================================== */
void CapturePhotonWorkResult::load(Stream *stream) {
	size_t nEntries = (size_t)m_size.x * (size_t)m_size.y;
	stream->readFloatArray(reinterpret_cast<Float *>(m_bitmap->getFloatData()),
		nEntries * SPECTRUM_SAMPLES);
	m_range->load(stream);
	m_PhtonsEachProcess = stream->readSize();
}

void CapturePhotonWorkResult::save(Stream *stream) const {
	size_t nEntries = (size_t)m_size.x * (size_t)m_size.y;
	stream->writeFloatArray(reinterpret_cast<const Float *>(m_bitmap->getFloatData()),
		nEntries * SPECTRUM_SAMPLES);
	m_range->save(stream);
	stream->writeSize(m_PhtonsEachProcess);
}


/* ==================================================================== */
/*                         Work processor impl.                         */
/* ==================================================================== */
CapturePhotonWorker::CapturePhotonWorker(Stream *stream, InstanceManager *manager)
	: PhotonTracer(stream, manager) {
	m_maxPathDepth = stream->readInt();
	m_bruteForce = stream->readBool();
}

void CapturePhotonWorker::serialize(Stream *stream, InstanceManager *manager) const {
	PhotonTracer::serialize(stream, manager);
	stream->writeInt(m_maxPathDepth);
	stream->writeBool(m_bruteForce);
}

void CapturePhotonWorker::prepare() {
	PhotonTracer::prepare();
	m_sensor = static_cast<Sensor *>(getResource("sensor"));
	m_rfilter = m_sensor->getFilm()->getReconstructionFilter();
	m_subSceneUpperLeft = Vector2(m_scene->getIntegrator()->getProperties().getFloat("subSceneXSize", 100)*0.5,
		m_scene->getIntegrator()->getProperties().getFloat("subSceneZSize", 100)*0.5);
	m_filmSize = m_sensor->getFilm()->getSize();
}

ref<WorkProcessor> CapturePhotonWorker::clone() const {
	return new CapturePhotonWorker(m_maxDepth,
		m_maxPathDepth, m_rrDepth, m_bruteForce);
}

ref<WorkResult> CapturePhotonWorker::createWorkResult() const {
	const Film *film = m_sensor->getFilm();
	return new CapturePhotonWorkResult(film->getCropSize(), m_rfilter.get());
}

void CapturePhotonWorker::process(const WorkUnit *workUnit, WorkResult *workResult,
	const bool &stop) {
	const RangeWorkUnit *range = static_cast<const RangeWorkUnit *>(workUnit);
	m_workResult = static_cast<CapturePhotonWorkResult *>(workResult);
	m_workResult->setRangeWorkUnit(range);
	m_workResult->clear();
	//每次开始前，需要清空前一次的结果
	m_workResult->m_downwellingWorkResult->clear();
	m_workResult->m_upwellingWorkResult->clear();
	m_workResult->m_PhtonsEachProcess = 0;
	PhotonTracer::process(workUnit, workResult, stop);
	m_workResult = NULL;
}

void CapturePhotonWorker::handleEmission(const PositionSamplingRecord &pRec,
	const Medium *medium, const Spectrum &weight) {
	if (m_bruteForce)
		return;

	DirectSamplingRecord dRec(pRec.p, pRec.time);
	int maxInteractions = m_maxPathDepth - 1;

	/* Create a dummy intersection to ensure that sampleAttenuatedSensorDirect()
	treats the light source vertex as being located on a surface */
	Intersection its;
	its.p = pRec.p;

	Spectrum value = weight * m_scene->sampleAttenuatedSensorDirect(
		dRec, its, medium, maxInteractions, m_sampler->next2D(), m_sampler);

	if (value.isZero())
		return;

	const Emitter *emitter = static_cast<const Emitter *>(pRec.object);
	value *= emitter->evalDirection(DirectionSamplingRecord(dRec.d), pRec);

	/* Splat onto the accumulation buffer */
	m_workResult->put(dRec.uv, (Float *)&value[0]);
}

void CapturePhotonWorker::handleSurfaceInteraction(int depth, int nullInteractions,
	bool caustic, const Intersection &its, const Medium *medium,
	const Spectrum &weight) {

	if (m_bruteForce || (depth >= m_maxPathDepth && m_maxPathDepth > 0))
		return;

	int maxInteractions = m_maxPathDepth - depth - 1;

	Vector2 relDist = m_subSceneUpperLeft - Vector2(its.p.x, its.p.z);
	Point2 uv = Point2(m_filmSize.x *relDist.x / (m_subSceneUpperLeft.x * 2), m_filmSize.y * relDist.y / (m_subSceneUpperLeft.y * 2));

	Spectrum re = weight;

	m_workResult->m_downwellingWorkResult->put(uv, (Float *) (&re[0]));
	m_workResult->m_PhtonsEachProcess++;
}

//扩展版本，可以得到上一个交点的信息
void CapturePhotonWorker::handleSurfaceInteractionExt(int depth, int nullInteractions,
	bool delta, const Intersection &its, Point &previousPoint, const Medium *medium,
	const Spectrum &weight) {
	
	if (m_bruteForce || (depth >= m_maxPathDepth && m_maxPathDepth > 0))
		return;

	int maxInteractions = m_maxPathDepth - depth - 1;

    //1. 第一次直接入射 如果没有交点，那么就直接结束
	if (its.t == std::numeric_limits<Float>::infinity() && depth == 1)
		return;



	//2. 如果有交点，则要判断交点是否在超出场景范围，因为有时候树在边缘时，树枝会超出场景
	Vector2 relDist = m_subSceneUpperLeft - Vector2(its.p.x, its.p.z);
	Point2 uv = Point2(m_filmSize.x *relDist.x / (m_subSceneUpperLeft.x * 2), m_filmSize.y * relDist.y / (m_subSceneUpperLeft.y * 2));
	Point2i pos((int)std::floor(uv.x), (int)std::floor(uv.y));
	if ((pos.x < 0 || pos.x > m_filmSize.x - 1 || pos.y < 0 || pos.y > m_filmSize.y - 1) && depth == 1)
		return;
	
	Spectrum re = weight;
	//上一个点所在的像元
	Vector2 previous_relDist = m_subSceneUpperLeft - Vector2(previousPoint.x, previousPoint.z);
	Point2 prev_uv = Point2(m_filmSize.x *previous_relDist.x / (m_subSceneUpperLeft.x * 2), m_filmSize.y * previous_relDist.y / (m_subSceneUpperLeft.y * 2));
	const Point2i pre_pos((int)std::floor(prev_uv.x), (int)std::floor(prev_uv.y));

    //3. 直接下行辐射，即光线在范围内，depth==1 
	if (depth == 1) {
		m_workResult->m_downwellingWorkResult->put_no_filter(pos, (Float *)(&re[0]));
	}
	else {//多次散射，上下行
		//如果当前交点超过场景范围，或者没有交点，则只记录上一个交点处的上行辐射
		if (its.t == std::numeric_limits<Float>::infinity() || pos.x < 0 || pos.x > m_filmSize.x - 1 || pos.y < 0 || pos.y > m_filmSize.y - 1) {
			//上一个交点也需要在范围以内
			if (pre_pos.x >= 0 && pre_pos.x <= m_filmSize.x - 1 && pre_pos.y >= 0 && pre_pos.y <= m_filmSize.y - 1) 
				m_workResult->m_upwellingWorkResult->put_no_filter(pre_pos, (Float *)(&re[0]));
		}
		else {//如果当前交点在范围以内
			if (pre_pos == pos) {//如果当前交点和上一次交点在同一个像元，则不记录
				return;
			}
			else {
				m_workResult->m_downwellingWorkResult->put_no_filter(pos, (Float *)(&re[0]));
				if (pre_pos.x >= 0 && pre_pos.x <= m_filmSize.x - 1 && pre_pos.y >= 0 && pre_pos.y <= m_filmSize.y - 1)
					m_workResult->m_upwellingWorkResult->put_no_filter(pre_pos, (Float *)(&re[0]));
			}

		}
	
	}
	//m_workResult->m_PhtonsEachProcess++;
}

void CapturePhotonWorker::handleMediumInteraction(int depth, int nullInteractions, bool caustic,
	const MediumSamplingRecord &mRec, const Medium *medium, const Vector &wi,
	const Spectrum &weight) {
}



/* ==================================================================== */
/*                        Parallel process impl.                        */
/* ==================================================================== */

void CapturePhotonProcess::develop() {
	m_film->setBitmap(m_accum_downwell->getBitmap(), 1/ (Float)m_receivedResultCount);
	m_film_upwell->setBitmap(m_accum_upwell->getBitmap(), 1 / (Float)m_receivedResultCount);
	//m_film_upwell->develop(m_scene, 0);
	m_queue->signalRefresh(m_job);
	m_film_upwell->develop(m_scene, 0);
}

void CapturePhotonProcess::processResult(const WorkResult *wr, bool cancelled) {
	const CapturePhotonWorkResult *result
		= static_cast<const CapturePhotonWorkResult *>(wr);
	const RangeWorkUnit *range = result->getRangeWorkUnit();
	if (cancelled)
		return;

	LockGuard lock(m_resultMutex);
	increaseResultCount(range->getSize());
	//m_accum->put(result);
	m_accum_downwell->put(result->m_downwellingWorkResult.get());
	m_accum_upwell->put(result->m_upwellingWorkResult.get());
	m_totalPhotons += result->m_PhtonsEachProcess;
	if (m_job->isInteractive() || m_receivedResultCount == m_workCount)
		develop();
}

void CapturePhotonProcess::bindResource(const std::string &name, int id) {
	if (name == "scene") {
		m_scene = static_cast<Scene *>(Scheduler::getInstance()->getResource(id));
	}

	if (name == "sensor") {
		Sensor *sensor = static_cast<Sensor *>(Scheduler::getInstance()->getResource(id));
		m_film = sensor->getFilm();
		m_film->setDestinationFile(m_scene->getDestinationFile().string() + "_downwelling", m_scene->getBlockSize());

		m_film_upwell = static_cast<Film *>(PluginManager::getInstance()->createObject(
				MTS_CLASS(Film), m_film->getProperties()));
		std::string upwell_file = m_scene->getDestinationFile().string() + "_upwelling";
		m_film_upwell->setDestinationFile(upwell_file, m_scene->getBlockSize());

		//m_accum = new ImageBlock(Bitmap::ESpectrum, m_film->getCropSize(), NULL);
		//m_accum->clear();
		m_accum_downwell = new ImageBlock(Bitmap::ESpectrum, m_film->getCropSize(), NULL); //下行辐射
		m_accum_downwell->clear();

		m_accum_upwell = new ImageBlock(Bitmap::ESpectrum, m_film->getCropSize(), NULL); //上行辐射
		m_accum_upwell->clear();
	}
	PhotonProcess::bindResource(name, id);
}

ref<WorkProcessor> CapturePhotonProcess::createWorkProcessor() const {
	return new CapturePhotonWorker(m_maxDepth, m_maxPathDepth,
		m_rrDepth, m_bruteForce);
}


MTS_IMPLEMENT_CLASS(CapturePhotonProcess, false, ParticleProcess)
MTS_IMPLEMENT_CLASS(CapturePhotonWorkResult, false, ImageBlock)
MTS_IMPLEMENT_CLASS_S(CapturePhotonWorker, false, ParticleTracer)

MTS_NAMESPACE_END