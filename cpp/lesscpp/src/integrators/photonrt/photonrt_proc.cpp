
#include "photonrt_proc.h"
#include <mitsuba/core/plugin.h>

MTS_NAMESPACE_BEGIN
/* ==================================================================== */
/*                           Work result impl.                          */
/* ==================================================================== */
void CapturePhotonWorkResult::load(Stream *stream) {
	size_t nEntries = (size_t)(m_downwellingWorkResult->getSize().x) * (size_t)(m_downwellingWorkResult->getSize().y);
	stream->readFloatArray(reinterpret_cast<Float *>(m_downwellingWorkResult->getBitmap()->getFloatData()),
		nEntries * SPECTRUM_SAMPLES);
	stream->readFloatArray(reinterpret_cast<Float *>(m_upwellingWorkResult->getBitmap()->getFloatData()),
		nEntries * SPECTRUM_SAMPLES);
	m_range->load(stream);
	m_PhtonsEachProcess = stream->readSize();
	m_hasBRFProducts = stream->readBool();
	if (m_hasBRFProducts)
		m_dirBRFWorkResult->unserialize(stream);
	m_hasUpDownProducts = stream->readBool();
	m_numberOfDirections = stream->readInt();
	m_hasfPARProducts = stream->readBool();
	if (m_hasfPARProducts)
		m_fPARsWordResult->unserialize(stream);
}

void CapturePhotonWorkResult::save(Stream *stream) const {
	//save ImageBlock m_downwellingWorkResult and m_upwellingWorkResult
	size_t nEntries = (size_t)(m_downwellingWorkResult->getSize().x) * (size_t)(m_downwellingWorkResult->getSize().y);
	stream->writeFloatArray(reinterpret_cast<const Float *>(m_downwellingWorkResult->getBitmap()->getFloatData()),
		nEntries * SPECTRUM_SAMPLES);
	stream->writeFloatArray(reinterpret_cast<const Float *>(m_upwellingWorkResult->getBitmap()->getFloatData()),
		nEntries * SPECTRUM_SAMPLES);
	m_range->save(stream);
	stream->writeSize(m_PhtonsEachProcess);
	stream->writeBool(m_hasBRFProducts);
	if (m_hasBRFProducts)
		m_dirBRFWorkResult->serialize(stream);
	stream->writeBool(m_hasUpDownProducts);
	stream->writeInt(m_numberOfDirections);
	stream->writeBool(m_hasfPARProducts);
	if (m_hasfPARProducts)
		m_fPARsWordResult->serialize(stream);
}


/* ==================================================================== */
/*                         Work processor impl.                         */
/* ==================================================================== */
CapturePhotonWorker::CapturePhotonWorker(Stream *stream, InstanceManager *manager)
	: PhotonTracer(stream, manager) {
	m_maxPathDepth = stream->readInt();
	m_bruteForce = stream->readBool();
	m_hasBRFProducts = stream->readBool();
	m_hasUpDownProducts = stream->readBool();
	m_numberOfDirections = stream->readInt();
	m_hasfPARProducts = stream->readBool();
}

void CapturePhotonWorker::serialize(Stream *stream, InstanceManager *manager) const {
	PhotonTracer::serialize(stream, manager);
	stream->writeInt(m_maxPathDepth);
	stream->writeBool(m_bruteForce);
	stream->writeBool(m_hasBRFProducts);
	stream->writeBool(m_hasUpDownProducts);
	stream->writeInt(m_numberOfDirections);
	stream->writeBool(m_hasfPARProducts);
}

