#include <boost/filesystem.hpp>

#include <mitsuba/core/sched.h>
#include <mitsuba/render/scene.h>

#include <vector>
#include <iostream>
#include <cstdio>

#include "lidarutils.h"



MTS_NAMESPACE_BEGIN

class WaveformWorkUnit;
class WaveformWorkResult;
class WaveformWorkProcessor;
class WaveformProcess;

class WaveformWorkUnit : public WorkUnit {
public:
	void set(const WorkUnit *workUnit) {
		const WaveformWorkUnit *wu = static_cast<const WaveformWorkUnit *>(workUnit);
		m_x = wu->m_x;
		m_y = wu->m_y;
		m_z = wu->m_z;
		m_u = wu->m_u;
		m_v = wu->m_v;
		m_w = wu->m_w;
		m_i = wu->m_i;
	}

	void load(Stream *stream) {
		m_x = stream->readDouble();
		m_y = stream->readDouble();
		m_z = stream->readDouble();
		m_u = stream->readDouble();
		m_v = stream->readDouble();
		m_w = stream->readDouble();
		m_i = stream->readInt();
	}

	void save(Stream *stream) const {
		stream->writeDouble(m_x);
		stream->writeDouble(m_y);
		stream->writeDouble(m_z);
		stream->writeDouble(m_u);
		stream->writeDouble(m_v);
		stream->writeDouble(m_w);
		stream->writeInt(m_i);
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "WaveformWorkUnit[" << endl
			<< "  x = " << m_x << endl
			<< "  y = " << m_y << endl
			<< "  z = " << m_z << endl
			<< "  u = " << m_u << endl
			<< "  v = " << m_v << endl
			<< "  w = " << m_w << endl
			<< "  i = " << m_i << endl
			<< "]";
		return oss.str();
	}

	inline Point getOrigin() const {
		return Point(m_x, m_y, m_z);
	}

	inline Vector getDirection() const {
		return Vector(m_u, m_v, m_w);
	}

	inline void set(Float x, Float y, Float z, Float u, Float v, Float w) {
		m_x = x;
		m_y = y;
		m_z = z;
		m_u = u;
		m_v = v;
		m_w = w;
	}

	MTS_DECLARE_CLASS()
		
public:

	double m_x;
	double m_y;
	double m_z;
	double m_u;
	double m_v;
	double m_w;
	int m_i;
};

/* ==================================================================== */
/*                           Work result impl.                          */
/* ==================================================================== */
class WaveformWorkResult : public WorkResult {
public:

	void load(Stream *stream) {
		
		m_i = stream->readInt();
		m_numOfBins = stream->readSize();
		for (int i = 0; i < m_numOfBins; i++) {
			
			m_bin[i] = Spectrum(stream);
		}
	}

	void save(Stream *stream) const {
		
		stream->writeInt(m_i);
		stream->writeSize(m_numOfBins);
		for (int i = 0; i < m_numOfBins; i++) {
		
			m_bin[i].serialize(stream);
		}
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "WaveformWorkResult[" << endl
			<< "  m_numOfBins = " << m_numOfBins << endl
			<< "  m_i = " << m_i << ", " << endl
			<< "]";
		return oss.str();
	}

	void addToBin(int i, const Spectrum &w) {
		
		if (i >= m_numOfBins) {
			return;
		}
		m_bin[i] += w;
		
	}

	MTS_DECLARE_CLASS()

public:
	size_t m_numOfBins;
	
	std::vector<Spectrum> m_bin;
	int m_i;
};

/* ==================================================================== */
/*                         Work processor impl.                         */
/* ==================================================================== */
class WaveformWorkProcessor : public WorkProcessor {
public :
	WaveformWorkProcessor() : WorkProcessor() {}

	WaveformWorkProcessor(Stream *stream, InstanceManager *manager) : WorkProcessor(stream, manager) {}

	void serialize(Stream *stream, InstanceManager *manager) const {}

	ref<WorkUnit> createWorkUnit() const {
		return new WaveformWorkUnit();
	}	

	ref<WorkResult> createWorkResult() const {
		return new WaveformWorkResult();
	}

	ref<WorkProcessor> clone() const {
		return new WaveformWorkProcessor();
	}

	void prepare() {
		Scene *scene = static_cast<Scene *>(getResource("scene"));
		m_scene = new Scene(scene);
		m_random = new Random();
	}

	void process(const WorkUnit *workUnit, WorkResult *workResult, const bool &stop) {
		const WaveformWorkUnit *wu = static_cast<const WaveformWorkUnit *>(workUnit);
		WaveformWorkResult *wr = static_cast<WaveformWorkResult *>(workResult);
	
		wr->m_i = wu->m_i;
		wr->m_numOfBins = m_numOfBins;
		wr->m_bin.clear();
		wr->m_bin.resize(m_numOfBins);
		getWaveformResult(wu, wr);
	}

