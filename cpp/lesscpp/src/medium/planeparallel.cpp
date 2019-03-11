// implementing a plane parallel medium

#include <mitsuba/render/scene.h>
#include <mitsuba/core/plugin.h>
#include <string> 
using namespace std;

//#define QI_DEBUG

MTS_NAMESPACE_BEGIN
class PlaneParallelMedium : public Medium {
public:

	enum EPointPosition {
		EBelowMedium=-2,   /// point is below medium
		EUpperMedium=-1,   /// point is upper medium
	};

	PlaneParallelMedium(const Properties &props)
		: Medium(props) {
		std::string layerThicknessStr = props.getString("layerThickness", "");
		std::vector<std::string> layerThickness =
			tokenize(layerThicknessStr, " ,;");
		if (layerThickness.size() == 0)
			Log(EError, "No layterThickness were supplied!");
		m_layerThickness.resize(layerThickness.size());

		char *end_ptr = NULL;
		for (int i = 0; i<layerThickness.size(); ++i) {
			double thickness = (double)strtod(layerThickness[i].c_str(), &end_ptr);
			if (*end_ptr != '\0')
				SLog(EError, "Could not parse the layer thickness!");
			if (thickness < 0)
				SLog(EError, "Invalid layer thickness!");
			m_layerThickness[i] = thickness;
		}
		
		m_startAltitude = props.getFloat("startAltitude", 0);

		m_numLayers = (int)m_layerThickness.size();

		m_currentSampledLayer = 0;

		//load sigmaT and albedo
		for (int i = 0; i < m_numLayers; i++) {
			std::string sigmaT_layerName = "singmaT_layer" + std::to_string(i+1);
			std::string albedo_layerName = "albedo_layer" + std::to_string(i + 1);
			Spectrum singmaT = props.getSpectrum(sigmaT_layerName, Spectrum(0.0));
			if (singmaT.isZero())
				singmaT = Spectrum(1e-12);
			m_layerSigmaT.push_back(singmaT);
			Spectrum albedo = props.getSpectrum(albedo_layerName, Spectrum(0.0));
			if (albedo.isZero())
				albedo = Spectrum(1e-12);
			m_layerAlbedo.push_back(albedo);
			m_layerSigmaS.push_back(singmaT*albedo);

			string phaseweightName = "phasefunc_weights_layer" + std::to_string(i + 1);
			string layerPhaseWeights = props.getString(phaseweightName, "0.5,0.5");
			string phasegName = "phasefunc_g_value_layer" + std::to_string(i + 1);
			Spectrum phase_g = props.getSpectrum(phasegName, Spectrum(0.0));

			string phaseSampledIndexName = "phasefunc_sampledBandIndex_layer" + std::to_string(i + 1);
			int layerPhaseSampledIndex = props.getInteger(phaseSampledIndexName, 0);
			cout << "layerPhaseSampledIndex: " << layerPhaseSampledIndex << endl;
			//create phase function
			Properties phaseProp("mixturephase");
			phaseProp.setString("weights", layerPhaseWeights);
			Properties rayleighProp("rayleigh");
			Properties hgProps("hg");
			hgProps.setSpectrum("g", phase_g);
			hgProps.setInteger("sampledSpecIndex", layerPhaseSampledIndex);
			ref<PhaseFunction> mixturePhaseFunc = static_cast<PhaseFunction *>(
				PluginManager::getInstance()->createObject(MTS_CLASS(PhaseFunction), phaseProp));

			ref<PhaseFunction> rayleighPhaseFunc = static_cast<PhaseFunction *>(
				PluginManager::getInstance()->createObject(MTS_CLASS(PhaseFunction), rayleighProp));
			rayleighPhaseFunc->configure();

			ref<PhaseFunction> hgPhaseFunc = static_cast<PhaseFunction *>(
				PluginManager::getInstance()->createObject(MTS_CLASS(PhaseFunction), hgProps));
			hgPhaseFunc->configure();

			mixturePhaseFunc->addChild(rayleighPhaseFunc);
			mixturePhaseFunc->addChild(hgPhaseFunc);
			mixturePhaseFunc->configure();
			m_layerPhaseFunctions.push_back(mixturePhaseFunc);
		}
		

	}