void CapturePhotonWorker::prepare() {
	PhotonTracer::prepare();
	m_sensor = static_cast<Sensor *>(getResource("sensor"));
	m_rfilter = m_sensor->getFilm()->getReconstructionFilter();

	AABB scene_bound = m_scene->getKDTree()->getAABB();

	Properties integratorProps = m_scene->getIntegrator()->getProperties();

	m_subSceneUpperLeft = Vector2(integratorProps.getFloat("subSceneXSize", 100)*0.5,
		m_scene->getIntegrator()->getProperties().getFloat("subSceneZSize", 100)*0.5);
	m_filmSize = m_sensor->getFilm()->getSize();

	m_repetitiveSceneNum = integratorProps.getInteger("RepetitiveScene", 15);

	//首先获取sceneBounds
	Vector2 sceneSize = Vector2(integratorProps.getFloat("subSceneXSize", scene_bound.getExtents().x),
		integratorProps.getFloat("subSceneZSize", scene_bound.getExtents().z));

	double sceneMaxY = scene_bound.max.y;
	double sceneMinY = scene_bound.min.y;
	double x_min = -0.5*sceneSize.x;
	double x_max = 0.5*sceneSize.x;
	double z_min = -0.5*sceneSize.y;
	double z_max = 0.5*sceneSize.y;
	m_sceneBounds = AABB(Point(x_min, sceneMinY, z_min), Point(x_max, sceneMaxY, z_max));

	//virtual bounds
	if (integratorProps.getBoolean("SceneVirtualPlane", false)){
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
		m_virtualBounds = AABB(Point(centerX - 0.5*sizeX, sceneMinY, centerZ - 0.5*sizeZ), 
			Point(centerX + 0.5*sizeX, sceneMaxY, centerZ + 0.5*sizeZ));
	}
	else {
		m_virtualBounds = m_sceneBounds;
	}
}

Spectrum CapturePhotonWorker::repetitiveOcclude(Spectrum value, Point p, Vector d, const Scene* scene, bool & isRepetitiveOcclude)const {
	Ray occludeRay = Ray(p, d, 0);
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
			//	cout << "new Pos: " << ray.toString() << endl;
			if (scene->rayIntersect(occludeRay)) {
				isRepetitiveOcclude = true;
				return Spectrum(0.0);
			}

		}
		else {
			break;
		}
	}
	return value;
}

bool CapturePhotonWorker::rayIntersectExcludeEdge(Ray &ray, Intersection &its) {
	bool isIntersected = m_scene->rayIntersect(ray, its);
	if (isIntersected) {
		while (isIntersected && (!m_sceneBounds.contains(its.p))) {
			ray.o = its.p;
			isIntersected = m_scene->rayIntersect(ray, its);
		}
	}
	return isIntersected;
}

