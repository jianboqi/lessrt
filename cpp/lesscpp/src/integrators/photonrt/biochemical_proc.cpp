
#include "biochemical_proc.h"
#include <mitsuba/core/plugin.h>
#include <mitsuba/core/statistics.h>

MTS_NAMESPACE_BEGIN
/* ==================================================================== */
/*                           Work result impl.                          */
/* ==================================================================== */
void CapturePhotonWorkResult::load(Stream* stream) {
	m_range->load(stream);
	m_PhtonsEachProcess = stream->readSize();
	m_numberOfDirections = stream->readInt();
	m_hasfPARProducts = stream->readBool();
	if (m_hasfPARProducts)
		m_fPARsWordResult->unserialize(stream);
	m_hasFluxMeasureProduct = stream->readBool();
	if (m_hasFluxMeasureProduct) {
		m_fluxMeasureProduct->unserialize(stream);
	}
	m_hasFluorProducts = stream->readInt();
	if (m_hasFluorProducts) {
		m_dirFluorAllWorkResult->unserialize(stream);
		if (m_hasfPARProducts) {
			m_multilevelFluorWorkResult->unserialize(stream);
		}
	}
	m_hasBiochemicalProduct = stream->readInt();
	if (m_hasBiochemicalProduct) {
		m_PSproductsWorkResult->unserialize(stream);
	}
}

void CapturePhotonWorkResult::save(Stream* stream) const {
	m_range->save(stream);
	stream->writeSize(m_PhtonsEachProcess);
	stream->writeInt(m_numberOfDirections);
	stream->writeBool(m_hasfPARProducts);
	if (m_hasfPARProducts)
		m_fPARsWordResult->serialize(stream);
	stream->writeBool(m_hasFluxMeasureProduct);
	if (m_hasFluxMeasureProduct) {
		m_fluxMeasureProduct->serialize(stream);
	}
	stream->writeInt(m_hasFluorProducts);
	if (m_hasFluorProducts) {
		m_dirFluorAllWorkResult->serialize(stream);
		if (m_hasfPARProducts) {
			m_multilevelFluorWorkResult->serialize(stream);
		}
	}
	stream->writeInt(m_hasBiochemicalProduct);
	if (m_hasBiochemicalProduct) {
		m_PSproductsWorkResult->serialize(stream);
	}
}


/* ==================================================================== */
/*                         Work processor impl.                         */
/* ==================================================================== */
CapturePhotonWorker::CapturePhotonWorker(Stream* stream, InstanceManager* manager)
	: PhotonTracer(stream, manager) {
	m_maxPathDepth = stream->readInt();
	m_bruteForce = stream->readBool();
	m_numberOfDirections = stream->readInt();
	m_hasfPARProducts = stream->readBool();
	m_hasFluorProducts = stream->readInt();
	m_hasBiochemicalProduct = stream->readInt();
}

void CapturePhotonWorker::serialize(Stream* stream, InstanceManager* manager) const {
	PhotonTracer::serialize(stream, manager);
	stream->writeInt(m_maxPathDepth);
	stream->writeBool(m_bruteForce);
	stream->writeInt(m_numberOfDirections);
	stream->writeBool(m_hasfPARProducts);
	stream->writeInt(m_hasFluorProducts);
	stream->writeInt(m_hasBiochemicalProduct);
}

void CapturePhotonWorker::prepare() {
	PhotonTracer::prepare();
	m_sensor = static_cast<Sensor*>(getResource("sensor"));
	m_rfilter = m_sensor->getFilm()->getReconstructionFilter();

	AABB scene_bound = m_scene->getKDTree()->getAABB();

	Properties integratorProps = m_scene->getIntegrator()->getProperties();

	m_subSceneUpperLeft = Vector2(integratorProps.getFloat("subSceneXSize", 100) * 0.5,
		m_scene->getIntegrator()->getProperties().getFloat("subSceneZSize", 100) * 0.5);
	m_filmSize = m_sensor->getFilm()->getSize();

	m_repetitiveSceneNum = integratorProps.getInteger("RepetitiveScene", 15);

	//���Ȼ�ȡsceneBounds
	Vector2 sceneSize = Vector2(integratorProps.getFloat("subSceneXSize", scene_bound.getExtents().x),
		integratorProps.getFloat("subSceneZSize", scene_bound.getExtents().z));

	double sceneMaxY = scene_bound.max.y;
	double sceneMinY = scene_bound.min.y;
	double x_min = -0.5 * sceneSize.x - SceneBoundEpsilon; //a small offset to handle repititive scene when using pure medium
	double x_max = 0.5 * sceneSize.x + SceneBoundEpsilon;
	double z_min = -0.5 * sceneSize.y - SceneBoundEpsilon;
	double z_max = 0.5 * sceneSize.y + SceneBoundEpsilon;
	m_sceneBounds = AABB(Point(x_min, sceneMinY, z_min), Point(x_max, sceneMaxY, z_max));

	//virtual bounds
	if (integratorProps.getBoolean("SceneVirtualPlane", false)) {
		double centerX = integratorProps.getFloat("vx", 0);
		double centerZ = integratorProps.getFloat("vz", 0);
		double sizeX = integratorProps.getFloat("sizex", m_sceneBounds.getExtents().x);
		double sizeZ = integratorProps.getFloat("sizez", m_sceneBounds.getExtents().y);
		double topY = 0;
		string topYstr = integratorProps.getString("vy", "MAX");
		if (topYstr == "MAX") {
			topY = sceneMaxY;
		}
		else {
			topY = atof(topYstr.c_str());
		}
		m_virtualBounds = AABB(Point(centerX - 0.5 * sizeX, sceneMinY, centerZ - 0.5 * sizeZ),
			Point(centerX + 0.5 * sizeX, sceneMaxY, centerZ + 0.5 * sizeZ));
	}
	else {
		m_virtualBounds = m_sceneBounds;
	}
	if (m_hasfSunlitLeafProducts) {
		//Get Sun direction
		m_sunDirInv = Vector(0.0, 1.0, 0.0);
		ref_vector<Emitter> emitters = m_scene->getEmitters();
		for (int i = 0; i < emitters.size(); i++) {
			if (emitters[i]->getProperties().hasProperty("direction")) {
				m_sunDirInv = -(emitters[i]->getProperties().getVector("direction"));
			}
		}

		//Initialize shape surface area pdf
		ref_vector<Shape>& shapes = m_scene->getShapes();
		for (int i = 0; i < shapes.size(); i++) {
			ref<Shape> shape = shapes[i];
			if (shape->getID() != "terrain") {
				m_shapesExcludeTerrain.push_back(shape);
				m_shapePDF.append(shape->getSurfaceArea());
			}
		}
		m_shapePDF.normalize();
	}
}

bool CapturePhotonWorker::rayIntersectExcludeEdge(Ray& ray, Intersection& its) {
	bool isIntersected = m_scene->rayIntersect(ray, its);
	if (isIntersected) {
		while (isIntersected && (!m_sceneBounds.contains(its.p))) {
			ray.o = its.p;
			isIntersected = m_scene->rayIntersect(ray, its);
		}
	}
	return isIntersected;
}

bool CapturePhotonWorker::isRepetitiveOcclude(Ray& occludeRay, const Scene* scene, Intersection& its) {
	bool isIntersected = rayIntersectExcludeEdge(occludeRay, its);
	if (!isIntersected) {
		for (int iteration = 0; iteration < m_repetitiveSceneNum; iteration++) {
			Float tNear, tFar;
			int exitFace;
			Vector boundExtend = m_sceneBounds.getExtents();
			m_sceneBounds.rayIntersectExt(occludeRay, tNear, tFar, exitFace);
			Point its_p = occludeRay.o + tFar * occludeRay.d;
			if (its_p.y < m_sceneBounds.max.y && exitFace != 1) {
				//offset the ray
				if (exitFace == 0) {
					if (occludeRay.d.x > 0) {
						occludeRay.o = its_p + Vector(-boundExtend.x, 0, 0);
					}
					else {
						occludeRay.o = its_p + Vector(boundExtend.x, 0, 0);
					}
				}
				else if (exitFace == 2) {
					if (occludeRay.d.z > 0) {
						occludeRay.o = its_p + Vector(0, 0, -boundExtend.z);
					}
					else {
						occludeRay.o = its_p + Vector(0, 0, boundExtend.z);
					}
				}
				isIntersected = rayIntersectExcludeEdge(occludeRay, its);
				if (isIntersected) {
					return true;
				}
			}
			else {
				break;
			}
		}
	}
	return isIntersected;
}


void CapturePhotonWorker::sampleShapePosition(ref<Scene> scene, const Point2& objSample, const Point2& spatialSample, PositionSamplingRecord& pRec) {
	Point2 sample(objSample);
	Float emPdf;
	size_t index = m_shapePDF.sampleReuse(sample.x, emPdf);
	ref<Shape> chosenShape = m_shapesExcludeTerrain[index].get();
	chosenShape->samplePosition(pRec, spatialSample);
}