	// not overrided methods

	void getWaveformResult(const WaveformWorkUnit *wu, WaveformWorkResult *wr) {
	
		m_convergence = getConvergencePoint(wu);
		m_rotateRayTransform = getRotateRayTransform(wu);
		
		CircleBeamGridSampler sampler(m_axialDivision);

		while (sampler.hasNext()) {
			Vector2 s = sampler.next();
			Ray ray = generateRay(s, wu);
			Spectrum w = Spectrum(gaussian(s.length(), m_sigmaSquareOfBeam)) / m_weightTotal * m_pulseEnergy;
			trace(wu, wr, ray, w);	
		}
	}

	void trace(const WaveformWorkUnit *wu, WaveformWorkResult *wr, Ray &ray, Spectrum w) {
		Intersection its;
		Float l = 0;
		Spectrum r;

		for (int depth = 0; depth < m_maxDepth && m_scene->rayIntersect(ray, its); depth++) {
			const BSDF *bsdf = its.getBSDF();
			r = bsdf->getDiffuseReflectance(its);

			record(wu, wr, its, l, w);

			// calculate new ray
			l += its.t;
			w = w * r;
			ray.setOrigin(its.p);
			ray.setDirection(generateRandomDirection(its));
		}
	}

	void record(const WaveformWorkUnit *wu, WaveformWorkResult *wr, const Intersection &its, const Float &l, const Spectrum &w) {
		Ray ray;
		ray.setOrigin(its.p);
		ray.setDirection(normalize(wu->getOrigin() - its.p));

		Intersection shadowIts;
		m_scene->rayIntersect(ray, shadowIts);
		// if it is not blocked and in fov
		Vector vectorFromConvergence = normalize(its.p - m_convergence);
		Vector wiWorld = its.shFrame.toWorld(its.wi);
		if (dot(wiWorld, its.shFrame.n) * dot(vectorFromConvergence, its.shFrame.n) < 0
			&& ((wu->getOrigin()) - its.p).length() < shadowIts.t
			&& dot(vectorFromConvergence, wu->getDirection()) > m_cosFov) {
			// calculate path length and weight
			Vector v = wu->getOrigin() - its.p;
			Float d = v.length();
			Float solidAngle = m_area / (d * d) * (dot(-wu->getDirection(), normalize(v)));
			
			Float length = l + its.t + d;
			Spectrum weight = solidAngle * its.getBSDF()->getDiffuseReflectance(its) * INV_PI * w * absDot(normalize(wiWorld), its.shFrame.n);
			int i = (int)((length - 2.0 * m_minRange) / (C * m_rate));
			wr->addToBin(i, weight);
			
		}
	}

	Vector generateRandomDirection(const Intersection &its) {
		
		Float azimuth = 2.0 * M_PI * m_random->nextFloat();
		Float zenith = acos(m_random->nextFloat());

		Float x = sin(zenith) * cos(azimuth);
		Float y = sin(zenith) * sin(azimuth);
		Float z = cos(zenith);

		Vector n(its.shFrame.n);
		Vector wiWorld = its.shFrame.toWorld(its.wi);
		if (dot(wiWorld, n) < 0) {
			n = Vector(-n);
		}
		Vector direction = its.shFrame.s * x + its.shFrame.t * y + n * z;
		return direction;
	}

	Ray generateRay(const Vector2 &s, const WaveformWorkUnit *wu) {
		const Float d = 10000;
		Float t = d * tan(m_fov);
		Point p = Point(s.x * t, -d, s.y * t);
		
		p = m_rotateRayTransform.transformAffine(p);

		Ray ray;
		ray.setOrigin(wu->getOrigin());
		ray.setDirection(normalize(Vector(p)));
		
		return ray;
	}

	Point getConvergencePoint(const WaveformWorkUnit *wu) {
		Float r = sqrt(m_area * INV_PI);
		Point c = wu->getOrigin() - wu->getDirection() * (r / tan(m_fov));

		return c;
	}

	Transform getRotateRayTransform(const WaveformWorkUnit *wu) {
		Transform t;
		Float degree;

		Vector z(0, -1, 0);
		Vector n = wu->getDirection();

		Vector axis = cross(z, n);
		if (abs(dot(axis, axis)) > 0) {
			degree = acos(dot(n, z));
			degree = radToDeg(degree);
			t = Transform::rotate(axis, degree);
		}

		return t;
	}

	MTS_DECLARE_CLASS()
public:
	ref<Scene> m_scene;

	Point m_convergence;
	Transform m_rotateRayTransform;

	ref<Random> m_random;

	// parameter
	
	Float m_sigmaSquareOfBeam;
	Spectrum m_weightTotal;
	Float m_cosFov;
	int m_numOfBins;

	// from XML

	int m_maxDepth;
	int m_axialDivision;

	Float m_fp;
	Float m_fov;
	Float m_pulseEnergy;
	Float m_rate;
	Float m_area;
	Float m_minRange;
	Float m_maxRange;
};