void CapturePhotonWorker::process(const WorkUnit *workUnit, WorkResult *workResult,
	const bool &stop) {
	if ((!m_hasBRFProducts) && (!m_hasUpDownProducts) && (!m_hasfPARProducts)) {
		return;
	}
	
	const RangeWorkUnit *range = static_cast<const RangeWorkUnit *>(workUnit);
	m_workResult = static_cast<CapturePhotonWorkResult *>(workResult);
	m_workResult->setRangeWorkUnit(range);
	//m_workResult->clear();
	//每次开始前，需要清空前一次的结果
	if (m_hasUpDownProducts) {
		m_workResult->m_downwellingWorkResult->clear();
		m_workResult->m_upwellingWorkResult->clear();
	}

	if (m_hasBRFProducts)
		m_workResult->m_dirBRFWorkResult->clear();
	if (m_hasfPARProducts)
		m_workResult->m_fPARsWordResult->clear();

	m_workResult->m_PhtonsEachProcess = 0;	

	Intersection its;
	ref<Sensor> sensor = m_scene->getSensor();
	PositionSamplingRecord pRec(sensor->getShutterOpen()
		+ 0.5f * sensor->getShutterOpenTime());
	m_sampler->generate(Point2i(0));

	for (size_t index = range->getRangeStart(); index <= range->getRangeEnd() && !stop; ++index) {
		m_sampler->setSampleIndex(index);
		const Emitter *emitter = NULL;
		const Medium *medium;
		Spectrum power;
		Ray ray;

		power = m_scene->sampleEmitterRay(ray, emitter,
			m_sampler->next2D(), m_sampler->next2D(), pRec.time);

		//Determine emitted power with shded or sunlit temperature
		//This of for simulating thrermal radiation, but it is not correct
		//if (!power.isZero()) {
		//	if (emitter->getProperties().hasProperty("temperature") &&
		//		(emitter->getProperties().getFloat("deltaTemperature", 0) != 0)) {
		//		//determined shaded or not
		//		Vector sunDirection = emitter->getProperties().getVector("direction");
		//		Ray occludeRay(ray.o, -sunDirection, 0);
		//		bool shaded = m_scene->rayIntersect(occludeRay);
		//		if (!shaded) {
		//			// further determine for repetitive occlusion
		//			bool isRepetitiveOccluded = false;
		//			repetitiveOcclude(Spectrum(0.0), ray.o, -sunDirection, m_scene, isRepetitiveOccluded);
		//			shaded = isRepetitiveOccluded;
		//		}
		//		power = emitter->getPowerAccordingToTemperature(ray.o, ray.extra, shaded);
		//	}
		//}
		medium = emitter->getMedium();

		//Each Photon has a type, which can be used for different purpose.
		//BRF calculation needs repetitive, while up and down welling do not need
		int photoType = EPhotonType::ETypeNull;
		if(m_hasBRFProducts) photoType = photoType | ETypeBRF;
		if (m_hasfPARProducts) photoType = photoType | ETypefPAR;
		if(m_hasUpDownProducts) photoType = photoType | ETypeUpDown;

		if (m_hasBRFProducts || m_hasfPARProducts) {
			//sample 一条光线后，首先判断是否是有效光线，即在场景的顶部
			//如果再场景顶部，则进入场景
			double H = ray.o[1] - m_sceneBounds.max.y;
			if (H >= 0) {
				double a = ray.d.x;
				double b = ray.d.y;
				double c = ray.d.z;
				Point its_p = ray.o + Point(-a / b * H, -H, -c / b * H);
				//cout << "its_p" << its_p.toString() << endl;
				if (its_p.x >= m_sceneBounds.min.x && its_p.x <= m_sceneBounds.max.x
					&& its_p.z >= m_sceneBounds.min.z && its_p.z <= m_sceneBounds.max.z
					) {
					if (m_hasBRFProducts)
						m_workResult->m_dirBRFWorkResult->putIrradiance(power);
					if(m_hasfPARProducts)
						m_workResult->m_fPARsWordResult->putIrradiance(power);
				}
				else {
					//光子若从四边入射，对于brf和fpar计算来说都无效了，只保留辐射的计算，
					//此时的光子对于BRF来说已经无效，不需要继续计算，但是对于上下行辐射来说，是有效的
					//如果不需要计算上下行辐射，则可以停止计算。如果需要则需要设置光子状态。
					if (photoType & ETypeUpDown) { //表示要继续计算下去,但是需要去掉brf和fpar属性
						photoType &= ~EPhotonType::ETypeBRF;
						photoType &= ~EPhotonType::ETypefPAR;
					}
					else {
						continue;
					}			
				}
			}
			else {
				continue;
			}
		}
		
		int depth = 1, nullInteractions = 0;
		bool delta = false;
		Point previousPoint = Point(std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity());
		Spectrum throughput(1.0f); // unitless path throughput (used for russian roulette)
		while (!throughput.isZero() && (depth <= m_maxDepth || m_maxDepth < 0)) {
			//m_scene->rayIntersect(ray, its);
			rayIntersectExcludeEdge(ray, its);
			int repetitiveTimes = 0;
			//如果需要计算BRF产品，且photon type正确，则计算. repetitive
			if ((m_hasBRFProducts && (photoType & EPhotonType::ETypeBRF)) ||
				(m_hasfPARProducts && (photoType & EPhotonType::ETypefPAR))) {
					if (its.t == std::numeric_limits<Float>::infinity()) {
						//maximum iteration = 5
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
							//	cout << "new Pos: " << ray.toString() << endl;
								//m_scene->rayIntersect(ray, its);
								rayIntersectExcludeEdge(ray, its);
								if (its.t < std::numeric_limits<Float>::infinity())
									break;
							}
							else {
								break;
							}
						}
					}//is infinity

			}//hasBRFProducts or hasfPARProducts

			//如果最大穿越场景次数之后，还是没有交点，则放弃
			if (its.t == std::numeric_limits<Float>::infinity()) {
				handleSurfaceInteractionBRF(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput*power, photoType);
				handleSurfaceInteractionUpDown(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput*power, photoType);
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
						handleSurfaceInteractionUpDown(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput*power, photoType);
						break;
					}
				}
				if (m_hasfPARProducts) {
					
					Spectrum ref1;
					if (dot(its.geoFrame.n, its.geoFrame.toWorld(bRec.wi)) >= 0) {//入射方向在正面,计算正面反射率
						Intersection its_tmp1;
						its_tmp1.p = its.p;
						BSDFSamplingRecord bRecref1(its_tmp1, Vector(0, 0, 1), Vector(0, 0, 1));
						ref1 = bsdf->eval(bRecref1)*M_PI_DBL;
					}
					else {
						Intersection its_tmp2;
						its_tmp2.p = its.p;
						BSDFSamplingRecord bRecref2(its_tmp2, Vector(0, 0, -1), Vector(0, 0, -1));
						ref1 = bsdf->eval(bRecref2)*M_PI_DBL;						
					}
					Intersection its_tmp;
					its_tmp.p = its.p;
					BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, -1), Vector(0, 0, 1));
					Spectrum ref2 = bsdf->eval(bRecref)*M_PI_DBL;
					Spectrum singleAbsorbtion = Spectrum(1.0) - ref1 - ref2;
					handleSurfaceInteractionFPAR(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput*power*singleAbsorbtion, photoType);
				}
				handleSurfaceInteractionBRF(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput*power, photoType);
				handleSurfaceInteractionUpDown(depth, nullInteractions, delta, its, ray, previousPoint, medium, throughput*power, photoType);

				if (bsdfWeight.isZero() || bsdfWeight.min() < 0) {
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
	m_workResult = NULL;
}

