
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
	const bool &stop) {}

void PhotonTracer::handleEmission(const PositionSamplingRecord &pRec,
	const Medium *medium, const Spectrum &weight) { }

void PhotonTracer::handleNewParticle() { }

void PhotonTracer::handleSurfaceInteraction(int depth, int nullInteractions,
	bool delta, const Intersection &its, const Medium *medium,
	const Spectrum &weight) {
}

//void PhotonTracer::handleSurfaceInteractionExt(int depth, int nullInteractions,
//	bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
//	const Spectrum &weight) {};

void PhotonTracer::handleMediumInteraction(int depth, int nullInteractions,
	bool delta, const MediumSamplingRecord &mRec, const Medium *medium,
	const Vector &wi, const Spectrum &weight) { }

MTS_IMPLEMENT_CLASS(RangeWorkUnit, false, WorkUnit) //在Particleproc.cpp中已经实现了，所以此处不需要重复定义了-> 2018.6: 已删除particleparoc.cpp 因此需要定义
MTS_IMPLEMENT_CLASS(PhotonProcess, true, ParallelProcess)
MTS_IMPLEMENT_CLASS(PhotonTracer, true, WorkProcessor)

MTS_NAMESPACE_END