void CapturePhotonWorker::process(const WorkUnit* workUnit, WorkResult* workResult,
	const bool& stop) {
	if (!(m_hasfPARProducts || m_hasFluorProducts || m_hasFluxMeasureProduct || m_hasBiochemicalProduct)) {
		return;
	}

	const RangeWorkUnit* range = static_cast<const RangeWorkUnit*>(workUnit);
	m_workResult = static_cast<CapturePhotonWorkResult*>(workResult);
	m_workResult->setRangeWorkUnit(range);
	if (m_hasfPARProducts)
		m_workResult->m_fPARsWordResult->clear();
	if (m_hasFluxMeasureProduct) {
		m_workResult->m_fluxMeasureProduct->clear();
	}
	if (m_hasfSunlitLeafProducts)
		m_workResult->m_fSunlitLeafResult->clear();
	if (m_hasFluorProducts) {
		m_workResult->m_dirFluorAllWorkResult->clear();
		if (m_hasfPARProducts) {
			m_workResult->m_multilevelFluorWorkResult->clear();
		}
	}
	if (m_hasBiochemicalProduct) {
		m_workResult->m_PSproductsWorkResult->clear();
	}

	m_workResult->m_PhtonsEachProcess = 0;

	Intersection its;
	MediumSamplingRecord mRec;
	ref<Sensor> sensor = m_scene->getSensor();
	PositionSamplingRecord pRec(sensor->getShutterOpen()
		+ 0.5f * sensor->getShutterOpenTime());
	m_sampler->generate(Point2i(0));

	//sunlit leaf fraction
	Intersection shadedIts;
	PositionSamplingRecord pShadeRec;
	//fluor
	FluorMatrix m;
	FluorMatrix mt;
	if (m_hasFluorProducts) {
		m_workResult->m_FluorPhotonsNum = 0;
	}

	for (size_t index = range->getRangeStart(); index <= range->getRangeEnd() && !stop; ++index) {
		m_sampler->setSampleIndex(index);
		const Emitter* emitter = NULL;
		const Medium* medium;
		Spectrum power;
		Ray ray;

		/***************************** Sunlit Leaf Calculation****************************************/
		ref_vector<Shape>& shapes = m_scene->getShapes();
		if (m_hasfSunlitLeafProducts && shapes.size() >= 2) {
			sampleShapePosition(m_scene, m_sampler->next2D(), m_sampler->next2D(), pShadeRec);
			// Trace a ray in sun direction
			//First, get the sun direction
			Ray shadeRay(pShadeRec.p, m_sunDirInv, ray.time);
			bool isShaded = isRepetitiveOcclude(shadeRay, m_scene, shadedIts);
			m_workResult->m_fSunlitLeafResult->put(pShadeRec.p, pShadeRec.object->getID(), isShaded);
		}

		//If no other product, skip the following 
		if (!(m_hasfPARProducts || m_hasFluorProducts || m_hasFluxMeasureProduct || m_hasBiochemicalProduct)) {
			continue;
		}

		/***************************** End OF Leaf Calculation****************************************/

		power = m_scene->sampleEmitterRay(ray, emitter,
			m_sampler->next2D(), m_sampler->next2D(), pRec.time);

		medium = emitter->getMedium();

		//Each Photon has a type, which can be used for different purpose.
		//BRF calculation needs repetitive, while up and down welling do not need
		int photoType = EPhotonType::ETypeNull;
		if (m_hasfPARProducts) photoType = photoType | ETypefPAR;
		if (m_hasFluorProducts) photoType = photoType | ETypeFluor;
		if (m_hasFluxMeasureProduct) photoType = photoType | ETypeFlux;
		if (m_hasBiochemicalProduct) photoType = photoType | ETypePS;

		if (m_hasfPARProducts || m_hasFluorProducts || m_hasFluxMeasureProduct || m_hasBiochemicalProduct) {
			//sample 一条光线后，首先判断是否是有效光线，即在场景的顶部
			//如果在场景顶部，则进入场景
			double H = ray.o[1] - m_sceneBounds.max.y;
			if (H >= 0) {
				double a = ray.d.x;
				double b = ray.d.y;
				double c = ray.d.z;
				Point its_p = ray.o + Point(-a / b * H, -H, -c / b * H);
				if (its_p.x >= m_sceneBounds.min.x && its_p.x <= m_sceneBounds.max.x
					&& its_p.z >= m_sceneBounds.min.z && its_p.z <= m_sceneBounds.max.z) {
					if (m_hasfPARProducts)
						m_workResult->m_fPARsWordResult->putIrradiance(power);
					if (m_hasFluorProducts)
						m_workResult->m_dirFluorAllWorkResult->putIrradiance(power);
				}
			}
			else {
				continue;
			}
		}

		int depth = 1, nullInteractions = 0;
		bool delta = false;
		const Medium* previousMedium = NULL;
		const Shape* previousShape = NULL;
		Point previousPoint = Point(std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity());
		Point hotspotStartPoint = Point(std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity());
		Vector previousRayDir = Vector(0, 1, 0);
		int previousStatus = 0; //计算再碰撞概率，前一个是不是地面 0 for nothing, 1 for terrain, 2 for vegetation
		bool isIntersectedWithTerrainAlready = false;
		Spectrum throughput(1.0f); // unitless path throughput (used for russian roulette)

		m.setFluorMatrixZeros();
		bool RayForFluor = false;

		std::vector<const Medium*> meeted_mediums;
		bool has_medium_in_single_path = false;
		Float rand = m_sampler->next1D();
		Float sampledTau = -math::fastlog(1 - rand);
		bool needReSampleTau = false;
		bool isReachHotspotPosition = false;
		while (!throughput.isZero() && (depth <= m_maxDepth || m_maxDepth < 0)) {
			rayIntersectExcludeEdge(ray, its);  //判断光线是否与场景包围盒以外的元素发生相交作用。
			int repetitiveTimes = 0;
			//如果需要计算BRF产品，且photon type正确，则计算. repetitive
			/*if ((m_hasfPARProducts && (photoType & EPhotonType::ETypefPAR)) ||
				(m_hasFluorProducts && (photoType & EPhotonType::ETypeFluor)) ||
				(m_hasFluxMeasureProduct && (photoType & EPhotonType::ETypeFlux)) ||
				(m_hasBiochemicalProduct && (photoType & EPhotonType::ETypePS)))*/
			if (m_repetitiveSceneNum != 0) {
				if (its.t == std::numeric_limits<Float>::infinity()) {
					for (int iteration = 0; iteration < m_repetitiveSceneNum; iteration++) {
						repetitiveTimes = iteration;
						Float tNear, tFar;
						int exitFace;
						Vector boundExtend = m_sceneBounds.getExtents();
						m_sceneBounds.rayIntersectExt(ray, tNear, tFar, exitFace);
						Point its_p = ray.o + tFar * ray.d;
						if (its_p.y < m_sceneBounds.max.y && exitFace != 1) {
							//offset the ray
							if (exitFace == 0) {
								if (ray.d.x > 0) {
									ray.o = its_p + Vector(-boundExtend.x, 0, 0);
								}
								else {
									ray.o = its_p + Vector(boundExtend.x, 0, 0);
								}
							}
							else if (exitFace == 2) {
								if (ray.d.z > 0) {
									ray.o = its_p + Vector(0, 0, -boundExtend.z);
								}
								else {
									ray.o = its_p + Vector(0, 0, boundExtend.z);
								}
							}
							rayIntersectExcludeEdge(ray, its);
							if (its.t < std::numeric_limits<Float>::infinity())
								break;
						}
						else {
							break;
						}
					}
				}//is infinity

			}//hasfPARProducts or hasFluorProducts

			Float sigmaT = 0;
			Spectrum singleAlbedo(0.0);
			FluorMatrix FluorsingleAlbedo; FluorsingleAlbedo.setFluorMatrixZeros();
			if (medium) {
				if (meeted_mediums.size() == 1) {
					sigmaT = medium->getVegetationSigmaT(ray);
					singleAlbedo = medium->getVegetationSingleAlbedo(ray);
					if (medium->getClass()->getName() == "VegFluorMedium") {
						FluorsingleAlbedo = medium->getFluorVegetationSingleAlbedo(ray);
					}
				}
				else {
					for (int i = 0; i < meeted_mediums.size(); ++i) {
						Float eachSigmaT = meeted_mediums[i]->getVegetationSigmaT(ray);
						sigmaT += eachSigmaT;
						singleAlbedo += eachSigmaT * meeted_mediums[i]->getVegetationSingleAlbedo(ray);
						if (meeted_mediums[i]->getClass()->getName() == "VegFluorMedium") {
							FluorMatrix eachFluorVegetationSingleAlbedo = meeted_mediums[i]->getFluorVegetationSingleAlbedo(ray);
							FluorsingleAlbedo.compute_PlusEqual_M1(eachFluorVegetationSingleAlbedo, eachSigmaT);
						}
					}
					if (sigmaT != 0) {
						singleAlbedo /= sigmaT;
						FluorsingleAlbedo.compute_DivideEqual(sigmaT);
					}
				}
			}
			if (medium && needReSampleTau) {
				sampledTau = -math::fastlog(1 - m_sampler->next1D()); //Reset the sampledTau
				needReSampleTau = false;
			}
			bool medium_sampleDistanceWithTotalTauSigmaTandAlbedo = false;
			if (medium) {
				if (medium->getClass()->getName() == "VegFluorMedium") {
					medium_sampleDistanceWithTotalTauSigmaTandAlbedo =
						medium->sampleDistanceWithTotalTauSigmaTandAlbedo(Ray(ray, 0, its.t), mRec, m_sampler, sampledTau, needReSampleTau, sigmaT, singleAlbedo, FluorsingleAlbedo);
				}
				else {
					medium_sampleDistanceWithTotalTauSigmaTandAlbedo =
						medium->sampleDistanceWithTotalTauSigmaTandAlbedo(Ray(ray, 0, its.t), mRec, m_sampler, sampledTau, needReSampleTau, sigmaT, singleAlbedo);
				}
			}
			if (medium && medium_sampleDistanceWithTotalTauSigmaTandAlbedo) {
				Float mRec_transmittance_mRec_pdfSuccess = mRec.transmittance[0] / mRec.pdfSuccess;
				if (m_hasFluorProducts) {
					if (medium->getClass()->getName() == "VegFluorMedium") {
						m.compute_Mb1xMb2_isFluor2Mixture_M1(throughput, mRec.FluorsigmaS, mRec.sigmaS, mRec_transmittance_mRec_pdfSuccess);
					}
					else {
						m.compute_Mb1xMb2_isNotFluor2Mixture_M1(mRec.sigmaS, mRec_transmittance_mRec_pdfSuccess);
					}
				}
				throughput *= mRec.sigmaS * mRec_transmittance_mRec_pdfSuccess;
				if (m_hasFluorProducts)
					handleMediumInteractionFluor(depth, nullInteractions, delta, its, ray, hotspotStartPoint, previousPoint, mRec, medium, meeted_mediums, -ray.d, throughput, power, photoType, m);
				PhaseFunctionSamplingRecord pRec(mRec, -ray.d, EImportance);
				//because phase functions are different for each bands, we simply use uniform distribution with weight equal to 1.
				Spectrum phaseweight;
				FluorMatrix phaseFluorweight;
				bool isVegFluorMedium = medium->getClass()->getName() == "VegFluorMedium";
				if (isVegFluorMedium) {
					phaseweight = medium->getPhaseFunction()->sampleEFSpec(pRec, m_sampler, phaseFluorweight);
				}
				else {
					phaseweight = medium->getPhaseFunction()->sampleSpec(pRec, m_sampler);
				}
				if (m_hasfPARProducts) {
					Spectrum throughput_power = throughput * power;
					Spectrum throughput_power_mRec_sigmaA_mRec_sigmaS = throughput_power * mRec.sigmaA / mRec.sigmaS;
					handleMediumInteractionFPAR(depth, mRec, throughput_power_mRec_sigmaA_mRec_sigmaS, photoType, its);
					if (m_hasFluorProducts && isVegFluorMedium) {
						Spectrum weightPSI(0.0), weightPSII(0.0);
						m.compute_MbxPower(power, weightPSI, weightPSII, throughput_power); weightPSI = Spectrum(0.0); weightPSII = Spectrum(0.0);
						//Spectrum mRec_sigmaS_inv = 1 / mRec.sigmaS;
						//std::vector<Float> invPS;
						//if (!mRec.FluorsigmaS.compute_Mb_T_inv(mRec.sigmaS, invPS)) {
						//	Log(EError, "Something wrong when inversing T in Mb at \"handleMediumInteractionMultiLevelFluor\"!");
						//}
						//FluorMatrix Mb_M_inv = phaseFluorweight.compute_Mb_M_inv(invPS, mRec.FluorsigmaS, mRec_sigmaS_inv, phaseweight);
						//phaseFluorweight.compute_Mb1xMb2_isFluor2Mixture(phaseweight, Mb_M_inv, mRec_sigmaS_inv);
						mRec.FluorsigmaS.compute_MbxPower(throughput_power, weightPSI, weightPSII);
						handleMediumInteractionMultiLevelFluor(depth, mRec, throughput_power_mRec_sigmaA_mRec_sigmaS, photoType, its
							, medium, weightPSI, weightPSII);
					}
				}
				if (isVegFluorMedium) {
					m.compute_Mb1xMb2_isFluor2Mixture(throughput, phaseFluorweight, phaseweight);
				}
				else {
					m.compute_Mb1xMb2_isNotFluor2Mixture(phaseweight);
				}
				throughput *= phaseweight;
				delta = false;

				ray = Ray(mRec.p, pRec.wo, ray.time);
				ray.mint = Epsilon;
				hotspotStartPoint = mRec.p;
				previousPoint = mRec.p;

			}//如果最大穿越场景次数之后，还是没有交点，则放弃
			else if (its.t == std::numeric_limits<Float>::infinity()) {
				if (m_hasFluorProducts)
					handleSurfaceInteractionFluor(depth, nullInteractions, delta, its, ray, hotspotStartPoint, previousPoint, medium, meeted_mediums, power, photoType, has_medium_in_single_path,
						throughput, m);
				break;
			}
			else {
				if (medium) {
					Float mRec_transmittance_mRec_pdfFailure = mRec.transmittance[0] / mRec.pdfFailure;
					if (mRec_transmittance_mRec_pdfFailure != 1) {
						m.compute_MultiplyEqual(mRec_transmittance_mRec_pdfFailure);
						throughput *= mRec_transmittance_mRec_pdfFailure;// mRec.transmittance / mRec.pdfFailure;
					}
				}
				//处理BRDF
				const BSDF* bsdf = its.getBSDF();
				BSDFSamplingRecord bRec(its, m_sampler, EImportance);
				Spectrum bsdfWeight;
				FluorMatrix tm; tm.setFluorMatrixZeros();
				bool isFluor2MixtureBSDF = bsdf->getClass()->getName() == "Fluor2MixtureBSDF";
				if (isFluor2MixtureBSDF) {
					RayForFluor = true;
					if (bsdf->getType() & BSDF::ENull) {
						bsdfWeight = bsdf->sampleWithEF(bRec, Point2(), bsdf->getFluorMatrixs(), tm); //bsdfWeight: 方向反射率
					}
					else {
						bsdfWeight = bsdf->sampleWithEF(bRec, m_sampler->next2D(), bsdf->getFluorMatrixs(), tm); //bsdfWeight: 方向反射率
						needReSampleTau = true;
					}
				}
				else {
					if (bsdf->getType() & BSDF::ENull) {
						bsdfWeight = bsdf->sample(bRec, Point2()); //bsdfWeight: 方向反射率
					}
					else {
						bsdfWeight = bsdf->sample(bRec, m_sampler->next2D()); //bsdfWeight: 方向反射率
						needReSampleTau = true;
					}
				}
				if (bsdfWeight == Spectrum(-1)) {// -1表示碰撞点位于单面材质的背面
					if (depth == 1) {
						break;
					}
					else {//多次散射时，如果碰到了底面，则停止
						its.t = std::numeric_limits<Float>::infinity();
						break;
					}
				}
				if (m_hasfPARProducts && !(bsdf->getType() & BSDF::ENull)) {
					Spectrum singleAbsorbtion = Spectrum(1.0) - bsdfWeight;
					Spectrum throughput_power = throughput * power;
					Spectrum throughput_power_singleAbsorbtion = throughput_power * singleAbsorbtion;
					handleSurfaceInteractionFPAR(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput_power_singleAbsorbtion, throughput_power, photoType, isIntersectedWithTerrainAlready);
					if (m_hasFluorProducts && isFluor2MixtureBSDF) {
						Spectrum weightPSI(0.0), weightPSII(0.0);
						m.compute_MbxPower(power, weightPSI, weightPSII, throughput_power); weightPSI = Spectrum(0.0); weightPSII = Spectrum(0.0);
						tm.compute_MbxPower(throughput_power, weightPSI, weightPSII);
						handleSurfaceInteractionMultiLevelFluor(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput_power_singleAbsorbtion, photoType, isIntersectedWithTerrainAlready,
							bsdf, weightPSI, weightPSII);
					}
				}
				if (m_hasBiochemicalProduct && !(bsdf->getType() & BSDF::ENull)) {
					if (its.shape->isBioemitter() && its.shape->getBioemitter()->get_palnt_type() != "-") {
						Spectrum singleAbsorbtion = Spectrum(1.0) - bsdfWeight;
						Spectrum throughput_power = throughput * power;
						Spectrum throughput_power_singleAbsorbtion = throughput_power * singleAbsorbtion;
						Ray shadeRay(its.p, m_sunDirInv, ray.time);
						bool isShaded = isRepetitiveOcclude(shadeRay, m_scene, shadedIts);
						Spectrum ChlrelAbsorbtion = throughput_power_singleAbsorbtion * its.shape->getBioemitter()->get_kChlrel();
						handleSurfaceInteractionPSproduct(depth, its, previousPoint, ChlrelAbsorbtion, photoType, isShaded);
					}
				}

				if (m_hasFluxMeasureProduct && (bsdf->getType() & BSDF::ENull) && bsdf->getID() == "-flux-") {
					handleSurfaceInteractionFluxMeasure(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput * power, photoType);
					if (m_hasFluorProducts) {
						Spectrum weightPSI(0.0), weightPSII(0.0);
						m.compute_MbxPower(power, weightPSI, weightPSII);
						handleSurfaceInteractionFluxMeasure4Fluor(depth, nullInteractions, delta, its, ray, previousPoint, medium, weightPSI, weightPSI, photoType);
					}
				}

				if (m_hasFluorProducts && !(bsdf->getType() & BSDF::ENull)) {
					handleSurfaceInteractionFluor(depth, nullInteractions, delta, its, ray, hotspotStartPoint, previousPoint, medium, meeted_mediums, power, photoType, has_medium_in_single_path,
						throughput, m);
				}

				if (bsdfWeight.isZero() || bsdfWeight.min() < 0) {
					break;
				}

				Vector wi = -ray.d, wo = its.toWorld(bRec.wo);
				Float wiDotGeoN = dot(its.geoFrame.n, wi),
					woDotGeoN = dot(its.geoFrame.n, wo);
				/*if (wiDotGeoN * Frame::cosTheta(bRec.wi) <= 0 ||
					woDotGeoN * Frame::cosTheta(bRec.wo) <= 0)
					break;*/
				if (isFluor2MixtureBSDF) {
					m.compute_Mb1xMb2_isFluor2Mixture(throughput, tm, bsdfWeight);
				}
				else {
					m.compute_Mb1xMb2_isNotFluor2Mixture(bsdfWeight);
				}
				throughput *= bsdfWeight;
				if (its.isMediumTransition()) {
					medium = its.getTargetMedium(woDotGeoN);
					std::string meeted_mediums_name = its.shape->getName();
					if (medium) {
						has_medium_in_single_path = true;
						meeted_mediums.emplace_back(medium);
					}
					else {
						if (meeted_mediums.size() == 1) {
							meeted_mediums.clear();
						}
						else if (meeted_mediums.size() > 1) {
							const Medium* tmp = its.getTargetMedium(-wo);
							//std::string tmp_name = meeted_mediums_name;
							auto itr = remove_if(meeted_mediums.begin(), meeted_mediums.end(), [&](const Medium* x) {return x == tmp; });
							if (itr >= meeted_mediums.begin() && itr < meeted_mediums.end()) {
								meeted_mediums.erase(itr);
								if (meeted_mediums.size() > 0) {
									medium = meeted_mediums[meeted_mediums.size() - 1];
								}
							}
						}
					}

					if (!medium) {
						if (its.shape != previousShape) {
							medium = previousMedium;
						}
					}
					previousMedium = medium;
				}

				//previousPoint = its.p;
				previousRayDir = ray.d;
				//Vector wo = its.toWorld(bRec.wo);
				ray.setOrigin(its.p);
				ray.setDirection(wo);
				ray.mint = Epsilon;



				string previousOjb = its.shape->getID();
				previousShape = its.shape;
				if (previousOjb == "terrain") {
					previousStatus = 1;
				}
				else {
					previousStatus = 2;
				}

				//If is null intersection, we do not increase depth
				if (bsdf->getType() & BSDF::ENull) {
					if (medium && !isReachHotspotPosition) {
						hotspotStartPoint = its.p;
						isReachHotspotPosition = true;
					}
					continue;
				}
				else {
					previousPoint = its.p;
				}

			}
			if (depth++ >= m_rrDepth) { //当深度超过了设置的最小深度时，采用Russian roulette方法决定是否停止
				Float q = std::min(throughput.max(), (Float)0.95f);
				if (m_sampler->next1D() >= q)
					break;
				throughput /= q;
				if (m_hasFluorProducts)
					if (m.isFluorMatrixNotZeros()) {
						//Float max_mi = 0; Float max_mii = 0;
						//for (register size_t i = 0.1860 * EXCITATION_SAMPLES; i < 0.5582 * EXCITATION_SAMPLES; ++i) {
						//	for (register size_t j = 0.6338 * FLUOR_SAMPLES; j < 0.8311 * FLUOR_SAMPLES; ++j) {
						//		max_mi = m.m_mi[i * FLUOR_SAMPLES + j] > max_mi ? m.m_mi[i * FLUOR_SAMPLES + j] : max_mi;
						//		max_mii = m.m_mi[i * FLUOR_SAMPLES + j] > max_mii ? m.m_mii[i * FLUOR_SAMPLES + j] : max_mii;
						//	}
						//}
						//for (int i = 0; i < EFM_LENGTH; i++) { m.m_mi[i] /= max_mi; m.m_mii[i] /= max_mii; 
						m.compute_DivideEqual(q);
					}
			}
		}
		if (RayForFluor)
			m_workResult->m_FluorPhotonsNum++;
	}
	m_workResult = NULL;
}

