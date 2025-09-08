#pragma once

//Implementing a storage class to store directional Fluor/radiance
//value for different directions

#if !defined(_FLUX_MEASURE_PRODUCT_)
#define _FLUX_MEASURE_PRODUCT_

#include <iostream>
#include <vector>
#include <fstream>
#include <mitsuba/core/spectrum.h>
#include <mitsuba/mitsuba.h>
#include <boost/algorithm/string.hpp>
#include <iomanip>      // std::setprecision
#include <unordered_map>

using namespace std;

MTS_NAMESPACE_BEGIN

class FluxMeasureProduct : public Object {
public:
	FluxMeasureProduct(string measureMode) {
		m_outputMode = atoi(measureMode.c_str());
	}

	void serialize(Stream* stream) const {
		stream->writeInt(m_outputMode);
		stream->writeInt(m_frontIncident.size());
		stream->writeInt(m_backIncident.size());
		for (auto kv : m_frontIncident) {
			stream->writeString(kv.first);
			(kv.second).serialize(stream);
		}
		for (auto kv : m_backIncident) {
			stream->writeString(kv.first);
			(kv.second).serialize(stream);
		}

		if (WANTED_INDEX[0] != -1) {
			stream->writeInt(m_frontIncident_PSI.size());
			stream->writeInt(m_backIncident_PSI.size());
			for (auto kv : m_frontIncident_PSI) {
				stream->writeString(kv.first);
				(kv.second).serialize(stream);
			}
			for (auto kv : m_backIncident_PSI) {
				stream->writeString(kv.first);
				(kv.second).serialize(stream);
			}
			if (!IS_FLUSPECT_PRO) {
				stream->writeInt(m_frontIncident_PSII.size());
				stream->writeInt(m_backIncident_PSII.size());
				for (auto kv : m_frontIncident_PSII) {
					stream->writeString(kv.first);
					(kv.second).serialize(stream);
				}
				for (auto kv : m_backIncident_PSII) {
					stream->writeString(kv.first);
					(kv.second).serialize(stream);
				}
			}
		}
	}

	void unserialize(Stream* stream) {
		m_outputMode = stream->readInt();
		int m_numFront = stream->readInt();
		int m_numBack = stream->readInt();

		m_frontIncident.clear();
		m_backIncident.clear();
		for (int i = 0; i < m_numFront; i++) {
			string compName = stream->readString();
			m_frontIncident[compName] = Spectrum(stream);
		}
		for (int i = 0; i < m_numBack; i++) {
			string compName = stream->readString();
			m_backIncident[compName] = Spectrum(stream);
		}

		if (WANTED_INDEX[0] != -1) {
			m_frontIncident_PSI.clear();
			m_backIncident_PSI.clear();
			m_frontIncident_PSII.clear();
			m_backIncident_PSII.clear();

			if (!IS_FLUSPECT_PRO) {
				for (int i = 0; i < m_numFront; i++) {
					m_frontIncident_PSI[stream->readString()] = Spectrum(stream);
					m_frontIncident_PSII[stream->readString()] = Spectrum(stream);
				}
				for (int i = 0; i < m_numBack; i++) {
					m_backIncident_PSI[stream->readString()] = Spectrum(stream);
					m_backIncident_PSII[stream->readString()] = Spectrum(stream);
				}
			}
			else {
				for (int i = 0; i < m_numFront; i++) {
					m_frontIncident_PSI[stream->readString()] = Spectrum(stream);
				}
				for (int i = 0; i < m_numBack; i++) {
					m_backIncident_PSI[stream->readString()] = Spectrum(stream);
				}
			}
		}
	}

	double broadbandEnergy(Spectrum energy) {
		if (SPECTRUM_SAMPLES == 1)
			return energy[0];

		double total = 0.0;
		for (int j = 0; j < SPECTRUM_SAMPLES - 1; j++) {
			total += (energy[j] + energy[j + 1]) * (m_wavelengths[j + 1] - m_wavelengths[j]) * 0.5;
		}
		return total;
	}

	void clear() {
		m_frontIncident.clear();
		m_backIncident.clear();
		if (WANTED_INDEX[0] != -1) {
			m_frontIncident_PSI.clear();
			m_backIncident_PSI.clear();
			if (!IS_FLUSPECT_PRO) {
				m_frontIncident_PSII.clear();
				m_backIncident_PSII.clear();
			}
		}
	}

