#include <boost/filesystem.hpp>
#include <boost/thread/locks.hpp>
#include <boost/thread/shared_mutex.hpp>

#include <mitsuba/core/sched.h>
#include <mitsuba/render/scene.h>
#include <vector>
#include <iostream>
#include <windows.h>
#include <cstdio>
#include <cstring>

#include "../lidarutils.h"
#include "../fftconv1d.cpp"

#include "../PulseGaussianFitting.h"
#include "../mpfit.h"
#include "../threadsafe_queue.h"



MTS_NAMESPACE_BEGIN

class PointCloudWorkUnit;
class PointCloudWorkResult;
class PointCloudWorkProcessor;
class PointCloudProcess;

struct DiscretePoint {
	Float x;
	Float y;
	Float z;
	Float a;
	int i;
	DiscretePoint() {}
	DiscretePoint(Float x, Float y, Float z, Float a, int i) : x(x), y(y), z(z), a(a), i(i) {}
};

struct WorkResultRecord {
	Float l;
	Spectrum w;
	WorkResultRecord() {}
	WorkResultRecord(Float l, Spectrum w) : l(l), w(w) {}
};

class PointCloudWorkUnit : public WorkUnit {
public:
	void set(const WorkUnit *workUnit) {
		const PointCloudWorkUnit *wu = static_cast<const PointCloudWorkUnit *>(workUnit);
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
		oss << "PointCloudWorkUnit[" << endl
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
class PointCloudWorkResult : public WorkResult {
public:

	void load(Stream *stream) {
		cout << "Work Result load" << endl;
	}

	void save(Stream *stream) const {
		cout << "Work Result save" << endl;
	}

	std::string toString() const {
		std::ostringstream oss;
		return oss.str();
	}

	void init() {
		m_records.clear();
		m_points.clear();
	}

	void commit(Float length, Spectrum weight) {
		m_records.push_back(WorkResultRecord(length, weight));
	}

	MTS_DECLARE_CLASS()

public:

	int m_i;
	std::vector<WorkResultRecord> m_records;
	std::vector<DiscretePoint> m_points;
};

/* ==================================================================== */
/*                         Work processor impl.                         */
/* ==================================================================== */
class PointCloudWorkProcessor : public WorkProcessor {
public:
	PointCloudWorkProcessor() : WorkProcessor() {}

	PointCloudWorkProcessor(Stream *stream, InstanceManager *manager) : WorkProcessor(stream, manager) {}

	void serialize(Stream *stream, InstanceManager *manager) const {}

	ref<WorkUnit> createWorkUnit() const {
		return new PointCloudWorkUnit();
	}

	ref<WorkResult> createWorkResult() const {
		return new PointCloudWorkResult();
	}

	ref<WorkProcessor> clone() const {
		return new PointCloudWorkProcessor();
	}

	void prepare() {
		Scene *scene = static_cast<Scene *>(getResource("scene"));
		m_scene = new Scene(scene);
		m_random = new Random();
	}

	void process(const WorkUnit *workUnit, WorkResult *workResult, const bool &stop) {
		const PointCloudWorkUnit *wu = static_cast<const PointCloudWorkUnit *>(workUnit);
		PointCloudWorkResult *wr = static_cast<PointCloudWorkResult *>(workResult);

		//cout << wr << endl;

		wr->m_i = wu->m_i;
		
		wr->init();
		
		getWaveformResult(wu, wr);
		

		getPoints(wu, wr);

	}

	// not overrided methods

	void getWaveformResult(const PointCloudWorkUnit *wu, PointCloudWorkResult *wr) {

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

	void trace(const PointCloudWorkUnit *wu, PointCloudWorkResult *wr, Ray &ray, Spectrum w) {
		Intersection its;
		Float l = 0;
		Spectrum r;

		for (int depth = 0; depth < m_maxDepth && m_scene->rayIntersect(ray, its); depth++) {
			const BSDF *bsdf = its.getBSDF();
			r = bsdf->getDiffuseReflectance(its);

			if (r.abs().average() < eps) {
				return;
			}

			record(wu, wr, its, l, w);

			// calculate new ray
			l += its.t;
			w = w * r;
			ray.setOrigin(its.p);
			ray.setDirection(generateRandomDirection(its));
		}
	}

	void record(const PointCloudWorkUnit *wu, PointCloudWorkResult *wr, const Intersection &its, const Float &l, const Spectrum &w) {
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

			wr->commit(length, weight);

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

	Ray generateRay(const Vector2 &s, const PointCloudWorkUnit *wu) {
		const Float d = 10000;
		Float t = d * tan(m_fov);
		Point p = Point(s.x * t, -d, s.y * t);

		p = m_rotateRayTransform.transformAffine(p);

		Ray ray;
		ray.setOrigin(wu->getOrigin());
		ray.setDirection(normalize(Vector(p)));

		return ray;
	}

	Point getConvergencePoint(const PointCloudWorkUnit *wu) {
		Float r = sqrt(m_area * INV_PI);
		Point c = wu->getOrigin() - wu->getDirection() * (r / tan(m_fov));

		return c;
	}

	Transform getRotateRayTransform(const PointCloudWorkUnit *wu) {
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

	void getPoints(const PointCloudWorkUnit *wu, PointCloudWorkResult *wr) {
		std::vector<Spectrum> bin(m_numOfBins);
		int idx;
		for (const WorkResultRecord& r : wr->m_records) {
			idx = (int)((r.l - 2.0 * m_minRange) / (C * m_rate));
			addToBin(bin, idx, r.w);
		}

		// BEGIN: get point cloud from accumulation

		// 1. convolve
		std::vector<double> accumulation(bin.size());
		//cout << "accum" << endl;
		for (int i = 0; i < bin.size(); ++i) {
			accumulation[i] = bin[i].eval(wavelengths[0]);  // TODO
		}
		std::vector<double> waveform = conv(accumulation, m_pulse);

		// 2. gaussian decomposition
		std::vector<double> par;  // amp, center, sigma
		gaussianDecomposition(waveform, par);

		// 3. output point cloud
		Float step = C * m_rate * 0.5;
		Float a;
		Float t;
		Point o = Point(wu->m_x, wu->m_y, wu->m_z);
		Vector d = Vector(wu->m_u, wu->m_v, wu->m_w);
		Point p;
		for (int i = 0; 3 * i < par.size(); i++) {
			a = par[i * 3] / (sqrt(2 * M_PI) * par[i * 3 + 2]);
			t = m_minRange + (par[i * 3 + 1] + 0.5) * step;
			p = o + d * t;
			DiscretePoint point(p.x, p.y, p.z, a, wr->m_i);
			wr->m_points.push_back(point);
		}
		// END: get point cloud from accumulation
	}

	void gaussianDecomposition(std::vector<double> &wf, std::vector<double> &par) {
		vector<int> peaks = peaksDetectFisrtOrderZeroCrosssing(wf, 0.005, 3); //0.005 is set to 1/200 of the maximum waveform amplitude to avoid too small peaks.
		
		if (peaks.size() > 0) {
			vector<vector<int>> flexions = flexion_detect(wf, peaks);
			//cout << "after flexions_detect" << endl;

			//    vector<double> y_error;
				// Gaussian decomposition
			//vector<double> par; // amp, center, sigma
		//    if(intensityValueType != LidarProprietes::LIDAR_INTENSITY_NONE){ //0: only points(no need to create gaussian decomposition); 1: amplitude; 2: integral; 3: sigma; 4: solar signal; 5: all
			vector<double> y_error;
			vector<double> waveBinIndex;
			y_error.resize(wf.size());
			waveBinIndex.resize(wf.size());
			for (unsigned int i = 0; i < wf.size(); i++) {
				waveBinIndex[i] = i;
				//							*_wfdto.dStep;
				y_error[i] = 0.01;
			}

			for (unsigned int i = 0; i < peaks.size(); i++) {
				vector<double> sub_x(waveBinIndex.begin() + flexions[i][0], waveBinIndex.begin() + flexions[i][1]);
				vector<double> sub_y(wf.begin() + flexions[i][0], wf.begin() + flexions[i][1]);
				vector<double> comp_par = guess(sub_x, sub_y);
				
				par.push_back(comp_par[0]);
				par.push_back(comp_par[1]);
				par.push_back(comp_par[2]);
			}
			
			mp_par *paramConstraints = new mp_par[peaks.size() * 3 * sizeof(mp_par)];
			memset(paramConstraints, 0, peaks.size() * 3 * sizeof(mp_par));
			for (unsigned int i = 0; i < peaks.size(); i++) {
				int idx = i * 3;

				//integral
				paramConstraints[idx].fixed = false;
				paramConstraints[idx].limited[0] = true;
				paramConstraints[idx].limits[0] = 0.0;

				//center
				paramConstraints[idx + 1].fixed = false;
				paramConstraints[idx + 1].limited[0] = true;
				paramConstraints[idx + 1].limited[1] = true;
				paramConstraints[idx + 1].limits[0] = waveBinIndex[flexions[i][0]];
				paramConstraints[idx + 1].limits[1] = waveBinIndex[flexions[i][1]];

				//sigma
				paramConstraints[idx + 2].fixed = false;
				paramConstraints[idx + 2].limited[0] = true;
				paramConstraints[idx + 2].limits[0] = 0.0;

				//						cout<<"range..."<<endl;
				//						cout<<paramConstraints[idx + 0].fixed<<paramConstraints[idx + 0].limited[0]<<paramConstraints[idx + 0].limited[1]<<endl;
				//						cout<<paramConstraints[idx + 1].fixed<<paramConstraints[idx + 1].limited[0]<<paramConstraints[idx + 1].limited[1]<<endl;
				//						cout<<paramConstraints[idx + 2].fixed<<paramConstraints[idx + 2].limited[0]<<paramConstraints[idx + 2].limited[1]<<endl;
			}
			XYData xydata;
			xydata.x = waveBinIndex.data();
			xydata.y = wf.data();
			xydata.y_error = y_error.data();
			
			int status = mpfit(GaussianSum, waveBinIndex.size(), par.size(), par.data(), paramConstraints, 0, (void*)&xydata, 0);
			
			if (status <= 0) {
				cout << "Failed to perform Gaussian decomposition." << endl;
			}
		}
	}

	void addToBin(std::vector<Spectrum> &bin, const int &i, const Spectrum &w) {
		if (i >= m_numOfBins) {
			return;
		}
		bin[i] += w;
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
	size_t m_numOfBins;

	std::vector<double> m_pulse;

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
class PointCloudProcess : public ParallelProcess {
public:
	PointCloudProcess() : m_pos(0), m_numOfPulses(0) {}

	ref<WorkProcessor> createWorkProcessor() const {
		PointCloudWorkProcessor *processor = new PointCloudWorkProcessor();

		processor->m_sigmaSquareOfBeam = m_sigmaSquareOfBeam;
		processor->m_weightTotal = m_weightTotal;
		processor->m_cosFov = m_cosFov;
		processor->m_numOfBins = m_numOfBins;
		processor->m_pulse = m_pulse;

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
		PointCloudWorkUnit *wu = static_cast<PointCloudWorkUnit *>(unit);
		wu->set(m_x[m_pos], m_y[m_pos], m_z[m_pos], m_u[m_pos], m_v[m_pos], m_w[m_pos]);
		wu->m_i = m_pos;
		m_pos++;
		return ESuccess;
	}

	void processResult(const WorkResult *result, bool cancelled) {
		if (cancelled) {
			return;
		}

		const PointCloudWorkResult *wr = static_cast<const PointCloudWorkResult *>(result);

		for (auto& p : wr->m_points) {
			m_pointCloud.push(p);
		}
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

	void outputPointCloudToOneFile(std::string outName = "cloud.txt") {
		
		fs::path full_path(fs::initial_path());
		full_path = fs::system_complete(fs::path(m_scene->getDestinationFile().string(), fs::native));
		if (!fs::exists(full_path))
		{
			bool bRet = fs::create_directories(full_path);
			if (false == bRet)
			{
				cout << "output point cloud no dir" << endl;
			}
		}

		std::string folderPath = m_scene->getDestinationFile().string();
		std::ofstream fout(folderPath + "\\" + outName, std::ios::app);


		DiscretePoint p;
		while (m_pointCloud.try_pop(p)) {
			fout << p.x << "\t" << p.y << "\t" << p.z << "\t" << p.a << "\t" << p.i << endl;
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

	gdface::mt::threadsafe_queue<DiscretePoint> m_pointCloud;

	Float m_sigmaSquareOfBeam;
	Spectrum m_weightTotal;
	Float m_cosFov;
	size_t m_numOfBins;

	vector<double> m_pulse;

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

MTS_IMPLEMENT_CLASS(PointCloudWorkUnit, false, WorkUnit)
MTS_IMPLEMENT_CLASS(PointCloudWorkResult, false, WorkResult)
MTS_IMPLEMENT_CLASS_S(PointCloudWorkProcessor, false, WorkProcessor)
MTS_IMPLEMENT_CLASS(PointCloudProcess, false, ParallelProcess)

MTS_NAMESPACE_END
