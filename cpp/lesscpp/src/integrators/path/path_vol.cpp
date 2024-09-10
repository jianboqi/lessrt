/*
	This file is part of Mitsuba, a physically based rendering system.

	Copyright (c) 2007-2014 by Wenzel Jakob and others.

	Mitsuba is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License Version 3
	as published by the Free Software Foundation.

	Mitsuba is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

#include <mitsuba/render/scene.h>
#include <mitsuba/core/statistics.h>

MTS_NAMESPACE_BEGIN

static StatsCounter avgPathLength("Path tracer", "Average path length", EAverage);

/*! \plugin{path}{Path tracer}
 * \order{2}
 * \parameters{
 *     \parameter{maxDepth}{\Integer}{Specifies the longest path depth
 *         in the generated output image (where \code{-1} corresponds to $\infty$).
 *	       A value of \code{1} will only render directly visible light sources.
 *	       \code{2} will lead to single-bounce (direct-only) illumination,
 *	       and so on. \default{\code{-1}}
 *	   }
 *	   \parameter{rrDepth}{\Integer}{Specifies the minimum path depth, after
 *	      which the implementation will start to use the ``russian roulette''
 *	      path termination criterion. \default{\code{5}}
 *	   }
 *     \parameter{strictNormals}{\Boolean}{Be strict about potential
 *        inconsistencies involving shading normals? See the description below
 *        for details.\default{no, i.e. \code{false}}
 *     }
 *     \parameter{hideEmitters}{\Boolean}{Hide directly visible emitters?
 *        See page~\pageref{sec:hideemitters} for details.
 *        \default{no, i.e. \code{false}}
 *     }
 * }
 *
 * This integrator implements a basic path tracer and is a \emph{good default choice}
 * when there is no strong reason to prefer another method.
 *
 * To use the path tracer appropriately, it is instructive to know roughly how
 * it works: its main operation is to trace many light paths using \emph{random walks}
 * starting from the sensor. A single random walk is shown below, which entails
 * casting a ray associated with a pixel in the output image and searching for
 * the first visible intersection. A new direction is then chosen at the intersection,
 * and the ray-casting step repeats over and over again (until one of several
 * stopping criteria applies).
 * \begin{center}
 * \includegraphics[width=.7\textwidth]{images/integrator_path_figure.pdf}
 * \end{center}
 * At every intersection, the path tracer tries to create a connection to
 * the light source in an attempt to find a \emph{complete} path along which
 * light can flow from the emitter to the sensor. This of course only works
 * when there is no occluding object between the intersection and the emitter.
 *
 * This directly translates into a category of scenes where
 * a path tracer can be expected to produce reasonable results: this is the case
 * when the emitters are easily ``accessible'' by the contents of the scene. For instance,
 * an interior scene that is lit by an area light will be considerably harder
 * to render when this area light is inside a glass enclosure (which
 * effectively counts as an occluder).
 *
 * Like the \pluginref{direct} plugin, the path tracer internally relies on multiple importance
 * sampling to combine BSDF and emitter samples. The main difference in comparison
 * to the former plugin is that it considers light paths of arbitrary length to compute
 * both direct and indirect illumination.
 *
 * For good results, combine the path tracer with one of the
 * low-discrepancy sample generators (i.e. \pluginref{ldsampler},
 * \pluginref{halton}, or \pluginref{sobol}).
 *
 * \paragraph{Strict normals:}\label{sec:strictnormals}
 * Triangle meshes often rely on interpolated shading normals
 * to suppress the inherently faceted appearance of the underlying geometry. These
 * ``fake'' normals are not without problems, however. They can lead to paradoxical
 * situations where a light ray impinges on an object from a direction that is classified as ``outside''
 * according to the shading normal, and ``inside'' according to the true geometric normal.
 *
 * The \code{strictNormals}
 * parameter specifies the intended behavior when such cases arise. The default (\code{false}, i.e. ``carry on'')
 * gives precedence to information given by the shading normal and considers such light paths to be valid.
 * This can theoretically cause light ``leaks'' through boundaries, but it is not much of a problem in practice.
 *
 * When set to \code{true}, the path tracer detects inconsistencies and ignores these paths. When objects
 * are poorly tesselated, this latter option may cause them to lose a significant amount of the incident
 * radiation (or, in other words, they will look dark).
 *
 * The bidirectional integrators in Mitsuba (\pluginref{bdpt}, \pluginref{pssmlt}, \pluginref{mlt} ...)
 * implicitly have \code{strictNormals} set to \code{true}. Hence, another use of this parameter
 * is to match renderings created by these methods.
 *
 * \remarks{
 *    \item This integrator does not handle participating media
 *    \item This integrator has poor convergence properties when rendering
 *    caustics and similar effects. In this case, \pluginref{bdpt} or
 *    one of the photon mappers may be preferable.
 * }
 */
class MIPathVolTracer : public MonteCarloIntegrator {
public:
	MIPathVolTracer(const Properties& props)
		: MonteCarloIntegrator(props) {
		m_NoDataValue = props.getFloat("NoDataValue", -1.0);
		m_virtualPlane = props.getBoolean("SceneVirtualPlane", false);
		m_repetitiveSceneNum = props.getInteger("RepetitiveScene", 15);
		if (m_virtualPlane) {
			m_virtualPlane_vx = props.getFloat("vx", 0.0);
			m_virtualPlane_vz = props.getFloat("vz", 0.0);
			m_strVirtualPlane_vy = props.getString("vy", "MAX");
			m_virtualPlane_size_x = props.getFloat("sizex", 100.0);
			m_virtualPlane_size_z = props.getFloat("sizez", 100.0);
		}

		m_sceneXSize = props.getFloat("subSceneXSize", 100.0);
		m_sceneZSize = props.getFloat("subSceneZSize", 100.0);

		m_isThermal = props.getBoolean("isThermal", false);

		m_isOnlyMultiScattering = props.getBoolean("isOnlyMultiScattering", false);
		m_isOrthPhoto = props.hasProperty("reference_height");
		if (m_isOrthPhoto) {
			m_reference_height = props.getFloat("reference_height", 0);
			m_sensor_direction = props.getVector("sensor_direction", Vector(0, -1, 0));
		}
	}

	void serialize(Stream* stream, InstanceManager* manager) const {
		MonteCarloIntegrator::serialize(stream, manager);
		stream->writeDouble(m_NoDataValue);
		stream->writeBool(m_virtualPlane);
		stream->writeDouble(m_virtualPlane_vx);
		stream->writeString(m_strVirtualPlane_vy);
		stream->writeDouble(m_virtualPlane_vz);
		stream->writeDouble(m_virtualPlane_size_x);
		stream->writeDouble(m_virtualPlane_size_z);
		stream->writeInt(m_repetitiveSceneNum);
		stream->writeBool(m_isThermal);
		stream->writeBool(m_isOrthPhoto);
		stream->writeFloat(m_reference_height);
		m_sensor_direction.serialize(stream);
	}

