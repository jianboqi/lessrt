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

#include <mitsuba/render/basicshader.h>
#include <mitsuba/core/bitmap.h>
MTS_NAMESPACE_BEGIN


ConstantSpectrumTexture::ConstantSpectrumTexture(Stream *stream, InstanceManager *manager)
 : Texture(stream, manager) {
	m_value = Spectrum(stream);
}

void ConstantSpectrumTexture::serialize(Stream *stream, InstanceManager *manager) const {
	Texture::serialize(stream, manager);

	m_value.serialize(stream);
}

ref<Bitmap> ConstantSpectrumTexture::getBitmap(const Vector2i &sizeHint) const {
	ref<Bitmap> result = new Bitmap(Bitmap::ESpectrum, Bitmap::EFloat, Vector2i(1, 1));
	*((Spectrum *) result->getFloatData()) = m_value;
	return result;
}

ConstantFloatTexture::ConstantFloatTexture(Stream *stream, InstanceManager *manager)
 : Texture(stream, manager) {
	m_value = stream->readFloat();
}

void ConstantFloatTexture::serialize(Stream *stream, InstanceManager *manager) const {
	Texture::serialize(stream, manager);
	stream->writeFloat(m_value);
}

ref<Bitmap> ConstantFloatTexture::getBitmap(const Vector2i &sizeHint) const {
	ref<Bitmap> result = new Bitmap(Bitmap::ELuminance, Bitmap::EFloat, Vector2i(1, 1));
	*result->getFloatData() = m_value;
	return result;
}

SpectrumProductTexture::SpectrumProductTexture(Stream *stream, InstanceManager *manager)
 : Texture(stream, manager) {
	m_a = static_cast<Texture *>(manager->getInstance(stream));
	m_b = static_cast<Texture *>(manager->getInstance(stream));
}

void SpectrumProductTexture::serialize(Stream *stream, InstanceManager *manager) const {
	Texture::serialize(stream, manager);
	manager->serialize(stream, m_a.get());
	manager->serialize(stream, m_b.get());
}

ref<Bitmap> SpectrumProductTexture::getBitmap(const Vector2i &sizeHint) const {
	ref<Bitmap> bitmap1 = m_a->getBitmap(sizeHint);
	ref<Bitmap> bitmap2 = m_b->getBitmap(sizeHint);
	return Bitmap::arithmeticOperation(Bitmap::EMultiplication, bitmap1.get(), bitmap2.get());
}

SpectrumAdditionTexture::SpectrumAdditionTexture(Stream *stream, InstanceManager *manager)
 : Texture(stream, manager) {
	m_a = static_cast<Texture *>(manager->getInstance(stream));
	m_b = static_cast<Texture *>(manager->getInstance(stream));
}

void SpectrumAdditionTexture::serialize(Stream *stream, InstanceManager *manager) const {
	Texture::serialize(stream, manager);
	manager->serialize(stream, m_a.get());
	manager->serialize(stream, m_b.get());
}

ref<Bitmap> SpectrumAdditionTexture::getBitmap(const Vector2i &sizeHint) const {
	ref<Bitmap> bitmap1 = m_a->getBitmap(sizeHint);
	ref<Bitmap> bitmap2 = m_b->getBitmap(sizeHint);
	return Bitmap::arithmeticOperation(Bitmap::EAddition, bitmap1.get(), bitmap2.get());
}

SpectrumSubtractionTexture::SpectrumSubtractionTexture(Stream *stream, InstanceManager *manager)
 : Texture(stream, manager) {
	m_a = static_cast<Texture *>(manager->getInstance(stream));
	m_b = static_cast<Texture *>(manager->getInstance(stream));
}

void SpectrumSubtractionTexture::serialize(Stream *stream, InstanceManager *manager) const {
	Texture::serialize(stream, manager);
	manager->serialize(stream, m_a.get());
	manager->serialize(stream, m_b.get());
}

ref<Bitmap> SpectrumSubtractionTexture::getBitmap(const Vector2i &sizeHint) const {
	ref<Bitmap> bitmap1 = m_a->getBitmap(sizeHint);
	ref<Bitmap> bitmap2 = m_b->getBitmap(sizeHint);
	return Bitmap::arithmeticOperation(Bitmap::ESubtraction, bitmap1.get(), bitmap2.get());
}

MTS_IMPLEMENT_CLASS_S(ConstantSpectrumTexture, false, Texture)
MTS_IMPLEMENT_CLASS_S(ConstantFloatTexture, false, Texture)
MTS_IMPLEMENT_CLASS_S(SpectrumProductTexture, false, Texture)
MTS_IMPLEMENT_CLASS_S(SpectrumAdditionTexture, false, Texture)
MTS_IMPLEMENT_CLASS_S(SpectrumSubtractionTexture, false, Texture)
MTS_NAMESPACE_END
