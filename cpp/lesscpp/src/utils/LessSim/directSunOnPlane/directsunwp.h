
#if !defined(__LESS_DIRECT_SUN_WP_H_)
#define __LESS_DIRECT_SUN_WP_H_

#include <mitsuba/core/sched.h>
#include "directsunwu.h"
#include "directsunwr.h"
#include <ctime>
#include <list>
MTS_NAMESPACE_BEGIN
#define N 999 //三位小数。
/**
* \brief Work processor for sun illumination
*
* Used for emiting paticles into scene for sun direct illumination
*
*/
class DirectSunWorkProcessor : public WorkProcessor {
public:
	/// Construct a new work processor
	DirectSunWorkProcessor() : WorkProcessor() { }
	/// Unserialize from a binary data stream (nothing to do in our case)
	DirectSunWorkProcessor(Stream *stream, InstanceManager *manager)
		: WorkProcessor(stream, manager) { }
	/// Serialize to a binary data stream (nothing to do in our case)
	void serialize(Stream *stream, InstanceManager *manager) const {
	}

	ref<WorkUnit> createWorkUnit() const {
		return new SunDirectWorkUnit();
	}
	ref<WorkResult> createWorkResult() const {
		return new SunDirectWorkResult();
	}
	ref<WorkProcessor> clone() const {
		return new DirectSunWorkProcessor(); // No state to clone in our case
	}
	/// No internal state, thus no preparation is necessary
	void prepare() {
		Scene *scene = static_cast<Scene *>(getResource("scene"));
		m_scene = new Scene(scene);
		m_sampler = static_cast<Sampler *>(getResource("sampler"));
		//Sensor* m_sensor = static_cast<Sensor *>(getResource("sensor"));
		//m_integrator = static_cast<SamplingIntegrator *>(getResource("integrator"));
		//m_scene->removeSensor(scene->getSensor());
		//m_scene->addSensor(m_sensor);
		//m_scene->setSensor(m_sensor);
		m_scene->setSampler(m_sampler);
		//m_scene->setIntegrator(m_integrator);
		//m_integrator->wakeup(m_scene, m_resources);
		m_scene->wakeup(m_scene, m_resources);
		//m_scene->configure();
		m_scene->initializeBidirectional();
		
		//m_scene->initialize();
	}
	/// Do the actual computation
	void process(const WorkUnit *workUnit, WorkResult *workResult,
		const bool &stop) {
		const SunDirectWorkUnit *wu
			= static_cast<const SunDirectWorkUnit *>(workUnit);
		SunDirectWorkResult *wr = static_cast<SunDirectWorkResult *>(workResult);
		Vector2i size = wu->getSize();
		Point2i offset = wu->getOffset();
		Vector2i extended_size = wu->getExtendedSceneSize();
		int particleNum = wu->getParticleNum();
		float sunPlaneHeight = wu->getSunPlaneHeight();
		wr->setSize(size);
		wr->setOffset(offset);
		wr->setParticleNum(particleNum);
		Point2f real_offset = Point2f(0.5*extended_size.x - size.x*offset.y, 0.5*extended_size.y - size.y*offset.x);
		std::list<Point> intersected_points;
		for (int i = 0; i < size.y; i++)
		{
			for (int j = 0; j < size.x; j++)
			{
				srand(time(NULL));//设置随机数种子，使每次获取的随机序列不同。
				for (int k = 0; k < particleNum; k++) //每平米产生的随机随机数
				{
					float x = -rand() % (N + 1) / (float)(N + 1);//生成0-1间的随机数。
					float z = -rand() % (N + 1) / (float)(N + 1);//生成0-1间的随机数。
					Point2f pos_in_block = Point2f(i + x, j + z);
					Point2f pos_in_scene = real_offset + pos_in_block;
					Ray ray;
					Point o = Point(pos_in_scene.x, sunPlaneHeight, pos_in_scene.y);
					//Point o = Point(0, sunPlaneHeight,0);
					ray.setOrigin(o);
					ray.setDirection(Vector(1, -1, 0));
					Intersection its;				
					bool isIntersected = m_scene->rayIntersect(ray, its);
					if (isIntersected)
					{
						intersected_points.push_back(its.p);
						/*BSDFSamplingRecord query(its, m_sampler, ERadiance);
						const BSDF *bsdf = its.getBSDF();
						bsdf->sample(query, m_sampler->next2D());
						const Vector wo = its.toWorld(query.wo);
						Ray ray1 = Ray(its.p, wo, ray.time);
						Intersection its1;
						bool isIntersected1 = m_scene->rayIntersect(ray1, its1);
						if (isIntersected1)
						{
							intersected_points.push_back(its1.p);
						}*/
					}
				}
					

			}
		}
		float* result = new float[intersected_points.size() * 3];
		std::list<Point>::iterator it = intersected_points.begin();
		//cout << "intersected_size:" << intersected_points.size() << endl;
		int index = 0;
		for (;it != intersected_points.end(); it++)
		{
			result[index++] = (*it).x;
			result[index++] = (*it).y;
			result[index++] = (*it).z;
		}
		wr->setPointNum(intersected_points.size());
		wr->setPointCloud(result);
	}
	MTS_DECLARE_CLASS()
private:
	ref<Scene> m_scene;
	ref<Sampler> m_sampler;
};
MTS_IMPLEMENT_CLASS_S(DirectSunWorkProcessor, false, WorkProcessor)
MTS_NAMESPACE_END
#endif