	/// Unserialize from a binary data stream
	MIPathVolTracer(Stream* stream, InstanceManager* manager)
		: MonteCarloIntegrator(stream, manager) {
		m_NoDataValue = stream->readDouble();
		m_virtualPlane = stream->readBool();
		m_virtualPlane_vx = stream->readDouble();
		m_strVirtualPlane_vy = stream->readString();
		m_virtualPlane_vz = stream->readDouble();
		m_virtualPlane_size_x = stream->readDouble();
		m_virtualPlane_size_z = stream->readDouble();
		m_repetitiveSceneNum = stream->readInt();
		m_isThermal = stream->readBool();
		m_isOrthPhoto = stream->readBool();
		m_reference_height = stream->readFloat();
		m_sensor_direction = Vector(stream);
	}

	bool preprocess(const Scene* scene, RenderQueue* queue,
		const RenderJob* job, int sceneResID, int sensorResID,
		int samplerResID) {
		AABB scene_bound = scene->getKDTree()->getAABB();

		double sceneMaxY = scene_bound.max.y;
		double sceneMinY = scene_bound.min.y;
		double x_min = -0.5 * m_sceneXSize - SceneBoundEpsilon;
		double x_max = 0.5 * m_sceneXSize + SceneBoundEpsilon;
		double z_min = -0.5 * m_sceneZSize - SceneBoundEpsilon;
		double z_max = 0.5 * m_sceneZSize + SceneBoundEpsilon;

		m_sceneBounds = AABB(Point(x_min, sceneMinY, z_min), Point(x_max, sceneMaxY, z_max));

		if (m_virtualPlane) {
			m_virtualBounds = AABB(Point(m_virtualPlane_vx - 0.5 * m_virtualPlane_size_x, sceneMinY, m_virtualPlane_vz - 0.5 * m_virtualPlane_size_z),
				Point(m_virtualPlane_vx + 0.5 * m_virtualPlane_size_x, sceneMaxY, m_virtualPlane_vz + 0.5 * m_virtualPlane_size_z));
		}
		else {
			m_virtualBounds = m_sceneBounds;
		}
		return true;
	}

	//test occlusion for sun direct rays given reference point p and direction d
	Spectrum repetitiveOcclude(Spectrum value, Point p, Vector d, const Scene* scene, bool& isRepetitiveOcclude)const {
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

	//Test the ray repetitive nature for the first time, if the ray is not intersected within the
	//scene top bounding plane, it should be moved to the top scene bouding plane
	void rayRepetitiveInit(RayDifferential& ray, Intersection& its, const Scene* scene) const {
		if (m_repetitiveSceneNum == 0)
			return;

		//ray plane test
		double H = ray.o[1] - m_sceneBounds.max.y;
		if (H <= 0)
			return;
		double a = ray.d.x;
		double b = ray.d.y;
		double c = ray.d.z;
		Point its_p = ray.o + Point(-a / b * H, -H, -c / b * H);
		double offsetX = 0, offsetZ = 0;
		bool isOffseted = false;
		if (its_p.x > m_sceneBounds.max.x) {
			int numberOfX = (int)((its_p.x - m_sceneBounds.min.x) / m_sceneXSize);
			if (numberOfX <= m_repetitiveSceneNum) {
				offsetX = -numberOfX * m_sceneXSize;
				isOffseted = true;
			}
		}
		if (its_p.x < m_sceneBounds.min.x) {
			int numberOfX = (int)((m_sceneBounds.max.x - its_p.x) / m_sceneXSize);
			if (numberOfX <= m_repetitiveSceneNum) {
				offsetX = numberOfX * m_sceneXSize;
				isOffseted = true;
			}
		}

		if (its_p.z > m_sceneBounds.max.z) {
			int numberOfZ = (int)((its_p.z - m_sceneBounds.min.z) / m_sceneZSize);
			if (numberOfZ <= m_repetitiveSceneNum) {
				offsetZ = -numberOfZ * m_sceneZSize;
				isOffseted = true;
			}
		}

		if (its_p.z < m_sceneBounds.min.z) {
			int numberOfZ = (int)((m_sceneBounds.max.z - its_p.z) / m_sceneZSize);
			if (numberOfZ <= m_repetitiveSceneNum) {
				offsetZ = numberOfZ * m_sceneZSize;
				isOffseted = true;
			}
		}

		if (isOffseted) {
			ray.o.x += offsetX;
			ray.o.z += offsetZ;
		}
		scene->rayIntersect(ray, its);
	}

	void rayRepetitive(RayDifferential& ray, Intersection& its, const Scene* scene) const {
		if (!its.isValid()) {
			for (int iteration = 0; iteration < m_repetitiveSceneNum; iteration++) {
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
					scene->rayIntersect(ray, its);
					if (its.t < std::numeric_limits<Float>::infinity())
						break;
				}
				else {
					break;
				}
			}
		}
	}

