#if !defined(__LESS_DIRECT_SUN_PROCESS_H_)
#define __LESS_DIRECT_SUN_PROCESS_H_

#include <mitsuba/core/sched.h>
#include "directsunwp.h"

MTS_NAMESPACE_BEGIN

/**
* \brief Work parallel process
*
* Used for emiting paticles into scene for sun direct illumination
*
*/
class DirectSunProcess : public ParallelProcess {
public:
	DirectSunProcess(int particle_per_m2, int scene_w, int scene_h, int block_w, int block_h, float sunPlaneHeight) :
							m_particlePerM2(particle_per_m2), m_currentOffset(0) {
		this->scene_w = scene_w;
		this->scene_h = scene_h;
		this->m_sunPlaneHeight = sunPlaneHeight;
		m_size = Vector2i(block_w, block_h);
		m_numBlocks = Vector2i(
			(int)std::ceil((float)scene_w / (float)block_w),
			(int)std::ceil((float)scene_h / (float)block_h));
		//m_all_point_cloud = std::vector<Point>();
		m_all_point_cloud = new float*[m_numBlocks.x*m_numBlocks.y];
		m_actual_num_of_each_block = new int[m_numBlocks.x*m_numBlocks.y];
	}
	//~DirectSunProcess()
	//{
	//	delete[] m_all_point_cloud;
	//}

	ref<WorkProcessor> createWorkProcessor() const {
		return new DirectSunWorkProcessor();
	}
	std::vector<std::string> getRequiredPlugins() {
		std::vector<std::string> result;
		result.push_back("LessSim");
		return result;
	}
	EStatus generateWork(WorkUnit *unit, int worker /* unused */) {
		if (m_currentOffset >= (int)m_numBlocks.x*m_numBlocks.y)
			return EFailure;
		SunDirectWorkUnit *wu = static_cast<SunDirectWorkUnit *>(unit);
		wu->setSize(m_size);
		int r = int(m_currentOffset / m_numBlocks.x);
		int c = m_currentOffset % m_numBlocks.x;
		Point2i offset = Point2i(r, c); // offset: 代表subregion的编号
		wu->setOffset(offset);
		wu->setParticleNum(m_particlePerM2);
		wu->setExtendedSceneSize(Vector2i(this->scene_w, this->scene_h));
		wu->setSunPlaneHeight(m_sunPlaneHeight);
		m_currentOffset++;
		return ESuccess;
	}
	void processResult(const WorkResult *result, bool cancelled) {
		if (cancelled) // indicates a work unit, which was
			return; // cancelled partly through its execution
		const SunDirectWorkResult *wr =
			static_cast<const SunDirectWorkResult *>(result);
		Point2i offset = wr->getOffset();
		m_actual_num_of_each_block[offset.x*m_numBlocks.x + offset.y] = wr->getPointNum();
		m_all_point_cloud[offset.x*m_numBlocks.x + offset.y] = wr->getPointCloud();
		/*for (int i = 0; i < pointNum*3; i=i+3)
		{
			m_all_point_cloud.push_back(Point(pointcloud[i], pointcloud[i + 1], pointcloud[i+2]));
		}
		cout << "jaja:" << m_all_point_cloud.size() << endl;*/
		/*int array_offset = (offset.x*m_numBlocks.x + offset.y)*m_size.x*m_size.y*m_particlePerM2*3;
		for (int i = array_offset; i < array_offset + m_size.x*m_size.y*m_particlePerM2*3; i++)
		{
			m_all_point_cloud[i] = pointcloud[i - array_offset];
		}*/
	}
	inline float** &getOutput() {
		return m_all_point_cloud;
	}
	inline int* &get_actual_point_num(int &size)
	{
		size = m_numBlocks.x*m_numBlocks.y;
		return m_actual_num_of_each_block;
	}

	MTS_DECLARE_CLASS()
public:
	int m_currentOffset;   //用于分配任务，到各个workprocessor
	Vector2i m_size;		//每个子区域的大小 单位为m
	int m_particlePerM2;    //每平米发射的点的光线条数
	float** m_all_point_cloud; //最后得到的交点数据
	int * m_actual_num_of_each_block;
	int scene_w, scene_h;//width and height of scene (m)
	Vector2i m_numBlocks; //讲场景平面划分成不同子区域，每个区域并行运算
	float m_sunPlaneHeight; //发射太阳光线的平面的高度，一般为场景最高点加上一定缓冲
	Point3f m_sceneCenter;// centor point of scene
};

MTS_IMPLEMENT_CLASS(DirectSunProcess, false, ParallelProcess)
MTS_NAMESPACE_END
#endif 
