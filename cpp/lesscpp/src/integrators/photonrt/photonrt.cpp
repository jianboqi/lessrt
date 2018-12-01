

#include "photonrt_proc.h"
MTS_NAMESPACE_BEGIN

class PhotonRtTracer : public Integrator {
public:
	PhotonRtTracer(const Properties &props) : Integrator(props) {
		/* Depth to start using russian roulette */
		m_rrDepth = props.getInteger("rrDepth", 5);

		/* Longest visualized path length (<tt>-1</tt>=infinite).
		A value of <tt>1</tt> will produce a black image, since this integrator
		does not visualize directly visible light sources,
		<tt>2</tt> will lead to single-bounce (direct-only) illumination, and so on. */
		m_maxDepth = props.getInteger("maxDepth", -1);


		/* Granularity of the work units used in parallelizing
		the particle tracing task (default: 200K samples).
		Should be high enough so that sending and accumulating
		the partially exposed films is not the bottleneck. */
		m_granularity = props.getSize("granularity", 20000);

		m_sunRayResolution = props.getFloat("sunRayResolution", 0.05);
		m_hasBRFProducts = props.getBoolean("BRFProduct", false);
		m_hasUpDownProducts = props.getBoolean("UpDownProduct", false);
		m_numberOfDirections = props.getInteger("NumberOfDirections", 150);

		m_hasfPARProducts = props.getBoolean("fPARProduct", false);

		/* Rely on hitting the sensor via ray tracing? */
		m_bruteForce = props.getBoolean("bruteForce", false);

		if (m_rrDepth <= 0)
			Log(EError, "'rrDepth' must be set to a value than zero!");

		if (m_maxDepth <= 0 && m_maxDepth != -1)
			Log(EError, "'maxDepth' must be set to -1 (infinite) or a value greater than zero!");
	}

	PhotonRtTracer(Stream *stream, InstanceManager *manager)
		: Integrator(stream, manager) {
		m_maxDepth = stream->readInt();
		m_rrDepth = stream->readInt();
		m_granularity = stream->readSize();
		m_bruteForce = stream->readBool();
		m_hasBRFProducts = stream->readBool();
		m_hasUpDownProducts = stream->readBool();
		m_numberOfDirections = stream->readInt();
		m_hasfPARProducts = stream->readBool();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Integrator::serialize(stream, manager);
		stream->writeInt(m_maxDepth);
		stream->writeInt(m_rrDepth);
		stream->writeSize(m_granularity);
		stream->writeBool(m_bruteForce);
		stream->writeBool(m_hasBRFProducts);
		stream->writeBool(m_hasUpDownProducts);
		stream->writeInt(m_numberOfDirections);
		stream->writeBool(m_hasfPARProducts);
	}

	bool preprocess(const Scene *scene, RenderQueue *queue, const RenderJob *job,
		int sceneResID, int sensorResID, int samplerResID) {
		Integrator::preprocess(scene, queue, job, sceneResID, sensorResID, samplerResID);

		Scheduler *sched = Scheduler::getInstance();
		const Sensor *sensor = static_cast<Sensor *>(sched->getResource(sensorResID));
		Vector2i size = sensor->getFilm()->getCropSize();

		if (scene->getSubsurfaceIntegrators().size() > 0)
			Log(EError, "Subsurface integrators are not supported by the particle tracer!");

		//total samples for the whole scene
		AABB aabb = scene->getKDTree()->getAABB();
		Point2 scene_min = Point2(aabb.min.x >= 0 ? std::ceil(aabb.min.x) : std::floor(aabb.min.x),
			aabb.min.z >= 0 ? std::ceil(aabb.min.z) : std::floor(aabb.min.z));
		Point2 scene_max = Point2(aabb.max.x >= 0 ? std::ceil(aabb.max.x) : std::floor(aabb.max.x),
			aabb.max.z >= 0 ? std::ceil(aabb.max.z) : std::floor(aabb.max.z));
		Vector2 extent = scene_max - scene_min;
		m_sampleCount = static_cast<size_t>(1/(m_sunRayResolution*m_sunRayResolution) * extent.x*extent.y);
		return true;
	}

	void cancel() {
		Scheduler::getInstance()->cancel(m_process);
	}

	bool render(Scene *scene, RenderQueue *queue,
		const RenderJob *job, int sceneResID, int sensorResID, int samplerResID) {
		ref<Scheduler> scheduler = Scheduler::getInstance();

		ref<Sensor> sensor = scene->getSensor();
		AABB aabb = scene->getKDTree()->getAABB();
		Vector extent = aabb.getExtents();
		size_t nCores = scheduler->getCoreCount();
		Log(EInfo, "Starting simulation job (%.2fx%.2f, " SIZE_T_FMT " samples, " SIZE_T_FMT
			" %s, " SSE_STR ") ..", extent.x, extent.z,
			m_sampleCount, nCores, nCores == 1 ? "core" : "cores");

		int maxPtracerDepth = m_maxDepth - 1;

		//always add 1
		//if ((sensor->getType() & (Emitter::EDeltaDirection
		//	| Emitter::EDeltaPosition)) == 0 && sensor->isOnSurface()) {
		//	/* The sensor has a finite aperture and a non-degenerate
		//	response function -- trace one more bounce, since we
		//	can actually try to hit its aperture */
		//	maxPtracerDepth++;
		//}
		maxPtracerDepth++;
		ref<ParallelProcess> process = new CapturePhotonProcess(
			job, queue, m_sampleCount, m_granularity,
			maxPtracerDepth, m_maxDepth, m_rrDepth, m_bruteForce, m_hasBRFProducts,
			m_hasUpDownProducts, m_numberOfDirections, m_hasfPARProducts);
		process->bindResource("scene", sceneResID);
		process->bindResource("sensor", sensorResID);
		process->bindResource("sampler", samplerResID);
		scheduler->schedule(process);
		m_process = process;
		scheduler->wait(process);
		m_process = NULL;

		return process->getReturnStatus() == ParallelProcess::ESuccess;
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "PhotonRtTracer[" << endl
			<< "  maxDepth = " << m_maxDepth << "," << endl
			<< "  rrDepth = " << m_rrDepth << "," << endl
			<< "  granularity = " << m_granularity << "," << endl
			<< "  bruteForce = " << m_bruteForce << endl
			<< "]";
		return oss.str();
	}


	MTS_DECLARE_CLASS()
protected:
	ref<ParallelProcess> m_process;
	int m_maxDepth, m_rrDepth;
	size_t m_sampleCount, m_granularity;
	bool m_bruteForce;
	Float m_sunRayResolution;// for each subcell, there is one ray.

	bool m_hasBRFProducts;
	bool m_hasUpDownProducts;
	int m_numberOfDirections;

	bool m_hasfPARProducts;
};

MTS_IMPLEMENT_CLASS_S(PhotonRtTracer, false, Integrator)
MTS_EXPORT_PLUGIN(PhotonRtTracer, "Photon RT Tracer");
MTS_NAMESPACE_END
