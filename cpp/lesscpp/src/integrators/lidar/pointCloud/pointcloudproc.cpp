#include <boost/filesystem.hpp>
#include <boost/thread/locks.hpp>
#include <boost/thread/shared_mutex.hpp>

#include <mitsuba/core/sched.h>
#include <mitsuba/render/scene.h>
#include <vector>
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cstring>
#include <mitsuba/core/statistics.h>
#include <mitsuba/render/range.h>

#include "../lidarutils.h"
#include "../fftconv1d.cpp"

#include "../PulseGaussianFitting.h"
#include "../mpfit.h"
#include "../threadsafe_queue.h"
#include <numeric>



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
	short returnNum;
	short numberOfReturn;
	short bandIndex; // band index
	Float scanAngle;
	DiscretePoint() {}
	DiscretePoint(Float x, Float y, Float z, Float a, int i, int returnNum, int numberOfReturn, int bandIndex, Float scanAngle) : x(x), y(y), z(z), a(a), i(i),
		returnNum(returnNum), numberOfReturn(numberOfReturn), bandIndex(bandIndex), scanAngle(scanAngle){}

	inline void load(Stream* stream) {
		x = stream->readFloat();
		y = stream->readFloat();
		z = stream->readFloat();
		a = stream->readFloat();
		i = stream->readInt();
		returnNum = stream->readShort();
		numberOfReturn = stream->readShort();
		bandIndex = stream->readShort();
		scanAngle = stream->readFloat();
	}

	inline void save(Stream* stream) const {
		stream->writeFloat(x);
		stream->writeFloat(y);
		stream->writeFloat(z);
		stream->writeFloat(a);
		stream->writeInt(i);
		stream->writeShort(returnNum);
		stream->writeShort(numberOfReturn);
		stream->writeShort(bandIndex);
		stream->writeFloat(scanAngle);
	}
};

struct PulseRay {
	Float x;
	Float y;
	Float z;
	Float u;
	Float v;
	Float w;
	size_t index;
	PulseRay() {
		x = y = z = u = v = w = index = 0;
	}
	PulseRay(Float x, Float y, Float z, Float u, Float v, Float w, size_t index) :
		x(x), y(x), z(z), u(u), v(v), w(w), index(index) {}
};

struct WorkResultRecord {
	Float l;
	Spectrum w;
	WorkResultRecord() {}
	WorkResultRecord(Float l, Spectrum w) : l(l), w(w) {}
	inline void load(Stream* stream) {
		l = stream->readFloat();
		w = Spectrum(stream);
	}

	inline void save(Stream* stream) const {
		stream->writeFloat(l);
		w.serialize(stream);
	}
};

class PointCloudWorkUnit : public RangeWorkUnit {
public:
	void set(const WorkUnit *workUnit) {
		const PointCloudWorkUnit *wu = static_cast<const PointCloudWorkUnit *>(workUnit);
		setRange(wu->getRangeStart(), wu->getRangeEnd());
		m_pulses.resize(getSize());
		for (int i = 0; i < getSize(); i++) {
			PulseRay* pulseRay = new PulseRay();
			pulseRay->x = wu->m_pulses[i]->x;
			pulseRay->y = wu->m_pulses[i]->y;
			pulseRay->z = wu->m_pulses[i]->z;
			pulseRay->u = wu->m_pulses[i]->u;
			pulseRay->v = wu->m_pulses[i]->v;
			pulseRay->w = wu->m_pulses[i]->w;
			pulseRay->index = wu->m_pulses[i]->index;
			m_pulses[i] = pulseRay;
		}
	}

	void load(Stream *stream) {
		RangeWorkUnit::load(stream);
		m_pulses.resize(getSize());
		for (int i = 0; i < getSize(); i++) {
			PulseRay* pulseRay = new PulseRay();
			pulseRay->x = stream->readFloat();
			pulseRay->y = stream->readFloat();
			pulseRay->z = stream->readFloat();
			pulseRay->u = stream->readFloat();
			pulseRay->v = stream->readFloat();
			pulseRay->w = stream->readFloat();
			pulseRay->index = stream->readSize();
			m_pulses[i] = pulseRay;
		}
	}

