#pragma once

#if !defined(_PHOTONRT_H_)
#define _PHOTONRT_H_

#include <mitsuba/render/photonproc.h>
#include <mitsuba/render/range.h>
#include <mitsuba/render/renderjob.h>
#include <mitsuba/core/bitmap.h>
#include "DirectionalBRF.h"
#include "fPARProduct.h"
#include "fSunlitLeafProduct.h"
#include "DirectionalFluor.h"
#include "MultiLevelFluor.h"
#include "FluxMeasureProduct.h"
MTS_NAMESPACE_BEGIN

//结果保存到图像中
class CapturePhotonWorkResult :public WorkResult {
public:
	inline CapturePhotonWorkResult(const Vector2i& res, const ReconstructionFilter* filter,
		bool hasBRFProducts, bool hasUpDownProducts, string virtualDirectionStr, int numberOfDirections,
		string virtualDetectorDirection, bool hasfPARProducts, string layerDefinition, int pProbEscDirectionNumber, bool hasSunlitLeafProduct,
		size_t hasFluorProducts, size_t FluorPhotonsNum, Spectrum wavelengths, 
		bool hasFluxMeasureProduct, string measureMode) {
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
			m_fPARsWordResult = new fPARProduct(m_layerDefinition, pProbEscDirectionNumber);
		}

		m_hasSunlitLeafProduct = hasSunlitLeafProduct;
		m_layerDefinition = layerDefinition;
		if (m_hasSunlitLeafProduct) {
			m_fSunlitLeafResult = new fSunlitLeafProduct(m_layerDefinition);
		}

		m_hasFluxMeasureProduct = hasFluxMeasureProduct;
		m_measureMode = measureMode;
		if (m_hasFluxMeasureProduct) {
			m_fluxMeasureProduct = new FluxMeasureProduct(m_measureMode);
		}

		m_hasFluorProducts = hasFluorProducts;
		m_FluorPhotonsNum = FluorPhotonsNum;
		m_numberOfDirections = numberOfDirections;
		m_wavelengths = wavelengths;
		if (m_hasFluorProducts) {
			m_dirFluorAllWorkResult = new DirectionalFluor(m_numberOfDirections);
			m_dirFluorAllWorkResult->readVirtualDirections(virtualDirectionStr);
			m_dirFluorAllWorkResult->readVirtualDetectors(virtualDetectorDirection);
			if (m_hasfPARProducts) {
				m_multilevelFluorWorkResult = new MultiLevelFluor(m_layerDefinition, m_wavelengths);
			}
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
	
	bool m_hasSunlitLeafProduct;
	ref<fSunlitLeafProduct> m_fSunlitLeafResult;

	ref<DirectionalFluor> m_dirFluorAllWorkResult;
	ref<MultiLevelFluor> m_multilevelFluorWorkResult;
	Spectrum m_wavelengths;
	size_t m_hasFluorProducts;
	size_t m_FluorPhotonsNum;

	bool m_hasFluxMeasureProduct;
	string m_measureMode;
	ref<FluxMeasureProduct> m_fluxMeasureProduct;
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
		ETypeFluor = 0x0010,
		ETypeFlux = 0x1000,
		EtypeAllProducts = ETypeBRF | ETypefPAR | ETypeUpDown | ETypeFluor | ETypeFlux
		//EtypeBRFUpDown = ETypeBRF | ETypeUpDown
	};

	inline CapturePhotonWorker(int maxDepth, int maxPathDepth,
		int rrDepth, bool bruteForce, bool hasBRFProducts, bool hasUpDownProducts, string virtualDirections,
		int numberOfDirections, string virtualDetectorDirection, bool hasfPARProducts, string layerDefinition, int probEscDirectionNumber,
		bool hasfSunlitLeafProducts,
		size_t hasFluorProducts, Spectrum wavelengths,
		bool hasFluxMeasureProduct, string measureMode) : PhotonTracer(maxDepth, rrDepth, true),
		m_maxPathDepth(maxPathDepth), m_bruteForce(bruteForce), m_hasBRFProducts(hasBRFProducts),
		m_hasUpDownProducts(hasUpDownProducts), m_virtualDirections(virtualDirections),
		m_numberOfDirections(numberOfDirections), m_virtualDetectorDirection(virtualDetectorDirection),
		m_hasfPARProducts(hasfPARProducts), m_layerDefinition(layerDefinition), m_ProbEscDirectionNumber(probEscDirectionNumber), m_hasfSunlitLeafProducts(hasfSunlitLeafProducts),
		m_hasFluorProducts(hasFluorProducts), m_wavelengths(wavelengths),
		m_hasFluxMeasureProduct(hasFluxMeasureProduct),
		m_measureMode(measureMode){ }

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