ref<WorkProcessor> CapturePhotonWorker::clone() const {
	return new CapturePhotonWorker(m_maxDepth,
		m_maxPathDepth, m_rrDepth, m_bruteForce,
		m_virtualDirections, m_numberOfDirections, m_virtualDetectorDirection,
		m_hasfPARProducts, m_layerDefinition, m_hasfSunlitLeafProducts,
		m_hasFluorProducts, m_wavelengths,
		m_hasFluxMeasureProduct, m_measureMode,
		m_hasBiochemicalProduct);
}

ref<WorkResult> CapturePhotonWorker::createWorkResult() const {
	const Film* film = m_sensor->getFilm();
	return new CapturePhotonWorkResult(film->getCropSize(), m_rfilter.get(), m_virtualDirections,
		m_numberOfDirections, m_virtualDetectorDirection, m_hasfPARProducts, m_layerDefinition, m_hasfSunlitLeafProducts,
		m_hasFluorProducts, m_FluorPhotonsNum, m_wavelengths,
		m_hasFluxMeasureProduct, m_measureMode,
		m_hasBiochemicalProduct);
}


bool CapturePhotonWorker::sampleDistanceWithRandomOpticalDepth(const Scene* scene, const Medium* medium, Ray& ray, MediumSamplingRecord& mRec,
	Sampler* sampler, Intersection& its) {
	Float rand = sampler->next1D();
	bool success = true;
	/*
	* Then, sample a random optical depth
	*/
	Float tau = -math::fastlog(1 - rand);
	Float remaining = tau;
	Float cumulatedDist = 0;
	Float transmittance = 1.0;
	bool isFirstIntersect = true; //For the first time, no intersection test is needed, because it has been provided by privious calculation
	while (remaining > 0) {
		bool intersected = true;
		if (!isFirstIntersect) {
			intersected = scene->rayIntersect(ray, its);
		}
		isFirstIntersect = false;
		if (!intersected) {
			for (int iter = 0; iter < m_repetitiveSceneNum; iter++) {
				Float tNear, tFar;
				int exitFace;
				Vector boundExtend = m_sceneBounds.getExtents();
				m_sceneBounds.rayIntersectExt(ray, tNear, tFar, exitFace);
				Point its_p = ray.o + tFar * ray.d;
				if (its_p.y < m_sceneBounds.max.y && exitFace != 1) {
					//repetitive ray tracing
					if (exitFace == 0) {
						if (ray.d.x > 0) {
							ray.o = its_p + Vector(-boundExtend.x, 0, 0);
						}
						else {
							ray.o = its_p + Vector(boundExtend.x, 0, 0);
						}
					}
					else if (exitFace == 2) {
						if (ray.d.z > 0) {
							ray.o = its_p + Vector(0, 0, -boundExtend.z);
						}
						else {
							ray.o = its_p + Vector(0, 0, boundExtend.z);
						}
					}
					/*if (m_scene->rayIntersect(occludeRay)) {*/
					if (scene->rayIntersect(ray, its)) {
						intersected = true;
						break;
					}
				}
				else {
					break;
				}
			}
		}//end if intersected

		if (!medium) {
			if (its.t == std::numeric_limits<Float>::infinity()) {
				success = false;
				break;
			}
			ray.o = ray(its.t);
			ray.maxt = std::numeric_limits<Float>::infinity();
			ray.mint = Epsilon;
			if (its.isMediumTransition()) {
				medium = its.getTargetMedium(ray.d);
			}
			continue;
		}


		Float distSurf = its.t - ray.mint;
		Float currSigmaT = medium->getVegetationSigmaT(ray);
		Spectrum currAlbedo = medium->getVegetationSingleAlbedo(ray);
		Float segmentTau = currSigmaT * distSurf;
		if (remaining <= segmentTau) { // successful generate interacton in this medium in range[0, distSurf]
			cumulatedDist += remaining / currSigmaT;
			success = true;
			mRec.t = cumulatedDist + ray.mint;
			mRec.p = ray(mRec.t);
			mRec.sigmaA = currSigmaT * (Spectrum(1.0) - currAlbedo);
			mRec.sigmaS = currSigmaT * currAlbedo;
			mRec.time = ray.time;
			mRec.medium = medium;
			/* Fail if there is no forward progress
			(e.g. due to roundoff errors) */
			if (mRec.p == ray.o)
				success = false;
			transmittance *= math::fastexp(-remaining);
			mRec.transmittance = Spectrum(transmittance);
			mRec.sampledPhaseFun = const_cast<PhaseFunction*>(medium->getPhaseFunction());
			mRec.pdfSuccess = mRec.pdfSuccessRev = currSigmaT * transmittance;
			break;
		}
		else { // If sampled tau is larger than the segment tau
			transmittance *= math::fastexp(-currSigmaT * distSurf);
			cumulatedDist += distSurf;
			remaining -= distSurf * currSigmaT;
			mRec.pdfFailure = transmittance;
			mRec.transmittance = Spectrum(transmittance);
			if (!(its.getBSDF()->getType() & BSDF::ENull)) {
				/* Encountered an occluder --*/
				success = false;
				break;
			}
			if (its.isMediumTransition()) {
				medium = its.getTargetMedium(ray.d);
			}
			//continue do tracing
			ray.o = ray(its.t);
			ray.maxt = std::numeric_limits<Float>::infinity();
			ray.mint = Epsilon;
		}
	}

	return success;
}

