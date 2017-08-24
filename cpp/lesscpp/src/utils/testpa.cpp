#include <mitsuba/core/platform.h>
#include <mitsuba/render/util.h>
#include <mitsuba/core/sched.h>
#include <mitsuba/core/fresolver.h>
#include <fstream>
#include<boost/filesystem.hpp>  

MTS_NAMESPACE_BEGIN
class SunDirectWorkUnit : public WorkUnit {
public:
	inline SunDirectWorkUnit() { }

	/* WorkUnit implementation */
	void set(const WorkUnit *wu)
	{
		const SunDirectWorkUnit *sundirect = static_cast<const SunDirectWorkUnit *>(wu);
		m_offset = sundirect->m_offset;
		m_size = sundirect->m_size;
		m_particlePerM2 = sundirect->m_particlePerM2;
		m_sunPlaneHeight = sundirect->m_sunPlaneHeight;
	}
	void load(Stream *stream)
	{
		int data[4];
		stream->readIntArray(data, 4);
		m_offset.x = data[0];
		m_offset.y = data[1];
		m_size.x = data[2];
		m_size.y = data[3];
		m_particlePerM2 = stream->readInt();
		m_sunPlaneHeight = stream->readFloat();
	}
	void save(Stream *stream) const
	{
		int data[4];
		data[0] = m_offset.x;
		data[1] = m_offset.y;
		data[2] = m_size.x;
		data[3] = m_size.y;
		stream->writeIntArray(data, 4);
		stream->writeInt(m_particlePerM2);
		stream->writeFloat(m_sunPlaneHeight);
	}

	inline const Point2i &getOffset() const { return m_offset; }
	inline const Vector2i &getSize() const { return m_size; }
	inline const int &getParticleNum() const { return m_particlePerM2; }
	inline const float &getSunPlaneHeight() const { return m_sunPlaneHeight; }

	inline void setOffset(const Point2i &offset) { m_offset = offset; }
	inline void setSize(const Vector2i &size) { m_size = size; }
	inline void setParticleNum(int num) { m_particlePerM2 = num; }
	inline void setSunPlaneHeight(float height) { m_sunPlaneHeight = height; }

	std::string toString() const
	{
		std::ostringstream oss;
		oss << "SunDirectWorkUnit[offset=" << m_offset.toString()
			<< ", size=" << m_size.toString() << "]";
		return oss.str();
	}
	MTS_DECLARE_CLASS()
private:
	Point2i m_offset;
	Vector2i m_size;
	int m_particlePerM2;
	float m_sunPlaneHeight; //发射太阳光线的平面的高度，一般为场景最高点加上一定缓冲

};
MTS_IMPLEMENT_CLASS(SunDirectWorkUnit, false, WorkUnit)


class SunDirectWorkResult :public WorkResult
{
public:

	void load(Stream *stream) {
		int data[4];
		stream->readIntArray(data, 4);
		m_offset.x = data[0];
		m_offset.y = data[1];
		m_size.x = data[2];
		m_size.y = data[3];
		size_t nEntries = (size_t)m_size.x * (size_t)m_size.y;
		stream->readFloatArray(reinterpret_cast<float *>(point_cloud),
			nEntries * m_particlePerM2);
		m_particlePerM2 = stream->readInt();
	}

	void save(Stream *stream) const {
		int data[4];
		data[0] = m_offset.x;
		data[1] = m_offset.y;
		data[2] = m_size.x;
		data[3] = m_size.y;
		stream->writeIntArray(data, 4);
		size_t nEntries = (size_t)m_size.x * (size_t)m_size.y;
		stream->writeFloatArray(reinterpret_cast<const float *>(point_cloud),
			nEntries * m_particlePerM2);
		stream->writeInt(m_particlePerM2);
	}

	inline const Point2i &getOffset() const { return m_offset; }
	inline const Vector2i &getSize() const { return m_size; }
	inline float* getPointCloud() const { return point_cloud; }

	inline void setOffset(const Point2i &offset) { m_offset = offset; }
	inline void setSize(const Vector2i &size) { m_size = size; }
	inline void setParticleNum(const int num) { m_particlePerM2 = num; }
	inline void setPointCloud(float * pointcloud) { point_cloud = pointcloud; }


	std::string toString() const {
		std::ostringstream oss;
		oss << "SunDirectWorkResult[" << endl
			<< "]";
		return oss.str();
	}
	MTS_DECLARE_CLASS()
private:
	float* point_cloud;
	Point2i m_offset;
	Vector2i m_size;
	int m_particlePerM2;

};
MTS_IMPLEMENT_CLASS(SunDirectWorkResult, false, WorkResult)



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
		m_scene->wakeup(m_scene, m_resources);
		m_scene->initializeBidirectional();
	}
	/// Do the actual computation
	void process(const WorkUnit *workUnit, WorkResult *workResult,
		const bool &stop) {
		const SunDirectWorkUnit *wu
			= static_cast<const SunDirectWorkUnit *>(workUnit);
		SunDirectWorkResult *wr = static_cast<SunDirectWorkResult *>(workResult);
		Vector2i size = wu->getSize();
		Point2i offset = wu->getOffset();
		int particleNum = wu->getParticleNum();
		cout << particleNum << endl;
		float sunPlaneHeight = wu->getSunPlaneHeight();
		wr->setSize(size);
		wr->setOffset(offset);
		wr->setParticleNum(particleNum);
		float* result = new float[size.x*size.y*particleNum];
		for (int i = 0; i < size.x*size.y*particleNum; i++)
		{
			Vector direction = Vector(0.0f, -1.0f, 0.0f);
			Ray ray;
			ray.setOrigin(Point(i, i, i));
			ray.setDirection(Vector(0, -1, 0));
			Intersection its;
			bool isIntersected = m_scene->rayIntersect(ray, its);
			/*if (isIntersected)
			cout << its.p.x << " " << its.p.y << " " << its.p.z << endl;*/
			if (isIntersected)
				result[i] = -111;
			else
				result[i] = -9;
		}
		wr->setPointCloud(result);
	}
	MTS_DECLARE_CLASS()
