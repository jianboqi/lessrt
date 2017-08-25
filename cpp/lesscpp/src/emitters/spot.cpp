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
#include <mitsuba/hw/basicshader.h>

MTS_NAMESPACE_BEGIN

/*!\plugin{spot}{Spot light source}
 * \icon{emitter_spot}
 * \order{3}
 * \parameters{
 *     \parameter{toWorld}{\Transform\Or\Animation}{
 *	      Specifies an optional sensor-to-world transformation.
 *        \default{none (i.e. sensor space $=$ world space)}
 *     }
 *     \parameter{intensity}{\Spectrum}{
 *         Specifies the maximum radiant intensity at the center
 *         in units of power per unit steradian.
 *         \default{1}
 *     }
 *     \parameter{cutoffAngle}{\Float}{Cutoff angle, beyond which the spot light is completely black \default{\code{20} degrees}}
 *     \parameter{beamWidth}{\Float}{Subtended angle of the central beam portion \default{\code{cutoffAngle}$\ \cdot\ \nicefrac 34$}}
 *     \parameter{texture}{\Texture}{
 *         An optional texture to be projected along the spot light
 *     }
 *     \parameter{samplingWeight}{\Float}{
 *         Specifies the relative amount of samples
 *         allocated to this emitter. \default{1}
 *     }
 * }
 *
 * This plugin provides a spot light with a linear falloff.
 * In its local coordinate system, the spot light is positioned at the origin
 * and points along the positive Z direction. It can be conveniently
 * reoriented using the \code{lookat} tag, e.g.:
 * \begin{xml}
 * <emitter type="spot">
 *     <transform name="toWorld">
 *         <!-- Orient the light so that points from (1, 1, 1) towards (1, 2, 1) -->
 *         <lookat origin="1, 1, 1" target="1, 2, 1"/>
 *     </transform>
 * </emitter>
 * \end{xml}
 *
 * The intensity linearly ramps up from \code{cutoffAngle}
 * to \code{beamWidth} (both specified in degrees), after which it remains at
 * the maximum value. A projection texture may optionally be supplied.
 */

class SpotEmitter : public Emitter {
public:
	SpotEmitter(const Properties &props) : Emitter(props) {
		m_intensity = props.getSpectrum("intensity", Spectrum(1.0f));
		m_cutoffAngle = props.getFloat("cutoffAngle", 20);
		m_beamWidth = props.getFloat("beamWidth", m_cutoffAngle * 3.0f/4.0f);
		m_beamWidth = degToRad(m_beamWidth);
		m_cutoffAngle = degToRad(m_cutoffAngle);
		Assert(m_cutoffAngle >= m_beamWidth);
		m_type = EDeltaPosition;
		m_texture = new ConstantSpectrumTexture(
			props.getSpectrum("texture", Spectrum::getD65()));
	}

	SpotEmitter(Stream *stream, InstanceManager *manager)
		: Emitter(stream, manager) {
		m_texture = static_cast<Texture *>(manager->getInstance(stream));
		m_intensity = Spectrum(stream);
		m_beamWidth = stream->readFloat();
		m_cutoffAngle = stream->readFloat();
		configure();
	}

	void configure() {
		m_cosBeamWidth = std::cos(m_beamWidth);
		m_cosCutoffAngle = std::cos(m_cutoffAngle);
		m_uvFactor = std::tan(m_cutoffAngle);
		m_invTransitionWidth = 1.0f / (m_cutoffAngle - m_beamWidth);
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Emitter::serialize(stream, manager);

		manager->serialize(stream, m_texture.get());
		m_intensity.serialize(stream);
		stream->writeFloat(m_beamWidth);
		stream->writeFloat(m_cutoffAngle);
	}

	inline Spectrum falloffCurve(const Vector &d) const {
		const Float cosTheta = Frame::cosTheta(d);

		if (cosTheta <= m_cosCutoffAngle)
			return Spectrum(0.0f);

		Spectrum result(1.0f);
		if (m_texture->getClass() != MTS_CLASS(ConstantSpectrumTexture)) {
			Intersection its;
			its.hasUVPartials = false;
			its.uv = Point2(0.5f + 0.5f * d.x / (d.z * m_uvFactor),
			                0.5f + 0.5f * d.y / (d.z * m_uvFactor));
			result = m_texture->eval(its);
		}

		if (cosTheta >= m_cosBeamWidth)
			return result;

		return result * ((m_cutoffAngle - std::acos(cosTheta))
				* m_invTransitionWidth);
	}