void CapturePhotonWorker::handleEmission(const PositionSamplingRecord& pRec,
	const Medium* medium, const Spectrum& weight) {
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

	const Emitter* emitter = static_cast<const Emitter*>(pRec.object);
	value *= emitter->evalDirection(DirectionSamplingRecord(dRec.d), pRec);

	/* Splat onto the accumulation buffer */
	//m_workResult->put(dRec.uv, (Float *)&value[0]);
}

void CapturePhotonWorker::handleSurfaceInteraction(int depth, int nullInteractions,
	bool caustic, const Intersection& its, const Medium* medium,
	const Spectrum& weight) {

	if (m_bruteForce || (depth >= m_maxPathDepth && m_maxPathDepth > 0))
		return;

	int maxInteractions = m_maxPathDepth - depth - 1;

	Vector2 relDist = m_subSceneUpperLeft - Vector2(its.p.x, its.p.z);
	Point2 uv = Point2(m_filmSize.x * relDist.x / (m_subSceneUpperLeft.x * 2), m_filmSize.y * relDist.y / (m_subSceneUpperLeft.y * 2));

	Spectrum re = weight;

	m_workResult->m_PhtonsEachProcess++;
}

void CapturePhotonWorker::handleSurfaceInteractionFPAR(int depth, int nullInteractions,
	bool delta, const Intersection& its, Ray& ray, Point& previousPoint, const Medium* medium,
	const Spectrum& weight, const Spectrum& incidentEnergy, int photoType, bool& isIntersectedWithTerrainAlready) {
	if (m_hasfPARProducts && (photoType & EPhotonType::ETypefPAR)) {
		if (m_virtualBounds.contains(its.p))
			m_workResult->m_fPARsWordResult->put(depth, its, previousPoint, weight, incidentEnergy, isIntersectedWithTerrainAlready);
	}

}

void CapturePhotonWorker::handleMediumInteractionFPAR(int depth, const MediumSamplingRecord& mRec,
	const Spectrum& weight, int photoType, Intersection& its) {
	if (m_hasfPARProducts && (photoType & EPhotonType::ETypefPAR)) {
		if (m_virtualBounds.contains(mRec.p))
			m_workResult->m_fPARsWordResult->put(depth, its, mRec, weight);
	}
}