ref<WorkProcessor> CapturePhotonWorker::clone() const {
	return new CapturePhotonWorker(m_maxDepth,
		m_maxPathDepth, m_rrDepth, m_bruteForce, m_hasBRFProducts, m_hasUpDownProducts, m_virtualDirections,
		m_numberOfDirections,m_virtualDetectorDirection, m_hasfPARProducts,m_layerDefinition);
}

ref<WorkResult> CapturePhotonWorker::createWorkResult() const {
	const Film *film = m_sensor->getFilm();
	return new CapturePhotonWorkResult(film->getCropSize(), m_rfilter.get(), m_hasBRFProducts, m_hasUpDownProducts, m_virtualDirections,
		m_numberOfDirections, m_virtualDetectorDirection,m_hasfPARProducts, m_layerDefinition);
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
	//m_workResult->put(dRec.uv, (Float *)&value[0]);
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

void CapturePhotonWorker::handleSurfaceInteractionFPAR(int depth, int nullInteractions,
	bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
	const Spectrum &weight, int photoType) {
	if (m_hasfPARProducts && (photoType & EPhotonType::ETypefPAR)) {
		if(m_virtualBounds.contains(its.p))
			m_workResult->m_fPARsWordResult->put(its, weight);
	}

}
//扩展版本，可以得到上一个交点的信息
void CapturePhotonWorker::handleSurfaceInteractionBRF(int depth, int nullInteractions,
	bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
	const Spectrum &weight, int photoType) {
	
	//if (m_bruteForce || (depth >= m_maxPathDepth && m_maxPathDepth > 0))
	//	return;

	int maxInteractions = m_maxPathDepth - depth - 1;

	//BRF Products
	if (m_hasBRFProducts && (photoType & EPhotonType::ETypeBRF)) {
		//BRF 如果没有交点,则记录BRF值
		if (its.t == std::numeric_limits<Float>::infinity()) {
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
						double AzimuthAngle = 0.5*PHRT_M_PI - atan2(ray.d.z, -ray.d.x);
						if (AzimuthAngle < 0) AzimuthAngle += 2 * PHRT_M_PI;
						m_workResult->m_dirBRFWorkResult->put(zenithAngle, AzimuthAngle, weight);
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
			// At the intersected point, calculating the contribution of a photon tewards the virtual direction
			//First, determine whether the point has been occluded.
			const BSDF *bsdf = its.getBSDF();
			for (int i = 0; i < m_workResult->m_dirBRFWorkResult->m_nVirtualDirections; i++) {
				double dx = m_workResult->m_dirBRFWorkResult->m_virtualDirXYZ[3 * i];
				double dy = m_workResult->m_dirBRFWorkResult->m_virtualDirXYZ[3 * i+1];
				double dz = m_workResult->m_dirBRFWorkResult->m_virtualDirXYZ[3 * i+2];
				Vector wo = Vector(dx, dy, dz);
				Ray occludeRay(its.p, wo, 0);
				bool isDirectionOccuded = false;
				//for repetitive scene rayIntersectExcludeEdge
				//if (!m_scene->rayIntersect(occludeRay)) {
				Intersection tmp;
				if (!rayIntersectExcludeEdge(occludeRay, tmp)) {
					for (int iter = 0; iter < m_repetitiveSceneNum; iter++) {
						Float tNear, tFar;
						int exitFace;
						Vector boundExtend = m_sceneBounds.getExtents();
						m_sceneBounds.rayIntersectExt(occludeRay, tNear, tFar, exitFace);
						/*cout << "*************" << endl;
						cout << "occludeRay: " << occludeRay.toString()<< endl;
						cout << "exitFace: " << exitFace << endl;*/
						Point its_p = occludeRay.o + tFar * occludeRay.d;
						//cout << "its_p " << its_p.toString() << endl;
						if (its_p.y < m_sceneBounds.max.y && exitFace != 1) {
							//repetitive ray tracing
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
							if (m_scene->rayIntersect(occludeRay)) {
								isDirectionOccuded = true;
								break;
							}
						}
						else {
							break;
						}
					}
					if (isDirectionOccuded)
						continue;
					//virtual bounds
					double H = occludeRay.o[1] - m_virtualBounds.max.y;
					double a = occludeRay.d.x;
					double b = occludeRay.d.y;
					double c = occludeRay.d.z;
					Point itsP = occludeRay.o + Point(-a / b * H, -H, -c / b * H);
					if (itsP.x >= m_virtualBounds.min.x && itsP.x <= m_virtualBounds.max.x
						&& itsP.z >= m_virtualBounds.min.z && itsP.z <= m_virtualBounds.max.z) {
						BSDFSamplingRecord bRec(its, its.toLocal(wo), EImportance);
						m_workResult->m_dirBRFWorkResult->putVirtualBRF(i, weight*bsdf->eval(bRec));
					}
				}
			}
		}//end of virtual direction
	}
}


void CapturePhotonWorker::handleSurfaceInteractionUpDown(int depth, int nullInteractions,
	bool delta, const Intersection &its, Ray &ray, Point &previousPoint, const Medium *medium,
	const Spectrum &weight, int photoType) {
	//if (m_bruteForce || (depth >= m_maxPathDepth && m_maxPathDepth > 0))
	//	return;

	int maxInteractions = m_maxPathDepth - depth - 1;
	//radiation Products
	if (m_hasUpDownProducts && (photoType & EPhotonType::ETypeUpDown)) {
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
	}

}


void CapturePhotonWorker::handleMediumInteraction(int depth, int nullInteractions, bool caustic,
	const MediumSamplingRecord &mRec, const Medium *medium, const Vector &wi,
	const Spectrum &weight) {
}



/* ==================================================================== */
/*                        Parallel process impl.                        */
/* ==================================================================== */

void CapturePhotonProcess::develop() {
	if (m_hasUpDownProducts) {
		m_film_downwell->setBitmap(m_accum_downwell->getBitmap(), 1 / (Float)m_receivedResultCount);
		m_film_upwell->setBitmap(m_accum_upwell->getBitmap(), 1 / (Float)m_receivedResultCount);
	}

	m_queue->signalRefresh(m_job);

	if (m_hasUpDownProducts)
		m_film_upwell->develop(m_scene, 0);////m_film_downwell no need to save manually, because it will be automatically saved.
	//save BRF
	if(m_hasBRFProducts)
		m_dirBRFs->develop(1 / (Float)m_receivedResultCount);

	if (m_hasfPARProducts)
		m_fPARs->develop(1 / (Float)m_receivedResultCount);
}

void CapturePhotonProcess::processResult(const WorkResult *wr, bool cancelled) {
	const CapturePhotonWorkResult *result
		= static_cast<const CapturePhotonWorkResult *>(wr);
	const RangeWorkUnit *range = result->getRangeWorkUnit();
	if (cancelled)
		return;

	LockGuard lock(m_resultMutex);
	increaseResultCount(range->getSize());
	if (m_hasUpDownProducts) {
		m_accum_downwell->put(result->m_downwellingWorkResult.get());
		m_accum_upwell->put(result->m_upwellingWorkResult.get());
	}
	m_totalPhotons += result->m_PhtonsEachProcess;
	
	if(m_hasBRFProducts)
		m_dirBRFs->merge(result->m_dirBRFWorkResult.get());

	if (m_hasfPARProducts)
		m_fPARs->merge(result->m_fPARsWordResult.get());

	if (m_job->isInteractive() || m_receivedResultCount == m_workCount)
		develop();
}

void CapturePhotonProcess::bindResource(const std::string &name, int id) {
	if (name == "scene") {
		m_scene = static_cast<Scene *>(Scheduler::getInstance()->getResource(id));
	}

	if (name == "sensor") {
		if (m_hasUpDownProducts) {
			//*************************Updown Radiation******************************
			Sensor *sensor = static_cast<Sensor *>(Scheduler::getInstance()->getResource(id));
			m_film_downwell = sensor->getFilm();
			m_film_downwell->setDestinationFile(m_scene->getDestinationFile().string() + "_downwelling", m_scene->getBlockSize());

			m_film_upwell = static_cast<Film *>(PluginManager::getInstance()->createObject(
				MTS_CLASS(Film), m_film_downwell->getProperties()));
			std::string upwell_file = m_scene->getDestinationFile().string() + "_upwelling";
			m_film_upwell->setDestinationFile(upwell_file, m_scene->getBlockSize());

			m_accum_downwell = new ImageBlock(Bitmap::ESpectrum, m_film_downwell->getCropSize(), NULL); //下行辐射
			m_accum_downwell->clear();

			m_accum_upwell = new ImageBlock(Bitmap::ESpectrum, m_film_downwell->getCropSize(), NULL); //上行辐射
			m_accum_upwell->clear();
		}

		AABB scene_bound = m_scene->getKDTree()->getAABB();
		Properties inegratorProps = m_scene->getIntegrator()->getProperties();
		double sceneBoundX = inegratorProps.getFloat("subSceneXSize", scene_bound.getExtents().x);
		double scenBoundZ = inegratorProps.getFloat("subSceneZSize", scene_bound.getExtents().z);

		cout << "INFO: Scene Height: " << scene_bound.getExtents().y << endl;

		//*************************BRF******************************
		if (m_hasBRFProducts) {
			m_dirBRFs = new DirectionalBRF(m_numberOfDirections);
			//get scene Size
			if (m_scene->getIntegrator()->getProperties().hasProperty("isThermal") &&
				m_scene->getIntegrator()->getProperties().getBoolean("isThermal")) {
				m_dirBRFs->setDestinationFile(m_scene->getDestinationFile().string() + "_BT.txt");
				m_dirBRFs->setWavelengths(m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths"));
				m_dirBRFs->setCalculationMode(true);
			}
			else {
				m_dirBRFs->setDestinationFile(m_scene->getDestinationFile().string() + "_BRF.txt");
				m_dirBRFs->setInfoDestinationFile(m_scene->getDestinationFile().string() + "_LESS.txt");
				m_dirBRFs->setWavelengths(m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths"));
				m_dirBRFs->setCalculationMode(false);
			}
			
			m_dirBRFs->setSceneBoundPlaneSize(Vector2(sceneBoundX, scenBoundZ));
			if (inegratorProps.getBoolean("SceneVirtualPlane", false)) {
				double vSizeX = inegratorProps.getFloat("sizex", sceneBoundX);
				double vSizeZ = inegratorProps.getFloat("sizez", scenBoundZ);
				m_dirBRFs->setVirtualBoundXZSize(Vector2(vSizeX, vSizeZ));
			}
			else {
				m_dirBRFs->setVirtualBoundXZSize(Vector2(sceneBoundX, scenBoundZ));
			}

			//read virtual direction
			m_virtualDirections = m_scene->getIntegrator()->getProperties().getString("virtualDirections", "");
			m_virtualDetectorDirection = m_scene->getIntegrator()->getProperties().getString("virtualDetectorDirections", "");
			m_dirBRFs->readVirtualDirections(m_virtualDirections);
			m_dirBRFs->readVirtualDetectors(m_virtualDetectorDirection);

		}

		//*********************************fPAR***************************************
		//create products for fpar
		if (m_hasfPARProducts) {
			m_layerDefinition = m_scene->getIntegrator()->getProperties().getString("LayerDefinition", "0:2:20");
			m_fPARs = new fPARProduct(m_layerDefinition);
			m_fPARs->setDestinationFile(m_scene->getDestinationFile().string() + "_Layer_fPAR.txt");
			m_fPARs->setWavelengths(m_scene->getIntegrator()->getProperties().getSpectrum("wavelengths"));

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
		
	}
	PhotonProcess::bindResource(name, id);
}

ref<WorkProcessor> CapturePhotonProcess::createWorkProcessor() const {
	return new CapturePhotonWorker(m_maxDepth, m_maxPathDepth,
		m_rrDepth, m_bruteForce, m_hasBRFProducts,m_hasUpDownProducts, m_virtualDirections,m_numberOfDirections, m_virtualDetectorDirection,m_hasfPARProducts, m_layerDefinition);
}


MTS_IMPLEMENT_CLASS(CapturePhotonProcess, false, PhotonProcess)
MTS_IMPLEMENT_CLASS(CapturePhotonWorkResult, false, WorkResult)
MTS_IMPLEMENT_CLASS_S(CapturePhotonWorker, false, PhotonTracer)

MTS_NAMESPACE_END