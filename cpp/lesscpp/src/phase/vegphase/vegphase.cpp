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

#include <mitsuba/render/phase.h>
#include <mitsuba/render/sampler.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/core/pmf.h>
#include "vegphase.h"

MTS_NAMESPACE_BEGIN

//enum class LeafAngleDistribution {
//	Sphirical = 1,
//	Uniform = 2,
//	Planophile = 3,
//	Erectophile = 4, //ÊúÖ±ÐÍ
//	Plagiophile = 5, //ÇãÐ±
//	Extremophile = 6   //¼«¶Ë
//};

class VegPhaseFunction : public PhaseFunction {
	public:
		VegPhaseFunction(const Properties &props)
			: PhaseFunction(props) {
			m_opticalName = props.getString("opticalName", "");
			m_frontRef = props.getSpectrum("frontReflectance", Spectrum(0.0));
			m_backRef = props.getSpectrum("backReflectance", Spectrum(0.0));
			m_transmittance = props.getSpectrum("transmittance", Spectrum(0.0));
			string ladType = props.getString("ladtype", "Spherical");
			if (ladType == "Spherical") {
				m_ladType = ESpherical;
			}
			else if (ladType == "Planophile") {
				m_ladType = EPlanophile;
			}
			else if (ladType == "Erectophile") {
				m_ladType = EErectophile;
			}
			else if (ladType == "Plagiophile") {
				m_ladType = EPlagiophile;
			}
			else if (ladType == "Extremophile") {
				m_ladType = EExtremophile;
			}
			else if (ladType == "Uniform") {
				m_ladType = EUniform;
			}
			else {
				m_ladType = EINVALIDE;
			}
		}

		VegPhaseFunction(Stream *stream, InstanceManager *manager)
			: PhaseFunction(stream, manager) {
			m_ladType = (ELadType)stream->readInt();
			m_frontRef = Spectrum(stream);
			m_backRef = Spectrum(stream);
			m_transmittance = Spectrum(stream);
			configure();
		}

		virtual ~VegPhaseFunction() { }