void CapturePhotonWorker::handleSurfaceInteractionMultiLevelFluor(int depth, int nullInteractions,
	bool delta, const Intersection& its, Ray& ray, Point& previousPoint, const Medium* medium,
	const Spectrum& absorbedEnergy, int photoType, bool& isIntersectedWithTerrainAlready,
	const BSDF* bsdf, const Spectrum& excitePSIFluorEnergy, const Spectrum& excitePSIIFluorEnergy) {
	if (m_hasfPARProducts && (photoType & EPhotonType::ETypefPAR)) {
		if (m_virtualBounds.contains(its.p)) {//bsdf->getepsilon(its) * 
			m_workResult->m_multilevelFluorWorkResult->put(depth, its, previousPoint, absorbedEnergy, isIntersectedWithTerrainAlready,
				bsdf, excitePSIFluorEnergy, excitePSIIFluorEnergy);
		}
	}
}

void CapturePhotonWorker::handleSurfaceInteractionPSproduct(int depth, const Intersection& its, Point& previousPoint,
	Spectrum ChlAbsorb, int photoType, bool isShaded) {
	if (m_hasBiochemicalProduct && (photoType & EPhotonType::ETypePS)) {
		if (m_virtualBounds.contains(its.p)) {
			m_workResult->m_PSproductsWorkResult->put(depth, its, previousPoint, ChlAbsorb, isShaded);
		}
	}
}

void CapturePhotonWorker::handleMediumInteractionMultiLevelFluor(int depth, const MediumSamplingRecord& mRec,
	const Spectrum& weight, int photoType, Intersection& its,
	const Medium* medium, const Spectrum& excitePSIFluorEnergy, const Spectrum& excitePSIIFluorEnergy) {
	if (m_hasfPARProducts && (photoType & EPhotonType::ETypefPAR)) {
		if (m_virtualBounds.contains(mRec.p))
			m_workResult->m_multilevelFluorWorkResult->put(depth, its, mRec, weight,
				medium, excitePSIFluorEnergy, excitePSIIFluorEnergy);
	}
}

void CapturePhotonWorker::handleMediumInteractionFluor(int depth, int nullInteractions,
	bool delta, const Intersection& its, Ray& ray, Point& hotspotStartPoint, Point& previousPoint, MediumSamplingRecord mRec,
	const Medium* medium, std::vector<const Medium*>& meeted_mediums, const Vector& wi,
	Spectrum throughput, Spectrum power_e, int photoType,
	FluorMatrix m) {
	//since virtual direction will try to connect with sensor, when depth equals to 2, it actually
	// get second order scattering results,but for real photon, it is the first order.
	if (depth >= m_maxPathDepth && m_maxPathDepth > 0) {
		return;
	}
	Spectrum tpowerPSI(0.0f);
	Spectrum tpowerPSII(0.0f);
	Spectrum tpower(0.0f);
	if (m_workResult->m_dirFluorAllWorkResult->m_nVirtualDirections > 0) {
		tpower = throughput * power_e;
		m.compute_MbxPower(power_e, tpowerPSI, tpowerPSII, tpower);
	}
	//Evaluate a transmittance between the intersection point and sensor (infinity in virtual direction case)
	for (int i = 0; i < m_workResult->m_dirFluorAllWorkResult->m_nVirtualDirections; i++) {
		double dx = m_workResult->m_dirFluorAllWorkResult->m_virtualDirXYZ[3 * i];
		double dy = m_workResult->m_dirFluorAllWorkResult->m_virtualDirXYZ[3 * i + 1];
		double dz = m_workResult->m_dirFluorAllWorkResult->m_virtualDirXYZ[3 * i + 2];
		Vector wo = Vector(dx, dy, dz);
		Point p2 = mRec.p + 10000000.0 * wo;
		int maxNumberInteractions = 10000;
		Ray tray(mRec.p, wo, 0); // Please note that drcp should not be zero. Otherwise errorw will happend. shoule not use: Ray tray; tray.o = ; tray.d=;
		//Spectrum trans = evalTransmittance(mRec.p, false, p2, false, 0, medium, maxNumberInteractions, tray);
		Spectrum trans = evalTransmittanceWithHotspot(mRec.p, false,
			p2, false, 0, medium, meeted_mediums,
			maxNumberInteractions, ray, hotspotStartPoint, tray, depth, true);
		if (trans.isZero())
			continue;
		//virtual bounds
		double H = tray.o[1] - m_virtualBounds.max.y;
		double a = tray.d.x;
		double b = tray.d.y;
		double c = tray.d.z;
		Point itsP = tray.o + Point(-a / b * H, -H, -c / b * H);
		if (itsP.x >= m_virtualBounds.min.x && itsP.x <= m_virtualBounds.max.x
			&& itsP.z >= m_virtualBounds.min.z && itsP.z <= m_virtualBounds.max.z) {
			Spectrum phaseval(0.0);
			FluorMatrix phaseFluorVal; phaseFluorVal.setFluorMatrixZeros();

			const PhaseFunction* phase = medium->getPhaseFunction();
			PhaseFunctionSamplingRecord pRec(mRec, wi, wo, EImportance);
			//trans *= phase->eval(pRec);
			if (meeted_mediums.size() == 1) {
				if (medium->getClass()->getName() == "VegFluorMedium") {
					phaseval = phase->evalWithEF(pRec, phaseFluorVal);
				}
				else {
					phaseval = phase->eval(pRec);
				}
			}
			else {
				for (int i = 0; i < meeted_mediums.size(); ++i) {
					Float eachSigmaT = meeted_mediums[i]->getVegetationSigmaT(ray);
					Spectrum eachAlbedo = meeted_mediums[i]->getVegetationSingleAlbedo(ray);
					FluorMatrix eachFluorAlbedo;
					Spectrum eachphaseval;
					FluorMatrix eachphaseFluorVal;
					if (meeted_mediums[i]->getClass()->getName() == "VegFluorMedium") {
						eachFluorAlbedo = meeted_mediums[i]->getFluorVegetationSingleAlbedo(ray);
						eachphaseval = meeted_mediums[i]->getPhaseFunction()->evalWithEF(pRec, eachphaseFluorVal);
						phaseFluorVal.compute_PlusEqual_Mb1xMb2_isFluor2Mixture_M1(eachFluorAlbedo, eachAlbedo, eachphaseFluorVal, eachphaseval, eachSigmaT);
					}
					else {
						eachphaseval = meeted_mediums[i]->getPhaseFunction()->eval(pRec);
					}
					phaseval += eachSigmaT * eachAlbedo * eachphaseval;
				}

				Spectrum mRec_sigmaS_inv = 1 / mRec.sigmaS;
				std::vector<Float> invPS;
				if (!mRec.FluorsigmaS.compute_Mb_T_inv(mRec.sigmaS, invPS)) {
					Log(EError, "Something wrong when inversing T in Mb at \"handleMediumInteractionFluor\"!");
				}
				FluorMatrix Mb_M_inv = phaseFluorVal.compute_Mb_M_inv(invPS, mRec.FluorsigmaS, mRec_sigmaS_inv, phaseval);
				phaseFluorVal.compute_Mb1xMb2_isFluor2Mixture(phaseval, Mb_M_inv, mRec_sigmaS_inv);
				phaseval *= mRec_sigmaS_inv;
			}
			Spectrum powerPSI(0.0f);
			Spectrum powerPSII(0.0f);
			Spectrum power(0.0f);
			power = phaseval * tpower;
			phaseFluorVal.compute_MbxPower(tpower, powerPSI, powerPSII, power);
			if (tpowerPSI[FLUOR_0_INDEX] != 0 || tpowerPSII[FLUOR_0_INDEX] != 0) {
				m.compute_FluorSpectrum_PlusEqual_M1(powerPSI, powerPSII, phaseval, tpowerPSI, tpowerPSII);
			}
			if (trans[0] != 1 || trans[EXCITATION_MIN_INDEX] != 1 || trans[FLUOR_MIN_INDEX] != 1 || trans[SPECTRUM_SAMPLES - 1] != 1) {
				power *= trans;
				m.compute_FluorSpectrum_MultiplyEqual(powerPSI, powerPSII, trans);
			}
			m_workResult->m_dirFluorAllWorkResult->putVirtualFluor(depth, its, i, power, powerPSI, powerPSII, false);
		}
	}
}

static StatsCounter mediumInconsistencies("General", "Detected medium inconsistencies");
Spectrum CapturePhotonWorker::evalTransmittance(const Point& p1, bool p1OnSurface,
	const Point& p2, bool p2OnSurface, Float time, const Medium* medium,
	int& interactions, Ray& ray, Sampler* sampler) const {
	Vector d = p2 - p1;
	Float remaining = d.length();
	d /= remaining;

	Float lengthFactor = p2OnSurface ? (1 - ShadowEpsilon) : 1;
	ray.mint = p1OnSurface ? Epsilon : 0;
	ray.maxt = remaining * lengthFactor;
	ray.time = time;
	Spectrum transmittance(1.0f);
	Intersection its;
	int maxInteractions = interactions;
	interactions = 0;
	while (remaining > 0) {
		Normal n;
		bool intersected = m_scene->rayIntersect(ray, its);
		if (!intersected) {
			for (int iter = 0; iter < m_repetitiveSceneNum; iter++) {
				Float tNear, tFar;
				int exitFace;
				Vector boundExtend = m_sceneBounds.getExtents();
				m_sceneBounds.rayIntersectExt(ray, tNear, tFar, exitFace);
				Point its_p = ray.o + tFar * ray.d;
				if (its_p.y < m_sceneBounds.max.y && exitFace != 1) {
					//repetitive ray tracing
					if (exitFace == 0) {
						if (ray.d.x > 0) {
							ray.o = its_p + Vector(-boundExtend.x, 0, 0);
						}
						else {
							ray.o = its_p + Vector(boundExtend.x, 0, 0);
						}
					}
					else if (exitFace == 2) {
						if (ray.d.z > 0) {
							ray.o = its_p + Vector(0, 0, -boundExtend.z);
						}
						else {
							ray.o = its_p + Vector(0, 0, boundExtend.z);
						}
					}
					/*if (m_scene->rayIntersect(occludeRay)) {*/
					if (m_scene->rayIntersect(ray, its)) {
						intersected = true;
						break;
					}
				}
				else {
					break;
				}
			}
		}

		if (intersected && (interactions == maxInteractions ||
			!(its.getBSDF()->getType() & BSDF::ENull))) {
			/* Encountered an occluder -- zero transmittance. */
			return Spectrum(0.0f);
		}

		if (medium)
			transmittance *= medium->evalTransmittance(
				Ray(ray, 0, std::min(its.t, remaining)), sampler);
		if (!intersected || transmittance.isZero())
			break;

		const BSDF* bsdf = its.getBSDF();

		/*its.p = ray.o;
		its.geoFrame = Frame(its.geoFrame.n);
		its.hasUVPartials = false;*/
		Vector wo = its.geoFrame.toLocal(ray.d);
		BSDFSamplingRecord bRec(its, -wo, wo, ERadiance);
		bRec.typeMask = BSDF::ENull;
		transmittance *= bsdf->eval(bRec, EDiscrete);

		if (its.isMediumTransition()) {
			if (medium != its.getTargetMedium(-d)) {
				++mediumInconsistencies;
				return Spectrum(0.0f);
			}
			medium = its.getTargetMedium(d);
		}

		if (++interactions > 100) { /// Just a precaution..
			Log(EWarn, "evalTransmittance(): round-off error issues?");
			break;
		}

		ray.o = ray(its.t);
		remaining -= its.t;
		ray.maxt = remaining * lengthFactor;
		ray.mint = Epsilon;
	}

	return transmittance;
}

