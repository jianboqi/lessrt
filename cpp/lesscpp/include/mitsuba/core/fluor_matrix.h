/*
	This file is part of LESS_Fluor, implement fluorescence matrix calculation.
*/
#pragma once
#if !defined(__MITSUBA_CORE_FLUOR_MATRIX_H_)
#define __MITSUBA_CORE_FLUOR_MATRIX_H_

#include <mitsuba/mitsuba.h>
#include <mitsuba/core/spectrum.h>
#include <mitsuba/core/logger.h>

MTS_NAMESPACE_BEGIN
const static int EXCITATION_MIN_INDEX = FFEF(".less/EFwlinfo.txt", 1);//exminidx
const static int EXCITATION_SAMPLES = FFEF(".less/EFwlinfo.txt", 2);//exsamples
const static int FLUOR_MIN_INDEX = FFEF(".less/EFwlinfo.txt", 3);//flminidx
const static int FLUOR_SAMPLES = FFEF(".less/EFwlinfo.txt", 4);//flsamples
const static int IS_FLUSPECT_PRO = FFEF(".less/EFwlinfo.txt", 5);//isFluspectPro

const static int EFM_LENGTH = EXCITATION_SAMPLES * FLUOR_SAMPLES;//mLength
const static int EFM_MULTI_LENGTH = EXCITATION_MIN_INDEX + EXCITATION_SAMPLES - FLUOR_MIN_INDEX;//MultiLength
const static int M_IS_0_INDEX = int(0.7863 * EXCITATION_SAMPLES) * FLUOR_SAMPLES + int(0.4550 * FLUOR_SAMPLES);//misZeroindx
const static int FLUOR_0_INDEX = int(0.7583 * SPECTRUM_SAMPLES);//FluorsZeroindx

const static std::vector<int> WANTED_INDEX = FFEF(".less/EFwantedwlidx.txt");

class MTS_EXPORT_CORE FluorMatrixs {
public:
	FluorMatrixs() {
		m_Mbi.resize(EFM_LENGTH);
		m_Mbii.resize(EFM_LENGTH);
		m_Mfi.resize(EFM_LENGTH);
		m_Mfii.resize(EFM_LENGTH);
	}
public:
	std::vector<Float> m_Mbi, m_Mbii, m_Mfi, m_Mfii;
};