		void configure() {
			PhaseFunction::configure();
			m_type = EIsotropic | EAngleDependence;
			//Spectrum phaseIntegral = validatePhaseFunction();

			if (m_ladType == EINVALIDE) return;

			//get band idx with highest albedo
			Spectrum albedo = m_frontRef + m_transmittance;
			Float result = albedo[0];
			m_idx_max_albedo = 0;
			for (int i = 1; i < SPECTRUM_SAMPLES; i++) {
				if (albedo[i] > result) {
					result = albedo[i];
					m_idx_max_albedo = i;
				}
			}

			//Precompuate the phase function
			//Here, only zenith angle needs to be considered, because azimuth angle does not affect the value
			//when azimuth angle is considered as independent to zenith angle
			if (m_isConfigured) return;
			m_precomputedPhase.clear();
			cout << "INFO: Computing phase functions..." << endl;
			m_integralStepZenith = 5 / 180.0 * M_PI_DBL;
			m_integralStepAzi = 20 / 180.0 * M_PI_DBL;
			m_zenith_num = int(M_PI_DBL / m_integralStepZenith);
			m_azi_num_half = int(M_PI_DBL / m_integralStepAzi);

			double phi = 0;
			MediumSamplingRecord m;
			for (int i = 0; i <= m_zenith_num; i++) { //for incident angle
				double inci_theta = i* m_integralStepZenith;
				Vector inci_vec(-cos(phi) * sin(inci_theta), cos(inci_theta), sin(phi) * sin(inci_theta));
				std::vector<std::vector<Spectrum>> outZenithForEachInci;
				for (int j = 0; j <= m_zenith_num; j++) {  //for scattered zenith angle
					double out_theta = j * m_integralStepZenith;
					std::vector<Spectrum> outAziForEachOutZenith;
					for (int k = 0; k <= m_azi_num_half; k++) {
						double out_azi = k*m_integralStepAzi;
						Vector out_vec(-cos(out_azi) * sin(out_theta), cos(out_theta), sin(out_azi) * sin(out_theta));
						PhaseFunctionSamplingRecord pfs(m, inci_vec, out_vec);
						Spectrum phaseVal = computePhasefunc(pfs);
						outAziForEachOutZenith.push_back(phaseVal);
					}
					outZenithForEachInci.push_back(outAziForEachOutZenith);
				}
				m_precomputedPhase.push_back(outZenithForEachInci);
			}

			//compute sampling tables
			int inciIndex = 0;
			m_phaseDiscrete.clear();
			for (int s = 0; s < SPECTRUM_SAMPLES; s++) {
				m_phaseDiscrete.push_back(std::vector<DiscreteDistribution>());
			}	
			for (int i = 0; i < m_zenith_num; i++) { //for incident angle
				double inci_theta = (i + 0.5) * m_integralStepZenith;
				//Vector inci_vec(-cos(phi) * sin(inci_theta), cos(inci_theta), sin(phi) * sin(inci_theta));
				for (int s = 0; s < SPECTRUM_SAMPLES; s++) {
					m_phaseDiscrete[s].push_back(DiscreteDistribution(size_t(m_azi_num_half) * size_t(m_azi_num_half)*2));
				}
				for (int j = 0; j < m_zenith_num;j++) {  //for scattered zenith angle
					double out_theta = (j + 0.5) * m_integralStepZenith;
					for (int k = 0; k < (m_azi_num_half * 2); k++) {
						double out_azi = (k + 0.5) * m_integralStepAzi;;
						//Vector out_vec(-cos(out_azi) * sin(out_theta), cos(out_theta), sin(out_azi) * sin(out_theta));
						//PhaseFunctionSamplingRecord pfs(m, inci_vec, out_vec);
						Spectrum phaseVal = GetInterpolatePhaseWithAngle(inci_theta, out_theta, (out_azi > M_PI_DBL) ? (2 * M_PI_DBL - out_azi) : out_azi) * m_integralStepZenith * m_integralStepAzi * abs(sin(out_theta));
						for (int s = 0; s < SPECTRUM_SAMPLES; s++) {
							m_phaseDiscrete[s][inciIndex].append(phaseVal[s]);
						}
					}
				}
				for (int s = 0; s < SPECTRUM_SAMPLES; s++) {
					m_phaseDiscrete[s][inciIndex].normalize();
				}
				inciIndex++;
			}
			m_isConfigured = true;
		}

