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
#include <mitsuba/core/warp.h>
#include <string>

MTS_NAMESPACE_BEGIN

/* Apparent radius of the sun as seen from the earth (in degrees).
This is an approximation--the actual value is somewhere between
0.526 and 0.545 depending on the time of year */
//#define SUN_APP_RADIUS 0.5358

/*!\plugin{directional}{Directional emitter}
 * \icon{emitter_directional}
 * \order{4}
 * \parameters{
 *     \parameter{toWorld}{\Transform\Or\Animation}{
 *	      Specifies an optional emitter-to-world transformation.
 *        \default{none (i.e. emitter space $=$ world space)}
 *     }
 *     \parameter{direction}{\Vector}{
 *        Alternative to \code{toWorld}: explicitly specifies
 *        the illumination direction. Note that only one of the
 *        two parameters can be used.
 *     }
 *     \parameter{irradiance}{\Spectrum}{
 *         Specifies the amount of power per unit area received
 *         by a hypothetical surface normal to the specified direction
 *         \default{1}
 *     }
 *     \parameter{samplingWeight}{\Float}{
 *         Specifies the relative amount of samples
 *         allocated to this emitter. \default{1}
 *     }
 * }
 *
 * This emitter plugin implements a distant directional source, which
 * radiates a specified power per unit area along a fixed direction.
 * By default, the emitter radiates in the direction of the postive Z axis.
 */

class DirectionalEmitter : public Emitter {
public:
	DirectionalEmitter(const Properties &props) : Emitter(props) {
		m_type |= EDeltaDirection;

		m_normalIrradiance = props.getSpectrum("irradiance", Spectrum::getD65());
		if (props.hasProperty("direction")) {
			if (props.hasProperty("toWorld"))
				Log(EError, "Only one of the parameters 'direction' and 'toWorld'"
					"can be used at a time!");

			Vector d(normalize(props.getVector("direction"))), u, unused;
			coordinateSystem(d, u, unused);
			m_worldTransform = new AnimatedTransform(
				Transform::lookAt(Point(0.0f), Point(d), u));
		} else {
			if (props.getTransform("toWorld", Transform()).hasScale())
				Log(EError, "Scale factors in the emitter-to-world "
					"transformation are not allowed!");
		}
		m_distance = props.getFloat("emitterDistance", 100000);

		//virtual bounds to narrow the illumination area
		m_hasVirtualPlane = props.getBoolean("virtualBounds", false);
	}

	DirectionalEmitter(Stream *stream, InstanceManager *manager)
	 : Emitter(stream, manager) {
		m_normalIrradiance = Spectrum(stream);
		m_bsphere = BSphere(stream);
		m_distance = stream->readFloat();
		m_hasVirtualPlane = stream->readBool();
		configure();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Emitter::serialize(stream, manager);
		m_normalIrradiance.serialize(stream);
		m_bsphere.serialize(stream);
		stream->writeFloat(m_distance);
		stream->writeBool(m_hasVirtualPlane);
	}

	ref<Shape> createShape(const Scene *scene) {
		/* Create a bounding sphere that surrounds the scene */
		if (m_hasVirtualPlane) {
			Vector2 sceneSize = Vector2(scene->getIntegrator()->getProperties().getFloat("subSceneXSize", 100),
				scene->getIntegrator()->getProperties().getFloat("subSceneZSize", 100));

			Vector2 virtualPlaneCenter = Vector2(scene->getIntegrator()->getProperties().getFloat("vx", 0),
				scene->getIntegrator()->getProperties().getFloat("vz", 0));
			Vector2 virtualPlaneSize = Vector2(scene->getIntegrator()->getProperties().getFloat("sizex", sceneSize.x),
				scene->getIntegrator()->getProperties().getFloat("sizez", sceneSize.y));

			double virtualPlaneHeight;
			std::string heightString = scene->getIntegrator()->getProperties().getString("vy", "MAX");
			if (heightString == "MAX") {
				AABB scene_bound = scene->getKDTree()->getAABB();
				virtualPlaneHeight = scene_bound.max.y;
			}
			else {
				virtualPlaneHeight = atof(heightString.c_str());
			}

			//virtual box
			double x_min = virtualPlaneCenter.x - 0.5*virtualPlaneSize.x;
			double x_max = virtualPlaneCenter.x + 0.5*virtualPlaneSize.x;
			double z_min = virtualPlaneCenter.y - 0.5*virtualPlaneSize.y;
			double z_max = virtualPlaneCenter.y + 0.5*virtualPlaneSize.y;
			AABB virtualbox = AABB(Point(x_min, 0, z_min), Point(x_max, virtualPlaneHeight, z_max));
			m_bsphere = virtualbox.getBSphere();//目前没有使用这个
			
		}
		else {
			m_bsphere = scene->getKDTree()->getAABB().getBSphere();
		}
		m_bsphere.radius *= 1.1f;
		configure();
		return NULL;
	}

	void configure() {
		Emitter::configure();
		Float surfaceArea = M_PI * m_bsphere.radius * m_bsphere.radius;
		m_invSurfaceArea = 1.0f / surfaceArea;
		//这里很奇怪，如果直接写m_power=m_normalIrradiance * surfaceArea,在并行计算时，
		//如果核数量比较多时，会出错。
		Spectrum tmp = m_normalIrradiance * surfaceArea;
		m_power = tmp;
		//m_power = Spectrum(0.0);
	}

