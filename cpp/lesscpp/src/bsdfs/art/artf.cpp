

#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/texture.h>
#include <mitsuba/render/basicshader.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/core/math.h>
#include "art_data.h"

MTS_NAMESPACE_BEGIN

class ARTF : public BSDF {
public:
	ARTF(const Properties& props)
		:BSDF(props) {
		m_L = props.getFloat("L", 1e-6);
		m_M = props.getFloat("M", 0);
		m_D = props.getFloat("D", 0);
		m_E = props.getFloat("E", 0.2);
		m_wavelengths = props.getSpectrum("wavelengths");
	}

	ARTF(Stream* stream, InstanceManager* manager)
		: BSDF(stream, manager) {
		m_L = stream->readFloat();
		m_M = stream->readFloat();
		m_D = stream->readFloat();
		m_E = stream->readFloat();
		m_wavelengths = Spectrum(stream);
		configure();
	}

	void serialize(Stream* stream, InstanceManager* manager) const {
		BSDF::serialize(stream, manager);
		stream->writeFloat(m_L);
		stream->writeFloat(m_M);
		stream->writeFloat(m_D);
		stream->writeFloat(m_E);
		m_wavelengths.serialize(stream);
	}

	void configure() {
		m_components.clear();
		m_components.push_back(EGlossyReflection | EFrontSide);
		BSDF::configure();
	}

	Spectrum computeDirectinalRelectance(const BSDFSamplingRecord& bRec) const {
		//parameter at each intersected position
		Float cosThetai = Frame::cosTheta(bRec.wi);
		Float cosThetar = Frame::cosTheta(bRec.wo);
		Float sinThetai = Frame::sinTheta(bRec.wi);
		Float sinThetar = Frame::sinTheta(bRec.wo);
		Vector wi_h = normalize(Vector(bRec.wi.x, bRec.wi.y, 0));
		Vector wo_h = normalize(Vector(bRec.wo.x, bRec.wo.y, 0));
		Float cosdPhi = -dot(wi_h, wo_h);
		if (sinThetai == 0 && sinThetar == 0) cosdPhi = 1;

		//get refraction index at specific wavelengths
		Float aa = 1.247;
		Float bb = 1.186;
		Float cc = 5.157;
		Float BigCosTheta = cosThetai * cosThetar + sinThetai * sinThetar * cosdPhi;
		Float BigTheta = acos(-BigCosTheta);
		Float pp = 11.1 * exp(-0.087 * BigTheta / M_PI_DBL * 180) + 1.1 * exp(-0.014 * BigTheta / M_PI_DBL * 180);
		Float r0 = 0.25 * (aa + bb * (cosThetai + cosThetar) + cc * cosThetai * cosThetar + pp) / (cosThetai + cosThetar);
		Float Ks = 3 * (1 + 2 * cosThetai) / 7.0;
		Float Kv = 3 * (1 + 2 * cosThetar) / 7.0;
		Spectrum reflectance;
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			Float wavelength = m_wavelengths[i];
			Float left_wavelength = int(wavelength);
			Float right_wavelength = int(wavelength) + 1;
			if (wavelength < 400) {
				left_wavelength = right_wavelength = 400;
			}
			if (wavelength > 2500) {
				left_wavelength = right_wavelength = 2500;
			}
			int left_index = int(left_wavelength - 400);
			int right_index = int(right_wavelength - 400);
			Float deltaY = RefractionIndexARTF[right_index] - RefractionIndexARTF[left_index];
			Float refraction = deltaY * (wavelength - left_wavelength) + RefractionIndexARTF[left_index];

			Float alpha = sqrt(4. * M_PI_DBL * m_L * (refraction + m_M) / (wavelength*1e-9));
			Float fg = cos(BigCosTheta) * exp(-cos(BigCosTheta)) - exp(-1);
			Float rso = r0* exp(-alpha * Ks * Kv / r0) * (m_E - m_D * fg);
			/*Float alpha = 5.8 * sqrt(4 * M_PI_DBL * m_particle_size * (refraction + 0.2 * m_pollution_content) / wavelength * 1000);
			Float rso = r0 * exp(-alpha * Ks * Kv / r0);*/
			reflectance[i] = rso;
		}
		return reflectance;
	}

	Spectrum eval(const BSDFSamplingRecord& bRec, EMeasure measure) const {
		if (!(bRec.typeMask & EGlossyReflection) || measure != ESolidAngle
			|| Frame::cosTheta(bRec.wi) <= 0
			|| Frame::cosTheta(bRec.wo) <= 0)
			return Spectrum(0.0f);
		return computeDirectinalRelectance(bRec) * (INV_PI * Frame::cosTheta(bRec.wo));
	}
	Spectrum evalWithEF(const BSDFSamplingRecord& bRec,
		FluorMatrixs ms, FluorMatrix& m, EMeasure measure) const {
		return Spectrum(0.0f);
	}

	Float pdf(const BSDFSamplingRecord& bRec, EMeasure measure) const {
		if (!(bRec.typeMask & EDiffuseReflection) || measure != ESolidAngle
			|| Frame::cosTheta(bRec.wi) <= 0
			|| Frame::cosTheta(bRec.wo) <= 0)
			return 0.0f;
		return warp::squareToCosineHemispherePdf(bRec.wo);
	}

	Spectrum sample(BSDFSamplingRecord& bRec, const Point2& sample) const {
		//当碰撞到背面时，返回一个负值
		if (!(bRec.typeMask & EGlossyReflection) || Frame::cosTheta(bRec.wi) <= 0)
			return Spectrum(-1.0f);

		bRec.wo = warp::squareToCosineHemisphere(sample);
		bRec.eta = 1.0f;
		bRec.sampledComponent = 0;
		bRec.sampledType = EGlossyReflection;
		return computeDirectinalRelectance(bRec);
	}
	Spectrum sampleWithEF(BSDFSamplingRecord& bRec, const Point2& sample,
		FluorMatrixs ms, FluorMatrix& m) const {
		return Spectrum(0.0f);
	}

	Spectrum sample(BSDFSamplingRecord& bRec, Float& pdf, const Point2& sample) const {
		if (!(bRec.typeMask & EGlossyReflection) || Frame::cosTheta(bRec.wi) <= 0)
			return Spectrum(0.0f);
		bRec.wo = warp::squareToCosineHemisphere(sample);
		bRec.eta = 1.0f;
		bRec.sampledComponent = 0;
		bRec.sampledType = EGlossyReflection;
		pdf = warp::squareToCosineHemispherePdf(bRec.wo);
		return computeDirectinalRelectance(bRec);
	}
	Spectrum sampleWithEF(BSDFSamplingRecord& bRec, Float& pdf, const Point2& sample,
		FluorMatrixs ms, FluorMatrix& m) const {
		return Spectrum(0.0f);
	}


	void addChild(const std::string& name, ConfigurableObject* child) {
		if (child->getClass()->derivesFrom(MTS_CLASS(Texture))) {
		}
		else {
			BSDF::addChild(name, child);
		}
	}

	Float getRoughness(const Intersection& its, int component) const {
		return std::numeric_limits<Float>::infinity();
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "ARTF[" << endl
			<< "]";
		return oss.str();
	}
	MTS_DECLARE_CLASS()
private:
	Float m_L;
	Float m_M;
	Float m_D;
	Float m_E;
	Spectrum m_wavelengths;
};

MTS_IMPLEMENT_CLASS_S(ARTF, false, BSDF)
MTS_EXPORT_PLUGIN(ARTF, "ARTF BRDF")
MTS_NAMESPACE_END