		Spectrum GetInterpolatePhaseWithAngle(Float inciZenithAngle, Float outZenithAngle, Float outDeltaAzimuthAngle) const{
			int inciIndexLower = (int)(inciZenithAngle / m_integralStepZenith);
			int inciIndexUpper = inciIndexLower + 1;
			if (inciIndexUpper >= (M_PI_DBL / m_integralStepZenith) + 1) inciIndexUpper = inciIndexLower;
			int outIndexZenithLower = (int)(outZenithAngle / m_integralStepZenith);
			int outIndexZenithUpper = outIndexZenithLower + 1;
			if (outIndexZenithUpper >= (M_PI_DBL / m_integralStepZenith) + 1) outIndexZenithUpper = outIndexZenithLower;
			int outIndexAziLower = (int)(outDeltaAzimuthAngle / m_integralStepAzi);
			int outIndexAziUpper = outIndexAziLower + 1;
			if (outIndexAziUpper >= (M_PI_DBL / m_integralStepAzi) + 1) outIndexAziUpper = outIndexAziLower;

			Float deltaInc = inciZenithAngle - inciIndexLower * m_integralStepZenith;
			Float deltaOutZenith = outZenithAngle - outIndexZenithLower * m_integralStepZenith;
			Float deltaOutAzi = outDeltaAzimuthAngle - outIndexAziLower * m_integralStepAzi;


			Spectrum incL_zenL_aziL = m_precomputedPhase[inciIndexLower][outIndexZenithLower][outIndexAziLower];
			Spectrum incL_zenL_aziU = m_precomputedPhase[inciIndexLower][outIndexZenithLower][outIndexAziUpper];
			Spectrum incL_zenU_aziL = m_precomputedPhase[inciIndexLower][outIndexZenithUpper][outIndexAziLower];
			Spectrum incL_zenU_aziU = m_precomputedPhase[inciIndexLower][outIndexZenithUpper][outIndexAziUpper];
			Spectrum incL_zenL_interpolatedAzi = (incL_zenL_aziU - incL_zenL_aziL) / m_integralStepAzi * deltaOutAzi + incL_zenL_aziL;
			Spectrum incL_zenU_interpolatedAzi = (incL_zenU_aziU - incL_zenU_aziL) / m_integralStepAzi * deltaOutAzi + incL_zenU_aziL;
			Spectrum incL_inpterpolatedZen_interpolatedAzi = (incL_zenU_interpolatedAzi - incL_zenL_interpolatedAzi) / m_integralStepZenith * deltaOutZenith + incL_zenL_interpolatedAzi;

			Spectrum incU_zenL_aziL = m_precomputedPhase[inciIndexUpper][outIndexZenithLower][outIndexAziLower];
			Spectrum incU_zenL_aziU = m_precomputedPhase[inciIndexUpper][outIndexZenithLower][outIndexAziUpper];
			Spectrum incU_zenU_aziL = m_precomputedPhase[inciIndexUpper][outIndexZenithUpper][outIndexAziLower];
			Spectrum incU_zenU_aziU = m_precomputedPhase[inciIndexUpper][outIndexZenithUpper][outIndexAziUpper];
			Spectrum incU_zenL_interpolatedAzi = (incU_zenL_aziU - incU_zenL_aziL) / m_integralStepAzi * deltaOutAzi + incU_zenL_aziL;
			Spectrum incU_zenU_interpolatedAzi = (incU_zenU_aziU - incU_zenU_aziL) / m_integralStepAzi * deltaOutAzi + incU_zenU_aziL;
			Spectrum incU_inpterpolatedZen_interpolatedAzi = (incU_zenU_interpolatedAzi - incU_zenL_interpolatedAzi) / m_integralStepZenith * deltaOutZenith + incU_zenL_interpolatedAzi;

			Spectrum interpolated = (incU_inpterpolatedZen_interpolatedAzi - incL_inpterpolatedZen_interpolatedAzi) / m_integralStepZenith * deltaInc + incL_inpterpolatedZen_interpolatedAzi;
			return interpolated;
		}


		// the cubic linear interpolation
		Spectrum GetInterpolatedPhase(const PhaseFunctionSamplingRecord& pRec) const {
			//return computePhasefunc(pRec);
			Float incZenith = math::safe_acos(pRec.wi.y);
			Float outZenith = math::safe_acos(pRec.wo.y);

			Float outDeltaAzi = 0;
			Vector v1 = Vector(pRec.wi.x, 0, pRec.wi.z);
			Vector v2 = Vector(pRec.wo.x, 0, pRec.wo.z);
			Float v1length = v1.length();
			Float v2length = v2.length();
			if(v1length !=0 && v2length!=0)
				outDeltaAzi = math::safe_acos(dot(v1/ v1length, v2/ v2length));
			return GetInterpolatePhaseWithAngle(incZenith, outZenith, outDeltaAzi);
		}

		void serialize(Stream *stream, InstanceManager *manager) const {
			PhaseFunction::serialize(stream, manager);
			stream->writeInt(m_ladType);
			m_frontRef.serialize(stream);
			m_backRef.serialize(stream);
			m_transmittance.serialize(stream);
		}

