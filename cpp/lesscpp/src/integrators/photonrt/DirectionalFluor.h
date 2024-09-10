#pragma once

//Implementing a storage class to store directional Fluor/radiance
//value for different directions

#if !defined(_DIRECTIONAL_Fluor_)
#define _DIRECTIONAL_Fluor_

#include <iostream>
#include <vector>
#include <fstream>
#include "photonRTUtils.h"
#include <mitsuba/core/spectrum.h>
#include <mitsuba/mitsuba.h>
#include <boost/algorithm/string.hpp>
#include <iomanip>      // std::setprecision

using namespace std;

MTS_NAMESPACE_BEGIN

class DirectionalFluor :public Object {
public:
	DirectionalFluor(int NumberOfDirections) {
		m_numOfDirections = NumberOfDirections;
		PhotonRTUtils::generationDiscreteDirections(NumberOfDirections, accumulated_ZenithAngle, accumulated_azimuthAngle);
		numberOfZenith = accumulated_ZenithAngle.size();
		for (int i = 0; i < numberOfZenith; i++) {
			numberOfAzimuth.push_back(accumulated_azimuthAngle[i].size());
			vector<Spectrum> aziTmp;
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				aziTmp.push_back(Spectrum(0.0));
			}
			m_fluors_All.push_back(aziTmp);
			m_fluors_PSI.push_back(aziTmp);
			m_fluors_PSII.push_back(aziTmp);

		}
	}

	void unserialize(Stream* stream) {
		numberOfZenith = stream->readInt();
		numberOfAzimuth.resize(numberOfZenith);
		stream->readIntArray(numberOfAzimuth.data(), numberOfZenith);
		accumulated_ZenithAngle.resize(numberOfZenith);
		stream->readDoubleArray(accumulated_ZenithAngle.data(), numberOfZenith);

		for (int i = 0; i < numberOfZenith; i++) {
			accumulated_azimuthAngle.resize(numberOfAzimuth[i]);
			stream->readDoubleArray(accumulated_azimuthAngle[i].data(), numberOfAzimuth[i]);
		}

		for (int i = 0; i < numberOfZenith; i++) {
			vector<Spectrum> aziTmp;
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				aziTmp.push_back(Spectrum(stream));
			}
			getFluorAllData().push_back(aziTmp);
			getFluorPSIData().push_back(aziTmp);
			getFluorPSIIData().push_back(aziTmp);
		}
		m_verticalIrradiance = Spectrum(stream);
		m_nVirtualDirections = stream->readInt();
		m_virtualDirZenith.resize(m_nVirtualDirections);
		m_virtualDirAzimuth.resize(m_nVirtualDirections);
		stream->readDoubleArray(m_virtualDirZenith.data(), m_nVirtualDirections);
		stream->readDoubleArray(m_virtualDirAzimuth.data(), m_nVirtualDirections);
		m_virtualDirXYZ.resize(m_nVirtualDirections * 3);
		stream->readDoubleArray(m_virtualDirXYZ.data(), m_nVirtualDirections * 3);

		m_virtualFluors_All.resize(m_nVirtualDirections);
		m_virtualFluors_PSI.resize(m_nVirtualDirections);
		m_virtualFluors_PSII.resize(m_nVirtualDirections);
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualFluors_All[i] = Spectrum(stream);
			m_virtualFluors_PSI[i] = Spectrum(stream);
			m_virtualFluors_PSII[i] = Spectrum(stream);
		}

		m_numAngularDirection = stream->readInt();
		m_anglarDirections.resize(m_numAngularDirection);
		m_virtualDetectorFluors_All.resize(m_numAngularDirection);
		m_virtualDetectorFluors_PSI.resize(m_numAngularDirection);
		m_virtualDetectorFluors_PSII.resize(m_numAngularDirection);
		for (int i = 0; i < m_numAngularDirection; i++) {
			m_anglarDirections[i] = AngularDirection(stream->readDouble(), stream->readDouble(), stream->readDouble());
			m_virtualDetectorFluors_All[i] = Spectrum(stream);
			m_virtualDetectorFluors_PSI[i] = Spectrum(stream);
			m_virtualDetectorFluors_PSII[i] = Spectrum(stream);
		}
		m_isTheramlMode = stream->readBool();
		m_wavelengths = Spectrum(stream);
	}

	void serialize(Stream* stream) const {
		stream->writeInt(numberOfZenith);
		stream->writeIntArray(numberOfAzimuth.data(), numberOfZenith);
		stream->writeDoubleArray(accumulated_ZenithAngle.data(), numberOfZenith);

		for (int i = 0; i < numberOfZenith; i++) {
			vector<double> tmp;
			stream->writeDoubleArray(tmp.data(), numberOfAzimuth[i]);
			getazimuthAngleData().push_back(tmp);
		}
		for (int i = 0; i < numberOfZenith; i++) {
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				m_fluors_All[i][j].serialize(stream);
				m_fluors_PSI[i][j].serialize(stream);
				m_fluors_PSII[i][j].serialize(stream);
			}
		}
		m_verticalIrradiance.serialize(stream);
		stream->writeInt(m_nVirtualDirections);
		stream->writeDoubleArray(m_virtualDirZenith.data(), m_nVirtualDirections);
		stream->writeDoubleArray(m_virtualDirAzimuth.data(), m_nVirtualDirections);
		stream->writeDoubleArray(m_virtualDirXYZ.data(), m_nVirtualDirections * 3);
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualFluors_All[i].serialize(stream);
			m_virtualFluors_PSI[i].serialize(stream);
			m_virtualFluors_PSII[i].serialize(stream);
		}

		stream->writeInt(m_numAngularDirection);
		for (int i = 0; i < m_numAngularDirection; i++) {
			stream->writeDouble(m_anglarDirections[i].center_zenith);
			stream->writeDouble(m_anglarDirections[i].center_azimuth);
			stream->writeDouble(m_anglarDirections[i].angleInterval);
			m_virtualDetectorFluors_All[i].serialize(stream);
			m_virtualDetectorFluors_PSI[i].serialize(stream);
			m_virtualDetectorFluors_PSII[i].serialize(stream);
		}
		stream->writeBool(m_isTheramlMode);
		m_wavelengths.serialize(stream);
	}

	void clear() {
		m_verticalIrradiance = Spectrum(0.0);
		m_fluors_All.clear();
		m_fluors_PSI.clear();
		m_fluors_PSII.clear();
		for (int i = 0; i < numberOfZenith; i++) {
			vector<Spectrum> aziTmp;
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				aziTmp.push_back(Spectrum(0.0));
			}
			m_fluors_All.push_back(aziTmp);
			m_fluors_PSI.push_back(aziTmp);
			m_fluors_PSII.push_back(aziTmp);
		}

		m_virtualDetectorFluors_All.clear();
		m_virtualDetectorFluors_PSI.clear();
		m_virtualDetectorFluors_PSII.clear();
		for (int i = 0; i < m_numAngularDirection; i++) {
			m_virtualDetectorFluors_All.push_back(Spectrum(0.0));
			m_virtualDetectorFluors_PSI.push_back(Spectrum(0.0));
			m_virtualDetectorFluors_PSII.push_back(Spectrum(0.0));
		}

		m_virtualFluors_All.clear();
		m_virtualFluors_PSI.clear();
		m_virtualFluors_PSII.clear();
		m_accFluorsPerDirection.clear();
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualFluors_All.push_back(Spectrum(0.0));
			m_virtualFluors_PSI.push_back(Spectrum(0.0));
			m_virtualFluors_PSII.push_back(Spectrum(0.0));
			m_accFluorsPerDirection.push_back(0);
		}

		m_virtualColSlgFluors_All.clear();
		m_virtualMltFluors_All.clear();
		m_virtualUcSlgFluors_All.clear();
		m_virtualColSlgFluors_PSI.clear();
		m_virtualMltFluors_PSI.clear();
		m_virtualUcSlgFluors_PSI.clear();
		m_virtualColSlgFluors_PSII.clear();
		m_virtualMltFluors_PSII.clear();
		m_virtualUcSlgFluors_PSII.clear();
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualColSlgFluors_All.push_back(Spectrum(0.0));
			m_virtualMltFluors_All.push_back(Spectrum(0.0));
			m_virtualUcSlgFluors_All.push_back(Spectrum(0.0));
			m_virtualColSlgFluors_PSI.push_back(Spectrum(0.0));
			m_virtualMltFluors_PSI.push_back(Spectrum(0.0));
			m_virtualUcSlgFluors_PSI.push_back(Spectrum(0.0));
			m_virtualColSlgFluors_PSII.push_back(Spectrum(0.0));
			m_virtualMltFluors_PSII.push_back(Spectrum(0.0));
			m_virtualUcSlgFluors_PSII.push_back(Spectrum(0.0));
		}
	}


	//Collect total irradiance at the top of the virtual plane for Fluor calculation.
	void putIrradiance(Spectrum value) {
		m_verticalIrradiance += value;
	}

	void scaleIrradiance(double scale = 1) {
		m_verticalIrradiance *= scale;
	}

	void scaleVirtualFluors(double scale = 1) {
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualFluors_All[i] *= scale;
			m_virtualFluors_PSI[i] *= scale;
			m_virtualFluors_PSII[i] *= scale;
		}
	}

	void putVirtualFluor(int depth, const Intersection& its, int directionIndex, Spectrum value_All, Spectrum value_PSI, Spectrum value_PSII,
		bool isMediumInteraction) {
		m_accFluorsPerDirection[directionIndex]++;
		if (value_All[FLUOR_0_INDEX] != 0)
			m_virtualFluors_All[directionIndex] += value_All;
		if (value_PSI[FLUOR_0_INDEX] != 0 || value_PSII[FLUOR_0_INDEX] != 0) {
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
				m_virtualFluors_PSI[directionIndex], m_virtualFluors_PSII[directionIndex], value_PSI, value_PSII);
		}
		//rami 5
		// co_sgl only the photons interacting once with the leaves or woody elements (and not with the soil) are considered in the computation of Fluors.
		if (!isMediumInteraction) {
			string compName = its.shape->getID();
			if (depth == 1 && !(compName == "terrain")) {
				if (value_All[FLUOR_0_INDEX] != 0)
					m_virtualColSlgFluors_All[directionIndex] += value_All;
				if (value_PSI[FLUOR_0_INDEX] != 0 || value_PSII[FLUOR_0_INDEX] != 0) {
					m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
						m_virtualColSlgFluors_PSI[directionIndex], m_virtualColSlgFluors_PSII[directionIndex], value_PSI, value_PSII);
				}
			}
			else if (depth >= 2) {
				if (value_All[FLUOR_0_INDEX] != 0)
					m_virtualMltFluors_All[directionIndex] += value_All;
				if (value_PSI[FLUOR_0_INDEX] != 0 || value_PSII[FLUOR_0_INDEX] != 0) {
					m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
						m_virtualMltFluors_PSI[directionIndex], m_virtualMltFluors_PSII[directionIndex], value_PSI, value_PSII);
				}
			}
			else if (depth == 1 && compName == "terrain") {
				if (value_All[FLUOR_0_INDEX] != 0)
					m_virtualUcSlgFluors_All[directionIndex] += value_All;
				if (value_PSI[FLUOR_0_INDEX] != 0 || value_PSII[FLUOR_0_INDEX] != 0) {
					m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
						m_virtualUcSlgFluors_PSI[directionIndex], m_virtualUcSlgFluors_PSII[directionIndex], value_PSI, value_PSII);
				}
			}
		}
		else {
			if (depth == 1) {
				if (value_All[FLUOR_0_INDEX] != 0)
					m_virtualColSlgFluors_All[directionIndex] += value_All;
				if (value_PSI[FLUOR_0_INDEX] != 0 || value_PSII[FLUOR_0_INDEX] != 0) {
					m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
						m_virtualColSlgFluors_PSI[directionIndex], m_virtualColSlgFluors_PSII[directionIndex], value_PSI, value_PSII);
				}
			}
			else if (depth >= 2) {
				if (value_All[FLUOR_0_INDEX] != 0)
					m_virtualMltFluors_All[directionIndex] += value_All;
				if (value_PSI[FLUOR_0_INDEX] != 0 || value_PSII[FLUOR_0_INDEX] != 0) {
					m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
						m_virtualMltFluors_PSI[directionIndex], m_virtualMltFluors_PSII[directionIndex], value_PSI, value_PSII);
				}
			}
		}

	}

	void setWavelengths(Spectrum spectrum) {
		this->m_wavelengths = spectrum;
	}

	//Collect photons for each solid angle
	void put(double zenith, double azimuth, Spectrum value_All, Spectrum value_PSI, Spectrum value_PSII) {
		//determine the zenith solid angle patch
		int i = 0;
		for (i = 0; i < accumulated_ZenithAngle.size(); i++) {
			if (zenith <= accumulated_ZenithAngle[i]) {
				break;
			}
		}
		int zenithIndex = i;
		//determine azimuth index
		double aziInterval = PHRT_M_PI * 2 / accumulated_azimuthAngle[zenithIndex].size();
		int aziIndex = int(azimuth / aziInterval);
		if (zenithIndex >= 0 && zenithIndex < m_fluors_All.size() &&
			aziIndex >= 0 && aziIndex < m_fluors_All[zenithIndex].size()) {
			m_fluors_All[zenithIndex][aziIndex] += value_All;
			if (value_PSI[FLUOR_0_INDEX] != 0 || value_PSII[FLUOR_0_INDEX] != 0) {
				m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
					m_fluors_PSI[zenithIndex][aziIndex], m_fluors_PSII[zenithIndex][aziIndex], value_PSI, value_PSII);
			}
		}

		//determine virtual detectors
		for (int i = 0; i < m_numAngularDirection; i++) {
			AngularDirection angularDir = m_anglarDirections[i];
			bool angularDir_isInside = angularDir.isInside(zenith, azimuth);
			if (angularDir_isInside) {
				m_virtualDetectorFluors_All[i] += value_All;
				if (value_PSI[FLUOR_0_INDEX] != 0 || value_PSII[FLUOR_0_INDEX] != 0) {
					m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
						m_virtualDetectorFluors_PSI[i], m_virtualDetectorFluors_PSII[i], value_PSI, value_PSII);
				}
			}
		}

	}

	vector<vector<Spectrum>> getFluorAllData() const {
		return m_fluors_All;
	}

	vector<vector<Spectrum>> getFluorPSIData() const {
		return m_fluors_PSI;
	}

	vector<vector<Spectrum>> getFluorPSIIData() const {
		return m_fluors_PSII;
	}

	vector<vector<double>> getazimuthAngleData() const {
		return accumulated_azimuthAngle;
	}

	//merge another directionalFluorAll in current one
	void merge(const DirectionalFluor* dirFluor) {
		m_verticalIrradiance += dirFluor->m_verticalIrradiance;
		if (IS_FLUSPECT_PRO == 0) {
			for (int i = 0; i < numberOfZenith; i++)
				for (int j = 0; j < numberOfAzimuth[i]; j++) {
					m_fluors_All[i][j] += dirFluor->getFluorAllData()[i][j];
					m_FluorSpectrum_fun.compute_isFluspectPro_FluorSpectrum_PlusEqual(
						m_fluors_PSI[i][j], m_fluors_PSII[i][j], 
						dirFluor->getFluorPSIData()[i][j], dirFluor->getFluorPSIIData()[i][j]);
				}

			for (int i = 0; i < m_numAngularDirection; i++) {
				m_virtualDetectorFluors_All[i] += dirFluor->m_virtualDetectorFluors_All[i];
				m_FluorSpectrum_fun.compute_isFluspectPro_FluorSpectrum_PlusEqual(
					m_virtualDetectorFluors_PSI[i], m_virtualDetectorFluors_PSII[i], 
					dirFluor->m_virtualDetectorFluors_PSI[i], dirFluor->m_virtualDetectorFluors_PSII[i]);
			}

			for (int i = 0; i < dirFluor->m_nVirtualDirections; i++) {
				m_accFluorsPerDirection[i] += dirFluor->m_accFluorsPerDirection[i];
				m_virtualFluors_All[i] += dirFluor->m_virtualFluors_All[i];
				m_FluorSpectrum_fun.compute_isFluspectPro_FluorSpectrum_PlusEqual(
					m_virtualFluors_PSI[i], m_virtualFluors_PSII[i],
					dirFluor->m_virtualFluors_PSI[i], dirFluor->m_virtualFluors_PSII[i]);

				//rami 5
				m_virtualColSlgFluors_All[i] += dirFluor->m_virtualColSlgFluors_All[i];
				m_virtualMltFluors_All[i] += dirFluor->m_virtualMltFluors_All[i];
				m_virtualUcSlgFluors_All[i] += dirFluor->m_virtualUcSlgFluors_All[i];

				for (int k = 0; k < FLUOR_SAMPLES; k++) {
					m_virtualColSlgFluors_PSI[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualColSlgFluors_PSI[i][FLUOR_MIN_INDEX + k];
					m_virtualMltFluors_PSI[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualMltFluors_PSI[i][FLUOR_MIN_INDEX + k];
					m_virtualUcSlgFluors_PSI[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualUcSlgFluors_PSI[i][FLUOR_MIN_INDEX + k];

					m_virtualColSlgFluors_PSII[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualColSlgFluors_PSII[i][FLUOR_MIN_INDEX + k];
					m_virtualMltFluors_PSII[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualMltFluors_PSII[i][FLUOR_MIN_INDEX + k];
					m_virtualUcSlgFluors_PSII[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualUcSlgFluors_PSII[i][FLUOR_MIN_INDEX + k];
				}
			}
		}
		else {
			for (int i = 0; i < numberOfZenith; i++)
				for (int j = 0; j < numberOfAzimuth[i]; j++) {
					m_fluors_All[i][j] += dirFluor->getFluorAllData()[i][j];
					m_FluorSpectrum_fun.compute_isNotFluspectPro_FluorSpectrum_PlusEqual(
						m_fluors_PSI[i][j], 
						dirFluor->getFluorPSIData()[i][j]);
				}

			for (int i = 0; i < m_numAngularDirection; i++) {
				m_virtualDetectorFluors_All[i] += dirFluor->m_virtualDetectorFluors_All[i];
				m_FluorSpectrum_fun.compute_isNotFluspectPro_FluorSpectrum_PlusEqual(
					m_virtualDetectorFluors_PSI[i],
					dirFluor->m_virtualDetectorFluors_PSI[i]);
			}

			for (int i = 0; i < dirFluor->m_nVirtualDirections; i++) {
				m_accFluorsPerDirection[i] += dirFluor->m_accFluorsPerDirection[i];
				m_virtualFluors_All[i] += dirFluor->m_virtualFluors_All[i];
				m_FluorSpectrum_fun.compute_isNotFluspectPro_FluorSpectrum_PlusEqual(
					m_virtualFluors_PSI[i],
					dirFluor->m_virtualFluors_PSI[i]);

				//rami 5
				m_virtualColSlgFluors_All[i] += dirFluor->m_virtualColSlgFluors_All[i];
				m_virtualMltFluors_All[i] += dirFluor->m_virtualMltFluors_All[i];
				m_virtualUcSlgFluors_All[i] += dirFluor->m_virtualUcSlgFluors_All[i];

				for (int k = 0; k < FLUOR_SAMPLES; k++) {
					m_virtualColSlgFluors_PSI[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualColSlgFluors_PSI[i][FLUOR_MIN_INDEX + k];
					m_virtualMltFluors_PSI[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualMltFluors_PSI[i][FLUOR_MIN_INDEX + k];
					m_virtualUcSlgFluors_PSI[i][FLUOR_MIN_INDEX + k] += dirFluor->m_virtualUcSlgFluors_PSI[i][FLUOR_MIN_INDEX + k];
				}
			}
		}

	}

	inline double rad2degree(double rad) {
		return rad / PHRT_M_PI * 180;
	}

	inline double degree2rad(double degree) {
		return degree / ((double)180) * PHRT_M_PI;
	}

	inline double InvertPlanck(double radiance, double wavelength) {
		if (radiance <= 0)
			return 0;
		double kb = 1.38064852e-23;  // Boltzmann constant
		double hp = 6.626070040e-34;  // Planck constant
		double c = 299792458;
		double wavelengthMeter = wavelength * std::pow(10, -9);
		double scaledRadiance = radiance * std::pow(10, 9);

		double inside = 1 + 2 * hp * c * c / (std::pow(wavelengthMeter, 5) * scaledRadiance);
		double down = wavelengthMeter * kb * std::log(inside);
		double up = hp * c;
		return up / down;
	}

	double broadbandIntegral(Spectrum energy) {
		if (SPECTRUM_SAMPLES == 1)
			return energy[0];

		double total = 0.0;
		for (int j = 0; j < SPECTRUM_SAMPLES - 1; j++) {
			total += (energy[j] + energy[j + 1]) * (m_wavelengths[j + 1] - m_wavelengths[j]) * 0.5;
		}
		return total;
	}

	void develop(size_t hasFluorProducts, double scale = 1.0) {
		scaleIrradiance(scale * 1 / (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y));
		//cout << "\nINFO: Total Irradiance: " << m_verticalIrradiance.toString() << endl;
		if (m_destnationFile != "") {
			vector<double> zenithAngle = accumulated_ZenithAngle;
			vector<vector<double>> azimuthAngle = accumulated_azimuthAngle;
			if (numberOfAzimuth[0] == 1) {
				zenithAngle.insert(zenithAngle.begin(), -accumulated_ZenithAngle[0]);
			}
			else {
				zenithAngle.insert(zenithAngle.begin(), 0);
			}
			double solidAnglePerPatch = 2 * PHRT_M_PI / (double)m_numOfDirections;

			for (int i = 0; i < accumulated_ZenithAngle.size(); i++) {
				azimuthAngle[i].insert(azimuthAngle[i].begin(), 0);
			}
			ofstream out(m_destnationFile);
			if (m_isTheramlMode)
				out << "Zentih_Angle Azimuth_Angle BrightnessTemperature_with_Fluor" << endl;
			else
				out << "Zentih_Angle Azimuth_Angle BRF_with_Fluor (Number of Directions=" << m_numOfDirections << ")" << endl;
			Spectrum Albedo(0.0), HemisphereFluor_PSI(0.0), HemisphereFluor_PSII(0.0);
			for (int i = 1; i < zenithAngle.size(); i++) {
				for (int j = 1; j < azimuthAngle[i - 1].size(); j++) {
					double centerZenith = 0.5 * (zenithAngle[i] + zenithAngle[i - 1]);
					out << rad2degree(centerZenith) << " " << rad2degree(0.5 * (azimuthAngle[i - 1][j] + azimuthAngle[i - 1][j - 1])) << " ";
					if (!m_isTheramlMode) {
						Albedo += m_fluors_All[i - 1][j - 1] * scale;
						m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual_M1(HemisphereFluor_PSI, HemisphereFluor_PSII, scale, m_fluors_PSI[i - 1][j - 1], m_fluors_PSII[i - 1][j - 1]);
						for (int k = 0; k < WANTED_INDEX.size(); k++) {
							out << m_fluors_All[i - 1][j - 1][WANTED_INDEX[k]] * scale / solidAnglePerPatch / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(centerZenith)) / m_verticalIrradiance[WANTED_INDEX[k]] * PHRT_M_PI << " ";
						}
					}
					else {
						for (int k = 0; k < WANTED_INDEX.size(); k++) {
							out << InvertPlanck(m_fluors_All[i - 1][j - 1][WANTED_INDEX[k]] * scale / solidAnglePerPatch / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(centerZenith)), m_wavelengths[WANTED_INDEX[k]]) << " ";
						}
					}
					out << endl;
				}
			}
			//virtual Detectors
			for (int i = 0; i < m_numAngularDirection; i++) {
				AngularDirection angularDir = m_anglarDirections[i];
				out << rad2degree(angularDir.center_zenith) << " " << rad2degree(angularDir.center_azimuth) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode)
						out << m_virtualDetectorFluors_All[i][WANTED_INDEX[k]] * scale / angularDir.solidAngle() / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(angularDir.center_zenith)) / m_verticalIrradiance[WANTED_INDEX[k]] * PHRT_M_PI << " ";
					else
						out << InvertPlanck(m_virtualDetectorFluors_All[i][WANTED_INDEX[k]] * scale / angularDir.solidAngle() / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(angularDir.center_zenith)), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				out << endl;
			}
			//virtual directions
			for (int i = 0; i < m_nVirtualDirections; i++) {
				out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode) {
						out << m_virtualFluors_All[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) / m_verticalIrradiance[WANTED_INDEX[k]] * PHRT_M_PI << " ";
					}
					else
						out << InvertPlanck(m_virtualFluors_All[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				out << endl;
			}

			if (m_isTheramlMode && hasFluorProducts == 1)
				out << "\nZentih_Angle Azimuth_Angle BrightnessTemperature_From_PSI_Fluor" << endl;
			else if(m_isTheramlMode && hasFluorProducts == 2)
				out << "\nZentih_Angle Azimuth_Angle BrightnessTemperature_From_Fluor" << endl;
			else if (hasFluorProducts == 1)
				out << "\nZentih_Angle Azimuth_Angle PSI_Fluor (Number of Directions=" << m_numOfDirections << ", unit: mW*m-2*nm-1*sr-1)" << endl;
			else if (hasFluorProducts == 2)
				out << "\nZentih_Angle Azimuth_Angle Fluor (Number of Directions=" << m_numOfDirections << ", unit: mW*m-2*nm-1*sr-1)" << endl;
			for (int i = 1; i < zenithAngle.size(); i++) {
				for (int j = 1; j < azimuthAngle[i - 1].size(); j++) {
					double centerZenith = 0.5 * (zenithAngle[i] + zenithAngle[i - 1]);
					out << rad2degree(centerZenith) << " " << rad2degree(0.5 * (azimuthAngle[i - 1][j] + azimuthAngle[i - 1][j - 1])) << " ";
					if (!m_isTheramlMode) {
						for (int k = 0; k < WANTED_INDEX.size(); k++) {
							out << m_fluors_PSI[i - 1][j - 1][WANTED_INDEX[k]] * scale / solidAnglePerPatch / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(centerZenith)) * 1000 << " ";// * PHRT_M_PI
						}
					}
					else {
						for (int k = 0; k < WANTED_INDEX.size(); k++) {
							out << InvertPlanck(m_fluors_PSI[i - 1][j - 1][WANTED_INDEX[k]] * scale / solidAnglePerPatch / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(centerZenith)), m_wavelengths[WANTED_INDEX[k]]) << " ";
						}
					}
					out << endl;
				}
			}
			//virtual Detectors
			for (int i = 0; i < m_numAngularDirection; i++) {
				AngularDirection angularDir = m_anglarDirections[i];
				out << rad2degree(angularDir.center_zenith) << " " << rad2degree(angularDir.center_azimuth) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode)
						out << m_virtualDetectorFluors_PSI[i][WANTED_INDEX[k]] * scale / angularDir.solidAngle() / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(angularDir.center_zenith)) * 1000 << " ";// * PHRT_M_PI
					else
						out << InvertPlanck(m_virtualDetectorFluors_PSI[i][WANTED_INDEX[k]] * scale / angularDir.solidAngle() / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(angularDir.center_zenith)), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				out << endl;
			}
			//virtual directions
			for (int i = 0; i < m_nVirtualDirections; i++) {
				out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode) {
						out << m_virtualFluors_PSI[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) * 1000 << " ";
					}
					else
						out << InvertPlanck(m_virtualFluors_PSI[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";// * PHRT_M_PI
				}
				out << endl;
			}
			if (hasFluorProducts == 1) {
				if (m_isTheramlMode)
					out << "\nZentih_Angle Azimuth_Angle BrightnessTemperature_From_PSII_Fluor" << endl;
				else
					out << "\nZentih_Angle Azimuth_Angle PSII_Fluor (Number of Directions=" << m_numOfDirections << ", unit: mW*m-2*nm-1*sr-1)" << endl;
				for (int i = 1; i < zenithAngle.size(); i++) {
					for (int j = 1; j < azimuthAngle[i - 1].size(); j++) {
						double centerZenith = 0.5 * (zenithAngle[i] + zenithAngle[i - 1]);
						out << rad2degree(centerZenith) << " " << rad2degree(0.5 * (azimuthAngle[i - 1][j] + azimuthAngle[i - 1][j - 1])) << " ";
						if (!m_isTheramlMode) {
							for (int k = 0; k < WANTED_INDEX.size(); k++) {
								out << m_fluors_PSII[i - 1][j - 1][WANTED_INDEX[k]] * scale / solidAnglePerPatch / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(centerZenith)) * 1000 << " ";// * PHRT_M_PI
							}
						}
						else {
							for (int k = 0; k < WANTED_INDEX.size(); k++) {
								out << InvertPlanck(m_fluors_PSII[i - 1][j - 1][WANTED_INDEX[k]] * scale / solidAnglePerPatch / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(centerZenith)), m_wavelengths[WANTED_INDEX[k]]) << " ";
							}
						}
						out << endl;
					}
				}
				//virtual Detectors
				for (int i = 0; i < m_numAngularDirection; i++) {
					AngularDirection angularDir = m_anglarDirections[i];
					out << rad2degree(angularDir.center_zenith) << " " << rad2degree(angularDir.center_azimuth) << " ";
					for (int k = 0; k < WANTED_INDEX.size(); k++) {
						if (!m_isTheramlMode)
							out << m_virtualDetectorFluors_PSII[i][WANTED_INDEX[k]] * scale / angularDir.solidAngle() / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(angularDir.center_zenith)) * 1000 << " ";// * PHRT_M_PI
						else
							out << InvertPlanck(m_virtualDetectorFluors_PSII[i][WANTED_INDEX[k]] * scale / angularDir.solidAngle() / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(angularDir.center_zenith)), m_wavelengths[WANTED_INDEX[k]]) << " ";
					}
					out << endl;
				}
				//virtual directions
				for (int i = 0; i < m_nVirtualDirections; i++) {
					out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
					for (int k = 0; k < WANTED_INDEX.size(); k++) {
						if (!m_isTheramlMode) {
							out << m_virtualFluors_PSII[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) * 1000 << " ";// *PHRT_M_PI
						}
						else
							out << InvertPlanck(m_virtualFluors_PSII[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
					}
					out << endl;
				}
			}
			out.close();

			if (!m_isTheramlMode) {
				if (m_infoDestnationFile != "") {
					ofstream infoOut(m_infoDestnationFile);

					//broadband albedo
					double broadbandAlbedo = broadbandIntegral(Albedo) / broadbandIntegral(m_verticalIrradiance * (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y));
					infoOut << "Broadband Albedo: " << std::fixed << std::setprecision(5) << broadbandAlbedo << endl;

					//spectral albedo
					Albedo = Albedo / (m_verticalIrradiance * (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y));

					infoOut << "Spectral Albedo: ";
					for (int i = 0; i < WANTED_INDEX.size(); i++)
						infoOut << Albedo[WANTED_INDEX[i]] << " ";
					infoOut << endl;
					infoOut << endl;

					//broadband Fluor
					double broadbandHemisphereFluor_PSI = broadbandIntegral(HemisphereFluor_PSI);// / (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y)

					if (IS_FLUSPECT_PRO) {
						infoOut << "Broadband Hemisphere Fluor (mW): " << std::fixed << std::setprecision(5) << broadbandHemisphereFluor_PSI * 1000 << endl;
						//spectral Fluor
						//HemisphereFluor_PSI /= (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y);
						infoOut << "Spectral Hemisphere Fluor (mW*nm-1): ";
					}
					else {
						infoOut << "Broadband Hemisphere Fluor PSI (mW): " << std::fixed << std::setprecision(5) << broadbandHemisphereFluor_PSI * 1000 << endl;
						//spectral Fluor
						//HemisphereFluor_PSI /= (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y);
						infoOut << "Spectral Hemisphere Fluor PSI (mW*nm-1): ";
					}
					for (int i = 0; i < WANTED_INDEX.size(); i++)
						infoOut << HemisphereFluor_PSI[WANTED_INDEX[i]] * 1000 << " ";
					infoOut << endl;
					infoOut << endl;

					if (!IS_FLUSPECT_PRO) {
						//broadband Fluor
						double broadbandHemisphereFluor_PSII = broadbandIntegral(HemisphereFluor_PSII);// / (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y)
						infoOut << "Broadband Hemisphere Fluor PSII (mW): " << std::fixed << std::setprecision(5) << broadbandHemisphereFluor_PSII * 1000 << endl;
						//spectral Fluor
						//HemisphereFluor_PSII /= (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y);
						infoOut << "Spectral Hemisphere Fluor PSII (mW*nm-1): ";
						for (int i = 0; i < WANTED_INDEX.size(); i++)
							infoOut << HemisphereFluor_PSII[WANTED_INDEX[i]] * 1000 << " ";
						infoOut << endl;
					}
				}
			}

			//RAMI 5
			ofstream cosgl_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_co_sgl.txt");
			cosgl_out << "BRF_with_Fluor_co_sgl" << endl;
			for (int i = 0; i < m_nVirtualDirections; i++) {
				cosgl_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode)
						cosgl_out << m_virtualColSlgFluors_All[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) / m_verticalIrradiance[WANTED_INDEX[k]] * PHRT_M_PI << " ";
					else
						cosgl_out << InvertPlanck(m_virtualColSlgFluors_All[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				cosgl_out << endl;
			}
			if (hasFluorProducts == 1)
				cosgl_out << "\nPSI_Fluor_co_sgl (unit: mW*m-2*nm-1*sr-1)" << endl;
			else if(hasFluorProducts == 2)
				cosgl_out << "\nFluor_co_sgl (unit: mW*m-2*nm-1*sr-1)" << endl;
			for (int i = 0; i < m_nVirtualDirections; i++) {
				cosgl_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode)
						cosgl_out << m_virtualColSlgFluors_PSI[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) * 1000 << " ";// * PHRT_M_PI
					else
						cosgl_out << InvertPlanck(m_virtualColSlgFluors_PSI[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				cosgl_out << endl;
			}
			if (hasFluorProducts == 1) {
				cosgl_out << "\nPSII_Fluor_co_sgl (unit: mW*m-2*nm-1*sr-1)" << endl;
				for (int i = 0; i < m_nVirtualDirections; i++) {
					cosgl_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
					for (int k = 0; k < WANTED_INDEX.size(); k++) {
						if (!m_isTheramlMode)
							cosgl_out << m_virtualColSlgFluors_PSII[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) * 1000 << " ";// * PHRT_M_PI
						else
							cosgl_out << InvertPlanck(m_virtualColSlgFluors_PSII[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
					}
					cosgl_out << endl;
				}
			}
			cosgl_out.close();

			ofstream mlt_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_mlt.txt");
			mlt_out << "BRF_with_Fluor_mlt" << endl;
			for (int i = 0; i < m_nVirtualDirections; i++) {
				mlt_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode)
						mlt_out << m_virtualMltFluors_All[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) / m_verticalIrradiance[WANTED_INDEX[k]] * PHRT_M_PI << " ";
					else
						mlt_out << InvertPlanck(m_virtualMltFluors_All[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				mlt_out << endl;
			}
			if (hasFluorProducts == 1)
				mlt_out << "\nPSI_Fluor_mlt (unit: mW*m-2*nm-1*sr-1)" << endl;
			else if (hasFluorProducts == 2)
				mlt_out << "\nFluor_mlt (unit: mW*m-2*nm-1*sr-1)" << endl;
			for (int i = 0; i < m_nVirtualDirections; i++) {
				mlt_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode)
						mlt_out << m_virtualMltFluors_PSI[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) * 1000 << " ";// * PHRT_M_PI
					else
						mlt_out << InvertPlanck(m_virtualMltFluors_PSI[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				mlt_out << endl;
			}
			if (hasFluorProducts == 1) {
				mlt_out << "\nPSII_Fluor_mlt (unit: mW*m-2*nm-1*sr-1)" << endl;
				for (int i = 0; i < m_nVirtualDirections; i++) {
					mlt_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
					for (int k = 0; k < WANTED_INDEX.size(); k++) {
						if (!m_isTheramlMode)
							mlt_out << m_virtualMltFluors_PSII[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) * 1000 << " ";// * PHRT_M_PI
						else
							mlt_out << InvertPlanck(m_virtualMltFluors_PSII[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
					}
					mlt_out << endl;
				}
			}
			mlt_out.close();

			ofstream ucsgl_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_uc_sgl.txt");
			ucsgl_out << "BRF_with_Fluor_uc_sgl" << endl;
			for (int i = 0; i < m_nVirtualDirections; i++) {
				ucsgl_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode)
						ucsgl_out << m_virtualUcSlgFluors_All[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) / m_verticalIrradiance[WANTED_INDEX[k]] * PHRT_M_PI << " ";
					else
						ucsgl_out << InvertPlanck(m_virtualUcSlgFluors_All[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				ucsgl_out << endl;
			}
			if (hasFluorProducts == 1)
				ucsgl_out << "\nPSI_Fluor_uc_sgl (unit: mW*m-2*nm-1*sr-1)" << endl;
			else if (hasFluorProducts == 2)
				ucsgl_out << "\nFluor_uc_sgl (unit: mW*m-2*nm-1*sr-1)" << endl;
			for (int i = 0; i < m_nVirtualDirections; i++) {
				ucsgl_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < WANTED_INDEX.size(); k++) {
					if (!m_isTheramlMode)
						ucsgl_out << m_virtualUcSlgFluors_PSI[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) * 1000 << " ";// * PHRT_M_PI
					else
						ucsgl_out << InvertPlanck(m_virtualUcSlgFluors_PSI[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
				}
				ucsgl_out << endl;
			}
			if (hasFluorProducts == 1) {
				ucsgl_out << "\nPSII_Fluor_uc_sgl (unit: mW*m-2*nm-1*sr-1)" << endl;
				for (int i = 0; i < m_nVirtualDirections; i++) {
					ucsgl_out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
					for (int k = 0; k < WANTED_INDEX.size(); k++) {
						if (!m_isTheramlMode)
							ucsgl_out << m_virtualUcSlgFluors_PSII[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])) * 1000 << " ";// * PHRT_M_PI
						else
							ucsgl_out << InvertPlanck(m_virtualUcSlgFluors_PSII[i][WANTED_INDEX[k]] * scale / (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y * std::cos(m_virtualDirZenith[i])), m_wavelengths[WANTED_INDEX[k]]) << " ";
					}
					ucsgl_out << endl;
				}
			}
			ucsgl_out.close();
		}
	}


	void setDestinationFile(string destinationFile) {
		m_destnationFile = destinationFile;
	}

	void setInfoDestinationFile(string infoDestinationFile) {
		m_infoDestnationFile = infoDestinationFile;
	}

	void setSceneBoundPlaneSize(Vector2 size) {
		this->m_scenBoundPlaneSize = size;
	}

	void setVirtualBoundXZSize(Vector2 size) {
		this->m_virtualBoundXZSize = size;
	}

	void setCalculationMode(bool isThermal) {
		this->m_isTheramlMode = isThermal;
	}

	//virtual detector
	void readVirtualDetectors(string virtualDetectors) {
		if (virtualDetectors == "") {
			m_numAngularDirection = 0;
			return;
		}

		m_anglarDirections.clear();

		std::vector<std::string> tmp;
		boost::algorithm::split(tmp, virtualDetectors, boost::is_any_of(";"));
		if (tmp.size() == 3) { // combination
			string zenithStr = tmp[0];
			string AziStr = tmp[1];
			string angleInterStr = tmp[2];
			std::vector<std::string> zen_arr;
			boost::algorithm::split(zen_arr, zenithStr, boost::is_any_of(","));

			std::vector<std::string> azi_arr;
			boost::algorithm::split(azi_arr, AziStr, boost::is_any_of(","));

			double angleInterval = degree2rad(atof(angleInterStr.c_str()));

			for (int i = 0; i < zen_arr.size(); i++) {
				double zen = degree2rad(atof(zen_arr[i].c_str()));
				for (int j = 0; j < azi_arr.size(); j++) {
					double azi = degree2rad(atof(azi_arr[j].c_str()));
					m_anglarDirections.push_back(AngularDirection(zen, azi, angleInterval));
				}
			}
		}
		else {
			std::vector<std::string> arr;
			boost::algorithm::split(arr, virtualDetectors, boost::is_any_of(",;"));
			for (int i = 0; i < arr.size() - 1; i = i + 3) {
				double zen = degree2rad(atof(arr[i].c_str()));
				double azi = degree2rad(atof(arr[i + 1].c_str()));
				double angleInterval = degree2rad(atof(arr[i + 2].c_str()));
				m_anglarDirections.push_back(AngularDirection(zen, azi, angleInterval));
			}
		}

		m_numAngularDirection = m_anglarDirections.size();

		//initialize m_virtualFluors
		for (int i = 0; i < m_numAngularDirection; i++) {
			m_virtualDetectorFluors_All.push_back(Spectrum(0.0));
			m_virtualDetectorFluors_PSI.push_back(Spectrum(0.0));
			m_virtualDetectorFluors_PSII.push_back(Spectrum(0.0));
		}

	}

	//virtual Directions
	void readVirtualDirections(string virtualDirections)
	{
		if (virtualDirections == "") {
			m_nVirtualDirections = 0;
			return;
		}

		m_virtualDirZenith.clear();
		m_virtualDirAzimuth.clear();
		m_virtualDirXYZ.clear();

		if (virtualDirections.find(":") != string::npos) {
			std::vector<std::string> arr;
			boost::algorithm::split(arr, virtualDirections, boost::is_any_of(":;"));
			for (int i = 0; i < arr.size() - 1; i = i + 2) {
				double zen = degree2rad(atof(arr[i].c_str()));
				m_virtualDirZenith.push_back(zen);
				double azi = degree2rad(atof(arr[i + 1].c_str()));
				m_virtualDirAzimuth.push_back(azi);
				double x = -std::sin(zen) * std::cos(0.5 * PHRT_M_PI - azi);
				double y = std::cos(zen);
				double z = std::sin(zen) * std::sin(0.5 * PHRT_M_PI - azi);
				m_virtualDirXYZ.push_back(x);
				m_virtualDirXYZ.push_back(y);
				m_virtualDirXYZ.push_back(z);
			}
			m_nVirtualDirections = m_virtualDirAzimuth.size();
		}


		if (virtualDirections.find(",") != string::npos) { //combine
			std::vector<std::string> arr;
			boost::algorithm::split(arr, virtualDirections, boost::is_any_of(";"));
			if (arr.size() != 2) {
				cout << "Error for inputing the virtual Directions" << endl;
			}
			else {
				string zenithStr = arr[0]; string aziStr = arr[1];
				std::vector<std::string> zenithArr;
				boost::algorithm::split(zenithArr, zenithStr, boost::is_any_of(","));
				std::vector<std::string> AziArr;
				boost::algorithm::split(AziArr, aziStr, boost::is_any_of(","));
				for (int i = 0; i < zenithArr.size(); i++) {
					double zen = degree2rad(atof(zenithArr[i].c_str()));
					for (int j = 0; j < AziArr.size(); j++) {
						double azi = degree2rad(atof(AziArr[j].c_str()));
						m_virtualDirZenith.push_back(zen);
						m_virtualDirAzimuth.push_back(azi);
						double x = -std::sin(zen) * std::cos(0.5 * PHRT_M_PI - azi);
						double y = std::cos(zen);
						double z = std::sin(zen) * std::sin(0.5 * PHRT_M_PI - azi);
						m_virtualDirXYZ.push_back(x);
						m_virtualDirXYZ.push_back(y);
						m_virtualDirXYZ.push_back(z);
						m_nVirtualDirections++;
					}
				}
			}
		}

		//initialize m_virtualFluors
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualFluors_All.push_back(Spectrum(0.0));
			m_virtualFluors_PSI.push_back(Spectrum(0.0));
			m_virtualFluors_PSII.push_back(Spectrum(0.0));
			m_accFluorsPerDirection.push_back(0);
		}

		m_virtualColSlgFluors_All.clear();
		m_virtualMltFluors_All.clear();
		m_virtualUcSlgFluors_All.clear();
		m_virtualColSlgFluors_PSI.clear();
		m_virtualMltFluors_PSI.clear();
		m_virtualUcSlgFluors_PSI.clear();
		m_virtualColSlgFluors_PSII.clear();
		m_virtualMltFluors_PSII.clear();
		m_virtualUcSlgFluors_PSII.clear();
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualColSlgFluors_All.push_back(Spectrum(0.0));
			m_virtualMltFluors_All.push_back(Spectrum(0.0));
			m_virtualUcSlgFluors_All.push_back(Spectrum(0.0));
			m_virtualColSlgFluors_PSI.push_back(Spectrum(0.0));
			m_virtualMltFluors_PSI.push_back(Spectrum(0.0));
			m_virtualUcSlgFluors_PSI.push_back(Spectrum(0.0));
			m_virtualColSlgFluors_PSII.push_back(Spectrum(0.0));
			m_virtualMltFluors_PSII.push_back(Spectrum(0.0));
			m_virtualUcSlgFluors_PSII.push_back(Spectrum(0.0));
		}

	}

	void outputVirtualDirections() {
		cout << "Total Number of virtual Directions: " << m_nVirtualDirections << endl;
		for (int i = 0; i < m_virtualDirZenith.size(); i++) {
			cout << "Zenith: " << m_virtualDirZenith[i] << " Azimuth: " << m_virtualDirAzimuth[i] << endl;
		}
	}


public:
	vector<double> accumulated_ZenithAngle; // the list of zenith angles
	vector<vector<double>> accumulated_azimuthAngle; // the list of azimuth angles for each zenith angle
	vector<vector<Spectrum>> m_fluors_All;//fluor for each zenith and each azimuth
	vector<vector<Spectrum>> m_fluors_PSI;//fluor for each zenith and each azimuth
	vector<vector<Spectrum>> m_fluors_PSII;//fluor for each zenith and each azimuth
	int numberOfZenith = 0; // Total number of zenith angles
	vector<int> numberOfAzimuth; //Number of azimuth angles for each zenith angle
	string m_destnationFile; //output file path
	string m_infoDestnationFile;//out file path to albedo file

	vector<double> m_virtualDirZenith;
	vector<double> m_virtualDirAzimuth;
	vector<double> m_virtualDirXYZ;
	vector<Spectrum> m_virtualFluors_All;
	vector<Spectrum> m_virtualFluors_PSI;
	vector<Spectrum> m_virtualFluors_PSII;
	vector<int> m_accFluorsPerDirection; //Number of accumulated Fluors for each direction.
	int m_nVirtualDirections = 0;

	//For RAMI 5
	vector<Spectrum> m_virtualColSlgFluors_All; //co_sgl only the photons interacting once with the leaves or woody elements (and not with the soil) are considered in the computation of Fluors.
	vector<Spectrum> m_virtualMltFluors_All; // mlt only the photons which interacted twice with any scatterer in the scene are considered in the computation of Fluors.
	vector<Spectrum> m_virtualUcSlgFluors_All; //uc_sgl only the photons which interacted has interacted once only with the underlying background, i.e. the soil (and with nothing else), are considered in the computation of Fluors.

	vector<Spectrum> m_virtualColSlgFluors_PSI; //co_sgl only the photons interacting once with the leaves or woody elements (and not with the soil) are considered in the computation of Fluors.
	vector<Spectrum> m_virtualMltFluors_PSI; // mlt only the photons which interacted twice with any scatterer in the scene are considered in the computation of Fluors.
	vector<Spectrum> m_virtualUcSlgFluors_PSI; //uc_sgl only the photons which interacted has interacted once only with the underlying background, i.e. the soil (and with nothing else), are considered in the computation of Fluors.

	vector<Spectrum> m_virtualColSlgFluors_PSII; //co_sgl only the photons interacting once with the leaves or woody elements (and not with the soil) are considered in the computation of Fluors.
	vector<Spectrum> m_virtualMltFluors_PSII; // mlt only the photons which interacted twice with any scatterer in the scene are considered in the computation of Fluors.
	vector<Spectrum> m_virtualUcSlgFluors_PSII; //uc_sgl only the photons which interacted has interacted once only with the underlying background, i.e. the soil (and with nothing else), are considered in the computation of Fluors.
	//virtual detectors
	int m_numAngularDirection; // number of virtual detectors
	vector<AngularDirection> m_anglarDirections;
	vector<Spectrum> m_virtualDetectorFluors_All;
	vector<Spectrum> m_virtualDetectorFluors_PSI;
	vector<Spectrum> m_virtualDetectorFluors_PSII;
	bool m_isTheramlMode;
	Spectrum m_wavelengths;

	//no need to serilize
	int m_numOfDirections = 0;
	Vector2 m_scenBoundPlaneSize;
	Spectrum m_verticalIrradiance;
	Vector2 m_virtualBoundXZSize;

	//only FluorSpectrum function use
	FluorMatrix m_FluorSpectrum_fun;
};


MTS_NAMESPACE_END
#endif
