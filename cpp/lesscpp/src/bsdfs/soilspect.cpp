

#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/texture.h>
#include <mitsuba/render/basicshader.h>
#include <mitsuba/core/warp.h>

MTS_NAMESPACE_BEGIN

class SoilSpect : public BSDF {
public:
	SoilSpect(const Properties &props)
		:BSDF(props) {
		m_albedo = new ConstantSpectrumTexture(props.getSpectrum("albedo", Spectrum(.5f)));
		m_c1 = new ConstantSpectrumTexture(props.getSpectrum("c1", Spectrum(.5f)));
		m_c2 = new ConstantSpectrumTexture(props.getSpectrum("c2", Spectrum(.5f)));
		m_c3 = new ConstantSpectrumTexture(props.getSpectrum("c3", Spectrum(.5f)));
		m_c4 = new ConstantSpectrumTexture(props.getSpectrum("c4", Spectrum(.5f)));
		m_h1 = new ConstantSpectrumTexture(props.getSpectrum("h1", Spectrum(.5f)));
		m_h2 = new ConstantSpectrumTexture(props.getSpectrum("h2", Spectrum(.5f)));
	}

	SoilSpect(Stream *stream, InstanceManager *manager)
		: BSDF(stream, manager) {
		m_albedo = static_cast<Texture *>(manager->getInstance(stream));
		m_c1 = static_cast<Texture *>(manager->getInstance(stream));
		m_c2 = static_cast<Texture *>(manager->getInstance(stream));
		m_c3 = static_cast<Texture *>(manager->getInstance(stream));
		m_c4 = static_cast<Texture *>(manager->getInstance(stream));
		m_h1 = static_cast<Texture *>(manager->getInstance(stream));
		m_h2 = static_cast<Texture *>(manager->getInstance(stream));
		configure();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		BSDF::serialize(stream, manager);
		manager->serialize(stream, m_albedo.get());
		manager->serialize(stream, m_c1.get());
		manager->serialize(stream, m_c2.get());
		manager->serialize(stream, m_c3.get());
		manager->serialize(stream, m_c4.get());
		manager->serialize(stream, m_h1.get());
		manager->serialize(stream, m_h2.get());
	}

	void configure() {
		m_components.clear();
		m_components.push_back(EGlossyReflection | EFrontSide
			| ((!m_albedo->isConstant() || 
				!m_c1->isConstant() ||
				!m_c2->isConstant() ||
				!m_c3->isConstant() ||
				!m_c4->isConstant() ||
				!m_h1->isConstant() ||
				!m_h2->isConstant())
				? ESpatiallyVarying : 0));

		m_usesRayDifferentials = m_albedo->usesRayDifferentials() || 
			m_c1->usesRayDifferentials() ||
			m_c2->usesRayDifferentials() ||
			m_c3->usesRayDifferentials() ||
			m_c4->usesRayDifferentials() ||
			m_h1->usesRayDifferentials() ||
			m_h2->usesRayDifferentials();

		BSDF::configure();
	}