		//This function is only used to verify the integral of the phase function whether equals to 1 or not
		Spectrum validatePhaseFunction() {
			double theta_step = 5 / 180.0 * M_PI_DBL;
			int theta_num = (int)(M_PI_DBL / theta_step);

			double phi_step = 10 / 180.0 * M_PI_DBL;
			int phi_num = (int)(2 * M_PI_DBL / phi_step);
			Spectrum total(0.0);
			MediumSamplingRecord m;
			for (int i = 0; i < theta_num; i++) {
				Float center_theta = (i + 0.5) * theta_step;
				cout << "center_theta: " << center_theta/ M_PI_DBL*180 << endl;
				for (int j = 0; j < phi_num; j++) {
					Float center_phi = (j + 0.5) * phi_step;
					Vector inc_vec = normalize(Vector(0, 1, 0));
					Vector out_vec(-cos(center_phi) * sin(center_theta), cos(center_theta), sin(center_phi) * sin(center_theta));
					PhaseFunctionSamplingRecord pfs(m, inc_vec, out_vec);
					Spectrum phaseVal = computePhasefunc(pfs);
					total += phaseVal * phi_step * theta_step* abs(sin(center_theta));
					cout << "center_phi: " << center_phi / M_PI_DBL * 180 <<" phase: "<< phaseVal.toString() << endl;
				}
			}
			return total;
		}

		//Given wi, wo, compute the phase function value using Gauss Quad
		Spectrum computePhasefunc(const PhaseFunctionSamplingRecord& pRec) const {
			Spectrum scattered(0.0), tot_scattered(0.0);
			double theta_L = 0, theta_U = 0.5 * M_PI_DBL;
			double phi_L = 0, phi_U = 2 * M_PI_DBL;
			double theta_diff = (theta_U - theta_L) * 0.5;
			double theta_midd = (theta_U + theta_L) * 0.5;
			double phi_diff = (phi_U - phi_L) * 0.5;
			double phi_midd = (phi_U + phi_L) * 0.5;

			for (int i = 0; i < gauss_quad_pos.size(); i++) {
				double newTheta = theta_diff * gauss_quad_pos[i] + theta_midd;
				double cosTheta = cos(newTheta), sinTheta = sin(newTheta);
				for (int j = 0; j < gauss_quad_pos.size(); j++) {
					double newPhi = phi_diff * gauss_quad_pos[j] + phi_midd;
					Vector norm_vec(-cos(newPhi) * sinTheta, cosTheta, sin(newPhi) * sinTheta);
					Float OmgLDotOmgS = dot(norm_vec, pRec.wi);
					Float OmgLDotOmgV = dot(norm_vec, pRec.wo);
					Spectrum gamma;
					Spectrum albedo;
					if (OmgLDotOmgS > 0 && OmgLDotOmgV > 0) {
						gamma = m_frontRef;
					}
					else if (OmgLDotOmgS < 0 && OmgLDotOmgV < 0) {
						gamma = m_backRef;
					}
					else {
						gamma = m_transmittance;
					}

					if (OmgLDotOmgS > 0) {
						albedo = m_frontRef + m_transmittance;
					}
					else {
						albedo = m_backRef + m_transmittance;
					}

					Float lad = sin(newTheta); //Spherical

					switch (m_ladType) {
					case ESpherical:
						lad = sin(newTheta); //Spherical
						break;
					case EPlanophile:
						lad = INV_PI * 2 * (1 + cos(2 * newTheta));
						break;
					case EErectophile:
						lad = INV_PI * 2 * (1 - cos(2 * newTheta));
						break;
					case EPlagiophile:
						lad = INV_PI * 2 * (1 - cos(4 * newTheta));
						break;
					case EExtremophile:
						lad = INV_PI * 2 * (1 + cos(4 * newTheta));
						break;
					case EUniform:
						lad = 2 * INV_PI;
						break;
					default:
						break;
					}
					Float common = gauss_quad_coeff[i] * gauss_quad_coeff[j];
					scattered += lad * abs(OmgLDotOmgS) * common * abs(OmgLDotOmgV) * INV_PI_DBL * gamma;
					tot_scattered += lad * abs(OmgLDotOmgS) * common * albedo;
				}
			}
			return scattered / tot_scattered;
		}