	Spectrum samplePosition(PositionSamplingRecord &pRec, const Point2 &sample,
			const Point2 *extra) const {
		const Transform &trafo = m_worldTransform->eval(pRec.time);
		pRec.p = trafo.transformAffine(Point(0.0f));
		pRec.n = Normal(0.0f);
		pRec.pdf = 1.0f;
		pRec.measure = EDiscrete;
		return m_intensity * (4 * M_PI);
	}

	Spectrum evalPosition(const PositionSamplingRecord &pRec) const {
		return (pRec.measure == EDiscrete) ? (m_intensity * 4*M_PI) : Spectrum(0.0f);
	}

	Float pdfPosition(const PositionSamplingRecord &pRec) const {
		return (pRec.measure == EDiscrete) ? 1.0f : 0.0f;
	}

	Spectrum sampleDirection(DirectionSamplingRecord &dRec,
			PositionSamplingRecord &pRec,
			const Point2 &sample,
			const Point2 *extra) const {
		const Transform &trafo = m_worldTransform->eval(pRec.time);
		Vector d = warp::squareToUniformCone(m_cosCutoffAngle, sample);
		dRec.d = trafo(d);
		dRec.pdf = warp::squareToUniformConePdf(m_cosCutoffAngle);
		dRec.measure = ESolidAngle;
		return evalDirection(dRec, pRec)/dRec.pdf;
	}

	Float pdfDirection(const DirectionSamplingRecord &dRec,
			const PositionSamplingRecord &pRec) const {
		return (dRec.measure == ESolidAngle) ? warp::squareToUniformConePdf(m_cosCutoffAngle) : 0.0f;
	}

	Spectrum evalDirection(const DirectionSamplingRecord &dRec,
			const PositionSamplingRecord &pRec) const {
		const Transform &trafo = m_worldTransform->eval(pRec.time);
		return (dRec.measure == ESolidAngle) ?
			falloffCurve(trafo.inverse()(dRec.d)) * INV_FOURPI : Spectrum(0.0f);
	}

	Spectrum sampleRay(Ray &ray,
			const Point2 &spatialSample,
			const Point2 &directionalSample,
			Float time) const {
		const Transform &trafo = m_worldTransform->eval(time);

		Vector local = warp::squareToUniformCone(
			m_cosCutoffAngle, directionalSample);
		ray.setTime(time);
		ray.setOrigin(trafo.transformAffine(Point(0.0f)));
		ray.setDirection(trafo(local));
		Float dirPdf = warp::squareToUniformConePdf(m_cosCutoffAngle);
		return m_intensity * falloffCurve(local) / dirPdf;
	}

	Spectrum sampleDirect(DirectSamplingRecord &dRec, const Point2 &sample) const {
		const Transform &trafo = m_worldTransform->eval(dRec.time);

		dRec.p = trafo.transformAffine(Point(0.0f));
		dRec.pdf = 1.0f;
		dRec.measure = EDiscrete;
		dRec.uv = Point2(0.5f);
		dRec.d = dRec.p - dRec.ref;
		dRec.dist = dRec.d.length();
		Float invDist = 1.0f / dRec.dist;
		dRec.d *= invDist;
		dRec.n = Normal(0.0f);
		dRec.pdf = 1;
		dRec.measure = EDiscrete;

		return m_intensity * falloffCurve(trafo.inverse()(-dRec.d)) * (invDist * invDist);
	}

	Float pdfDirect(const DirectSamplingRecord &dRec) const {
		return dRec.measure == EDiscrete ? 1.0f : 0.0f;
	}

	void addChild(const std::string &name, ConfigurableObject *child) {
		if (child->getClass()->derivesFrom(MTS_CLASS(Texture)) && name == "texture") {
			m_texture = static_cast<Texture *>(child);
		} else {
			Emitter::addChild(name, child);
		}
	}

	AABB getAABB() const {
		return m_worldTransform->getTranslationBounds();
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "SpotEmitter[" << std::endl
			<< "  intensity = " << m_intensity.toString() << "," << std::endl
			<< "  texture = " << m_texture.toString() << "," << std::endl
			<< "  beamWidth = " << (m_beamWidth * 180/M_PI) << "," << std::endl
			<< "  cutoffAngle = " << (m_cutoffAngle * 180/M_PI) << std::endl
			<< "]";
		return oss.str();
	}


	MTS_DECLARE_CLASS()
private:
	Spectrum m_intensity;
	ref<Texture> m_texture;
	Float m_beamWidth, m_cutoffAngle, m_uvFactor;
	Float m_cosBeamWidth, m_cosCutoffAngle, m_invTransitionWidth;
};


MTS_IMPLEMENT_CLASS_S(SpotEmitter, false, Emitter)
MTS_EXPORT_PLUGIN(SpotEmitter, "Spot light");
MTS_NAMESPACE_END
