
#if !defined(__LESS_DIRECT_SUN_WU_H_)
#define __LESS_DIRECT_SUN_WU_H_

#include <mitsuba/core/sched.h>

MTS_NAMESPACE_BEGIN

/**
* \brief Work unit that specifies a rectangular region in an plane.
*
* Used for emiting paticles into scene for sun direct illumination
* 
*/
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
		int data[6];
		stream->readIntArray(data, 6);
		m_offset.x = data[0];
		m_offset.y = data[1];
		m_size.x = data[2];
		m_size.y = data[3];
		m_extendedSceneSize.x = data[4];
		m_extendedSceneSize.y = data[5];
		m_particlePerM2 = stream->readInt();
		m_sunPlaneHeight = stream->readFloat();
	}
	void save(Stream *stream) const
	{
		int data[6];
		data[0] = m_offset.x;
		data[1] = m_offset.y;
		data[2] = m_size.x;
		data[3] = m_size.y;
		data[4] = m_extendedSceneSize.x;
		data[5] = m_extendedSceneSize.y;
		stream->writeIntArray(data, 6);
		stream->writeInt(m_particlePerM2);
		stream->writeFloat(m_sunPlaneHeight);
	}

	inline const Point2i &getOffset() const { return m_offset; }
	inline const Vector2i &getSize() const { return m_size; }
	inline const int &getParticleNum() const { return m_particlePerM2; }
	inline const float &getSunPlaneHeight() const { return m_sunPlaneHeight; }
	inline const Vector2i &getExtendedSceneSize() const { return m_extendedSceneSize; }

	inline void setOffset(const Point2i &offset) { m_offset = offset; }
	inline void setSize(const Vector2i &size) { m_size = size; }
	inline void setParticleNum(int num) { m_particlePerM2 = num; }
	inline void setSunPlaneHeight(float height) { m_sunPlaneHeight = height; }
	inline void setExtendedSceneSize(const Vector2i &extendedSize) { m_extendedSceneSize = extendedSize; }

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
	Vector2i m_extendedSceneSize;//添加了边缘缓冲区的场景水平方向尺寸：宽度和高度
	int m_particlePerM2;
	float m_sunPlaneHeight; //发射太阳光线的平面的高度，一般为场景最高点加上一定缓冲

	
};
MTS_IMPLEMENT_CLASS(SunDirectWorkUnit, false, WorkUnit)

MTS_NAMESPACE_END

#endif 