		//Given wi, wo, compute the phase function value
		Spectrum computePhasefuncU(const PhaseFunctionSamplingRecord& pRec) const{
			Spectrum scattered(0.0), tot_scattered(0.0);
			double theta_step = 10 / 180.0 * M_PI_DBL;
			int theta_num = (int)(0.5 * M_PI_DBL / theta_step);

			double phi_step = 20 / 180.0 * M_PI_DBL;
			int phi_num = (int)(2 * M_PI_DBL / phi_step);

			for (int i = 0; i < theta_num; i++) {
				Float center_theta = (i + 0.5) * theta_step;
				for (int j = 0; j < phi_num; j++) {
					Float center_phi = (j + 0.5) * phi_step;
					Vector norm_vec(-cos(center_phi) * sin(center_theta), cos(center_theta), sin(center_phi) * sin(center_theta));
					Float OmgLDotOmgS = dot(norm_vec, pRec.wi);
					Float OmgLDotOmgV = dot(norm_vec, pRec.wo);
					Spectrum gamma;
					Spectrum albedo;
					if (OmgLDotOmgS > 0 && OmgLDotOmgV > 0) {
						gamma = m_frontRef;
					}
					else if (OmgLDotOmgS < 0 && OmgLDotOmgV < 0) {
						gamma = m_backRef;
					}
					else {
						gamma = m_transmittance;
					}

					if (OmgLDotOmgS > 0) {
						albedo = m_frontRef + m_transmittance;
					}
					else {
						albedo = m_backRef + m_transmittance;
					}

					Float lad = sin(center_theta); //Spherical

					switch (m_ladType) {
					case ESpherical:
						lad = sin(center_theta); //Spherical
						break;
					case EPlanophile:
						lad = INV_PI * 2 * (1 + cos(2 * center_theta));
						break;
					case EErectophile:
						lad = INV_PI * 2 * (1 - cos(2 * center_theta));
						break;
					case EPlagiophile:
						lad = INV_PI * 2 * (1 - cos(4 * center_theta));
						break;
					case EExtremophile:
						lad = INV_PI * 2 * (1 + cos(4 * center_theta));
						break;
					case EUniform:
						lad = 2 * INV_PI;
						break;
					default:
						break;
					}

					//Float common = sin(center_theta) * phi_step * theta_step;
					Float common = phi_step * theta_step;
					scattered += lad*abs(OmgLDotOmgS) * common *  abs(OmgLDotOmgV) * INV_PI_DBL* gamma;
					tot_scattered += lad*abs(OmgLDotOmgS) * common * albedo;
				}
			}
		//	scattered *= INV_TWOPI_DBL;
		//	tot_scattered *= INV_TWOPI_DBL;
			return scattered / tot_scattered;
		}

		Float sample(PhaseFunctionSamplingRecord &pRec,
			Sampler *sampler) const {
			Point2 sample(sampler->next2D());
			Float inc_zenithAngle = math::safe_acos(pRec.wi.y);
			int inciIndex = (int)(inc_zenithAngle / m_integralStepZenith);
			Float pdf;
			int rand_band = int(SPECTRUM_SAMPLES * sample.x);
			Point2 sample1(sampler->next2D());
			size_t entry = m_phaseDiscrete[rand_band][inciIndex].sampleReuse(sample1.x, pdf);
			int outZenithIndex = int(entry / (size_t(m_azi_num_half) * 2));
			int outAziIndex = entry - size_t(outZenithIndex) * (size_t(m_azi_num_half) * 2);
			Float out_zenith = (outZenithIndex + 0.5) * m_integralStepZenith;
			Float out_azi = (outAziIndex + 0.5) * m_integralStepAzi;  //relative to incident angle, not absolute

			//compute incident azimuth angle
			Float inci_azi = atan2(pRec.wi.z, -pRec.wi.x);  //start from nagative x, clockwise: -180~0, anti-clockwise:0~180
			Float absolute_out_azi = inci_azi + out_azi;

			pRec.wo = Vector(-cos(absolute_out_azi) * sin(out_zenith), cos(out_zenith), sin(absolute_out_azi) * sin(out_zenith));
			return 1.0;
		}

