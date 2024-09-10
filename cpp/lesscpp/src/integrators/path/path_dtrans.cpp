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
class MIPathDirectTransTracer : public MonteCarloIntegrator {
public:
	MIPathDirectTransTracer(const Properties& props)
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
	}

	/// Unserialize from a binary data stream
	MIPathDirectTransTracer(Stream* stream, InstanceManager* manager)
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

		//jianboqi:
		//handle virtual plane
		if (m_virtualPlane)
		{
			double x_min = m_virtualPlane_vx - 0.5 * m_virtualPlane_size_x;
			double x_max = m_virtualPlane_vx + 0.5 * m_virtualPlane_size_x;
			double z_min = m_virtualPlane_vz - 0.5 * m_virtualPlane_size_z;
			double z_max = m_virtualPlane_vz + 0.5 * m_virtualPlane_size_z;

			double H = r.o[1] - m_virtualBounds.max.y;
			if (H > 0)
			{
				double a = r.d.x;
				double b = r.d.y;
				double c = r.d.z;
				Point its_p = r.o + Point(-a / b * H, -H, -c / b * H);
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

		if (!its.isValid()) {
			return Spectrum(1.0);
		}
		else {
			Spectrum Li(1.0);
			std::vector<const Medium*> meeted_mediums;
			while (rRec.depth <= m_maxDepth || m_maxDepth < 0) {
				if (rRec.medium && ray.maxt< std::numeric_limits<Float>::infinity()) {
					Float sigmaT = 0;
					if (meeted_mediums.size() > 1) {
						for (int i = 0; i < meeted_mediums.size(); ++i) {
							Float eachSigmaT = meeted_mediums[i]->getVegetationSigmaT(ray);
							sigmaT += eachSigmaT;
						}
					}
					else {
						sigmaT = rRec.medium->getVegetationSigmaT(ray);
					}
					//Float sigmaT = rRec.medium->getVegetationSigmaT(ray);
					Float distance = ray.maxt - ray.mint;
					Li *= Spectrum(sigmaT * (-distance)).exp();
				}


				if (!its.isValid()) break;
				if (!(its.getBSDF(ray)->getType() & BSDF::ENull))
					return Spectrum(0.0);

				if (its.isMediumTransition()) {
					rRec.medium = its.getTargetMedium(ray.d);
					if (rRec.medium) {
						meeted_mediums.push_back(rRec.medium);
					}
					else {
						if (meeted_mediums.size() == 1) {
							meeted_mediums.clear();
						}
						else if (meeted_mediums.size() > 0) {
							const Medium* tmp = its.getTargetMedium(-ray.d);
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

				ray = Ray(its.p, ray.d, ray.time);
				ray.mint = Epsilon;
				scene->rayIntersect(ray, its);
				rayRepetitive(ray, its, scene);
				ray.maxt = its.t;
				
				rRec.depth++;
			}
			return Li;
		}

		/* Store statistics */
		avgPathLength.incrementBase();
		avgPathLength += rRec.depth;

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

MTS_IMPLEMENT_CLASS_S(MIPathDirectTransTracer, false, MonteCarloIntegrator)
MTS_EXPORT_PLUGIN(MIPathDirectTransTracer, "Direct path vol tracer");
MTS_NAMESPACE_END
