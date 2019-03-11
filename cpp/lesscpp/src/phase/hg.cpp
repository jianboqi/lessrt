
#include <mitsuba/render/phase.h>
#include <mitsuba/render/sampler.h>
#include <mitsuba/core/properties.h>
#include <mitsuba/core/frame.h>

// hg phase function multispectrual version

MTS_NAMESPACE_BEGIN
class HGPhaseFunction : public PhaseFunction {
public:
	HGPhaseFunction(const Properties &props)
		: PhaseFunction(props) {
		/* Asymmetry parameter: must lie in [-1, 1] where >0 is
		forward scattering and <0 is backward scattering. */
		m_param_g = props.getSpectrum("g", Spectrum(0.0));
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			if (m_param_g[i] >= 1 || m_param_g[i] <= -1)
				Log(EError, "The asymmetry parameter must lie in the interval (-1, 1)!");
		}
	}

	HGPhaseFunction(Stream *stream, InstanceManager *manager)
		: PhaseFunction(stream, manager) {
		m_param_g = Spectrum(stream);
		configure();
	}

	virtual ~HGPhaseFunction() { }

	void serialize(Stream *stream, InstanceManager *manager) const {
		PhaseFunction::serialize(stream, manager);
		m_param_g.serialize(stream);
	}

	void configure() {
		PhaseFunction::configure();
		m_type = EAngleDependence;
	}

	inline Float sample(PhaseFunctionSamplingRecord &pRec,
		Sampler *sampler) const {
		Point2 sample(sampler->next2D());

		Float g = m_param_g[m_sampleSpecIndex];

		Float cosTheta;
		if (std::abs(g) < Epsilon) {
			cosTheta = 1 - 2 * sample.x;
		}
		else {
			Float sqrTerm = (1 - g * g) / (1 - g + 2 * g * sample.x);
			cosTheta = (1 + g * g - sqrTerm * sqrTerm) / (2 * g);
		}

		Float sinTheta = math::safe_sqrt(1.0f - cosTheta * cosTheta),
			sinPhi, cosPhi;

		math::sincos(2 * M_PI*sample.y, &sinPhi, &cosPhi);

		pRec.wo = Frame(-pRec.wi).toWorld(Vector(
			sinTheta * cosPhi,
			sinTheta * sinPhi,
			cosTheta
		));

		return 1.0f;
	}

	Float sample(PhaseFunctionSamplingRecord &pRec,
		Float &pdf, Sampler *sampler) const {
		HGPhaseFunction::sample(pRec, sampler);
		pdf = HGPhaseFunction::eval(pRec)[m_sampleSpecIndex];
		return 1.0f;
	}

	Spectrum eval(const PhaseFunctionSamplingRecord &pRec) const {
		Spectrum spec;
		for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
			Float g = m_param_g[i];
			Float temp = 1.0f + g * g + 2.0f * g * dot(pRec.wi, pRec.wo);
			Float val = INV_FOURPI * (1 - g * g) / (temp * std::sqrt(temp));
			spec[i] = val;
		}
		return spec;
	}

	Float getMeanCosine() const {
		return m_param_g[m_sampleSpecIndex];
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "HGPhaseFunction[g=" << m_param_g.toString() << "]";
		return oss.str();
	}

	MTS_DECLARE_CLASS()
private:
	Spectrum m_param_g;
};

MTS_IMPLEMENT_CLASS_S(HGPhaseFunction, false, PhaseFunction)
MTS_EXPORT_PLUGIN(HGPhaseFunction, "Henyey-Greenstein phase function");
MTS_NAMESPACE_END