	bool sampleDistanceWithRandomOpticalDepth(const Scene* scene, const Medium* medium, Ray& ray, MediumSamplingRecord& mRec,
		Sampler* sampler, Intersection& its);

	/**
	* \brief extended version of handleSurfaceInteraction
	* * This is 
	* If a connection to the sensor is possible, compute the importance
	* and accumulate in the proper pixel of the accumulation buffer.
	*/
	void handleSurfaceInteractionBRF(int depth, int nullInteractions,
		bool delta, const Intersection &its, Ray &ray, Point & hotspotStartPoint, Point &previousPoint, const Medium *medium, std::vector<const Medium*>& meeted_mediums,
		const Spectrum &weight, int photoType, bool has_medium_in_single_path);

	void handleMediumInteractionBRF(int depth, int nullInteractions,
		bool delta, const Intersection& its, Ray& ray, Point& hotspotStartPoint, Point& previousPoint, const MediumSamplingRecord& mRec,
		const Medium* medium, std::vector<const Medium*> &meeted_mediums, const Vector& wi,
		const Spectrum& weight, int photoType);

	void handleSurfaceInteractionFPAR(int depth, int nullInteractions,
		bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
		const Spectrum &weight, const Spectrum & incidentEnergy, int photoType, bool & isIntersectedWithTerrainAlready);

	void handleMediumInteractionFPAR(int depth, const MediumSamplingRecord& mRec,
		const Spectrum& weight, int photoType, Intersection& its);

	void handleSurfaceInteractionMultiLevelFluor(int depth, int nullInteractions,
		bool delta, const Intersection& its, Ray& ray, Point& previousPoint, const Medium* medium,
		const Spectrum& absorbedEnergy, int photoType, bool& isIntersectedWithTerrainAlready,
		const BSDF* bsdf, const Spectrum& excitePSIFluorEnergy, const Spectrum& excitePSIIFluorEnergy);

	void handleMediumInteractionMultiLevelFluor(int depth, const MediumSamplingRecord& mRec,
		const Spectrum& weight, int photoType, Intersection& its,
		const Medium* medium, const Spectrum& excitePSIFluorEnergy, const Spectrum& excitePSIIFluorEnergy);

	void handleSurfaceInteractionUpDown(int depth, int nullInteractions,
		bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
		const Spectrum &weight, int photoType);

	void handleSurfaceInteractionFluxMeasure(int depth, int nullInteractions,
		bool delta, const Intersection& its, Ray& ray, Point& previousPoint, const Medium* medium,
		const Spectrum& weight, int photoType);

	void handleSurfaceInteractionFluxMeasure4Fluor(int depth, int nullInteractions,
		bool delta, const Intersection& its, Ray& ray, Point& previousPoint, const Medium* medium,
		const Spectrum& weightPSI, const Spectrum& weightPSII, int photoType);

	void handleMediumInteractionUpDown(int depth, const MediumSamplingRecord& mRec, Point& previousPoint,
		const Spectrum& weight, int photoType);

	void handleSurfaceInteractionFluor(int depth, int nullInteractions,
		bool delta, const Intersection& its, Ray& ray, Point& hotspotStartPoint, Point& previousPoint, const Medium* medium, std::vector<const Medium*>& meeted_mediums,
		Spectrum power, int photoType, bool has_medium_in_single_path,
		Spectrum throughput, FluorMatrix m);