		Float sample(PhaseFunctionSamplingRecord &pRec,
			Float &pdf, Sampler *sampler) const {
			pRec.wo = warp::squareToUniformSphere(sampler->next2D());
			pdf = warp::squareToUniformSpherePdf();
			return 1.0f;
		}

		Spectrum sampleSpec(PhaseFunctionSamplingRecord& pRec,
			Sampler* sampler, int depth) const {
			Point2 sample(sampler->next2D());
			Float inc_zenithAngle = math::safe_acos(pRec.wi.y);
			int inciIndex = (int)(inc_zenithAngle / m_integralStepZenith);
			Float pdf;
			int rand_band = 0;
			if (depth <= 2) {
				rand_band = int(SPECTRUM_SAMPLES * sample.x);
			}
			else {
				rand_band = m_idx_max_albedo;
			}
			Point2 sample1(sampler->next2D());
			size_t entry = m_phaseDiscrete[rand_band][inciIndex].sampleReuse(sample1.x, pdf);
			int outZenithIndex = int(entry / (size_t(m_azi_num_half) * 2));
			int outAziIndex = entry - size_t(outZenithIndex) * (size_t(m_azi_num_half) * 2);
			Float out_zenith = (outZenithIndex + 0.5) * m_integralStepZenith;
			Float out_azi = (outAziIndex + 0.5) * m_integralStepAzi;  //relative to incident angle, not absolute

			//compute incident azimuth angle
			Float inci_azi = atan2(pRec.wi.z, -pRec.wi.x);  //start from nagative x, clockwise: -180~0, anti-clockwise:0~180
			Float absolute_out_azi = inci_azi + out_azi;

			pRec.wo = Vector(-cos(absolute_out_azi) * sin(out_zenith), cos(out_zenith), sin(absolute_out_azi) * sin(out_zenith));
			Spectrum phaseValue = GetInterpolatePhaseWithAngle(inc_zenithAngle, out_zenith, (out_azi > M_PI_DBL) ? (2 * M_PI_DBL - out_azi) : out_azi) * m_integralStepZenith * m_integralStepAzi * abs(sin(out_zenith));
			return phaseValue / pdf;
		}
		Spectrum sampleEFSpec(PhaseFunctionSamplingRecord& pRec,
			Sampler* sampler, int depth,
			FluorMatrix& phasePSVal) const {
			return Spectrum(0.0f);
		}

		Spectrum sampleSpec(PhaseFunctionSamplingRecord& pRec,
			Sampler* sampler) const {
			Point2 sample(sampler->next2D());
			Float inc_zenithAngle = math::safe_acos(pRec.wi.y);
			int inciIndex = (int)(inc_zenithAngle / m_integralStepZenith);
			Float pdf;
			int rand_band = int(SPECTRUM_SAMPLES * sample.x);
			rand_band = 1;
			Point2 sample1(sampler->next2D());
			size_t entry = m_phaseDiscrete[rand_band][inciIndex].sampleReuse(sample1.x, pdf);
			int outZenithIndex = int(entry / (size_t(m_azi_num_half) * 2));
			int outAziIndex = entry - size_t(outZenithIndex) * (size_t(m_azi_num_half) * 2);
			Float out_zenith = (outZenithIndex + 0.5) * m_integralStepZenith;
			Float out_azi = (outAziIndex + 0.5) * m_integralStepAzi;  //relative to incident angle, not absolute

			//compute incident azimuth angle
			Float inci_azi = atan2(pRec.wi.z, -pRec.wi.x);  //start from nagative x, clockwise: -180~0, anti-clockwise:0~180
			Float absolute_out_azi = inci_azi + out_azi;

			pRec.wo = Vector(-cos(absolute_out_azi) * sin(out_zenith), cos(out_zenith), sin(absolute_out_azi) * sin(out_zenith));
			Spectrum phaseValue = GetInterpolatePhaseWithAngle(inc_zenithAngle, out_zenith, (out_azi> M_PI_DBL) ? (2*M_PI_DBL- out_azi): out_azi)* m_integralStepZenith * m_integralStepAzi * abs(sin(out_zenith));
			return phaseValue/pdf;
		}
		Spectrum sampleEFSpec(PhaseFunctionSamplingRecord& pRec,
			Sampler* sampler,
			FluorMatrix& phasePSVal) const {
			return Spectrum(0.0f);
		}

