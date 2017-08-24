#include "simjob.h"
#include "directsun.h"
#include "Tools.h"
MTS_NAMESPACE_BEGIN

SimJob::SimJob(){}

SimJob::SimJob(Scene* scene)
{
	m_scene = scene;
	ref<Scheduler> sched = Scheduler::getInstance();
	m_sceneResID = sched->registerResource(m_scene);
	ref<Sensor> sensor = m_scene->getSensor();
	ref<Sampler> sampler = m_scene->getSampler();
	m_sensorID = sched->registerResource(sensor);
	/* Create a sampler instance for every core */
	std::vector<SerializableObject *> samplers(sched->getCoreCount());
	for (size_t i = 0; i<sched->getCoreCount(); ++i) {
	ref<Sampler> clonedSampler = sampler->clone();
	clonedSampler->incRef();
	samplers[i] = clonedSampler.get();
	}
	m_samplerID = sched->registerMultiResource(samplers);
	for (size_t i = 0; i<sched->getCoreCount(); ++i)
	samplers[i]->decRef();
}

void SimJob::startDirectIlluminationOnPlane()
{
	ref<Scheduler> sched = Scheduler::getInstance();
	AABB aabb = m_scene->getKDTree()->getAABB();
	Vector extent = aabb.getExtents();
	cout << extent.toString() << endl;

	float height = extent.y + 1;
	float x_extent = 30;
	float z_extent = 30;
	int N_PER_M = 100;// 1m^2的光子个数
	float power = 1000; // w/m^2
	float Pe = power / float(N_PER_M);// 每个光子的能量
	ref<DirectSunProcess> proc = new DirectSunProcess(N_PER_M, x_extent, z_extent, 5, 5, height, Pe);
	
	cout << "core:" << sched->getCoreCount() << endl;
	proc->bindResource("scene", m_sceneResID);
	//proc->bindResource("sensor", m_sensorID);
	proc->bindResource("sampler", m_samplerID);
	m_scene->bindUsedResources(proc);
	/* Submit the encryption job to the scheduler */
	sched->schedule(proc);
	/* Wait for its completion */
	sched->wait(proc);
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

	writeArray2File(output, actural_num, block_num, "points.txt");
}

void SimJob::startDirectIlluminationOnDisk()
{
	BSphere bsphere = m_scene->getKDTree()->getAABB().getBSphere();

}
MTS_NAMESPACE_END