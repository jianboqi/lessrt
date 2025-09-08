#include <mitsuba/render/scene.h>

MTS_NAMESPACE_BEGIN
class QIntegrator : public MonteCarloIntegrator {
public:
	QIntegrator(const Properties &props) : MonteCarloIntegrator(props) {
		Spectrum defaultColor;
		defaultColor.fromLinearRGB(0.2f, 0.5f, 0.2f);
		m_color = props.getSpectrum("color", defaultColor);
	}

	QIntegrator(Stream *stream, InstanceManager *manager)
		:MonteCarloIntegrator(stream, manager) {
		m_color = Spectrum(stream);
	}
	void serialize(Stream *stream, InstanceManager *manager) const
	{
		SamplingIntegrator::serialize(stream, manager);
		m_color.serialize(stream);
	}

	bool preprocess(const Scene *scene, RenderQueue *queue,
		const RenderJob *job, int sceneResID, int sensorResID,
		int samplerResID) {
		MonteCarloIntegrator::preprocess(scene, queue, job, sceneResID, sensorResID, samplerResID);
		return true;
	}

	Spectrum Li(const RayDifferential &r, RadianceQueryRecord &rRec) const {
		const Scene* scene = rRec.scene;
		Intersection &its = rRec.its;
		RayDifferential ray(r);
		Spectrum Li(0.0f);
		bool scattered = false;

		rRec.rayIntersect(ray);
		ray.mint = Epsilon;
		Float  eta = 1;

		Spectrum throughput(1.0f);
		//SLog(EInfo, "%d", m_maxDepth);
		while (rRec.depth <= m_maxDepth || m_maxDepth < 0) {
			if (!its.isValid()) {
				break;
			}
			//找到第一个交点,取得其表面BSDF
			const BSDF *bsdf = its.getBSDF(ray);

			if ((rRec.depth >= m_maxDepth && m_maxDepth > 0)
				|| (m_strictNormals && dot(ray.d, its.geoFrame.n)
					* Frame::cosTheta(its.wi) >= 0)) {
				/* Only continue if:
				  1. The current path length is below the specifed maximum
				  2. If 'strictNormals'=true, when the geometric and shading
					 normals classify the incident direction to the same side */
				break;
			}
			/*=========================================================================================*/
			/* 采用Multiple importance sampling方法求解辐射传输方程
			*  采用power heuristic方法以降低噪声
			*  首先对光源进行采样，再对BSDF进行采样。*/
			/*=========================================================================================*/


			/*=========================================================================================*/
			/* Direct illumination sampling */
			/*对光源进行采样时，首先调用emitter的sampleDirect函数采样，并返回pdf。同时，还需要计算积分函数
			中其项，例如BSDF在采样方向的概率（产生该方向的概率），需要注意的是，此处得到的BSDF值（bsdfVal）不需要除于
			概率，因为emitter得到的pdf就是重要性采样函数分母中的p(x)*/
			/*=========================================================================================*/
			DirectSamplingRecord dRec(its);
			if(rRec.type & RadianceQueryRecord::EDirectSurfaceRadiance &&
				(bsdf->getType() & BSDF::ESmooth)) {
				/*
				此处返回的value值，对于directional光源而言,返回辐照度/pdf，单位是瓦/平米，测度是EDiscrete
				如果是hemisphere等光源，则返回辐亮度/pdf，测度是ESolidAngle
				*/
				Spectrum value = scene->sampleEmitterDirect(dRec, rRec.nextSample2D());
		//		std::cout << "*********************" << std::endl;
		//		std::cout <<"Emitter value: "<< value.toString() <<" PDF: "<< dRec.pdf<< std::endl;
				if (!value.isZero()) {
					const Emitter *emitter = static_cast<const Emitter *>(dRec.object);

					BSDFSamplingRecord bRec(its, its.toLocal(dRec.d), ERadiance);
					/* Evaluate BSDF * cos(theta) */
					const Spectrum bsdfVal = bsdf->eval(bRec);
					if (!bsdfVal.isZero() && (!m_strictNormals
						|| dot(its.geoFrame.n, dRec.d) * Frame::cosTheta(bRec.wo) > 0)) {
		//				std::cout<<"Measure: " << dRec.measure << std::endl;
		//				std::cout << "emitter->isOnSurface(): " << emitter->isOnSurface() << std::endl;
						Float bsdfPdf = (emitter->isOnSurface() && dRec.measure == ESolidAngle)
							? bsdf->pdf(bRec) : 0;
			//			std::cout << "bsdfPdf: " << bsdfPdf<<" dRec.pdf:"<< dRec.pdf << std::endl;

						/* Weight using the power heuristic */
						Float weight = miWeight(dRec.pdf, bsdfPdf);
			//			std::cout << "miWeight: " << weight << std::endl;
			//			std::cout << "throughput: " << throughput.toString() << std::endl;
		//				std::cout << "bsdfVal: " << bsdfVal.toString() << std::endl;
						Li += throughput * value * bsdfVal * weight;
						//std::cout << "Li: " << Li.toString() << std::endl;

					}


				}
				
			}

		   /* ==================================================================== */
		   /*                            BSDF sampling                             */
		   /* 紧接着，对BRDF函数进行采样*/
		   /* ==================================================================== */
			/* Sample BSDF * cos(theta) */
			Float bsdfPdf;
			BSDFSamplingRecord bRec(its, rRec.sampler, ERadiance);
			//根据表面的BSDF类，随机产生一个方向，该方向符合BSDF的概率分布（重要性采样）
			//sample函数返回
			Spectrum bsdfWeight = bsdf->sample(bRec, bsdfPdf, rRec.nextSample2D());
			if (bsdfWeight.isZero())
				break;

			/* Prevent light leaks due to the use of shading normals */
			const Vector wo = its.toWorld(bRec.wo);
			Float woDotGeoN = dot(its.geoFrame.n, wo);
			if (m_strictNormals && woDotGeoN * Frame::cosTheta(bRec.wo) <= 0)
				break;
			scattered |= bRec.sampledType != BSDF::ENull;

			bool hitEmitter = false;
			Spectrum value;

			/* Trace a ray in this direction */
			ray = Ray(its.p, wo, ray.time);
			if (scene->rayIntersect(ray, its)) {
				//intersected something-check if it was a luminaire
				std::cout << its.toString() << std::endl;
				if (its.isEmitter()) {
					value = its.Le(-ray.d);
					dRec.setQuery(ray, its);
					hitEmitter = true;
				}
			}
			else {
				/* Intersected nothing -- perhaps there is an environment map? */
				const Emitter *env = scene->getEnvironmentEmitter();
				if (env) {
					if (m_hideEmitters && !scattered)
						break;

					value = env->evalEnvironment(ray);
					std::cout << "env-value: " << value.toString() << endl;
					if (!env->fillDirectSamplingRecord(dRec, ray))
						break;
					hitEmitter = true;
				}
				else {
					break;
				}
			}
			/* Keep track of the throughput and relative
			   refractive index along the path */
			std::cout << "throughput: " << throughput.toString() << endl;
			throughput *= bsdfWeight;
			std::cout << "throughput-bsdfweight: " << throughput.toString() << endl;
			eta *= bRec.eta;

			if (hitEmitter &&
				(rRec.type & RadianceQueryRecord::EDirectSurfaceRadiance)) {
				/* Compute the prob. of generating that direction using the
				   implemented direct illumination sampling technique */
				const Float lumPdf = (!(bRec.sampledType & BSDF::EDelta)) ?
					scene->pdfEmitterDirect(dRec) : 0;
				std::cout << "lumPdf: " << lumPdf<<" bsdfPdf: "<< bsdfPdf << endl;
				std::cout << "value: " << value.toString() << endl;
				Li += throughput * value * miWeight(bsdfPdf, lumPdf);
				std::cout << "Li: " << Li.toString() << endl;
			}

			if (rRec.depth++ >= m_rrDepth) {
				/* Russian roulette: try to keep path weights equal to one,
				   while accounting for the solid angle compression at refractive
				   index boundaries. Stop with at least some probability to avoid
				   getting stuck (e.g. due to total internal reflection) */

				Float q = std::min(throughput.max() * eta * eta, (Float) 0.95f);
				if (rRec.nextSample1D() >= q)
					break;
				throughput /= q;
			}

		}
		return Li;
	}
	Spectrum LiWithEF(const RayDifferential& ray, RadianceQueryRecord& rRec,
		Spectrum& LiAll, Spectrum& LiPSI, Spectrum& LiPSII) const {
		return Spectrum(0.0f);
	}

	inline Float miWeight(Float pdfA, Float pdfB) const {
		pdfA *= pdfA;
		pdfB *= pdfB;
		return pdfA / (pdfA + pdfB);
	}

	MTS_DECLARE_CLASS()
protected:
	Spectrum m_color;
};

MTS_IMPLEMENT_CLASS_S(QIntegrator, false, MonteCarloIntegrator)
MTS_EXPORT_PLUGIN(QIntegrator, "A contrived integrator");
MTS_NAMESPACE_END