Spectrum CapturePhotonWorker::evalTransmittanceWithHotspot(const Point& p1, bool p1OnSurface,
	const Point& p2, bool p2OnSurface, Float time, const Medium* medium, std::vector<const Medium*> meeted_mediums,
	int& interactions, Ray& solarRay, Point& hotspotStartPoint, Ray& sensorRay, int depth, bool has_medium_in_single_path,
	Sampler* sampler) const {
	Vector d = p2 - p1;
	Float remaining = d.length();
	d /= remaining;
	bool consider_hotspot = true;
	if (!has_medium_in_single_path) {
		if (!medium)
			consider_hotspot = false;
	}

	Float lengthFactor = p2OnSurface ? (1 - ShadowEpsilon) : 1;
	sensorRay.mint = p1OnSurface ? Epsilon : 0;
	sensorRay.maxt = remaining * lengthFactor;
	sensorRay.time = time;
	Spectrum transmittance(1.0f);
	Intersection its;
	int maxInteractions = interactions;
	interactions = 0;
	Float maxRange = (hotspotStartPoint - sensorRay.o).length();
	while (remaining > 0) {
		Normal n;
		bool intersected = m_scene->rayIntersect(sensorRay, its);
		if (!intersected) {
			for (int iter = 0; iter < m_repetitiveSceneNum; iter++) {
				Float tNear, tFar;
				int exitFace;
				Vector boundExtend = m_sceneBounds.getExtents();
				m_sceneBounds.rayIntersectExt(sensorRay, tNear, tFar, exitFace);
				Point its_p = sensorRay.o + tFar * sensorRay.d;
				if (its_p.y < m_sceneBounds.max.y && exitFace != 1) {
					//repetitive ray tracing
					if (exitFace == 0) {
						if (sensorRay.d.x > 0) {
							sensorRay.o = its_p + Vector(-boundExtend.x, 0, 0);
						}
						else {
							sensorRay.o = its_p + Vector(boundExtend.x, 0, 0);
						}
					}
					else if (exitFace == 2) {
						if (sensorRay.d.z > 0) {
							sensorRay.o = its_p + Vector(0, 0, -boundExtend.z);
						}
						else {
							sensorRay.o = its_p + Vector(0, 0, boundExtend.z);
						}
					}
					/*if (m_scene->rayIntersect(occludeRay)) {*/
					if (m_scene->rayIntersect(sensorRay, its)) {
						intersected = true;
						break;
					}
				}
				else {
					break;
				}
			}
		}

		if (intersected && (interactions == maxInteractions ||
			!(its.getBSDF()->getType() & BSDF::ENull))) {
			/* Encountered an occluder -- zero transmittance. */
			return Spectrum(0.0f);
		}

		if (medium) {
			Float sigmaT = 0, GValueSensor = 0, GValueSolar = 0;
			if (meeted_mediums.size() == 1) {
				sigmaT = medium->getVegetationSigmaT(sensorRay);
				GValueSensor = medium->getVegetationG(sensorRay);
				GValueSolar = medium->getVegetationG(solarRay);
			}
			else {
				for (int i = 0; i < meeted_mediums.size(); ++i) {
					Float eachSigmaT = meeted_mediums[i]->getVegetationSigmaT(sensorRay);
					sigmaT += eachSigmaT;
					GValueSensor += eachSigmaT * meeted_mediums[i]->getVegetationG(sensorRay);
					GValueSolar += eachSigmaT * meeted_mediums[i]->getVegetationG(solarRay);
				}
				GValueSolar /= sigmaT;
				GValueSensor /= sigmaT;
			}
			if (depth == 1 && consider_hotspot) {
				Spectrum tmp = medium->evalTransmittanceWithHotspotWithSigmaT(solarRay,
					Ray(sensorRay, 0, std::min(its.t, remaining)), p1, p1OnSurface, maxRange, sigmaT, GValueSensor, GValueSolar, sampler);
				transmittance *= tmp;
			}
			else {
				/*transmittance *= medium->evalTransmittance(
					Ray(sensorRay, 0, std::min(its.t, remaining)), sampler);*/
				Float negLength = -std::min(its.t, remaining);
				Float tmp = sigmaT != 0 ? math::fastexp(sigmaT * negLength) : (Float)1.0f;
				transmittance *= tmp;
			}

		}

		if (!intersected || transmittance.isZero())
			break;

		const BSDF* bsdf = its.getBSDF();

		/*its.p = sensorRay.o;
		its.geoFrame = Frame(its.geoFrame.n);
		its.hasUVPartials = false;*/
		Vector wo = its.geoFrame.toLocal(sensorRay.d);
		BSDFSamplingRecord bRec(its, -wo, wo, ERadiance);
		bRec.typeMask = BSDF::ENull;
		Spectrum tmp = bsdf->eval(bRec, EDiscrete);
		transmittance *= tmp;
		if (its.isMediumTransition()) {
			medium = its.getTargetMedium(d);
			if (medium) {
				meeted_mediums.emplace_back(medium);
			}
			else {
				if (meeted_mediums.size() == 1) {
					meeted_mediums.clear();
				}
				else if (meeted_mediums.size() > 0) {
					const Medium* tmp = its.getTargetMedium(-d);
					auto itr = remove_if(meeted_mediums.begin(), meeted_mediums.end(), [&](const Medium* x) {return x == tmp; });
					if (itr >= meeted_mediums.begin() && itr < meeted_mediums.end()) {
						meeted_mediums.erase(itr);
						if (meeted_mediums.size() > 0) {
							medium = meeted_mediums[meeted_mediums.size() - 1];
						}
					}
				}

			}
		}

		if (++interactions > 100) { /// Just a precaution..
			Log(EWarn, "evalTransmittance(): round-off error issues?");
			break;
		}

		sensorRay.o = sensorRay(its.t);
		remaining -= its.t;
		sensorRay.maxt = remaining * lengthFactor;
		sensorRay.mint = Epsilon;
	}

	return transmittance;
}

Spectrum CapturePhotonWorker::evalTransmittanceWithHotspot(const Point& p1, bool p1OnSurface,
	const Point& p2, bool p2OnSurface, Float time, const Medium* medium,
	int& interactions, Ray& solarRay, Point& hotspotStartPoint, Ray& sensorRay, int depth, bool has_medium_in_single_path, Sampler* sampler) const {
	Vector d = p2 - p1;
	Float remaining = d.length();
	d /= remaining;

	bool consider_hotspot = true;
	if (!has_medium_in_single_path) {
		if (!medium)
			consider_hotspot = false;
	}

	Float lengthFactor = p2OnSurface ? (1 - ShadowEpsilon) : 1;
	sensorRay.mint = p1OnSurface ? Epsilon : 0;
	sensorRay.maxt = remaining * lengthFactor;
	sensorRay.time = time;
	Spectrum transmittance(1.0f);
	Intersection its;
	int maxInteractions = interactions;
	interactions = 0;
	Float maxRange = (hotspotStartPoint - sensorRay.o).length();
	while (remaining > 0) {
		Normal n;
		bool intersected = m_scene->rayIntersect(sensorRay, its);
		if (!intersected) {
			for (int iter = 0; iter < m_repetitiveSceneNum; iter++) {
				Float tNear, tFar;
				int exitFace;
				Vector boundExtend = m_sceneBounds.getExtents();
				m_sceneBounds.rayIntersectExt(sensorRay, tNear, tFar, exitFace);
				Point its_p = sensorRay.o + tFar * sensorRay.d;
				if (its_p.y < m_sceneBounds.max.y && exitFace != 1) {
					//repetitive ray tracing
					if (exitFace == 0) {
						if (sensorRay.d.x > 0) {
							sensorRay.o = its_p + Vector(-boundExtend.x, 0, 0);
						}
						else {
							sensorRay.o = its_p + Vector(boundExtend.x, 0, 0);
						}
					}
					else if (exitFace == 2) {
						if (sensorRay.d.z > 0) {
							sensorRay.o = its_p + Vector(0, 0, -boundExtend.z);
						}
						else {
							sensorRay.o = its_p + Vector(0, 0, boundExtend.z);
						}
					}
					/*if (m_scene->rayIntersect(occludeRay)) {*/
					if (m_scene->rayIntersect(sensorRay, its)) {
						intersected = true;
						break;
					}
				}
				else {
					break;
				}
			}
		}

		if (intersected && (interactions == maxInteractions ||
			!(its.getBSDF()->getType() & BSDF::ENull))) {
			/* Encountered an occluder -- zero transmittance. */
			return Spectrum(0.0f);
		}

		if (medium) {
			if (depth == 1 && consider_hotspot) {
				transmittance *= medium->evalTransmittanceWithHotspot(solarRay,
					Ray(sensorRay, 0, std::min(its.t, remaining)), p1, p1OnSurface, maxRange, sampler);
			}
			else {
				transmittance *= medium->evalTransmittance(
					Ray(sensorRay, 0, std::min(its.t, remaining)), sampler);
			}

		}

		if (!intersected || transmittance.isZero())
			break;

		const BSDF* bsdf = its.getBSDF();

		/*its.p = sensorRay.o;
		its.geoFrame = Frame(its.geoFrame.n);
		its.hasUVPartials = false;*/
		Vector wo = its.geoFrame.toLocal(sensorRay.d);
		BSDFSamplingRecord bRec(its, -wo, wo, ERadiance);
		bRec.typeMask = BSDF::ENull;
		transmittance *= bsdf->eval(bRec, EDiscrete);

		if (its.isMediumTransition()) {
			if (medium != its.getTargetMedium(-d)) {
				++mediumInconsistencies;
				return Spectrum(0.0f);
			}
			medium = its.getTargetMedium(d);
		}

		if (++interactions > 100) { /// Just a precaution..
			Log(EWarn, "evalTransmittance(): round-off error issues?");
			break;
		}

		sensorRay.o = sensorRay(its.t);
		remaining -= its.t;
		sensorRay.maxt = remaining * lengthFactor;
		sensorRay.mint = Epsilon;
	}

	return transmittance;
}

