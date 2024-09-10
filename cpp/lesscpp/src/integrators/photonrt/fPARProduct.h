#pragma once

//Implementing a storage class to store directional BRF/radiance
//value for different directions

#if !defined(_FPARPRODUCT_H_)
#define _FPARPRODUCT_H_

#include <iostream>
#include <vector>
#include <map>
#include <fstream>
#include "photonRTUtils.h"
#include <mitsuba/core/spectrum.h>
#include <mitsuba/mitsuba.h>
#include <boost/algorithm/string.hpp>
#include <iomanip>      // std::setprecision
#include <unordered_map>

using namespace std;

MTS_NAMESPACE_BEGIN

class fPARProduct :public Object {
public:
	fPARProduct(string layerDefinition, int numberOfEscDirections) {
		std::vector<std::string> tmp;
		boost::algorithm::split(tmp, layerDefinition, boost::is_any_of(":,/"));
		if (tmp.size() >= 3) { //mode: from:step:to
			double from = atof(tmp[0].c_str());
			double step = atof(tmp[1].c_str());
			double to = atof(tmp[2].c_str());
			int i = 0;
			while (true) {
				double layerHeightLower = from + i * step;
				double layerheightUpper = from + (i + 1)*step;
				if (layerheightUpper > to) {
					break;
				}
				i++;
				m_layerLowerBounds.push_back(layerHeightLower);
				m_layerUpperBounds.push_back(layerheightUpper);
				m_totalFPAR.push_back(Spectrum(0.0));
				m_totalIncidentPAR.push_back(Spectrum(0.0));
			}
			m_mumberOfLayers = i;
		}
		if (tmp.size() >= 4) {
			m_outputMode = atoi(tmp[3].c_str());
		}
		if (tmp.size() >= 5 && m_outputMode == 2) {
			for (int i = 4; i < tmp.size(); i++) {
				if(tmp[i] != "")
					m_considerTriangleInstances.push_back(tmp[i]);
			}
		}

		m_numComponents = 0;

		for (int i = 0; i < 30; i++) {
			m_reprobs[i] = vector<int>();
			m_reprobs.at(i).push_back(0);  //total photons on leaf
			m_reprobs.at(i).push_back(0);  //total re-intercepted (exclude terrain)
			m_reprobs.at(i).push_back(0);  //up ward photons
			m_reprobs.at(i).push_back(0);  //downward photons
			m_reprobs.at(i).push_back(0);  // total launched photons in reference plane
			m_reprobs.at(i).push_back(0);   // total intercept photons by canopy
		}

		// Esc probability
		m_numOfDirections = numberOfEscDirections;
		PhotonRTUtils::generationDiscreteDirections(m_numOfDirections, accumulated_ZenithAngle, accumulated_azimuthAngle);
		numberOfZenith = accumulated_ZenithAngle.size();
		for (int i = 0; i < numberOfZenith; i++) {
			numberOfAzimuth.push_back(accumulated_azimuthAngle[i].size());
			vector<vector<int>> aziTmp;
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				vector<int> scatter_order = vector<int>();
				for (int i = 0; i < 30; i++) {
					scatter_order.push_back(0);
				}
				aziTmp.push_back(scatter_order);
			}
			m_dirEscProbs.push_back(aziTmp);

		}
	}

	void serialize(Stream *stream) const {
		stream->writeInt(m_mumberOfLayers);
		stream->writeDoubleArray(m_layerLowerBounds.data(), m_mumberOfLayers);
		stream->writeDoubleArray(m_layerUpperBounds.data(), m_mumberOfLayers);
		stream->writeInt(m_numComponents);
		for (int i = 0; i < m_numComponents; i++)
			stream->writeString(m_components[i]);

		for (int i = 0; i < m_numComponents; i++) {
			string compName = m_components[i];
			for(int j=0;j<m_mumberOfLayers;j++)
				m_fPAR.at(compName)[j].serialize(stream);
		}

		//temp
		for (int i = 0; i < m_mumberOfLayers; i++) {
			m_totalFPAR[i].serialize(stream);
			m_totalIncidentPAR[i].serialize(stream);
		}
			

		//prob
		for (int i = 0; i < 30; i++) {
			stream->writeIntArray(m_reprobs.at(i).data(), 6);
		}

		//directinal esc probablity
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
				stream->writeIntArray(m_dirEscProbs[i][j].data(), 30);
			}
		}
	}
	void unserialize(Stream *stream) {
		m_mumberOfLayers = stream->readInt();
		m_layerLowerBounds.resize(m_mumberOfLayers);
		stream->readDoubleArray(m_layerLowerBounds.data(), m_mumberOfLayers);
		m_layerUpperBounds.resize(m_mumberOfLayers);
		stream->readDoubleArray(m_layerUpperBounds.data(), m_mumberOfLayers);
		m_numComponents = stream->readInt();
		m_components.resize(m_numComponents);
		for (int i = 0; i < m_numComponents; i++)
			m_components[i] = stream->readString();

		m_fPAR.clear();
		for (int i = 0; i < m_numComponents; i++) {
			string compName = m_components[i];
			m_fPAR[compName] = vector<Spectrum>();
			m_fPAR[compName].resize(m_mumberOfLayers);
			for (int j = 0; j<m_mumberOfLayers; j++)
				m_fPAR.at(compName)[j] = Spectrum(stream);
		}

		//temp
		for (int i = 0; i < m_mumberOfLayers; i++) {
			m_totalFPAR[i] = Spectrum(stream);
			m_totalIncidentPAR[i] = Spectrum(stream);
		}
			

		//prob
		for (int i = 0; i < 30; i++) {
			m_reprobs[i] = vector<int>();
			m_reprobs.at(i).resize(6);
			stream->readIntArray(m_reprobs.at(i).data(), 6);
		}

		//esc probability
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
			vector<vector<int>> aziTmp;
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				vector<int> scatter_order = vector<int>();
				scatter_order.resize(30);
				stream->readIntArray(scatter_order.data(), 30);
				aziTmp.push_back(scatter_order);
				
			}
			getEscProbData().push_back(aziTmp);
		}
	}

	vector<vector<double>> getazimuthAngleData() const {
		return accumulated_azimuthAngle;
	}

	vector<vector<vector<int>>> getEscProbData() const {
		return m_dirEscProbs;
	}

	double broadbandEnergy(Spectrum energy) {
		if (SPECTRUM_SAMPLES == 1)
			return energy[0];

		double total = 0.0;
		for (int j = 0; j < SPECTRUM_SAMPLES-1; j++) {
			total += (energy[j] + energy[j + 1])*(m_wavelengths[j + 1] - m_wavelengths[j])*0.5;
		}
		return total;
	}

	inline double rad2degree(double rad) {
		return rad / PHRT_M_PI * 180;
	}

	void develop(double scale = 1.0) {
		if (m_destnationFile != "") {
			Spectrum totalIncidentW = scale * 1 / (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y)*(m_virtualBoundXZSize.x*m_virtualBoundXZSize.y)*m_verticalIrradiance;
			ofstream out(m_destnationFile);
			ofstream par_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_APAR.txt");
			ofstream inc_par_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_incident_PAR.txt");
			out << "**FPAR**" << endl;
			out << "layer_bottom  layer_upper  TfPAR ";
			par_out << "**APAR (W): Absorbed Photosynthetically Active Radiation**" << endl;
			par_out << "layer_bottom  layer_upper  TAPAR ";
			inc_par_out << "**Incident PAR (W) for each layer, including multiple scattering (i.e., energy entering each layer from both top and down layers)" << endl;
			inc_par_out << "layer_bottom  layer_upper  TotalIncidentPAR ";
			for (int i = 0; i < m_numComponents; i++) {
				out << m_components[i] << " ";
				par_out << m_components[i] << " ";
			}
				
			out << endl;
			par_out << endl;
			inc_par_out << endl;
			for (int i = 0; i < m_mumberOfLayers; i++) {
				out <<std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
				out << std::fixed << std::setprecision(4) << setw(8) << broadbandEnergy(scale*m_totalFPAR[i]) / broadbandEnergy(totalIncidentW) << " ";

				par_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
				par_out << std::fixed << std::setprecision(4) << setw(8) << broadbandEnergy(scale * m_totalFPAR[i])<< " ";

				inc_par_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
				inc_par_out << std::fixed << std::setprecision(4) << setw(8) << broadbandEnergy(scale * m_totalIncidentPAR[i]);

				for (int j = 0; j < m_numComponents; j++) {
					string compName = m_components[j];
					double fpar = broadbandEnergy(scale*m_fPAR.at(compName)[i]) / broadbandEnergy(totalIncidentW);
					out << std::fixed << std::setprecision(4)<< setw(8) << fpar<<" ";
					par_out << std::fixed << std::setprecision(4) << setw(8) << broadbandEnergy(scale * m_fPAR.at(compName)[i]) << " ";
				}
				out << endl;
				par_out << endl;
				inc_par_out << endl;
			}

			//Absorption for each band
			if (m_boolOutParEachBand) {
				out << endl << "**Absorption for each band**" << endl;
				out << " - Total Absorption" << endl;
				out << "layer_bottom  layer_upper  Absorption_For_Each_Band..." << endl;

				par_out << endl << "**Absorption for each band (W)**" << endl;
				par_out << " - Total Absorption" << endl;
				par_out << "layer_bottom  layer_upper  Absorption_For_Each_Band..." << endl;

				inc_par_out << endl << "**Incident PAR for each band (W)**" << endl;
				inc_par_out << "layer_bottom  layer_upper  Absorption_For_Each_Band..." << endl;

				for (int j = 0; j < m_mumberOfLayers; j++) {
					out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[j] << " " << setw(8) << m_layerUpperBounds[j] << " ";
					par_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[j] << " " << setw(8) << m_layerUpperBounds[j] << " ";
					inc_par_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[j] << " " << setw(8) << m_layerUpperBounds[j] << " ";
					for (int k = 0; k < SPECTRUM_SAMPLES; k++) {
						out << std::fixed << std::setprecision(4) << setw(8) << scale * m_totalFPAR[j][k] / totalIncidentW[k] << " ";
						par_out << std::fixed << std::setprecision(4) << setw(8) << scale * m_totalFPAR[j][k] << " ";
						inc_par_out << std::fixed << std::setprecision(4) << setw(8) << scale * m_totalIncidentPAR[j][k] << " ";
					}
					out << endl;
					par_out << endl;
					inc_par_out << endl;
				}
				for (int i = 0; i < m_numComponents; i++) {
					out << endl << " - Absorption of " << m_components[i] << endl;
					out << "layer_bottom  layer_upper  Absorption_For_Each_Band..." << endl;
					par_out << endl << " - Absorption of " << m_components[i] << endl;
					par_out << "layer_bottom  layer_upper  Absorption_For_Each_Band..." << endl;
					for (int j = 0; j < m_mumberOfLayers; j++) {
						out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[j] << " " << setw(8) << m_layerUpperBounds[j] << " ";
						par_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[j] << " " << setw(8) << m_layerUpperBounds[j] << " ";
						string compName = m_components[i];
						Spectrum fpar = scale * m_fPAR.at(compName)[j] / totalIncidentW;
						for (int k = 0; k < SPECTRUM_SAMPLES; k++) {
							out << std::fixed << std::setprecision(4) << setw(8) << fpar[k] << " ";
							par_out << std::fixed << std::setprecision(4) << setw(8) << scale * m_fPAR.at(compName)[j][k] << " ";
						}
						out << endl;
						par_out << endl;
					}
				}
			}
			out.close();
			par_out.close();
			inc_par_out.close();


			ofstream coco_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_ftrans_coco.txt");
			for (int k = 0; k < SPECTRUM_SAMPLES; k++) {
				coco_out << std::fixed << std::setprecision(4) << setw(8) << scale * m_ftran_coco[k] / totalIncidentW[k] << " ";
			}
			coco_out << endl;
			coco_out.close();

			ofstream uc_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_ftrans_uc.txt");
			for (int k = 0; k < SPECTRUM_SAMPLES; k++) {
				uc_out << std::fixed << std::setprecision(4) << setw(8) << scale * m_ftran_uc[k] / totalIncidentW[k] << " ";
			}
			uc_out << endl;
			uc_out.close();

			ofstream tot_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_ftrans_tot.txt");
			for (int k = 0; k < SPECTRUM_SAMPLES; k++) {
				tot_out << std::fixed << std::setprecision(4) << setw(8) << scale * m_ftran_tot[k] / totalIncidentW[k] << " ";
			}
			tot_out << endl;
			tot_out.close();

		}

		//prob
		if (m_destnationProbFile != "") {
			ofstream out(m_destnationProbFile);
			out << "**Spectral invariant (probability)**" << endl;

			out << " - Canopy interception probability" << endl;
			out << std::fixed << std::setprecision(4) << setw(8) << (double)m_reprobs.at(0)[5] / (double(m_reprobs.at(0)[4])) << endl;

			out << " - Total probability" << endl;
			int totalPhotons = 0;
			int collisionPhotons = 0;
			int upwardPhotons = 0;
			int downwardPhotons = 0;
			for (int i = 0; i < 30; i++) {
				totalPhotons += m_reprobs.at(i)[0];
				collisionPhotons += m_reprobs.at(i)[1];
				upwardPhotons += m_reprobs.at(i)[2];
				downwardPhotons += m_reprobs.at(i)[3];
			}
			out << std::fixed << std::setprecision(4) << setw(8) << (double)collisionPhotons / (double(totalPhotons)) << endl;


			out << " - Upward/Downward escape probability" << endl;
			out << std::fixed << std::setprecision(4) << setw(8) << (double)upwardPhotons / (double(totalPhotons)) << "/";
			out << std::fixed << std::setprecision(4) << setw(8) << (double)downwardPhotons / (double(totalPhotons)) << endl;

			out << endl<< " - Probability for each scattering order" << endl;
			out << "Scat_order Tot_photons Its_photons Up_escape_photons Down_escape_photons" << endl;
			for (int i = 0; i < 30; i++) {
				out << std::fixed << setw(10) << (i + 1);
				out << std::fixed << std::setprecision(10) << setw(12)<< m_reprobs.at(i)[0];
				out << std::fixed << std::setprecision(10) << setw(12)<< m_reprobs.at(i)[1];
				out << std::fixed << std::setprecision(10) << setw(18) << m_reprobs.at(i)[2];
				out << std::fixed << std::setprecision(10) << setw(20) << m_reprobs.at(i)[3] << endl;
			}

			//ESC probility
			vector<double> zenithAngle(accumulated_ZenithAngle);
			vector<vector<double>> azimuthAngle(accumulated_azimuthAngle);
			if (numberOfAzimuth[0] == 1) {
				zenithAngle.insert(zenithAngle.begin(), -accumulated_ZenithAngle[0]);
			}
			else {
				zenithAngle.insert(zenithAngle.begin(), 0);
			}
			for (int i = 0; i < accumulated_ZenithAngle.size(); i++) {
				azimuthAngle[i].insert(azimuthAngle[i].begin(), 0);
			}
			out << endl << " - Directinal Escape Probability for upper hemisphere (Number of directions=" << m_numOfDirections<<")"<< endl;
			for (int ii = 0; ii < 30; ii++) {
				out << "Scattering order: " << std::fixed << setw(3) << (ii + 1) << endl;
				out << "Zentih_Angle Azimuth_Angle Escape_photons" << endl;
				for (int zen = 1; zen < zenithAngle.size(); zen++) {
					for (int azi = 1; azi < azimuthAngle[zen - 1].size(); azi++) {
						double centerZenith = 0.5 * (zenithAngle[zen] + zenithAngle[zen - 1]);
						double centerAzi = 0.5 * (azimuthAngle[zen - 1][azi] + azimuthAngle[zen - 1][azi - 1]);
						out << std::fixed << std::setprecision(2) << setw(12) << rad2degree(centerZenith);
						out << std::fixed << std::setprecision(2) << setw(14) << rad2degree(centerAzi);
						out << std::fixed << std::setprecision(2) << setw(15) << m_dirEscProbs[zen-1][azi-1][ii];
						out << endl;
					}
				}
				out << endl;
			}
			out.close();
		}
	}

	void clear() {
		m_verticalIrradiance = Spectrum(0.0);
		m_fPAR.clear();

		m_numComponents = 0;
		m_components.clear();

		//
		//temp

		m_totalFPAR.clear();
		m_totalIncidentPAR.clear();
		for (int i = 0; i < m_mumberOfLayers; i++) {
			m_totalFPAR.push_back(Spectrum(0.0));
			m_totalIncidentPAR.push_back(Spectrum(0.0));
		}
			

		//prob
		for (int i = 0; i < 30; i++) {
			m_reprobs.at(i) = vector<int>();
			m_reprobs.at(i).push_back(0);
			m_reprobs.at(i).push_back(0);
			m_reprobs.at(i).push_back(0);
			m_reprobs.at(i).push_back(0);
			m_reprobs.at(i).push_back(0);
			m_reprobs.at(i).push_back(0);
		}

		m_ftran_coco = Spectrum(0.0);
		m_ftran_uc = Spectrum(0.0);
		m_ftran_tot = Spectrum(0.0);
		m_ftran_vprof.clear();

		//prob esc
		m_dirEscProbs.clear();
		for (int i = 0; i < numberOfZenith; i++) {
			vector<vector<int>> aziTmp;
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				vector<int> scatter_order = vector<int>();
				for (int i = 0; i < 30; i++) {
					scatter_order.push_back(0);
				}
				aziTmp.push_back(scatter_order);
			}
			m_dirEscProbs.push_back(aziTmp);
		}
	}

	//merge another directionalBRF in current one
	void merge(const fPARProduct* fPARs) {
		m_verticalIrradiance += fPARs->m_verticalIrradiance;
		for (int i = 0; i < fPARs->m_numComponents; i++) {
			string compName = fPARs->m_components[i];
			vector<Spectrum> compLayerFpar = fPARs->m_fPAR.at(compName);
			if (m_fPAR.count(compName) == 0) {//Î´³öÏÖ
				m_fPAR[compName] = fPARs->m_fPAR.at(compName);
				m_numComponents++;
				m_components.push_back(compName);
			}
			else {
				for (int j = 0; j < m_mumberOfLayers; j++)
					m_fPAR.at(compName)[j] += fPARs->m_fPAR.at(compName)[j];
			}
		}

		//tmp
		for (int i = 0; i < m_mumberOfLayers; i++) {
			m_totalFPAR[i] += fPARs->m_totalFPAR[i];
			m_totalIncidentPAR[i] += fPARs->m_totalIncidentPAR[i];
		}

		//prob
		for (int i = 0; i < 30; i++) {
			m_reprobs.at(i)[0] += fPARs->m_reprobs.at(i)[0];
			m_reprobs.at(i)[1] += fPARs->m_reprobs.at(i)[1];
			m_reprobs.at(i)[2] += fPARs->m_reprobs.at(i)[2];
			m_reprobs.at(i)[3] += fPARs->m_reprobs.at(i)[3];
			m_reprobs.at(i)[4] += fPARs->m_reprobs.at(i)[4];
			m_reprobs.at(i)[5] += fPARs->m_reprobs.at(i)[5];
		}

		//rami5
		m_ftran_coco += fPARs->m_ftran_coco;
		m_ftran_uc += fPARs->m_ftran_uc;
		m_ftran_tot += fPARs->m_ftran_tot;

		//esc probability
		for (int i = 0; i < numberOfZenith; i++) {
			for (int j = 0; j < numberOfAzimuth[i]; j++) {
				for(int k=0;k<30;k++)
					m_dirEscProbs[i][j][k] += fPARs->getEscProbData()[i][j][k];
			}
		}
	}

	//Collect total irradiance at the top of the virtual plane for BRF calculation.
	void putIrradiance(Spectrum value) {
		m_verticalIrradiance += value;
	}

	void put(int depth,const Intersection &its, Point& previousPoint, Spectrum absorbedEnergy, Spectrum incidentEnergy, bool & isIntersectedWithTerrainAlready) {
		Point p = its.p;
		string compName = its.shape->getName();
		if (m_outputMode == 1) {
			if (its.instance) {
				compName = its.instance->getName()+"_"+ compName;
			}
		}
		else if (m_outputMode == 2) {
			if (its.instance) {
				string instance_name = its.instance->getName();
				if (m_considerTriangleInstances.size() == 0) {
					compName = its.instance->getName() + "_" + compName + "_" + to_string(its.primIndex);
				}
				else {
					if (std::find(m_considerTriangleInstances.begin(), m_considerTriangleInstances.end(), instance_name) != m_considerTriangleInstances.end()) {
						compName = its.instance->getName() + "_" + compName + "_" + to_string(its.primIndex);
					}
					else {
						compName = its.instance->getName() + "_" + compName;
					}
				}
				
			}
		}
		double step = m_layerUpperBounds[0] - m_layerLowerBounds[0];
		int index = (int)((p.y - m_layerLowerBounds[0]) / step);
		int pre_index = (int)((previousPoint.y - m_layerLowerBounds[0]) / step);
		if (index >= 0 && index <= m_mumberOfLayers - 1) {

			//tmp
			m_totalFPAR[index] += absorbedEnergy;

			if (m_fPAR.count(compName) == 0) {
				m_numComponents++;
				m_components.push_back(compName);
				m_fPAR[compName].resize(m_mumberOfLayers);
				for (int j = 0; j<m_mumberOfLayers; j++)
					m_fPAR.at(compName)[j] = Spectrum(0.0);	
			}
			m_fPAR.at(compName)[index] += absorbedEnergy;

			//incident par 
			if (pre_index >= 0 && pre_index <= m_mumberOfLayers - 1) {
				if (pre_index < index) {
					for (int i = pre_index + 1; i <= index; i++) {
						m_totalIncidentPAR[i] += incidentEnergy;
					}
				}
				else {
					for (int i = index; i < pre_index; i++) {
						m_totalIncidentPAR[i] += incidentEnergy;
					}
				}
			}
			else {
				for (int i = index; i < m_mumberOfLayers; i++) {
					m_totalIncidentPAR[i] += incidentEnergy;
				}
			}
		}

		if (compName == "terrain") {
			if ((depth >= 2) && (!isIntersectedWithTerrainAlready)) {
				m_ftran_coco += incidentEnergy;
			}

			if (depth == 1) {
				m_ftran_uc += incidentEnergy;
			}
			m_ftran_tot += incidentEnergy;
			isIntersectedWithTerrainAlready = true;
		}

	}

	//its is the intersection with the surface containing the medium, it is th exiting point
	void put(int depth, const Intersection& its, const MediumSamplingRecord& mRec, Spectrum absorbedEnergy) {
		Point p = mRec.p;
		string compName = its.shape->getName();
		if (m_outputMode == 1 || m_outputMode == 2) {
			if (its.instance) {
				compName = its.instance->getName() + "_" + compName;
			}
		}
		double step = m_layerUpperBounds[0] - m_layerLowerBounds[0];
		int index = (int)((p.y - m_layerLowerBounds[0]) / step);
		if (index >= 0 && index <= m_mumberOfLayers - 1) {

			//tmp
			m_totalFPAR[index] += absorbedEnergy;

			if (m_fPAR.count(compName) == 0) {
				m_numComponents++;
				m_components.push_back(compName);
				m_fPAR[compName].resize(m_mumberOfLayers);
				for (int j = 0; j < m_mumberOfLayers; j++)
					m_fPAR.at(compName)[j] = Spectrum(0.0);
			}
			m_fPAR.at(compName)[index] += absorbedEnergy;
		}
	}

	void putReProb(int depth, const Intersection &its, int previousStatus, Ray& ray) {
		if (depth == 1) {
			m_reprobs.at(0)[4]++;
			if (its.isValid() && its.shape->getID() != "terrain") {
				m_reprobs.at(0)[5]++;
			}
		}
		else if (depth >= 2 && depth <= 31 && (previousStatus == 2)) {
			m_reprobs.at(depth - 2)[0]++;
			string compName = its.shape->getID();
			if (its.isValid() && compName != "terrain") {
				m_reprobs.at(depth - 2)[1]++;
			}
			else {  //escaped
				if (ray.d.y >= 0) {
					m_reprobs.at(depth - 2)[2]++;

					//directinal esc prob
					double zenithAngle = math::safe_acos(ray.d.y);
					double AzimuthAngle = 0.5 * PHRT_M_PI - atan2(ray.d.z, -ray.d.x);
					if (AzimuthAngle < 0) AzimuthAngle += 2 * PHRT_M_PI;
					int zenithIndex;
					//determine the zenith solid angle patch
					int i = 0;
					for (i = 0; i < accumulated_ZenithAngle.size(); i++) {
						if (zenithAngle <= accumulated_ZenithAngle[i]) {
							break;
						}
					}
					zenithIndex = i;
					//determine azimuth index
					double aziInterval = PHRT_M_PI * 2 / accumulated_azimuthAngle[zenithIndex].size();
					int aziIndex = int(AzimuthAngle / aziInterval);
					if (zenithIndex >= 0 && zenithIndex < m_dirEscProbs.size() &&
						aziIndex >= 0 && aziIndex < m_dirEscProbs[zenithIndex].size()) {
						m_dirEscProbs[zenithIndex][aziIndex][depth - 2]++;
					}
				}
				else {
					m_reprobs.at(depth - 2)[3]++;
				}
				
			}
		}
	}

	void setDestinationFile(string destinationFile) {
		m_destnationFile = destinationFile;
	}
	void setDestnationProbFile(string destnationProbFile) {
		m_destnationProbFile = destnationProbFile;
	}

	void setSceneBoundPlaneSize(Vector2 size) {
		this->m_scenBoundPlaneSize = size;
	}

	void setVirtualBoundXZSize(Vector2 size) {
		this->m_virtualBoundXZSize = size;
	}
	void setWavelengths(Spectrum spectrum) {
		this->m_wavelengths = spectrum;
	}