	PlaneParallelMedium(Stream *stream, InstanceManager *manager)
		: Medium(stream, manager){
		m_numLayers = stream->readInt();
		stream->readDoubleArray(m_layerThickness.data(), m_numLayers);
		m_startAltitude = stream->readDouble();

		for (int i = 0; i < m_numLayers; i++) {
			m_layerSigmaT.push_back(Spectrum(stream));
		}
		for (int i = 0; i < m_numLayers; i++) {
			m_layerAlbedo.push_back(Spectrum(stream));
		}
		for (int i = 0; i < m_numLayers; i++) {
			m_layerPhaseFunctions.push_back(static_cast<PhaseFunction *>(manager->getInstance(stream)));
		}

		for (int i = 0; i < m_numLayers; i++) {
			m_layerSigmaS.push_back(m_layerSigmaT[i]* m_layerAlbedo[i]);
		}
		configure();
	}

	virtual ~PlaneParallelMedium() {

	}

	void configure() {
		Medium::configure();
		//precompute accumulated layer heights
		m_thicknessCDF.push_back(0);
		for (int i = 0; i < m_numLayers; i++) {
			m_thicknessCDF.push_back(m_thicknessCDF[i] + m_layerThickness[i]);
		}

		for (int i = 0; i < m_numLayers+1; i++) {
			cout << "Layer: " << i << " " << m_thicknessCDF[i] << endl;
		}

		m_layerMaxSigmaT.resize(m_numLayers);
		//for (int i = 0; i < m_numLayers; i++) {
		//	m_layerMaxSigmaT[i] = 0.0;
		//	for (int j = 0; j<SPECTRUM_SAMPLES; ++j) {
		//		m_layerMaxSigmaT[i] = std::max(m_layerMaxSigmaT[i], m_layerSigmaT[i][j]);
		//	}
		//}

		//固定波段
		for (int i = 0; i < m_numLayers; i++) {
			m_layerMaxSigmaT[i] = m_layerSigmaT[i][0];
		}

		for (int i = 0; i < m_layerMaxSigmaT.size(); i++) {
			if (m_layerMaxSigmaT[i] == 0)
				m_layerMaxSigmaT[i] = 1e-12;
		}


		std::vector<double> verticalOpticalDepthPerLayerAtMaxSigmaT;
		for (int i = 0; i < m_numLayers; i++) {
			verticalOpticalDepthPerLayerAtMaxSigmaT.push_back(m_layerThickness[i] * m_layerMaxSigmaT[i]);
		}
		m_MaxOpticalDepthCDF.push_back(0);
		for (int i = 0; i < m_numLayers; i++) {
			m_MaxOpticalDepthCDF.push_back(m_MaxOpticalDepthCDF[i] + verticalOpticalDepthPerLayerAtMaxSigmaT[i]);
		}

		for (int i = 0; i < m_numLayers + 1; i++) {
			cout << "Optical: " << i << " " << m_MaxOpticalDepthCDF[i] << endl;
		}

	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Medium::serialize(stream, manager);
		stream->writeInt(m_numLayers);
		stream->writeDoubleArray(m_layerThickness.data(), m_numLayers);
		stream->writeDouble(m_startAltitude);
		for (int i = 0; i < m_numLayers; i++) {
			m_layerSigmaT[i].serialize(stream);
		}
		for (int i = 0; i < m_numLayers; i++) {
			m_layerAlbedo[i].serialize(stream);
		}
		for (int i = 0; i < m_numLayers; i++) {
			manager->serialize(stream, m_layerPhaseFunctions[i].get());
		}
	}


