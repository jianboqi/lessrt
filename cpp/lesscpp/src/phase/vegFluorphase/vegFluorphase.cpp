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
#include "vegFluorphase.h"

MTS_NAMESPACE_BEGIN

//enum class LeafAngleDistribution {
//	Sphirical = 1,
//	Uniform = 2,
//	Planophile = 3,
//	Erectophile = 4, //ÊúÖ±ÐÍ
//	Plagiophile = 5, //ÇãÐ±
//	Extremophile = 6   //¼«¶Ë
//};

class VegFluorPhaseFunction : public PhaseFunction {
public:
	VegFluorPhaseFunction(const Properties& props)
		: PhaseFunction(props) {
		m_opticalName = props.getString("opticalName", "");
		m_frontRef = props.getSpectrum("frontReflectance", Spectrum(0.0));
		m_backRef = props.getSpectrum("backReflectance", Spectrum(0.0));
		m_transmittance = props.getSpectrum("transmittance", Spectrum(0.0));

		// BEGIN Fluorescence
		/* Parse the excitation-fluorescence matrix parameter */
		if (IS_FLUSPECT_PRO) {
			parseEFMatrix(props, "Mb", m_M.m_Mbi);
			parseEFMatrix(props, "Mf", m_M.m_Mfi);
			parseSpectrumTxt(props, "phi", m_phiI);
		}
		else {
			parseEFMatrix(props, "Mbi", m_M.m_Mbi);
			parseEFMatrix(props, "Mfi", m_M.m_Mfi);
			parseEFMatrix(props, "Mbii", m_M.m_Mbii);
			parseEFMatrix(props, "Mfii", m_M.m_Mfii);
			parseSpectrumTxt(props, "phiI", m_phiI);
			parseSpectrumTxt(props, "phiII", m_phiII);
		}
		m_albedo_PS.compute_AddForwardBackwardEF(m_M);
		m_albedo = m_frontRef + m_transmittance;
		if (!m_albedo_PS.compute_Mb_T_inv(m_albedo, m_inv_MbMf))
			Log(EError, "Something wrong when inversing T in Mb at \"VegFluorPhaseFunction\"!");
		parseSpectrumTxt(props, "kChlrel", m_kChlrel);
		// END Fluorescence

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

	VegFluorPhaseFunction(Stream* stream, InstanceManager* manager)
		: PhaseFunction(stream, manager) {
		m_ladType = (ELadType)stream->readInt();
		m_frontRef = Spectrum(stream);
		m_backRef = Spectrum(stream);
		m_M = (FluorMatrixs)stream->readEFMatrix(EFM_LENGTH);
		configure();
	}

	virtual ~VegFluorPhaseFunction() { }

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
		m_precomputedPSIPhase.clear();
		if (!IS_FLUSPECT_PRO)
			m_precomputedPSIIPhase.clear();
		cout << "INFO: Computing phase functions..." << endl;
		m_integralStepZenith = 5 / 180.0 * M_PI_DBL;
		m_integralStepAzi = 20 / 180.0 * M_PI_DBL;
		m_zenith_num = int(M_PI_DBL / m_integralStepZenith);
		m_azi_num_half = int(M_PI_DBL / m_integralStepAzi);

		double phi = 0;
		MediumSamplingRecord m;
		for (int i = 0; i <= m_zenith_num; i++) { //for incident angle
			double inci_theta = i * m_integralStepZenith;
			Vector inci_vec(-cos(phi) * sin(inci_theta), cos(inci_theta), sin(phi) * sin(inci_theta));
			std::vector<std::vector<Spectrum>> outZenithForEachInci;
			std::vector<std::vector<vector<Float>>> outPSIZenithForEachInci;
			std::vector<std::vector<vector<Float>>> outPSIIZenithForEachInci;
			for (int j = 0; j <= m_zenith_num; j++) {  //for scattered zenith angle
				double out_theta = j * m_integralStepZenith;
				std::vector<Spectrum> outAziForEachOutZenith;
				std::vector<vector<Float>> outPSIAziForEachOutZenith;
				std::vector<vector<Float>> outPSIIAziForEachOutZenith;
				for (int k = 0; k <= m_azi_num_half; k++) {
					double out_azi = k * m_integralStepAzi;
					Vector out_vec(-cos(out_azi) * sin(out_theta), cos(out_theta), sin(out_azi) * sin(out_theta));
					PhaseFunctionSamplingRecord pfs(m, inci_vec, out_vec);
					FluorMatrix phasePSVal;
					Spectrum phaseVal = computePhasefunc(pfs, phasePSVal);
					outAziForEachOutZenith.push_back(phaseVal);
					outPSIAziForEachOutZenith.push_back(phasePSVal.m_mi);
					if (!IS_FLUSPECT_PRO)
						outPSIIAziForEachOutZenith.push_back(phasePSVal.m_mii);
				}
				outZenithForEachInci.push_back(outAziForEachOutZenith);
				outPSIZenithForEachInci.push_back(outPSIAziForEachOutZenith);
				if (!IS_FLUSPECT_PRO)
					outPSIIZenithForEachInci.push_back(outPSIIAziForEachOutZenith);
			}
			m_precomputedPhase.push_back(outZenithForEachInci);
			m_precomputedPSIPhase.push_back(outPSIZenithForEachInci);
			if (!IS_FLUSPECT_PRO)
				m_precomputedPSIIPhase.push_back(outPSIIZenithForEachInci);
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
			size_t size_t_m_azi_num_half_size_t_m_azi_num_half_2 = size_t(m_azi_num_half) * size_t(m_azi_num_half) * 2;
			for (int s = 0; s < SPECTRUM_SAMPLES; s++) {
				m_phaseDiscrete[s].push_back(DiscreteDistribution(size_t_m_azi_num_half_size_t_m_azi_num_half_2));
			}
			for (int j = 0; j < m_zenith_num; j++) {  //for scattered zenith angle
				double out_theta = (j + 0.5) * m_integralStepZenith;
				for (int k = 0; k < (m_azi_num_half * 2); k++) {
					double out_azi = (k + 0.5) * m_integralStepAzi;;
					//Vector out_vec(-cos(out_azi) * sin(out_theta), cos(out_theta), sin(out_azi) * sin(out_theta));
					//PhaseFunctionSamplingRecord pfs(m, inci_vec, out_vec);
					Float m_integralStepZenith_m_integralStepAzi_abs_sin_out_theta_ = m_integralStepZenith * m_integralStepAzi * abs(sin(out_theta));
					FluorMatrix phasePSVal;
					Spectrum phaseVal = GetInterpolatePhaseWithAngle(inci_theta, out_theta, (out_azi > M_PI_DBL) ? (2 * M_PI_DBL - out_azi) : out_azi, phasePSVal.m_mi, phasePSVal.m_mii) * m_integralStepZenith_m_integralStepAzi_abs_sin_out_theta_;
					phasePSVal.compute_MultiplyEqual(m_integralStepZenith_m_integralStepAzi_abs_sin_out_theta_);
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

	Spectrum GetInterpolatePhaseWithAngle(Float inciZenithAngle, Float outZenithAngle, Float outDeltaAzimuthAngle,
		std::vector<Float>& interpolatedPhasePSIVal, std::vector<Float>& interpolatedPhasePSIIVal) const {
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

		Float PS_incL_zenL_interpolatedAzi;
		Float PS_incL_zenU_interpolatedAzi;
		Float PS_incL_inpterpolatedZen_interpolatedAzi;

		Float PS_incU_zenL_interpolatedAzi;
		Float PS_incU_zenU_interpolatedAzi;
		Float PS_incU_inpterpolatedZen_interpolatedAzi;
		if (IS_FLUSPECT_PRO) {
			std::vector<Float> PSI_incL_zenL_aziL = m_precomputedPSIPhase[inciIndexLower][outIndexZenithLower][outIndexAziLower];
			std::vector<Float> PSI_incL_zenL_aziU = m_precomputedPSIPhase[inciIndexLower][outIndexZenithLower][outIndexAziUpper];
			std::vector<Float> PSI_incL_zenU_aziL = m_precomputedPSIPhase[inciIndexLower][outIndexZenithUpper][outIndexAziLower];
			std::vector<Float> PSI_incL_zenU_aziU = m_precomputedPSIPhase[inciIndexLower][outIndexZenithUpper][outIndexAziUpper];

			std::vector<Float> PSI_incU_zenL_aziL = m_precomputedPSIPhase[inciIndexUpper][outIndexZenithLower][outIndexAziLower];
			std::vector<Float> PSI_incU_zenL_aziU = m_precomputedPSIPhase[inciIndexUpper][outIndexZenithLower][outIndexAziUpper];
			std::vector<Float> PSI_incU_zenU_aziL = m_precomputedPSIPhase[inciIndexUpper][outIndexZenithUpper][outIndexAziLower];
			std::vector<Float> PSI_incU_zenU_aziU = m_precomputedPSIPhase[inciIndexUpper][outIndexZenithUpper][outIndexAziUpper];

			interpolatedPhasePSIVal.resize(EFM_LENGTH);
			for (register size_t mi = 0; mi < EFM_LENGTH; mi++) {
				PS_incL_zenL_interpolatedAzi = (PSI_incL_zenL_aziU[mi] - PSI_incL_zenL_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSI_incL_zenL_aziL[mi];
				PS_incL_zenU_interpolatedAzi = (PSI_incL_zenU_aziU[mi] - PSI_incL_zenU_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSI_incL_zenU_aziL[mi];
				PS_incL_inpterpolatedZen_interpolatedAzi = (PS_incL_zenU_interpolatedAzi - PS_incL_zenL_interpolatedAzi) / m_integralStepZenith * deltaOutZenith + PS_incL_zenL_interpolatedAzi;
				PS_incU_zenL_interpolatedAzi = (PSI_incU_zenL_aziU[mi] - PSI_incU_zenL_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSI_incU_zenL_aziL[mi];
				PS_incU_zenU_interpolatedAzi = (PSI_incU_zenU_aziU[mi] - PSI_incU_zenU_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSI_incU_zenU_aziL[mi];
				PS_incU_inpterpolatedZen_interpolatedAzi = (PS_incU_zenU_interpolatedAzi - PS_incU_zenL_interpolatedAzi) / m_integralStepZenith * deltaOutZenith + PS_incU_zenL_interpolatedAzi;
				interpolatedPhasePSIVal[mi] = (PS_incU_inpterpolatedZen_interpolatedAzi - PS_incL_inpterpolatedZen_interpolatedAzi) / m_integralStepZenith * deltaInc + PS_incL_inpterpolatedZen_interpolatedAzi;
			}
		}
		else {
			std::vector<Float> PSI_incL_zenL_aziL = m_precomputedPSIPhase[inciIndexLower][outIndexZenithLower][outIndexAziLower];
			std::vector<Float> PSI_incL_zenL_aziU = m_precomputedPSIPhase[inciIndexLower][outIndexZenithLower][outIndexAziUpper];
			std::vector<Float> PSI_incL_zenU_aziL = m_precomputedPSIPhase[inciIndexLower][outIndexZenithUpper][outIndexAziLower];
			std::vector<Float> PSI_incL_zenU_aziU = m_precomputedPSIPhase[inciIndexLower][outIndexZenithUpper][outIndexAziUpper];

			std::vector<Float> PSI_incU_zenL_aziL = m_precomputedPSIPhase[inciIndexUpper][outIndexZenithLower][outIndexAziLower];
			std::vector<Float> PSI_incU_zenL_aziU = m_precomputedPSIPhase[inciIndexUpper][outIndexZenithLower][outIndexAziUpper];
			std::vector<Float> PSI_incU_zenU_aziL = m_precomputedPSIPhase[inciIndexUpper][outIndexZenithUpper][outIndexAziLower];
			std::vector<Float> PSI_incU_zenU_aziU = m_precomputedPSIPhase[inciIndexUpper][outIndexZenithUpper][outIndexAziUpper];

			std::vector<Float> PSII_incL_zenL_aziL = m_precomputedPSIIPhase[inciIndexLower][outIndexZenithLower][outIndexAziLower];
			std::vector<Float> PSII_incL_zenL_aziU = m_precomputedPSIIPhase[inciIndexLower][outIndexZenithLower][outIndexAziUpper];
			std::vector<Float> PSII_incL_zenU_aziL = m_precomputedPSIIPhase[inciIndexLower][outIndexZenithUpper][outIndexAziLower];
			std::vector<Float> PSII_incL_zenU_aziU = m_precomputedPSIIPhase[inciIndexLower][outIndexZenithUpper][outIndexAziUpper];

			std::vector<Float> PSII_incU_zenL_aziL = m_precomputedPSIIPhase[inciIndexUpper][outIndexZenithLower][outIndexAziLower];
			std::vector<Float> PSII_incU_zenL_aziU = m_precomputedPSIIPhase[inciIndexUpper][outIndexZenithLower][outIndexAziUpper];
			std::vector<Float> PSII_incU_zenU_aziL = m_precomputedPSIIPhase[inciIndexUpper][outIndexZenithUpper][outIndexAziLower];
			std::vector<Float> PSII_incU_zenU_aziU = m_precomputedPSIIPhase[inciIndexUpper][outIndexZenithUpper][outIndexAziUpper];

			interpolatedPhasePSIVal.resize(EFM_LENGTH);
			interpolatedPhasePSIIVal.resize(EFM_LENGTH);
			for (register size_t mi = 0; mi < EFM_LENGTH; mi++) {
				PS_incL_zenL_interpolatedAzi = (PSI_incL_zenL_aziU[mi] - PSI_incL_zenL_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSI_incL_zenL_aziL[mi];
				PS_incL_zenU_interpolatedAzi = (PSI_incL_zenU_aziU[mi] - PSI_incL_zenU_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSI_incL_zenU_aziL[mi];
				PS_incL_inpterpolatedZen_interpolatedAzi = (PS_incL_zenU_interpolatedAzi - PS_incL_zenL_interpolatedAzi) / m_integralStepZenith * deltaOutZenith + PS_incL_zenL_interpolatedAzi;
				PS_incU_zenL_interpolatedAzi = (PSI_incU_zenL_aziU[mi] - PSI_incU_zenL_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSI_incU_zenL_aziL[mi];
				PS_incU_zenU_interpolatedAzi = (PSI_incU_zenU_aziU[mi] - PSI_incU_zenU_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSI_incU_zenU_aziL[mi];
				PS_incU_inpterpolatedZen_interpolatedAzi = (PS_incU_zenU_interpolatedAzi - PS_incU_zenL_interpolatedAzi) / m_integralStepZenith * deltaOutZenith + PS_incU_zenL_interpolatedAzi;
				interpolatedPhasePSIVal[mi] = (PS_incU_inpterpolatedZen_interpolatedAzi - PS_incL_inpterpolatedZen_interpolatedAzi) / m_integralStepZenith * deltaInc + PS_incL_inpterpolatedZen_interpolatedAzi;

				PS_incL_zenL_interpolatedAzi = (PSII_incL_zenL_aziU[mi] - PSII_incL_zenL_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSII_incL_zenL_aziL[mi];
				PS_incL_zenU_interpolatedAzi = (PSII_incL_zenU_aziU[mi] - PSII_incL_zenU_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSII_incL_zenU_aziL[mi];
				PS_incL_inpterpolatedZen_interpolatedAzi = (PS_incL_zenU_interpolatedAzi - PS_incL_zenL_interpolatedAzi) / m_integralStepZenith * deltaOutZenith + PS_incL_zenL_interpolatedAzi;
				PS_incU_zenL_interpolatedAzi = (PSII_incU_zenL_aziU[mi] - PSII_incU_zenL_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSII_incU_zenL_aziL[mi];
				PS_incU_zenU_interpolatedAzi = (PSII_incU_zenU_aziU[mi] - PSII_incU_zenU_aziL[mi]) / m_integralStepAzi * deltaOutAzi + PSII_incU_zenU_aziL[mi];
				PS_incU_inpterpolatedZen_interpolatedAzi = (PS_incU_zenU_interpolatedAzi - PS_incU_zenL_interpolatedAzi) / m_integralStepZenith * deltaOutZenith + PS_incU_zenL_interpolatedAzi;
				interpolatedPhasePSIIVal[mi] = (PS_incU_inpterpolatedZen_interpolatedAzi - PS_incL_inpterpolatedZen_interpolatedAzi) / m_integralStepZenith * deltaInc + PS_incL_inpterpolatedZen_interpolatedAzi;
			}
		}
		return interpolated;
	}
	Spectrum GetInterpolatePhaseWithAngle(Float inciZenithAngle, Float outZenithAngle, Float outDeltaAzimuthAngle) const {
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
		if (v1length != 0 && v2length != 0)
			outDeltaAzi = math::safe_acos(dot(v1 / v1length, v2 / v2length));
		return GetInterpolatePhaseWithAngle(incZenith, outZenith, outDeltaAzi);
	}
	// the cubic linear interpolation for Fluor
	Spectrum GetInterpolatedPhase(const PhaseFunctionSamplingRecord& pRec,
		std::vector<Float>& interpolatedPhasePSIVal, std::vector<Float>& interpolatedPhasePSIIVal) const {
		//return computePhasefunc(pRec);
		Float incZenith = math::safe_acos(pRec.wi.y);
		Float outZenith = math::safe_acos(pRec.wo.y);

		Float outDeltaAzi = 0;
		Vector v1 = Vector(pRec.wi.x, 0, pRec.wi.z);
		Vector v2 = Vector(pRec.wo.x, 0, pRec.wo.z);
		Float v1length = v1.length();
		Float v2length = v2.length();
		if (v1length != 0 && v2length != 0)
			outDeltaAzi = math::safe_acos(dot(v1 / v1length, v2 / v2length));
		return GetInterpolatePhaseWithAngle(incZenith, outZenith, outDeltaAzi, interpolatedPhasePSIVal, interpolatedPhasePSIIVal);
	}

	void serialize(Stream* stream, InstanceManager* manager) const {
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
			cout << "center_theta: " << center_theta / M_PI_DBL * 180 << endl;
			for (int j = 0; j < phi_num; j++) {
				Float center_phi = (j + 0.5) * phi_step;
				Vector inc_vec = normalize(Vector(0, 1, 0));
				Vector out_vec(-cos(center_phi) * sin(center_theta), cos(center_theta), sin(center_phi) * sin(center_theta));
				PhaseFunctionSamplingRecord pfs(m, inc_vec, out_vec);
				FluorMatrix phasePSVal;
				Spectrum phaseVal = computePhasefunc(pfs, phasePSVal);
				total += phaseVal * phi_step * theta_step * abs(sin(center_theta));
				cout << "center_phi: " << center_phi / M_PI_DBL * 180 << " phase: " << phaseVal.toString() << endl;
			}
		}
		return total;
	}

	//Given wi, wo, compute the phase function value using Gauss Quad
	Spectrum computePhasefunc(const PhaseFunctionSamplingRecord& pRec, FluorMatrix& phasePSVal) const {
		Spectrum scattered(0.0), tot_scattered(0.0);
		FluorMatrix PS_scattered;
		phasePSVal.setFluorMatrixZeros();
		PS_scattered.setFluorMatrixZeros();
		double theta_L = 0, theta_U = 0.5 * M_PI_DBL;
		double phi_L = 0, phi_U = 2 * M_PI_DBL;
		double theta_diff = (theta_U - theta_L) * 0.5;
		double theta_midd = (theta_U + theta_L) * 0.5;
		double phi_diff = (phi_U - phi_L) * 0.5;
		double phi_midd = (phi_U + phi_L) * 0.5;

		Float lad_abs_OmgLDotOmgS_common = 0;
		Float lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL_isBackward = 0;
		Float lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL_isForward = 0;
		for (int i = 0; i < gauss_quad_pos.size(); i++) {
			double newTheta = theta_diff * gauss_quad_pos[i] + theta_midd;
			double cosTheta = cos(newTheta), sinTheta = sin(newTheta);
			for (int j = 0; j < gauss_quad_pos.size(); j++) {
				double newPhi = phi_diff * gauss_quad_pos[j] + phi_midd;
				Vector norm_vec(-cos(newPhi) * sinTheta, cosTheta, sin(newPhi) * sinTheta);
				Float OmgLDotOmgS = dot(norm_vec, pRec.wi);
				Float OmgLDotOmgV = dot(norm_vec, pRec.wo);
				bool isBackward = true;
				if (OmgLDotOmgS > 0 && OmgLDotOmgV > 0) {
					isBackward = true;
				}
				else if (OmgLDotOmgS < 0 && OmgLDotOmgV < 0) {
					isBackward = true;
				}
				else {
					isBackward = false;
				}

				Float lad = sinTheta; //Spherical

				switch (m_ladType) {
				case ESpherical:
					lad = sinTheta; //Spherical
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
				Float lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL = lad * abs(OmgLDotOmgS) * common * abs(OmgLDotOmgV) * INV_PI_DBL;
				lad_abs_OmgLDotOmgS_common += lad * abs(OmgLDotOmgS) * common;
				if (isBackward) {
					lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL_isBackward += lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL;
				}
				else {
					lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL_isForward += lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL;
				}
			}
		}
		Float a_c, b_c;
		a_c = lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL_isBackward / lad_abs_OmgLDotOmgS_common;
		b_c = lad_abs_OmgLDotOmgS_common_abs_OmgLDotOmgV_INV_PI_DBL_isForward / lad_abs_OmgLDotOmgS_common;
		scattered += a_c * m_frontRef;
		scattered += b_c * m_transmittance;
		PS_scattered.compute_AddForwardBackwardEFbyab(m_M, a_c, b_c);
		Spectrum inv_tot_scattered = 1 / m_albedo;
		FluorMatrix Mb_M_inv = phasePSVal.compute_Mb_M_inv(m_inv_MbMf, m_albedo_PS, inv_tot_scattered, scattered);
		PS_scattered.compute_Mb1xMb2_isFluor2Mixture_mt(phasePSVal, scattered, Mb_M_inv, inv_tot_scattered);
		return scattered * inv_tot_scattered;
	}

	//Given wi, wo, compute the phase function value
	Spectrum computePhasefuncU(const PhaseFunctionSamplingRecord& pRec) const {
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
				scattered += lad * abs(OmgLDotOmgS) * common * abs(OmgLDotOmgV) * INV_PI_DBL * gamma;
				tot_scattered += lad * abs(OmgLDotOmgS) * common * albedo;
			}
		}
		//	scattered *= INV_TWOPI_DBL;
		//	tot_scattered *= INV_TWOPI_DBL;
		return scattered / tot_scattered;
	}

	Float sample(PhaseFunctionSamplingRecord& pRec,
		Sampler* sampler) const {
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

	Float sample(PhaseFunctionSamplingRecord& pRec,
		Float& pdf, Sampler* sampler) const {
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
		Float m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf = m_integralStepZenith * m_integralStepAzi * abs(sin(out_zenith)) / pdf;
		Spectrum phaseValue = GetInterpolatePhaseWithAngle(inc_zenithAngle, out_zenith, (out_azi > M_PI_DBL) ? (2 * M_PI_DBL - out_azi) : out_azi, phasePSVal.m_mi, phasePSVal.m_mii) * m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf;
		phasePSVal.compute_MultiplyEqual(m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf);
		return phaseValue;
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
		Spectrum phaseValue = GetInterpolatePhaseWithAngle(inc_zenithAngle, out_zenith, (out_azi > M_PI_DBL) ? (2 * M_PI_DBL - out_azi) : out_azi) * m_integralStepZenith * m_integralStepAzi * abs(sin(out_zenith));
		return phaseValue / pdf;
	}
	Spectrum sampleEFSpec(PhaseFunctionSamplingRecord& pRec,
		Sampler* sampler,
		FluorMatrix& phasePSVal) const {
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
		Float m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf = m_integralStepZenith * m_integralStepAzi * abs(sin(out_zenith)) / pdf;
		Spectrum phaseValue = GetInterpolatePhaseWithAngle(inc_zenithAngle, out_zenith, (out_azi > M_PI_DBL) ? (2 * M_PI_DBL - out_azi) : out_azi, phasePSVal.m_mi, phasePSVal.m_mii);
		phasePSVal.compute_MultiplyEqual(m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf);
		return phaseValue * m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf;
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
		Float m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf = m_integralStepZenith * m_integralStepAzi * abs(sin(out_zenith)) / pdf;
		Spectrum phaseValue = GetInterpolatePhaseWithAngle(inc_zenithAngle, out_zenith, (out_azi > M_PI_DBL) ? (2 * M_PI_DBL - out_azi) : out_azi, phasePSVal.m_mi, phasePSVal.m_mii) * m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf;
		phasePSVal.compute_MultiplyEqual(m_integralStepZenith_m_integralStepAzi_abs_sin_out_zenith_pdf);
		return phaseValue;
	}

	Spectrum eval(const PhaseFunctionSamplingRecord& pRec) const {
		//return Spectrum(warp::squareToUniformSpherePdf());
	/*	Spectrum interpo = GetInterpolatedPhase(pRec);
		Spectrum comp = computePhasefunc(pRec);*/
		return GetInterpolatedPhase(pRec);
	}
	Spectrum evalWithEF(const PhaseFunctionSamplingRecord& pRec,
		FluorMatrix& phasePSVal) const {
		//return Spectrum(warp::squareToUniformSpherePdf());
	/*	Spectrum interpo = GetInterpolatedPhase(pRec);
		Spectrum comp = computePhasefunc(pRec);*/
		return GetInterpolatedPhase(pRec, phasePSVal.m_mi, phasePSVal.m_mii);
	}

	Float getMeanCosine() const {
		return 0.0f;
	}

	std::string toString() const {
		return "IsotropicPhaseFunction[]";
	}
private:

	/* Parse excitation-fluorescence matrix */
	void parseEFMatrix(const Properties& props, const std::string& name, std::vector<Float>& m) {
		std::vector<std::string> s
			= tokenize(props.getString(name, ""), " ,;\n");
		if (s.size() == 0) {
			SLog(EError, "No %s were supplied!", name.c_str());
		}
		if (s.size() != EFM_LENGTH) {
			SLog(EError, "Invalid number of %s matrix elements!", name.c_str());
		}
		m.resize(EFM_LENGTH);
		char* fend_ptr = NULL;
		for (size_t i = 0; i < s.size(); ++i) {
			Float v = (Float)strtod(s[i].c_str(), &fend_ptr);
			if (*fend_ptr != '\0') {
				SLog(EError, "Could not parse the %s matrix!", name.c_str());
			}
			//if (v < 0) {
			//	SLog(EError, "Invalid %s matrix!", name.c_str());
			//}
			m[i] = v;
		}
	}
	void parseSpectrumTxt(const Properties& props, const std::string& name, Spectrum& m) {
		std::vector<std::string> s = tokenize(props.getString(name, ""), " ,;\n");
		if (s.size() == 0) {
			SLog(EError, "No %s were supplied!", name.c_str());
		}
		if (s.size() != SPECTRUM_SAMPLES) {
			SLog(EError, "Invalid number of %s spectrum elements!", name.c_str());
		}
		char* fend_ptr = NULL;
		for (size_t i = 0; i < s.size(); ++i) {
			Float v = (Float)strtod(s[i].c_str(), &fend_ptr);
			if (*fend_ptr != '\0') {
				SLog(EError, "Could not parse the %s spectrum!", name.c_str());
			}
			if (v < 0) {
				SLog(EError, "Invalid %s spectrum!", name.c_str());
			}
			m[i] = v;
		}
	}
	MTS_DECLARE_CLASS()

private:

	std::vector<std::vector<std::vector<Spectrum>>> m_precomputedPhase;
	std::vector<std::vector<std::vector<vector<Float>>>> m_precomputedPSIPhase;
	std::vector<std::vector<std::vector<vector<Float>>>> m_precomputedPSIIPhase;
	std::vector<std::vector<DiscreteDistribution>> m_phaseDiscrete;
	Float m_integralStepZenith;
	Float m_integralStepAzi;
	int m_zenith_num;
	int m_azi_num_half;
	int m_idx_max_albedo;

	Spectrum m_albedo;
	// BEGIN Fluorescence
	FluorMatrixs m_M;
	FluorMatrix m_albedo_PS;
	std::vector<Float> m_inv_MbMf;

	Spectrum m_kChlrel;
	Spectrum m_phiI;
	Spectrum m_phiII;
	// END Fluorescence
};


MTS_IMPLEMENT_CLASS_S(VegFluorPhaseFunction, false, PhaseFunction)
MTS_EXPORT_PLUGIN(VegFluorPhaseFunction, "Vegtation Fluor phase function");
MTS_NAMESPACE_END
