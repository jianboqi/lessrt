#pragma once

//Implementing a storage class to store directional Fluor/radiance
//value for different directions

#if !defined(_MultiLevelFluor_)
#define _MultiLevelFluor_

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

#define AVOGADRO_C            6.02214e23             // [mol-1]       Constant of Avogadro
#define PLANCK_C              6.626070040e-34        // [J s]         Planck's constant
#define LIGHT_SPEED_C         299792458              // [m s-1]       Speed of light 
#define PLANCK_LIGHT_SPEED_C  1.986445824171758e-25  // PLANCK_C * LIGHT_SPEED_C
#define HALF_PI               M_PI*0.5               // pi/2


class MultiLevelFluor :public Object {
public:
	MultiLevelFluor(string layerDefinition, Spectrum wavelengths) {
		std::vector<std::string> tmp;
		boost::algorithm::split(tmp, layerDefinition, boost::is_any_of(":,/"));
		if (tmp.size() >= 3) { //mode: from:step:to
			double from = atof(tmp[0].c_str());
			double step = atof(tmp[1].c_str());
			double to = atof(tmp[2].c_str());
			int i = 0;
			while (true) {
				double layerHeightLower = from + i * step;
				double layerheightUpper = from + (i + 1) * step;
				if (layerheightUpper > to) {
					break;
				}
				i++;
				m_layerLowerBounds.push_back(layerHeightLower);
				m_layerUpperBounds.push_back(layerheightUpper);
				m_total_psi_fluor.push_back(Spectrum(0.0));
				m_total_psii_fluor.push_back(Spectrum(0.0));
				m_total_l_fluor_PSI.push_back(Spectrum(0.0));
				m_total_l_fluor_PSII.push_back(Spectrum(0.0));
			}
			m_mumberOfLayers = i;
		}
		if (tmp.size() >= 4) {
			m_outputMode = atoi(tmp[3].c_str());
		}
		if (tmp.size() >= 5 && m_outputMode == 2) {
			for (int i = 4; i < tmp.size(); i++) {
				if (tmp[i] != "")
					m_considerTriangleInstances.push_back(tmp[i]);
			}
		}
		m_numComponents = 0;
		setWavelengths(wavelengths);
	}

	void serialize(Stream* stream) const {
		stream->writeInt(m_mumberOfLayers);
		stream->writeDoubleArray(m_layerLowerBounds.data(), m_mumberOfLayers);
		stream->writeDoubleArray(m_layerUpperBounds.data(), m_mumberOfLayers);
		stream->writeInt(m_numComponents);

		for (int i = 0; i < m_numComponents; i++)
			stream->writeString(m_components[i]);

		for (int i = 0; i < m_numComponents; i++) {
			string compName = m_components[i];
			for (int j = 0; j < m_mumberOfLayers; j++) {
				m_psi_fluor.at(compName)[j].serialize(stream);
				m_psii_fluor.at(compName)[j].serialize(stream);
				m_l_fluor_PSI.at(compName)[j].serialize(stream);
				m_l_fluor_PSII.at(compName)[j].serialize(stream);
			}
		}
		//temp
		for (int i = 0; i < m_mumberOfLayers; i++) {
			m_total_psi_fluor[i].serialize(stream);
			m_total_psii_fluor[i].serialize(stream);
			m_total_l_fluor_PSI[i].serialize(stream);
			m_total_l_fluor_PSII[i].serialize(stream);
		}
		m_wavelengths.serialize(stream);
		m_wavelengths_m.serialize(stream);
		m_ep.serialize(stream);
	}