private:
	ref<Scene> m_scene;

};
MTS_IMPLEMENT_CLASS_S(DirectSunWorkProcessor, false, WorkProcessor)


class DirectSunProcess : public ParallelProcess {
public:
	DirectSunProcess(int particle_per_m2, int scene_w, int scene_h, int block_w, int block_h, float sunPlaneHeight) :
		m_particlePerM2(particle_per_m2), m_currentOffset(0) {
		this->scene_w = scene_w;
		this->scene_h = scene_h;
		this->sunPlaneHeight = sunPlaneHeight;
		m_size = Vector2i(block_w, block_h);
		m_numBlocks = Vector2i(
			(int)std::ceil((float)scene_w / (float)block_w),
			(int)std::ceil((float)scene_h / (float)block_h));
		m_all_point_cloud = new float[m_numBlocks.x*m_numBlocks.y*particle_per_m2*block_w*block_h];
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
		Point2i offset = Point2i(r, c); // offset: x轴朝下，y轴朝右，代表subregion的编号
		wu->setOffset(offset);
		wu->setParticleNum(m_particlePerM2);
		m_currentOffset++;
		return ESuccess;
	}
	void processResult(const WorkResult *result, bool cancelled) {
		if (cancelled) // indicates a work unit, which was
			return; // cancelled partly through its execution
		const SunDirectWorkResult *wr =
			static_cast<const SunDirectWorkResult *>(result);
		Point2i offset = wr->getOffset();
		float * pointcloud = wr->getPointCloud();
		int array_offset = (offset.x*m_numBlocks.x + offset.y)*m_size.x*m_size.y*m_particlePerM2;
		for (int i = array_offset; i < array_offset + m_size.x*m_size.y*m_particlePerM2; i++)
		{
			m_all_point_cloud[i] = pointcloud[i - array_offset];
		}
	}
	inline float* &getOutput() {
		return m_all_point_cloud;
	}
	MTS_DECLARE_CLASS()
public:
	int m_currentOffset;   //用于分配任务，到各个workprocessor
	Vector2i m_size;		//每个子区域的大小 单位为m
	int m_particlePerM2;    //每平米发射的点的光线条数
	float* m_all_point_cloud; //最后得到的交点数据
	int scene_w, scene_h;//width and height of scene (m)
	Vector2i m_numBlocks; //讲场景平面划分成不同子区域，每个区域并行运算
	float sunPlaneHeight; //发射太阳光线的平面的高度，一般为场景最高点加上一定缓冲
};

MTS_IMPLEMENT_CLASS(DirectSunProcess, false, ParallelProcess)



class SimJob
{
public:
	SimJob(){}
	SimJob(Scene* scene)
	{
		m_scene = scene;
		ref<Scheduler> sched = Scheduler::getInstance();
		m_sceneResID = sched->registerResource(m_scene);
		//proc->bindResource("scene", sceneResID);
	}
	void start_illumination()
	{
		AABB aabb = m_scene->getAABB();
		Vector extent = aabb.getExtents();
		cout << extent.x << " " << extent.z << endl;
		float height = extent.y + 1;
		float x_extent = extent.x + 20;
		float z_extent = extent.z + 20;

		ref<DirectSunProcess> proc = new DirectSunProcess(1, x_extent, z_extent, 100, 100, height);
		ref<Scheduler> sched = Scheduler::getInstance();
		proc->bindResource("scene", m_sceneResID);
		m_scene->bindUsedResources(proc);
		/* Submit the encryption job to the scheduler */
		sched->schedule(proc);
		/* Wait for its completion */
		sched->wait(proc);

		cout << "result:" << proc->getOutput()[499];
	}
	~SimJob(){}
private:
	ref<Scene> m_scene;
	int m_sceneResID;
};

class testpa : public Utility {
public:
	//load and initialize scene
	void loadAndInitScene(fs::path scene_path);

	int run(int argc, char **argv) {
		fs::path scenPath = fs::path(argv[1]);
		this->loadAndInitScene(scenPath);

		SimJob* simjob = new SimJob(m_scene);
		simjob->start_illumination();

		return 0;
	}

private:
	ref<Scene> m_scene;
	MTS_DECLARE_UTILITY()
};

void testpa::loadAndInitScene(fs::path scene_path)
{
	ParameterMap params;
	ref<FileResolver> fileResolver = Thread::getThread()->getFileResolver();
	fs::path
		filename = fileResolver->resolve(scene_path),
		filePath = fs::absolute(filename).parent_path();
	fileResolver->prependPath(filePath);
	this->m_scene = this->loadScene(filename, params);
	this->m_scene->configure();
	this->m_scene->initialize();
}
MTS_EXPORT_UTILITY(testpa, "LESS Simulation")
MTS_NAMESPACE_END