	// Determine the positon of a point in the medium layers
	int determineLayerIndexAccordingHeight(double h) const{
		double heightRelative = h - m_startAltitude;
		if (heightRelative < 0) return EBelowMedium;
		for (std::size_t i = 0; i < m_thicknessCDF.size()-1; i++) {
			if (heightRelative >= m_thicknessCDF[i] && heightRelative <= m_thicknessCDF[i+1]) {
				return (int)i;
			}
		}
		return EUpperMedium;
	}

	//Determine the position of a point in the medium layer according to optical depth
	int determineLayerIndexAccordingOpticalDepth(double relativeOpticalDepth) const {
		if (relativeOpticalDepth < 0) {
			return EBelowMedium;
		}
		for (std::size_t i = 0; i < m_MaxOpticalDepthCDF.size() - 1; i++) {
			if (relativeOpticalDepth >= m_MaxOpticalDepthCDF[i] && relativeOpticalDepth <= m_MaxOpticalDepthCDF[i + 1]) {
				return (int)i;
			}
		}
		return EUpperMedium;
	}

	// Integral the maxmium optical depth between ray.mint and ray.maxt
	//用每一层的消光系数最大的波段来进行积分采样
	Float opticalDepthIntegralMaximum(const Ray &ray) const {
		Point3d mintPos = ray.o + ray.mint*ray.d;
		Point3d maxPos = ray.o + ray.maxt*ray.d;
		double h1 = mintPos.y, h2 = maxPos.y;
		if (h1 > h2) swap(h1, h2);
		int lowerIndex = determineLayerIndexAccordingHeight(h1);
		int upperIndex = determineLayerIndexAccordingHeight(h2);
#ifdef QI_DEBUG
		cout << " opticalIntegral lowerIndex: " << lowerIndex << endl;
		cout << " opticalIntegral upperIndex: " << upperIndex << endl;
#endif
		if ((lowerIndex == upperIndex) && (lowerIndex == EBelowMedium || lowerIndex == EUpperMedium))
			return 0.0;
		if ((lowerIndex == upperIndex) && lowerIndex >= 0)
			return (ray.maxt - ray.mint)*m_layerMaxSigmaT[lowerIndex];

		int newLowerIndex, newUpperIndex;
		double remainLowerLength, remainUpperLength;
		Float totalOpticalDepth =0.0;
		if (lowerIndex < 0) {
			newLowerIndex = 0;
			remainLowerLength = 0;
		}
		else {
			newLowerIndex = lowerIndex + 1;
			remainLowerLength = m_thicknessCDF[lowerIndex + 1] - (h1 - m_startAltitude);
			totalOpticalDepth += remainLowerLength * m_layerMaxSigmaT[lowerIndex];
		}
		if (upperIndex < 0) {
			newUpperIndex = (int)m_numLayers - 1;
			remainUpperLength = 0;
		}
		else {
			newUpperIndex = upperIndex - 1;
			remainUpperLength = (h2 - m_startAltitude) - m_thicknessCDF[upperIndex];
			totalOpticalDepth += remainUpperLength * m_layerMaxSigmaT[upperIndex];
		}

		for (int i = newLowerIndex; i <= newUpperIndex; i++) {
			totalOpticalDepth += m_layerThickness[i] * m_layerMaxSigmaT[i];
		}
		return totalOpticalDepth / abs(ray.d.y);
	}