	void unserialize(Stream* stream) {
		m_mumberOfLayers = stream->readInt();
		m_layerLowerBounds.resize(m_mumberOfLayers);
		stream->readDoubleArray(m_layerLowerBounds.data(), m_mumberOfLayers);
		m_layerUpperBounds.resize(m_mumberOfLayers);
		stream->readDoubleArray(m_layerUpperBounds.data(), m_mumberOfLayers);
		m_numComponents = stream->readInt();
		m_components.resize(m_numComponents);
		for (int i = 0; i < m_numComponents; i++)
			m_components[i] = stream->readString();

		m_psi_fluor.clear();
		m_psii_fluor.clear();
		m_l_fluor_PSI.clear();
		m_l_fluor_PSII.clear();
		for (int i = 0; i < m_numComponents; i++) {
			string compName = m_components[i];
			m_psi_fluor[compName] = vector<Spectrum>();
			m_psi_fluor[compName].resize(m_mumberOfLayers);
			m_psii_fluor[compName] = vector<Spectrum>();
			m_psii_fluor[compName].resize(m_mumberOfLayers);
			m_l_fluor_PSI[compName] = vector<Spectrum>();
			m_l_fluor_PSI[compName].resize(m_mumberOfLayers);
			m_l_fluor_PSII[compName] = vector<Spectrum>();
			m_l_fluor_PSII[compName].resize(m_mumberOfLayers);
			for (int j = 0; j < m_mumberOfLayers; j++) {
				m_psi_fluor.at(compName)[j] = Spectrum(stream);
				m_psii_fluor.at(compName)[j] = Spectrum(stream);
				m_l_fluor_PSI.at(compName)[j] = Spectrum(stream);
				m_l_fluor_PSII.at(compName)[j] = Spectrum(stream);
			}
		}

		//temp
		for (int i = 0; i < m_mumberOfLayers; i++) {
			m_total_psi_fluor[i] = Spectrum(stream);
			m_total_psii_fluor[i] = Spectrum(stream);
			m_total_l_fluor_PSI[i] = Spectrum(stream);
			m_total_l_fluor_PSII[i] = Spectrum(stream);
		}
		m_wavelengths = Spectrum(stream);
		m_wavelengths_m = Spectrum(stream);
		m_ep = Spectrum(stream);
	}

	void clear() {
		m_psi_fluor.clear();
		m_psii_fluor.clear();
		m_l_fluor_PSI.clear();
		m_l_fluor_PSII.clear();

		m_numComponents = 0;
		m_components.clear();

		m_total_psi_fluor.clear();
		m_total_psii_fluor.clear();
		m_total_l_fluor_PSI.clear();
		m_total_l_fluor_PSII.clear();
		for (int i = 0; i < m_mumberOfLayers; i++) {
			m_total_psi_fluor.push_back(Spectrum(0.0));
			m_total_psii_fluor.push_back(Spectrum(0.0));
			m_total_l_fluor_PSI.push_back(Spectrum(0.0));
			m_total_l_fluor_PSII.push_back(Spectrum(0.0));
		}
	}

	//merge another MultiLevelFluorAll in current one
	void merge(const MultiLevelFluor* multimevelFluor) {
		for (int i = 0; i < multimevelFluor->m_numComponents; i++) {
			string compName = multimevelFluor->m_components[i];
			vector<Spectrum> compLayer_ps_fluor_PSI = multimevelFluor->m_psi_fluor.at(compName);
			vector<Spectrum> compLayer_ps_fluor_PSII = multimevelFluor->m_psii_fluor.at(compName);
			vector<Spectrum> compLayer_l_fluor_PSI = multimevelFluor->m_l_fluor_PSI.at(compName);
			vector<Spectrum> compLayer_l_fluor_PSII = multimevelFluor->m_l_fluor_PSII.at(compName);
			if (m_psi_fluor.count(compName) == 0) {//Î´³öÏÖ
				m_psi_fluor[compName] = multimevelFluor->m_psi_fluor.at(compName);
				m_psii_fluor[compName] = multimevelFluor->m_psii_fluor.at(compName);
				m_l_fluor_PSI[compName] = multimevelFluor->m_l_fluor_PSI.at(compName);
				m_l_fluor_PSII[compName] = multimevelFluor->m_l_fluor_PSII.at(compName);
				m_numComponents++;
				m_components.push_back(compName);
			}
			else {
				for (int j = 0; j < m_mumberOfLayers; j++) {
					m_psi_fluor.at(compName)[j] += multimevelFluor->m_psi_fluor.at(compName)[j];
					m_psii_fluor.at(compName)[j] += multimevelFluor->m_psii_fluor.at(compName)[j];
					m_l_fluor_PSI.at(compName)[j] += multimevelFluor->m_l_fluor_PSI.at(compName)[j];
					m_l_fluor_PSII.at(compName)[j] += multimevelFluor->m_l_fluor_PSII.at(compName)[j];
				}
			}
		}

		//tmp
		for (int i = 0; i < m_mumberOfLayers; i++) {
			m_total_psi_fluor[i] += multimevelFluor->m_total_psi_fluor[i];
			m_total_psii_fluor[i] += multimevelFluor->m_total_psii_fluor[i];
			m_total_l_fluor_PSI[i] += multimevelFluor->m_total_l_fluor_PSI[i];
			m_total_l_fluor_PSII[i] += multimevelFluor->m_total_l_fluor_PSII[i];
		}
	}

