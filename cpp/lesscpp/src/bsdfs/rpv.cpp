

#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/texture.h>
#include <mitsuba/render/basicshader.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/core/math.h>

MTS_NAMESPACE_BEGIN

class RPV : public BSDF {
public:
	RPV(const Properties& props)
		:BSDF(props) {
		m_rho0 = new ConstantSpectrumTexture(props.getSpectrum("rho0", Spectrum(.5f)));
		m_k = new ConstantSpectrumTexture(props.getSpectrum("k", Spectrum(.5f)));
		m_THETA = new ConstantSpectrumTexture(props.getSpectrum("THETA", Spectrum(.5f)));
		m_rhoc = new ConstantSpectrumTexture(props.getSpectrum("rhoc", Spectrum(.5f)));
	}

	RPV(Stream* stream, InstanceManager* manager)
		: BSDF(stream, manager) {
		m_rho0 = static_cast<Texture*>(manager->getInstance(stream));
		m_k = static_cast<Texture*>(manager->getInstance(stream));
		m_THETA = static_cast<Texture*>(manager->getInstance(stream));
		m_rhoc = static_cast<Texture*>(manager->getInstance(stream));
		configure();
	}

	void serialize(Stream* stream, InstanceManager* manager) const {
		BSDF::serialize(stream, manager);
		manager->serialize(stream, m_rho0.get());
		manager->serialize(stream, m_k.get());
		manager->serialize(stream, m_THETA.get());
		manager->serialize(stream, m_rhoc.get());
	}

	void configure() {
		m_components.clear();
		m_components.push_back(EGlossyReflection | EFrontSide
			| ((!m_rho0->isConstant() ||
				!m_k->isConstant() ||
				!m_THETA->isConstant() ||
				!m_rhoc->isConstant())
				? ESpatiallyVarying : 0));

		m_usesRayDifferentials = m_rho0->usesRayDifferentials() ||
			m_k->usesRayDifferentials() ||
			m_THETA->usesRayDifferentials() ||
			m_rhoc->usesRayDifferentials();

		BSDF::configure();
	}


	Spectrum MFH(Spectrum& rho0, Spectrum& k, Spectrum& THETA, Spectrum& rhoc, const BSDFSamplingRecord& bRec) const {
		Vector wi = Vector(bRec.wi);
		Vector wo = Vector(bRec.wo);
		Float cosThetai = Frame::cosTheta(bRec.wi);
		Float cosThetar = Frame::cosTheta(bRec.wo);
		Float sinThetai = Frame::sinTheta(bRec.wi);
		Float sinThetar = Frame::sinTheta(bRec.wo);
		Vector wi_h = normalize(Vector(bRec.wi.x, bRec.wi.y, 0));
		Vector wo_h = normalize(Vector(bRec.wo.x, bRec.wo.y, 0));
		Float cosdPhi = dot(wi_h, wo_h);
		if (sinThetai == 0 && sinThetar == 0) cosdPhi = 1;
		Float cosg = cosThetai * cosThetar + sinThetai * sinThetar * cosdPhi;

		//M(k)
		Float ui_plus_ur = cosThetai + cosThetar;
		Float uiur = cosThetai * cosThetar;
		Spectrum M(0.0);
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			M[i] = pow(uiur, k[i] - 1) / pow(ui_plus_ur, 1 - k[i]);
		}
		
		//FHG
		Spectrum FHG(0.0);
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			FHG[i] = (1 - THETA[i] * THETA[i]) / pow((1 + THETA[i] * THETA[i] + 2 * THETA[i] * cosg), 1.5);
		}

		//H
		Float tanThetai2 = Frame::tanTheta2(bRec.wi);
		Float tanThetar2 = Frame::tanTheta2(bRec.wo);
		Float tanThetai = Frame::tanTheta(bRec.wi);
		Float tanThetar = Frame::tanTheta(bRec.wo);
		Spectrum H(0.0);
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			Float G = math::safe_sqrt(tanThetai2 + tanThetar2 - 2 * tanThetai * tanThetar * cosdPhi);
			H[i] = 1 + (1 - rhoc[i]) / (1 + G);
		}
		Spectrum out(0.0);
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			out[i] = rho0[i] * M[i] * FHG[i] * H[i];
		}
		return out;
	}

	Spectrum computeDirectinalRelectance(const BSDFSamplingRecord& bRec) const {
		//parameter at each intersected position
		Spectrum rho0 = m_rho0->eval(bRec.its);
		Spectrum k = m_k->eval(bRec.its);
		Spectrum THETA = m_THETA->eval(bRec.its);
		Spectrum rhoc = m_rhoc->eval(bRec.its);

		return MFH(rho0, k, THETA, rhoc, bRec);
	}

	Spectrum eval(const BSDFSamplingRecord& bRec, EMeasure measure) const {
		if (!(bRec.typeMask & EGlossyReflection) || measure != ESolidAngle
			|| Frame::cosTheta(bRec.wi) <= 0
			|| Frame::cosTheta(bRec.wo) <= 0)
			return Spectrum(0.0f);
		return computeDirectinalRelectance(bRec) * (INV_PI * Frame::cosTheta(bRec.wo));
	}
	Spectrum evalWithEF(const BSDFSamplingRecord& bRec,
		FluorMatrixs ms,FluorMatrix& m, EMeasure measure) const {
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
			if (name == "rho0") m_rho0 = static_cast<Texture*>(child);
			if (name == "k") m_k = static_cast<Texture*>(child);
			if (name == "THETA") m_THETA = static_cast<Texture*>(child);
			if (name == "rhoc") m_rhoc = static_cast<Texture*>(child);
		}
		else {
			BSDF::addChild(name, child);
		}
	}

	Float getRoughness(const Intersection& its, int component) const {
		return std::numeric_limits<Float>::infinity();
	}

	Spectrum getSingleScatteringAlbedo(const Intersection& its)  const {
		return m_rho0->eval(its);
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "RPV[" << endl
			<< "]";
		return oss.str();
	}
	MTS_DECLARE_CLASS()
private:
	ref<Texture> m_rho0;
	ref<Texture> m_k;
	ref<Texture> m_THETA;
	ref<Texture> m_rhoc;
};

MTS_IMPLEMENT_CLASS_S(RPV, false, BSDF)
MTS_EXPORT_PLUGIN(RPV, "RPV BRDF")
MTS_NAMESPACE_END