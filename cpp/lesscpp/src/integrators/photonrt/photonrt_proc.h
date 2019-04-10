#pragma once

#if !defined(_PHOTONRT_H_)
#define _PHOTONRT_H_

#include <mitsuba/render/photonproc.h>
#include <mitsuba/render/range.h>
#include <mitsuba/render/renderjob.h>
#include <mitsuba/core/bitmap.h>
#include "DirectionalBRF.h"
#include "fPARProduct.h"
MTS_NAMESPACE_BEGIN

//结果保存到图像中
class CapturePhotonWorkResult :public WorkResult {
public:
	inline CapturePhotonWorkResult(const Vector2i &res, const ReconstructionFilter *filter, 
		bool hasBRFProducts, bool hasUpDownProducts, string virtualDirectionStr, int numberOfDirections,
		string virtualDetectorDirection, bool hasfPARProducts, string layerDefinition){
		m_range = new RangeWorkUnit();

		m_hasUpDownProducts = hasUpDownProducts;
		if (m_hasUpDownProducts) {
			m_downwellingWorkResult = new ImageBlock(Bitmap::ESpectrum, res, filter);
			m_upwellingWorkResult = new ImageBlock(Bitmap::ESpectrum, res, filter);
		}
		
		m_hasBRFProducts = hasBRFProducts;
		m_numberOfDirections = numberOfDirections;

		if (m_hasBRFProducts) {
			m_dirBRFWorkResult = new DirectionalBRF(m_numberOfDirections);
			m_dirBRFWorkResult->readVirtualDirections(virtualDirectionStr);
			m_dirBRFWorkResult->readVirtualDetectors(virtualDetectorDirection);
		}

		m_hasfPARProducts = hasfPARProducts;
		m_layerDefinition = layerDefinition;
		if (m_hasfPARProducts) {
			m_fPARsWordResult = new fPARProduct(m_layerDefinition);
		}
		
		m_PhtonsEachProcess = 0;
	}

	inline const RangeWorkUnit *getRangeWorkUnit() const {
		return m_range.get();
	}

	inline void setRangeWorkUnit(const RangeWorkUnit *range) {
		m_range->set(range);
	}

	/* Work unit implementation */
	void load(Stream *stream);
	void save(Stream *stream) const;


	std::string toString() const {
		std::ostringstream oss;
		oss << "CapturePhotonWorkResult" << endl;
		return oss.str();
	}
	MTS_DECLARE_CLASS()
protected:
	/// Virtual destructor
	virtual ~CapturePhotonWorkResult() { }
protected:
	ref<RangeWorkUnit> m_range;
public:
	ref<ImageBlock> m_downwellingWorkResult;
	ref<ImageBlock> m_upwellingWorkResult;
	ref<DirectionalBRF> m_dirBRFWorkResult;
	bool m_hasBRFProducts;
	bool m_hasUpDownProducts;
	size_t m_PhtonsEachProcess;
	int m_numberOfDirections;
	bool m_hasfPARProducts;
	ref<fPARProduct> m_fPARsWordResult;
	string m_layerDefinition;
};


/* ==================================================================== */
/*                             Work processor                           */
/* ==================================================================== */

/**
* \brief Particle tracing worker -- looks for volume and surface interactions
* and tries to accumulate the resulting information at the image plane.
*/
class CapturePhotonWorker : public PhotonTracer {
public:
	enum EPhotonType {
		ETypeNull = 0x0001,
		ETypeBRF = 0x0002,
		ETypefPAR = 0x0004,
		ETypeUpDown = 0x0008,
		EtypeAllProducts = ETypeBRF | ETypefPAR | ETypeUpDown
		//EtypeBRFUpDown = ETypeBRF | ETypeUpDown
	};

	inline CapturePhotonWorker(int maxDepth, int maxPathDepth,
		int rrDepth, bool bruteForce, bool hasBRFProducts, bool hasUpDownProducts, string virtualDirections,
		int numberOfDirections, string virtualDetectorDirection, bool hasfPARProducts, string layerDefinition) : PhotonTracer(maxDepth, rrDepth, true),
		m_maxPathDepth(maxPathDepth), m_bruteForce(bruteForce), m_hasBRFProducts(hasBRFProducts),
		m_hasUpDownProducts(hasUpDownProducts), m_virtualDirections(virtualDirections),
		m_numberOfDirections(numberOfDirections), m_virtualDetectorDirection(virtualDetectorDirection),
		m_hasfPARProducts(hasfPARProducts),m_layerDefinition(layerDefinition){ }

	CapturePhotonWorker(Stream *stream, InstanceManager *manager);

	void serialize(Stream *stream, InstanceManager *manager) const;

	void prepare();
	void process(const WorkUnit *workUnit, WorkResult *workResult,
		const bool &stop);

	ref<WorkProcessor> clone() const;
	ref<WorkResult> createWorkResult() const;