	void put(int depth, const Intersection& its, Point& previousPoint, Spectrum absorbedEnergy, bool& isIntersectedWithTerrainAlready,
		const BSDF* bsdf, Spectrum excitePSIFluorEnergy, Spectrum excitePSIIFluorEnergy) {
		Point p = its.p;
		string compName = its.shape->getName();
		if (m_outputMode == 1) {
			if (its.instance) {
				compName = its.instance->getName() + "_" + compName;
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
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
				m_total_l_fluor_PSI[index], m_total_l_fluor_PSII[index], excitePSIFluorEnergy, excitePSIIFluorEnergy);

			Float fqeI, fqeII;
			bsdf->getfqe(fqeI, fqeII);
			Spectrum phiI, phiII;
			bsdf->getphi(phiI, phiII);
			Spectrum ps_fluor_PSI, ps_fluor_PSII;
			//computePSFluor(ps_fluor_PSI, ps_fluor_PSII, bsdf->getkChlrel() * absorbedEnergy, fqeI, fqeII, phiI, phiII);//SCOPE v2.1
			computePSFluor1(ps_fluor_PSI, ps_fluor_PSII, absorbedEnergy, fqeI, fqeII, phiI, phiII); if (!IS_FLUSPECT_PRO)ps_fluor_PSI = Spectrum(0.0f);//SCOPE v1.73
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(m_total_psi_fluor[index], m_total_psii_fluor[index], ps_fluor_PSI, ps_fluor_PSII);
			if (m_psi_fluor.count(compName) == 0) {
				m_numComponents++;
				m_components.push_back(compName);
				m_psi_fluor[compName].resize(m_mumberOfLayers);
				m_psii_fluor[compName].resize(m_mumberOfLayers);
				m_l_fluor_PSI[compName].resize(m_mumberOfLayers);
				m_l_fluor_PSII[compName].resize(m_mumberOfLayers);
				for (int j = 0; j < m_mumberOfLayers; j++) {
					m_psi_fluor.at(compName)[j] = Spectrum(0.0);
					m_psii_fluor.at(compName)[j] = Spectrum(0.0);
					m_l_fluor_PSI.at(compName)[j] = Spectrum(0.0);
					m_l_fluor_PSII.at(compName)[j] = Spectrum(0.0);
				}
			}
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
				m_psi_fluor.at(compName)[index], m_psii_fluor.at(compName)[index], ps_fluor_PSI, ps_fluor_PSII);
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
				m_l_fluor_PSI.at(compName)[index], m_l_fluor_PSII.at(compName)[index], excitePSIFluorEnergy, excitePSIIFluorEnergy);
		}
	}
	//its is the intersection with the surface containing the medium, it is th exiting point
	void put(int depth, const Intersection& its, const MediumSamplingRecord& mRec, Spectrum absorbedEnergy,
		const Medium* medium, Spectrum excitePSIFluorEnergy, Spectrum excitePSIIFluorEnergy) {
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
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
				m_total_l_fluor_PSI[index], m_total_l_fluor_PSII[index], excitePSIFluorEnergy, excitePSIIFluorEnergy);

			Float fqeI, fqeII;
			medium->getfqe(fqeI, fqeII);
			Spectrum phiI, phiII;
			medium->getphi(phiI, phiII);
			Spectrum ps_fluor_PSI, ps_fluor_PSII;
			//computePSFluor(ps_fluor_PSI, ps_fluor_PSII, medium->getkChlrel() * absorbedEnergy, fqeI, fqeII, phiI, phiII);//SCOPE v2.1
			computePSFluor1(ps_fluor_PSI, ps_fluor_PSII, absorbedEnergy, fqeI, fqeII, phiI, phiII); if (!IS_FLUSPECT_PRO)ps_fluor_PSI = Spectrum(0.0f);//SCOPE v1.73
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(m_total_psi_fluor[index], m_total_psii_fluor[index], ps_fluor_PSI, ps_fluor_PSII);
			if (m_psi_fluor.count(compName) == 0) {
				m_numComponents++;
				m_components.push_back(compName);
				m_psi_fluor[compName].resize(m_mumberOfLayers);
				m_psii_fluor[compName].resize(m_mumberOfLayers);
				m_l_fluor_PSI[compName].resize(m_mumberOfLayers);
				m_l_fluor_PSII[compName].resize(m_mumberOfLayers);
				for (int j = 0; j < m_mumberOfLayers; j++) {
					m_psi_fluor.at(compName)[j] = Spectrum(0.0);
					m_psii_fluor.at(compName)[j] = Spectrum(0.0);
					m_l_fluor_PSI.at(compName)[j] = Spectrum(0.0);
					m_l_fluor_PSII.at(compName)[j] = Spectrum(0.0);
				}
			}
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
				m_psi_fluor.at(compName)[index], m_psii_fluor.at(compName)[index], ps_fluor_PSI, ps_fluor_PSII);
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(
				m_l_fluor_PSI.at(compName)[index], m_l_fluor_PSII.at(compName)[index], excitePSIFluorEnergy, excitePSIIFluorEnergy);
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
	void setWavelengths(Spectrum spectrum) {
		this->m_wavelengths = spectrum;
		this->m_wavelengths_m = spectrum * 1E-9;
		this->m_hc_lambda = ephoton(m_wavelengths_m);
		this->m_ep = AVOGADRO_C * m_hc_lambda;
		for (register size_t i = 0; i < SPECTRUM_SAMPLES; i++) {
			if (m_wavelengths[i] >= 400 ) {
				m_wavelengths_400_idx = i; break;
			}
		}
		for (register size_t i = m_wavelengths_400_idx; i < SPECTRUM_SAMPLES; i++) {
			if (m_wavelengths[i] > 700) {
				m_wavelengths_700_idx = i - 1; break;
			}
		}
	}

	void develop(size_t hasFluorProducts, double scale = 1.0) {
		//scale *= 1 / (m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y);
		if (m_destnationFile != "") {
			if (hasFluorProducts == 2) {
				ofstream total_ps_f_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_total_PS_Fluor.txt");
				ofstream total_l_f_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_total_Leaf_Fluor.txt");
				total_ps_f_out << "**Total Photosystem ChlF for each layer**" << endl;
				total_ps_f_out << "layer_bottom  layer_upper  PS_Fluor (mW)" << endl;
				total_l_f_out << "**Total Leaf ChlF for each layer**" << endl;
				total_l_f_out << "layer_bottom  layer_upper  Leaf_Fluor (mW)" << endl;

				for (register size_t i = 0; i < m_mumberOfLayers; i++) {
					total_ps_f_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					total_l_f_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					for (register size_t k = 0; k < WANTED_INDEX.size(); k++) {
						total_ps_f_out << std::fixed << std::setprecision(4) << setw(8) << m_total_psi_fluor[i][WANTED_INDEX[k]] * scale << " ";
						total_l_f_out << std::fixed << std::setprecision(4) << setw(8) << m_total_l_fluor_PSI[i][WANTED_INDEX[k]] * scale << " ";
					}
					total_ps_f_out << endl;
					total_l_f_out << endl;
				}

				ofstream ps_f_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_PS_Fluor.txt");
				ofstream l_f_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_Leaf_Fluor.txt");
				ps_f_out << "**Photosystem ChlF for Components**" << endl;
				l_f_out << "**Leaf ChlF for Components" << endl;
				ps_f_out << "layer_bottom  layer_upper  PS_Fluor(mW) ";
				l_f_out << "layer_bottom  layer_upper  Leaf_Fluor(mW) ";
				for (int i = 0; i < m_numComponents; i++) {
					ps_f_out << m_components[i] << " ";
					l_f_out << m_components[i] << " ";
				}
				ps_f_out << endl;
				l_f_out << endl;
				for (int i = 0; i < m_mumberOfLayers; i++) {
					ps_f_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					l_f_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					for (register size_t k = 0; k < WANTED_INDEX.size(); k++) {
						ps_f_out << std::fixed << std::setprecision(4) << setw(8) << m_total_psi_fluor[i][WANTED_INDEX[k]] * scale << " ";
						l_f_out << std::fixed << std::setprecision(4) << setw(8) << m_total_l_fluor_PSI[i][WANTED_INDEX[k]] * scale << " ";
					}
					for (int j = 0; j < m_numComponents; j++) {
						for (register size_t k = 0; k < WANTED_INDEX.size(); k++) {
							ps_f_out << std::fixed << std::setprecision(4) << setw(8) << m_psi_fluor.at(m_components[j])[i][WANTED_INDEX[k]] * scale << " ";
							l_f_out << std::fixed << std::setprecision(4) << setw(8) << m_l_fluor_PSI.at(m_components[j])[i][WANTED_INDEX[k]] * scale << " ";
						}
					}
					ps_f_out << endl;
					l_f_out << endl;
				}
				ps_f_out.close();
				l_f_out.close();
			}
			else if(hasFluorProducts == 1){
				ofstream total_psi_f_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_total_PSI_Fluor.txt");
				ofstream total_psii_f_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_total_PSII_Fluor.txt");
				ofstream total_l_f_psi_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_total_Leaf_Fluor_PSI.txt");
				ofstream total_l_f_psii_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_total_Leaf_Fluor_PSII.txt");
				total_psi_f_out << "**Total Photosystem I ChlF for each layer**" << endl;
				total_psii_f_out << "**Total Photosystem II ChlF for each layer**" << endl;
				total_psi_f_out << "layer_bottom  layer_upper  PSI_Fluor (mW)" << endl;
				total_psii_f_out << "layer_bottom  layer_upper  PSII_Fluor (mW)" << endl;
				total_l_f_psi_out << "**Total Leaf PSI ChlF for each layer**" << endl;
				total_l_f_psii_out << "**Total Leaf PSII ChlF for each layer**" << endl;
				total_l_f_psi_out << "layer_bottom  layer_upper  Leaf_Fluor_PSI (mW)" << endl;
				total_l_f_psii_out << "layer_bottom  layer_upper  Leaf_Fluor_PSII (mW)" << endl;

				for (int i = 0; i < m_mumberOfLayers; i++) {
					total_psi_f_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					total_psii_f_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					total_l_f_psi_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					total_l_f_psii_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					for (int k = 0; k < WANTED_INDEX.size(); k++) {
						total_psi_f_out << std::fixed << std::setprecision(4) << setw(8) << m_total_psi_fluor[i][WANTED_INDEX[k]] * scale << " ";
						total_psii_f_out << std::fixed << std::setprecision(4) << setw(8) << m_total_psii_fluor[i][WANTED_INDEX[k]] * scale << " ";
						total_l_f_psi_out << std::fixed << std::setprecision(4) << setw(8) << m_total_l_fluor_PSI[i][WANTED_INDEX[k]] * scale << " ";
						total_l_f_psii_out << std::fixed << std::setprecision(4) << setw(8) << m_total_l_fluor_PSII[i][WANTED_INDEX[k]] * scale << " ";
					}
					total_psi_f_out << endl;
					total_psii_f_out << endl;
					total_l_f_psi_out << endl;
					total_l_f_psii_out << endl;
				}

				ofstream psi_f_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_PSI_Fluor.txt");
				ofstream psii_f_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_PSII_Fluor.txt");
				ofstream l_f_psi_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_Leaf_Fluor_PSI.txt");
				ofstream l_f_psii_out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_Leaf_Fluor_PSII.txt");
				psi_f_out << "**Photosystem I ChlF for Components**" << endl;
				psii_f_out << "**Photosystem II ChlF for Components**" << endl;
				l_f_psi_out << "**Leaf PSI ChlF for Components" << endl;
				l_f_psii_out << "**Leaf PSII ChlF for Components" << endl;
				psi_f_out << "layer_bottom  layer_upper  PSI_Fluor(mW) ";
				psii_f_out << "layer_bottom  layer_upper  PSII_Fluor(mW) ";
				l_f_psi_out << "layer_bottom  layer_upper  Leaf_Fluor_PSI(mW) ";
				l_f_psii_out << "layer_bottom  layer_upper  Leaf_Fluor_PSII(mW) ";
				for (int i = 0; i < m_numComponents; i++) {
					psi_f_out << m_components[i] << " ";
					psii_f_out << m_components[i] << " ";
					l_f_psi_out << m_components[i] << " ";
					l_f_psii_out << m_components[i] << " ";
				}
				psi_f_out << endl;
				psii_f_out << endl;
				l_f_psi_out << endl;
				l_f_psii_out << endl;
				for (int i = 0; i < m_mumberOfLayers; i++) {
					psi_f_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					psii_f_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					l_f_psi_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					l_f_psii_out << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
					for (register size_t k = 0; k < WANTED_INDEX.size(); k++) {
						psi_f_out << std::fixed << std::setprecision(4) << setw(8) << m_total_psi_fluor[i][WANTED_INDEX[k]] * scale << " ";
						psii_f_out << std::fixed << std::setprecision(4) << setw(8) << m_total_psii_fluor[i][WANTED_INDEX[k]] * scale << " ";
						l_f_psi_out << std::fixed << std::setprecision(4) << setw(8) << m_total_l_fluor_PSI[i][WANTED_INDEX[k]] * scale << " ";
						l_f_psii_out << std::fixed << std::setprecision(4) << setw(8) << m_total_l_fluor_PSII[i][WANTED_INDEX[k]] * scale << " ";
					}
					for (int j = 0; j < m_numComponents; j++) {
						for (register size_t k = 0; k < WANTED_INDEX.size(); k++) {
							psi_f_out << std::fixed << std::setprecision(4) << setw(8) << m_psi_fluor.at(m_components[j])[i][WANTED_INDEX[k]] * scale << " ";
							psii_f_out << std::fixed << std::setprecision(4) << setw(8) << m_psii_fluor.at(m_components[j])[i][WANTED_INDEX[k]] * scale << " ";
							l_f_psi_out << std::fixed << std::setprecision(4) << setw(8) << m_l_fluor_PSI.at(m_components[j])[i][WANTED_INDEX[k]] * scale << " ";
							l_f_psii_out << std::fixed << std::setprecision(4) << setw(8) << m_l_fluor_PSII.at(m_components[j])[i][WANTED_INDEX[k]] * scale << " ";
						}
					}
					psi_f_out << endl;
					psii_f_out << endl;
					l_f_psi_out << endl;
					l_f_psii_out << endl;
				}
				psi_f_out.close();
				psii_f_out.close();
				l_f_psi_out.close();
				l_f_psii_out.close();
			}
		}
	}
	Spectrum e2phot(Spectrum E) {
		Spectrum photons = E / m_hc_lambda;
		return  photons / AVOGADRO_C;
	}

	Spectrum ephoton(Spectrum lambda) {
		return  PLANCK_LIGHT_SPEED_C / lambda;//[J] energy of 1 photon
	}

	Float Sint(Spectrum y, Spectrum x) {
		Float int_sum = 0.0;
		Float step, mean;
		for (register size_t i = 0; i < SPECTRUM_SAMPLES - 1; i++) {
			step = x[i + 1] - x[i];
			mean = 0.5 * (y[i] + y[i + 1]);
			int_sum += mean * step;
		}
		return int_sum;
	}
	//SCOPE v1.73
	void computePSFluor1(Spectrum& ps_fluor_PSI, Spectrum& ps_fluor_PSII, Spectrum absorbedEnergy, Float fqeI, Float fqeII, Spectrum phiI, Spectrum phiII) {
		Float Rn_Cab = 0;
		Float step, mean;
		for (register size_t i = m_wavelengths_400_idx; i < m_wavelengths_700_idx - 1; i++) {
			step = m_wavelengths[i + 1] - m_wavelengths[i];
			mean = 0.5 * (absorbedEnergy[i] + absorbedEnergy[i + 1]);
			Rn_Cab += mean * step;
		}
		m_FluorSpectrum_fun.compute_FluorSpectrum_Equal_M2(ps_fluor_PSI, ps_fluor_PSII, fqeI * Rn_Cab, fqeII * Rn_Cab, Spectrum(1.0f), Spectrum(1.0f), phiI, phiII);
	}
	//SCOPE v2.1
	void computePSFluor(Spectrum& ps_fluor_PSI, Spectrum& ps_fluor_PSII, Spectrum Cab_absorbedEnergy, Float fqeI, Float fqeII, Spectrum phiI, Spectrum phiII) {
		Spectrum Pn_Cab_ = e2phot(Cab_absorbedEnergy); // Net(absorbed) as PAR photons by Cab  0.001 * e2phot(m_wavelengths_m, bsdf->getkChlrel() * absorbedEnergy)
		Float Pn_Cab = Sint(Pn_Cab_, m_wavelengths);// moles m-2 s-1  1E6 * Sint(Pn_Cab_, m_wavelengths)
		Float Pn_Cab_fqeI = Pn_Cab * fqeI;
		Float Pn_Cab_fqeII = Pn_Cab * fqeII;

		//Spectrum ep = AVOGADRO_C * ephoton(m_wavelengths_m);
		m_FluorSpectrum_fun.compute_FluorSpectrum_Equal_M2(ps_fluor_PSI, ps_fluor_PSII, Pn_Cab_fqeI, Pn_Cab_fqeII, m_ep, m_ep, phiI, phiII);
	}

