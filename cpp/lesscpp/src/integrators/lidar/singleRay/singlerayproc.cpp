#include <boost/filesystem.hpp>

#include <mitsuba/core/sched.h>
#include <mitsuba/render/scene.h>
#include <mitsuba/render/range.h>
#include <vector>
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <mitsuba/core/statistics.h>

#include "../threadsafe_queue.h"



MTS_NAMESPACE_BEGIN

namespace singleRay {

	const Spectrum NO_INTERSECTION = Spectrum(-1.0);

	struct DiscretePoint {
		Float x;
		Float y;
		Float z;
		Spectrum a;
		int i;
		std::string name;
		DiscretePoint() {}
		DiscretePoint(Float x, Float y, Float z, Spectrum a, int i, std::string name) : x(x), y(y), z(z), a(a), i(i), name(name) {}

		inline void load(Stream* stream) {
			x = stream->readFloat();
			y = stream->readFloat();
			z = stream->readFloat();
			a = Spectrum(stream);
			i = stream->readInt();
			name = stream->readString();
		}

		inline void save(Stream* stream) const {
			stream->writeFloat(x);
			stream->writeFloat(y);
			stream->writeFloat(z);
			a.serialize(stream);
			stream->writeInt(i);
			stream->writeString(name);
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

	class WaveformWorkUnit;
	class WaveformWorkResult;
	class WaveformWorkProcessor;
	class WaveformProcess;

	class WaveformWorkUnit : public RangeWorkUnit {
	public:
		void set(const WorkUnit *workUnit) {
			const WaveformWorkUnit *wu = static_cast<const WaveformWorkUnit *>(workUnit);
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
			oss << "WaveformWorkUnit[" << "]";
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
	class WaveformWorkResult : public WorkResult {
	public:

		WaveformWorkResult() {
			m_range = new RangeWorkUnit();
		}
		void load(Stream *stream) {
			m_range->load(stream);
			m_pointCloud.resize(m_range->getSize());
			for (int i = 0; i < m_range->getSize(); i++) {
				DiscretePoint* p = new DiscretePoint();
				p->load(stream);
			}
		}

		void save(Stream *stream) const {
			m_range->save(stream);
			for (int i = 0; i < m_range->getSize(); i++) {
				m_pointCloud[i]->save(stream);
			}
		}

		inline const RangeWorkUnit* getRangeWorkUnit() const {
			return m_range.get();
		}

		inline void setRangeWorkUnit(const RangeWorkUnit* range) {
			m_range->set(range);
		}

		std::string toString() const {
			std::ostringstream oss;
			return oss.str();
		}

		MTS_DECLARE_CLASS()

	public:
		ref<RangeWorkUnit> m_range;
		std::vector<DiscretePoint*> m_pointCloud;
	};

	/* ==================================================================== */
	/*                         Work processor impl.                         */
	/* ==================================================================== */
	class WaveformWorkProcessor : public WorkProcessor {
	public:
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
			wr->setRangeWorkUnit(wu);
			wr->m_pointCloud.clear();
			wr->m_pointCloud.resize(wu->getSize());
			for (size_t index = wu->getRangeStart(); index <= wu->getRangeEnd() && !stop; ++index) {
				size_t indexOfWR = index - wu->getRangeStart();
				wr->m_pointCloud[indexOfWR] = new DiscretePoint();
				getPoint(wu, wr, indexOfWR, index);
			}
		}

		// not override methods

		void getPoint(const WaveformWorkUnit *wu, WaveformWorkResult *wr, size_t indexOfWR, size_t indexOfRange) {
			Ray ray;
			ray.setOrigin(wu->getOrigin(indexOfWR));
			ray.setDirection(wu->getDirection(indexOfWR));

			Intersection its;
			if (!m_scene->rayIntersect(ray, its)) {
				wr->m_pointCloud[indexOfWR]->a = NO_INTERSECTION;
				return;
			}
			else {
				if (its.t < m_minRange || its.t > m_maxRange) {
					wr->m_pointCloud[indexOfWR]->a = NO_INTERSECTION;
					return;
				}	
			}

			// TODO: intensity
			const BSDF *bsdf = its.getBSDF();
			Vector v = ray.o - its.p;
			Float d = v.length();
			Float solidAngle = m_area / (d * d);
			BSDFSamplingRecord bRec(its, its.toLocal(normalize(v)), EImportance);
			Spectrum weight = solidAngle * bsdf->eval(bRec) * m_pulseEnergy;
			//Spectrum weight = m_pulseEnergy*solidAngle * its.getBSDF()->getDiffuseReflectance(its) * INV_PI * absDot(normalize(v), its.shFrame.n);

			wr->m_pointCloud[indexOfWR]->i = indexOfRange;
			wr->m_pointCloud[indexOfWR]->a = weight;
			wr->m_pointCloud[indexOfWR]->x = its.p.x;
			wr->m_pointCloud[indexOfWR]->y = its.p.y;
			wr->m_pointCloud[indexOfWR]->z = its.p.z;
			std::string compName = its.shape->getName();
			if (its.instance) {
				compName = its.instance->getName() + "_" + compName;
			}
			wr->m_pointCloud[indexOfWR]->name = compName;
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
		WaveformProcess() : m_pos(0), m_numOfPulses(0){}
		~WaveformProcess() {
			delete m_progress;
		}

		//Setup progressReporter
		void setupProgressReporter(const std::string& progressText, size_t numPulses,const void* progressReporterPayload) {
			/* Create a visual progress reporter */
			m_receivedResultCount = 0;
			m_progress = new ProgressReporter(progressText, numPulses,
				progressReporterPayload);
			m_resultMutex = new Mutex();
		}

		void increaseResultCount(size_t resultCount) {
			LockGuard lock(m_resultMutex);
			m_receivedResultCount += resultCount;
			m_progress->update(m_receivedResultCount);
		}

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
			WaveformWorkUnit* wu = static_cast<WaveformWorkUnit*>(unit);
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
				wu->m_pulses[i- wu->getRangeStart()] = pulseRay;
			}
			m_numGeneratedPulses += workUnitSize;
			return ESuccess;
		}

		void processResult(const WorkResult *result, bool cancelled) {
			if (cancelled) {
				return;
			}

			const WaveformWorkResult *wr = static_cast<const WaveformWorkResult *>(result);
			const RangeWorkUnit* range = wr->getRangeWorkUnit();

			LockGuard lock(m_resultMutex);
			increaseResultCount(range->getSize());

			for (int i = 0; i < range->getSize(); i++){
				const DiscretePoint* point = wr->m_pointCloud[i];
				if (point->a != NO_INTERSECTION) {
					DiscretePoint p(point->x, point->y, point->z, point->a, point->i, point->name);
					//if (point->a > m_maxIntensity) m_maxIntensity = point->a;
					//if (point->a < m_minIntensity) m_minIntensity = point->a;
					m_points.push(p);
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

			DiscretePoint p;
			fout << "         X          Y          Z PulseIndex";
			for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
				fout << "        Intensity(" << m_wavelengths[i]<<")";
			}
			fout << "     Name(OBJName_InstanceID_ComponentName)" << endl;
			while (m_points.try_pop(p)) {
				fout << std::fixed << std::setprecision(4) << std::setw(10) << 0.5 * m_sceneXSzie - p.x << " " <<
					std::fixed << std::setprecision(4) << std::setw(10) << 0.5 * m_sceneZSize - p.z << " " <<
					std::fixed << std::setprecision(4) << std::setw(10) << p.y << " " <<
					std::fixed << std::setprecision(4) << std::setw(10) << p.i + m_batchStartIndex << " ";
					for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
						fout<< std::setprecision(5)<< std::scientific << std::setw(20)<< p.a[i] << " ";
					}
					fout<<"     "<<p.name << endl;
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
		gdface::mt::threadsafe_queue<DiscretePoint> m_points;
		//Float m_maxIntensity, m_minIntensity;

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

		//Progressbar
		ProgressReporter* m_progress;
		ref<Mutex> m_resultMutex;
		size_t m_receivedResultCount;

		Float m_sceneXSzie;
		Float m_sceneZSize;
		size_t m_numGeneratedPulses;
		size_t m_granularityPulses;

		Spectrum m_wavelengths;

		int m_batchStartIndex;//start index of the batchfile
	};

	MTS_IMPLEMENT_CLASS(WaveformWorkUnit, false, WorkUnit)
	MTS_IMPLEMENT_CLASS(WaveformWorkResult, false, WorkResult)
	MTS_IMPLEMENT_CLASS_S(WaveformWorkProcessor, false, WorkProcessor)
	MTS_IMPLEMENT_CLASS(WaveformProcess, false, ParallelProcess)
}
MTS_NAMESPACE_END
