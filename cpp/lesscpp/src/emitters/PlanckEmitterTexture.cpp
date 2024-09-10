//author Jianbo Qi


#include <mitsuba/render/emitter.h>
#include <mitsuba/render/shape.h>
#include <mitsuba/render/medium.h>
#include <mitsuba/render/bsdf.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/render/scene.h>
#include <mitsuba/render/texture.h>
#include <mitsuba/render/basicshader.h>

MTS_NAMESPACE_BEGIN

class PlanckAreaLight : public Emitter {
public:
	PlanckAreaLight(const Properties &props) : Emitter(props) {
		m_type |= EOnSurface | EPlanckEmitter;

		if (props.hasProperty("toWorld"))
			Log(EError, "Found a 'toWorld' transformation -- this is not "
				"allowed -- the area light inherits this transformation from "
				"its parent shape");
		m_temperature = new ConstantSpectrumTexture(props.getSpectrum("temperature", Spectrum(275.0f)));

		//m_temperature = props.getFloat("temperature", 300);
		m_deltaTemperature = props.getFloat("deltaTemperature", 5);
		m_sunDirection = normalize(props.getVector("direction"));
		m_waveLengths = props.getSpectrum("wavelengths");

		//use average temperature as initial 
		m_power = Spectrum(0.0f); /// Don't know the power yet
		m_lowerPower = Spectrum(0.0f);/// Don't know the power yet
		m_upperPower = Spectrum(0.0f);
	}

	PlanckAreaLight(Stream *stream, InstanceManager *manager)
		: Emitter(stream, manager) {
		m_temperature = static_cast<Texture*>(manager->getInstance(stream));
		m_deltaTemperature = stream->readDouble();
		m_waveLengths = Spectrum(stream);
		m_sunDirection = Vector(stream);
		configure();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Emitter::serialize(stream, manager);
		manager->serialize(stream, m_temperature.get());
		stream->writeDouble(m_deltaTemperature);
		m_waveLengths.serialize(stream);
		m_sunDirection.serialize(stream);
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
		return m_power; //This is not used in path tracing
	}

	Spectrum evalPosition(const PositionSamplingRecord &pRec) const {
		//return m_radiance * M_PI;
		return Spectrum(0.0); //This is not used in path tracing
	}

	Spectrum eval(const Intersection &its, const Vector &d) const {
		Spectrum radiance;
		Float its_temper = m_temperature->eval(its)[0];  //Temperature is the same for all bands
		if (its.shaded) {
			radiance = calculateSpectrumAccordT(its_temper-m_deltaTemperature * 0.5);
		}
		else{
			radiance = calculateSpectrumAccordT(its_temper + m_deltaTemperature * 0.5);
		}
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
		m_shape->sampleDirect(dRec, sample, m_worldTransform.get());

		//offset the sampled position to the position of instance
		/*if (m_worldTransform != nullptr) {
			const Transform& trafo = m_worldTransform->eval(0);
			dRec.p = trafo(dRec.p);
		}*/
		

		/* Check that the emitter and reference position are oriented correctly
		   with respect to each other. Note that the >= 0 check
		   for 'refN' is intentional -- those sampling requests that specify
		   a reference point within a medium or on a transmissive surface
		   will set dRec.refN = 0, hence they should always be accepted. */
		//if (dot(dRec.d, dRec.refN) >= 0 && dRec.pdf != 0) {
		dRec.pdf = dRec.pdf*0.5;
		if (dRec.pdf != 0) {
			//return radiance / dRec.pdf;
			return Spectrum(1.0); // return a non-zero value is OK for path tracing
			
		} else {
			dRec.pdf = 0.0f;
			return Spectrum(0.0f);
		}

	}

	Float pdfDirect(const DirectSamplingRecord &dRec) const {
		/* Check that the emitter and receiver are oriented correctly
		   with respect to each other. */
		if (dot(dRec.d, dRec.refN) >= 0 ) {
			return 0.5*m_shape->pdfDirect(dRec);
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
		} else {
			Log(EError, "An area light must be child of a shape instance");
		}
	}

	AABB getAABB() const {
		return m_shape->getAABB();
	}

	Spectrum getSpectrumAccordingToTemperature(DirectSamplingRecord &dRec, Intersection& its, bool shaded) const {

		if (dRec.pdf == 0) return Spectrum(0.0);

		Spectrum radiance;
		Float its_temper = m_temperature->eval(its)[0];  //Temperature is the same for all bands
		if (its.shaded) {
			radiance = calculateSpectrumAccordT(its_temper - m_deltaTemperature * 0.5);
		}
		else {
			radiance = calculateSpectrumAccordT(its_temper + m_deltaTemperature * 0.5);
		}
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

	void addChild(const std::string& name, ConfigurableObject* child) {
		if (child->getClass()->derivesFrom(MTS_CLASS(Texture))
			&& (name == "temperature")) {
			m_temperature = static_cast<Texture*>(child);
		}
		else {
			Emitter::addChild(name, child);
		}
	}


	std::string toString() const {
		std::ostringstream oss;
		oss << "PlanckAreaLightTexture[" << endl
			<< "  temperature = " << indent(m_temperature->toString()) << "," << endl
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
	Spectrum m_power;

	Spectrum m_waveLengths;
	Vector m_sunDirection;

	Spectrum m_lowerThermalSpectrum;
	Spectrum m_upperThermalSpecturm;
	Spectrum m_lowerPower;
	Spectrum m_upperPower;

private:
	ref<Texture> m_temperature;
	double m_deltaTemperature;
};


MTS_IMPLEMENT_CLASS_S(PlanckAreaLight, false, Emitter)
MTS_EXPORT_PLUGIN(PlanckAreaLight, "Planck Area light");
MTS_NAMESPACE_END