public:

	vector<double> m_layerLowerBounds;
	vector<double> m_layerUpperBounds;
	vector<Spectrum> m_total_psi_fluor;  // total PSI ps fluor of each layer
	vector<Spectrum> m_total_psii_fluor;  // total PSII ps fluor of each layer
	vector<Spectrum> m_total_l_fluor_PSI;  // total PSI leaf fluor of each layer
	vector<Spectrum> m_total_l_fluor_PSII;  // total PSII leaf fluor of each layer
	int m_mumberOfLayers;
	int m_outputMode = 0; // 0: output each component; 1: output each instance-component; 2: output each instance-component-triangle
	vector<string> m_considerTriangleInstances;  //When m_outputMode=2, only consider the listed object for calculate fpar of each triangle. By default, considers all object
	int m_numComponents;// Number of components
	vector<string> m_components;
	std::unordered_map<string, vector<Spectrum> > m_psi_fluor;  // PSI ps fluor of each components and each layer
	std::unordered_map<string, vector<Spectrum> > m_psii_fluor;  // PSII ps fluor of each components and each layer
	std::unordered_map<string, vector<Spectrum> > m_l_fluor_PSI;  // PSI leaf fluor of each components and each layer
	std::unordered_map<string, vector<Spectrum> > m_l_fluor_PSII;  // PSII leaf fluor of each components and each layer
	Spectrum m_wavelengths;//nm
	Spectrum m_wavelengths_m;//m
	int m_wavelengths_400_idx;
	int m_wavelengths_700_idx;
	Spectrum m_ep;
	Spectrum m_hc_lambda;

	//no need to serilize
	string  m_destnationFile;//The path to store the MultiLevelFluor products
	Vector2 m_scenBoundPlaneSize;
	Vector2 m_virtualBoundXZSize;

	//only FluorSpectrum function use
	FluorMatrix m_FluorSpectrum_fun;
};


MTS_NAMESPACE_END
#endif
