#include <mitsuba/render/scene.h>
#include "directsun.h"
#include "LessSim\Tools.h"
MTS_NAMESPACE_BEGIN
class LessIntegrator :public Integrator
{
public:
	LessIntegrator(const Properties &props) : Integrator(props) {
		m_particle_per_m2 = props.getInteger("particlePerM2", 100);
		m_theta = lesstool::split2float(props.getString("theta"),",");
		m_phi = lesstool::split2float(props.getString("phi"), ",");

	}


	LessIntegrator(Stream *stream, InstanceManager *manager)
		: Integrator(stream, manager) {
	}
	/// Serialize to a binary data stream
	void serialize(Stream *stream, InstanceManager *manager) const {
		Integrator::serialize(stream, manager);
	}

	bool preprocess(const Scene *scene, RenderQueue *queue, const RenderJob *job,
		int sceneResID, int sensorResID, int samplerResID) {
		Integrator::preprocess(scene, queue, job, sceneResID, sensorResID, samplerResID);
		return true;
	}

	bool render(Scene *scene, RenderQueue *queue,
		const RenderJob *job, int sceneResID, int sensorResID, int samplerResID) {
		ref<Scheduler> sched = Scheduler::getInstance();

		AABB aabb = scene->getKDTree()->getAABB();
		Vector extent = aabb.getExtents();
		//cout << extent.toString() << endl;
		//float height = extent.y + 1;
		float height = extent.y + 1;
		float x_extent = 30;
		float z_extent = 30;
		int N_PER_M = m_particle_per_m2;// 1m^2的光子个数
		float power = 1300; // w/m^2
		float Pe = power / float(N_PER_M);// 每个光子的能量
		ref<DirectSunProcess> proc = new DirectSunProcess(N_PER_M, x_extent, z_extent, 5, 5, height, Pe);
		//proc->m_sceneCenter = aabb.getCenter();
		proc->bindResource("scene", sceneResID);
		proc->bindResource("sensor", sensorResID);
		proc->bindResource("sampler", samplerResID);
		sched->schedule(proc);
		m_process = proc;
		sched->wait(proc);
		m_process = NULL;

		cout << "computing done." << endl;
		float** output = proc->getOutput();
		int block_num;
		int * actural_num = proc->get_actual_point_num(block_num);
		int totalnum = 0;
		for (int i = 0; i < block_num; i++)
		{
			totalnum += actural_num[i];
		}
		cout << "number of points:" << totalnum << endl;
		lesstool::writeArray2File(output, actural_num, block_num, "points.txt");
		return proc->getReturnStatus() == ParallelProcess::ESuccess;
	}

	void cancel() {
		Scheduler::getInstance()->cancel(m_process);
	}

	MTS_DECLARE_CLASS()
private:
	ref<ParallelProcess> m_process;
	int m_particle_per_m2; //每平米光子数量
	std::vector<float> m_theta;//天顶角
	std::vector<float> m_phi;//方位角
};
MTS_IMPLEMENT_CLASS_S(LessIntegrator, false, Integrator)
MTS_EXPORT_PLUGIN(LessIntegrator, "Less Sim");
MTS_NAMESPACE_END