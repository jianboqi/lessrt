#include <mitsuba/render/photonproc.h>
#include <mitsuba/render/range.h>
#include <mitsuba/render/renderjob.h>
#include <mitsuba/core/bitmap.h>
#include <boost/filesystem.hpp>
#include "trac_utility.h"
#include <iomanip>

MTS_NAMESPACE_BEGIN

class TracInstrument : public Integrator {
public:
	TracInstrument(const Properties& props) : Integrator(props) {
		m_startPos = props.getPoint("StartPos", Point(0, 0, 0));
		m_endPos = props.getPoint("EndPos", Point(0, 0, 0));
		m_step = props.getFloat("step", 0.05);
		m_axialDivision = props.getSize("AxialDivision", 30);
		m_repetitiveSceneNum = props.getInteger("RepetitiveScene", 15);

		m_subSceneXSize = props.getFloat("subSceneXSize", 100); //scene size
		m_subSceneZSize = props.getFloat("subSceneZSize", 100);
	}

	TracInstrument(Stream* stream, InstanceManager* manager)
		: Integrator(stream, manager) {
	}

	void serialize(Stream* stream, InstanceManager* manager) const {
		Integrator::serialize(stream, manager);
	}

	bool preprocess(const Scene* scene, RenderQueue* queue, const RenderJob* job,
		int sceneResID, int sensorResID, int samplerResID) {
		Integrator::preprocess(scene, queue, job, sceneResID, sensorResID, samplerResID);

		//首先获取sceneBounds
		Vector2 sceneSize = Vector2(m_subSceneXSize, m_subSceneZSize);
		AABB scene_bound = scene->getKDTree()->getAABB();

		double sceneMaxY = scene_bound.max.y;
		double sceneMinY = scene_bound.min.y;
		double x_min = -0.5 * sceneSize.x;
		double x_max = 0.5 * sceneSize.x;
		double z_min = -0.5 * sceneSize.y;
		double z_max = 0.5 * sceneSize.y;
		m_sceneBounds = AABB(Point(x_min, sceneMinY, z_min), Point(x_max, sceneMaxY, z_max));
		return true;
	}

	void cancel() {
		//Scheduler::getInstance()->cancel(m_process);
	}

	bool rayIntersectExcludeEdge(const Scene* scene, Ray& ray, Intersection& its) {
		bool isIntersected = scene->rayIntersect(ray, its);
		if (isIntersected) {
			while (isIntersected && (!m_sceneBounds.contains(its.p))) {
				ray.o = its.p;
				isIntersected = scene->rayIntersect(ray, its);
			}
		}
		return isIntersected;
	}

	bool isRepetitiveOcclude(Ray& occludeRay, const Scene* scene, Intersection& its) {
		bool isIntersected = rayIntersectExcludeEdge(scene, occludeRay, its);
		if (!isIntersected) {
			for (int iteration = 0; iteration < m_repetitiveSceneNum; iteration++) {
				Float tNear, tFar;
				int exitFace;
				Vector boundExtend = m_sceneBounds.getExtents();
				m_sceneBounds.rayIntersectExt(occludeRay, tNear, tFar, exitFace);
				Point its_p = occludeRay.o + tFar * occludeRay.d;
				if (its_p.y < m_sceneBounds.max.y && exitFace != 1) {
					//offset the ray
					if (exitFace == 0) {
						if (occludeRay.d.x > 0) {
							occludeRay.o = its_p + Vector(-boundExtend.x, 0, 0);
						}
						else {
							occludeRay.o = its_p + Vector(boundExtend.x, 0, 0);
						}
					}
					else if (exitFace == 2) {
						if (occludeRay.d.z > 0) {
							occludeRay.o = its_p + Vector(0, 0, -boundExtend.z);
						}
						else {
							occludeRay.o = its_p + Vector(0, 0, boundExtend.z);
						}
					}
					isIntersected = rayIntersectExcludeEdge(scene, occludeRay, its);
					if (isIntersected) {
						return true;
					}
				}
				else {
					break;
				}
			}
		}
		return isIntersected;
	}