		Spectrum sampleSpec(PhaseFunctionSamplingRecord& pRec,
			Float& pdf, Sampler* sampler) const {
			Point2 sample(sampler->next2D());
			Float inc_zenithAngle = math::safe_acos(pRec.wi.y);
			int inciIndex = (int)(inc_zenithAngle / m_integralStepZenith);
			int rand_band = int(SPECTRUM_SAMPLES * sample.x);
			Point2 sample1(sampler->next2D());
			size_t entry = m_phaseDiscrete[rand_band][inciIndex].sampleReuse(sample1.x, pdf);
			int outZenithIndex = int(entry / (size_t(m_azi_num_half) * 2));
			int outAziIndex = entry - size_t(outZenithIndex) * (size_t(m_azi_num_half) * 2);
			Float out_zenith = (outZenithIndex + 0.5) * m_integralStepZenith;
			Float out_azi = (outAziIndex + 0.5) * m_integralStepAzi;  //relative to incident angle, not absolute

			//compute incident azimuth angle
			Float inci_azi = atan2(pRec.wi.z, -pRec.wi.x);  //start from nagative x, clockwise: -180~0, anti-clockwise:0~180
			Float absolute_out_azi = inci_azi + out_azi;

			pRec.wo = Vector(-cos(absolute_out_azi) * sin(out_zenith), cos(out_zenith), sin(absolute_out_azi) * sin(out_zenith));
			Spectrum phaseValue = GetInterpolatePhaseWithAngle(inc_zenithAngle, out_zenith, (out_azi > M_PI_DBL) ? (2 * M_PI_DBL - out_azi) : out_azi) * m_integralStepZenith * m_integralStepAzi * abs(sin(out_zenith));
			return phaseValue / pdf;
		}
		Spectrum sampleEFSpec(PhaseFunctionSamplingRecord& pRec,
			Float& pdf, Sampler* sampler,
			FluorMatrix& phasePSVal) const {
			return Spectrum(0.0f);
		}

		Spectrum eval(const PhaseFunctionSamplingRecord &pRec) const {
			//return Spectrum(warp::squareToUniformSpherePdf());
		/*	Spectrum interpo = GetInterpolatedPhase(pRec);
			Spectrum comp = computePhasefunc(pRec);*/
			return GetInterpolatedPhase(pRec);
		}
		Spectrum evalWithEF(const PhaseFunctionSamplingRecord& pRec,
			FluorMatrix& phasePSVal) const {
			return Spectrum(0.0f);
		}

		Float getMeanCosine() const {
			return 0.0f;
		}

		std::string toString() const {
			return "IsotropicPhaseFunction[]";
		}

		MTS_DECLARE_CLASS()
private:

	std::vector<std::vector<std::vector<Spectrum>>> m_precomputedPhase;
	std::vector<std::vector<DiscreteDistribution>> m_phaseDiscrete;
	Float m_integralStepZenith;
	Float m_integralStepAzi;
	int m_zenith_num;
	int m_azi_num_half;
	int m_idx_max_albedo;
};


MTS_IMPLEMENT_CLASS_S(VegPhaseFunction, false, PhaseFunction)
MTS_EXPORT_PLUGIN(VegPhaseFunction, "Vegtation phase function");
MTS_NAMESPACE_END
