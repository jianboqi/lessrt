#if !defined(__SIMJOB_H_)
#define __SIMJOB_H_
#include <mitsuba/core/platform.h>
#include <mitsuba/render/util.h>
#include <mitsuba/core/sched.h>
#include <mitsuba/core/fresolver.h>
#include <fstream>
#include<boost/filesystem.hpp>
MTS_NAMESPACE_BEGIN
class SimJob
{
public:
	SimJob();
	SimJob(Scene* scene);
	/**
	* emite directinal illumnation from a plane
	* which is on the top of the scene
	*/
	void startDirectIlluminationOnPlane();
	/**
	* emite directinal illumnation from a disk
	* which is perpendicular to the sun direction.
	* this ensure that all the parts of the scene
	* can be illuminated despite of the sun zenith angle
	*/
	void startDirectIlluminationOnDisk();
	~SimJob(){}
private:
	ref<Scene> m_scene;
	int m_sceneResID, m_sensorID, m_samplerID;
};
MTS_NAMESPACE_END

#endif