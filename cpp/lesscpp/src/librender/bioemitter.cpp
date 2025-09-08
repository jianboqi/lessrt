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

#include <mitsuba/render/bioemitter.h>
#include <mitsuba/render/medium.h>
#include <mitsuba/core/track.h>
#include <mitsuba/render/shape.h>

MTS_NAMESPACE_BEGIN

AbstractBioemitter::AbstractBioemitter(const Properties& props)
	: ConfigurableObject(props), m_shape(NULL), m_type(0) {
	m_worldTransform = props.getAnimatedTransform("toWorld", Transform());
}

AbstractBioemitter::AbstractBioemitter(Stream* stream, InstanceManager* manager)
	: ConfigurableObject(stream, manager) {
	m_worldTransform = new AnimatedTransform(stream);
	m_medium = static_cast<Medium*>(manager->getInstance(stream));
	m_shape = static_cast<Shape*>(manager->getInstance(stream));
	m_type = stream->readUInt();
}

AbstractBioemitter::~AbstractBioemitter() {
}

void AbstractBioemitter::serialize(Stream* stream, InstanceManager* manager) const {
	ConfigurableObject::serialize(stream, manager);
	m_worldTransform->serialize(stream);
	manager->serialize(stream, m_medium.get());
	manager->serialize(stream, m_shape);
	stream->writeUInt(m_type);
}

void AbstractBioemitter::addChild(const std::string& name, ConfigurableObject* child) {
	if (child->getClass()->derivesFrom(MTS_CLASS(Medium))) {
		Assert(m_medium == NULL);
		m_medium = static_cast<Medium*>(child);
	}
	else {
		ConfigurableObject::addChild(name, child);
	}
}

ref<Shape> AbstractBioemitter::createShape(const Scene* scene) {
	return NULL;
}

Spectrum AbstractBioemitter::getSpectrumAccordingToTemperature(DirectSamplingRecord& dRec, Intersection& its, bool shaded) const {
	NotImplementedError("getSpectrumAccordingToTemperature");
}

Spectrum AbstractBioemitter::getPowerAccordingToTemperature(Point p, int FrontorBack, bool shaded) const {
	NotImplementedError("getPowerAccordingToTemperature");
}

Spectrum AbstractBioemitter::samplePosition(PositionSamplingRecord& pRec,
	const Point2& sample, const Point2* extra) const {
	NotImplementedError("samplePosition");
}

Spectrum AbstractBioemitter::sampleDirection(DirectionSamplingRecord& dRec,
	PositionSamplingRecord& pRec, const Point2& sample,
	const Point2* extra) const {
	NotImplementedError("sampleDirection");
}

Spectrum AbstractBioemitter::sampleDirect(DirectSamplingRecord& dRec, const Point2& sample) const {
	NotImplementedError("sampleDirect");
}

Spectrum AbstractBioemitter::evalPosition(const PositionSamplingRecord& pRec) const {
	NotImplementedError("evalPosition");
}

Spectrum AbstractBioemitter::evalDirection(const DirectionSamplingRecord& dRec,
	const PositionSamplingRecord& pRec) const {
	NotImplementedError("evalDirection");
}

Float AbstractBioemitter::pdfPosition(const PositionSamplingRecord& pRec) const {
	NotImplementedError("pdfPosition");
}

Float AbstractBioemitter::pdfDirection(const DirectionSamplingRecord& dRec,
	const PositionSamplingRecord& pRec) const {
	NotImplementedError("pdfDirection");
}

Float AbstractBioemitter::pdfDirect(const DirectSamplingRecord& dRec) const {
	NotImplementedError("pdfDirect");
}

Bioemitter::Bioemitter(const Properties& props)
	: AbstractBioemitter(props) {
	// Importance sampling weight (used by the luminaire sampling code in \ref Scene)
	m_samplingWeight = props.getFloat("samplingWeight", 1.0f);
}

Bioemitter::Bioemitter(Stream* stream, InstanceManager* manager)
	: AbstractBioemitter(stream, manager) {
	m_samplingWeight = stream->readFloat();
}

void Bioemitter::serialize(Stream* stream, InstanceManager* manager) const {
	AbstractBioemitter::serialize(stream, manager);

	stream->writeFloat(m_samplingWeight);
}

Spectrum Bioemitter::sampleRay(Ray& ray,
	const Point2& spatialSample,
	const Point2& directionalSample,
	Float time) const {
	NotImplementedError("sampleRay");
}


Bioemitter& Bioemitter::operator=(const Bioemitter& other)
{
	NotImplementedError("operator=");
}

void Bioemitter::set_m_Q(Float Q)
{
	NotImplementedError("set_m_Q");
}

int Bioemitter::get_triangleCount() const
{
	NotImplementedError("get_triangleCount");
}

Float* Bioemitter::get_trianglesArea() const
{
	NotImplementedError("get_trianglesArea");
}

void Bioemitter::set_triangleCount(int triangleCount)
{
	NotImplementedError("set_triangleCount");
}

void Bioemitter::set_trianglesArea(Float* trianglesArea)
{
	NotImplementedError("set_trianglesArea");
}

Spectrum Bioemitter::eval(const Intersection& its, const Vector& d) const {
	NotImplementedError("eval");
}
bio_param Bioemitter::get_value_sun() const
{
	NotImplementedError("get_value");
}
std::string Bioemitter::get_shape_name() const
{
	NotImplementedError("get_shape_name");
}

std::string Bioemitter::get_palnt_type() const
{
	NotImplementedError("get_palnt_type");
}

Spectrum Bioemitter::get_kChlrel() const
{
	NotImplementedError("get_kChlrel");
}

void Bioemitter::compute_photosynthesis(bool hasFluor, Float AtsPressure, Float AtsCO2, Float AtsO2, Float Q, unsigned int ShadePhotonNum, unsigned int SunPhotonNum, Float& A, Float& eta)
{
	NotImplementedError("compute_A");
}

Spectrum Bioemitter::evalEnvironment(const RayDifferential& ray) const {
	NotImplementedError("evalEnvironment");
}

bool Bioemitter::fillDirectSamplingRecord(DirectSamplingRecord& dRec,
	const Ray& ray) const {
	NotImplementedError("fillDirectSamplingRecord");
}

Bioemitter::~Bioemitter() { }

Bioemitter* Bioemitter::getElement(size_t index) {
	return NULL;
}

bool Bioemitter::isCompound() const {
	return false;
}

ref<Bitmap> Bioemitter::getBitmap(const Vector2i& sizeHint) const {
	NotImplementedError("getBitmap");
}

MTS_IMPLEMENT_CLASS(Bioemitter, false, AbstractBioemitter)
MTS_IMPLEMENT_CLASS(AbstractBioemitter, true, ConfigurableObject)
MTS_NAMESPACE_END