	void merge(const FluxMeasureProduct* fluxProduct) {
		for (auto kv : fluxProduct->m_frontIncident) {
			string compName = kv.first;
			if (m_frontIncident.count(compName) == 0) {
				m_frontIncident[compName] = kv.second;
			}
			else {
				m_frontIncident[compName] += kv.second;
			}
		}

		for (auto kv : fluxProduct->m_backIncident) {
			string compName = kv.first;
			if (m_backIncident.count(compName) == 0) {
				m_backIncident[compName] = kv.second;
			}
			else {
				m_backIncident[compName] += kv.second;
			}
		}
		if (WANTED_INDEX[0] != -1) {
			for (auto kv : fluxProduct->m_frontIncident_PSI) {
				string compName = kv.first;
				if (m_frontIncident_PSI.count(compName) == 0) {
					m_frontIncident_PSI[compName] = kv.second;
				}
				else {
					m_frontIncident_PSI[compName] += kv.second;
				}
			}

			for (auto kv : fluxProduct->m_backIncident_PSI) {
				string compName = kv.first;
				if (m_backIncident_PSI.count(compName) == 0) {
					m_backIncident_PSI[compName] = kv.second;
				}
				else {
					m_backIncident_PSI[compName] += kv.second;
				}
			}
			if (!IS_FLUSPECT_PRO) {
				for (auto kv : fluxProduct->m_frontIncident_PSII) {
					string compName = kv.first;
					if (m_frontIncident_PSII.count(compName) == 0) {
						m_frontIncident_PSII[compName] = kv.second;
					}
					else {
						m_frontIncident_PSII[compName] += kv.second;
					}
				}

				for (auto kv : fluxProduct->m_backIncident_PSII) {
					string compName = kv.first;
					if (m_backIncident_PSII.count(compName) == 0) {
						m_backIncident_PSII[compName] = kv.second;
					}
					else {
						m_backIncident_PSII[compName] += kv.second;
					}
				}
			}
		}
	}