	Spectrum samplePosition(PositionSamplingRecord &pRec, const Point2 &sample, const Point2 *extra) const {
		const Transform &trafo = m_worldTransform->eval(pRec.time);

		Point2 p = warp::squareToUniformDiskConcentric(sample);

		Vector perpOffset = trafo(Vector(p.x, p.y, 0) * m_bsphere.radius);
		Vector d = trafo(Vector(0, 0, 1));

		//pRec.p = m_bsphere.center - d*m_bsphere.radius + perpOffset;
		pRec.p = m_bsphere.center - d * m_distance + perpOffset;
		pRec.n = d;
		pRec.pdf = m_invSurfaceArea;
		pRec.measure = EArea;
		return m_power;
	}

	Spectrum evalPosition(const PositionSamplingRecord &pRec) const {
		return (pRec.measure == EArea) ? m_normalIrradiance : Spectrum(0.0f);
	}

	Float pdfPosition(const PositionSamplingRecord &pRec) const {
		return (pRec.measure == EArea) ? m_invSurfaceArea : 0.0f;
	}

	Spectrum sampleDirection(DirectionSamplingRecord &dRec,
			PositionSamplingRecord &pRec,
			const Point2 &sample, const Point2 *extra) const {
		dRec.d = pRec.n;
		dRec.pdf = 1.0f;
		dRec.measure = EDiscrete;
		return Spectrum(1.0f);
	}

	Float pdfDirection(const DirectionSamplingRecord &dRec,
			const PositionSamplingRecord &pRec) const {
		return (dRec.measure == EDiscrete) ? 1.0f : 0.0f;
	}

	Spectrum evalDirection(const DirectionSamplingRecord &dRec,
			const PositionSamplingRecord &pRec) const {
		return Spectrum((dRec.measure == EDiscrete) ? 1.0f : 0.0f);
	}

	Spectrum sampleRay(Ray &ray,
			const Point2 &spatialSample,
			const Point2 &directionalSample,
			Float time) const {
		const Transform &trafo = m_worldTransform->eval(time);
		Point2 p = warp::squareToUniformDiskConcentric(spatialSample);

		Vector perpOffset = trafo(Vector(p.x, p.y, 0) * m_bsphere.radius);
		Vector d = trafo(Vector(0, 0, 1));
		//ray.setOrigin(m_bsphere.center - d*m_bsphere.radius + perpOffset);
		ray.setOrigin(m_bsphere.center - d * m_distance + perpOffset);
		ray.setDirection(d);
		ray.setTime(time);
		return m_power;
	}

	Spectrum sampleDirect(DirectSamplingRecord &dRec, const Point2 &sample) const {
		const Transform &trafo = m_worldTransform->eval(dRec.time);
		Vector d = trafo(Vector(0,0,1));
		//Point diskCenter = m_bsphere.center - d*m_bsphere.radius;
		Point diskCenter = m_bsphere.center - d * m_distance;

		Float distance = dot(dRec.ref - diskCenter, d);
		if (distance < 0) {
			/* This can happen when doing bidirectional renderings
			   involving environment maps and directional sources. Just
			   return zero */
			return Spectrum(0.0f);
		}

		dRec.p = dRec.ref - distance * d;
		dRec.d = -d;
		dRec.n = Normal(d);
		dRec.dist = distance;

		dRec.pdf = 1.0f;
		dRec.measure = EDiscrete;
		return m_normalIrradiance;
	}

	//Spectrum evalEnvironment(const RayDifferential &ray) const {
	//	const Transform &trafo = m_worldTransform->eval(0);
	//	Vector d = -trafo(Vector(0, 0, 1));
	//	double theta = degToRad(SUN_APP_RADIUS * 0.5f);
	//	if (dot(d, ray.d) >= std::cos(theta)) {
	//		double solidAngle = 2 * M_PI * (1 - std::cos(theta));
	//		return m_normalIrradiance / solidAngle;
	//	}
	//	return Spectrum(0.0);
	//}

	Float pdfDirect(const DirectSamplingRecord &dRec) const {
		return dRec.measure == EDiscrete ? 1.0f : 0.0f;
	}

	AABB getAABB() const {
		return AABB();
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "DirectionalEmitter[" << endl
			<< "  normalIrradiance = " << m_normalIrradiance.toString() << "," << endl
			<< "  samplingWeight = " << m_samplingWeight << "," << endl
			<< "  worldTransform = " << indent(m_worldTransform.toString()) << "," << endl
			<< "  medium = " << indent(m_medium.toString()) << endl
			<< "]";
		return oss.str();
	}

	MTS_DECLARE_CLASS()
private:
	Spectrum m_normalIrradiance, m_power;
	BSphere m_bsphere;
	Float m_invSurfaceArea;
	Float m_distance; // the distance of the emitter from the scene

	//for virtual plane
	bool m_hasVirtualPlane;
};

MTS_IMPLEMENT_CLASS_S(DirectionalEmitter, false, Emitter)
MTS_EXPORT_PLUGIN(DirectionalEmitter, "Directional emitter");
MTS_NAMESPACE_END
