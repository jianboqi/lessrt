

#include <mitsuba/render/scene.h>
#include <mitsuba/core/warp.h>
#include <string>

MTS_NAMESPACE_BEGIN

class HorizontalPlaneEmitter : public Emitter {
public:
	HorizontalPlaneEmitter(const Properties &props) : Emitter(props) {
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
		}
		else {
			if (props.getTransform("toWorld", Transform()).hasScale())
				Log(EError, "Scale factors in the emitter-to-world "
					"transformation are not allowed!");
		}

		//virtual bounds to narrow the illumination area
		m_hasVirtualPlane = props.getBoolean("virtualBounds", false);
	}

	HorizontalPlaneEmitter(Stream *stream, InstanceManager *manager)
		: Emitter(stream, manager) {
		m_normalIrradiance = Spectrum(stream);
		m_hasVirtualPlane = stream->readBool();
		m_sceneHeight = stream->readFloat();
		m_topPlaneAABB = AABB2(stream);
		configure();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Emitter::serialize(stream, manager);
		m_normalIrradiance.serialize(stream);
		stream->writeBool(m_hasVirtualPlane);
		stream->writeFloat(m_sceneHeight);
		m_topPlaneAABB.serialize(stream);
	}

	ref<Shape> createShape(const Scene *scene) {
		Point2 minP, maxP;
		/* get the extends of the top plane */
		if (m_hasVirtualPlane) {
			Vector2 sceneSize = Vector2(scene->getIntegrator()->getProperties().getFloat("subSceneXSize", 100),
				scene->getIntegrator()->getProperties().getFloat("subSceneZSize", 100));

			Vector2 virtualPlaneCenter = Vector2(scene->getIntegrator()->getProperties().getFloat("vx", 0),
				scene->getIntegrator()->getProperties().getFloat("vz", 0));
			Vector2 virtualPlaneSize = Vector2(scene->getIntegrator()->getProperties().getFloat("sizex", sceneSize.x),
				scene->getIntegrator()->getProperties().getFloat("sizez", sceneSize.y));

			AABB scene_bound = scene->getKDTree()->getAABB();

			//virtual box
			double x_min = virtualPlaneCenter.x - 0.5*virtualPlaneSize.x;
			double x_max = virtualPlaneCenter.x + 0.5*virtualPlaneSize.x;
			double z_min = virtualPlaneCenter.y - 0.5*virtualPlaneSize.y;
			double z_max = virtualPlaneCenter.y + 0.5*virtualPlaneSize.y;
			minP = Point2(x_min, z_min);
			maxP = Point2(x_max, z_max);
			m_sceneHeight = scene_bound.max.y+0.1;
			m_topPlaneAABB = AABB2(minP, maxP);
		}
		else {
			AABB scene_bound = scene->getKDTree()->getAABB();
			minP = Point2(scene_bound.min.x, scene_bound.min.z);
			maxP = Point2(scene_bound.max.x, scene_bound.max.z);
			m_sceneHeight = scene_bound.max.y+0.1;
			m_topPlaneAABB = AABB2(minP, maxP);
		}
		configure();
		return NULL;
	}

	void configure() {
		Emitter::configure();
		Float surfaceArea = m_topPlaneAABB.getExtents().x*m_topPlaneAABB.getExtents().y;
		m_invSurfaceArea = 1.0f / surfaceArea;
		const Transform &trafo = m_worldTransform->eval(0.0);
		Vector d = trafo(Vector(0, 0, 1));
		//这里很奇怪，如果直接写m_power=m_normalIrradiance * surfaceArea,在并行计算时，
		//如果核数量比较多时，会出错。
		Spectrum tmp = m_normalIrradiance * surfaceArea*(-d.y);
		m_power = tmp;
		//m_power = Spectrum(0.0);
	}

	Spectrum samplePosition(PositionSamplingRecord &pRec, const Point2 &sample, const Point2 *extra) const {
		const Transform &trafo = m_worldTransform->eval(pRec.time);
		Vector d = trafo(Vector(0, 0, 1));

		double x = m_topPlaneAABB.min.x + m_topPlaneAABB.getExtents().x*sample.x;
		double z = m_topPlaneAABB.min.y + m_topPlaneAABB.getExtents().y*sample.y;
		Point generatedPos = Point(x, m_sceneHeight, z);

		//pRec.p = m_bsphere.center - d*m_bsphere.radius + perpOffset;
		pRec.p = generatedPos;
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
		double x = m_topPlaneAABB.min.x + m_topPlaneAABB.getExtents().x*spatialSample.x;
		double z = m_topPlaneAABB.min.y + m_topPlaneAABB.getExtents().y*spatialSample.y;
		Point generatedPos = Point(x, m_sceneHeight, z);

		//ray.setOrigin(m_bsphere.center - d*m_bsphere.radius + perpOffset);
		ray.setOrigin(generatedPos);
		ray.setDirection(d);
		ray.setTime(time);
		return m_power;
	}

	Spectrum sampleDirect(DirectSamplingRecord &dRec, const Point2 &sample) const {
		const Transform &trafo = m_worldTransform->eval(dRec.time);
		Vector d = trafo(Vector(0, 0, 1));
		//Point diskCenter = m_bsphere.center - d*m_bsphere.radius;
		Float relativeHeight = m_sceneHeight - dRec.ref.y;
		Float distance = relativeHeight / (-d.y);
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

	//Spectrum evalEnvironment(const RayDifferential &ray) const {
	//	const Transform &trafo = m_worldTransform->eval(0);
	//	Vector d = -trafo(Vector(0, 0, 1));
	//	double theta = degToRad(SUN_APP_RADIUS * 0.5f);
	//	if (dot(d, ray.d) >= std::cos(theta)) {
	//		double solidAngle = 2 * M_PI * (1 - std::cos(theta));
	//		return m_normalIrradiance / solidAngle;
	//	}
	//	return Spectrum(0.0);
	//}

	Float pdfDirect(const DirectSamplingRecord &dRec) const {
		return dRec.measure == EDiscrete ? 1.0f : 0.0f;
	}

	AABB getAABB() const {
		return AABB();
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "HorizontalPlaneEmitter[" << endl
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
	//BSphere m_bsphere;
	Float m_invSurfaceArea;

	//for virtual plane
	bool m_hasVirtualPlane;
	double m_sceneHeight;
	AABB2 m_topPlaneAABB;
};

MTS_IMPLEMENT_CLASS_S(HorizontalPlaneEmitter, false, Emitter)
MTS_EXPORT_PLUGIN(HorizontalPlaneEmitter, "HorizontalPlane emitter");
MTS_NAMESPACE_END