	/**
	* \brief Handles particles emitted by a light source
	*
	* If a connection to the sensor is possible, compute the importance
	* and accumulate in the proper pixel of the accumulation buffer.
	*/
	void handleEmission(const PositionSamplingRecord &pRec,
		const Medium *medium, const Spectrum &weight);

	/**
	* \brief Handles particles interacting with a surface
	*
	* If a connection to the sensor is possible, compute the importance
	* and accumulate in the proper pixel of the accumulation buffer.
	*/
	void handleSurfaceInteraction(int depth, int nullInteractions, bool caustic,
		const Intersection &its, const Medium *medium,
		const Spectrum &weight);

	/**
	* \brief extended version of handleSurfaceInteraction
	* * This is 
	* If a connection to the sensor is possible, compute the importance
	* and accumulate in the proper pixel of the accumulation buffer.
	*/
	void handleSurfaceInteractionBRF(int depth, int nullInteractions,
		bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
		const Spectrum &weight, int photoType);

	void handleSurfaceInteractionFPAR(int depth, int nullInteractions,
		bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
		const Spectrum &weight, int photoType);

	void handleSurfaceInteractionUpDown(int depth, int nullInteractions,
		bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
		const Spectrum &weight, int photoType);

	bool rayIntersectExcludeEdge(Ray &ray, Intersection &its);
	/**
	* \brief Handles particles interacting with a medium
	*
	* If a connection to the sensor is possible, compute the importance
	* and accumulate in the proper pixel of the accumulation buffer.
	*/
	void handleMediumInteraction(int depth, int nullInteractions, bool caustic,
		const MediumSamplingRecord &mRec, const Medium *medium,
		const Vector &wi, const Spectrum &weight);

	/**
	* determine the repetitive occlusion 
	*/
	Spectrum repetitiveOcclude(Spectrum value, Point p, Vector d, const Scene* scene, bool & isRepetitiveOcclude)const;

	MTS_DECLARE_CLASS()
protected:
	/// Virtual destructor
	virtual ~CapturePhotonWorker() { }
private:
	ref<const Sensor> m_sensor;
	ref<const ReconstructionFilter> m_rfilter;
	ref<CapturePhotonWorkResult> m_workResult;
	int m_maxPathDepth;
	bool m_bruteForce;

	//query parameters from scene xml
	Vector2 m_subSceneUpperLeft;
	Vector2i m_filmSize;

	AABB m_sceneBounds;

	AABB m_virtualBounds;

	int m_repetitiveSceneNum;

	bool m_hasBRFProducts;
	bool m_hasUpDownProducts;
	string m_virtualDirections;
	int m_numberOfDirections;
	string m_virtualDetectorDirection;
	bool m_hasfPARProducts;
	string m_layerDefinition;
};


/* ==================================================================== */
/*                           Parallel process                           */
/* ==================================================================== */
/**
* Parallel particle tracing process - used to run this over
* a group of machines
*/
class CapturePhotonProcess : public PhotonProcess {
public:
	CapturePhotonProcess(const RenderJob *job, RenderQueue *queue,
		size_t sampleCount, size_t granularity, int maxDepth,
		int maxPathDepth, int rrDepth, bool bruteForce, bool hasBRFProducts, bool hasUpDownProducts,
		int numberOfDirections, bool hasfPARProducts)
		: PhotonProcess(PhotonProcess::ETrace, sampleCount,
			granularity, "Simulating", job), m_job(job), m_queue(queue),
		m_maxDepth(maxDepth), m_maxPathDepth(maxPathDepth),
		m_rrDepth(rrDepth), m_bruteForce(bruteForce), m_hasBRFProducts(hasBRFProducts),
		m_hasUpDownProducts(hasUpDownProducts),
		m_numberOfDirections(numberOfDirections),
		m_hasfPARProducts(hasfPARProducts){
	}

	void develop();

	/* ParallelProcess impl. */
	void processResult(const WorkResult *wr, bool cancelled);
	void bindResource(const std::string &name, int id);
	ref<WorkProcessor> createWorkProcessor() const;

	MTS_DECLARE_CLASS()
protected:
	/// Virtual destructor
	virtual ~CapturePhotonProcess() { }
private:
	ref<const RenderJob> m_job;
	ref<RenderQueue> m_queue;
	//ref<ImageBlock> m_accum;
	int m_maxDepth;
	int m_maxPathDepth;
	int m_rrDepth;
	bool m_bruteForce;

	ref<Scene> m_scene;

	ref<Film> m_film_downwell;
	ref<ImageBlock> m_accum_downwell;

	ref<Film> m_film_upwell;
	ref<ImageBlock> m_accum_upwell;
	ref<DirectionalBRF> m_dirBRFs;
	ref<fPARProduct> m_fPARs;

	AABB m_virtualBounds;//scene virtual bounds

	//Products
	bool m_hasBRFProducts;
	bool m_hasUpDownProducts;
	string m_virtualDirections;
	string m_virtualDetectorDirection;
	int m_numberOfDirections;
	bool m_hasfPARProducts;
	string m_layerDefinition;

	size_t m_totalPhotons;
};


MTS_NAMESPACE_END
#endif
