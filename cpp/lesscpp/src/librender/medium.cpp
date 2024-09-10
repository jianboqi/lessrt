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

#include <mitsuba/core/plugin.h>
#include <mitsuba/core/properties.h>
#include <mitsuba/render/medium.h>
#include <mitsuba/render/phase.h>
#include "../medium/materials.h"

MTS_NAMESPACE_BEGIN

Medium::Medium(const Properties& props)
	: NetworkedObject(props) {
	Spectrum g;
	lookupMaterial(props, m_sigmaS, m_sigmaA, g);

	/* For now, ignore the anisotropy information of preset materials
	   and use the reduced scattering coefficient */
	m_sigmaS *= Spectrum(1.0f) - g;

	m_sigmaT = m_sigmaA + m_sigmaS;
}

Medium::Medium(Stream* stream, InstanceManager* manager)
	: NetworkedObject(stream, manager) {
	m_phaseFunction = static_cast<PhaseFunction*>(manager->getInstance(stream));
	m_sigmaA = Spectrum(stream);
	m_sigmaS = Spectrum(stream);
	m_sigmaT = m_sigmaA + m_sigmaS;
}

void Medium::addChild(const std::string& name, ConfigurableObject* child) {
	const Class* cClass = child->getClass();

	if (cClass->derivesFrom(MTS_CLASS(PhaseFunction))) {
		Assert(m_phaseFunction == NULL);
		m_phaseFunction = static_cast<PhaseFunction*>(child);
	}
	else {
		Log(EError, "Medium: Invalid child node! (\"%s\")",
			cClass->getName().c_str());
	}
}

void Medium::configure() {
	if (m_phaseFunction == NULL) {
		m_phaseFunction = static_cast<PhaseFunction*> (PluginManager::getInstance()->
			createObject(MTS_CLASS(PhaseFunction), Properties("isotropic")));
		m_phaseFunction->configure();
	}
}

Spectrum Medium::evalTransmittanceWithHotspot(const Ray& solarRay, const Ray& sensorRay, const Point& p1, bool isOnSurface, Float& maxEvalRange, Sampler* sampler) const {
	NotImplementedError("evalTransmittanceWithHotspot");
}

Spectrum Medium::evalTransmittanceWithHotspotWithSigmaT(const Ray& solarRay, const Ray& sensorRay, const Point& p1, bool& isOnSurface,
	Float& maxEvalRange, Float sigmaT, Float Gsensor, Float Gsoloar, Sampler* sampler) const {
	NotImplementedError("evalTransmittanceWithHotspotWithSigmaT");
}

bool Medium::sampleDistanceWithHotspot(const Ray& ray,
	MediumSamplingRecord& mRec, Sampler* sampler, int depth,
	Point& previousRayPos, Vector& previousRayDir) const {
	NotImplementedError("sampleDistanceWithHotspot");
}

bool Medium::sampleDistanceWithTau(const Ray& ray,
	MediumSamplingRecord& mRec, Float& sampledTau, Sampler* sampler) const {
	NotImplementedError("sampleDistanceWithTau");
}

bool Medium::sampleDistanceWithTotalTauSigmaTandAlbedo(const Ray& ray,
	MediumSamplingRecord& mRec, Sampler* sampler, Float& sampledTau, bool& needReSampleTau, Float sigmaT, Spectrum singleAlbedo) const {
	NotImplementedError("sampleDistanceWithTotalTauSigmaTandAlbedo");
}

bool Medium::sampleDistanceWithTotalTauSigmaTandAlbedo(const Ray& ray,
	MediumSamplingRecord& mRec, Sampler* sampler, Float& sampledTau, bool& needReSampleTau, Float sigmaT, Spectrum singleAlbedo,
	FluorMatrix PSsingleAlbedo) const {
	NotImplementedError("sampleDistanceWithTotalTauSigmaTandAlbedo");
}


bool Medium::sampleDistanceWithSigmaTandAlbedo(const Ray& ray,
	MediumSamplingRecord& mRec, Sampler* sampler, Float sigmaT, Spectrum singleAlbedo) const {
	NotImplementedError("sampleDistanceWithSigmaTandAlbedo");
}

bool Medium::sampleDistanceWithRandomOpticalDepth(const Scene* scene, Ray& ray,
	MediumSamplingRecord& mRec, Sampler* sampler) const {
	NotImplementedError("sampleDistanceWithRandomOpticalDepth");
}

Float Medium::getVegetationSigmaT(const Ray& ray) const {
	NotImplementedError("getVegetationSigmaT");
}

Float Medium::getVegetationG(const Ray& ray) const {
	NotImplementedError("getVegetationG");
}

Spectrum Medium::getVegetationSingleAlbedo(const Ray& ray) const {
	NotImplementedError("getVegetationSingleAlbedo");
}

FluorMatrix Medium::getFluorVegetationSingleAlbedo(const Ray& ray) const {
	NotImplementedError("getFluorIVegetationSingleAlbedo");
}
Spectrum Medium::getkChlrel() const {
	NotImplementedError("getkChlrel");
}
void Medium::getphi(Spectrum& phiI, Spectrum& phiII) const {
	NotImplementedError("getphi");
}
void Medium::getfqe(Float& fqeI, Float& fqeII) const {
	NotImplementedError("getfqe");
}


void Medium::serialize(Stream* stream, InstanceManager* manager) const {
	NetworkedObject::serialize(stream, manager);
	manager->serialize(stream, m_phaseFunction.get());
	m_sigmaA.serialize(stream);
	m_sigmaS.serialize(stream);
}

std::string MediumSamplingRecord::toString() const {
	std::ostringstream oss;
	oss << "MediumSamplingRecord[" << endl
		<< "  t = " << t << "," << endl
		<< "  p = " << p.toString() << "," << endl
		<< "  sigmaA = " << sigmaA.toString() << "," << endl
		<< "  sigmaS = " << sigmaS.toString() << "," << endl
		<< "  pdfFailure = " << pdfFailure << "," << endl
		<< "  pdfSuccess = " << pdfSuccess << "," << endl
		<< "  pdfSuccessRev = " << pdfSuccessRev << "," << endl
		<< "  transmittance = " << transmittance.toString() << "," << endl
		<< "  medium = " << indent(medium ? medium->toString().c_str() : "null") << endl
		<< "]";
	return oss.str();
}

MTS_IMPLEMENT_CLASS(Medium, true, NetworkedObject)
MTS_NAMESPACE_END