	Spectrum Li(const RayDifferential& r, RadianceQueryRecord& rRec) const {
		/* Some aliases and local variables */

		const Scene* scene = rRec.scene;
		Intersection& its = rRec.its;
		MediumSamplingRecord mRec;
		RayDifferential ray(r);
		Spectrum Li(0.0f);
		bool scattered = false;
		bool nullChain = true;
		if (m_isOrthPhoto) {
			Ray up_ray(ray.o, Vector(0, 1, 0), 0);  //query the terrain height
			Intersection up_its;
			scene->rayIntersect(up_ray, up_its);
			Float demHeight = 0;
			if (up_its.isValid()) {
				demHeight = up_its.t;
			}
			Float orth_height = m_reference_height + demHeight;
			Float d = 100000;
			ray = Ray(ray.o + Vector(0, orth_height, 0) - d * m_sensor_direction, m_sensor_direction, 0);
		}

		//jianboqi:
		//handle virtual plane
		if (m_virtualPlane)
		{
			double x_min = m_virtualPlane_vx - 0.5 * m_virtualPlane_size_x;
			double x_max = m_virtualPlane_vx + 0.5 * m_virtualPlane_size_x;
			double z_min = m_virtualPlane_vz - 0.5 * m_virtualPlane_size_z;
			double z_max = m_virtualPlane_vz + 0.5 * m_virtualPlane_size_z;

			double H = ray.o[1] - m_virtualBounds.max.y;
			if (H > 0)
			{
				double a = ray.d.x;
				double b = ray.d.y;
				double c = ray.d.z;
				Point its_p = ray.o + Point(-a / b * H, -H, -c / b * H);
				if (!(its_p.x > x_min && its_p.x < x_max
					&& its_p.z > z_min && its_p.z < z_max
					))
				{
					return Spectrum(m_NoDataValue);
				}
			}
			else
			{
				return Spectrum(m_NoDataValue);
			}
		}
		

		/* Perform the first ray intersection (or ignore if the
		   intersection has already been provided). */
		rRec.rayIntersect(ray);
		ray.mint = Epsilon;
		rayRepetitiveInit(ray, its, scene);
		rayRepetitive(ray, its, scene);


		Spectrum throughput(1.0f);
		Float eta = 1.0f;
		Point hotspotStartPoint = Point(std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity());
		int max_interaaction_times = 0;
		std::vector<const Medium*> meeted_mediums;
		meeted_mediums.reserve(5);
		bool has_medium_in_single_path = false;
		Float rand = rRec.sampler->next1D();
		if (rand == 0.0) {
			return Spectrum(0.0);
		}
		Float sampledTau = -math::fastlog(1 - rand);
		bool needReSampleTau = false;
		bool isReachHotspotPosition = false;
		while (rRec.depth <= m_maxDepth || m_maxDepth < 0) {
			Float sigmaT = 0;
			Spectrum singleAlbedo(0.0);
			if (rRec.medium) {
				if (meeted_mediums.size() == 1) {
					sigmaT = rRec.medium->getVegetationSigmaT(ray);
					singleAlbedo = rRec.medium->getVegetationSingleAlbedo(ray);
				}
				else {
					for (int i = 0; i < meeted_mediums.size(); ++i) {
						Float eachSigmaT = meeted_mediums[i]->getVegetationSigmaT(ray);
						sigmaT += eachSigmaT;
						singleAlbedo += eachSigmaT * meeted_mediums[i]->getVegetationSingleAlbedo(ray);
					}
					singleAlbedo /= sigmaT;
				}
			}
			if (rRec.medium && needReSampleTau) {
				sampledTau = -math::fastlog(1 - rRec.sampler->next1D()); //Reset the sampledTau
				needReSampleTau = false;
			}
			if (rRec.medium && rRec.medium->sampleDistanceWithTotalTauSigmaTandAlbedo(Ray(ray, 0, its.t), mRec, rRec.sampler, sampledTau,needReSampleTau, sigmaT, singleAlbedo)) {
				const PhaseFunction* phase = mRec.getSampledPhaseFunction();
				throughput *= mRec.sigmaS * mRec.transmittance / mRec.pdfSuccess;

				//Modify transmittance according to hotspot


				/* Estimate the single scattering component if this is requested */
				if (rRec.type & RadianceQueryRecord::EDirectMediumRadiance) {
					DirectSamplingRecord dRec(mRec.p, mRec.time);
					int maxInteractions = -1;
					max_interaaction_times++;
					Spectrum value = scene->sampleAttenuatedEmitterDirect(
						dRec, rRec.medium, meeted_mediums, maxInteractions,rRec.depth, hotspotStartPoint,
						rRec.nextSample2D(),has_medium_in_single_path, rRec.sampler);

					if (!value.isZero()) {
						/*Li += throughput * value * phase->eval(
							PhaseFunctionSamplingRecord(mRec, -ray.d, dRec.d));*/

						if (meeted_mediums.size() == 1) {
							Li += throughput * value * phase->eval(
								PhaseFunctionSamplingRecord(mRec, -ray.d, dRec.d));
						}
						else {
							Spectrum phaseval(0.0);
							for (int i = 0; i < meeted_mediums.size(); ++i) {
								Float eachSigmaT = meeted_mediums[i]->getVegetationSigmaT(ray);
								Spectrum eachAlbedo = meeted_mediums[i]->getVegetationSingleAlbedo(ray);
								phaseval += eachSigmaT * eachAlbedo * meeted_mediums[i]->getPhaseFunction()->eval(
									PhaseFunctionSamplingRecord(mRec, -ray.d, dRec.d));
							}
							phaseval /= mRec.sigmaS;
							Li += throughput * value * phaseval;
						}
						
					}
						
				}

				/* Stop if multiple scattering was not requested, or if the path gets too long */
				if ((rRec.depth + 1 >= m_maxDepth && m_maxDepth > 0) ||
					!(rRec.type & RadianceQueryRecord::EIndirectMediumRadiance))
					break;

				/* ==================================================================== */
				/*             Phase function sampling / Multiple scattering            */
				/* ==================================================================== */

				PhaseFunctionSamplingRecord pRec(mRec, -ray.d);
				//sampleSpec(pRec, rRec.sampler, rRec.depth);
				Spectrum phaseVal = phase->sampleSpec(pRec, rRec.sampler);
				if (phaseVal.isZero())
					break;
				throughput *= phaseVal;

				/* Trace a ray in this direction */
				ray = Ray(mRec.p, pRec.wo, ray.time);
				hotspotStartPoint = mRec.p;
				ray.mint = 0;
				scene->rayIntersect(ray, its);
				nullChain = false;
				scattered = true;
			}
			else {
				if (rRec.medium) {
					throughput *= mRec.transmittance / mRec.pdfFailure;
				}

				if (!its.isValid()) {
					/* If no intersection could be found, potentially return
					   radiance from a environment luminaire if it exists */
					   //如果隐藏了emiter，则返回-1. 只有多波段模式才启用。
					if (m_hideEmitters)
					{
						Li = Spectrum(m_NoDataValue);
						break;
					}
					if ((rRec.type & RadianceQueryRecord::EEmittedRadiance)
						&& (!m_hideEmitters || scattered))
						Li += throughput * scene->evalEnvironment(ray);
					break;
				}

				const BSDF* bsdf = its.getBSDF(ray);

				/* Possibly include emitted radiance if requested */
				if (its.isEmitter() && (rRec.type & RadianceQueryRecord::EEmittedRadiance)
					&& (!m_hideEmitters || scattered)) {
					//For thermal direct emitted
					if (its.shape->getEmitter()->getProperties().hasProperty("temperature") &&
						its.shape->getEmitter()->getProperties().getFloat("deltaTemperature", 0) != 0) {
						Vector sunDirection = its.shape->getEmitter()->getProperties().getVector("direction");
						//test occlusion. temperature will be different when shaded or not shaded
						Ray occludeRay(its.p, -sunDirection, 0);
						if (scene->rayIntersect(occludeRay)) {
							its.shaded = true;
						}
						else {
							// further determine for repetitive occlusion
							bool isRepetitiveOccluded = false;
							repetitiveOcclude(Spectrum(0.0), its.p, -sunDirection, scene, isRepetitiveOccluded);
							its.shaded = isRepetitiveOccluded;
						}
					}
					Li += throughput * its.Le(-ray.d);
				}


				/* Include radiance from a subsurface scattering model if requested */
				if (its.hasSubsurface() && (rRec.type & RadianceQueryRecord::ESubsurfaceRadiance))
					Li += throughput * its.LoSub(scene, rRec.sampler, -ray.d, rRec.depth);

				if ((rRec.depth >= m_maxDepth && m_maxDepth > 0)
					|| (m_strictNormals && dot(ray.d, its.geoFrame.n)
						* Frame::cosTheta(its.wi) >= 0)) {

					/* Only continue if:
					   1. The current path length is below the specifed maximum
					   2. If 'strictNormals'=true, when the geometric and shading
						  normals classify the incident direction to the same side */
					break;
				}

				/* ==================================================================== */
				/*                     Direct illumination sampling                     */
				/* ==================================================================== */

				/* Estimate the direct illumination if this is requested */
				DirectSamplingRecord dRec(its);

				if (rRec.type & RadianceQueryRecord::EDirectSurfaceRadiance &&
					(bsdf->getType() & BSDF::ESmooth)) {
					needReSampleTau = true;
					Spectrum value;
					if (!m_isThermal) {
						//int maxInteractions = m_maxDepth - rRec.depth - 1;
						int maxInteractions = -1;
						max_interaaction_times++;
					//	if (max_interaaction_times >= 200) break; //hlton simpler only support max dimension 1024, we need to stop when the iertaction time is large
						value = scene->sampleAttenuatedEmitterDirect(
						dRec, its, rRec.medium,meeted_mediums, maxInteractions,rRec.depth, hotspotStartPoint,
						rRec.nextSample2D(), has_medium_in_single_path, rRec.sampler);
						//value = scene->sampleEmitterDirect(dRec, rRec.nextSample2D());
						////determine repetitive of sample sun rays
						//if (!value.isZero()) {
						//	bool tmp;
						//	value = repetitiveOcclude(value, its.p, dRec.d, scene, tmp);
						//}
					}
					else {//thermal
						//First, try to sample a point on a emitter
						value = scene->sampleEmitterDirect(dRec, rRec.nextSample2D());
						//if it is a planck emitter, try to decide its status of shade to assign different temperatures
						if (!value.isZero()) {
							const Emitter* emitter = static_cast<const Emitter*>(dRec.object);
							if (emitter->getProperties().hasProperty("temperature") &&
								(emitter->getProperties().getFloat("deltaTemperature", 0) != 0)) {
								//determined shaded or not
								Vector sunDirection = emitter->getProperties().getVector("direction");
								Ray occludeRay(dRec.p, -sunDirection, 0);
								bool shaded = scene->rayIntersect(occludeRay);
								if (!shaded) {
									// further determine for repetitive occlusion
									bool isRepetitiveOccluded = false;
									repetitiveOcclude(Spectrum(0.0), dRec.p, -sunDirection, scene, isRepetitiveOccluded);
									shaded = isRepetitiveOccluded;
								}
								value = emitter->getSpectrumAccordingToTemperature(dRec, its, shaded);
							}
							else { // when the sampled emitter is sky emitter, consider the repetitive
								bool tmp;
								value = repetitiveOcclude(value, its.p, dRec.d, scene, tmp);
							}
						}

					}

					//four component
					if (m_hasFourComponentProduct && rRec.depth == 1) {
						if (!value.isZero()) {//illuminated area
							if (its.shape->getName() == "terrain") {//intersect with terrain
								rRec.extra = 1; // illuminated soil
							}
							else {
								rRec.extra = 2; // illuminated object (leaf)
							}
						}
						else {//shaded area
							if (its.shape->getName() == "terrain") {//intersect with terrain
								rRec.extra = 3; // shaded soil
							}
							else {
								rRec.extra = 4; // shaded object (leaf)
							}
						}
					}

					if (!value.isZero()) {
						const Emitter* emitter = static_cast<const Emitter*>(dRec.object);

						/* Allocate a record for querying the BSDF */
						BSDFSamplingRecord bRec(its, its.toLocal(dRec.d), ERadiance);

						/* Evaluate BSDF * cos(theta) */
						const Spectrum bsdfVal = bsdf->eval(bRec);

						/* Prevent light leaks due to the use of shading normals */
						if (!bsdfVal.isZero() && (!m_strictNormals
							|| dot(its.geoFrame.n, dRec.d) * Frame::cosTheta(bRec.wo) > 0)) {
							/* Calculate prob. of having generated that direction
							   using BSDF sampling */
							Float bsdfPdf = (emitter->isOnSurface() && dRec.measure == ESolidAngle)
								? bsdf->pdf(bRec) : 0;
							/* Weight using the power heuristic */
							Float weight = miWeight(dRec.pdf, bsdfPdf);
							if (m_isOnlyMultiScattering && rRec.depth == 1) {

							}
							else {
								Li += throughput * value * bsdfVal * weight;
							}

						}
					}
				}

				/* ==================================================================== */
				/*                            BSDF sampling                             */
				/* ==================================================================== */

				/* Sample BSDF * cos(theta) */
				Float bsdfPdf;
				BSDFSamplingRecord bRec(its, rRec.sampler, ERadiance);
				//if (times++ > 10) {
				//	cout << times <<" rRec"<< rRec.depth<< endl;
				//	if (times == 502) {
				//		int b = 0;
				//	}
				//}
				max_interaaction_times++;
			//	if (max_interaaction_times >= 200) break; //hlton simpler only support max dimension 1024, we need to stop when the iertaction time is large
				Spectrum bsdfWeight;
				if (bsdf->getType() & BSDF::ENull) {
					bsdfWeight = bsdf->sample(bRec, bsdfPdf, Point2());
				}
				else {
					bsdfWeight = bsdf->sample(bRec, bsdfPdf, rRec.nextSample2D());
				}
				if (bsdfWeight.isZero())
					break;

				scattered |= bRec.sampledType != BSDF::ENull;

				/* Prevent light leaks due to the use of shading normals */
				const Vector wo = its.toWorld(bRec.wo);
				Float woDotGeoN = dot(its.geoFrame.n, wo);
				if (m_strictNormals && woDotGeoN * Frame::cosTheta(bRec.wo) <= 0)
					break;

				if (its.isMediumTransition()) {
					rRec.medium = its.getTargetMedium(wo);
					if (rRec.medium) {
						has_medium_in_single_path = true;
						meeted_mediums.emplace_back(rRec.medium);
					}
					else {
						if (meeted_mediums.size() == 1) {
							meeted_mediums.clear();
						}
						else if (meeted_mediums.size() > 0) {
							const Medium* tmp = its.getTargetMedium(-wo);
							auto itr = remove_if(meeted_mediums.begin(), meeted_mediums.end(), [&](const Medium* x) {return x == tmp; });
							if (itr >= meeted_mediums.begin() && itr < meeted_mediums.end()) {
								meeted_mediums.erase(itr);
								if (meeted_mediums.size() > 0) {
									rRec.medium = meeted_mediums[meeted_mediums.size()-1];
								}
							}	
						}
						
					}
				}
					

				bool hitEmitter = false;
				Spectrum value;

				/* Trace a ray in this direction */
				ray = Ray(its.p, wo, ray.time);
				scene->rayIntersect(ray, its);
				rayRepetitive(ray, its, scene);
				if (its.isValid()) {
					/* Intersected something - check if it was a luminaire */
					if (its.isEmitter()) {
						//For thermal direct emitted
						if (its.shape->getEmitter()->getProperties().hasProperty("temperature") &&
							its.shape->getEmitter()->getProperties().getFloat("deltaTemperature", 0) != 0) {
							Vector sunDirection = its.shape->getEmitter()->getProperties().getVector("direction");
							//test occlusion. temperature will be different when shaded or not shaded
							Ray occludeRay(its.p, -sunDirection, 0);
							if (scene->rayIntersect(occludeRay)) {
								its.shaded = true;
							}
							else {								// further determine for repetitive occlusion
								bool isRepetitiveOccluded = false;
								repetitiveOcclude(Spectrum(0.0), its.p, -sunDirection, scene, isRepetitiveOccluded);
								its.shaded = isRepetitiveOccluded;
							}
						}
						value = its.Le(-ray.d);
						dRec.setQuery(ray, its);
						hitEmitter = true;
					}
				}
				else {
					/* Intersected nothing -- perhaps there is an environment map? */
					const Emitter* env = scene->getEnvironmentEmitter();
					if (env) {
						if (m_hideEmitters && !scattered)
							break;

						value = env->evalEnvironment(ray);
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
				throughput *= bsdfWeight;
				eta *= bRec.eta;

				/* If a luminaire was hit, estimate the local illumination and
				   weight using the power heuristic */
				if (hitEmitter &&
					(rRec.type & RadianceQueryRecord::EDirectSurfaceRadiance)) {
					/* Compute the prob. of generating that direction using the
					   implemented direct illumination sampling technique */
					const Float lumPdf = (!(bRec.sampledType & BSDF::EDelta)) ?
						scene->pdfEmitterDirect(dRec) : 0;
					Li += throughput * value * miWeight(bsdfPdf, lumPdf);
				}

				/* ==================================================================== */
				/*                         Indirect illumination                        */
				/* ==================================================================== */

				/* Set the recursive query type. Stop if no surface was hit by the
				   BSDF sample or if indirect illumination was not requested */
				if (!its.isValid() || !(rRec.type & RadianceQueryRecord::EIndirectSurfaceRadiance))
					break;
				rRec.type = RadianceQueryRecord::ERadianceNoEmission;

				//If is null intersection, we do not increase depth
				if (bsdf->getType() & BSDF::ENull) {
					if (rRec.medium && !isReachHotspotPosition) {
						hotspotStartPoint = ray.o;
						isReachHotspotPosition = true;
					}
					continue;
				}
			}
			if (rRec.depth++ >= m_rrDepth) {
				/* Russian roulette: try to keep path weights equal to one,
				   while accounting for the solid angle compression at refractive
				   index boundaries. Stop with at least some probability to avoid
				   getting stuck (e.g. due to total internal reflection) */

				Float q = std::min(throughput.max() * eta * eta, (Float)0.95f);
				if (rRec.nextSample1D() >= q)
					break;
				throughput /= q;
			}
		}

		/* Store statistics */
		avgPathLength.incrementBase();
		avgPathLength += rRec.depth;

		return Li;
	}
	Spectrum LiWithEF(const RayDifferential& r, RadianceQueryRecord& rRec,
		Spectrum& LiAll, Spectrum& LiPSI, Spectrum& LiPSII) const {
		const Scene* scene = rRec.scene;
		Intersection& its = rRec.its;
		MediumSamplingRecord mRec;
		RayDifferential ray(r);
		Spectrum Li(0.0f);
		bool scattered = false;
		bool nullChain = true;
		if (m_isOrthPhoto) {
			Ray up_ray(ray.o, Vector(0, 1, 0), 0);  //query the terrain height
			Intersection up_its;
			scene->rayIntersect(up_ray, up_its);
			Float demHeight = 0;
			if (up_its.isValid()) {
				demHeight = up_its.t;
			}
			Float orth_height = m_reference_height + demHeight;
			Float d = 100000;
			ray = Ray(ray.o + Vector(0, orth_height, 0) - d * m_sensor_direction, m_sensor_direction, 0);
		}

		//jianboqi:
		//handle virtual plane
		if (m_virtualPlane)
		{
			double x_min = m_virtualPlane_vx - 0.5 * m_virtualPlane_size_x;
			double x_max = m_virtualPlane_vx + 0.5 * m_virtualPlane_size_x;
			double z_min = m_virtualPlane_vz - 0.5 * m_virtualPlane_size_z;
			double z_max = m_virtualPlane_vz + 0.5 * m_virtualPlane_size_z;

			double H = ray.o[1] - m_virtualBounds.max.y;
			if (H > 0)
			{
				double a = ray.d.x;
				double b = ray.d.y;
				double c = ray.d.z;
				Point its_p = ray.o + Point(-a / b * H, -H, -c / b * H);
				if (!(its_p.x > x_min && its_p.x < x_max
					&& its_p.z > z_min && its_p.z < z_max
					))
				{
					LiAll = Spectrum(m_NoDataValue);
					LiPSI = Spectrum(m_NoDataValue);
					LiPSII = Spectrum(m_NoDataValue);
					return Spectrum(m_NoDataValue);
				}
			}
			else
			{
				LiAll = Spectrum(m_NoDataValue);
				LiPSI = Spectrum(m_NoDataValue);
				LiPSII = Spectrum(m_NoDataValue);
				return Spectrum(m_NoDataValue);
			}
		}


		/* Perform the first ray intersection (or ignore if the
		   intersection has already been provided). */
		rRec.rayIntersect(ray);
		ray.mint = Epsilon;
		rayRepetitiveInit(ray, its, scene);
		rayRepetitive(ray, its, scene);


		Spectrum throughput(1.0f);
		Float eta = 1.0f;

		Float Addmimii = 0;//
		FluorMatrix m;
		m.setFluorMatrixZeros();
		FluorMatrix mt;
		FluorMatrixs ms;

		Point hotspotStartPoint = Point(std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity(), std::numeric_limits<Float>::infinity());
		int max_interaaction_times = 0;
		std::vector<const Medium*> meeted_mediums;
		meeted_mediums.reserve(5);
		bool has_medium_in_single_path = false;
		Float rand = rRec.sampler->next1D();
		if (rand == 0.0) {
			LiAll = Spectrum(0.0);
			LiPSI = Spectrum(0.0);
			LiPSII = Spectrum(0.0);
			return Spectrum(0.0);
		}
		Float sampledTau = -math::fastlog(1 - rand);
		bool needReSampleTau = false;
		bool isReachHotspotPosition = false;
		while (rRec.depth <= m_maxDepth || m_maxDepth < 0) {
			Float sigmaT = 0;
			Spectrum singleAlbedo(0.0);
			FluorMatrix FluorsingleAlbedo; FluorsingleAlbedo.setFluorMatrixZeros();
			if (rRec.medium) {
				if (meeted_mediums.size() == 1) {
					sigmaT = rRec.medium->getVegetationSigmaT(ray);
					singleAlbedo = rRec.medium->getVegetationSingleAlbedo(ray);
					if (rRec.medium->getClass()->getName() == "VegFluorMedium") {
						FluorsingleAlbedo = rRec.medium->getFluorVegetationSingleAlbedo(ray);
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
					singleAlbedo /= sigmaT;
					FluorsingleAlbedo.compute_DivideEqual(sigmaT);
				}
			}
			if (rRec.medium && needReSampleTau) {
				sampledTau = -math::fastlog(1 - rRec.sampler->next1D()); //Reset the sampledTau
				needReSampleTau = false;
			}
			bool medium_sampleDistanceWithTotalTauSigmaTandAlbedo = false;
			if (rRec.medium) {
				if (rRec.medium->getClass()->getName() == "VegFluorMedium") {
					medium_sampleDistanceWithTotalTauSigmaTandAlbedo =
						rRec.medium->sampleDistanceWithTotalTauSigmaTandAlbedo(Ray(ray, 0, its.t), mRec, rRec.sampler, sampledTau, needReSampleTau, sigmaT, singleAlbedo, FluorsingleAlbedo);
				}
				else {
					medium_sampleDistanceWithTotalTauSigmaTandAlbedo =
						rRec.medium->sampleDistanceWithTotalTauSigmaTandAlbedo(Ray(ray, 0, its.t), mRec, rRec.sampler, sampledTau, needReSampleTau, sigmaT, singleAlbedo);
				}
			}
			if (rRec.medium && medium_sampleDistanceWithTotalTauSigmaTandAlbedo) {
				const PhaseFunction* phase = mRec.getSampledPhaseFunction();
				Float mRec_transmittance_mRec_pdfSuccess = mRec.transmittance[0] / mRec.pdfSuccess;
				if (rRec.medium->getClass()->getName() == "VegFluorMedium") {
					m.compute_Mb1xMb2_isFluor2Mixture_M1(throughput, mRec.FluorsigmaS, mRec.sigmaS, mRec_transmittance_mRec_pdfSuccess);
				}
				else {
					m.compute_Mb1xMb2_isNotFluor2Mixture_M1(mRec.sigmaS, mRec_transmittance_mRec_pdfSuccess);
				}
				throughput *= mRec.sigmaS * mRec_transmittance_mRec_pdfSuccess;

				//Modify transmittance according to hotspot


				/* Estimate the single scattering component if this is requested */
				if (rRec.type & RadianceQueryRecord::EDirectMediumRadiance) {
					DirectSamplingRecord dRec(mRec.p, mRec.time);
					int maxInteractions = -1;
					max_interaaction_times++;
					Spectrum value = scene->sampleAttenuatedEmitterDirect(
						dRec, rRec.medium, meeted_mediums, maxInteractions, rRec.depth, hotspotStartPoint,
						rRec.nextSample2D(), has_medium_in_single_path, rRec.sampler);

					if (!value.isZero()) {
						/*Li += throughput * value * phase->eval(
							PhaseFunctionSamplingRecord(mRec, -ray.d, dRec.d));*/
						Spectrum phaseval(0.0);
						FluorMatrix phaseFluorVal; phaseFluorVal.setFluorMatrixZeros();
						PhaseFunctionSamplingRecord pRec = PhaseFunctionSamplingRecord(mRec, -ray.d, dRec.d);
						bool isFluor2MixtureMedium = false;
						if (meeted_mediums.size() == 1) {
							if (rRec.medium->getClass()->getName() == "VegFluorMedium") {
								phaseval = phase->eval(pRec); isFluor2MixtureMedium = true;
							}
							else {
								phaseval = phase->evalWithEF(pRec, phaseFluorVal);
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
									isFluor2MixtureMedium = true;
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
						Spectrum throughput_value_phaseval = throughput * value * phaseval;
						if (isFluor2MixtureMedium) {
							m.compute_Mb1xMb2_isFluor2Mixture_mt(mt, throughput, phaseFluorVal, phaseval);
						}
						else {
							m.compute_Mb1xMb2_isNotFluor2Mixture_mt(mt, phaseval);
						}
						Spectrum powerPSIt(0.0f);
						Spectrum powerPSIIt(0.0f);
						mt.compute_MbxPower(value, powerPSIt, powerPSIIt, LiAll, LiPSI, LiPSII);
						LiAll += throughput_value_phaseval;
						Li += throughput_value_phaseval;
					}

				}

				/* Stop if multiple scattering was not requested, or if the path gets too long */
				if ((rRec.depth + 1 >= m_maxDepth && m_maxDepth > 0) ||
					!(rRec.type & RadianceQueryRecord::EIndirectMediumRadiance))
					break;

				/* ==================================================================== */
				/*             Phase function sampling / Multiple scattering            */
				/* ==================================================================== */

				PhaseFunctionSamplingRecord pRec(mRec, -ray.d);
				//sampleSpec(pRec, rRec.sampler, rRec.depth);
				Spectrum phaseVal;
				if (phase->getClass()->getName() == "VegFluorPhaseFunction") {
					FluorMatrix phaseFluorweight;
					phaseVal = phase->sampleEFSpec(pRec, rRec.sampler, phaseFluorweight);
					m.compute_Mb1xMb2_isFluor2Mixture(throughput, phaseFluorweight, phaseVal);
				}
				else {
					phaseVal = phase->sampleSpec(pRec, rRec.sampler);
					m.compute_Mb1xMb2_isNotFluor2Mixture(phaseVal);
				}
				if (phaseVal.isZero())
					break;
				throughput *= phaseVal;

				/* Trace a ray in this direction */
				ray = Ray(mRec.p, pRec.wo, ray.time);
				hotspotStartPoint = mRec.p;
				ray.mint = 0;
				scene->rayIntersect(ray, its);
				nullChain = false;
				scattered = true;
			}
			else {
				if (rRec.medium) {
					Float mRec_transmittance_mRec_pdfFailure = mRec.transmittance[0] / mRec.pdfFailure;
					if (mRec_transmittance_mRec_pdfFailure != 1) {
						m.compute_MultiplyEqual(mRec_transmittance_mRec_pdfFailure);
						throughput *= mRec_transmittance_mRec_pdfFailure;// mRec.transmittance / mRec.pdfFailure;
					}
				}

				if (!its.isValid()) {
					/* If no intersection could be found, potentially return
					   radiance from a environment luminaire if it exists */
					   //如果隐藏了emiter，则返回-1. 只有多波段模式才启用。
					if (m_hideEmitters)
					{
						LiAll = Spectrum(m_NoDataValue);
						LiPSI = Spectrum(m_NoDataValue);
						LiPSII = Spectrum(m_NoDataValue);
						Li = Spectrum(m_NoDataValue);
						break;
					}
					if ((rRec.type & RadianceQueryRecord::EEmittedRadiance)
						&& (!m_hideEmitters || scattered)) {
						Spectrum throughput_scene_evalEnvironment_ray_ = throughput * scene->evalEnvironment(ray);
						Spectrum powerPSIt(0.0f);
						Spectrum powerPSIIt(0.0f);
						m.compute_MbxPower(scene->evalEnvironment(ray), powerPSIt, powerPSIIt, LiAll, LiPSI, LiPSII);
						LiAll += throughput_scene_evalEnvironment_ray_;
						Li += throughput_scene_evalEnvironment_ray_;
					}
					break;
				}

				const BSDF* bsdf = its.getBSDF(ray);
				bool isFluor2MixtureBSDF = bsdf->getClass()->getName() == "Fluor2MixtureBSDF";
				if (isFluor2MixtureBSDF)
					ms = bsdf->getFluorMatrixs();

				/* Possibly include emitted radiance if requested */
				if (its.isEmitter() && (rRec.type & RadianceQueryRecord::EEmittedRadiance)
					&& (!m_hideEmitters || scattered)) {
					//For thermal direct emitted
					if (its.shape->getEmitter()->getProperties().hasProperty("temperature") &&
						its.shape->getEmitter()->getProperties().getFloat("deltaTemperature", 0) != 0) {
						Vector sunDirection = its.shape->getEmitter()->getProperties().getVector("direction");
						//test occlusion. temperature will be different when shaded or not shaded
						Ray occludeRay(its.p, -sunDirection, 0);
						if (scene->rayIntersect(occludeRay)) {
							its.shaded = true;
						}
						else {
							// further determine for repetitive occlusion
							bool isRepetitiveOccluded = false;
							repetitiveOcclude(Spectrum(0.0), its.p, -sunDirection, scene, isRepetitiveOccluded);
							its.shaded = isRepetitiveOccluded;
						}
					}
					Spectrum throughput_its_Le__ray_d_ = throughput * its.Le(-ray.d);
					Spectrum powerPSIt(0.0f);
					Spectrum powerPSIIt(0.0f);
					m.compute_MbxPower(its.Le(-ray.d), powerPSIt, powerPSIIt, LiAll, LiPSI, LiPSII);
					LiAll += throughput_its_Le__ray_d_;
					Li += throughput_its_Le__ray_d_;
				}


				/* Include radiance from a subsurface scattering model if requested */
				if (its.hasSubsurface() && (rRec.type & RadianceQueryRecord::ESubsurfaceRadiance)) {
					Spectrum throughput_its_LoSub_scene_rRec_sampler_ray_d_rRec_depth_ = throughput * its.LoSub(scene, rRec.sampler, -ray.d, rRec.depth);
					Spectrum powerPSIt(0.0f);
					Spectrum powerPSIIt(0.0f);
					m.compute_MbxPower(its.LoSub(scene, rRec.sampler, -ray.d, rRec.depth), powerPSIt, powerPSIIt, LiAll, LiPSI, LiPSII);
					LiAll += throughput_its_LoSub_scene_rRec_sampler_ray_d_rRec_depth_;
					Li += throughput_its_LoSub_scene_rRec_sampler_ray_d_rRec_depth_;
				}

				if ((rRec.depth >= m_maxDepth && m_maxDepth > 0)
					|| (m_strictNormals && dot(ray.d, its.geoFrame.n)
						* Frame::cosTheta(its.wi) >= 0)) {

					/* Only continue if:
					   1. The current path length is below the specifed maximum
					   2. If 'strictNormals'=true, when the geometric and shading
						  normals classify the incident direction to the same side */
					break;
				}

				/* ==================================================================== */
				/*                     Direct illumination sampling                     */
				/* ==================================================================== */

				/* Estimate the direct illumination if this is requested */
				DirectSamplingRecord dRec(its);

				if (rRec.type & RadianceQueryRecord::EDirectSurfaceRadiance &&
					(bsdf->getType() & BSDF::ESmooth)) {
					needReSampleTau = true;
					Spectrum value;
					if (!m_isThermal) {
						//int maxInteractions = m_maxDepth - rRec.depth - 1;
						int maxInteractions = -1;
						max_interaaction_times++;
						//	if (max_interaaction_times >= 200) break; //hlton simpler only support max dimension 1024, we need to stop when the iertaction time is large
						value = scene->sampleAttenuatedEmitterDirect(
							dRec, its, rRec.medium, meeted_mediums, maxInteractions, rRec.depth, hotspotStartPoint,
							rRec.nextSample2D(), has_medium_in_single_path, rRec.sampler);
						//value = scene->sampleEmitterDirect(dRec, rRec.nextSample2D());
						////determine repetitive of sample sun rays
						//if (!value.isZero()) {
						//	bool tmp;
						//	value = repetitiveOcclude(value, its.p, dRec.d, scene, tmp);
						//}
					}
					else {//thermal
						//First, try to sample a point on a emitter
						value = scene->sampleEmitterDirect(dRec, rRec.nextSample2D());
						//if it is a planck emitter, try to decide its status of shade to assign different temperatures
						if (!value.isZero()) {
							const Emitter* emitter = static_cast<const Emitter*>(dRec.object);
							if (emitter->getProperties().hasProperty("temperature") &&
								(emitter->getProperties().getFloat("deltaTemperature", 0) != 0)) {
								//determined shaded or not
								Vector sunDirection = emitter->getProperties().getVector("direction");
								Ray occludeRay(dRec.p, -sunDirection, 0);
								bool shaded = scene->rayIntersect(occludeRay);
								if (!shaded) {
									// further determine for repetitive occlusion
									bool isRepetitiveOccluded = false;
									repetitiveOcclude(Spectrum(0.0), dRec.p, -sunDirection, scene, isRepetitiveOccluded);
									shaded = isRepetitiveOccluded;
								}
								value = emitter->getSpectrumAccordingToTemperature(dRec, its, shaded);
							}
							else { // when the sampled emitter is sky emitter, consider the repetitive
								bool tmp;
								value = repetitiveOcclude(value, its.p, dRec.d, scene, tmp);
							}
						}

					}

					//four component
					if (m_hasFourComponentProduct && rRec.depth == 1) {
						if (!value.isZero()) {//illuminated area
							if (its.shape->getName() == "terrain") {//intersect with terrain
								rRec.extra = 1; // illuminated soil
							}
							else {
								rRec.extra = 2; // illuminated object (leaf)
							}
						}
						else {//shaded area
							if (its.shape->getName() == "terrain") {//intersect with terrain
								rRec.extra = 3; // shaded soil
							}
							else {
								rRec.extra = 4; // shaded object (leaf)
							}
						}
					}

					if (!value.isZero()) {
						const Emitter* emitter = static_cast<const Emitter*>(dRec.object);

						/* Allocate a record for querying the BSDF */
						BSDFSamplingRecord bRec(its, its.toLocal(dRec.d), ERadiance);

						/* Evaluate BSDF * cos(theta) */
						Spectrum bsdfVal;// = bsdf->eval(bRec);
						FluorMatrix ttm;
						ttm.setFluorMatrixZeros();
						if (isFluor2MixtureBSDF) {
							bsdfVal = bsdf->evalWithEF(bRec, ms, ttm);
						}
						else {
							bsdfVal = bsdf->eval(bRec);
						}

						/* Prevent light leaks due to the use of shading normals */
						if (!bsdfVal.isZero() && (!m_strictNormals
							|| dot(its.geoFrame.n, dRec.d) * Frame::cosTheta(bRec.wo) > 0)) {
							/* Calculate prob. of having generated that direction
							   using BSDF sampling */
							Float bsdfPdf = (emitter->isOnSurface() && dRec.measure == ESolidAngle)
								? bsdf->pdf(bRec) : 0;
							/* Weight using the power heuristic */
							Float weight = miWeight(dRec.pdf, bsdfPdf);
							if (m_isOnlyMultiScattering && rRec.depth == 1) {

							}
							else {
								Spectrum throughput_value_weight_bsdfVal = throughput * value * bsdfVal * weight;
								if (isFluor2MixtureBSDF) {
									m.compute_Mb1xMb2_isFluor2Mixture_mt(mt, throughput, ttm, bsdfVal);
								}
								else {
									m.compute_Mb1xMb2_isNotFluor2Mixture_mt(mt, bsdfVal);
								}
								Spectrum powerPSIt(0.0f);
								Spectrum powerPSIIt(0.0f);
								mt.compute_MbxPower(value, powerPSIt, powerPSIIt, LiAll, LiPSI, LiPSII, weight);
								LiAll += throughput_value_weight_bsdfVal;
								Li += throughput_value_weight_bsdfVal;
							}

						}
					}
				}

				/* ==================================================================== */
				/*                            BSDF sampling                             */
				/* ==================================================================== */

				/* Sample BSDF * cos(theta) */
				Float bsdfPdf;
				BSDFSamplingRecord bRec(its, rRec.sampler, ERadiance);
				//if (times++ > 10) {
				//	cout << times <<" rRec"<< rRec.depth<< endl;
				//	if (times == 502) {
				//		int b = 0;
				//	}
				//}
				max_interaaction_times++;
				//	if (max_interaaction_times >= 200) break; //hlton simpler only support max dimension 1024, we need to stop when the iertaction time is large
				Spectrum bsdfWeight;
				FluorMatrix tm; tm.setFluorMatrixZeros();
				if (bsdf->getType() & BSDF::ENull) {
					bsdfWeight = bsdf->sample(bRec, bsdfPdf, Point2());
				}
				else if (isFluor2MixtureBSDF) {
					bsdfWeight = bsdf->sampleWithEF(bRec, bsdfPdf, rRec.nextSample2D(), bsdf->getFluorMatrixs(), tm); //bsdfWeight: 方向反射率
				}
				else {
					bsdfWeight = bsdf->sample(bRec, bsdfPdf, rRec.nextSample2D());
				}
				if (bsdfWeight.isZero())
					break;

				scattered |= bRec.sampledType != BSDF::ENull;

				/* Prevent light leaks due to the use of shading normals */
				const Vector wo = its.toWorld(bRec.wo);
				Float woDotGeoN = dot(its.geoFrame.n, wo);
				if (m_strictNormals && woDotGeoN * Frame::cosTheta(bRec.wo) <= 0)
					break;

				if (its.isMediumTransition()) {
					rRec.medium = its.getTargetMedium(wo);
					if (rRec.medium) {
						has_medium_in_single_path = true;
						meeted_mediums.emplace_back(rRec.medium);
					}
					else {
						if (meeted_mediums.size() == 1) {
							meeted_mediums.clear();
						}
						else if (meeted_mediums.size() > 0) {
							const Medium* tmp = its.getTargetMedium(-wo);
							auto itr = remove_if(meeted_mediums.begin(), meeted_mediums.end(), [&](const Medium* x) {return x == tmp; });
							if (itr >= meeted_mediums.begin() && itr < meeted_mediums.end()) {
								meeted_mediums.erase(itr);
								if (meeted_mediums.size() > 0) {
									rRec.medium = meeted_mediums[meeted_mediums.size() - 1];
								}
							}
						}

					}
				}


				bool hitEmitter = false;
				Spectrum value;

				/* Trace a ray in this direction */
				ray = Ray(its.p, wo, ray.time);
				scene->rayIntersect(ray, its);
				rayRepetitive(ray, its, scene);
				if (its.isValid()) {
					/* Intersected something - check if it was a luminaire */
					if (its.isEmitter()) {
						//For thermal direct emitted
						if (its.shape->getEmitter()->getProperties().hasProperty("temperature") &&
							its.shape->getEmitter()->getProperties().getFloat("deltaTemperature", 0) != 0) {
							Vector sunDirection = its.shape->getEmitter()->getProperties().getVector("direction");
							//test occlusion. temperature will be different when shaded or not shaded
							Ray occludeRay(its.p, -sunDirection, 0);
							if (scene->rayIntersect(occludeRay)) {
								its.shaded = true;
							}
							else {								// further determine for repetitive occlusion
								bool isRepetitiveOccluded = false;
								repetitiveOcclude(Spectrum(0.0), its.p, -sunDirection, scene, isRepetitiveOccluded);
								its.shaded = isRepetitiveOccluded;
							}
						}
						value = its.Le(-ray.d);
						dRec.setQuery(ray, its);
						hitEmitter = true;
					}
				}
				else {
					/* Intersected nothing -- perhaps there is an environment map? */
					const Emitter* env = scene->getEnvironmentEmitter();
					if (env) {
						if (m_hideEmitters && !scattered)
							break;

						value = env->evalEnvironment(ray);
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
				if (isFluor2MixtureBSDF) {
					m.compute_Mb1xMb2_isFluor2Mixture(throughput, tm, bsdfWeight);
				}
				else {
					m.compute_Mb1xMb2_isNotFluor2Mixture(bsdfWeight);
				}
				throughput *= bsdfWeight;
				eta *= bRec.eta;

				/* If a luminaire was hit, estimate the local illumination and
				   weight using the power heuristic */
				if (hitEmitter &&
					(rRec.type & RadianceQueryRecord::EDirectSurfaceRadiance)) {
					/* Compute the prob. of generating that direction using the
					   implemented direct illumination sampling technique */
					const Float lumPdf = (!(bRec.sampledType & BSDF::EDelta)) ?
						scene->pdfEmitterDirect(dRec) : 0;
					Float miWeight_bsdfPdf_lumPdf_ = miWeight(bsdfPdf, lumPdf);
					Spectrum throughput_value_miWeight_bsdfPdf_lumPdf_ = throughput * value * miWeight_bsdfPdf_lumPdf_;
					Spectrum powerPSIt(0.0f);
					Spectrum powerPSIIt(0.0f);
					mt.compute_MbxPower(value, powerPSIt, powerPSIIt, LiAll, LiPSI, LiPSII, miWeight_bsdfPdf_lumPdf_);
					LiAll += throughput_value_miWeight_bsdfPdf_lumPdf_;
					Li += throughput_value_miWeight_bsdfPdf_lumPdf_;
				}

				/* ==================================================================== */
				/*                         Indirect illumination                        */
				/* ==================================================================== */

				/* Set the recursive query type. Stop if no surface was hit by the
				   BSDF sample or if indirect illumination was not requested */
				if (!its.isValid() || !(rRec.type & RadianceQueryRecord::EIndirectSurfaceRadiance))
					break;
				rRec.type = RadianceQueryRecord::ERadianceNoEmission;

				//If is null intersection, we do not increase depth
				if (bsdf->getType() & BSDF::ENull) {
					if (rRec.medium && !isReachHotspotPosition) {
						hotspotStartPoint = ray.o;
						isReachHotspotPosition = true;
					}
					continue;
				}
			}
			if (rRec.depth++ >= m_rrDepth) {
				/* Russian roulette: try to keep path weights equal to one,
				   while accounting for the solid angle compression at refractive
				   index boundaries. Stop with at least some probability to avoid
				   getting stuck (e.g. due to total internal reflection) */

				Float q = std::min(throughput.max() * eta * eta, (Float)0.95f);
				if (rRec.nextSample1D() >= q)
					break;
				throughput /= q;
				m.compute_DivideEqual(q);
			}
		}

		/* Store statistics */
		avgPathLength.incrementBase();
		avgPathLength += rRec.depth;

		return Li;
	}

	inline Float miWeight(Float pdfA, Float pdfB) const {
		pdfA *= pdfA;
		pdfB *= pdfB;
		return pdfA / (pdfA + pdfB);
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "MIPathTracer[" << endl
			<< "  maxDepth = " << m_maxDepth << "," << endl
			<< "  rrDepth = " << m_rrDepth << "," << endl
			<< "  strictNormals = " << m_strictNormals << endl
			<< "]";
		return oss.str();
	}

	MTS_DECLARE_CLASS()
protected:
	double m_NoDataValue;
	bool m_virtualPlane;
	double m_virtualPlane_vx;
	std::string m_strVirtualPlane_vy;
	//double m_virtualPlane_vy;
	double m_virtualPlane_vz;
	double m_virtualPlane_size_x;
	double m_virtualPlane_size_z;

	double m_sceneXSize;
	double m_sceneZSize;

	int m_repetitiveSceneNum;

	AABB m_sceneBounds;
	AABB m_virtualBounds;

	bool m_isThermal;

	bool m_isOnlyMultiScattering; //Only records the multiple scattering energy for a image

	//for orth images
	bool m_isOrthPhoto;
	Float m_reference_height;
	Vector m_sensor_direction;
};

MTS_IMPLEMENT_CLASS_S(MIPathVolTracer, false, MonteCarloIntegrator)
MTS_EXPORT_PLUGIN(MIPathVolTracer, "MI path vol tracer");
MTS_NAMESPACE_END
