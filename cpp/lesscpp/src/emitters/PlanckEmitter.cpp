//author Jianbo Qi


#include <mitsuba/render/emitter.h>
#include <mitsuba/render/shape.h>
#include <mitsuba/render/medium.h>
#include <mitsuba/render/bsdf.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/render/scene.h>

MTS_NAMESPACE_BEGIN

class PlanckAreaLight : public Emitter {
public:
	PlanckAreaLight(const Properties &props) : Emitter(props) {
		m_type |= EOnSurface | EPlanckEmitter;

		if (props.hasProperty("toWorld"))
			Log(EError, "Found a 'toWorld' transformation -- this is not "
				"allowed -- the area light inherits this transformation from "
				"its parent shape");

		m_temperature = props.getFloat("temperature", 300);
		m_deltaTemperature = props.getFloat("deltaTemperature", 5);

		m_sunDirection = normalize(props.getVector("direction"));

		m_waveLengths = props.getSpectrum("wavelengths");

		//use average temperature as initial 
		m_radiance = calculateSpectrumAccordT(m_temperature);
		m_power = Spectrum(0.0f); /// Don't know the power yet

		m_lowerThermalSpectrum = calculateSpectrumAccordT(m_temperature - m_deltaTemperature * 0.5);
		m_upperThermalSpecturm = calculateSpectrumAccordT(m_temperature + m_deltaTemperature * 0.5);
		m_lowerPower = Spectrum(0.0f);/// Don't know the power yet
		m_upperPower = Spectrum(0.0f);
	}

	PlanckAreaLight(Stream *stream, InstanceManager *manager)
		: Emitter(stream, manager) {
		m_radiance = Spectrum(stream);
		m_power = Spectrum(stream);
		m_lowerPower = Spectrum(stream);
		m_upperPower = Spectrum(stream);
		m_temperature = stream->readDouble();
		m_deltaTemperature = stream->readDouble();
		m_waveLengths = Spectrum(stream);
		m_sunDirection = Vector(stream);
		m_lowerThermalSpectrum = Spectrum(stream);
		m_upperThermalSpecturm = Spectrum(stream);
		configure();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Emitter::serialize(stream, manager);
		m_radiance.serialize(stream);
		m_power.serialize(stream);
		m_lowerPower.serialize(stream);
		m_upperPower.serialize(stream);
		stream->writeDouble(m_temperature);
		stream->writeDouble(m_deltaTemperature);
		m_waveLengths.serialize(stream);
		m_sunDirection.serialize(stream);
		m_lowerThermalSpectrum.serialize(stream);
		m_upperThermalSpecturm.serialize(stream);
	}

	//calculate emitted *radiance* spectrum according to temperature
	Spectrum calculateSpectrumAccordT(double T) const{
		/* Convert inputs to meters and kelvins */
		const double c = 299792458;      /* Speed of light */
		const double k = 1.3806488e-23;  /* Boltzmann constant */
		const double h = 6.62606957e-34; /* Planck constant */

		Spectrum re(0.0);
		for (int spec = 0; spec < SPECTRUM_SAMPLES; spec++) {
			const double lambda = m_waveLengths[spec] * 1e-9;  /* Wavelength in meters */
											 /* Watts per unit surface area (m^-2) per unit wavelength (nm^-1) per
											 steradian (sr^-1) */
			re[spec] = (2 * h*c*c) * std::pow(lambda, -5.0)
				/ ((math::fastexp((h / k)*c / (lambda*T)) - 1.0) * 1e9);
		}
		return re;
	}

	Spectrum samplePosition(PositionSamplingRecord &pRec,
			const Point2 &sample, const Point2 *extra) const {
		m_shape->samplePosition(pRec, sample);
		return m_power;
	}

	Spectrum evalPosition(const PositionSamplingRecord &pRec) const {
		return m_radiance * M_PI;
	}

