
#include <mitsuba/render/sensor.h>
#include <mitsuba/render/medium.h>
#include <mitsuba/core/track.h>


MTS_NAMESPACE_BEGIN

#define SQRT_TWO 1.414213562

class HemisphericalFisheyeCamera : public Sensor {
public:
	HemisphericalFisheyeCamera(const Properties &props) : Sensor(props) {
		m_type |= EDeltaPosition | EDirectionSampleMapsToPixels;

		if (props.getTransform("toWorld", Transform()).hasScale())
			Log(EError, "Scale factors in the sensor-to-world "
			"transformation are not allowed!");
		m_angular_fov = props.getFloat("angular_fov", 180);
		m_angular_fov = m_angular_fov / 180.0*M_PI;

		//equisolid orthographic equidistant stereographic :https://wiki.panotools.org/Fisheye_Projection
		m_projectionType = props.getString("projection_type", "equisolid");
	}

	HemisphericalFisheyeCamera(Stream *stream, InstanceManager *manager)
		: Sensor(stream, manager) {
		configure();
	}

	Float getPointAngle(Point pixelSample) const{
		Float coord_x = pixelSample.x * m_invResolution.x;
		Float coord_y = pixelSample.y * m_invResolution.y;
		Float dist = math::safe_sqrt((coord_x - 0.5)*(coord_x - 0.5) + (coord_y - 0.5)*(coord_y - 0.5));
		Float point_angle = 0;

		if (m_projectionType == "equisolid") {
			point_angle = 2 * math::safe_asin(SQRT_TWO*dist);
		}
		else if (m_projectionType == "orthographic") {
			point_angle = math::safe_asin(dist / 0.5);
		}
		else if (m_projectionType == "equidistant") {
			point_angle = dist * M_PI;
		}
		else if (m_projectionType == "stereographic") {
			point_angle = 2 * atanf(dist / 0.5);
		}
		else {//default: equisolid
			point_angle = 2 * math::safe_asin(SQRT_TWO*dist);
		}
		return point_angle;
	}

	Spectrum sampleRay(Ray &ray, const Point2 &pixelSample,
		const Point2 &otherSample, Float timeSample) const {
		ray.time = sampleTime(timeSample);
		ray.mint = Epsilon;
		ray.maxt = std::numeric_limits<Float>::infinity();

		//calculate the distance between the sample point and the image center in space [0,1]
		//https://wiki.panotools.org/Fisheye_Projection
		Float coord_x = pixelSample.x * m_invResolution.x;
		Float coord_y = pixelSample.y * m_invResolution.y;
		Float dist = math::safe_sqrt((coord_x - 0.5)*(coord_x - 0.5) + (coord_y - 0.5)*(coord_y - 0.5));
		Float point_angle = 0;

		if (m_projectionType == "equisolid"){
			point_angle = 2 * math::safe_asin(SQRT_TWO*dist);
		}
		else if (m_projectionType == "orthographic"){
			point_angle = math::safe_asin(dist / 0.5);
		}
		else if (m_projectionType == "equidistant"){
			point_angle = dist*M_PI;
		}
		else if (m_projectionType == "stereographic"){
			point_angle = 2 * atanf(dist/0.5);
		}
		else{//default: equisolid
			point_angle = 2 * math::safe_asin(SQRT_TWO*dist);
		}
		
		const Transform &trafo = m_worldTransform->eval(ray.time);

		Float sinPhi, cosPhi, sinTheta, cosTheta;
		math::sincos(point_angle, &sinTheta, &cosTheta);
		Float Phi = std::atan2(0.5 - coord_y, coord_x - 0.5);
		math::sincos(Phi, &sinPhi, &cosPhi);

		Vector d(sinPhi*sinTheta, cosTheta, -cosPhi*sinTheta);

		ray.setOrigin(trafo(Point(0.0f)));
		ray.setDirection(trafo(d));

		if (point_angle >= m_angular_fov / 2.0){
			return Spectrum(0.0f);
		}
		return Spectrum(1.0f);
	}

	Spectrum samplePosition(PositionSamplingRecord &pRec,
		const Point2 &sample, const Point2 *extra) const {
		const Transform &trafo = m_worldTransform->eval(pRec.time);
		pRec.p = trafo(Point(0.0f));
		pRec.n = Normal(0.0f);
		pRec.pdf = 1.0f;
		pRec.measure = EDiscrete;
		return Spectrum(1.0f);
	}

	Spectrum evalPosition(const PositionSamplingRecord &pRec) const {
		return Spectrum((pRec.measure == EDiscrete) ? 1.0f : 0.0f);
	}

	Float pdfPosition(const PositionSamplingRecord &pRec) const {
		return (pRec.measure == EDiscrete) ? 1.0f : 0.0f;
	}

