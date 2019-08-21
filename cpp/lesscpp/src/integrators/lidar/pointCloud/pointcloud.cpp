#include <boost/interprocess/file_mapping.hpp>
#include <boost/interprocess/mapped_region.hpp>

#include <cmath>
#include <iostream>
#include <mitsuba/render/scene.h>
#include "pointcloudproc.cpp"
#include "../lidarutils.h"

MTS_NAMESPACE_BEGIN

class PointCloud : public Integrator {
public:
	PointCloud(const Properties &props) : Integrator(props) {
		m_maxDepth = props.getInteger("maxOrder", 2);
		m_axialDivision = props.getInteger("axialDivision", 100);
		m_fractionAtRadius = props.getFloat("fractionAtRadius", 0.368);
		m_fp = props.getFloat("footprintHalfAngle", 0.0012);
		m_fov = props.getFloat("halfFov", 0.0015);
		m_pulseEnergy = props.getFloat("pulseEnergy", 1e-3);
		m_rate = props.getFloat("acquisitionPeriod", 1);
		m_rate *= 1e-9;  // ns
		m_area = props.getFloat("sensorArea", 0.1);

		m_numOfSigma = props.getFloat("halfDurationNumberOfSigma", 3);
		m_durationAtRelativePower = props.getFloat("halfPulseDurationAtHalfPeak", 2);
		
		m_minRange = props.getFloat("minRange", 40);
		m_maxRange = props.getFloat("maxRange", 60);

		m_batchFile = props.getString("batchFile", "");
	}

	PointCloud(Stream *stream, InstanceManager *manager)
		: Integrator(stream, manager) {
		m_maxDepth = stream->readInt();
		m_axialDivision = stream->readInt();
		m_fractionAtRadius = stream->readFloat();
		m_fp = stream->readFloat();
		m_fov = stream->readFloat();
		m_pulseEnergy = stream->readFloat();
		m_rate = stream->readFloat();
		m_area = stream->readFloat();
		m_numOfSigma = stream->readFloat();
		m_durationAtRelativePower = stream->readFloat();
		m_minRange = stream->readFloat();
		m_maxRange = stream->readFloat();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Integrator::serialize(stream, manager);
		stream->writeInt(m_maxDepth);
		stream->writeInt(m_axialDivision);
		stream->writeFloat(m_fractionAtRadius);
		stream->writeFloat(m_fp);
		stream->writeFloat(m_fov);
		stream->writeFloat(m_pulseEnergy);
		stream->writeFloat(m_rate);
		stream->writeFloat(m_area);
		stream->writeFloat(m_numOfSigma);
		stream->writeFloat(m_durationAtRelativePower);
		stream->writeFloat(m_minRange);
		stream->writeFloat(m_maxRange);
	}

	bool preprocess(const Scene *scene, RenderQueue *queue, const RenderJob *job,
		int sceneResID, int sensorResID, int samplerResID) {
		Integrator::preprocess(scene, queue, job, sceneResID, sensorResID, samplerResID);

		Scheduler *sched = Scheduler::getInstance();

		// auxiliary
		m_sigmaSquareOfBeam = -0.5 / std::log(m_fractionAtRadius);
		m_weightTotal = calculateTotalWeight(m_axialDivision, m_sigmaSquareOfBeam);
		m_cosFov = cos(m_fov);
		m_numOfBins = (int)(2 * (m_maxRange - m_minRange) / (C * m_rate)) + 1;

		return true;
	}

	void cancel() {
		Scheduler::getInstance()->cancel(m_process);
	}

	bool render(Scene *scene, RenderQueue *queue,
		const RenderJob *job, int sceneResID, int sensorResID, int samplerResID) {

		ref<Scheduler> scheduler = Scheduler::getInstance();
		ref<PointCloudProcess> process = new PointCloudProcess();
		m_scene = static_cast<Scene *>(Scheduler::getInstance()->getResource(sceneResID));
		configureProcess(process);
		int numOfPulses = generatePulsesConfiguration(process);
		process->m_numOfPulses = numOfPulses;
		
		process->bindResource("scene", sceneResID);
		scheduler->schedule(process);
		m_process = process;

		scheduler->wait(process);
		
		process->outputPointCloudToOneFile(m_batchFile + ".txt");
		m_process = NULL;

		return process->getReturnStatus() == ParallelProcess::ESuccess;
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "PointCloud[" << endl
			<< "  maxDepth = " << m_maxDepth << "," << endl
		
			<< "]";
		return oss.str();
	}