//扩展版本，可以得到上一个交点的信息
void CapturePhotonWorker::handleSurfaceInteractionFluor(int depth, int nullInteractions,
	bool delta, const Intersection& its, Ray& ray, Point& hotspotStartPoint, Point& previousPoint, const Medium* medium, std::vector<const Medium*>& meeted_mediums,
	Spectrum power_e, int photoType, bool has_medium_in_single_path,
	Spectrum throughput, FluorMatrix m) {

	//if (m_bruteForce || (depth >= m_maxPathDepth && m_maxPathDepth > 0))
	//	return;
	int maxInteractions = m_maxPathDepth - depth - 1;

	//Fluor Products
	if (photoType & EPhotonType::ETypeFluor) {
		//Fluor 如果没有交点,则记录Fluor值
		if (its.t == std::numeric_limits<Float>::infinity()) {
			Spectrum powerPSI(0.0f);
			Spectrum powerPSII(0.0f);
			Spectrum power = throughput * power_e;
			m.compute_MbxPower(power_e, powerPSI, powerPSII, power);
			if (ray.d.y >= 0) {
				double H = ray.o[1] - m_sceneBounds.max.y;
				if (H <= 0) {
					double a = ray.d.x;
					double b = ray.d.y;
					double c = ray.d.z;
					Point its_p = ray.o + Point(-a / b * H, -H, -c / b * H);
					if (its_p.x >= m_virtualBounds.min.x && its_p.x <= m_virtualBounds.max.x
						&& its_p.z >= m_virtualBounds.min.z && its_p.z <= m_virtualBounds.max.z) {
						//determine the zentih and azimuth angle according to ray direction
						double zenithAngle = math::safe_acos(ray.d.y);
						double AzimuthAngle = 0.5 * PHRT_M_PI - atan2(ray.d.z, -ray.d.x);
						if (AzimuthAngle < 0) AzimuthAngle += 2 * PHRT_M_PI;
						int zenithIndex; int aziIndex; bool angularDir_isInside;
						m_workResult->m_dirFluorAllWorkResult->put(zenithAngle, AzimuthAngle, power, powerPSI, powerPSII);
					}
				}
			}
		}
		else { //handling virtual directions
			//since virtual direction will try to connect with sensor, when depth equals to 2, it actually
			// get second order scattering results,but for real photon, it is the first order.
			if (depth >= m_maxPathDepth && m_maxPathDepth > 0) {
				return;
			}
			Spectrum tpowerPSI(0.0f);
			Spectrum tpowerPSII(0.0f);
			Spectrum tpower = throughput * power_e;
			m.compute_MbxPower(power_e, tpowerPSI, tpowerPSII, tpower);
			// At the intersected point, calculating the contribution of a photon tewards the virtual direction
			//First, determine whether the point has been occluded.
			const BSDF* bsdf = its.getBSDF();
			for (int i = 0; i < m_workResult->m_dirFluorAllWorkResult->m_nVirtualDirections; i++) {
				double dx = m_workResult->m_dirFluorAllWorkResult->m_virtualDirXYZ[3 * i];
				double dy = m_workResult->m_dirFluorAllWorkResult->m_virtualDirXYZ[3 * i + 1];
				double dz = m_workResult->m_dirFluorAllWorkResult->m_virtualDirXYZ[3 * i + 2];
				Vector wo = Vector(dx, dy, dz);
				Point p2 = its.p + 10000000.0 * wo;
				int maxNumberInteractions = 10000;
				Ray tray(its.p, wo, 0); // do not use: ray ray.p = p, ray.wo=wo,otherwise ray.drcp will be invalid
				//Spectrum trans = evalTransmittance(its.p, true, p2, false, 0, medium, maxNumberInteractions, tray);
				Spectrum trans = evalTransmittanceWithHotspot(its.p, true,
					p2, false, 0, medium, meeted_mediums,
					maxNumberInteractions, ray, hotspotStartPoint, tray, depth, has_medium_in_single_path);
				if (trans.isZero())
					continue;

				//virtual bounds
				double H = tray.o[1] - m_virtualBounds.max.y;
				double a = tray.d.x;
				double b = tray.d.y;
				double c = tray.d.z;
				Point itsP = tray.o + Point(-a / b * H, -H, -c / b * H);
				if (itsP.x >= m_virtualBounds.min.x && itsP.x <= m_virtualBounds.max.x
					&& itsP.z >= m_virtualBounds.min.z && itsP.z <= m_virtualBounds.max.z) {
					BSDFSamplingRecord bRec(its, its.toLocal(wo), EImportance);
					Spectrum powerPSI(0.0f);
					Spectrum powerPSII(0.0f);
					Spectrum power(0.0f);
					FluorMatrix m2sensor;
					if (bsdf->getClass()->getName() == "Fluor2MixtureBSDF") {
						Spectrum bsdfWeight = bsdf->evalWithEF(bRec, bsdf->getFluorMatrixs(), m2sensor);
						power = bsdfWeight * tpower;
						m2sensor.compute_MbxPower(tpower, powerPSI, powerPSII, power);
						if (tpowerPSI[FLUOR_0_INDEX] != 0 || tpowerPSII[FLUOR_0_INDEX] != 0) {
							m2sensor.compute_FluorSpectrum_PlusEqual_M1(powerPSI, powerPSII, bsdfWeight, tpowerPSI, tpowerPSII);
						}
						if (trans[0] != 1 || trans[EXCITATION_MIN_INDEX] != 1 || trans[FLUOR_MIN_INDEX] != 1 || trans[SPECTRUM_SAMPLES - 1] != 1) {
							power *= trans;
							m2sensor.compute_FluorSpectrum_MultiplyEqual(powerPSI, powerPSII, trans);
						}
					}
					else {
						Spectrum trans_eval_bRec;
						if (trans[0] == 1 && trans[EXCITATION_MIN_INDEX] == 1 && trans[FLUOR_MIN_INDEX] == 1 && trans[SPECTRUM_SAMPLES - 1] == 1)
							trans_eval_bRec = bsdf->eval(bRec);
						else
							trans_eval_bRec = trans * bsdf->eval(bRec);
						power = trans_eval_bRec * tpower;
						if (tpowerPSI[FLUOR_0_INDEX] != 0 || tpowerPSII[FLUOR_0_INDEX] != 0)
							m2sensor.compute_FluorSpectrum_Equal_M1(powerPSI, powerPSII, trans_eval_bRec, tpowerPSI, tpowerPSII);
					}
					m_workResult->m_dirFluorAllWorkResult->putVirtualFluor(depth, its, i, power, powerPSI, powerPSII, false);
				}
			}
		}//end of virtual direction
	}
}

void CapturePhotonWorker::handleSurfaceInteractionFluxMeasure(int depth, int nullInteractions,
	bool delta, const Intersection& its, Ray& ray, Point& previousPoint, const Medium* medium,
	const Spectrum& weight, int photoType) {
	if (dot(ray.d, its.geoFrame.n) <= 0) {  //front
		m_workResult->m_fluxMeasureProduct->put_flux(depth, its, weight, true);
	}
	else {
		m_workResult->m_fluxMeasureProduct->put_flux(depth, its, weight, false);
	}
}

void CapturePhotonWorker::handleSurfaceInteractionFluxMeasure4Fluor(int depth, int nullInteractions,
	bool delta, const Intersection& its, Ray& ray, Point& previousPoint, const Medium* medium,
	const Spectrum& weightPSI, const Spectrum& weightPSII, int pchotoType) {
	if (dot(ray.d, its.geoFrame.n) <= 0) {  //front
		m_workResult->m_fluxMeasureProduct->put_flux_fluor(depth, its, weightPSI, weightPSII, true);
	}
	else {
		m_workResult->m_fluxMeasureProduct->put_flux_fluor(depth, its, weightPSI, weightPSII, false);
	}
}

void CapturePhotonWorker::handleMediumInteraction(int depth, int nullInteractions, bool caustic,
	const MediumSamplingRecord& mRec, const Medium* medium, const Vector& wi,
	const Spectrum& weight) {
}



/* ==================================================================== */
/*                        Parallel process impl.                        */
/* ==================================================================== */

