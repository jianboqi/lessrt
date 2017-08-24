
#if !defined(__LESS_DIRECT_SUN_WR_H_)
#define __LESS_DIRECT_SUN_WR_H_

#include <mitsuba/core/sched.h>

MTS_NAMESPACE_BEGIN

/**
* \brief Work result that specifies store the result of particle trace
*
* Used for emiting paticles into scene for sun direct illumination
*
*/
class SunDirectWorkResult :public WorkResult
{
public:

	void load(Stream *stream) {
		int data[5];
		stream->readIntArray(data, 5);
		m_offset.x = data[0];
		m_offset.y = data[1];
		m_size.x = data[2];
		m_size.y = data[3];
		m_pointNum = data[4];
		stream->readFloatArray(reinterpret_cast<float *>(point_cloud),
			m_pointNum * 3);
		m_particlePerM2 = stream->readInt();
	}

	void save(Stream *stream) const {
		int data[5];
		data[0] = m_offset.x;
		data[1] = m_offset.y;
		data[2] = m_size.x;
		data[3] = m_size.y;
		data[4] = m_pointNum;
		stream->writeIntArray(data, 5);
		stream->writeFloatArray(reinterpret_cast<const float *>(point_cloud),
			m_pointNum * 3);
		stream->writeInt(m_particlePerM2);
	}

	inline const Point2i &getOffset() const { return m_offset; }
	inline const Vector2i &getSize() const { return m_size; }
	inline float* getPointCloud() const { return point_cloud; }
	inline int getPointNum() const { return m_pointNum; }

	inline void setOffset(const Point2i &offset) { m_offset = offset; }
	inline void setSize(const Vector2i &size) { m_size = size; }
	inline void setParticleNum(const int num) { m_particlePerM2 = num; }
	inline void setPointCloud(float * pointcloud) { point_cloud = pointcloud;}
	inline void setPointNum(int num) { m_pointNum = num; }
	

	std::string toString() const {
		std::ostringstream oss;
		oss << "SunDirectWorkResult[" << endl
			<< "]";
		return oss.str();
	}
MTS_DECLARE_CLASS()
private:
	float* point_cloud;
	int m_pointNum; //actual intersected number
	Point2i m_offset;
	Vector2i m_size;
	int m_particlePerM2;
	
};
MTS_IMPLEMENT_CLASS(SunDirectWorkResult, false, WorkResult)

MTS_NAMESPACE_END
#endif 