class MTS_EXPORT_CORE FluorMatrix {
public:
	FluorMatrix() {
		m_mi.resize(EFM_LENGTH);
		if (IS_FLUSPECT_PRO == 0) {
			m_mii.resize(EFM_LENGTH);
		}
	}
	bool isFluorMatrixNotZeros() {
		if (IS_FLUSPECT_PRO == 0)
			return m_mi[M_IS_0_INDEX] != 0 || m_mii[M_IS_0_INDEX] != 0;
		else
			return m_mi[M_IS_0_INDEX] != 0;
	}
	void setFluorMatrixZeros() {
		if (WANTED_INDEX[0] != -1 && isFluorMatrixNotZeros()) {
			if (IS_FLUSPECT_PRO == 0)
				for (register size_t i = 0; i < EFM_LENGTH; i++) { m_mi[i] = 0; m_mii[i] = 0; }
			else
				for (register size_t i = 0; i < EFM_LENGTH; i++) m_mi[i] = 0;
		}
	}
	void setFluorMatrixForward(FluorMatrixs ms) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t i = 0; i < EFM_LENGTH; i++) {
				m_mi[i] = ms.m_Mfi[i]; m_mii[i] = ms.m_Mfii[i];
			}
		else
			for (register size_t i = 0; i < EFM_LENGTH; i++)
				m_mi[i] = ms.m_Mfi[i];
	}
	void setFluorMatrixForward_M1(FluorMatrixs ms, Float M1) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t i = 0; i < EFM_LENGTH; i++) {
				m_mi[i] = ms.m_Mfi[i] * M1;
				m_mii[i] = ms.m_Mfii[i] * M1;
			}
		else
			for (register size_t i = 0; i < EFM_LENGTH; i++)
				m_mi[i] = ms.m_Mfi[i] * M1;
	}
	void setFluorMatrixBackward(FluorMatrixs ms) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t i = 0; i < EFM_LENGTH; i++) {
				m_mi[i] = ms.m_Mbi[i]; m_mii[i] = ms.m_Mbii[i];
			}
		else
			for (register size_t i = 0; i < EFM_LENGTH; i++)
				m_mi[i] = ms.m_Mbi[i];
	}
	void setFluorMatrixBackward_M1(FluorMatrixs ms, Float M1) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t i = 0; i < EFM_LENGTH; i++) {
				m_mi[i] = ms.m_Mbi[i] * M1;
				m_mii[i] = ms.m_Mbii[i] * M1;
			}
		else
			for (register size_t i = 0; i < EFM_LENGTH; i++)
				m_mi[i] = ms.m_Mbi[i] * M1;
	}
	void compute_AddForwardBackwardEF(FluorMatrixs ms) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t ii = 0; ii < EFM_LENGTH; ii++) {
				m_mi[ii] = ms.m_Mbi[ii] + ms.m_Mfi[ii];
				m_mii[ii] = ms.m_Mbii[ii] + ms.m_Mfii[ii];
			}
		else
			for (register size_t ii = 0; ii < EFM_LENGTH; ii++)
				m_mi[ii] = ms.m_Mbi[ii] + ms.m_Mfi[ii];
	}
	void compute_AddForwardBackwardEFbyab(FluorMatrixs ms, Float a, Float b) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t ii = 0; ii < EFM_LENGTH; ii++) {
				m_mi[ii] = a * ms.m_Mbi[ii] + b * ms.m_Mfi[ii];
				m_mii[ii] = a * ms.m_Mbii[ii] + b * ms.m_Mfii[ii];
			}
		else
			for (register size_t ii = 0; ii < EFM_LENGTH; ii++)
				m_mi[ii] = a * ms.m_Mbi[ii] + b * ms.m_Mfi[ii];
	}
	void compute_PlusEqual(FluorMatrix tm) {
		if (tm.isFluorMatrixNotZeros())
			if (IS_FLUSPECT_PRO == 0)
				for (register size_t ii = 0; ii < EFM_LENGTH; ii++) {
					m_mi[ii] += tm.m_mi[ii];
					m_mii[ii] += tm.m_mii[ii];
				}
			else
				for (register size_t ii = 0; ii < EFM_LENGTH; ii++)
					m_mi[ii] += tm.m_mi[ii];
	}
	void compute_PlusEqual_M1(FluorMatrix tm, Float M1) {
		if (tm.isFluorMatrixNotZeros() && M1 != 1)
			if (IS_FLUSPECT_PRO == 0)
				for (register size_t ii = 0; ii < EFM_LENGTH; ii++) {
					m_mi[ii] += tm.m_mi[ii] * M1;
					m_mii[ii] += tm.m_mii[ii] * M1;
				}
			else
				for (register size_t ii = 0; ii < EFM_LENGTH; ii++)
					m_mi[ii] += tm.m_mi[ii] * M1;
	}
	void compute_MultiplyEqual(Float M) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t ii = 0; ii < EFM_LENGTH; ii++) {
				m_mi[ii] *= M;
				m_mii[ii] *= M;
			}
		else
			for (register size_t ii = 0; ii < EFM_LENGTH; ii++)
				m_mi[ii] *= M;
	}
	void compute_DivideEqual(Float M) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t ii = 0; ii < EFM_LENGTH; ii++) {
				m_mi[ii] /= M;
				m_mii[ii] /= M;
			}
		else
			for (register size_t ii = 0; ii < EFM_LENGTH; ii++)
				m_mi[ii] /= M;
	}
	void compute_EqualMb_M1(FluorMatrix tm, Float M) {
		if (IS_FLUSPECT_PRO) {
			for (register size_t i = 0; i < EFM_LENGTH; i++) {
				m_mi[i] = M * tm.m_mi[i];
			}
		}
		else {
			for (register size_t i = 0; i < EFM_LENGTH; i++) {
				m_mi[i] = M * tm.m_mi[i];
				m_mii[i] = M * tm.m_mii[i];
			}
		}
	}
	void compute_Mb1xMb2_isFluor2Mixture(Spectrum throughput, FluorMatrix tm, Spectrum bsdfWeight) {
		Float AddmimiiMultitmi, AddmimiiMultitmii, Addmimii;
		FluorMatrix mt;
		if (IS_FLUSPECT_PRO == 0) {
			if (isFluorMatrixNotZeros()) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						AddmimiiMultitmi = 0;
						AddmimiiMultitmii = 0;
						for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
							Addmimii = m_mi[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] + m_mii[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii];
							AddmimiiMultitmi += Addmimii * tm.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
							AddmimiiMultitmii += Addmimii * tm.m_mii[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
						}
						mt.m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j] +
							m_mi[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmi;
						mt.m_mii[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mii[i * FLUOR_SAMPLES + j] +
							m_mii[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmii;
					}
				}
				m_mi = mt.m_mi; m_mii = mt.m_mii;
			}
			else {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j];
						m_mii[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mii[i * FLUOR_SAMPLES + j];
					}
				}
			}
		}
		else {
			if (isFluorMatrixNotZeros()) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						AddmimiiMultitmi = 0;
						for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
							AddmimiiMultitmi += m_mi[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] * tm.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
						}
						mt.m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j] +
							m_mi[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmi;
					}
				}
				m_mi = mt.m_mi;
			}
			else {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j];
					}
				}
			}
		}

	}
	void compute_Mb1xMb2_isNotFluor2Mixture(Spectrum bsdfWeight) {
		if (WANTED_INDEX[0] != -1 && isFluorMatrixNotZeros() && bsdfWeight[FLUOR_0_INDEX] != 1) {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						m_mi[i * FLUOR_SAMPLES + j] *= bsdfWeight[FLUOR_MIN_INDEX + j];
						m_mii[i * FLUOR_SAMPLES + j] *= bsdfWeight[FLUOR_MIN_INDEX + j];
					}
				}
			}
			else {
				if (isFluorMatrixNotZeros() && bsdfWeight[FLUOR_0_INDEX] != 1) {
					for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
						for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
							m_mi[i * FLUOR_SAMPLES + j] *= bsdfWeight[FLUOR_MIN_INDEX + j];
						}
					}
				}
			}
		}
	}
	void compute_MbxPower(Spectrum power_e, Spectrum& powerPSI, Spectrum& powerPSII, Spectrum& power) {
		if (isFluorMatrixNotZeros()) {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					for (register size_t exj = 0; exj < EXCITATION_SAMPLES; ++exj) {
						powerPSI[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mi[exj * FLUOR_SAMPLES + fli];
						powerPSII[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mii[exj * FLUOR_SAMPLES + fli];
					}
				}
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli)
					power[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli] + powerPSII[FLUOR_MIN_INDEX + fli];
			}
			else {
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					for (register size_t exj = 0; exj < EXCITATION_SAMPLES; ++exj) {
						powerPSI[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mi[exj * FLUOR_SAMPLES + fli];
					}
				}
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli)
					power[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli];
			}
		}
	}
	void compute_MbxPower(Spectrum power_e, Spectrum& powerPSI, Spectrum& powerPSII) {
		if (isFluorMatrixNotZeros()) {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					for (register size_t exj = 0; exj < EXCITATION_SAMPLES; ++exj) {
						powerPSI[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mi[exj * FLUOR_SAMPLES + fli];
						powerPSII[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mii[exj * FLUOR_SAMPLES + fli];
					}
				}
			}
			else {
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					for (register size_t exj = 0; exj < EXCITATION_SAMPLES; ++exj) {
						powerPSI[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mi[exj * FLUOR_SAMPLES + fli];
					}
				}
			}
		}
	}
	void compute_MbxPower(Spectrum power_e, Spectrum powerPSI, Spectrum powerPSII, Spectrum& LiAll, Spectrum& LiPSI, Spectrum& LiPSII) {
		if (isFluorMatrixNotZeros()) {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					for (register size_t exj = 0; exj < EXCITATION_SAMPLES; ++exj) {
						powerPSI[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mi[exj * FLUOR_SAMPLES + fli];
						powerPSII[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mii[exj * FLUOR_SAMPLES + fli];
					}
				}
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					LiPSI[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli];
					LiPSII[FLUOR_MIN_INDEX + fli] += powerPSII[FLUOR_MIN_INDEX + fli];
					LiAll[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli] + powerPSII[FLUOR_MIN_INDEX + fli];
				}
			}
			else {
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					for (register size_t exj = 0; exj < EXCITATION_SAMPLES; ++exj) {
						powerPSI[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mi[exj * FLUOR_SAMPLES + fli];
					}
				}
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					LiPSI[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli];
					LiAll[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli];
				}
			}
		}
	}
	void compute_MbxPower(Spectrum power_e, Spectrum powerPSI, Spectrum powerPSII, Spectrum& LiAll, Spectrum& LiPSI, Spectrum& LiPSII, Float weight) {
		if (isFluorMatrixNotZeros()) {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					for (register size_t exj = 0; exj < EXCITATION_SAMPLES; ++exj) {
						powerPSI[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mi[exj * FLUOR_SAMPLES + fli];// *weight;
						powerPSII[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mii[exj * FLUOR_SAMPLES + fli];// *weight;
					}
				}
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					LiPSI[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli] * weight;
					LiPSII[FLUOR_MIN_INDEX + fli] += powerPSII[FLUOR_MIN_INDEX + fli] * weight;
					LiAll[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli] + powerPSII[FLUOR_MIN_INDEX + fli] * weight;
				}
			}
			else {
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					for (register size_t exj = 0; exj < EXCITATION_SAMPLES; ++exj) {
						powerPSI[FLUOR_MIN_INDEX + fli] += power_e[EXCITATION_MIN_INDEX + exj] * m_mi[exj * FLUOR_SAMPLES + fli];// *weight;
					}
				}
				for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
					LiPSI[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli] * weight;
					LiAll[FLUOR_MIN_INDEX + fli] += powerPSI[FLUOR_MIN_INDEX + fli] * weight;
				}
			}
		}
	}
	void compute_Mb1xMb2_isFluor2Mixture_mt(FluorMatrix& mt, Spectrum throughput, FluorMatrix tm, Spectrum bsdfWeight) {
		Float AddmimiiMultitmi, AddmimiiMultitmii, Addmimii;
		if (IS_FLUSPECT_PRO == 0) {
			if (isFluorMatrixNotZeros()) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						AddmimiiMultitmi = 0;
						AddmimiiMultitmii = 0;
						for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
							Addmimii = m_mi[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] + m_mii[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii];
							AddmimiiMultitmi += Addmimii * tm.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
							AddmimiiMultitmii += Addmimii * tm.m_mii[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
						}
						mt.m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j] +
							m_mi[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmi;
						mt.m_mii[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mii[i * FLUOR_SAMPLES + j] +
							m_mii[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmii;
					}
				}
			}
			else {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						mt.m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j];
						mt.m_mii[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mii[i * FLUOR_SAMPLES + j];
					}
				}
			}
		}
		else {
			if (isFluorMatrixNotZeros()) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						AddmimiiMultitmi = 0;
						for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
							AddmimiiMultitmi += m_mi[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] * tm.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
						}
						mt.m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j] +
							m_mi[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmi;
					}
				}
			}
			else {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						mt.m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j];
					}
				}
			}
		}
	}
	void compute_Mb1xMb2_isNotFluor2Mixture_mt(FluorMatrix& mt, Spectrum bsdfWeight) {
		if (isFluorMatrixNotZeros()) {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						mt.m_mi[i * FLUOR_SAMPLES + j] = m_mi[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j];
						mt.m_mii[i * FLUOR_SAMPLES + j] = m_mii[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j];
					}
				}
			}
			else {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						mt.m_mi[i * FLUOR_SAMPLES + j] = m_mi[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j];
					}
				}
			}
		}
		else {
			mt.setFluorMatrixZeros();
		}
	}
	void compute_Mb1xMb2_isFluor2Mixture_M1(Spectrum throughput, FluorMatrix tm, Spectrum bsdfWeight, Float M1) {
		Float AddmimiiMultitmi, AddmimiiMultitmii, Addmimii;
		FluorMatrix mt;
		if (isFluorMatrixNotZeros()) {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						AddmimiiMultitmi = 0;
						AddmimiiMultitmii = 0;
						for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
							Addmimii = m_mi[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] + m_mii[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii];
							AddmimiiMultitmi += Addmimii * tm.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
							AddmimiiMultitmii += Addmimii * tm.m_mii[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
						}
						mt.m_mi[i * FLUOR_SAMPLES + j] = M1 * (throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j] +
							m_mi[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmi);
						mt.m_mii[i * FLUOR_SAMPLES + j] = M1 * (throughput[EXCITATION_MIN_INDEX + i] * tm.m_mii[i * FLUOR_SAMPLES + j] +
							m_mii[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmii);
					}
				}
				m_mi = mt.m_mi; m_mii = mt.m_mii;
			}
			else {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						AddmimiiMultitmi = 0;
						for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
							AddmimiiMultitmi += m_mi[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] * tm.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
						}
						mt.m_mi[i * FLUOR_SAMPLES + j] = M1 * (throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j] +
							m_mi[i * FLUOR_SAMPLES + j] * bsdfWeight[FLUOR_MIN_INDEX + j] + AddmimiiMultitmi);
					}
				}
				m_mi = mt.m_mi;
			}
		}
		else {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j] * M1;
						m_mii[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mii[i * FLUOR_SAMPLES + j] * M1;
					}
				}
			}
			else {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						m_mi[i * FLUOR_SAMPLES + j] = throughput[EXCITATION_MIN_INDEX + i] * tm.m_mi[i * FLUOR_SAMPLES + j] * M1;
					}
				}
			}
		}
	}
	void compute_Mb1xMb2_isNotFluor2Mixture_M1(Spectrum bsdfWeight, Float M1) {
		FluorMatrix mt;
		if (isFluorMatrixNotZeros()) {
			if (IS_FLUSPECT_PRO == 0) {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						m_mi[i * FLUOR_SAMPLES + j] *= bsdfWeight[FLUOR_MIN_INDEX + j] * M1;
						m_mii[i * FLUOR_SAMPLES + j] *= bsdfWeight[FLUOR_MIN_INDEX + j] * M1;
					}
				}
			}
			else {
				for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
					for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
						m_mi[i * FLUOR_SAMPLES + j] *= bsdfWeight[FLUOR_MIN_INDEX + j] * M1;
					}
				}
			}
		}
		else {
			setFluorMatrixZeros();
		}
	}
	void compute_PlusEqual_Mb1xMb2_isFluor2Mixture_M1(FluorMatrix eachFluorAlbedo, Spectrum eachAlbedo, FluorMatrix eachphaseFluorVal, Spectrum eachphaseval, Float M1) {
		Float AddmimiiMultitmi, AddmimiiMultitmii, Addmimii;
		if (IS_FLUSPECT_PRO == 0) {
			for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
				for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
					AddmimiiMultitmi = 0;
					AddmimiiMultitmii = 0;
					for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
						Addmimii = eachFluorAlbedo.m_mi[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] + eachFluorAlbedo.m_mii[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii];
						AddmimiiMultitmi += Addmimii * eachphaseFluorVal.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
						AddmimiiMultitmii += Addmimii * eachphaseFluorVal.m_mii[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
					}
					m_mi[i * FLUOR_SAMPLES + j] += M1 * (eachAlbedo[EXCITATION_MIN_INDEX + i] * eachphaseFluorVal.m_mi[i * FLUOR_SAMPLES + j] +
						eachFluorAlbedo.m_mi[i * FLUOR_SAMPLES + j] * eachphaseval[FLUOR_MIN_INDEX + j] + AddmimiiMultitmi);
					m_mii[i * FLUOR_SAMPLES + j] += M1 * (eachAlbedo[EXCITATION_MIN_INDEX + i] * eachphaseFluorVal.m_mii[i * FLUOR_SAMPLES + j] +
						eachFluorAlbedo.m_mii[i * FLUOR_SAMPLES + j] * eachphaseval[FLUOR_MIN_INDEX + j] + AddmimiiMultitmii);
				}
			}
		}
		else {
			for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
				for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
					AddmimiiMultitmi = 0;
					for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
						AddmimiiMultitmi += eachFluorAlbedo.m_mi[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] * eachphaseFluorVal.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
					}
					m_mi[i * FLUOR_SAMPLES + j] += M1 * (eachAlbedo[EXCITATION_MIN_INDEX + i] * eachphaseFluorVal.m_mi[i * FLUOR_SAMPLES + j] +
						eachFluorAlbedo.m_mi[i * FLUOR_SAMPLES + j] * eachphaseval[FLUOR_MIN_INDEX + j] + AddmimiiMultitmi);
				}
			}
		}
	}
	void compute_FluorSpectrum_PlusEqual(Spectrum& base_PS1, Spectrum& base_PS2, Spectrum add_FS) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] += add_FS[FLUOR_MIN_INDEX + fli];
				base_PS2[FLUOR_MIN_INDEX + fli] += add_FS[FLUOR_MIN_INDEX + fli];
			}
		else
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli)
				base_PS1[FLUOR_MIN_INDEX + fli] += add_FS[FLUOR_MIN_INDEX + fli];
	}
	void compute_FluorSpectrum_PlusEqual(Spectrum& base_PS1, Spectrum& base_PS2, Spectrum add_PS1, Spectrum add_PS2) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] += add_PS1[FLUOR_MIN_INDEX + fli];
				base_PS2[FLUOR_MIN_INDEX + fli] += add_PS2[FLUOR_MIN_INDEX + fli];
			}
		else
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli)
				base_PS1[FLUOR_MIN_INDEX + fli] += add_PS1[FLUOR_MIN_INDEX + fli];
	}
	void compute_isFluspectPro_FluorSpectrum_PlusEqual(Spectrum& base_PS1, Spectrum& base_PS2, Spectrum add_PS1, Spectrum add_PS2) {
		for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
			base_PS1[FLUOR_MIN_INDEX + fli] += add_PS1[FLUOR_MIN_INDEX + fli];
			base_PS2[FLUOR_MIN_INDEX + fli] += add_PS2[FLUOR_MIN_INDEX + fli];
		}
	}
	void compute_isNotFluspectPro_FluorSpectrum_PlusEqual(Spectrum& base_PS, Spectrum add_PS) {
		for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
			base_PS[FLUOR_MIN_INDEX + fli] += add_PS[FLUOR_MIN_INDEX + fli];
		}
	}
	void compute_FluorSpectrum_PlusEqual_M1(Spectrum& base_PS1, Spectrum& base_PS2, Spectrum M1, Spectrum MPS1, Spectrum MPS2) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] += M1[FLUOR_MIN_INDEX + fli] * MPS1[FLUOR_MIN_INDEX + fli];
				base_PS2[FLUOR_MIN_INDEX + fli] += M1[FLUOR_MIN_INDEX + fli] * MPS2[FLUOR_MIN_INDEX + fli];
			}
		else
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] += M1[FLUOR_MIN_INDEX + fli] * MPS1[FLUOR_MIN_INDEX + fli];
			}
	}
	void compute_FluorSpectrum_PlusEqual_M1(Spectrum& base_PS1, Spectrum& base_PS2, Float M1, Spectrum MPS1, Spectrum MPS2) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] += M1 * MPS1[FLUOR_MIN_INDEX + fli];
				base_PS2[FLUOR_MIN_INDEX + fli] += M1 * MPS2[FLUOR_MIN_INDEX + fli];
			}
		else
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] += M1 * MPS1[FLUOR_MIN_INDEX + fli];
			}
	}
	void compute_FluorSpectrum_MultiplyEqual(Spectrum& base_PS1, Spectrum& base_PS2, Spectrum mult_FS) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] *= mult_FS[FLUOR_MIN_INDEX + fli];
				base_PS2[FLUOR_MIN_INDEX + fli] *= mult_FS[FLUOR_MIN_INDEX + fli];
			}
		else
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] *= mult_FS[FLUOR_MIN_INDEX + fli];
			}
	}
	void compute_FluorSpectrum_Equal_M1(Spectrum& base_PS1, Spectrum& base_PS2, Spectrum M1, Spectrum MPS1, Spectrum MPS2) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] = M1[FLUOR_MIN_INDEX + fli] * MPS1[FLUOR_MIN_INDEX + fli];
				base_PS2[FLUOR_MIN_INDEX + fli] = M1[FLUOR_MIN_INDEX + fli] * MPS2[FLUOR_MIN_INDEX + fli];
			}
		else
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] = M1[FLUOR_MIN_INDEX + fli] * MPS1[FLUOR_MIN_INDEX + fli];
			}
	}
	void compute_FluorSpectrum_Equal_M2(Spectrum& base_PS1, Spectrum& base_PS2, Float M1, Float M2, Spectrum MPS1_1, Spectrum MPS2_1, Spectrum MPS1_2, Spectrum MPS2_2) {
		if (IS_FLUSPECT_PRO == 0)
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] = M1 * MPS1_1[FLUOR_MIN_INDEX + fli] * MPS1_2[FLUOR_MIN_INDEX + fli];
				base_PS2[FLUOR_MIN_INDEX + fli] = M2 * MPS2_1[FLUOR_MIN_INDEX + fli] * MPS2_2[FLUOR_MIN_INDEX + fli];
			}
		else
			for (register size_t fli = 0; fli < FLUOR_SAMPLES; ++fli) {
				base_PS1[FLUOR_MIN_INDEX + fli] = M1 * MPS1_1[FLUOR_MIN_INDEX + fli] * MPS1_2[FLUOR_MIN_INDEX + fli];
			}
	}
	/// Compute the inverse of a square matrix using the Gauss-Jordan algorithm
	bool compute_Mb_T_inv(Spectrum& Albedo, std::vector<Float>& invPS) {
		invPS.resize(EFM_LENGTH);
		int N = SPECTRUM_SAMPLES;
		std::vector<int> indxc, indxr, ipiv;
		indxc.resize(N);
		indxr.resize(N);
		ipiv.resize(N);
		for (register size_t i = 0; i < N; i++) {
			ipiv[i] = 0;
		}
		std::vector<std::vector<Float>>target_m;
		target_m.resize(N);
		for (register size_t i = 0; i < N; i++) {
			target_m[i].resize(N);
			target_m[i][i] = Albedo[i];
		}
		if (IS_FLUSPECT_PRO) {
			for (register size_t i = 0; i < EXCITATION_SAMPLES; i++) {
				for (register size_t j = 0; j < FLUOR_SAMPLES; j++) {
					target_m[i][FLUOR_MIN_INDEX + j] += m_mi[i * FLUOR_SAMPLES + j];
				}
			}
		}
		else {
			for (register size_t i = 0; i < EXCITATION_SAMPLES; i++) {
				for (register size_t j = 0; j < FLUOR_SAMPLES; j++) {
					target_m[i][FLUOR_MIN_INDEX + j] += m_mi[i * FLUOR_SAMPLES + j] + m_mii[i * FLUOR_SAMPLES + j];
				}
			}
		}

		//-------------Gauss-Jordan algorithm--------------
		for (register size_t i = 0; i < N; i++) {
			int irow = -1, icol = -1;
			Float big = 0;
			for (register size_t j = 0; j < N; j++) {
				if (ipiv[j] != 1) {
					for (register size_t k = 0; k < N; k++) {
						if (ipiv[k] == 0) {
							if (std::abs(target_m[j][k]) >= big) {
								big = std::abs(target_m[j][k]);
								irow = j;
								icol = k;
							}
						}
						else if (ipiv[k] > 1) {
							return false;
						}
					}
				}
			}
			++ipiv[icol];
			if (irow != icol) {
				for (register size_t k = 0; k < N; ++k)
					std::swap(target_m[irow][k], target_m[icol][k]);
			}
			indxr[i] = irow;
			indxc[i] = icol;
			if (target_m[icol][icol] == 0)
				return false;
			Float pivinv = 1.f / target_m[icol][icol];
			target_m[icol][icol] = 1.f;
			for (register size_t j = 0; j < N; j++)
				target_m[icol][j] *= pivinv;
			for (register size_t j = 0; j < N; j++) {
				if (j != icol) {
					Float save = target_m[j][icol];
					target_m[j][icol] = 0;
					for (register size_t k = 0; k < N; k++)
						target_m[j][k] -= target_m[icol][k] * save;
				}
			}
		}
		for (register int j = N - 1; j >= 0; j--) {
			if (indxr[j] != indxc[j]) {
				for (register size_t k = 0; k < N; k++)
					std::swap(target_m[k][indxr[j]], target_m[k][indxc[j]]);
			}
		}
		//-------------Gauss-Jordan algorithm--------------

		for (register size_t i = 0; i < N; i++) {
			target_m[i][i] -= 1 / Albedo[i];
		}
		for (register size_t i = 0; i < EXCITATION_SAMPLES; i++) {
			for (register size_t j = 0; j < FLUOR_SAMPLES; j++) {
				invPS[i * FLUOR_SAMPLES + j] = target_m[i][FLUOR_MIN_INDEX + j];
			}
		}
		return true;
	}
	FluorMatrix compute_Mb_M_inv(std::vector<Float> invPS, FluorMatrix mRec_FluorsigmaS, Spectrum mRec_sigmaS_inv, Spectrum phaseval) {
		Float AddPSI, AddPSII, AddmimiiMultitmi, AddmimiiMultitmii, Addmimii;
		FluorMatrix Mb_M_inv;
		if (IS_FLUSPECT_PRO) {
			for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
				for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
					AddPSI = 0;
					for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
						AddPSI += invPS[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] *
							mRec_FluorsigmaS.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
					}
					Mb_M_inv.m_mi[i * FLUOR_SAMPLES + j] = -mRec_sigmaS_inv[EXCITATION_MIN_INDEX + i] * mRec_FluorsigmaS.m_mi[i * FLUOR_SAMPLES + j] *
						mRec_sigmaS_inv[FLUOR_MIN_INDEX + j] - AddPSI * mRec_sigmaS_inv[FLUOR_MIN_INDEX + j];
				}
			}
		}
		else {
			for (register size_t i = 0; i < EXCITATION_SAMPLES; ++i) {
				for (register size_t j = 0; j < FLUOR_SAMPLES; ++j) {
					AddPSI = 0, AddPSII = 0;
					for (register size_t ii = 0; ii < EFM_MULTI_LENGTH; ++ii) {
						AddPSI += invPS[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] *
							mRec_FluorsigmaS.m_mi[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
						AddPSII += invPS[i * FLUOR_SAMPLES + EXCITATION_MIN_INDEX + ii] *
							mRec_FluorsigmaS.m_mii[(FLUOR_MIN_INDEX + ii) * FLUOR_SAMPLES + j];
					}
					Mb_M_inv.m_mi[i * FLUOR_SAMPLES + j] = -mRec_sigmaS_inv[EXCITATION_MIN_INDEX + i] * mRec_FluorsigmaS.m_mi[i * FLUOR_SAMPLES + j] *
						mRec_sigmaS_inv[FLUOR_MIN_INDEX + j] - AddPSI * mRec_sigmaS_inv[FLUOR_MIN_INDEX + j];
					Mb_M_inv.m_mii[i * FLUOR_SAMPLES + j] = -mRec_sigmaS_inv[EXCITATION_MIN_INDEX + i] * mRec_FluorsigmaS.m_mii[i * FLUOR_SAMPLES + j] *
						mRec_sigmaS_inv[FLUOR_MIN_INDEX + j] - AddPSII * mRec_sigmaS_inv[FLUOR_MIN_INDEX + j];
				}
			}
		}
		return Mb_M_inv;
	}

public:
	std::vector<Float> m_mi, m_mii;
};

MTS_NAMESPACE_END
#endif /* __MITSUBA_CORE_FLUOR_MATRIX_H_ */