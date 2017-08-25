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

#include <mitsuba/render/texture.h>
#include <mitsuba/render/shape.h>
#include <mitsuba/core/properties.h>

MTS_NAMESPACE_BEGIN

/*!\plugin{checkerboard}{Checkerboard}
 * \order{2}
 * \parameters{
 *     \parameter{color0, color1}{\Spectrum}{
 *       Color values for the two differently-colored patches
 *       \default{0.4 and 0.2}
 *     }
 *     \parameter{uoffset, voffset}{\Float}{
 *       Numerical offset that should be applied to UV values before a lookup
 *     }
 *     \parameter{uscale, vscale}{\Float}{
 *       Multiplicative factors that should be applied to UV values before a lookup
 *     }
 * }
 * \renderings{
 *     \rendering{Checkerboard applied to the material test object
 *                as well as the ground plane}{tex_checkerboard}
 * }
 * This plugin implements a simple procedural checkerboard texture with
 * customizable colors.
 */
class Checkerboard : public Texture2D {
public:
	Checkerboard(const Properties &props) : Texture2D(props) {
		m_color0 = props.getSpectrum("color0", Spectrum(.4f));
		m_color1 = props.getSpectrum("color1", Spectrum(.2f));
	}

	Checkerboard(Stream *stream, InstanceManager *manager)
	 : Texture2D(stream, manager) {
		m_color0 = Spectrum(stream);
		m_color1 = Spectrum(stream);
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Texture2D::serialize(stream, manager);
		m_color0.serialize(stream);
		m_color1.serialize(stream);
	}

	inline Spectrum eval(const Point2 &uv) const {
		int x = 2*math::modulo((int) (uv.x * 2), 2) - 1,
			y = 2*math::modulo((int) (uv.y * 2), 2) - 1;

		if (x*y == 1)
			return m_color0;
		else
			return m_color1;
	}

	Spectrum eval(const Point2 &uv,
			const Vector2 &d0, const Vector2 &d1) const {
		/* Filtering is currently not supported */
		return Checkerboard::eval(uv);
	}

	bool usesRayDifferentials() const {
		return false;
	}

	Spectrum getMaximum() const {
		Spectrum max;
		for (int i=0; i<SPECTRUM_SAMPLES; ++i)
			max[i] = std::max(m_color0[i], m_color1[i]);
		return max;
	}

	Spectrum getMinimum() const {
		Spectrum min;
		for (int i=0; i<SPECTRUM_SAMPLES; ++i)
			min[i] = std::min(m_color0[i], m_color1[i]);
		return min;
	}

	Spectrum getAverage() const {
		return (m_color0 + m_color1) * 0.5f;
	}

	bool isConstant() const {
		return false;
	}

	bool isMonochromatic() const {
		return Spectrum(m_color0[0]) == m_color0
			&& Spectrum(m_color1[0]) == m_color1;
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "Checkerboard[" << endl
			<< "    color1 = " << m_color1.toString() << "," << endl
			<< "    color0 = " << m_color0.toString() << endl
			<< "]";
		return oss.str();
	}

	MTS_DECLARE_CLASS()
protected:
	Spectrum m_color1;
	Spectrum m_color0;
};

MTS_IMPLEMENT_CLASS_S(Checkerboard, false, Texture2D)
MTS_EXPORT_PLUGIN(Checkerboard, "Checkerboard texture");
MTS_NAMESPACE_END