	void handleMediumInteractionFluor(int depth, int nullInteractions,
		bool delta, const Intersection& its, Ray& ray, Point& hotspotStartPoint, Point& previousPoint, MediumSamplingRecord mRec,
		const Medium* medium, std::vector<const Medium*>& meeted_mediums, const Vector& wi,
		Spectrum throughput, Spectrum power, int photoType,
		FluorMatrix m);

	void handleSurfaceReProb(int depth, int nullInteractions,
		bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
		int photoType, int previousStatus);

	bool rayIntersectExcludeEdge(Ray &ray, Intersection &its);

	//This is an extended version of scene->evalTransmittance to handle repetitive scene
	Spectrum evalTransmittance(const Point& p1, bool p1OnSurface,
		const Point& p2, bool p2OnSurface, Float time, const Medium* medium,
		int& interactions,Ray & ray, Sampler* sampler = NULL) const;

	//This is an extended version of scene->evalTransmittance to handle repetitive scene
	// and also hotspot
	Spectrum evalTransmittanceWithHotspot(const Point& p1, bool p1OnSurface,
		const Point& p2, bool p2OnSurface, Float time, const Medium* medium,
		int& interactions, Ray& solarRay, Point &hotspotStartPoint, Ray & sensorRay,int depth,bool has_medium_in_single_path, Sampler* sampler = NULL) const;

	Spectrum evalTransmittanceWithHotspot(const Point& p1, bool p1OnSurface,
		const Point& p2, bool p2OnSurface, Float time, const Medium* medium, std::vector<const Medium*> meeted_mediums,
		int& interactions, Ray& solarRay, Point& hotspotStartPoint, Ray& sensorRay, int depth, bool has_medium_in_single_path, 
		Sampler* sampler = NULL) const;

	/**
	* Handle sunlit and shaded leaf fraction
	*/
	///
	///Sample a position on all object surfaces
	///
	void sampleShapePosition(ref<Scene> scene, const Point2& objSample, const Point2& spatialSample, PositionSamplingRecord& pRec);

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
	bool isRepetitiveOcclude(Ray & occludeRay, const Scene* scene, Intersection& its);

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
	int m_ProbEscDirectionNumber;

	size_t m_hasFluorProducts;
	Spectrum m_wavelengths;
	size_t m_FluorPhotonsNum;

	bool m_hasFluxMeasureProduct;
	string m_measureMode;

	bool m_hasfSunlitLeafProducts;
	Vector m_sunDirInv;
	DiscreteDistribution m_shapePDF;
	ref_vector<Shape> m_shapesExcludeTerrain;
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
		int numberOfDirections, bool hasfPARProducts, bool hasfSunlitLeafProducts, bool m_boolOutParEachBand,
		size_t hasFluorProducts, bool m_hasFluxMeasureProduct)
		: PhotonProcess(PhotonProcess::ETrace, sampleCount,
			granularity, "Simulating", job), m_job(job), m_queue(queue),
		m_maxDepth(maxDepth), m_maxPathDepth(maxPathDepth),
		m_rrDepth(rrDepth), m_bruteForce(bruteForce), m_hasBRFProducts(hasBRFProducts),
		m_hasUpDownProducts(hasUpDownProducts),
		m_numberOfDirections(numberOfDirections),
		m_hasfPARProducts(hasfPARProducts),
		m_hasfSunlitLeafProducts(hasfSunlitLeafProducts),
		m_boolOutParEachBand(m_boolOutParEachBand),
		m_hasFluorProducts(hasFluorProducts),
		m_hasFluxMeasureProduct(m_hasFluxMeasureProduct){}

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
	ref<DirectionalFluor> m_dirFluors_All;
	ref<MultiLevelFluor> m_MultiLevelFluor;
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
	int m_ProbEscDirectionNumber;

	size_t m_totalPhotons; //it is not used by now

	bool m_hasfSunlitLeafProducts;
	ref<fSunlitLeafProduct> m_fSunlitLeafProduct;

	bool m_boolOutParEachBand;

	size_t m_hasFluorProducts;
	Spectrum m_wavelengths;
	bool m_hasFluxMeasureProduct;
	string m_measureMode;
	ref<FluxMeasureProduct> m_fluxMeasureProduct;
};


MTS_NAMESPACE_END
#endif
