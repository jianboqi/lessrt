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
class MIPathTracer : public MonteCarloIntegrator {
public:
	MIPathTracer(const Properties &props)
		: MonteCarloIntegrator(props) {
		m_NoDataValue = props.getFloat("NoDataValue", -1.0);
		m_virtualPlane = props.getBoolean("SceneVirtualPlane", false);
		m_repetitiveSceneNum = props.getInteger("RepetitiveScene", 15);
		if (m_virtualPlane) {
			m_virtualPlane_vx = props.getFloat("vx",0.0);
			m_virtualPlane_vz = props.getFloat("vz",0.0);
			m_strVirtualPlane_vy = props.getString("vy","MAX");
			m_virtualPlane_size_x = props.getFloat("sizex",100.0);
			m_virtualPlane_size_z = props.getFloat("sizez", 100.0);
		}

		m_sceneXSize = props.getFloat("subSceneXSize", 100.0);
		m_sceneZSize = props.getFloat("subSceneZSize", 100.0);

		m_isThermal = props.getBoolean("isThermal", false);

		m_isOnlyMultiScattering = props.getBoolean("isOnlyMultiScattering", false);
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
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
	}

	/// Unserialize from a binary data stream
	MIPathTracer(Stream *stream, InstanceManager *manager)
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
	}

	bool preprocess(const Scene *scene, RenderQueue *queue,
		const RenderJob *job, int sceneResID, int sensorResID,
		int samplerResID) {
		AABB scene_bound = scene->getKDTree()->getAABB();

		double sceneMaxY = scene_bound.max.y;
		double sceneMinY = scene_bound.min.y;
		double x_min = -0.5*m_sceneXSize;
		double x_max = 0.5*m_sceneXSize;
		double z_min = -0.5*m_sceneZSize;
		double z_max = 0.5*m_sceneZSize;
		m_sceneBounds = AABB(Point(x_min, sceneMinY, z_min), Point(x_max, sceneMaxY, z_max));

		if (m_virtualPlane) {
			m_virtualBounds = AABB(Point(m_virtualPlane_vx - 0.5*m_virtualPlane_size_x, sceneMinY, m_virtualPlane_vz - 0.5*m_virtualPlane_size_z),
				Point(m_virtualPlane_vx + 0.5*m_virtualPlane_size_x, sceneMaxY, m_virtualPlane_vz + 0.5*m_virtualPlane_size_z));
		}
		else {
			m_virtualBounds = m_sceneBounds;
		}
		return true;
	}

	//test occlusion for sun direct rays given reference point p and direction d
	Spectrum repetitiveOcclude(Spectrum value, Point p, Vector d, const Scene* scene, bool & isRepetitiveOcclude)const {
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

	void rayRepetitive(RayDifferential &ray, Intersection &its, const Scene *scene) const{
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

	Spectrum Li(const RayDifferential &r, RadianceQueryRecord &rRec) const {
		/* Some aliases and local variables */
		const Scene *scene = rRec.scene;
		Intersection &its = rRec.its;
		RayDifferential ray(r);
		Spectrum Li(0.0f);
		bool scattered = false;

		//jianboqi:
		//handle virtual plane
		if (m_virtualPlane)
		{			
			double x_min = m_virtualPlane_vx - 0.5*m_virtualPlane_size_x;
			double x_max = m_virtualPlane_vx + 0.5*m_virtualPlane_size_x;
			double z_min = m_virtualPlane_vz - 0.5*m_virtualPlane_size_z;
			double z_max = m_virtualPlane_vz + 0.5*m_virtualPlane_size_z;

			double H = r.o[1] - m_virtualBounds.max.y;
			if (H > 0)
			{
				double a = r.d.x;
				double b = r.d.y;
				double c = r.d.z;
				Point its_p = r.o + Point(-a / b*H, -H, -c / b*H);
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
		rayRepetitive(ray, its, scene);

		Spectrum throughput(1.0f);
		Float eta = 1.0f;

		while (rRec.depth <= m_maxDepth || m_maxDepth < 0) {

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

			const BSDF *bsdf = its.getBSDF(ray);

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
				Spectrum value;
				if (!m_isThermal) {
					value = scene->sampleEmitterDirect(dRec, rRec.nextSample2D());
					//determine repetitive of sample sun rays
					if (!value.isZero()) {
						bool tmp;
						value = repetitiveOcclude(value, its.p, dRec.d, scene, tmp);
					}
				}
				else {//thermal
					//First, try to sample a point on a emitter
					value = scene->sampleEmitterDirect(dRec, rRec.nextSample2D());
					//if it is a planck emitter, try to decide its status of shade to assign different temperatures
					if (!value.isZero()) {
						const Emitter *emitter = static_cast<const Emitter *>(dRec.object);
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
							value = emitter->getSpectrumAccordingToTemperature(dRec, shaded);
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
					const Emitter *emitter = static_cast<const Emitter *>(dRec.object);

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
			Spectrum bsdfWeight = bsdf->sample(bRec, bsdfPdf, rRec.nextSample2D());
			if (bsdfWeight.isZero())
				break;

			scattered |= bRec.sampledType != BSDF::ENull;

			/* Prevent light leaks due to the use of shading normals */
			const Vector wo = its.toWorld(bRec.wo);
			Float woDotGeoN = dot(its.geoFrame.n, wo);
			if (m_strictNormals && woDotGeoN * Frame::cosTheta(bRec.wo) <= 0)
				break;

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
			} else {
				/* Intersected nothing -- perhaps there is an environment map? */
				const Emitter *env = scene->getEnvironmentEmitter();
				if (env) {
					if (m_hideEmitters && !scattered)
						break;

					value = env->evalEnvironment(ray);
					if (!env->fillDirectSamplingRecord(dRec, ray))
						break;
					hitEmitter = true;
				} else {
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
};

MTS_IMPLEMENT_CLASS_S(MIPathTracer, false, MonteCarloIntegrator)
MTS_EXPORT_PLUGIN(MIPathTracer, "MI path tracer");
MTS_NAMESPACE_END
