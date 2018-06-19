#pragma once

//Implementing a storage class to store directional BRF/radiance
//value for different directions

#if !defined(_DIRECTIONAL_BRF_)
#define _DIRECTIONAL_BRF_

#include <iostream>
#include <vector>
#include <fstream>
#include "photonRTUtils.h"
#include <mitsuba/core/spectrum.h>
#include <mitsuba/mitsuba.h>
#include <boost/algorithm/string.hpp>

using namespace std;

MTS_NAMESPACE_BEGIN

class DirectionalBRF:public Object {
public:
	DirectionalBRF(int NumberOfDirections) {
		m_numOfDirections = NumberOfDirections;
		PhotonRTUtils::generationDiscreteDirections(NumberOfDirections, accumulated_ZenithAngle, accumulated_azimuthAngle);
		numberOfZenith = accumulated_ZenithAngle.size();
		for (int i = 0; i < numberOfZenith; i++) {
			numberOfAzimuth.push_back(accumulated_azimuthAngle[i].size());
			vector<Spectrum> aziTmp;
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				aziTmp.push_back(Spectrum(0.0));
			}
			m_brfs.push_back(aziTmp);
		}
	}

	void unserialize(Stream *stream) {
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
			getBRFData().push_back(aziTmp);
		}
		m_verticalIrradiance = Spectrum(stream);
		m_nVirtualDirections = stream->readInt();
		m_virtualDirZenith.resize(m_nVirtualDirections);
		m_virtualDirAzimuth.resize(m_nVirtualDirections);
		stream->readDoubleArray(m_virtualDirZenith.data(), m_nVirtualDirections);
		stream->readDoubleArray(m_virtualDirAzimuth.data(), m_nVirtualDirections);
		m_virtualDirXYZ.resize(m_nVirtualDirections * 3);
		stream->readDoubleArray(m_virtualDirXYZ.data(), m_nVirtualDirections * 3);

		m_virtualBRFs.resize(m_nVirtualDirections);
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualBRFs[i] = Spectrum(stream);
		}
	}

	void serialize(Stream *stream) const {
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
				m_brfs[i][j].serialize(stream);
			}
		}
		m_verticalIrradiance.serialize(stream);
		stream->writeInt(m_nVirtualDirections);
		stream->writeDoubleArray(m_virtualDirZenith.data(), m_nVirtualDirections);
		stream->writeDoubleArray(m_virtualDirAzimuth.data(), m_nVirtualDirections);
		stream->writeDoubleArray(m_virtualDirXYZ.data(), m_nVirtualDirections * 3);
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualBRFs[i].serialize(stream);
		}
	}

	void clear() {
		m_verticalIrradiance = Spectrum(0.0);
		m_brfs.clear();
		for (int i = 0; i < numberOfZenith; i++) {
			vector<Spectrum> aziTmp;
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				aziTmp.push_back(Spectrum(0.0));
			}
			m_brfs.push_back(aziTmp);
		}

		m_virtualBRFs.clear();
		m_accBRFsPerDirection.clear();
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualBRFs.push_back(Spectrum(0.0));
			m_accBRFsPerDirection.push_back(0);
		}
	}


	//Collect total irradiance at the top of the virtual plane for BRF calculation.
	void putIrradiance(Spectrum value) {
		m_verticalIrradiance += value;
	}

	void scaleIrradiance(double scale = 1) {
		m_verticalIrradiance *= scale;
	}

	void scaleVirtualBRFs(double scale = 1) {
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualBRFs[i] *= scale;
		}
	}

	void putVirtualBRF(int directionIndex, Spectrum value) {
		m_accBRFsPerDirection[directionIndex]++;
		m_virtualBRFs[directionIndex] += value;
	}

	//Collect photons for each solid angle
	void put(double zenith, double azimuth, Spectrum value) {
		int zenithIndex;
		//determine the zenith solid angle patch
		int i = 0;
		for (i = 0; i < accumulated_ZenithAngle.size(); i++) {
			if (zenith <= accumulated_ZenithAngle[i]) {
				break;
			}
		}
		zenithIndex = i;
		//determine azimuth index
		double aziInterval = PHRT_M_PI * 2 / accumulated_azimuthAngle[zenithIndex].size();
		int aziIndex = int(azimuth / aziInterval);
		if (zenithIndex >= 0 && zenithIndex < m_brfs.size() &&
			aziIndex >= 0 && aziIndex < m_brfs[zenithIndex].size()) {
			m_brfs[zenithIndex][aziIndex] += value;
		}		
	}

	vector<vector<Spectrum>> getBRFData() const{
		return m_brfs;
	}

	vector<vector<double>> getazimuthAngleData() const {
		return accumulated_azimuthAngle;
	}

	//merge another directionalBRF in current one
	void merge(const DirectionalBRF* dirBRF) {
		m_verticalIrradiance += dirBRF->m_verticalIrradiance;
		for (int i = 0; i < numberOfZenith; i++) {
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				m_brfs[i][j] += dirBRF->getBRFData()[i][j];
			}
		}

		for (int i = 0; i < dirBRF->m_nVirtualDirections; i++) {
			m_accBRFsPerDirection[i] += dirBRF->m_accBRFsPerDirection[i];
			m_virtualBRFs[i] += dirBRF->m_virtualBRFs[i];
		}

		


	}

	inline double rad2degree(double rad) {
		return rad / PHRT_M_PI * 180;
	}

	inline double degree2rad(double degree) {
		return degree / ((double)180) * PHRT_M_PI;
	}

	void develop(double scale=1.0) {
		//scale irradiance
		scaleIrradiance(scale*1/ (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y));
		scaleVirtualBRFs(scale);
		cout << "\nTotal Irradiance: " << m_verticalIrradiance.toString() << endl;
		if (m_destnationFile != "") {
			vector<double> zenithAngle(accumulated_ZenithAngle);
			vector<vector<double>> azimuthAngle(accumulated_azimuthAngle);
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
			out << "Zentih_Angle Azimuth_Angle BRF" << endl;
			Spectrum Albedo(0.0);
			for (int i = 1; i < zenithAngle.size(); i++) {
				for (int j = 1; j < azimuthAngle[i-1].size(); j++) {
					double centerZenith = 0.5*(zenithAngle[i] + zenithAngle[i - 1]);
					out << rad2degree(centerZenith) << " " << rad2degree(0.5*(azimuthAngle[i-1][j]+ azimuthAngle[i-1][j-1])) << " ";
					Albedo += m_brfs[i - 1][j - 1] * scale;
					for (int k = 0; k < SPECTRUM_SAMPLES; k++) {
						out << m_brfs[i-1][j-1][k] * scale/ solidAnglePerPatch/ (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y*std::cos(centerZenith))/ m_verticalIrradiance[k]*PHRT_M_PI << " ";
					}
					out << endl;
				}
			}
			Albedo = Albedo /( m_verticalIrradiance*(m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y));
			cout << " - Albedo: ";
			for (int i = 0; i < SPECTRUM_SAMPLES; i++)
				cout << Albedo[i] << " ";
			cout << endl;

			//virtual directions
			for (int i = 0; i < m_nVirtualDirections; i++) {
				out << rad2degree(m_virtualDirZenith[i]) << " " << rad2degree(m_virtualDirAzimuth[i]) << " ";
				for (int k = 0; k < SPECTRUM_SAMPLES; k++) {
					out << m_virtualBRFs[i][k]/ (m_virtualBoundXZSize.x * m_virtualBoundXZSize.y*std::cos(m_virtualDirZenith[i]))/ m_verticalIrradiance[k]*PHRT_M_PI<< " ";
				}
				out << endl;
			}

			out.close();
		}
	}

	void setDestinationFile(string destinationFile) {
		m_destnationFile = destinationFile;
	}

	void setSceneBoundPlaneSize(Vector2 size) {
		this->m_scenBoundPlaneSize = size;
	}

	void setVirtualBoundXZSize(Vector2 size) {
		this->m_virtualBoundXZSize = size;
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
			for (int i = 0; i < arr.size()-1; i = i+2) {
				double zen = degree2rad(atof(arr[i].c_str()));
				m_virtualDirZenith.push_back(zen);
				double azi = degree2rad(atof(arr[i + 1].c_str()));
				m_virtualDirAzimuth.push_back(azi);
				double x = -std::sin(zen)*std::cos(0.5*PHRT_M_PI - azi);
				double y = std::cos(zen);
				double z = std::sin(zen)*std::sin(0.5*PHRT_M_PI - azi);
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
						double x = -std::sin(zen)*std::cos(0.5*PHRT_M_PI - azi);
						double y = std::cos(zen);
						double z = std::sin(zen)*std::sin(0.5*PHRT_M_PI - azi);
						m_virtualDirXYZ.push_back(x);
						m_virtualDirXYZ.push_back(y);
						m_virtualDirXYZ.push_back(z);
						m_nVirtualDirections++;
					}
				}
			}
		}

		//initialize m_virtualBRFs
		for (int i = 0; i < m_nVirtualDirections; i++) {
			m_virtualBRFs.push_back(Spectrum(0.0));
			m_accBRFsPerDirection.push_back(0);
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
	vector<vector<Spectrum>> m_brfs;//brf for each zenith and each azimuth
	int numberOfZenith=0; // Total number of zenith angles
	vector<int> numberOfAzimuth; //Number of azimuth angles for each zenith angle
	string m_destnationFile; //output file path
	
	vector<double> m_virtualDirZenith;
	vector<double> m_virtualDirAzimuth;
	vector<double> m_virtualDirXYZ;
	vector<Spectrum> m_virtualBRFs;
	vector<int> m_accBRFsPerDirection; //Number of accumulated BRFs for each direction.
	int m_nVirtualDirections=0;

	//no need to serilize
	int m_numOfDirections=0;
	Vector2 m_scenBoundPlaneSize;
	Spectrum m_verticalIrradiance;
	Vector2 m_virtualBoundXZSize;
};


MTS_NAMESPACE_END
#endif
