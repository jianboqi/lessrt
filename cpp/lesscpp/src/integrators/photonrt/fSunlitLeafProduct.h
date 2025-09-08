#pragma once

//Implementing a storage class to store directional BRF/radiance
//value for different directions

#if !defined(_fSunlitLeafProduct_H_)
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

using namespace std;

MTS_NAMESPACE_BEGIN

class fSunlitLeafProduct :public Object {
public:
	fSunlitLeafProduct(string layerDefinition) {
		m_mumberOfLayers = 0;
		std::vector<std::string> tmp;
		boost::algorithm::split(tmp, layerDefinition, boost::is_any_of(":"));
		if (tmp.size() == 3) { //mode: from:step:to
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
			}
			m_mumberOfLayers = i;
		}
		m_numComponents = 0;
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
				stream->writeLong(m_totalPhotonPerLayer.at(compName)[j]);
				stream->writeLong(m_sunlitPhotonPerLayer.at(compName)[j]);
			}
				
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

		m_totalPhotonPerLayer.clear();
		m_sunlitPhotonPerLayer.clear();
		for (int i = 0; i < m_numComponents; i++) {
			string compName = m_components[i];
			m_totalPhotonPerLayer[compName] = vector<int64_t>();
			m_totalPhotonPerLayer[compName].resize(m_mumberOfLayers);
			m_sunlitPhotonPerLayer[compName] = vector<int64_t>();
			m_sunlitPhotonPerLayer[compName].resize(m_mumberOfLayers);
			for (int j = 0; j < m_mumberOfLayers; j++) {
				m_totalPhotonPerLayer[compName][j] = stream->readLong();
				m_sunlitPhotonPerLayer[compName][j] = stream->readLong();
			}
		}

	}


	void develop() {
		if (m_destnationFile != "") {
			ofstream out(m_destnationFile);
			out << "**Sunlit/Shaded Leaf Fraction**" << endl;
			out << " - All Scene Components (";
			for (int i = 0; i < m_numComponents-1; i++) {
				out << m_components[i] << " + ";
			}
			out << m_components[m_numComponents-1] <<")" <<endl;

			out << std::fixed << setw(12) << "layer_bottom" << " " << setw(12) << "layer_upper" << " " << setw(12) << "fSunlitLeaf" << " " << setw(12) << "fShadedLeaf" << endl;
			int64_t totAll = 0, sunlitAll = 0;
			for (int i = 0; i < m_mumberOfLayers; i++) {
				out << std::fixed << std::setprecision(4) << setw(12) << m_layerLowerBounds[i] << " " << setw(12) << m_layerUpperBounds[i] << " ";
				int64_t tot=0, sunlit=0;
				for (int j = 0; j < m_numComponents; j++) {
					tot += m_totalPhotonPerLayer.at(m_components[j])[i];
					sunlit += m_sunlitPhotonPerLayer.at(m_components[j])[i];
				}
				if (tot == 0) {
					out << std::fixed << setw(12) << 0 <<" "<< std::fixed << setw(12) << 0 << endl;
				}
				else {
					double sunlitf = sunlit / ((double)tot);
					out << std::fixed << std::setprecision(4) << setw(12) << sunlitf << " " << std::fixed << std::setprecision(4) << setw(12) << 1 - sunlitf<<endl;
				}
				totAll += tot;
				sunlitAll += sunlit;
			}
			out << "------------ ------------ ------------ ------------"<<endl;
			out << std::fixed << setw(12) << "Total"<<"              ";
			if (totAll == 0) {
				out << std::fixed << setw(12) << 0 << " " << std::fixed << setw(12) << 0 << endl;
			}
			else {
				double sunlitf = sunlitAll / ((double)totAll);
				out << std::fixed << std::setprecision(4) << setw(12) << sunlitf << " " << std::fixed << std::setprecision(4) << setw(12) << 1 - sunlitf << endl;
			}

			if (m_numComponents == 1) return;

			out << endl << endl;
			for (int i = 0; i < m_numComponents; i++) {
				out << " - Sunlit/Shaded Leaf Fraction of ";
				string compName = m_components[i];
				out << compName << endl;
			//	out << "layer_bottom  layer_upper  fSunlitLeaf fShadedLeaf" << endl;
				out << std::fixed << setw(12) << "layer_bottom" << " " << setw(12) << "layer_upper" << " " << setw(12) << "fSunlitLeaf" << " " << setw(12) << "fShadedLeaf" << endl;
				totAll = 0;
				sunlitAll = 0;
				for (int j = 0; j < m_mumberOfLayers; j++) {
					out << std::fixed << std::setprecision(4) << setw(12)<<m_layerLowerBounds[j] << " " << setw(12) << m_layerUpperBounds[j]<<" ";
					int64_t tot = m_totalPhotonPerLayer.at(compName)[j];
					int64_t	sunlit = m_sunlitPhotonPerLayer.at(compName)[j];
					if (tot == 0) {
						out << std::fixed << setw(12) << 0 <<" "<< std::fixed << setw(12)<< 0 <<endl;
					}
					else {
						double sunlitf = sunlit / ((double)tot);
						out << std::fixed << std::setprecision(4) << setw(12) << sunlitf << " " << std::fixed << std::setprecision(4) << setw(12) << 1 - sunlitf << endl;
					}
					totAll += tot;
					sunlitAll += sunlit;
				}
				out << "------------ ------------ ------------ ------------" << endl;
				out << std::fixed << setw(12) << "Total" << "              ";
				if (totAll == 0) {
					out << std::fixed << setw(12) << 0 << " " << std::fixed << setw(12) << 0 << endl;
				}
				else {
					double sunlitf = sunlitAll / ((double)totAll);
					out << std::fixed << std::setprecision(4) << setw(12) << sunlitf << " " << std::fixed << std::setprecision(4) << setw(12) << 1 - sunlitf << endl;
				}
				out << endl;
			}

			
			out.close();

		}
	}

	void clear() {
		m_numComponents = 0;
		m_components.clear();
		m_totalPhotonPerLayer.clear();
		m_sunlitPhotonPerLayer.clear();
	}

	//merge another product in current one
	void merge(const fSunlitLeafProduct* fSLProduct) {
		for (int i = 0; i < fSLProduct->m_numComponents; i++) {
			string compName = fSLProduct->m_components[i];
			//m_sunlitPhotonPerLayer and m_totalPhotonPerLayer will have the same behavior
			if (m_totalPhotonPerLayer.count(compName) == 0 && m_sunlitPhotonPerLayer.count(compName)==0) {
				m_totalPhotonPerLayer[compName] = fSLProduct->m_totalPhotonPerLayer.at(compName);
				m_sunlitPhotonPerLayer[compName] = fSLProduct->m_sunlitPhotonPerLayer.at(compName);
				m_numComponents++;
				m_components.push_back(compName);
			}
			else {
				for (int j = 0; j < m_mumberOfLayers; j++) {
					m_totalPhotonPerLayer.at(compName)[j] += fSLProduct->m_totalPhotonPerLayer.at(compName)[j];
					m_sunlitPhotonPerLayer.at(compName)[j] += fSLProduct->m_sunlitPhotonPerLayer.at(compName)[j];
				}
					
			}
		}
	}


	void put(Point &p,string compName, bool isShadedPhoton) {
		double step = m_layerUpperBounds[0] - m_layerLowerBounds[0];
		int index = (int)((p.y - m_layerLowerBounds[0]) / step);
		if (index >= 0 && index <= m_mumberOfLayers - 1) {
			if (m_totalPhotonPerLayer.count(compName) == 0) {
				m_numComponents++;
				m_components.push_back(compName);
				m_totalPhotonPerLayer[compName].resize(m_mumberOfLayers);
				m_sunlitPhotonPerLayer[compName].resize(m_mumberOfLayers);
				for (int j = 0; j < m_mumberOfLayers; j++) {
					m_totalPhotonPerLayer.at(compName)[j] = 0;
					m_sunlitPhotonPerLayer.at(compName)[j] = 0;
				}
					
			}
			m_totalPhotonPerLayer.at(compName)[index] ++;
			if(!isShadedPhoton)
				m_sunlitPhotonPerLayer.at(compName)[index] ++;
		}
	}

	//The Destination File
	void setDestinationFile(string destinationFile) {
		m_destnationFile = destinationFile;
	}

public:
	vector<double> m_layerLowerBounds;
	vector<double> m_layerUpperBounds;
	int m_mumberOfLayers;

	int m_numComponents;// Number of components
	vector<string> m_components;
	map<string, vector<int64_t>> m_totalPhotonPerLayer;
	map<string, vector<int64_t>> m_sunlitPhotonPerLayer; //vector<size_t> means each layer
	
	//no need to serilize
	string  m_destnationFile;//The path to store the sunlit leaf fraction products
};


MTS_NAMESPACE_END
#endif