	// Integral the optical depth between ray.mint and ray.maxt
	Spectrum opticalDepthIntegral(const Ray &ray) const{
		Point3d mintPos = ray.o + ray.mint*ray.d;
		Point3d maxPos = ray.o + ray.maxt*ray.d;
		double h1 = mintPos.y, h2 = maxPos.y;
		if (h1 > h2) swap(h1, h2);
		int lowerIndex = determineLayerIndexAccordingHeight(h1);
		int upperIndex = determineLayerIndexAccordingHeight(h2);
#ifdef QI_DEBUG
		cout << " opticalIntegral lowerIndex: " << lowerIndex << endl;
		cout << " opticalIntegral upperIndex: " << upperIndex << endl;
#endif
		if ((lowerIndex == upperIndex) && (lowerIndex == EBelowMedium || lowerIndex == EUpperMedium))
			return Spectrum(0.0);
		if ((lowerIndex == upperIndex) && lowerIndex >= 0)
			return (ray.maxt - ray.mint)*m_layerSigmaT[lowerIndex];

		int newLowerIndex, newUpperIndex;
		double remainLowerLength, remainUpperLength;
		Spectrum totalOpticalDepth = Spectrum(0.0);
		if (lowerIndex < 0) {
			newLowerIndex = 0;
			remainLowerLength = 0;
		}
		else {
			newLowerIndex = lowerIndex + 1;
			remainLowerLength = m_thicknessCDF[lowerIndex + 1] - (h1 - m_startAltitude);
			totalOpticalDepth += remainLowerLength*m_layerSigmaT[lowerIndex];
		}
		if (upperIndex < 0) {
			newUpperIndex = (int)m_numLayers - 1;
			remainUpperLength = 0;
		}
		else {
			newUpperIndex = upperIndex - 1;
			remainUpperLength = (h2 - m_startAltitude) - m_thicknessCDF[upperIndex];
			totalOpticalDepth += remainUpperLength*m_layerSigmaT[upperIndex];
		}
		
		for (int i = newLowerIndex; i <= newUpperIndex; i++) {
			totalOpticalDepth += m_layerThickness[i]*m_layerSigmaT[i];
		}
		
		return totalOpticalDepth / abs(ray.d[1]);
	}

	Spectrum evalTransmittance(const Ray &ray, Sampler *) const {
		Spectrum transmittance;
		Spectrum opticalDepthSpec = opticalDepthIntegral(ray);
		for (int i = 0; i<SPECTRUM_SAMPLES; ++i)
			transmittance[i] = opticalDepthSpec[i] != 0
			? math::fastexp(-opticalDepthSpec[i]) : (Float) 1.0f;
		return transmittance;
	}