	void save(Stream *stream) const {
		RangeWorkUnit::save(stream);
		for (int i = 0; i < m_pulses.size(); i++) {
			ref<PulseRay> pulse = m_pulses[i];
			stream->writeFloat(pulse->x);
			stream->writeFloat(pulse->y);
			stream->writeFloat(pulse->z);
			stream->writeFloat(pulse->u);
			stream->writeFloat(pulse->v);
			stream->writeFloat(pulse->w);
			stream->writeSize(pulse->index);
		}
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "PointCloudWorkUnit[" << "]";
		return oss.str();
	}

	inline Point getOrigin(size_t index) const {
		PulseRay* pulseRay = m_pulses[index];
		return Point(pulseRay->x, pulseRay->y, pulseRay->z);
	}

	inline Vector getDirection(size_t index) const {
		PulseRay* pulseRay = m_pulses[index];
		return Vector(pulseRay->u, pulseRay->v, pulseRay->w);
	}

	MTS_DECLARE_CLASS()

public:
	std::vector<PulseRay*> m_pulses;
};

/* ==================================================================== */
/*                           Work result impl.                          */
/* ==================================================================== */
class PointCloudWorkResult : public WorkResult {
public:
	PointCloudWorkResult() {
		m_range = new RangeWorkUnit();
	}

	void load(Stream *stream) {
		m_range->load(stream);
		m_points.resize(m_range->getSize(), std::vector<DiscretePoint*>(0));
		for (int i = 0; i < m_range->getSize(); i++) {
			int pointNumEachPulse = stream->readInt();
			for (int j = 0; j < pointNumEachPulse; j++) {
				DiscretePoint* p = new DiscretePoint();
				p->load(stream);
				m_points[i].push_back(p);
			}
		}

		m_records.resize(m_range->getSize(), std::vector<WorkResultRecord*>(0));
		for (int i = 0; i < m_range->getSize(); i++) {
			int recordNum = stream->readInt();
			for (int j = 0; j < recordNum; j++) {
				WorkResultRecord* p = new WorkResultRecord();
				p->load(stream);
				m_records[i].push_back(p);
			}
		}
	}

	void save(Stream *stream) const {
		m_range->save(stream);
		for (int i = 0; i < m_range->getSize(); i++) {
			stream->writeInt(m_points[i].size());
			for (int j = 0; j < m_points[i].size(); j++) {
				m_points[i][j]->save(stream);
			}
		}
		for (int i = 0; i < m_range->getSize(); i++) {
			stream->writeInt(m_records[i].size());
			for (int j = 0; j < m_records[i].size(); j++) {
				m_records[i][j]->save(stream);
			}
		}

	}

	std::string toString() const {
		std::ostringstream oss;
		return oss.str();
	}

	void init(size_t size) {
		m_records.clear();
		m_points.clear();
		m_points.resize(size, std::vector<DiscretePoint*>(0));
		m_records.resize(size, std::vector<WorkResultRecord*>(0)); //Reserve the array for each pulse
	}

	inline const RangeWorkUnit* getRangeWorkUnit() const {
		return m_range.get();
	}

	inline void setRangeWorkUnit(const RangeWorkUnit* range) {
		m_range->set(range);
	}

	void commit(Float length, Spectrum weight, size_t index) {
		m_records[index].push_back(new WorkResultRecord(length, weight));
	}

	MTS_DECLARE_CLASS()

public:
	ref<RangeWorkUnit> m_range;
	std::vector<std::vector<WorkResultRecord*>> m_records;
	std::vector<std::vector<DiscretePoint*>> m_points;
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

		m_sampler = static_cast<Sampler*>(getResource("sampler"));

		m_circleBeamSampler = new CircleBeamGridSampler(m_axialDivision);
		m_circleBeamSampler->generate();

