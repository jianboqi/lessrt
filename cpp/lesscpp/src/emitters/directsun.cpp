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

MTS_NAMESPACE_BEGIN

class DirectSunEmitter : public Emitter {
public:
	DirectSunEmitter(const Properties &props) : Emitter(props) {
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
	}

	DirectSunEmitter(Stream *stream, InstanceManager *manager)
	 : Emitter(stream, manager) {
		m_normalIrradiance = Spectrum(stream);
		scene_aabb = AABB(stream);
		configure();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Emitter::serialize(stream, manager);
		m_normalIrradiance.serialize(stream);
		scene_aabb.serialize(stream);
	}

	ref<Shape> createShape(const Scene *scene) {
		scene_aabb = scene->getKDTree()->getAABB();

		Point2 scene_min = Point2(scene_aabb.min.x >= 0 ? std::ceil(scene_aabb.min.x) : std::floor(scene_aabb.min.x),
			scene_aabb.min.z >= 0 ? std::ceil(scene_aabb.min.z) : std::floor(scene_aabb.min.z));
		Point2 scene_max = Point2(scene_aabb.max.x >= 0 ? std::ceil(scene_aabb.max.x) : std::floor(scene_aabb.max.x),
			scene_aabb.max.z >= 0 ? std::ceil(scene_aabb.max.z) : std::floor(scene_aabb.max.z));
		scene_extends_integer = scene_max - scene_min;
		scene_extends = scene_aabb.getExtents();
		m_emitterHeight = scene_aabb.max.y+1;
		configure();
		return NULL;
	}

	void configure() {
		Emitter::configure();
		Float surfaceArea = scene_extends_integer.x * scene_extends_integer.y;
		m_invSurfaceArea = 1.0f / surfaceArea;

		const Transform &trafo = m_worldTransform->eval(0);
		Vector d = -trafo(Vector(0, 0, 1));
		m_incident_cos = dot(d, Vector(0, 1, 0));
		m_power = m_normalIrradiance * surfaceArea * m_incident_cos;
	}

	Spectrum samplePosition(PositionSamplingRecord &pRec, const Point2 &sample, const Point2 *extra) const {
		const Transform &trafo = m_worldTransform->eval(pRec.time);
		Vector d = trafo(Vector(0, 0, 1));
		pRec.p = Point(scene_aabb.min.x + sample.x*scene_extends.x, m_emitterHeight, scene_aabb.min.z + sample.y*scene_extends.z);
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
		Vector d = trafo(Vector(0, 0, 1));
		ray.setOrigin(Point(0, m_emitterHeight, 0));
		ray.setDirection(d);
		ray.setTime(time);
		return m_power;
	}

	Spectrum sampleDirect(DirectSamplingRecord &dRec, const Point2 &sample) const {
		const Transform &trafo = m_worldTransform->eval(dRec.time);
		Vector d = trafo(Vector(0,0,1));
		Float distance = (m_emitterHeight - dRec.ref.y) / m_incident_cos;
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

	Float pdfDirect(const DirectSamplingRecord &dRec) const {
		return dRec.measure == EDiscrete ? 1.0f : 0.0f;
	}

	AABB getAABB() const {
		return AABB();
	}


	std::string toString() const {
		std::ostringstream oss;
		oss << "DirectSunEmitter[" << endl
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
	AABB scene_aabb;
	Vector scene_extends; // real scene extends
	Vector2 scene_extends_integer; // round to integer extends
	Float m_emitterHeight; //emitter height
	Float m_incident_cos; // cos term of incident angle
	Float m_invSurfaceArea;
};

MTS_IMPLEMENT_CLASS_S(DirectSunEmitter, false, Emitter)
MTS_EXPORT_PLUGIN(DirectSunEmitter, "DirectSun emitter");
MTS_NAMESPACE_END