public:
	vector<double> accumulated_ZenithAngle; // the list of zenith angles
	vector<vector<double>> accumulated_azimuthAngle; // the list of azimuth angles for each zenith angle
	vector<vector<vector<int>>> m_dirEscProbs;//directional Escape Prob for each zenith and each azimuth, each direction is a vector store 30 scattering orders
	int numberOfZenith = 0; // Total number of zenith angles
	vector<int> numberOfAzimuth; //Number of azimuth angles for each zenith angle
	int m_numOfDirections = 1;  //Number of directions to discrete upper hemisphere
	vector<string> m_considerTriangleInstances;  //When m_outputMode=2, only consider the listed object for calculate fpar of each triangle. By default, considers all object

	vector<double> m_layerLowerBounds;
	vector<double> m_layerUpperBounds;
	int m_numComponents;// Number of components
	vector<string> m_components;
	std::unordered_map<string, vector<Spectrum> > m_fPAR;  // absorption of each components and each layer
	int m_mumberOfLayers;
	vector<Spectrum> m_totalFPAR;  // total absorption of each layer
	vector<Spectrum> m_totalIncidentPAR; // total incident par for each layer, including multiple scattering
	int m_outputMode = 0; // 0: output each component; 1: output each instance-component; 2: output each instance-component-triangle

	//re-collision probablity
	std::unordered_map<int, vector<int>> m_reprobs;
	string m_destnationProbFile;

	//For RAMI5
	Spectrum m_ftran_coco;
	Spectrum m_ftran_uc;
	Spectrum m_ftran_tot;
	vector<Spectrum> m_ftran_vprof;

	//no need to serilize
	string  m_destnationFile;//The path to store the fpar products
	Vector2 m_scenBoundPlaneSize; //used to calculate totcal incident energy w/m2
	Spectrum m_verticalIrradiance; // total energy incident on the top of the scene
	Vector2 m_virtualBoundXZSize; //only compute the energy which has been incident on the virtual plane
	Spectrum m_wavelengths;

	bool m_boolOutParEachBand=false; //output par for each band
};


MTS_NAMESPACE_END
#endif