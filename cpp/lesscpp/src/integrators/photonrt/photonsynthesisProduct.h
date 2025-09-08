#pragma once

//Implementing a storage class to store directional BRF/radiance
//value for different directions

#if !defined(_PHOTONSYNTHESISRODUCT_H_)
#define _PHOTONSYNTHESISRODUCT_H_

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

#include <numeric>
#include <omp.h>

#define C_e2p_inv  8.359184470515155E-3//  10^-3 / (Planck_constant * Speed_of_light * Constant_of_Avogadro) nuit:W -> moles s-1

using namespace std;

MTS_NAMESPACE_BEGIN

class photonsynthesisProduct :public Object {
public:
	photonsynthesisProduct(string layerDefinition, Spectrum wavelengths) {
		std::vector<std::string> tmp;
		boost::algorithm::split(tmp, layerDefinition, boost::is_any_of(":,/"));
		if (tmp.size() >= 3) { //mode: from:step:to
			double from = atof(tmp[0].c_str());
			double step = atof(tmp[1].c_str());
			double to = atof(tmp[2].c_str());
			int i = 0;
			while (true) {
				double layerHeightLower = from + i * step;
				double layerHeightUpper = from + (i + 1) * step;
				if (layerHeightUpper > to) {
					break;
				}
				i++;
				m_layerLowerBounds.push_back(layerHeightLower);
				m_layerUpperBounds.push_back(layerHeightUpper);
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

		m_components_layers.resize(m_mumberOfLayers);
	}

	void serialize(Stream* stream) const {
		stream->writeInt(m_mumberOfLayers);
		stream->writeDoubleArray(m_layerLowerBounds.data(), m_mumberOfLayers);
		stream->writeDoubleArray(m_layerUpperBounds.data(), m_mumberOfLayers);
		stream->writeInt(m_numComponents);

		for (int i = 0; i < m_numComponents; i++) {
			stream->writeString(m_components[i]);

			string compName = m_components[i];
			stream->writeInt(m_count_sun.at(compName));
			stream->writeInt(m_count_shade.at(compName));

			m_PAR_Chl.at(compName).serialize(stream);
			for (int j = 0; j < m_mumberOfLayers; j++)
				stream->writeInt(m_count_photons.at(compName)[j]);
		}
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

		m_count_sun.clear();
		m_count_shade.clear();
		for (int i = 0; i < m_numComponents; i++) {
			string compName = m_components[i];
			m_count_sun[compName] = 0;
			m_count_shade[compName] = 0;
			m_count_sun.at(compName) = stream->readInt();
			m_count_shade.at(compName) = stream->readInt();
		}

		m_PAR_Chl.clear();
		m_count_photons.clear();
		for (int i = 0; i < m_numComponents; i++) {
			string compName = m_components[i];
			m_PAR_Chl[compName] = Spectrum(0.0f);
			m_PAR_Chl.at(compName) = Spectrum(stream);
			m_count_photons[compName] = vector<unsigned int>();
			m_count_photons[compName].resize(m_mumberOfLayers);
			for (int j = 0; j < m_mumberOfLayers; j++)
				m_count_photons.at(compName)[j] = stream->readInt();
		}
	}

	Float Energy2Quantum(Spectrum energy) {
		if (SPECTRUM_SAMPLES == 1)
			return energy[0];
		energy *= m_wavelengths;
		double total = 0.0;
		for (int j = 0; j < SPECTRUM_SAMPLES - 1; j++) {
			total += (energy[j] + energy[j + 1]) * (m_wavelengths[j + 1] - m_wavelengths[j]) * 0.5;
		}
		return C_e2p_inv * total;
	}

	inline double rad2degree(double rad) {
		return rad / PHRT_M_PI * 180;
	}
	bool isInteger(const std::string& str) {
		std::istringstream iss(str);
		int number;
		char trailingCharacter;

		// noskipws 表示不忽略字符串中的空白字符
		if (!(iss >> std::noskipws >> number)) {
			return false; // 不是一个整数
		}
		// 检查是否有多余字符
		if (iss >> trailingCharacter) {
			return false; // 之后还有多余字符，不是纯整数
		}
		return true; // 是一个整数
	}
	void develop(ref_vector<Bioemitter> bioemitters, bool hasFluor, Float AtsPressure, Float AtsCO2, Float AtsO2, double scale = 1.0) {
		vector<string> shap_name;
		for (size_t i = 0; i < bioemitters.size(); i++) {
			shap_name.push_back(bioemitters[i].get()->get_shape_name());
		}
		Float sceneBoundArea = m_scenBoundPlaneSize.x * m_scenBoundPlaneSize.y;
		std::unordered_map<string, Float > A_comp, trianglesArea_comp, Q_comp, eta_comp;
		std::unordered_map<string, unsigned int > photoNum_comp;
		// 并行区域
		// Before your loop, setup OpenMP environment
		omp_set_dynamic(0);     // Disable dynamic teams
		omp_set_num_threads(1); // Use 4 threads for all consecutive parallel regions  omp_get_max_threads()
		#pragma omp parallel for // Add this line to parallelize the loop
		for (int j = 0; j < m_numComponents; j++) {
			string compName = m_components[j];
			unsigned int ShadePhotonNum = m_count_shade.count(compName) == 0 ? 0 : m_count_shade.at(compName);
			unsigned int SunPhotonNum = m_count_sun.count(compName) == 0 ? 0 : m_count_sun.at(compName);
			unsigned int totalPhotonNum = ShadePhotonNum + SunPhotonNum;

			std::vector<std::string> tmp;
			boost::algorithm::split(tmp, compName, boost::is_any_of("."));
			int primIndex = -1;
			string ShapeName;
			if (isInteger(tmp[tmp.size() - 1])) {
				ShapeName = tmp[tmp.size() - 2];
				primIndex = atoi(tmp[tmp.size() - 1].c_str());
			}
			else {
				ShapeName = tmp[tmp.size() - 1];
			}

			auto shap_name_it = std::find(shap_name.begin(), shap_name.end(), ShapeName);
			unsigned int index = std::distance(shap_name.begin(), shap_name_it);
			Float trianglesArea = primIndex >= 0 ? bioemitters[index]->get_trianglesArea()[primIndex] : bioemitters[index]->get_trianglesArea()[0];
			Float Q = scale * Energy2Quantum(m_PAR_Chl.at(compName)) / trianglesArea;

			// 创建一个Bioemitter实例副本，确保每个线程有自己的实例
			auto bioemitter_copy = bioemitters[index];
			bioemitter_copy->set_m_Q(Q);
			// 计算光合作用结果
			Float A, eta;
			bioemitter_copy->compute_photosynthesis(hasFluor, AtsPressure, AtsCO2, AtsO2, Q, ShadePhotonNum, SunPhotonNum, A, eta);

			// 保护共享资源的更新
			#pragma omp critical
			{
				photoNum_comp[compName] = totalPhotonNum;
				trianglesArea_comp[compName] = trianglesArea;
				Q_comp[compName] = Q;
				A_comp[compName] = A;
				eta_comp[compName] = eta;
			}
		}
		std::vector<Float> A_Layers, Q_Layers, eta_Layers;
		A_Layers.resize(m_mumberOfLayers);
		Q_Layers.resize(m_mumberOfLayers);
		eta_Layers.resize(m_mumberOfLayers);
		for (int i = 0; i < m_mumberOfLayers; i++) {
			for (int j = 0; j < m_components_layers[i].size(); j++) {
				string compName = m_components_layers[i][j];
				Float photoRatioLayer = 1.0 * m_count_photons.at(compName)[i] / photoNum_comp[compName];
				A_Layers[i] += A_comp[compName] * trianglesArea_comp[compName] * photoRatioLayer;
				Q_Layers[i] += Q_comp[compName] * trianglesArea_comp[compName] * photoRatioLayer;
				eta_Layers[i] += eta_comp[compName] * trianglesArea_comp[compName] * photoRatioLayer;
			}
			A_Layers[i] /= sceneBoundArea;
			Q_Layers[i] /= sceneBoundArea;
			eta_Layers[i] /= sceneBoundArea;
		}
		if (m_destnationFile != "") {
			ofstream out_A_(m_destnationFile + "_A_layer.txt");
			ofstream out_par_chl_(m_destnationFile + "_APAR_Chl_layer.txt");
			ofstream out_A(m_destnationFile + "_A.txt");
			ofstream out_par_chl(m_destnationFile + "_APAR_Chl.txt");
			out_A_ << "**Canopy Photosynthetic Rate per Layer [umol s-1 m-2]**" << endl;
			out_A_ << "layer_bottom  layer_upper  A";
			out_A << "**A (umol s-1 m-2): Leaf Photosynthetic Rate per trimesh**" << endl;
			out_A << "layer_bottom  layer_upper  A ";
			out_par_chl_ << "**APAR_Chl (umol s-1 m-2) for each layer, including multiple scattering (i.e., energy entering each layer from both top and down layers)" << endl;
			out_par_chl_ << "layer_bottom  layer_upper  APAR_Chl ";
			out_par_chl << "**APAR_Chl (umol s-1 m-2) for each trimesh)" << endl;
			out_par_chl << "layer_bottom  layer_upper  APAR_Chl ";
			for (int i = 0; i < m_numComponents; i++) {
				string compName = m_components[i];
				std::replace(compName.begin(), compName.end(), '.', '_');
				out_A << compName << " ";
				out_par_chl << compName << " ";
			}

			out_A_ << endl;
			out_A << endl;
			out_par_chl_ << endl;
			out_par_chl << endl;
			for (int i = 0; i < m_mumberOfLayers; i++) {
				out_A_ << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
				out_A_ << std::fixed << std::setprecision(4) << setw(8) << A_Layers[i] << " ";

				out_par_chl_ << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[i] << " " << setw(8) << m_layerUpperBounds[i] << " ";
				out_par_chl_ << std::fixed << std::setprecision(4) << setw(8) << Q_Layers[i];

				out_A_ << endl;
				out_par_chl_ << endl;
			}
			out_A << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[0] << " " << setw(8) << m_layerUpperBounds[m_layerUpperBounds.size() - 1] << " ";
			out_A << std::fixed << std::setprecision(4) << setw(8) << std::accumulate(A_Layers.begin(), A_Layers.end(), 0) << " ";

			out_par_chl << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[0] << " " << setw(8) << m_layerUpperBounds[m_layerUpperBounds.size() - 1] << " ";
			out_par_chl << std::fixed << std::setprecision(4) << setw(8) << std::accumulate(Q_Layers.begin(), Q_Layers.end(), 0) << " ";

			for (int j = 0; j < m_numComponents; j++) {
				string compName = m_components[j];
				out_A << std::fixed << std::setprecision(4) << setw(8) << A_comp.at(compName) << " ";
				out_par_chl << std::fixed << std::setprecision(4) << setw(8) << Q_comp.at(compName) << " ";
			}

			if (hasFluor) {
				ofstream out_eta(m_destnationFile + "_eta.txt");
				out_eta << "**eta : eta per trimesh**" << endl;
				out_eta << "layer_bottom  layer_upper  eta ";
				for (int i = 0; i < m_numComponents; i++) {
					string compName = m_components[i];
					std::replace(compName.begin(), compName.end(), '.', '_');
					out_eta << compName << " ";
				}
				out_eta << endl;
				out_eta << std::fixed << std::setprecision(4) << setw(8) << m_layerLowerBounds[0] << " " << setw(8) << m_layerUpperBounds[m_layerUpperBounds.size() - 1] << " ";
				out_eta << std::fixed << std::setprecision(4) << setw(8) << std::accumulate(eta_Layers.begin(), eta_Layers.end(), 0) << " ";
				for (int j = 0; j < m_numComponents; j++) {
					string compName = m_components[j];
					out_eta << std::fixed << std::setprecision(4) << setw(8) << eta_comp.at(compName) << " ";
				}
			}
		}
	}

	void clear() {

		m_numComponents = 0;
		m_components.clear();

		m_count_sun.clear();
		m_count_shade.clear();

		m_PAR_Chl.clear();
		m_count_photons.clear();
		m_components_layers.clear();
	}

	//merge another directionalBRF in current one
	void merge(const photonsynthesisProduct* PSs) {
		for (int i = 0; i < PSs->m_numComponents; i++) {
			string compName = PSs->m_components[i];
			auto compName_it = std::find(m_components.begin(), m_components.end(), compName);
			bool is_new_comp = compName_it == m_components.end();
			if (is_new_comp) {//未出现
				m_count_sun[compName] = PSs->m_count_sun.at(compName);
				m_count_shade[compName] = PSs->m_count_shade.at(compName);
				m_PAR_Chl[compName] = PSs->m_PAR_Chl.at(compName);
				m_count_photons[compName].resize(m_mumberOfLayers);
				for (int j = 0; j < m_mumberOfLayers; j++) {
					m_count_photons[compName][j] = PSs->m_count_photons.at(compName)[j];
				}
				m_numComponents++;
				m_components.push_back(compName);
			}
			else {
				m_count_sun.at(compName) += PSs->m_count_sun.at(compName);
				m_count_shade.at(compName) += PSs->m_count_shade.at(compName);
				m_PAR_Chl.at(compName) += PSs->m_PAR_Chl.at(compName);
				for (int j = 0; j < m_mumberOfLayers; j++) {
					m_count_photons[compName][j] += PSs->m_count_photons.at(compName)[j];
				}
			}
		}
		for (int i = 0; i < m_mumberOfLayers; i++) {
			vector<string> compName = PSs->m_components_layers[i];
			// 使用 set_union 合并并去除重复元素
			vector<string> merged;
			merged.reserve(m_components_layers[i].size() + compName.size());
			std::set_union(m_components_layers[i].begin(), m_components_layers[i].end(), compName.begin(), compName.end(), std::back_inserter(merged));
			m_components_layers[i] = merged;
		}
	}

	void put(int depth, const Intersection& its, Point& previousPoint, Spectrum fPAR_Chl, bool isShaded) {
		Point p = its.p;
		string compName = its.shape->getName();
		if (compName != "terrain") {
			if (m_outputMode == 1) {
				if (its.instance) {
					compName = its.instance->getName() + "." + compName;
				}
			}
			else if (m_outputMode == 2) {
				if (its.instance) {
					string instance_name = its.instance->getName();
					if (m_considerTriangleInstances.size() == 0) {
						compName = its.instance->getName() + "." + compName + "." + to_string(its.primIndex);
					}
					else {
						if (std::find(m_considerTriangleInstances.begin(), m_considerTriangleInstances.end(), instance_name) != m_considerTriangleInstances.end()) {
							compName = its.instance->getName() + "." + compName + "." + to_string(its.primIndex);
						}
						else {
							compName = its.instance->getName() + "." + compName;
						}
					}
				}
			}
			double step = m_layerUpperBounds[0] - m_layerLowerBounds[0];
			int index = (int)((p.y - m_layerLowerBounds[0]) / step);

			if (index >= 0 && index <= m_mumberOfLayers - 1) {
				auto compName_it = std::find(m_components.begin(), m_components.end(), compName);
				bool is_new_comp = compName_it == m_components.end();
				//std::string compName_ = *compName_it;
				if (is_new_comp) {
					m_count_shade[compName] = 0;
					m_count_sun[compName] = 0;
					m_PAR_Chl[compName] = Spectrum(0.0);
					m_count_photons[compName].resize(m_mumberOfLayers);
					for (int i = 0; i < m_mumberOfLayers; i++) {
						m_count_photons[compName][i] = 0;
					}
					m_numComponents++;
					m_components.push_back(compName);
				}
				if (isShaded) {
					m_count_shade.at(compName) += 1;
				}
				else {
					m_count_sun.at(compName) += 1;
				}
				m_count_photons[compName][index] += 1;
				m_components_layers[index].push_back(compName);
			}
		}
	}

	//its is the intersection with the surface containing the medium, it is th exiting point
	void put(int depth, const Intersection& its, const MediumSamplingRecord& mRec, bool isShade) {
		Point p = mRec.p;
		string compName = its.shape->getName();
		if (m_outputMode == 1 || m_outputMode == 2) {
			if (its.instance) {
				compName = its.instance->getName() + "." + compName;
			}
		}
		double step = m_layerUpperBounds[0] - m_layerLowerBounds[0];
		int index = (int)((p.y - m_layerLowerBounds[0]) / step);
		if (index >= 0 && index <= m_mumberOfLayers - 1) {
			bool is_new_comp = false;
			if (isShade) {
				if (m_count_shade.count(compName) == 0) {
					is_new_comp = true;
					m_count_shade[compName] = 0;
				}
				m_count_shade.at(compName) += 1;
			}
			else {
				if (index >= 0 && index <= m_mumberOfLayers - 1) {
					if (m_count_sun.count(compName) == 0) {
						is_new_comp = true;
						m_count_sun[compName] = 0;
					}
					m_count_sun.at(compName) += 1;
				}
			}
			if (is_new_comp) {
				m_numComponents++;
				m_components.push_back(compName);
			}
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
	}
public:

public:
	vector<string> m_considerTriangleInstances;  //When m_outputMode=2, only consider the listed object for calculate fpar of each triangle. By default, considers all object

	vector<double> m_layerLowerBounds;
	vector<double> m_layerUpperBounds;
	int m_numComponents;// Number of components
	vector<string> m_components;
	std::unordered_map<string, Spectrum > m_PAR_Chl;  // absorption of each components
	std::unordered_map<string, vector<unsigned int>> m_count_photons;  // photons of each components in a layer
	std::unordered_map<string, unsigned int> m_count_sun;  // count sun photon number on a triangle
	std::unordered_map<string, unsigned int> m_count_shade;  // count shade photon number on a triangle
	vector<vector<string> > m_components_layers;  // components in a layer
	int m_mumberOfLayers;
	int m_outputMode = 0; // 0: output each component; 1: output each instance-component; 2: output each instance-component-triangle

	//no need to serilize
	string  m_destnationFile;//The path to store the fpar products
	Vector2 m_scenBoundPlaneSize; //used to calculate totcal incident energy w/m2
	Vector2 m_virtualBoundXZSize; //only compute the energy which has been incident on the virtual plane
	Spectrum m_wavelengths;
};


MTS_NAMESPACE_END
#endif