	/// accumulate the optical depth until it reaches 'opticalDepth', return the path length
	double freePathAccordingAccumulateOpticalDepth(const Ray &ray, double opticalDepth, int &sampledLayerIndex) const{
		//using the wavelength which has maximum sigmaT to sampline free path
		double verticalOpticalDepth = opticalDepth * abs(ray.d[1]);
		Point3 mintPos = ray.o + ray.mint*ray.d;
		int currentLayerIndex = determineLayerIndexAccordingHeight(mintPos.y);
		if (verticalOpticalDepth == 0) {
			sampledLayerIndex = currentLayerIndex;
			return 0.0;
		}

		double currentRelativeOpticalDepth = 0;
		if (currentLayerIndex == 0) {
		//	cout << "m_layerMaxSigmaT[0]: " <<m_layerMaxSigmaT[0]<< endl;
			currentRelativeOpticalDepth = (ray.o[1] - m_startAltitude)*m_layerMaxSigmaT[0];
			//cout << "currentRelativeOpticalDepth: " << currentRelativeOpticalDepth << endl;
		}
		if (currentLayerIndex > 0) {
			currentRelativeOpticalDepth = (ray.o[1] - m_startAltitude - m_thicknessCDF[currentLayerIndex])*
				m_layerMaxSigmaT[currentLayerIndex] + m_MaxOpticalDepthCDF[currentLayerIndex];
		}

		//sensor is above the atmosphere
		if (currentLayerIndex == EUpperMedium) {
			currentRelativeOpticalDepth = m_MaxOpticalDepthCDF[m_MaxOpticalDepthCDF.size() - 1];
		}

		if (ray.d[1] == 0) {//horizontal
			sampledLayerIndex = currentLayerIndex;
			double sampleDistance = opticalDepth / m_layerMaxSigmaT[currentLayerIndex];
			return sampleDistance;
			
		}

		double totalVerticalLength = 0;
		if (ray.d[1] > 0) {
			double relativeOp = currentRelativeOpticalDepth + verticalOpticalDepth;
			int layerIndex = determineLayerIndexAccordingOpticalDepth(relativeOp);
			sampledLayerIndex = layerIndex;
			if (layerIndex < 0) {
				return std::numeric_limits<Float>::infinity();
				//totalVerticalLength += m_thicknessCDF[m_thicknessCDF.size() - 1] - (mintPos.y-m_startAltitude);
				//sampledLayerIndex = m_layerThickness.size() - 1;
			}			
			else if (layerIndex == currentLayerIndex) {
				double sampleDistance = opticalDepth / m_layerMaxSigmaT[currentLayerIndex];
				//calculate the optical depth for each band at the sampled position
				return sampleDistance;
				
			}
			else {
				double pathLength;
				pathLength = (m_MaxOpticalDepthCDF[currentLayerIndex + 1] - currentRelativeOpticalDepth) / m_layerMaxSigmaT[currentLayerIndex];
				totalVerticalLength += pathLength;
				pathLength = (relativeOp - m_MaxOpticalDepthCDF[layerIndex]) / m_layerMaxSigmaT[layerIndex];
				totalVerticalLength += pathLength;
				for (int i = currentLayerIndex + 1; i <= layerIndex - 1; i++) {
					totalVerticalLength += m_layerThickness[i];
				}
			}
			
		}

		if (ray.d[1] < 0) {
			double relativeOp = currentRelativeOpticalDepth - verticalOpticalDepth;
			int layerIndex = determineLayerIndexAccordingOpticalDepth(relativeOp);
			sampledLayerIndex = layerIndex;
			if (layerIndex < 0) {
				return std::numeric_limits<Float>::infinity();
				///totalVerticalLength += mintPos.y - m_startAltitude;
			//	sampledLayerIndex = 0;
			}				
			else if (layerIndex == currentLayerIndex) {
				double sampleDistance = opticalDepth / m_layerMaxSigmaT[currentLayerIndex];
				//calculate the optical depth for each band at the sampled position
				return sampleDistance;
			}
			else {
				double pathLength = 0;
				if (currentLayerIndex == EUpperMedium) {
					pathLength = mintPos.y - m_thicknessCDF[m_thicknessCDF.size() - 1];
					currentLayerIndex = m_numLayers - 1 + 1;
				}
				else {
					pathLength = (currentRelativeOpticalDepth - m_MaxOpticalDepthCDF[currentLayerIndex]) / m_layerMaxSigmaT[currentLayerIndex];
				}
				totalVerticalLength += pathLength;
				pathLength = (m_MaxOpticalDepthCDF[layerIndex + 1] - relativeOp) / m_layerMaxSigmaT[layerIndex];
				totalVerticalLength += pathLength;
				for (int i = layerIndex + 1; i <= currentLayerIndex - 1; i++) {
					totalVerticalLength += m_layerThickness[i];
				}
			}
			
			
		}
		return totalVerticalLength / abs(ray.d[1]);
	}