	void put_flux(int depth, const Intersection& its, Spectrum IncidentEnergy, bool front) {
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
				compName = its.instance->getName() + "_" + compName + "_" + to_string(its.primIndex);
			}
		}

		if (front) {
			if (m_frontIncident.count(compName) == 0) {
				m_frontIncident[compName] = Spectrum(0.0);
				m_backIncident[compName] = Spectrum(0.0);
			}
			m_frontIncident[compName] += IncidentEnergy;
		}
		else {
			if (m_backIncident.count(compName) == 0) {
				m_frontIncident[compName] = Spectrum(0.0);
				m_backIncident[compName] = Spectrum(0.0);
			}
			m_backIncident[compName] += IncidentEnergy;
		}
	}

	void put_flux_fluor(int depth, const Intersection& its, Spectrum IncidentFluorPSIEnergy, Spectrum IncidentFluorPSIIEnergy, bool front) {
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
				compName = its.instance->getName() + "_" + compName + "_" + to_string(its.primIndex);
			}
		}

		if (front) {
			if (m_frontIncident_PSI.count(compName) == 0) {
				m_frontIncident_PSI[compName] = Spectrum(0.0);
				m_backIncident_PSI[compName] = Spectrum(0.0);
				m_frontIncident_PSII[compName] = Spectrum(0.0);
				m_backIncident_PSII[compName] = Spectrum(0.0);
			}
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(m_frontIncident_PSI[compName], m_frontIncident_PSII[compName], IncidentFluorPSIEnergy, IncidentFluorPSIIEnergy);
		}
		else {
			if (m_backIncident_PSI.count(compName) == 0) {
				m_frontIncident_PSI[compName] = Spectrum(0.0);
				m_backIncident_PSI[compName] = Spectrum(0.0);
				m_frontIncident_PSII[compName] = Spectrum(0.0);
				m_backIncident_PSII[compName] = Spectrum(0.0);
			}
			m_FluorSpectrum_fun.compute_FluorSpectrum_PlusEqual(m_backIncident_PSI[compName], m_backIncident_PSII[compName], IncidentFluorPSIEnergy, IncidentFluorPSIIEnergy);
		}
	}
	void setDestinationFile(string destinationFile) {
		m_destnationFile = destinationFile;
	}

	void setWavelengths(Spectrum spectrum) {
		this->m_wavelengths = spectrum;
	}

	void develop(double scale = 1.0) {
		if (m_destnationFile == "") return;
		ofstream out(m_destnationFile);
		out << "**Flux entering and leaving a surface (W)**" << endl;
		out << "*Simualted with mode=" <<m_outputMode<<"*" <<endl;
		out << "Total Flux integrated over wavelengths"<<endl;
		out << "-------------------------------------------------"<<endl;
		int text_width = 15;
		out << setw(text_width) << "FluxType"<<" ";
		for (auto kv : m_frontIncident) {
			string compName = kv.first;
			out << setw(text_width) << compName << " ";
		}
		out << endl;
		out << setw(text_width) << "Entering" << " ";
		for (auto kv : m_frontIncident) {
			out << std::fixed << std::setprecision(4) << setw(text_width) << broadbandEnergy(scale * m_frontIncident[kv.first]) << " ";
		}
		out << endl;
		out << setw(text_width) << "Leaving" << " ";
		for (auto kv : m_frontIncident) {
			out << std::fixed << std::setprecision(4) << setw(text_width) << broadbandEnergy(scale * m_backIncident[kv.first]) << " ";
		}
		out << endl << endl;
		out << "**Flux for each band (W)**" << endl;
		out << "-------------------------------------------------"<<endl;

		for (auto kv : m_frontIncident) {
			string compName = kv.first;
			out << " - Flux for " << compName<< endl;
			out << setw(text_width) << "FluxType" << " ";
			for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
				out << std::fixed << std::setprecision(4) << setw(text_width) << m_wavelengths[i]<< " ";
			}
			out << endl;
			out << setw(text_width) << "Entering" << " ";
			for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
				out << std::fixed << std::setprecision(4) << setw(text_width) << scale * m_frontIncident[compName][i] << " ";
			}

			out << endl;
			out << setw(text_width) << "Leaving" << " ";
			for (int i = 0; i < SPECTRUM_SAMPLES; i++) {
				out << std::fixed << std::setprecision(4) << setw(text_width) << scale * m_backIncident[compName][i] << " ";
			}
			out << endl;
		}
	}

	void develop4Fluor(double scale = 1.0) {
		if (m_destnationFile == "") return;
		size_t WANTED_INDEX_LEN = WANTED_INDEX.size();
		if (IS_FLUSPECT_PRO) {
			ofstream out(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_Fluor.txt");
			out << "**Fluor Flux entering and leaving a surface (mW)**" << endl;
			out << "*Simualted with mode=" << m_outputMode << "*" << endl;
			out << "Total Fluor Flux integrated over wavelengths" << endl;
			out << "-------------------------------------------------" << endl;
			int text_width = 15;
			out << setw(text_width) << "FluxType" << " ";
			for (auto kv : m_frontIncident_PSI) {
				string compName = kv.first;
				out << setw(text_width) << compName << " ";
			}
			out << endl;
			out << setw(text_width) << "Entering" << " ";
			for (auto kv : m_frontIncident_PSI) {
				out << std::fixed << std::setprecision(4) << setw(text_width) << broadbandEnergy(scale * m_frontIncident_PSI[kv.first]) << " ";
			}
			out << endl;
			out << setw(text_width) << "Leaving" << " ";
			for (auto kv : m_frontIncident_PSI) {
				out << std::fixed << std::setprecision(4) << setw(text_width) << broadbandEnergy(scale * m_backIncident_PSI[kv.first]) << " ";
			}
			out << endl << endl;
			out << "**Fluor Flux for each band (mW)**" << endl;
			out << "-------------------------------------------------" << endl;

			for (auto kv : m_frontIncident_PSI) {
				string compName = kv.first;
				out << " - Fluor Flux for " << compName << endl;
				out << setw(text_width) << "FluxType" << " ";
				for (int i = 0; i < WANTED_INDEX_LEN; i++) {
					out << std::fixed << std::setprecision(4) << setw(text_width) << m_wavelengths[WANTED_INDEX[i]] << " ";
				}
				out << endl;
				out << setw(text_width) << "Entering" << " ";
				for (int i = 0; i < WANTED_INDEX_LEN; i++) {
					out << std::fixed << std::setprecision(4) << setw(text_width) << scale * m_frontIncident_PSI[compName][WANTED_INDEX[i]] << " ";
				}

				out << endl;
				out << setw(text_width) << "Leaving" << " ";
				for (int i = 0; i < WANTED_INDEX_LEN; i++) {
					out << std::fixed << std::setprecision(4) << setw(text_width) << scale * m_backIncident_PSI[compName][WANTED_INDEX[i]] << " ";
				}
				out << endl;
			}
		}
		else {
			ofstream out_PSI(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_PSI_Fluor.txt");
			ofstream out_PSII(m_destnationFile.substr(0, m_destnationFile.length() - 4) + "_PSII_Fluor.txt");
			out_PSI << "**PSI Fluor Flux entering and leaving a surface (mW)**" << endl;
			out_PSII << "**PSII Fluor Flux entering and leaving a surface (mW)**" << endl;
			out_PSI << "*Simualted with mode=" << m_outputMode << "*" << endl;
			out_PSII << "*Simualted with mode=" << m_outputMode << "*" << endl;
			out_PSI << "Total PSI Fluor Flux integrated over wavelengths" << endl;
			out_PSII << "Total PSII Fluor Flux integrated over wavelengths" << endl;
			out_PSI << "-------------------------------------------------" << endl;
			out_PSII << "-------------------------------------------------" << endl;
			int text_width = 15;
			out_PSI << setw(text_width) << "FluxType" << " ";
			out_PSII << setw(text_width) << "FluxType" << " ";
			for (auto kv : m_frontIncident_PSI) {
				string compName = kv.first;
				out_PSI << setw(text_width) << compName << " ";
				out_PSII << setw(text_width) << compName << " ";
			}
			out_PSI << endl;
			out_PSII << endl;
			out_PSI << setw(text_width) << "Entering" << " ";
			out_PSII << setw(text_width) << "Entering" << " ";
			for (auto kv : m_frontIncident_PSI) {
				out_PSI << std::fixed << std::setprecision(4) << setw(text_width) << broadbandEnergy(scale * m_frontIncident_PSI[kv.first]) << " ";
				out_PSII << std::fixed << std::setprecision(4) << setw(text_width) << broadbandEnergy(scale * m_frontIncident_PSII[kv.first]) << " ";
			}
			out_PSI << endl;
			out_PSII << endl;
			out_PSI << setw(text_width) << "Leaving" << " ";
			out_PSII << setw(text_width) << "Leaving" << " ";
			for (auto kv : m_frontIncident_PSI) {
				out_PSI << std::fixed << std::setprecision(4) << setw(text_width) << broadbandEnergy(scale * m_backIncident_PSI[kv.first]) << " ";
				out_PSII << std::fixed << std::setprecision(4) << setw(text_width) << broadbandEnergy(scale * m_backIncident_PSII[kv.first]) << " ";
			}
			out_PSI << endl << endl;
			out_PSII << endl << endl;
			out_PSI << "**PSI Fluor Flux for each band (mW)**" << endl;
			out_PSII << "**PSII Fluor Flux for each band (mW)**" << endl;
			out_PSI << "-------------------------------------------------" << endl;
			out_PSII << "-------------------------------------------------" << endl;

			for (auto kv : m_frontIncident_PSI) {
				string compName = kv.first;
				out_PSI << " - PSI Fluor Flux for " << compName << endl;
				out_PSII << " - PSII Fluor Flux for " << compName << endl;
				out_PSI << setw(text_width) << "FluxType" << " ";
				out_PSII << setw(text_width) << "FluxType" << " ";
				for (int i = 0; i < WANTED_INDEX_LEN; i++) {
					out_PSI << std::fixed << std::setprecision(4) << setw(text_width) << m_wavelengths[WANTED_INDEX[i]] << " ";
					out_PSII << std::fixed << std::setprecision(4) << setw(text_width) << m_wavelengths[WANTED_INDEX[i]] << " ";
				}
				out_PSI << endl;
				out_PSII << endl;
				out_PSI << setw(text_width) << "Entering" << " ";
				out_PSII << setw(text_width) << "Entering" << " ";
				for (int i = 0; i < WANTED_INDEX_LEN; i++) {
					out_PSI << std::fixed << std::setprecision(4) << setw(text_width) << scale * m_frontIncident_PSI[compName][WANTED_INDEX[i]] << " ";
					out_PSII << std::fixed << std::setprecision(4) << setw(text_width) << scale * m_frontIncident_PSII[compName][WANTED_INDEX[i]] << " ";
				}

				out_PSI << endl;
				out_PSII << endl;
				out_PSI << setw(text_width) << "Leaving" << " ";
				out_PSII << setw(text_width) << "Leaving" << " ";
				for (int i = 0; i < WANTED_INDEX_LEN; i++) {
					out_PSI << std::fixed << std::setprecision(4) << setw(text_width) << scale * m_backIncident_PSI[compName][WANTED_INDEX[i]] << " ";
					out_PSII << std::fixed << std::setprecision(4) << setw(text_width) << scale * m_backIncident_PSII[compName][WANTED_INDEX[i]] << " ";
				}
				out_PSI << endl;
				out_PSII << endl;
			}
		}
	}

private:
	int m_outputMode = 1; // 0: each component; 1: output each instance-component; 2: output each instance-component-triangle
	Spectrum m_wavelengths;
public:
	std::unordered_map<string, Spectrum> m_frontIncident; // front incident
	std::unordered_map<string, Spectrum> m_backIncident; // back incident
	string m_destnationFile;

	std::unordered_map<string, Spectrum> m_frontIncident_PSI; // front incident PSI Fluor
	std::unordered_map<string, Spectrum> m_frontIncident_PSII; // front incident PSII Fluor
	std::unordered_map<string, Spectrum> m_backIncident_PSI; // back incident PSI Fluor
	std::unordered_map<string, Spectrum> m_backIncident_PSII; // back incident PSII Fluor
	//only FluorSpectrum function use
	FluorMatrix m_FluorSpectrum_fun;
};


MTS_NAMESPACE_END
#endif