void CapturePhotonProcess::develop() {

	m_queue->signalRefresh(m_job);

	if (m_hasfPARProducts)
		m_fPARs->develop(1 / (Float)m_receivedResultCount);

	if (m_hasFluxMeasureProduct) {
		m_fluxMeasureProduct->develop(1 / (Float)m_receivedResultCount);
	}

	if (m_hasfSunlitLeafProducts) {
		m_fSunlitLeafProduct->develop();
	}

	//save Fluor
	if (m_hasFluorProducts) {
		m_dirFluors_All->develop(m_hasFluorProducts, 1 / (Float)m_receivedResultCount);
		if (m_hasfPARProducts) {
			m_MultiLevelFluor->develop(m_hasFluorProducts, 1000 / (Float)m_receivedResultCount);//for mW
		}
		if (m_hasFluxMeasureProduct) {
			m_fluxMeasureProduct->develop4Fluor(1000 / (Float)m_receivedResultCount);//for mW
		}
	}
	if (m_hasBiochemicalProduct) {
		m_PSproducts->develop(m_scene->getBioemitters(), m_hasFluorProducts, m_AtsPressure, m_AtsCO2, m_AtsO2, 1 / (Float)m_receivedResultCount);
	}
}

void CapturePhotonProcess::processResult(const WorkResult* wr, bool cancelled) {
	const CapturePhotonWorkResult* result
		= static_cast<const CapturePhotonWorkResult*>(wr);
	const RangeWorkUnit* range = result->getRangeWorkUnit();
	if (cancelled)
		return;

	LockGuard lock(m_resultMutex);
	increaseResultCount(range->getSize(), result->m_FluorPhotonsNum);

	if (m_hasfPARProducts)
		m_fPARs->merge(result->m_fPARsWordResult.get());

	if (m_hasFluorProducts) {
		m_dirFluors_All->merge(result->m_dirFluorAllWorkResult.get());
		if (m_hasfPARProducts) {
			m_MultiLevelFluor->merge(result->m_multilevelFluorWorkResult.get());
		}
	}

	if (m_hasFluxMeasureProduct) {
		m_fluxMeasureProduct->merge(result->m_fluxMeasureProduct.get());
	}

	if (m_hasfSunlitLeafProducts)
		m_fSunlitLeafProduct->merge(result->m_fSunlitLeafResult.get());

	if (m_hasBiochemicalProduct)
		m_PSproducts->merge(result->m_PSproductsWorkResult.get());

	if (m_job->isInteractive() || m_receivedResultCount == m_workCount)
		develop();
}

void CapturePhotonProcess::bindResource(const std::string& name, int id) {
	if (name == "scene") {
		m_scene = static_cast<Scene*>(Scheduler::getInstance()->getResource(id));
	}

	if (name == "sensor") {
		AABB scene_bound = m_scene->getKDTree()->getAABB();
		Properties inegratorProps = m_scene->getIntegrator()->getProperties();
		double sceneBoundX = inegratorProps.getFloat("subSceneXSize", scene_bound.getExtents().x);
		double scenBoundZ = inegratorProps.getFloat("subSceneZSize", scene_bound.getExtents().z);

		std::string scene_height = std::to_string(scene_bound.getExtents().y);
		cout << "INFO: Scene Height: " << scene_height << endl;

		//*********************************fPAR***************************************
		//create products for fpar
		if (m_hasfPARProducts) {
			m_layerDefinition = m_scene->getIntegrator()->getProperties().getString("LayerDefinition", "0:" + scene_height + ":" + scene_height + "/2");
			m_fPARs = new fPARProduct(m_layerDefinition, 1);
			m_fPARs->setDestinationFile(m_scene->getDestinationFile().string() + "_Layer_fPAR.txt");
			m_fPARs->setWavelengths(m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths"));
			m_fPARs->m_boolOutParEachBand = m_boolOutParEachBand;

			m_fPARs->setSceneBoundPlaneSize(Vector2(sceneBoundX, scenBoundZ));
			if (inegratorProps.getBoolean("SceneVirtualPlane", false)) {
				double vSizeX = inegratorProps.getFloat("sizex", sceneBoundX);
				double vSizeZ = inegratorProps.getFloat("sizez", scenBoundZ);
				m_fPARs->setVirtualBoundXZSize(Vector2(vSizeX, vSizeZ));
			}
			else {
				m_fPARs->setVirtualBoundXZSize(Vector2(sceneBoundX, scenBoundZ));
			}
		}

		if (m_hasFluxMeasureProduct) {
			m_measureMode = m_scene->getIntegrator()->getProperties().getString("measureMode", "");
			m_fluxMeasureProduct = new FluxMeasureProduct(m_measureMode);
			m_fluxMeasureProduct->setDestinationFile(m_scene->getDestinationFile().string() + "_FluxMeasure.txt");
			m_fluxMeasureProduct->setWavelengths(m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths"));
		}

		if (m_hasfSunlitLeafProducts) {
			m_layerDefinition = m_scene->getIntegrator()->getProperties().getString("LayerDefinition", "0:" + scene_height + ":" + scene_height + "/2");
			m_fSunlitLeafProduct = new fSunlitLeafProduct(m_layerDefinition);
			m_fSunlitLeafProduct->setDestinationFile(m_scene->getDestinationFile().string() + "_Layer_fSunlitLeaf.txt");
		}
		//*************************Fluor******************************
		if (m_hasFluorProducts) {
			m_dirFluors_All = new DirectionalFluor(m_numberOfDirections);
			//get scene Size
			if (m_scene->getIntegrator()->getProperties().hasProperty("isThermal") &&
				m_scene->getIntegrator()->getProperties().getBoolean("isThermal")) {
				m_dirFluors_All->setDestinationFile(m_scene->getDestinationFile().string() + "_BT_Fluor.txt");
				m_dirFluors_All->setWavelengths(m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths"));
				m_dirFluors_All->setCalculationMode(true);
			}
			else {
				m_dirFluors_All->setDestinationFile(m_scene->getDestinationFile().string() + "_Fluor_All.txt");
				m_dirFluors_All->setInfoDestinationFile(m_scene->getDestinationFile().string() + "_LESS_Fluor.txt");
				m_dirFluors_All->setWavelengths(m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths"));
				m_dirFluors_All->setCalculationMode(false);
			}

			m_dirFluors_All->setSceneBoundPlaneSize(Vector2(sceneBoundX, scenBoundZ));
			if (inegratorProps.getBoolean("SceneVirtualPlane", false)) {
				double vSizeX = inegratorProps.getFloat("sizex", sceneBoundX);
				double vSizeZ = inegratorProps.getFloat("sizez", scenBoundZ);
				m_dirFluors_All->setVirtualBoundXZSize(Vector2(vSizeX, vSizeZ));
			}
			else {
				m_dirFluors_All->setVirtualBoundXZSize(Vector2(sceneBoundX, scenBoundZ));
			}

			//read virtual direction
			m_virtualDirections = m_scene->getIntegrator()->getProperties().getString("virtualDirections", "");
			m_virtualDetectorDirection = m_scene->getIntegrator()->getProperties().getString("virtualDetectorDirections", "");
			m_dirFluors_All->readVirtualDirections(m_virtualDirections);
			m_dirFluors_All->readVirtualDetectors(m_virtualDetectorDirection);

			if (m_hasfPARProducts) {
				m_wavelengths = m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths");
				m_MultiLevelFluor = new MultiLevelFluor(m_layerDefinition, m_wavelengths);
				m_MultiLevelFluor->setDestinationFile(m_scene->getDestinationFile().string() + "_Layer_MultiLevelFluor.txt");
				//m_MultiLevelFluor->setWavelengths(m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths"));

				m_MultiLevelFluor->setSceneBoundPlaneSize(Vector2(sceneBoundX, scenBoundZ));
				if (inegratorProps.getBoolean("SceneVirtualPlane", false)) {
					double vSizeX = inegratorProps.getFloat("sizex", sceneBoundX);
					double vSizeZ = inegratorProps.getFloat("sizez", scenBoundZ);
					m_MultiLevelFluor->setVirtualBoundXZSize(Vector2(vSizeX, vSizeZ));
				}
				else {
					m_MultiLevelFluor->setVirtualBoundXZSize(Vector2(sceneBoundX, scenBoundZ));
				}
			}
		}
		if (m_hasBiochemicalProduct) {
			m_layerDefinition = m_scene->getIntegrator()->getProperties().getString("LayerDefinition", "0:" + scene_height + ":" + scene_height + "/2");
			m_wavelengths = m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths");
			m_AtsCO2 = m_scene->getIntegrator()->getProperties().getFloat("AtsCO2", 380);
			m_AtsO2 = m_scene->getIntegrator()->getProperties().getFloat("AtsO2", 209);
			m_AtsPressure = m_scene->getIntegrator()->getProperties().getFloat("AtsPressure", 970);
			m_PSproducts = new photonsynthesisProduct(m_layerDefinition, m_wavelengths);
			m_PSproducts->setDestinationFile(m_scene->getDestinationFile().string() + "_photosynthesis");

			m_PSproducts->setSceneBoundPlaneSize(Vector2(sceneBoundX, scenBoundZ));
			if (inegratorProps.getBoolean("SceneVirtualPlane", false)) {
				double vSizeX = inegratorProps.getFloat("sizex", sceneBoundX);
				double vSizeZ = inegratorProps.getFloat("sizez", scenBoundZ);
				m_PSproducts->setVirtualBoundXZSize(Vector2(vSizeX, vSizeZ));
			}
			else {
				m_PSproducts->setVirtualBoundXZSize(Vector2(sceneBoundX, scenBoundZ));
			}
		}
	}
	PhotonProcess::bindResource(name, id);
}

ref<WorkProcessor> CapturePhotonProcess::createWorkProcessor() const {
	return new CapturePhotonWorker(m_maxDepth, m_maxPathDepth,
		m_rrDepth, m_bruteForce,
		m_virtualDirections, m_numberOfDirections, m_virtualDetectorDirection,
		m_hasfPARProducts, m_layerDefinition, m_hasfSunlitLeafProducts,
		m_hasFluorProducts, m_wavelengths,
		m_hasFluxMeasureProduct, m_measureMode,
		m_hasBiochemicalProduct);
}


MTS_IMPLEMENT_CLASS(CapturePhotonProcess, false, PhotonProcess)
MTS_IMPLEMENT_CLASS(CapturePhotonWorkResult, false, WorkResult)
MTS_IMPLEMENT_CLASS_S(CapturePhotonWorker, false, PhotonTracer)

MTS_NAMESPACE_END