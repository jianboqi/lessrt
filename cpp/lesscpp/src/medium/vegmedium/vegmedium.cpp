/*
	This file is part of Mitsuba, a physically based rendering system.

	Copyright (c) 2007-2014 by Wenzel Jakob and others.

	Mitsuba is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License Version 3
	as published by the Free Software Foundation.

	Mitsuba is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

#include <mitsuba/render/scene.h>
#include "../maxexp.h"

MTS_NAMESPACE_BEGIN

	class VegMedium : public Medium {
	public:
		//enum ELadType {
		//	ESpherical,  /// 球型分布
		//	EUniform,   /// 统一型
		//	EPlanophile,   /// 平面型
		//	EErectophile,   /// 竖直型
		//	EPlagiophile,  /// 倾斜型
		//	EExtremophile  ///极端型
		//};

		VegMedium(const Properties &props)
			: Medium(props){
			m_leafAreaDensity = props.getFloat("leafAreaDensity", 1.2);
			m_hotSpotFactor = props.getFloat("hotspotFactor", 0.1);
			std::string ladType = props.getString("ladtype", "Spherical");
			if (ladType == "Spherical") {
				m_ladType = PhaseFunction::ESpherical;
			}
			else if (ladType == "Planophile") {
				m_ladType = PhaseFunction::EPlanophile;
			}
			else if (ladType == "Erectophile") {
				m_ladType = PhaseFunction::EErectophile;
			}
			else if (ladType == "Plagiophile") {
				m_ladType = PhaseFunction::EPlagiophile;
			}
			else if (ladType == "Extremophile") {
				m_ladType = PhaseFunction::EExtremophile;
			}
			else if (ladType == "Uniform") {
				m_ladType = PhaseFunction::EUniform;
			}
		}

		VegMedium(Stream *stream, InstanceManager *manager)
			: Medium(stream, manager){
			m_ladType = (PhaseFunction::ELadType)stream->readInt();
			m_hotSpotFactor = stream->readFloat();
			m_leafAreaDensity = stream->readFloat();
			configure();
		}

		void serialize(Stream* stream, InstanceManager* manager) const {
			Medium::serialize(stream, manager);
			stream->writeInt(m_ladType);
			stream->writeFloat(m_hotSpotFactor);
			stream->writeFloat(m_leafAreaDensity);
		}

		virtual ~VegMedium() {
		}

		void configure() {
			Medium::configure();
			//Precompute the G function in a step of 1 degree
			for (double i = 0; i <= 90; i++) {
				m_precomputedG.push_back(GFunc(i));//Spherical
			}
			m_frontRef = this->getPhaseFunction()->getProperties().getSpectrum("frontReflectance", Spectrum(0.0));
			m_backRef = this->getPhaseFunction()->getProperties().getSpectrum("backReflectance", Spectrum(0.0));
			m_transmittance = this->getPhaseFunction()->getProperties().getSpectrum("transmittance", Spectrum(0.0));
		}

		/// <summary>
		/// Interpolate G from the precomputed G arrays
		/// </summary>
		/// <param name="zenithInDegree"></param>
		/// <returns></returns>
		Float GetInterpolatedG(Float zenithInDegree) const{
			int lowerIndex = (int)zenithInDegree;
			int upperIndex = lowerIndex + 1;
			Float k = (m_precomputedG[upperIndex] - m_precomputedG[lowerIndex]); // Because interval is one degree
			return k * (zenithInDegree - lowerIndex) + m_precomputedG[lowerIndex];
		}

		/// <summary>
		/// Compute the G function according to zenith angle (degree)
		/// </summary>
		/// <param name="zenith"></param>
		/// <returns></returns>
		Float GFunc(double zenith) const {
			Float zenAngle = degToRad(zenith);
			Float deltaZenith = 2;
			Float deltaAzi = 2;
			int numAzi = int(360 / deltaAzi);
			int numZenith = int(90 / deltaZenith);
			deltaZenith = degToRad(deltaZenith);
			deltaAzi = degToRad(deltaAzi);
			Float Gvalue = 0;

			for (int i = 0; i < numAzi; i++) {
				for (int j = 0; j < numZenith; j++) {
					Float centerAzi = (i + 0.5) * deltaAzi;
					Float centerZenith = (j + 0.5) * deltaZenith;
					Float lad = sin(centerZenith); //Spherical
					if (m_ladType == PhaseFunction::ESpherical) {
						lad = sin(centerZenith); //Spherical
					}
					else if (m_ladType == PhaseFunction::EPlanophile) {
						lad = INV_PI * 2 * (1 + cos(2 * centerZenith));
					}
					else if (m_ladType == PhaseFunction::EErectophile) {
						lad = INV_PI * 2 * (1 - cos(2 * centerZenith));
					}
					else if (m_ladType == PhaseFunction::EPlagiophile) {
						lad = INV_PI * 2 * (1 - cos(4 * centerZenith));
					}
					else if (m_ladType == PhaseFunction::EExtremophile) {
						lad = INV_PI * 2 * (1 + cos(4 * centerZenith));
					}
					else if (m_ladType == PhaseFunction::EUniform) {
						lad = 2 * INV_PI;
					}
					Gvalue += lad * abs(cos(centerZenith) * cos(zenAngle) + sin(centerZenith) * sin(zenAngle) * cos(centerAzi)) * deltaZenith * deltaAzi;
				}
			}
			return Gvalue * INV_PI * 0.5;
		}

		//Compute single scattering albedo for turbid medium
		Spectrum computeSingleAlbedo() const{
			return m_frontRef + m_transmittance;// Assume that front reflectance equals to back reflectance
		}

		Spectrum evalTransmittance(const Ray &ray, Sampler *) const {
			/*First, compute the G function according to incident ray\
			* Here, precomputation of G is used, we only need to calculate the zenith, since azimuth angle is
			* assumed to be random distribution
			*/
			//int thetaInterval = (int)(math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180);
			//Float Gv = m_precomputedG[thetaInterval];
			Float zenith = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float Gv = GetInterpolatedG(zenith);
			Float sigmaT = Gv * m_leafAreaDensity;

			Float negLength = ray.mint - ray.maxt;
			Float transmittance = sigmaT != 0 ? math::fastexp(sigmaT * negLength): (Float)1.0f;
			return Spectrum(transmittance);
		}

		Spectrum evalTransmittanceWithHotspotWithSigmaT(const Ray& solarRay, const Ray& sensorRay, const Point& p1, bool &isOnSurface,
			Float& maxEvalRange, Float sigmaT, Float Gsensor, Float Gsoloar, Sampler* sampler) const {
			Float Gs = Gsoloar, Gv = Gsensor;
			/*
			* Then modify the extinction coefficient according to Hapke hotspot function
			* But the we only consider the range between range |solarRay.mint, solarRay.maxt|
			*/
			Float transmittance = 1.0;
			//Float maxRange = (sensorRay.o - solarRay.o).length();
			Float evalRange = sensorRay.maxt - sensorRay.mint;

			/////////////////////Hapke hotspot function///////////////////
			/*Float dotSolarSensor = absDot(solarRay.d, sensorRay.d);*/
			Float dotSolarSensor = dot(-solarRay.d, sensorRay.d);
			Float angle = math::safe_acos(dotSolarSensor);
			Float h = math::safe_sqrt((Gs + Gv) * 0.5) * m_leafAreaDensity * (m_hotSpotFactor) * 0.5;
			//Float h = (Gs + Gv) * 0.5 * m_leafAreaDensity * (m_hotSpotFactor) * 0.5;
			//Float h =  pow((Gs + Gv) * 0.5, 1.5) * m_leafAreaDensity * (m_hotSpotFactor) * 0.5;

			if (isOnSurface) {
				Float cosSolar = absDot(solarRay.d, Vector(0, 1, 0));
				Float cosSensor = absDot(sensorRay.d, Vector(0, 1, 0));
				Float u = 2 * cosSolar * cosSensor / (cosSolar + cosSensor);
				Float z1 = u * math::safe_sqrt((Gs + Gv) * 0.5) * (m_hotSpotFactor)*cos(angle * 0.5) / sin(angle * 0.5);
				Float deltaZ = sensorRay.o.y - p1.y;
				if (z1 > deltaZ) {
					Float factor = (1 - deltaZ / z1) * (1 - deltaZ / z1);
					h *= factor;
				}
				else {
					h = 0;
				}
				isOnSurface = false;
			}



			Float H = 1 - 1 / (1 + 1.0 / h * tan(angle * 0.5));
			Float newsigmaT = sigmaT * H;
			////////////////////End of Hapke/////////////////////////////

			if (evalRange <= maxEvalRange) { //consider hotspot
				transmittance = newsigmaT != 0 ? math::fastexp(-newsigmaT * evalRange) : (Float)1.0f;
				maxEvalRange = maxEvalRange - evalRange;
			}
			else { //Consider hotspot only in range maxRange
				transmittance = newsigmaT != 0 ? math::fastexp(-newsigmaT * maxEvalRange) : (Float)1.0f;
				transmittance *= sigmaT != 0 ? math::fastexp(-sigmaT * (evalRange - maxEvalRange)) : (Float)1.0f;
				maxEvalRange = 0;
			}

			return Spectrum(transmittance);
		}

		Spectrum evalTransmittanceWithHotspot(const Ray& solarRay, const Ray& sensorRay, const Point& p1, bool isOnSurface, Float& maxEvalRange,
			Sampler* sampler) const {
			/*
			* First, calcualte the inital G value for both incident direction, and outgoing direction.
			* according to different LAD
			*/
			//int thetaInterval = (int)(math::safe_acos(absDot(Vector(0, 1, 0), solarRay.d)) / M_PI_DBL * 180);
			//Float Gs = m_precomputedG[thetaInterval];
			//thetaInterval = (int)(math::safe_acos(absDot(Vector(0, 1, 0), sensorRay.d)) / M_PI_DBL * 180);
			//Float Gv = m_precomputedG[thetaInterval];
			Float zenith = math::safe_acos(absDot(Vector(0, 1, 0), solarRay.d)) / M_PI_DBL * 180;
			Float Gs = GetInterpolatedG(zenith);
			zenith = math::safe_acos(absDot(Vector(0, 1, 0), sensorRay.d)) / M_PI_DBL * 180;
			Float Gv = GetInterpolatedG(zenith);

			/*
			* Then modify the extinction coefficient according to Hapke hotspot function
			* But the we only consider the range between range |solarRay.mint, solarRay.maxt|
			*/
			Float transmittance = 1.0;
			//Float maxRange = (sensorRay.o - solarRay.o).length();
			Float evalRange = sensorRay.maxt - sensorRay.mint;

			Float sigmaT = Gv * m_leafAreaDensity;

			/////////////////////Hapke hotspot function///////////////////
			/*Float dotSolarSensor = absDot(solarRay.d, sensorRay.d);*/
			Float dotSolarSensor = dot(-solarRay.d, sensorRay.d);
			Float angle = math::safe_acos(dotSolarSensor);
			Float h = math::safe_sqrt((Gs + Gv) * 0.5) * m_leafAreaDensity * (m_hotSpotFactor) * 0.5;
			//Float h = (Gs + Gv) * 0.5 * m_leafAreaDensity * (m_hotSpotFactor) * 0.5;
			//Float h =  pow((Gs + Gv) * 0.5, 1.5) * m_leafAreaDensity * (m_hotSpotFactor) * 0.5;

			if (isOnSurface) {
				Float cosSolar = absDot(solarRay.d, Vector(0, 1, 0));
				Float cosSensor = absDot(sensorRay.d, Vector(0, 1, 0));
				Float u = 2 * cosSolar * cosSensor / (cosSolar + cosSensor);
				Float z1 = u * math::safe_sqrt((Gs + Gv) * 0.5) * (m_hotSpotFactor) * cos(angle * 0.5) / sin(angle * 0.5);
				Float deltaZ = sensorRay.o.y - p1.y;
				if (z1 > deltaZ) {
					Float factor = (1 - deltaZ / z1) * (1 - deltaZ / z1);
					h *= factor;
				}
				else {
					h = 0;
				}
			}
			
			

			Float H = 1 - 1 / (1 + 1.0 / h * tan(angle * 0.5));
			Float newsigmaT = sigmaT * H;
			////////////////////End of Hapke/////////////////////////////
			
 			if (evalRange <= maxEvalRange) { //consider hotspot
				transmittance = newsigmaT != 0 ? math::fastexp(-newsigmaT * evalRange) : (Float)1.0f;
				maxEvalRange = maxEvalRange - evalRange;
			}
			else { //Consider hotspot only in range maxRange
				transmittance = newsigmaT != 0 ? math::fastexp(-newsigmaT * maxEvalRange) : (Float)1.0f;
				transmittance *= sigmaT != 0 ? math::fastexp(-sigmaT * (evalRange- maxEvalRange)) : (Float)1.0f;
				maxEvalRange = 0;
			}
			
			return Spectrum(transmittance);
		}

		Spectrum getVegetationSingleAlbedo(const Ray& ray) const {
			return  m_frontRef + m_transmittance;
		}

		Float getVegetationSigmaT(const Ray& ray) const {
			Float zenithAngleInDegree = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float Gs = GetInterpolatedG(zenithAngleInDegree);
			Float sigmaT = Gs * m_leafAreaDensity;
			return sigmaT;
		}

		Float getVegetationG(const Ray& ray) const {
			Float zenithAngleInDegree = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float Gs = GetInterpolatedG(zenithAngleInDegree);
			return Gs;
		}

		bool sampleDistanceWithSigmaTandAlbedo(const Ray& ray,
			MediumSamplingRecord& mRec, Sampler* sampler, Float sigmaT, Spectrum singleAlbedo) const {
			Float rand = sampler->next1D(), sampledDistance;
			sampledDistance = -math::fastlog(1 - rand) / sigmaT;
			Float distSurf = ray.maxt - ray.mint;
			bool success = true;
			if (sampledDistance < distSurf) {
				mRec.t = sampledDistance + ray.mint;
				mRec.p = ray(mRec.t);
				mRec.sigmaA = sigmaT * (Spectrum(1.0) - singleAlbedo);
				mRec.sigmaS = sigmaT * singleAlbedo;
				mRec.time = ray.time;
				mRec.medium = this;

				/* Fail if there is no forward progress
				   (e.g. due to roundoff errors) */
				if (mRec.p == ray.o)
					success = false;
			}
			else {
				sampledDistance = distSurf;
				success = false;
			}
			mRec.transmittance = Spectrum(math::fastexp(-sampledDistance * sigmaT));
			mRec.medium = this;
			mRec.sampledPhaseFun = const_cast<PhaseFunction*>(this->getPhaseFunction());
			mRec.pdfFailure = math::fastexp(-sigmaT * sampledDistance);
			mRec.pdfSuccess = mRec.pdfSuccessRev = sigmaT * mRec.pdfFailure;
			if (mRec.transmittance.max() < 1e-20)
				mRec.transmittance = Spectrum(0.0f);
			return success;
		}

		bool sampleDistanceWithTau(const Ray& ray,
			MediumSamplingRecord& mRec, Float& sampledTau, Sampler* sampler) const {
			Float zenithAngleInDegree = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float Gs = GetInterpolatedG(zenithAngleInDegree);
			Float sigmaT = Gs * m_leafAreaDensity;
			Float distSurf = ray.maxt - ray.mint;
			Float tau = sigmaT * distSurf;
			Spectrum singleAlbedo = computeSingleAlbedo();
			bool success = true;
			Float sampledDistance;
			if (sampledTau < tau) {
				sampledDistance = sampledTau / sigmaT;
				mRec.t = sampledDistance + ray.mint;
				mRec.p = ray(mRec.t);
				mRec.sigmaA = sigmaT * (Spectrum(1.0) - singleAlbedo);
				mRec.sigmaS = sigmaT * singleAlbedo;
				mRec.time = ray.time;

				/* Fail if there is no forward progress
				   (e.g. due to roundoff errors) */
				if (mRec.p == ray.o)
					success = false;
				sampledTau = -math::fastlog(1 - sampler->next1D()); //Reset the sampledTau
			}
			else {
				sampledDistance = distSurf;
				sampledTau -= tau;
				success = false;
			}
			mRec.transmittance = Spectrum(math::fastexp(-sampledDistance * sigmaT));
			mRec.medium = this;
			mRec.sampledPhaseFun = const_cast<PhaseFunction*>(this->getPhaseFunction());
			mRec.pdfFailure = math::fastexp(-sigmaT * sampledDistance);
			mRec.pdfSuccess = mRec.pdfSuccessRev = sigmaT * mRec.pdfFailure;
			if (mRec.transmittance.max() < 1e-20)
				mRec.transmittance = Spectrum(0.0f);
			return success;
		}

		bool sampleDistanceWithTotalTauSigmaTandAlbedo(const Ray& ray,
			MediumSamplingRecord& mRec, Sampler* sampler, Float& sampledTau, bool& needReSampleTau, Float sigmaT, Spectrum singleAlbedo) const {
			Float zenithAngleInDegree = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float distSurf = ray.maxt - ray.mint;
			Float tau = sigmaT * distSurf;
			bool success = true;
			Float sampledDistance;
			if (sampledTau < tau) {
				sampledDistance = sampledTau / sigmaT;
				mRec.t = sampledDistance + ray.mint;
				mRec.p = ray(mRec.t);
				mRec.sigmaA = sigmaT * (Spectrum(1.0) - singleAlbedo);
				mRec.sigmaS = sigmaT * singleAlbedo;
				mRec.time = ray.time;

				/* Fail if there is no forward progress
				   (e.g. due to roundoff errors) */
				if (mRec.p == ray.o)
					success = false;
				//sampledTau = -math::fastlog(1 - sampler->next1D()); //Reset the sampledTau
				needReSampleTau = true;
			}
			else {
				sampledDistance = distSurf;
				sampledTau -= tau;
				success = false;
			}
			mRec.transmittance = Spectrum(math::fastexp(-sampledDistance * sigmaT));
			mRec.medium = this;
			mRec.sampledPhaseFun = const_cast<PhaseFunction*>(this->getPhaseFunction());
			mRec.pdfFailure = math::fastexp(-sigmaT * sampledDistance);
			mRec.pdfSuccess = mRec.pdfSuccessRev = sigmaT * mRec.pdfFailure;
			if (mRec.transmittance.max() < 1e-20)
				mRec.transmittance = Spectrum(0.0f);
			return success;
		}

		bool sampleDistance(const Ray &ray, MediumSamplingRecord &mRec,
			Sampler *sampler) const {
			Float rand = sampler->next1D(), sampledDistance;

			/*First, compute the G function according to incident ray\
			* Here, precomputation of G is used, we only need to calculate the zenith, since azimuth angle is
			* assumed to be random distribution
			*/
			Float zenithAngleInDegree = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float Gs = GetInterpolatedG(zenithAngleInDegree);
			/*Float zenith = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float Gs = GFunc(zenith);*/
			Float sigmaT = Gs * m_leafAreaDensity;

			Spectrum singleAlbedo = computeSingleAlbedo();

			sampledDistance = -math::fastlog(1 - rand) / sigmaT;
			Float distSurf = ray.maxt - ray.mint;
			bool success = true;
			if (sampledDistance < distSurf) {
				mRec.t = sampledDistance + ray.mint;
				mRec.p = ray(mRec.t);
				mRec.sigmaA = sigmaT*(Spectrum(1.0) - singleAlbedo);
				mRec.sigmaS = sigmaT* singleAlbedo;
				mRec.time = ray.time;

				/* Fail if there is no forward progress
				   (e.g. due to roundoff errors) */
				if (mRec.p == ray.o)
					success = false;
			}
			else {
				sampledDistance = distSurf;
				success = false;
			}
			mRec.transmittance = Spectrum(math::fastexp(-sampledDistance*sigmaT));
			mRec.medium = this;
			mRec.sampledPhaseFun = const_cast<PhaseFunction*>(this->getPhaseFunction());
			mRec.pdfFailure = math::fastexp(-sigmaT * sampledDistance);
			mRec.pdfSuccess = mRec.pdfSuccessRev = sigmaT * mRec.pdfFailure;
			if (mRec.transmittance.max() < 1e-20)
				mRec.transmittance = Spectrum(0.0f);
			return success;
		}

		void eval(const Ray &ray, MediumSamplingRecord &mRec) const {
			Float distance = ray.maxt - ray.mint;
			Float zenithAngleInDegree = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float Gs = GetInterpolatedG(zenithAngleInDegree);
			/*Float zenith = math::safe_acos(absDot(Vector(0, 1, 0), ray.d)) / M_PI_DBL * 180;
			Float Gs = GFunc(zenith);*/
			Spectrum singleAlbedo = computeSingleAlbedo();
			Float sigmaT = Gs * m_leafAreaDensity;
			mRec.transmittance = Spectrum(sigmaT * (-distance)).exp();
			mRec.pdfSuccess = mRec.pdfSuccessRev = mRec.pdfSuccess;
			mRec.pdfFailure = mRec.pdfFailure;
			mRec.sigmaA = sigmaT * (Spectrum(1.0) - singleAlbedo);
			mRec.sigmaS = sigmaT * singleAlbedo;;
			mRec.time = ray.time;
			mRec.medium = this;
			if (mRec.transmittance.max() < 1e-20)
				mRec.transmittance = Spectrum(0.0f);
		}

		bool isHomogeneous() const {
			return true;
		}

		std::string toString() const {
			std::ostringstream oss;
			oss << "VegMedium[" << endl
				<< "  leafAreaDensity = " << m_leafAreaDensity << "," << endl
				<< "  ladtype = " << m_ladType << "," << endl
				<< "  hotspotFactor = " << m_hotSpotFactor << "," << endl
				<< "  frontRef = " << m_frontRef.toString() << endl
				<< "  backRef = " << m_backRef.toString() << endl
				<< "  transmittance = " << m_transmittance.toString() << endl;
			oss << "  phase = " << indent(m_phaseFunction.toString()) << endl
				<< "]";
			return oss.str();
		}

		MTS_DECLARE_CLASS()
	private:
		std::vector<Float> m_precomputedG;
		Spectrum m_frontRef, m_backRef, m_transmittance;
		
};

MTS_IMPLEMENT_CLASS_S(VegMedium, false, Medium)
MTS_EXPORT_PLUGIN(VegMedium, "Vegetation medium");
MTS_NAMESPACE_END