	// not overrided methods
	inline void configureProcess(ParallelProcess *process) {
		PointCloudProcess *proc = static_cast<PointCloudProcess *>(process);

		proc->m_sigmaSquareOfBeam = m_sigmaSquareOfBeam;
		proc->m_weightTotal = m_weightTotal;
		proc->m_cosFov = m_cosFov;
		proc->m_numOfBins = m_numOfBins;

		proc->m_pulse = getPulse(m_numOfSigma, m_durationAtRelativePower, m_rate);

		// from XML
		proc->m_maxDepth = m_maxDepth;
		proc->m_axialDivision = m_axialDivision;

		proc->m_fp = m_fp;
		proc->m_fov = m_fov;
		proc->m_pulseEnergy = m_pulseEnergy;
		proc->m_rate = m_rate;
		proc->m_area = m_area;
		proc->m_minRange = m_minRange;
		proc->m_maxRange = m_maxRange;

		proc->m_outputPath = m_outputPath;

	}

	int generatePulsesConfiguration(PointCloudProcess *process) {
		return batchAddPulseFromFileUsingBoostFileMap(process);
	}

	int batchAddPulseFromFileUsingBoostFileMap(PointCloudProcess *process) {
		float x;
		float y;
		float z;
		float u;
		float v;
		float w;

		std::string  batchFilePath;
		
		if (m_batchFile == "") {
			fs::path path = m_scene->getSourceFile();
			path = path.parent_path() / "lidarbatch.txt";
			if (!fs::exists(path))
			{
				cout << "no geometry configuration file" << endl;
			}
			batchFilePath = path.string();
		}
		else {
			fs::path path = m_scene->getSourceFile();
			path = path.parent_path() / "lidarbatch" / m_batchFile;
			batchFilePath = path.string();
			
		}

		boost::interprocess::file_mapping file(batchFilePath.c_str(), boost::interprocess::read_write);
		boost::interprocess::mapped_region region(file, boost::interprocess::read_write);

		void *lpMapAddress = region.get_address();
		size_t size = region.get_size();

		int cnt = 0;
		std::stringstream ss((char *)lpMapAddress);
		while (ss >> x >> y >> z >> u >> v >> w) {
			process->addGeometryConfiguration(x, y, z, u, v, w);
			cnt++;
		}
		return cnt;
	}

	Spectrum calculateTotalWeight(int n, Float sigmaSquare) {
		Spectrum w(0.);
		Float r;
		CircleBeamGridSampler s(n);
		Vector2 v;
		while (s.hasNext()) {
			v = s.next();
			
			r = v.length();
			if (r > 1.0) {
				continue;
			}
			w += Spectrum(gaussian(r, sigmaSquare));
		}
		return w;
	}

	std::vector<double> getPulse(Float numberOfSigma, Float durationAtRelativePower, Float acquisitionRate) {
		Float relativePower = 0.5;
		Float sigmaPulse = durationAtRelativePower / sqrt(2.0) / sqrt(-log(relativePower));
		size_t n = (size_t)(round(2 * numberOfSigma * sigmaPulse / (acquisitionRate * 1e9) - 1) / 2);

		vector<double> pulse(2 * n + 1);

		Float d = numberOfSigma * sigmaPulse / n;
		Float s = 0;
		for (int i = 0; i < 2 * n + 1; i++) {
			pulse[i] = gaussian(-numberOfSigma * sigmaPulse + d * i, sigmaPulse * sigmaPulse);
			s += pulse[i];
		}

		return pulse;
	}

	MTS_DECLARE_CLASS()
protected:
	ref<ParallelProcess> m_process;
	ref<Scene> m_scene;

	Float m_sigmaSquareOfBeam;
	Spectrum m_weightTotal;
	Float m_cosFov;
	int m_numOfBins;
	// following from XML
	int m_maxDepth;
	int m_axialDivision;
	Float m_fractionAtRadius;
	Float m_fp;
	Float m_fov;
	Float m_pulseEnergy;
	Float m_rate;
	Float m_area;
	Float m_minRange;
	Float m_maxRange;

	Float m_numOfSigma;
	Float m_durationAtRelativePower;

	std::string m_batchFile;
	std::string m_outputPath;
};

MTS_IMPLEMENT_CLASS_S(PointCloud, false, Integrator)
MTS_EXPORT_PLUGIN(PointCloud, "Multi pulse waveform, output point clouds");
MTS_NAMESPACE_END