		m_bin.resize(m_numOfBins);
	}

	void process(const WorkUnit *workUnit, WorkResult *workResult, const bool &stop) {
		const PointCloudWorkUnit *wu = static_cast<const PointCloudWorkUnit *>(workUnit);
		PointCloudWorkResult *wr = static_cast<PointCloudWorkResult *>(workResult);
		wr->setRangeWorkUnit(wu);
		wr->init(wu->getSize());
		for (size_t index = wu->getRangeStart(); index <= wu->getRangeEnd() && !stop; ++index) {
			size_t indexOfWR = index - wu->getRangeStart();
			Point pulseOrigin = wu->getOrigin(indexOfWR);
			Vector pulseDirection = wu->getDirection(indexOfWR);
			getWaveformResult(pulseOrigin, pulseDirection, wr, indexOfWR);// for each pulse waveform
			getPoints(pulseOrigin, pulseDirection, wr, indexOfWR, index);
		}
		

	}

	// not overrided methods

	void getWaveformResult(const Point& pulseOrigin, const Vector& pulseDirection, PointCloudWorkResult *wr,size_t indexOfWR) {

		m_convergence = getConvergencePoint(pulseOrigin, pulseDirection);
		m_rotateRayTransform = getRotateRayTransform(pulseDirection);
		while (m_circleBeamSampler->hasNext()) {
			Vector2 s = m_circleBeamSampler->next();
			Ray ray = generateRay(s, pulseOrigin);
			Spectrum w = Spectrum(gaussian(s.length(), m_sigmaSquareOfBeam)) / m_weightTotal * m_pulseEnergy;
			trace(pulseOrigin, pulseDirection, wr, ray, w, indexOfWR);
		}
		m_circleBeamSampler->reset();
	}

	void trace(const Point& pulseOrigin, const Vector& pulseDirection, PointCloudWorkResult *wr, Ray &ray, Spectrum w, size_t indexOfWR) {
		Intersection its;
		Float l = 0;
		//Spectrum r;

		for (int depth = 0; depth < m_maxDepth && m_scene->rayIntersect(ray, its); depth++) {
			const BSDF *bsdf = its.getBSDF();
			/*r = bsdf->getDiffuseReflectance(its);

			if (r.abs().average() < eps) {
				return;
			}*/
			record(pulseOrigin, pulseDirection, wr, its, l, w, indexOfWR, depth);
			// calculate new ray
			BSDFSamplingRecord bRec(its, m_sampler, EImportance);
			Spectrum bsdfWeight = bsdf->sample(bRec, m_sampler->next2D()); //bsdfWeight: 方向反射率
			if (bsdfWeight.min() < 0)  //incident on the back side
				break;
			l += its.t;
			w = w * bsdfWeight;
			ray.setOrigin(its.p);
			ray.setDirection(its.toWorld(bRec.wo));
		}
	}

	void record(const Point& pulseOrigin, const Vector& pulseDirection, PointCloudWorkResult *wr, const Intersection &its, const Float &l, 
		const Spectrum &w, size_t indexOfWR, int depth) {
		Ray ray;
		ray.setOrigin(its.p);
		ray.setDirection(normalize(pulseOrigin - its.p));

		Intersection shadowIts;
		if(depth > 0) m_scene->rayIntersect(ray, shadowIts);
		
		// if it is not blocked and in fov
		Vector vectorFromConvergence = normalize(its.p - m_convergence);
		Vector wiWorld = its.shFrame.toWorld(its.wi);
		if (((pulseOrigin) - its.p).length() < shadowIts.t
			&& dot(vectorFromConvergence, pulseDirection) > m_cosFov) {
			// calculate path length and weight
			Vector v = pulseOrigin - its.p;
			Float d = v.length();
			Float solidAngle = m_area / (d * d) * (dot(-pulseDirection, normalize(v)));

			Float length = l + its.t + d;
			const BSDF* bsdf = its.getBSDF();
			BSDFSamplingRecord bRec(its, its.toLocal(normalize(v)), EImportance);
			Spectrum weight = solidAngle * bsdf->eval(bRec) * w;

			wr->commit(length, weight, indexOfWR);

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

	Ray generateRay(const Vector2 &s, const Point &Origin) {
		const Float d = 10000;
		Float t = d * tan(m_fov);
		Point p = Point(s.x * t, -d, s.y * t);

		p = m_rotateRayTransform.transformAffine(p);

		Ray ray;
		ray.setOrigin(Origin);
		ray.setDirection(normalize(Vector(p)));

		return ray;
	}

	/// <summary>
	/// The convergence point of the lidar detection sensor
	/// </summary>
	/// <param name="wu"></param>
	/// <param name="indexInWR"></param>
	/// <returns></returns>
	Point getConvergencePoint(const Point& pulseOrigin, const Vector& pulseDirection) {
		Float r = sqrt(m_area * INV_PI);
		Point c = pulseOrigin - pulseDirection * (r / tan(m_fov));

		return c;
	}

	Transform getRotateRayTransform(const Vector& pulseDirection) {
		Transform t;
		Float degree;
		Vector z(0, -1, 0);
		Vector axis = cross(z, pulseDirection);
		if (pulseDirection.x == 0 && pulseDirection.y == 1 && pulseDirection.z == 0) {
			axis = Vector(1, 0, 0);
		}
		if (abs(dot(axis, axis)) > 0) {
			degree = acos(dot(pulseDirection, z));
			degree = radToDeg(degree);
			t = Transform::rotate(axis, degree);
		}
		return t;
	}

	void getPoints(const Point& pulseOrigin, const Vector& pulseDirection, PointCloudWorkResult *wr, 
		size_t indexOfWR, size_t indexOfPulse) {

		// If this pulse does not have any records,e.g, pointing to the sky, we skip it
		if (wr->m_records[indexOfWR].size() == 0) {
			return;
		}
		std::fill(m_bin.begin(), m_bin.end(), Spectrum(0.0));
		int idx;
		int minIdx= numeric_limits<int>::max(), maxIdx = -numeric_limits<int>::max();
		for (const WorkResultRecord* r : wr->m_records[indexOfWR]) {
			idx = (int)((r->l - 2.0 * m_minRange) / (C * m_rate));
			if (idx >= 0 && idx < m_numOfBins) {
				if (idx > maxIdx) maxIdx = idx;
				if (idx < minIdx) minIdx = idx;
				addToBin(m_bin, idx, r->w);
			}
		}
		// If non records exist in the valid range, i.e., [min_range, max_range], we skip it
		if (minIdx == numeric_limits<int>::max())
			return;

		//clear records to save memory, because the following does not need it anymore
		std::vector<WorkResultRecord*>().swap(wr->m_records[indexOfWR]);

		if (m_echoDetectionMode == 1) {
			naivePointDetectionForTLS(pulseOrigin, pulseDirection, wr, indexOfWR, indexOfPulse, 0, minIdx, maxIdx);
			return;
		}

		//Hyperspectral Lidar
		Float scanAngle = acos(dot(pulseDirection, Vector(0, -1, 0))) / M_PI_DBL * 180;
		if (scanAngle != 0) {
			Vector2 d_2d = normalize(Vector2(pulseDirection[0], pulseDirection[2]));
			Float scanAziAngle = acos(d_2d[1]) / M_PI_DBL * 180;
			if (d_2d[0] > 0)
				scanAziAngle = 360 - scanAziAngle;
			if ((scanAziAngle - m_centerAzimuth) < 0 || (scanAziAngle - m_centerAzimuth) > 180) {
				scanAngle = -scanAngle;
			}
		}
		for (int k = 0; k < SPECTRUM_SAMPLES; k++) {
			// BEGIN: get point cloud from accumulation
			// 1. convolve
			int pulse_size = m_pulse.size();
			int acc_size = (maxIdx - minIdx) + 1 + 2 * pulse_size;
			std::vector<double> accumulation(acc_size);
			//cout << "accum" << endl;
			bool isAllZero = true;
			for (int i = minIdx; i <= maxIdx; ++i) {
				Float intensity = m_bin[i][k];
				if (intensity > 0) isAllZero = false;
				accumulation[i - minIdx + pulse_size] = intensity;
			}
			if (isAllZero) { //When all intensity is zero, no longer to do the following
				continue;
			}

			std::vector<double> waveform = conv(accumulation, m_pulse);
			// 2. gaussian decomposition
			std::vector<double> par;  // amp(积分能量), center, sigma
			gaussianDecomposition(waveform, par);

			// 3. output point cloud
			int numReturns = par.size() / 3;

			//maxmum number of returns can be recorded is set to 5, if larger than this value, remove some returns with less energy
			if (numReturns > 5) {  
				std::vector<int> V(numReturns);
				std::iota(V.begin(), V.end(), 0); //Initializing
				std::vector<double> energy;
				for (int i = 0; i < numReturns; i++) {
					energy.push_back(par[i * 3]);
				}
				sort(V.begin(), V.end(), [&](int i, int j) {return energy[i] < energy[j]; });
				std::vector<int> subV(V.begin() + numReturns - 5, V.end());
				std::vector<double> tmp = par;
				par.clear();
				for (int i = 0; i < numReturns; i++) {
					if (std::find(subV.begin(), subV.end(), i) != subV.end()) {
						par.push_back(tmp[i * 3]);
						par.push_back(tmp[i * 3 + 1]);
						par.push_back(tmp[i * 3 + 2]);
					}
				}
				numReturns = 5;
			}

			Float step = C * m_rate * 0.5;
			Float a;
			Float t;
			Point o = pulseOrigin;
			Vector d = pulseDirection;
			Point p;
			for (int i = 0; i < numReturns; i++) {
				//a = par[i * 3] / (sqrt(2 * M_PI) * par[i * 3 + 2]);//振幅
				a = par[i * 3];//能量积分
				t = m_minRange + (par[i * 3 + 1]-pulse_size+ minIdx) * step;
				p = o + d * t;
				wr->m_points[indexOfWR].push_back(new DiscretePoint(p.x, p.y, p.z, a, indexOfPulse, i + 1, numReturns, k+1, scanAngle));
			}
		}
		
		//single band

		// BEGIN: get point cloud from accumulation

		//// 1. convolve
		//std::vector<double> accumulation(m_bin.size());
		////cout << "accum" << endl;
		//bool isAllZero = true;
		//for (int i = 0; i < m_bin.size(); ++i) {
		//	Float intensity = m_bin[i][0];
		//	if (intensity > 0) isAllZero = false;
		//	accumulation[i] = intensity;  // TODO
		//}

		//if (isAllZero) { //When all intensity is zero, no longer to do the following
		//	return;
		//}

		//std::vector<double> waveform = conv(accumulation, m_pulse);

		//// 2. gaussian decomposition
		//std::vector<double> par;  // amp, center, sigma
		//gaussianDecomposition(waveform, par);

		//// 3. output point cloud
		//Float step = C * m_rate * 0.5;
		//Float a;
		//Float t;
		//Point o = pulseOrigin;
		//Vector d = pulseDirection;
		//Point p;
		//for (int i = 0; 3 * i < par.size(); i++) {
		//	//a = par[i * 3] / (sqrt(2 * M_PI) * par[i * 3 + 2]);//振幅
		//	//a = sqrt(2 * M_PI)* par[i * 3] * par[i * 3 + 2];//能量积分
		//	t = m_minRange + (par[i * 3 + 1]) * step;
		//	p = o + d * t;
		//	wr->m_points[indexOfWR].push_back(new DiscretePoint(p.x, p.y, p.z, a, indexOfPulse,i+1, par.size()/3));
		//}
		//// END: get point cloud from accumulation
	}

	void naivePointDetectionForTLS(const Point& pulseOrigin, const Vector& pulseDirection, PointCloudWorkResult* wr,
		size_t indexOfWR, size_t indexOfPulse, Float energyLevel, int minIdx, int maxIdx) {
		Float maxEnergy = 0;
		int maxPos = 0;
		for (int i = minIdx; i <= maxIdx; i++) {
			if (m_bin[i][0] > maxEnergy) {
				maxEnergy = m_bin[i][0];
				maxPos = i;
			}
		}
		if (maxEnergy > 0) {
			Float step = C * m_rate * 0.5;
			Float a;
			Float t;
			Point o = pulseOrigin;
			Vector d = pulseDirection;
			Point p;
			a = m_bin[maxPos][0];
			t = m_minRange + (maxPos + 0.5) * step;
			if (t > m_maxRange) return;
			p = o + d * t;
			Float scanAngle = acos(dot(d, Vector(0, -1, 0))) / M_PI_DBL * 180;
			Vector2 d_2d = normalize(Vector2(d[0], d[2]));
			Float scanAziAngle = acos(d_2d[1]) / M_PI_DBL * 180;
			if (d_2d[0] > 0)
				scanAziAngle = 360 - scanAziAngle;
			if ((scanAziAngle - m_centerAzimuth) < 0 || (scanAziAngle - m_centerAzimuth) > 180) {
				scanAngle = - scanAngle;
			}
			wr->m_points[indexOfWR].push_back(new DiscretePoint(p.x, p.y, p.z, a, indexOfPulse,1,1,1, scanAngle));
		}
		
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
			vector<double> comp_par;
			for (unsigned int i = 0; i < peaks.size(); i++) {
				vector<double> sub_x(waveBinIndex.begin() + flexions[i][0], waveBinIndex.begin() + flexions[i][1]);
				vector<double> sub_y(wf.begin() + flexions[i][0], wf.begin() + flexions[i][1]);
				comp_par = guess(sub_x, sub_y);
				
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
			delete[] paramConstraints;
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

	ref<CircleBeamGridSampler> m_circleBeamSampler;

	// parameter

	Float m_sigmaSquareOfBeam;
	Spectrum m_weightTotal;
	Float m_cosFov;
	size_t m_numOfBins;
	std::vector<Spectrum> m_bin;

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
	int m_echoDetectionMode;
	Float m_centerAzimuth;
	ref<Sampler> m_sampler;
};

/* ==================================================================== */
/*                        Parallel process impl.                        */
/* ==================================================================== */
class PointCloudProcess : public ParallelProcess {
public:
	PointCloudProcess() : m_pos(0), m_numOfPulses(0){}

	//Setup progressReporter
	void setupProgressReporter(const std::string& progressText, size_t numPulses, const void* progressReporterPayload) {
		/* Create a visual progress reporter */
		m_receivedResultCount = 0;
		m_progress = new ProgressReporter(progressText, numPulses,
			progressReporterPayload);
		m_resultMutex = new Mutex();
		m_minIntensity = numeric_limits<int>::max();
	}

	void increaseResultCount(size_t resultCount) {
		LockGuard lock(m_resultMutex);
		m_receivedResultCount += resultCount;
		m_progress->update(m_receivedResultCount);
	}

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
		processor->m_echoDetectionMode = m_echoDetectionMode;
		processor->m_centerAzimuth = m_centerAzimuth;
		return processor;
	}

	EStatus generateWork(WorkUnit *unit, int worker) {
		PointCloudWorkUnit* wu = static_cast<PointCloudWorkUnit*>(unit);
		size_t workUnitSize;
		if (m_numGeneratedPulses == m_numOfPulses) {
			return EFailure;
		}
		workUnitSize = std::min(m_granularityPulses, m_numOfPulses - m_numGeneratedPulses);
		wu->setRange(m_numGeneratedPulses, m_numGeneratedPulses + workUnitSize - 1);
		wu->m_pulses.resize(workUnitSize);
		for (int i = wu->getRangeStart(); i <= wu->getRangeEnd(); i++) {
			PulseRay* pulseRay = new PulseRay();
			pulseRay->x = m_x[i];
			pulseRay->y = m_y[i];
			pulseRay->z = m_z[i];
			pulseRay->u = m_u[i];
			pulseRay->v = m_v[i];
			pulseRay->w = m_w[i];
			pulseRay->index = i;
			wu->m_pulses[i - wu->getRangeStart()] = pulseRay;
		}
		m_numGeneratedPulses += workUnitSize;
		return ESuccess;
	}

	void processResult(const WorkResult *result, bool cancelled) {
		if (cancelled) {
			return;
		}
		const PointCloudWorkResult *wr = static_cast<const PointCloudWorkResult *>(result);
		const RangeWorkUnit* range = wr->getRangeWorkUnit();

		LockGuard lock(m_resultMutex);
		increaseResultCount(range->getSize());
		for (int i = 0; i < range->getSize(); i++) {
			std::vector<DiscretePoint*> points = wr->m_points[i];
			for (int j = 0; j < points.size(); j++) {
				DiscretePoint* point = points[j];
				DiscretePoint p(point->x, point->y, point->z, point->a, point->i, point->returnNum, point->numberOfReturn,
					point->bandIndex, point->scanAngle);
				if(point->a > 0)
					if (point->a < m_minIntensity) m_minIntensity = point->a;
				m_pointCloud.push(p);
			}
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

		//Determine scale for intensity
		Float intensity_scale = 1;
		int scale_times = 0;
		if (m_minIntensity < 0.01) {
			while (true) {
				
				intensity_scale *= 10;
				m_minIntensity *= 10;
				scale_times += 1;
				if (m_minIntensity >= 1.0) {
					break;
				}
			}
		}

		DiscretePoint p;
		fout << "         X          Y          Z PulseIndex BandIndex ReturnNum NumReturns ScanAngle     Intensity(e-" << scale_times <<")"<< endl;
		while (m_pointCloud.try_pop(p)) {
			fout << std::fixed << std::setprecision(4) << std::setw(10) << 0.5 * m_sceneXSzie - p.x << " " <<
				std::fixed << std::setprecision(4) << std::setw(10) << 0.5 * m_sceneZSize - p.z << " " <<
				std::fixed << std::setprecision(4) << std::setw(10) << p.y << " " <<
				std::fixed << std::setprecision(4) << std::setw(10) << p.i+ m_batchStartIndex <<
				std::fixed << std::setprecision(4) << std::setw(10) << p.bandIndex <<
				std::fixed << std::setprecision(4) << std::setw(10) << p.returnNum << 
				std::fixed << std::setprecision(4) << std::setw(11) << p.numberOfReturn<<
				std::fixed << std::setprecision(4) << std::setw(10) << p.scanAngle <<
				std::setprecision(5) << std::scientific << std::setw(20) << p.a* intensity_scale << endl;
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

	Float m_minIntensity;

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

	//Progressbar
	ProgressReporter* m_progress;
	ref<Mutex> m_resultMutex;
	size_t m_receivedResultCount;

	Float m_sceneXSzie;
	Float m_sceneZSize;
	int m_batchStartIndex;//start index of the batchfile

	Spectrum m_wavelengths;

	size_t m_numGeneratedPulses;
	size_t m_granularityPulses;

	int m_echoDetectionMode;
	Float m_centerAzimuth;
};

MTS_IMPLEMENT_CLASS(PointCloudWorkUnit, false, WorkUnit)
MTS_IMPLEMENT_CLASS(PointCloudWorkResult, false, WorkResult)
MTS_IMPLEMENT_CLASS_S(PointCloudWorkProcessor, false, WorkProcessor)
MTS_IMPLEMENT_CLASS(PointCloudProcess, false, ParallelProcess)

MTS_NAMESPACE_END