	bool sampleDistance(const Ray &ray, MediumSamplingRecord &mRec,
		Sampler *sampler) const {
		double rand = sampler->next1D(), sampledDistance;
		double randomOpticalDepth = -math::fastlog(1 - rand);
		//cumulate optical depth until it reaches randomOpticalDepth, starting form ray.o
		//cout <<"rand:"<< rand<< " randomOpticalDepth: " << randomOpticalDepth << endl;
		int sampledLayerIndex;
		sampledDistance = freePathAccordingAccumulateOpticalDepth(ray, randomOpticalDepth, sampledLayerIndex);
		//if(sampledLayerIndex > 1)
		Float distSurf = ray.maxt - ray.mint;
		bool success = true;
		if (sampledDistance != std::numeric_limits<Float>::infinity() && sampledDistance < distSurf) {
			mRec.t = sampledDistance + ray.mint;
			mRec.p = ray(mRec.t);
			mRec.time = ray.time;
			mRec.medium = this;
			if (sampledLayerIndex >= 0) {
				mRec.sigmaS = m_layerSigmaT[sampledLayerIndex] * m_layerAlbedo[sampledLayerIndex];
				mRec.sigmaA = m_layerSigmaT[sampledLayerIndex] - mRec.sigmaS;
				mRec.sampledPhaseFun = m_layerPhaseFunctions[sampledLayerIndex];
				m_currentSampledLayer = sampledLayerIndex;
				mRec.pdfSuccessRev = mRec.pdfSuccess = m_layerMaxSigmaT[sampledLayerIndex] * math::fastexp(-randomOpticalDepth);
			}
			else {
				success = false;
			}
			/* Fail if there is no forward progress
			(e.g. due to roundoff errors) */
			if (mRec.p == ray.o) {
				success = false;
				//cout << "near close" << endl;
			}
		}
		else {
			sampledDistance = distSurf;
			success = false;
		}
		Ray tmpray(ray);
		tmpray.maxt = sampledDistance;
		mRec.transmittance = evalTransmittance(tmpray, sampler);
		mRec.pdfFailure = math::fastexp(-opticalDepthIntegralMaximum(tmpray));
		mRec.medium = this;
		if (mRec.transmittance.max() < 1e-20)
			mRec.transmittance = Spectrum(0.0f);
		return success;
	}

	void eval(const Ray &ray, MediumSamplingRecord &mRec) const {
		Point3 maxPos = ray.o + ray.maxt*ray.d;
		int layerIndex = determineLayerIndexAccordingHeight(maxPos.y);

		Float distance = ray.maxt - ray.mint;
		mRec.transmittance = evalTransmittance(ray, NULL);
		Float opticalDepth = opticalDepthIntegralMaximum(ray);
		mRec.pdfFailure = math::fastexp(-opticalDepth);
		mRec.pdfSuccess = mRec.pdfSuccessRev = m_layerMaxSigmaT[layerIndex] * mRec.pdfFailure;
		mRec.sigmaS = m_layerSigmaT[layerIndex] * m_layerAlbedo[layerIndex];
		mRec.sigmaA = m_layerSigmaT[layerIndex] - mRec.sigmaS;;
		mRec.time = ray.time;
		mRec.medium = this;
		if (mRec.transmittance.max() < 1e-20)
			mRec.transmittance = Spectrum(0.0f);
	}

	bool isHomogeneous() const {
		return false;
	}

	std::string toString() const {
		std::ostringstream oss;
		return  oss.str();
	}

	MTS_DECLARE_CLASS()
private:
	int m_numLayers;
	std::vector<double> m_layerThickness; //thickness per layer
	double m_startAltitude; //start altitude position of the bottom layer
	std::vector<Spectrum> m_layerSigmaT; //extinction coefficient of each layer
	std::vector<Spectrum> m_layerAlbedo; //single scattering albedo of each layer
	std::vector<ref<PhaseFunction> > m_layerPhaseFunctions; // phasefunction per layer

	std::vector<Spectrum> m_layerSigmaS; //scattering coefficient of each layer
	std::vector<double> m_thicknessCDF;
	std::vector<double> m_layerMaxSigmaT; // maximum sigmaT of each layer
	std::vector<double> m_MaxOpticalDepthCDF;
	mutable int m_currentSampledLayer;
};

MTS_IMPLEMENT_CLASS_S(PlaneParallelMedium, false, Medium)
MTS_EXPORT_PLUGIN(PlaneParallelMedium, "PlaneParallel medium");
MTS_NAMESPACE_END