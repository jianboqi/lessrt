

#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/texture.h>
#include <mitsuba/render/basicshader.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/core/math.h>
#include <boost/math/special_functions/expint.hpp>
#include "hapke_marmit2_data.h"
#include <complex> //
MTS_NAMESPACE_BEGIN

class HapkeMarmit2 : public BSDF {
public:
	HapkeMarmit2(const Properties& props)
		:BSDF(props) {
		m_b = props.getFloat("b", 5.0);
		m_M = props.getFloat("M", 0.5);
		m_theta = props.getFloat("theta", 0.15);
		m_L = props.getFloat("L", 0.1);
		m_sigma = props.getFloat("sigma", 0.6);
		m_wavelengths = props.getSpectrum("wavelengths");
	}

	HapkeMarmit2(Stream* stream, InstanceManager* manager)
		: BSDF(stream, manager) {
		m_b = stream->readFloat();
		m_M = stream->readFloat();
		m_theta = stream->readFloat();
		m_L = stream->readFloat();
		m_sigma = stream->readFloat();
		m_wavelengths = Spectrum(stream);
		configure();
	}

	void serialize(Stream* stream, InstanceManager* manager) const {
		BSDF::serialize(stream, manager);
		stream->writeFloat(m_b);
		stream->writeFloat(m_M);
		stream->writeFloat(m_theta);
		stream->writeFloat(m_L);
		stream->writeFloat(m_sigma);
		m_wavelengths.serialize(stream);
	}

	void configure() {
		m_components.clear();
		m_components.push_back(EGlossyReflection | EFrontSide);
		BSDF::configure();

		//precompute coefficient for each bands
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			//get soil and water properties at specific wavelengths
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
			Float deltaY = data_soil_k[right_index] - data_soil_k[left_index];
			Float soil_k = deltaY * (wavelength - left_wavelength) + data_soil_k[left_index];
			deltaY = data_water_n_w[right_index] - data_water_n_w[left_index];
			Float water_n_w = deltaY * (wavelength - left_wavelength) + data_water_n_w[left_index];
			/*Float deltaY = data_water_k_w[right_index] - data_water_k_w[left_index];
			Float water_k_w = deltaY * (wavelength - left_wavelength) + data_water_k_w[left_index];*/
			deltaY = data_water_alpha_w[right_index] - data_water_alpha_w[left_index];
			Float water_alpha_w = deltaY * (wavelength - left_wavelength) + data_water_alpha_w[left_index];
			m_soil_k[i] = soil_k;
			m_water_n_w[i] = water_n_w;
			m_water_alpha_w[i] = water_alpha_w;
		}
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
		Float n_i = 1.53; Float k_i = 0.001;
		Spectrum reflectance;
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			Float wavelength = m_wavelengths[i];
			//compute the hapke function
			Float w = 1 - (4. * M_PI_DBL * m_M * m_soil_k[i]) / (wavelength / 1000000.0);
			Float c = 0.4;
			Float c1 = 0;
			Float B0 = 0.4;
			Float h = 0.1;
			Float b1 = 0.4;
			Float g = cosThetai * cosThetar + sinThetai * sinThetar * cosdPhi;
			Float g1 = cosThetai * cosThetar - sinThetai * sinThetar * cosdPhi;
			Float Pg = 1 + m_b * g + (c * (3 * g * g - 1)) / 2.0 + b1 * g1 + (c1 * (3 * g1 * g1 - 1)) / 2.0;
			Float Bg = B0 / (1 + tan(math::safe_acos(g) / 2) / h);
			Float Hs = ((1 + 2 * cosThetai) / (1 + 2 * cosThetai * math::safe_sqrt(1 - w)));
			Float Hv = ((1 + 2 * cosThetar) / (1 + 2 * cosThetar * math::safe_sqrt(1 - w)));
			Float ref = (w / 4) * (1.0 / (cosThetai + cosThetar)) * (Pg * (1 + Bg) + Hs * Hv - 1);
			//obtain the reflectance of the dry soil
			Float dry_ref = 0.7835 + 0.7969 * ref;

			// Use the reflectance of the dry soil to compute the reflectance of the wet soil with the marmit model
			// imaginary part of refractive index of water
			Float k_w = m_water_alpha_w[i] * wavelength * 1e-7 / (4 * M_PI_DBL);
			// complex permittivity of water
			/*
			* compute complex number analytically
			Float a = m_theta * (n_i * n_i - k_i * k_i - water_n_w * water_n_w + k_w * k_w) + water_n_w * water_n_w - k_w * k_w;
			Float b = 2 * (n_i * k_i * m_theta + water_n_w * k_w - water_n_w * k_w * m_theta);
			Float n = b/(2*sqrt((-a+sqrt(a*a+b*b))/2));
			Float k = sqrt((-a + sqrt(a * a + b * b)) / 2);*/
			std::complex<double> z(m_water_n_w[i], k_w); //
			std::complex<double> e_w = z * z; // complex permittivity of water
			//complex permittivity of soil particles
			std::complex<double> z1(n_i, k_i);
			std::complex<double> e_i = z1 * z1; // complex permittivity of soil particles
			// dielectric average
			std::complex<double> e = m_theta * e_i + (1 - m_theta) * e_w;
			// effectice refractive index of the mixture
			std::complex<double> e_sqrt = sqrt(e);
			Float n = e_sqrt.real();
			Float k = e_sqrt.imag();

			//effective absorption coefficient
			Float alpha = 4 * M_PI_DBL * k / (wavelength * 1e-7);
			//Fresnel coefficients integrated over the hemisphere
			Float r12_diffuse = (
				(3 * n * n + 2 * n + 1) / (3 * pow(n + 1,2))
				- 2 * n * n * n * (n * n + 2 * n - 1) / (pow(n * n + 1, 2) * (n * n - 1))
				+ n * n * (n * n + 1) * math::fastlog(n) / pow(n * n - 1, 2)
				- n * n * pow(n * n - 1, 2) * math::fastlog(n * (n + 1) / (n - 1)) / pow(n * n + 1, 3)
				);
			Float t12_diffuse = 1 - r12_diffuse;
			Float r21_diffuse = 1 - (1 - r12_diffuse) / (n * n);
			Float t21_diffuse = 1 - r21_diffuse;
			// transmission of the water layer
			Float Tw_diffuse;
			if (m_L > 0) {
				Tw_diffuse = (1 - alpha * m_L) * math::fastexp(-alpha * m_L) + pow(alpha * m_L,2) * -boost::math::expint(-alpha * m_L);
			}
			else {
				Tw_diffuse = 1.0;
			}
			Float Rw = t12_diffuse * t21_diffuse * dry_ref * Tw_diffuse * Tw_diffuse / (1 - r21_diffuse * dry_ref * Tw_diffuse * Tw_diffuse);
			Float Rm = pow(m_sigma * pow(Rw, (1 / 2.27)) + (1 - m_sigma) * pow(dry_ref, (1 / 2.27)), 2.27);
			reflectance[i] = Rm;
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
		oss << "ART[" << endl
			<< "]";
		return oss.str();
	}
	MTS_DECLARE_CLASS()
private:
	Float m_b;
	Float m_M;
	Float m_theta;
	Float m_L;
	Float m_sigma;
	Spectrum m_wavelengths;

	Spectrum m_soil_k;
	Spectrum m_water_n_w;
	Spectrum m_water_alpha_w;
};

MTS_IMPLEMENT_CLASS_S(HapkeMarmit2, false, BSDF)
MTS_EXPORT_PLUGIN(HapkeMarmit2, "HapkeMarmit2 BRDF")
MTS_NAMESPACE_END