/* ==================================================================== */
/*                        Parallel process impl.                        */
/* ==================================================================== */
class WaveformProcess : public ParallelProcess {
public:
	WaveformProcess() : m_pos(0), m_numOfPulses(0) {}

	ref<WorkProcessor> createWorkProcessor() const {
		WaveformWorkProcessor *processor = new WaveformWorkProcessor();

		processor->m_sigmaSquareOfBeam = m_sigmaSquareOfBeam;
		processor->m_weightTotal = m_weightTotal;
		processor->m_cosFov = m_cosFov;
		processor->m_numOfBins = m_numOfBins;

		processor->m_maxDepth = m_maxDepth;
		processor->m_axialDivision = m_axialDivision;
		processor->m_fp = m_fp;
		processor->m_fov = m_fov;
		processor->m_pulseEnergy = m_pulseEnergy;
		processor->m_rate = m_rate;
		processor->m_area = m_area;
		processor->m_minRange = m_minRange;
		processor->m_maxRange = m_maxRange;

		return processor;
	}

	EStatus generateWork(WorkUnit *unit, int worker) {
		if (m_pos >= m_numOfPulses) {
			return EFailure;
		}
		WaveformWorkUnit *wu = static_cast<WaveformWorkUnit *>(unit);
		wu->set(m_x[m_pos], m_y[m_pos], m_z[m_pos], m_u[m_pos], m_v[m_pos], m_w[m_pos]);
		wu->m_i = m_pos;
		m_pos++;
		return ESuccess;
	}

	void processResult(const WorkResult *result, bool cancelled) {
		if (cancelled) {
			return;
		}

		const WaveformWorkResult *wr = static_cast<const WaveformWorkResult *>(result);

		addWaveform(wr);

	}

	void bindResource(const std::string &name, int id) {
		if (name == "scene") {
			m_scene = static_cast<Scene *>(Scheduler::getInstance()->getResource(id));
		}

		ParallelProcess::bindResource(name, id);
	}

	// not overrided methods
	void addGeometryConfiguration(Float x, Float y, Float z, Float u, Float v, Float w) {
		m_x.push_back(x);
		m_y.push_back(y);
		m_z.push_back(z);

		Vector d(u, v, w);
		d = normalize(d);
		m_u.push_back(d.x);
		m_v.push_back(d.y);
		m_w.push_back(d.z);


	}

	void addWaveform(const WaveformWorkResult *wr) {
		
		m_waveforms[wr->m_i] = std::vector<Spectrum>(wr->m_bin);
	}
	
	void outputWaveformToOneFile(std::string outName = "accumulation.txt") {
		
		fs::path full_path(fs::initial_path());
		full_path = fs::system_complete(fs::path(m_scene->getDestinationFile().string(), fs::native));
		if (!fs::exists(full_path))
		{
			bool bRet = fs::create_directories(full_path);
			if (false == bRet)
			{
				cout << "no dir" << endl;
			}
		}
	
		std::string folderPath = m_scene->getDestinationFile().string();
		
		std::ofstream fout(folderPath + "\\" + outName);

		Float l;
		Float d = C * m_rate;
		
		for (auto w : m_waveforms) {
			l = m_minRange * 2.0;
			for (auto s : w) {
				//fout << l << "\t" << s.eval(361) << "\t" << s.eval(596) << "\t" << endl;  
				fout << l;
				for (auto& wl : wavelengths) {
					fout << "\t" << s.eval(wl);
				}
				fout << endl;
				
				l += d;
			}
		}
		fout.close();	
	}

	MTS_DECLARE_CLASS()
public:
	int m_pos;
	size_t m_numOfPulses;
	std::vector<Float> m_x;
	std::vector<Float> m_y;
	std::vector<Float> m_z;
	std::vector<Float> m_u;
	std::vector<Float> m_v;
	std::vector<Float> m_w;
	ref<Scene> m_scene;

	std::vector<std::vector<Spectrum> > m_waveforms;
	
	Float m_sigmaSquareOfBeam;
	Spectrum m_weightTotal;
	Float m_cosFov;
	int m_numOfBins;
	
	// from XML

	int m_maxDepth;
	int m_axialDivision;

	Float m_fp;
	Float m_fov;
	Float m_pulseEnergy;
	Float m_rate;
	Float m_area;
	Float m_minRange;
	Float m_maxRange;

	std::string m_outputPath;

};

MTS_IMPLEMENT_CLASS(WaveformWorkUnit, false, WorkUnit)
MTS_IMPLEMENT_CLASS(WaveformWorkResult, false, WorkResult)
MTS_IMPLEMENT_CLASS_S(WaveformWorkProcessor, false, WorkProcessor)
MTS_IMPLEMENT_CLASS(WaveformProcess, false, ParallelProcess)

MTS_NAMESPACE_END