	Spectrum sampleDirection(DirectionSamplingRecord &dRec,
		PositionSamplingRecord &pRec,
		const Point2 &sample, const Point2 *extra) const {
		const Transform &trafo = m_worldTransform->eval(pRec.time);

		Point samplePos(sample.x, sample.y, 0.0f);

		if (extra) {
			/* The caller wants to condition on a specific pixel position */
			samplePos.x = (extra->x + sample.x) * m_invResolution.x;
			samplePos.y = (extra->y + sample.y) * m_invResolution.y;
		}

		pRec.uv = Point2(samplePos.x * m_resolution.x,
			samplePos.y * m_resolution.y);

		Float coord_x = samplePos.x * m_invResolution.x;
		Float coord_y = samplePos.y * m_invResolution.y;
		Float dist = math::safe_sqrt((coord_x - 0.5)*(coord_x - 0.5) + (coord_y - 0.5)*(coord_y - 0.5));
		// the radius of the plane is 0.5
		Float point_angle = 0;

		if (m_projectionType == "equisolid"){
			point_angle = 2 * math::safe_asin(SQRT_TWO*dist);
		}
		else if (m_projectionType == "orthographic"){
			point_angle = math::safe_asin(dist / 0.5);
		}
		else if (m_projectionType == "equidistant"){
			point_angle = dist*M_PI;
		}
		else if (m_projectionType == "stereographic"){
			point_angle = 2 * atanf(dist/0.5);
		}
		else{//default: equisolid
			point_angle = 2 * math::safe_asin(SQRT_TWO*dist);
		}

		Float sinPhi, cosPhi, sinTheta, cosTheta;
		math::sincos(point_angle, &sinTheta, &cosTheta);
		Float Phi = std::atan2(0.5 - coord_y, coord_x - 0.5);
		math::sincos(Phi, &sinPhi, &cosPhi);

		dRec.d = trafo(Vector(sinPhi*sinTheta, cosTheta, -cosPhi*sinTheta));
		dRec.measure = ESolidAngle;
		dRec.pdf = 1 / (2 * M_PI * 0.5 * M_PI * std::max(sinTheta, Epsilon));

		if (point_angle >= m_angular_fov / 2.0){
			return Spectrum(-1.0f);
		}
		return Spectrum(1.0f);
	}

	Float pdfDirection(const DirectionSamplingRecord &dRec,
		const PositionSamplingRecord &pRec) const {
		if (dRec.measure != ESolidAngle)
			return 0.0f;
		Vector d = m_worldTransform->eval(pRec.time).inverse()(dRec.d);
		Float sinTheta = math::safe_sqrt(1 - d.y*d.y);

		return 1 / (2 * M_PI* 0.5 * M_PI * std::max(sinTheta, Epsilon));
	}

	Spectrum evalDirection(const DirectionSamplingRecord &dRec,
		const PositionSamplingRecord &pRec) const {
		if (dRec.measure != ESolidAngle)
			return Spectrum(0.0f);
		Vector d = m_worldTransform->eval(pRec.time).inverse()(dRec.d);
		Float sinTheta = math::safe_sqrt(1 - d.y*d.y);

		return Spectrum(1 / (2 * M_PI *0.5* M_PI * std::max(sinTheta, Epsilon)));
	}

	bool getSamplePosition(const PositionSamplingRecord &pRec,
		const DirectionSamplingRecord &dRec, Point2 &samplePosition) const {
		Vector d = normalize(m_worldTransform->eval(pRec.time).inverse()(dRec.d));

		samplePosition = Point2((0.5 - d.x)*m_resolution.x, (0.5 - d.z)*m_resolution.y);

		/*samplePosition = Point2(
			math::modulo(std::atan2(d.x, -d.z) * INV_TWOPI, (Float)1) * m_resolution.x,
			math::safe_acos(d.y) * INV_PI * m_resolution.y
			);*/

		return true;
	}

	Spectrum sampleDirect(DirectSamplingRecord &dRec, const Point2 &sample) const {
		const Transform &trafo = m_worldTransform->eval(dRec.time);

		/* Transform the reference point into the local coordinate system */
		Point refP = trafo.inverse().transformAffine(dRec.ref);
		Vector d(refP);
		Float dist = d.length(),
			invDist = 1.0f / dist;
		d *= invDist;

		dRec.uv = Point2((0.5 - d.x)*m_resolution.x, (0.5 - d.z)*m_resolution.y);

		/*dRec.uv = Point2(
			math::modulo(std::atan2(d.x, -d.z) * INV_TWOPI, (Float)1) * m_resolution.x,
			math::safe_acos(d.y) * INV_PI * m_resolution.y
			);*/

		Float sinTheta = math::safe_sqrt(1 - d.y*d.y);

		dRec.p = trafo.transformAffine(Point(0.0f));
		dRec.d = (dRec.p - dRec.ref) * invDist;
		dRec.dist = dist;
		dRec.n = Vector(0.0f);
		dRec.pdf = 1;
		dRec.measure = EDiscrete;

		return Spectrum(
			(1 / (2 * M_PI *0.5* M_PI * std::max(sinTheta, Epsilon))) * invDist * invDist);
	}

	Float pdfDirect(const DirectSamplingRecord &dRec) const {
		return (dRec.measure == EDiscrete) ? 1.0f : 0.0f;
	}

	AABB getAABB() const {
		return m_worldTransform->getTranslationBounds();
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "HemisphericalFisheyeCamera[" << endl
			<< "  worldTransform = " << indent(m_worldTransform.toString()) << "," << endl
			<< "  sampler = " << indent(m_sampler->toString()) << "," << endl
			<< "  film = " << indent(m_film->toString()) << "," << endl
			<< "  medium = " << indent(m_medium.toString()) << "," << endl
			<< "  shutterOpen = " << m_shutterOpen << "," << endl
			<< "  shutterOpenTime = " << m_shutterOpenTime << endl
			<< "]";
		return oss.str();
	}

	MTS_DECLARE_CLASS()
private:
	Float m_angular_fov;
	std::string m_projectionType;
};

MTS_IMPLEMENT_CLASS_S(HemisphericalFisheyeCamera, false, Sensor)
MTS_EXPORT_PLUGIN(HemisphericalFisheyeCamera, "Hemispherical fisheye camera");
MTS_NAMESPACE_END