	Spectrum H(Spectrum &albedo, double x) const {
		Spectrum hSpectrum(0.0);
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			hSpectrum[i] = (1 + 2 * x) / (1 + 2 *x* math::safe_sqrt(1 - albedo[i]));
		}
		return hSpectrum;
	}

	Spectrum B(Spectrum &h1, Spectrum &h2, const BSDFSamplingRecord &bRec) const {
		double cosPhisv = dot(bRec.wi, bRec.wo);
		double angle = math::safe_acos(cosPhisv);
		return h1 / (Spectrum(1.0) + (1 / h2) * tan(0.5*angle));
	}

	Spectrum P(Spectrum &c1, Spectrum &c2, Spectrum &c3, Spectrum &c4, const BSDFSamplingRecord &bRec) const{
		Vector wi = Vector(bRec.wi);
		Vector wo = Vector(bRec.wo);
		double cosPhisv = dot(wi, wo);
		double cosPhissv = dot(Vector(-wi.x, -wi.y, wi.z), wo);
		return Spectrum(1.0) + c1 * cosPhisv + c2 * (3 * cosPhisv*cosPhisv - 1)*0.5 +
			c3 * cosPhissv + c4 * (3 * cosPhissv*cosPhissv - 1)*0.5;
	}

	Spectrum computeDirectinalRelectance(const BSDFSamplingRecord &bRec) const{
		//parameter at each intersected position
		Spectrum albedo = m_albedo->eval(bRec.its);
		Spectrum c1 = m_c1->eval(bRec.its);
		Spectrum c2 = m_c2->eval(bRec.its);
		Spectrum c3 = m_c3->eval(bRec.its);
		Spectrum c4 = m_c4->eval(bRec.its);
		Spectrum h1 = m_h1->eval(bRec.its);
		Spectrum h2 = m_h2->eval(bRec.its);

		//tmp
		//Spectrum reflectance = Frame::cosTheta(bRec.wi) * albedo / 4.0 / (Frame::cosTheta(bRec.wi) + Frame::cosTheta(bRec.wo));
		Spectrum reflectance = albedo / 4.0 / (Frame::cosTheta(bRec.wi) + Frame::cosTheta(bRec.wo));
		reflectance *= (Spectrum(1.0) + B(h1, h2, bRec))*P(c1, c2, c3, c4, bRec) + H(albedo, Frame::cosTheta(bRec.wi))*H(albedo, Frame::cosTheta(bRec.wo)) - Spectrum(1.0);
		return reflectance;
	}

	Spectrum eval(const BSDFSamplingRecord &bRec, EMeasure measure) const {
		if (!(bRec.typeMask & EGlossyReflection) || measure != ESolidAngle
			|| Frame::cosTheta(bRec.wi) <= 0
			|| Frame::cosTheta(bRec.wo) <= 0)
			return Spectrum(0.0f);
		return computeDirectinalRelectance(bRec) * (INV_PI * Frame::cosTheta(bRec.wo));
	}

	Float pdf(const BSDFSamplingRecord &bRec, EMeasure measure) const {
		if (!(bRec.typeMask & EDiffuseReflection) || measure != ESolidAngle
			|| Frame::cosTheta(bRec.wi) <= 0
			|| Frame::cosTheta(bRec.wo) <= 0)
			return 0.0f;
		return warp::squareToCosineHemispherePdf(bRec.wo);
	}

	Spectrum sample(BSDFSamplingRecord &bRec, const Point2 &sample) const {
		//当碰撞到背面时，返回一个负值
		if (!(bRec.typeMask & EGlossyReflection) || Frame::cosTheta(bRec.wi) <= 0)
			return Spectrum(-1.0f);

		bRec.wo = warp::squareToCosineHemisphere(sample);
		bRec.eta = 1.0f;
		bRec.sampledComponent = 0;
		bRec.sampledType = EGlossyReflection;
		return computeDirectinalRelectance(bRec);
	}

	Spectrum sample(BSDFSamplingRecord &bRec, Float &pdf, const Point2 &sample) const {
		if (!(bRec.typeMask & EGlossyReflection) || Frame::cosTheta(bRec.wi) <= 0)
			return Spectrum(0.0f);
		bRec.wo = warp::squareToCosineHemisphere(sample);
		bRec.eta = 1.0f;
		bRec.sampledComponent = 0;
		bRec.sampledType = EGlossyReflection;
		pdf = warp::squareToCosineHemispherePdf(bRec.wo);
		return computeDirectinalRelectance(bRec);
	}


	void addChild(const std::string &name, ConfigurableObject *child) {
		if (child->getClass()->derivesFrom(MTS_CLASS(Texture))) {
			if (name == "albedo") m_albedo = static_cast<Texture *>(child);
			if (name == "c1") m_c1 = static_cast<Texture *>(child);
			if (name == "c2") m_c2 = static_cast<Texture *>(child);
			if (name == "c3") m_c3 = static_cast<Texture *>(child);
			if (name == "c4") m_c4 = static_cast<Texture *>(child);
			if (name == "h1") m_h1 = static_cast<Texture *>(child);
			if (name == "h2") m_h2 = static_cast<Texture *>(child);
		}
		else {
			BSDF::addChild(name, child);
		}
	}

	Float getRoughness(const Intersection &its, int component) const {
		return std::numeric_limits<Float>::infinity();
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "SoilSpect[" << endl
			<< "]";
		return oss.str();
	}
	MTS_DECLARE_CLASS()
private:
	ref<Texture> m_albedo;
	ref<Texture> m_c1;
	ref<Texture> m_c2;
	ref<Texture> m_c3;
	ref<Texture> m_c4;
	ref<Texture> m_h1;
	ref<Texture> m_h2;
};

MTS_IMPLEMENT_CLASS_S(SoilSpect, false, BSDF)
MTS_EXPORT_PLUGIN(SoilSpect, "SoilSpect BRDF")
MTS_NAMESPACE_END