#include "LessSim\simjob.h"
#include <mitsuba/core/platform.h>

#include <mitsuba/core/sched_remote.h>
#include <mitsuba/core/sstream.h>
#include <mitsuba/core/fresolver.h>
#include <mitsuba/core/fstream.h>
#include <mitsuba/core/appender.h>
#include <mitsuba/core/sshstream.h>
#include <mitsuba/core/shvector.h>
#include <mitsuba/core/statistics.h>
#include <mitsuba/render/renderjob.h>
#include <mitsuba/render/scenehandler.h>
#include <fstream>
#include <stdexcept>
#include <boost/algorithm/string.hpp>

#if defined(__WINDOWS__)
#include <mitsuba/core/getopt.h>
#include <winsock2.h>
#else
#include <signal.h>
#endif


MTS_NAMESPACE_BEGIN

#define _TIME_STATS_

class LessSim : public Utility {
public:
	//load and initialize scene
	void loadAndInitScene(fs::path scene_path);

	int run(int argc, char **argv) {
		#ifdef _TIME_STATS_
				clock_t start, finish;
				double totaltime;
				start = clock();
		#endif

		fs::path scenPath = fs::path(argv[1]);
		this->loadAndInitScene(scenPath);

		SimJob* simjob = new SimJob(m_scene);
		simjob->startDirectIlluminationOnPlane();




		#ifdef _TIME_STATS_
				finish = clock();
				totaltime = (double)(finish - start) / CLOCKS_PER_SEC;
				cout << "此程序的运行时间为" << totaltime << "秒！" << endl;
		#endif

		return 0;
	}

private:
	ref<Scene> m_scene;
	MTS_DECLARE_UTILITY()
};

void LessSim::loadAndInitScene(fs::path scene_path)
{
	ParameterMap params;
	ref<FileResolver> fileResolver = Thread::getThread()->getFileResolver();
	fs::path
		filename = fileResolver->resolve(scene_path),
		filePath = fs::absolute(filename).parent_path(),
		baseName = filename.stem();
	ref<FileResolver> frClone = fileResolver->clone();
	frClone->prependPath(filePath);
	Thread::getThread()->setFileResolver(frClone);
	m_scene = loadScene(scene_path, params);
	//this->m_scene->configure();
	this->m_scene->initialize();
}
MTS_EXPORT_UTILITY(LessSim, "LESS Simulation")
MTS_NAMESPACE_END