	Spectrum eval(const Intersection &its, const Vector &d) const {
		Spectrum radiance;
		if (its.shaded)
			radiance = m_lowerThermalSpectrum;
		else
			radiance = m_upperThermalSpecturm;

		const BSDF *bsdf = its.getBSDF();
		if (dot(its.shFrame.n, d) < 0) {//intersected back
			Intersection its_tmp;
			its_tmp.p = its.p;
			BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, -1), Vector(0, 0, -1));
			bRecref.typeMask = bsdf->EDiffuseReflection;
			Spectrum ref = bsdf->eval(bRecref)*M_PI_DBL;
			return (Spectrum(1.0) - ref)*radiance;
		}

		if (dot(its.shFrame.n, d) > 0) {//intersected front
			Intersection its_tmp;
			its_tmp.p = its.p;
			BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, 1), Vector(0, 0, 1));
			bRecref.typeMask = bsdf->EDiffuseReflection;
			Spectrum ref = bsdf->eval(bRecref)*M_PI_DBL;
			return (Spectrum(1.0) - ref)*radiance;
		}
		
		return Spectrum(0.0);
	}

	Float pdfPosition(const PositionSamplingRecord &pRec) const {
		return m_shape->pdfPosition(pRec);
	}

	Spectrum sampleDirection(DirectionSamplingRecord &dRec,
			PositionSamplingRecord &pRec,
			const Point2 &sample, const Point2 *extra) const {
		Vector local = warp::squareToCosineHemisphere(sample);
		dRec.d = Frame(pRec.n).toWorld(local);
		dRec.pdf = warp::squareToCosineHemispherePdf(local);
		dRec.measure = ESolidAngle;
		return Spectrum(1.0f);
	}

	Spectrum evalDirection(const DirectionSamplingRecord &dRec,
			const PositionSamplingRecord &pRec) const {
		Float dp = dot(dRec.d, pRec.n);

		if (dRec.measure != ESolidAngle)
			dp = 0.0f;

		return Spectrum(INV_PI * dp);
	}

	Float pdfDirection(const DirectionSamplingRecord &dRec,
			const PositionSamplingRecord &pRec) const {
		Float dp = dot(dRec.d, pRec.n);

		if (dRec.measure != ESolidAngle || dp < 0)
			dp = 0.0f;

		return INV_PI * dp;
	}

	Spectrum sampleRay(Ray &ray,
			const Point2 &spatialSample,
			const Point2 &directionalSample,
			Float time) const {
		NotImplementedError("PlanckAreaLight");

		PositionSamplingRecord pRec(time);
		m_shape->samplePosition(pRec, spatialSample);
		//object can emit energy at both sides according to emissivity
		const BSDF *bsdf = m_shape->getBSDF();
		//emesivity of front side
		Intersection its_tmp;
		its_tmp.p = pRec.p;
		BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, 1), Vector(0, 0, 1));
		bRecref.typeMask = bsdf->EDiffuseReflection;
		Spectrum em_front = Spectrum(1.0) - bsdf->eval(bRecref)*M_PI_DBL;
		//emissivity of back side
		BSDFSamplingRecord bRecback(its_tmp, Vector(0, 0, -1), Vector(0, 0, -1));
		bRecback.typeMask = bsdf->EDiffuseReflection;
		Spectrum em_back = Spectrum(1.0) - bsdf->eval(bRecback)*M_PI_DBL;

		//emit rays in front and back side according to the weights of emissivity
		double efrontweight = em_front.average();
		double ebackweight = em_back.average();
		//For ground, manually set to backside to zero
		if (m_shape->getName() == "terrain") {
			ebackweight = 0;
		}
		double frontWeight = efrontweight / (efrontweight + ebackweight);
		Vector local = warp::squareToCosineHemisphere(directionalSample);
		//ray.extra = 1;
		if (spatialSample.x > frontWeight) {//backside
			local = -local;
		//	ray.extra = 0;
		}
		//Determine the radiance according to temperature
		ray.setTime(time);
		ray.setOrigin(pRec.p);
		ray.setDirection(Frame(pRec.n).toWorld(local));
		return m_power; //return the average temperature temperally
	}

	Spectrum sampleDirect(DirectSamplingRecord &dRec,
			const Point2 &sample) const {
		m_shape->sampleDirect(dRec, sample);

		//must determine whether the sampled position is shaded or not
		//which will determine the emitted radiance


		/* Check that the emitter and reference position are oriented correctly
		   with respect to each other. Note that the >= 0 check
		   for 'refN' is intentional -- those sampling requests that specify
		   a reference point within a medium or on a transmissive surface
		   will set dRec.refN = 0, hence they should always be accepted. */
		if (dot(dRec.d, dRec.refN) >= 0 && dRec.pdf != 0) {
			return m_radiance / dRec.pdf;
		} else {
			dRec.pdf = 0.0f;
			return Spectrum(0.0f);
		}
	}

	Float pdfDirect(const DirectSamplingRecord &dRec) const {
		/* Check that the emitter and receiver are oriented correctly
		   with respect to each other. */
		if (dot(dRec.d, dRec.refN) >= 0 ) {
			return m_shape->pdfDirect(dRec);
		} else {
			return 0.0f;
		}
	}

	void setParent(ConfigurableObject *parent) {
		Emitter::setParent(parent);

		if (parent->getClass()->derivesFrom(MTS_CLASS(Shape))) {
			Shape *shape = static_cast<Shape *>(parent);
			if (m_shape == shape || shape->isCompound())
				return;

			if (m_shape != NULL)
				Log(EError, "An area light cannot be parent of multiple shapes");

			m_shape = shape;
			m_shape->configure();
			m_power = m_radiance * M_PI * m_shape->getSurfaceArea();
			m_lowerPower = m_lowerThermalSpectrum * M_PI * m_shape->getSurfaceArea();
			m_upperPower = m_upperThermalSpecturm * M_PI * m_shape->getSurfaceArea();
		} else {
			Log(EError, "An area light must be child of a shape instance");
		}
	}

	AABB getAABB() const {
		return m_shape->getAABB();
	}

	Spectrum getSpectrumAccordingToTemperature(DirectSamplingRecord &dRec, bool shaded) const {

		if (dRec.pdf == 0) return Spectrum(0.0);

		Spectrum radiance;
		if (shaded)
			radiance = m_lowerThermalSpectrum;
		else
			radiance = m_upperThermalSpecturm;

		//query absorbtion coefficient by quering reflectance
		const BSDF *bsdf = m_shape->getBSDF();
		if (dot(dRec.d, dRec.n) < 0) {//reference point is at front side of the emitter
			//querying front reflectance
			Intersection its_tmp;
			its_tmp.p = dRec.p;
			BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, 1), Vector(0, 0, 1));
			bRecref.typeMask = bsdf->EDiffuseReflection;
			Spectrum ref = bsdf->eval(bRecref)*M_PI_DBL;
			return (Spectrum(1.0) - ref)*radiance/ dRec.pdf;
		}
		if (dot(dRec.d, dRec.n) > 0) {//reference point is at back side of the emitter
			Intersection its_tmp;
			its_tmp.p = dRec.p;
			BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, -1), Vector(0, 0, -1));
			bRecref.typeMask = bsdf->EDiffuseReflection;
			Spectrum ref = bsdf->eval(bRecref)*M_PI_DBL;
			return (Spectrum(1.0) - ref)*radiance/ dRec.pdf;
		}
		return Spectrum(0.0f);
	}

	//Spectrum getPowerAccordingToTemperature(Point p, int FrontorBack, bool shaded) const {
	//	const BSDF *bsdf = m_shape->getBSDF();
	//	if (FrontorBack == 1) { //Font
	//		//querying front reflectance
	//		Intersection its_tmp;
	//		its_tmp.p = p;
	//		BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, 1), Vector(0, 0, 1));
	//		bRecref.typeMask = bsdf->EDiffuseReflection;
	//		Spectrum reffront = bsdf->eval(bRecref)*M_PI_DBL;
	//		if (shaded) {
	//			return m_lowerPower * (Spectrum(1.0) - reffront);
	//		}
	//		else {
	//			return m_upperPower * (Spectrum(1.0) - reffront);
	//		}
	//	}
	//	else {//Back
	//		Intersection its_tmp;
	//		its_tmp.p = p;
	//		BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, -1), Vector(0, 0, -1));
	//		bRecref.typeMask = bsdf->EDiffuseReflection;
	//		Spectrum refback = bsdf->eval(bRecref)*M_PI_DBL;
	//		if (shaded) {
	//			return m_lowerPower * (Spectrum(1.0) - refback);
	//		}
	//		else {
	//			return m_upperPower * (Spectrum(1.0) - refback);
	//		}
	//	}
	//	return Spectrum(0.0f);
	//}

	std::string toString() const {
		std::ostringstream oss;
		oss << "PlanckAreaLight[" << endl
			<< "  temperature = " <<m_temperature << "," << endl
			<< "  deltaTemperature = " << m_deltaTemperature << "," << endl
			<< "  surfaceArea = ";
		if (m_shape)
			oss << m_shape->getSurfaceArea();
		else
			oss << "<no shape attached!>";
		oss << "," << endl
		    << "  medium = " << indent(m_medium.toString()) << endl
			<< "]";
		return oss.str();
	}

	MTS_DECLARE_CLASS()
protected:
	Spectrum m_radiance, m_power;
	double m_temperature;
	double m_deltaTemperature;

	Spectrum m_waveLengths;
	Vector m_sunDirection;

	Spectrum m_lowerThermalSpectrum;
	Spectrum m_upperThermalSpecturm;
	Spectrum m_lowerPower;
	Spectrum m_upperPower;
};


MTS_IMPLEMENT_CLASS_S(PlanckAreaLight, false, Emitter)
MTS_EXPORT_PLUGIN(PlanckAreaLight, "Planck Area light");
MTS_NAMESPACE_END