	Transform getRotateRayTransform(const Vector& pulseDirection) {
		Transform t;
		Float degree;
		Vector z(0, -1, 0);
		Vector axis = cross(z, pulseDirection);
		if (pulseDirection.x == 0 && pulseDirection.y == 1 && pulseDirection.z == 0) {
			axis = Vector(1, 0, 0);
		}
		if (abs(dot(axis, axis)) > 0) {
			degree = acos(dot(pulseDirection, z));
			degree = radToDeg(degree);
			t = Transform::rotate(axis, degree);
		}
		return t;
	}

	Ray generateRay(Transform& rotateRayTransform, const Vector2& s, const Point& Origin) {
		const Float d = 10000;
		Float m_fov = 0.004363323129986; // 0.25 degree
		Float t = d * tan(m_fov);
		Point p = Point(s.x * t, -d, s.y * t);
		p = rotateRayTransform.transformAffine(p);
		Ray ray;
		ray.setOrigin(Origin);
		ray.setDirection(normalize(Vector(p)));

		return ray;
	}

	bool render(Scene* scene, RenderQueue* queue,
		const RenderJob* job, int sceneResID, int sensorResID, int samplerResID) {
		ref<Scheduler> scheduler = Scheduler::getInstance();

		ref<Sensor> sensor = scene->getSensor();
		AABB aabb = scene->getKDTree()->getAABB();
		Vector extent = aabb.getExtents();
		size_t nCores = scheduler->getCoreCount();
		Log(EInfo, "Starting simulation job (%.2fx%.2f, " SIZE_T_FMT " sub-divisions, " 
			", " SSE_STR ") ..", extent.x, extent.z,
			m_axialDivision);

		CircleBeamGridSampler circleSampler(m_axialDivision);
		circleSampler.generate();
		

		//sun direction
		Vector sunDirInv = Vector(0.0, 1.0, 0.0);
		ref_vector<Emitter> emitters = scene->getEmitters();
		for (int i = 0; i < emitters.size(); i++) {
			if (emitters[i]->getProperties().hasProperty("direction")) {
				sunDirInv = -(emitters[i]->getProperties().getVector("direction"));
			}
		}
		
		//Generate ray
		Transform rotateRayTransform = getRotateRayTransform(sunDirInv);

		//output
		std::string outfilePath = scene->getDestinationFile().string() + "_trac.txt";
		std::ofstream fout(outfilePath);


		Vector dir = normalize(m_endPos - m_startPos);
		Float length = (m_endPos - m_startPos).length();
		Intersection its;
		int numberOfPos = (int)(length / m_step) + 1;
		int totalRaysPerPos = circleSampler.getSampleSize();

		fout << numberOfPos << "\t" << std::setw(5) << 3 << "\t" << std::fixed << std::setprecision(6)<<m_startPos.y << endl;

		for (int i = 0; i < numberOfPos; i++) {
			Point rayOrigin = m_startPos + (i*m_step) * dir;
			int numberOfOccludedRays = 0; // rays that intersect something
			while (circleSampler.hasNext()) {
				Vector2 s = circleSampler.next();
				Ray ray = generateRay(rotateRayTransform, s, rayOrigin);
				if (isRepetitiveOcclude(ray, scene, its)) {
					numberOfOccludedRays++;
				}
			}
			double transmittance = 1 - numberOfOccludedRays / ((double)totalRaysPerPos);
			double x = 0.5 * m_subSceneXSize - rayOrigin.x;
			double y = 0.5 * m_subSceneZSize - rayOrigin.z;
			fout <<std::fixed<< std::setprecision(2) << x << "\t" << std::fixed << std::setprecision(2) << y << "\t" << std::fixed << std::setprecision(6) << transmittance << endl;
			circleSampler.reset();
		}
		fout.close();

		return true;
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "TracInstrument["
			<< "]"<<endl;
		return oss.str();
	}


	MTS_DECLARE_CLASS()
protected:
	//size_t m_sampleCount; //total number of photons
	Point m_startPos;
	Point m_endPos;
	Float m_step;
	size_t m_axialDivision;

	int m_repetitiveSceneNum;
	AABB m_sceneBounds;

	Float m_subSceneXSize;
	Float m_subSceneZSize;

};

MTS_IMPLEMENT_CLASS_S(TracInstrument, false, Integrator)
MTS_EXPORT_PLUGIN(TracInstrument, "TracInstrument");
MTS_NAMESPACE_END
