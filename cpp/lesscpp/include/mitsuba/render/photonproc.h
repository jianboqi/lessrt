#pragma once
#if !defined(_LESS_PHOTONPROC_H_)
#define _LESS_PHOTONPROC_H_

#include <mitsuba/render/scene.h>

MTS_NAMESPACE_BEGIN

/**
* Abstract Parallel photon tracing process
*/
class MTS_EXPORT_RENDER PhotonProcess :public ParallelProcess {
public:
	enum EMode {
		ETrace = 0,
		EGather
	};

	virtual EStatus generateWork(WorkUnit *unit, int worker);

	MTS_DECLARE_CLASS()
protected:
	PhotonProcess(EMode mode, size_t workCount,
		size_t granularity, const std::string &progressText,
		const void* progressReporterPayload);

	void increaseResultCount(size_t resultCount);

	/// Virtual destructor
	virtual ~PhotonProcess();

protected:
	EMode m_mode;
	ProgressReporter *m_progress;
	size_t m_workCount;
	size_t m_numGenerated;
	size_t m_granularity;
	ref<Mutex> m_resultMutex;
	size_t m_receivedResultCount;
};


class MTS_EXPORT_RENDER PhotonTracer :public WorkProcessor {

public:
	// =============================================================
	//! @{ \name Implementation of the WorkProcessor interface
	// =============================================================

	virtual ref<WorkUnit> createWorkUnit() const;
	virtual void prepare();
	virtual void process(const WorkUnit *workUnit, WorkResult *workResult,
		const bool &stop);
	void serialize(Stream *stream, InstanceManager *manager) const;

	virtual void handleEmission(const PositionSamplingRecord &pRec,
		const Medium *medium, const Spectrum &weight);

	virtual void handleNewParticle();

	virtual void handleSurfaceInteraction(int depth, int nullInteractions,
		bool delta, const Intersection &its, const Medium *medium,
		const Spectrum &weight);

	//virtual void handleSurfaceInteractionExt(int depth, int nullInteractions,
	//	bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
	//	const Spectrum &weight);

	virtual void handleMediumInteraction(int depth, int nullInteractions,
		bool delta, const MediumSamplingRecord &mRec, const Medium *medium,
		const Vector &wi, const Spectrum &weight);

	MTS_DECLARE_CLASS()
protected:
	/// Protected constructor
	PhotonTracer(int maxDepth, int rrDepth, bool emissionEvents);
	/// Protected constructor
	PhotonTracer(Stream *stream, InstanceManager *manager);
	/// Virtual destructor
	virtual ~PhotonTracer() { }
protected:
	ref<Scene> m_scene;
	ref<Sampler> m_sampler;
	int m_maxDepth;
	int m_rrDepth;
	bool m_emissionEvents;
};

MTS_NAMESPACE_END

#endif