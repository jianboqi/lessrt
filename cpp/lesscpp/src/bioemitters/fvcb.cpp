//author SunBin


#include <mitsuba/render/bioemitter.h>
#include <mitsuba/render/shape.h>
#include <mitsuba/render/medium.h>
#include <mitsuba/render/bsdf.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/render/scene.h>
#include <boost/algorithm/string.hpp>

MTS_NAMESPACE_BEGIN

class FvCB : public Bioemitter {
public:
	FvCB(const Properties &props) : Bioemitter(props) {
		m_type |= EFvCBBioemitter;
		m_PlantType = props.getString("PlantType", "-");
		m_shape_name = props.getString("ShapeName", "");
		if (m_PlantType != "-") {
			read_in_str2Float(props, "Vcmax", m_Vcmax_sun, m_Vcmax_shade);
			read_in_str2Float(props, "BallBerrySlope", m_BallBerrySlope_sun, m_BallBerrySlope_shade);
			read_in_str2Float(props, "BallBerry0", m_BallBerry0_sun, m_BallBerry0_shade);
			read_in_str2Float(props, "Rd", m_Rd_sun, m_Rd_shade);
			read_in_str2Float(props, "RH", m_RH_sun, m_RH_shade);
			read_in_str2Float(props, "Cs", m_Cs_sun, m_Cs_shade);
			read_in_str2Float(props, "Je_Q", m_Je_Q_sun, m_Je_Q_shade);
			if (m_PlantType == "C3") {
				read_in_str2Float(props, "Gamma_star", m_Gamma_star_sun, m_Gamma_star_shade);
				read_in_str2Float(props, "MM_consts", m_MM_consts_sun, m_MM_consts_shade);
				read_in_str2Float(props, "Vs_C3", m_Vs_C3_sun, m_Vs_C3_shade);
			}
			else if (m_PlantType == "C4") {
				read_in_str2Float(props, "Kpepcase", m_Kpepcase_sun, m_Kpepcase_shade);
			}
			if (props.hasProperty("Kn0")) {
				read_in_str2Float(props, "Kn0", m_Kn0_sun, m_Kn0_shade);
				read_in_str2Float(props, "Knalpha", m_Knalpha_sun, m_Knalpha_shade);
				read_in_str2Float(props, "Knbeta", m_Knbeta_sun, m_Knbeta_shade);
				read_in_str2Float(props, "po0", m_po0_sun, m_po0_shade);
				read_in_str2Float(props, "Kd", m_Kd_sun, m_Kd_shade);
			}
			m_kChlrel = props.getSpectrum("kChlrel");
		}
		m_triangleCount = 0;
		m_trianglesArea = NULL;
	}

	FvCB(Stream *stream, InstanceManager *manager)
		: Bioemitter(stream, manager) {
		m_PlantType = stream->readString();
		m_shape_name = stream->readString();
		m_Vcmax_sun = stream->readFloat();
		m_Vcmax_shade = stream->readFloat();
		m_BallBerrySlope_sun = stream->readFloat();
		m_BallBerrySlope_shade = stream->readFloat();
		m_BallBerry0_sun = stream->readFloat();
		m_BallBerry0_shade = stream->readFloat();
		m_Rd_sun = stream->readFloat();
		m_Rd_shade = stream->readFloat();
		m_Kn0_sun = stream->readFloat();
		m_Kn0_shade = stream->readFloat();
		m_Knalpha_sun = stream->readFloat();
		m_Knalpha_shade = stream->readFloat();
		m_Knbeta_sun = stream->readFloat();
		m_Knbeta_shade = stream->readFloat();
		m_po0_sun = stream->readFloat();
		m_po0_shade = stream->readFloat();
		m_Kd_sun = stream->readFloat();
		m_Kd_shade = stream->readFloat();
		m_RH_sun = stream->readFloat();
		m_RH_shade = stream->readFloat();
		m_Cs_sun = stream->readFloat();
		m_Cs_shade = stream->readFloat();
		m_Gamma_star_sun = stream->readFloat();
		m_Gamma_star_shade = stream->readFloat();
		m_MM_consts_sun = stream->readFloat();
		m_MM_consts_shade = stream->readFloat();
		m_Vs_C3_sun = stream->readFloat();
		m_Vs_C3_shade = stream->readFloat();
		m_Je_Q_sun = stream->readFloat();
		m_Je_Q_shade = stream->readFloat();
		m_Kpepcase_sun = stream->readFloat();
		m_Kpepcase_shade = stream->readFloat();
		m_triangleCount = stream->readInt();
		stream->readFloatArray(m_trianglesArea, m_triangleCount);
		m_kChlrel = Spectrum(stream);
		configure();
	}

	void serialize(Stream *stream, InstanceManager *manager) const {
		Bioemitter::serialize(stream, manager);
		stream->writeString(m_PlantType);
		stream->writeString(m_shape_name);
		stream->writeFloat(m_Vcmax_sun);
		stream->writeFloat(m_Vcmax_shade);
		stream->writeFloat(m_BallBerrySlope_sun);
		stream->writeFloat(m_BallBerrySlope_shade);
		stream->writeFloat(m_BallBerry0_sun);
		stream->writeFloat(m_BallBerry0_shade);
		stream->writeFloat(m_Rd_sun);
		stream->writeFloat(m_Rd_shade);
		stream->writeFloat(m_Kn0_sun);
		stream->writeFloat(m_Kn0_shade);
		stream->writeFloat(m_Knalpha_sun);
		stream->writeFloat(m_Knalpha_shade);
		stream->writeFloat(m_Knbeta_sun);
		stream->writeFloat(m_Knbeta_shade);
		stream->writeFloat(m_po0_sun);
		stream->writeFloat(m_po0_shade);
		stream->writeFloat(m_Kd_sun);
		stream->writeFloat(m_Kd_shade);
		stream->writeFloat(m_RH_sun);
		stream->writeFloat(m_RH_shade);
		stream->writeFloat(m_Cs_sun);
		stream->writeFloat(m_Cs_shade);
		stream->writeFloat(m_Gamma_star_sun);
		stream->writeFloat(m_Gamma_star_shade);
		stream->writeFloat(m_MM_consts_sun);
		stream->writeFloat(m_MM_consts_shade);
		stream->writeFloat(m_Vs_C3_sun);
		stream->writeFloat(m_Vs_C3_shade);
		stream->writeFloat(m_Je_Q_sun);
		stream->writeFloat(m_Je_Q_shade);
		stream->writeFloat(m_Kpepcase_sun);
		stream->writeFloat(m_Kpepcase_shade);
		stream->writeInt(m_triangleCount);
		stream->writeFloatArray(m_trianglesArea, m_triangleCount);
		m_kChlrel.serialize(stream);
	}

	void read_in_str2Float(const Properties& props, std::string name, Float& value_sun, Float& value_shade) {
		std::string read_in = props.getString(name);
		std::vector<std::string> arr;
		boost::algorithm::split(arr, read_in, boost::is_any_of(":"));
		value_sun = atof(arr[0].c_str());
		value_shade = atof(arr[1].c_str());
	}

	Spectrum eval(const Intersection &its, const Vector &d) const {
		Spectrum radiance;
		//if (its.shaded)
		//	radiance = m_lowerThermalSpectrum;
		//else
		//	radiance = m_upperThermalSpecturm;

		const BSDF *bsdf = its.getBSDF();
		if (dot(its.shFrame.n, d) < 0) {//intersected back
			Intersection its_tmp;
			its_tmp.p = its.p;
			BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, -1), Vector(0, 0, -1));
			bRecref.typeMask = bsdf->EDiffuseReflection;
			Spectrum ref = bsdf->eval(bRecref)*M_PI_DBL;
			return (Spectrum(1.0) - ref)*radiance;
		}

		if (dot(its.shFrame.n, d) > 0) {//intersected front
			Intersection its_tmp;
			its_tmp.p = its.p;
			BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, 1), Vector(0, 0, 1));
			bRecref.typeMask = bsdf->EDiffuseReflection;
			Spectrum ref = bsdf->eval(bRecref)*M_PI_DBL;
			return (Spectrum(1.0) - ref)*radiance;
		}
		
		return Spectrum(0.0);
	}

	Float pdfPosition(const PositionSamplingRecord &pRec) const {
		return m_shape->pdfPosition(pRec);
	}

	void setParent(ConfigurableObject *parent) {
		Bioemitter::setParent(parent);

		if (parent->getClass()->derivesFrom(MTS_CLASS(Shape))) {
			Shape *shape = static_cast<Shape *>(parent);
			if (m_shape == shape || shape->isCompound())
				return;

			if (m_shape != NULL)
				Log(EError, "A FvCB param cannot be parent of multiple shapes");

			m_shape = shape;
			m_shape->configure();
			m_trianglesArea = m_shape->getTrianglesArea(m_triangleCount);
		} else {
			Log(EError, "An FvCB param must be child of a shape instance");
		}
	}
	
	std::string get_shape_name()const {
		return m_shape_name;
	}

	// 定义 gsFun 函数，计算 gs 的值
	Float gsFun(Float Cs, Float RH, Float A, Float BallBerrySlope, Float BallBerry0) {
		Float gs = std::max(BallBerry0, BallBerrySlope * A * RH / (Cs + std::numeric_limits<Float>::epsilon()) + BallBerry0);
		// 处理 Cs 为 NaN 的情况
		if (std::isnan(Cs)) {
			gs = std::numeric_limits<Float>::quiet_NaN();
		}
		return gs;
	}

	// BallBerry 模型的主函数
	void BallBerry(Float Cs, Float RH, Float A, Float BallBerrySlope, Float BallBerry0, Float minCi, Float Ci_input, Float& Ci, Float& gs) {
		if (Ci_input != 0) {
			// Ci 给定，尝试计算 gs
			Ci = Ci_input;
			if (A != 0) {
				gs = gsFun(Cs, RH, A, BallBerrySlope, BallBerry0);
			}
		}
		else if (BallBerry0 == 0 || A == 0) {
			// 在平衡状态下计算 Ci
			Ci = std::max(minCi * Cs, Cs * (1 - 1.6 / (BallBerrySlope * RH)));
			gs = 0;
		}
		else {
			// 如果 b > 0，计算 Ci 和 gs
			gs = gsFun(Cs, RH, A, BallBerrySlope, BallBerry0);
			Ci = std::max(minCi * Cs, Cs - 1.6 * A / gs);
		}
	}

	// Fluorescence model 函数
	void Fluorescencemodel(Float ps, Float x, Float Kp, Float Kf, Float Kd, Float Kno, Float alpha, Float beta, Float& eta, Float& qE, Float& qQ, Float& fs, Float& fo, Float& fm, Float& fo0, Float& fm0, Float& Kn) {

		Float x_alpha = std::exp(std::log(x) * alpha); // 这是函数中最耗时的操作

		Kn = Kno * (1 + beta) * x_alpha / (beta + x_alpha);

		fo0 = Kf / (Kf + Kp + Kd);        // 暗适应荧光产额 Fo,0
		fo = Kf / (Kf + Kp + Kd + Kn);     // 光照下暗适应荧光产额 Fo
		fm = Kf / (Kf + Kd + Kn);         // 光照下荧光产额 Fm
		fm0 = Kf / (Kf + Kd);              // 暗适应荧光产额 Fm
		fs = fm * (1 - ps);                // 稳态荧光产额 Ft (也称 Fs)
		eta = fs / fo0;
		qQ = 1 - (fs - fo) / (fm - fo);    // 光化学猝灭
		qE = 1 - (fm - fo) / (fm0 - fo0);  // 非光化学猝灭
	}

	// 辅助函数，用于选择二次方程的根
	Float sel_root(Float a, Float b, Float c, int dsign) {
		// 计算判别式
		Float discriminant = b * b - 4 * a * c;
		// 根据 dsign 的值选择根
		if (dsign == 0) dsign = -1; // 如果 dsign 为 0，则选择较小的根
		// 使用二次公式计算根
		return (-b + (dsign > 0 ? +1 : -1) * std::sqrt(discriminant)) / (2 * a);
	}

	// 计算光合作用速率的函数
	void computeA(Float Ci, Float g_m, Float Vs_C3, Float MM_consts, Float Rd, Float Vcmax, Float Gamma_star, Float Je, Float effcon, Float atheta, Float kpepcase, Float& A, Float& Ag, Float& Vc, Float& Vs, Float& Ve, Float& CO2_per_electron) {
		if (m_PlantType == "C3") {
			Vs = Vs_C3;
			if (g_m < std::numeric_limits<Float>::infinity()) {
				Vc = sel_root(1. / g_m, -(MM_consts + Ci + (Rd + Vcmax) / g_m), Vcmax * (Ci - Gamma_star + Rd / g_m), -1);
				Ve = sel_root(1. / g_m, -(Ci + 2 * Gamma_star + (Rd + Je * effcon) / g_m), Je * effcon * (Ci - Gamma_star + Rd / g_m), -1);
				CO2_per_electron = Ve / Je;
			}
			else {
				Vc = Vcmax * (Ci - Gamma_star) / (MM_consts + Ci);
				CO2_per_electron = (Ci - Gamma_star) / (Ci + 2 * Gamma_star) * effcon;
				Ve = Je * CO2_per_electron;
			}
		}
		else if(m_PlantType == "C4") { // C4
			Vc = Vcmax;
			Vs = kpepcase * Ci;
			CO2_per_electron = effcon;
			Ve = Je * CO2_per_electron;
		}

		Float V = sel_root(atheta, -(Vc + Ve), Vc * Ve, signum(-Vc));
		Ag = sel_root(0.98, -(V + Vs), V * Vs, -1);
		A = Ag - Rd;
	}

	int signum(Float value) {
		if (value > 0) {
			return 1;
		}
		else if (value < 0) {
			return -1;
		}
		else {
			return 0;
		}
	}

	//Test - function for iteration
	// (note that it assigns A in the function's context.)
	// As with the next section, this code can be read as if the function body executed at this point.
	// (if iteration was used).In other words, A is assigned at this point in the file(when iterating).
	Float Ci_next(Float Ci_in, Float& err) {
		// compute the difference between "guessed" Ci(Ci_in) and Ci computed using BB after computing A
		Float A, Ci_out; //= A_fun(Ci_in);
		if (m_PlantType == "C3") {
			if (m_isShade) {
				Float Je = m_Je_Q_shade * m_Q;
				Float Ag, Vc, Vs, Ve, CO2_per_electron;
				computeA(Ci_in, std::numeric_limits<Float>::infinity(), m_Vs_C3_shade, m_MM_consts_shade, m_Rd_shade, m_Vcmax_shade, m_Gamma_star_shade, Je, 0.2, 0.8, 1, A, Ag, Vc, Vs, Ve, CO2_per_electron);
				Float A_bar = A * m_ppm2bar;
				Float gs;
				BallBerry(m_Cs_shade, m_RH_shade, A_bar, m_BallBerrySlope_shade, m_BallBerry0_shade, 0.3, 0, Ci_out, gs); // [Ci_out, gs]
			}
			else {
				Float Je = m_Je_Q_sun * m_Q;
				Float Ag, Vc, Vs, Ve, CO2_per_electron;
				computeA(Ci_in, std::numeric_limits<Float>::infinity(), m_Vs_C3_sun, m_MM_consts_sun, m_Rd_sun, m_Vcmax_sun, m_Gamma_star_sun, Je, 0.2, 0.8, 1, A, Ag, Vc, Vs, Ve, CO2_per_electron);
				Float A_bar = A * m_ppm2bar;
				Float gs;
				BallBerry(m_Cs_sun, m_RH_sun, A_bar, m_BallBerrySlope_sun, m_BallBerry0_sun, 0.3, 0, Ci_out, gs); // [Ci_out, gs]
			}
		}
		else if (m_PlantType == "C4") {
			if (m_isShade) {
				Float Je = m_Je_Q_shade * m_Q;
				Float Ag, Vc, Vs, Ve, CO2_per_electron;
				computeA(Ci_in, std::numeric_limits<Float>::infinity(), 0, 0, m_Rd_shade, m_Vcmax_shade, m_Gamma_star_shade, Je, 1.0 / 6, 0.8, m_Kpepcase_sun, A, Ag, Vc, Vs, Ve, CO2_per_electron);
				Float A_bar = A * m_ppm2bar;
				Float gs;
				BallBerry(m_Cs_shade, m_RH_shade, A_bar, m_BallBerrySlope_shade, m_BallBerry0_shade, 0.1, 0, Ci_out, gs); // [Ci_out, gs]
			}
			else {
				Float Je = m_Je_Q_sun * m_Q;
				Float Ag, Vc, Vs, Ve, CO2_per_electron;
				computeA(Ci_in, std::numeric_limits<Float>::infinity(), 0, 0, m_Rd_sun, m_Vcmax_sun, m_Gamma_star_sun, Je, 1.0 / 6, 0.8, m_Kpepcase_sun, A, Ag, Vc, Vs, Ve, CO2_per_electron);
				Float A_bar = A * m_ppm2bar;
				Float gs;
				BallBerry(m_Cs_sun, m_RH_sun, A_bar, m_BallBerrySlope_sun, m_BallBerry0_sun, 0.1, 0, Ci_out, gs); // [Ci_out, gs]
			}
		}
		err = Ci_out - Ci_in; // f(x) - x
		return Ci_out;
	}

	void fixedp_brent_ari(Float x0, Float tolFn, Float& b, Float& err2) {
		Float tolx_1 = 0;
		int subsetLimit = 0;
		bool accelBisection = false;
		int accelLimit = 3;
		bool rotatePrev = true;
		int iter_limit = 100;
		bool recompute_b = false;

		Float a = x0;
		Float err1;
		b = Ci_next(a, err1);
		Float t = Ci_next(b, err2);
		if (isnan(err2))err2 = 0;
		bool err_outside_tol = abs(err2) > tolFn;
		if (!err_outside_tol)return;
		recompute_b = true;
		bool not_bracketting_zero = (signum(err1) == signum(err2)) && err_outside_tol;
		if (not_bracketting_zero) {
			Float x1 = b - err2 * (b - a) / (err2 - err1);
			Float err_x1;
			t = Ci_next(x1, err_x1);
			bool use_x1 = (signum(err_x1) != signum(err1)) && not_bracketting_zero;
			if (use_x1) {
				//bool swap_to_a = (abs(err2) < abs(err1) && use_x1);
				a = b; err1 = err2;
				b = x1; err2 = err_x1;
			}
			err_outside_tol = std::min(abs(err1), abs(err2)) > tolFn;
			not_bracketting_zero = (signum(err1) == signum(err2)) && err_outside_tol;
			if (not_bracketting_zero) {
				//swap_to_a = (err2 < err1& not_bracketting_zero);
				std::swap(a, b);
				std::swap(err1, err2);
			}
			bool both_positive = err1 > 0 && not_bracketting_zero;
			int ntries = 1;
			while (both_positive) {
				Float diffab = b - a;
				a = a - diffab;
				t = Ci_next(a, err1);
				//swap_to_a = (err2 < err1& not_bracketting_zero);
				std::swap(a, b);
				std::swap(err1, err2);
				err_outside_tol = std::min(abs(err1), abs(err2)) > tolFn;
				not_bracketting_zero = (signum(err1) == signum(err2) && err_outside_tol);
				both_positive = not_bracketting_zero;
				if (both_positive && ntries > 10) {
					Log(EInfo, "Couldn't find contrapoint in 10 tries!");
					break;
				}
				ntries += 1;
			}
			bool both_negative = err2 < 0 && not_bracketting_zero;
			if (both_negative) {
				b = 0;
				t = Ci_next(b, err2);
			}
			recompute_b = true;
		}
		Float tolx = 2 * std::max(1.0, abs(b)) * tolx_1;
		err_outside_tol = 0.5 * abs(a - b) > tolx && std::min(abs(err1), abs(err2)) > tolFn;

		bool err1_is_best = abs(err2) > abs(err1);
		if (err1_is_best) {
			std::swap(a, b);
			std::swap(err1, err2);
			recompute_b = true;
		}

		Float ab_gap = (a - b);
		Float c = a; Float err3 = err1;
		bool best_is_unchanged = abs(err2) == abs(err1);
		Float xstep, xstep1;
		xstep = xstep1 = 3 * ab_gap;
		Float q = 1;
		Float p = 0;
		int counter = 0;
		Float accel_bi = 0;
		while (err_outside_tol) {
			Float xstep2 = xstep1;
			xstep1 = xstep;
			p = 0 * p;
			xstep = 0 * xstep;
			bool use_bisection = (abs(xstep2) < tolx) || best_is_unchanged;
			Float r2 = err2  / err1;
			bool try_interp = !use_bisection && err_outside_tol;
			bool quad_is_safe = (err1 != err3 && err2 != err3);
			bool use_quad = try_interp && quad_is_safe;
			if (use_quad) {
				Float r1 = err3 / err1;
				Float r3 = err2 / err3;
				p = r3 * (ab_gap * r1 * (r1 - r2) - (b - c) * (r2 - 1));
				q = (r1 - 1) * (r2 - 1) * (r3 - 1);
			}
			bool use_secant = try_interp && !quad_is_safe;
			if (use_secant) {
				Float p1 = ab_gap * r2;
				p = p1;
				q = 1 - r2;
			}
			if (try_interp) {
				xstep = p / q;
			}
			else {
				xstep = 0;
			}
			bool bi_test1 = abs(p) >= 0.75 * abs(ab_gap * q) - 0.5 * abs(tolx * q);
			bool bi_test3 = abs(p) >= 0.5 * abs(xstep2 * q);
			use_bisection = (use_bisection || bi_test1 || bi_test3) && err_outside_tol;
			if (use_bisection) {
				Float m = -ab_gap / (2 + accel_bi);
				xstep = xstep1 = m;
			}
			Float s = b - xstep;
			bool xstep_too_small = abs(xstep) < tolx && err_outside_tol;
			if (xstep_too_small) {
				Float s2 = b + signum(ab_gap) * tolx;
				s = s2;
			}
			if (!(use_secant || use_quad || use_bisection || !err_outside_tol)) {
				Log(EInfo, "Somehow, we didn't update idx");
				break;
			}
			Float err_s;
			t = Ci_next(s, err_s);
			counter += 1;
			if (counter > iter_limit) {
				Log(EInfo, "iteration limit exceeded");
				break;
			}
			if (abs(err_s) < tolFn) {
				b = s;
				err2 = err_s;
				err_outside_tol = false;
				recompute_b = false;
			}
			else {
				best_is_unchanged = abs(err_s) > abs(err2);
				if (accelBisection) {
					accel_bi = accel_bi + best_is_unchanged;
					if (!best_is_unchanged || (accel_bi >= accelLimit)) {
						accel_bi = 0;
					}
					best_is_unchanged = accel_bi > 0;
				}
				c = b; err3 = err2;
				bool s_b_sign_match = signum(err_s) == signum(err2);
				bool err_s_is_best = (abs(err_s) <= abs(err2)) && err_outside_tol;
				bool a_into_b = (s_b_sign_match && !err_s_is_best) && err_outside_tol;
				if (a_into_b) {
					b = a;
					err2 = err1;
				}
				bool b_into_a = !s_b_sign_match && err_s_is_best;
				if (b_into_a) {
					c = a; err3 = err1;
					a = b; err1 = err2;
				}
				if (err_s_is_best) {
					b = s;
					err2 = err_s;
				}
				bool err_s_not_best = !err_s_is_best && err_outside_tol;
				if (err_s_not_best) {
					a = s;
					err1 = err_s;
					xstep1 = xstep;
				}
				ab_gap = a - b;
				tolx = 2 * std::max(1.0, abs(b)) * tolx_1;
				err_outside_tol = (0.5 * abs(ab_gap) > tolx && abs(err2) > tolFn);
				recompute_b = true;
			}
		}
		if (recompute_b) {
			t = Ci_next(b, err2);
		}
	}
	std::string get_palnt_type() const
	{
		return m_PlantType;
	}
	void set_triangleCount(int triangleCount) {
		m_triangleCount = triangleCount;
	}
	int get_triangleCount() const {
		return m_triangleCount;
	}
	void set_trianglesArea(Float* trianglesArea) {
		m_trianglesArea = trianglesArea;
	}
	Float* get_trianglesArea() const {
		return m_trianglesArea;
	}
	Spectrum get_kChlrel() const
	{
		return m_kChlrel;
	}
	void set_m_Q(Float Q) {
		m_Q = Q;
	}

	void compute_photosynthesis(bool hasFluor,Float AtsPressure, Float AtsCO2, Float AtsO2, Float Q, unsigned int ShadePhotonNum, unsigned int SunPhotonNum, Float &A, Float& eta)
	{
		m_ppm2bar = AtsPressure * 1E-9;
		m_Q = Q;
		Float Ci, err, Ag;
		A = Ag = Ci = eta = err = 0;
		if (m_PlantType != "-"){
			Float A_shade, A_sun, Ag_shade, Ag_sun, CO2_per_electron_sun, CO2_per_electron_shade, Ci_sun, Ci_shade, err;
			A_shade = A_sun = Ag_shade = Ag_sun = Ci_sun = Ci_shade = err = 0;
			if (ShadePhotonNum) {
				m_isShade = true;
				fixedp_brent_ari(m_Cs_shade, 1e-9, Ci_shade, err);

				Float Je = m_Je_Q_shade * m_Q;
				Float Vc, Vs, Ve;
				if (m_PlantType == "C3") {
					computeA(Ci_shade, std::numeric_limits<Float>::infinity(), m_Vs_C3_shade, m_MM_consts_shade, m_Rd_shade, m_Vcmax_shade, m_Gamma_star_shade, Je, 0.2, 0.8, 1, A_shade, Ag_shade, Vc, Vs, Ve, CO2_per_electron_shade);
				}
				else if (m_PlantType == "C4") {
					computeA(Ci_shade, std::numeric_limits<Float>::infinity(), 0, 0, m_Rd_shade, m_Vcmax_shade, m_Gamma_star_shade, Je, 1.0 / 6, 0.8, m_Kpepcase_sun, A_shade, Ag_shade, Vc, Vs, Ve, CO2_per_electron_shade);
				}
			}
			if (SunPhotonNum) {
				m_isShade = false;
				fixedp_brent_ari(m_Cs_shade, 1e-9, Ci_sun, err);

				Float Je = m_Je_Q_sun * m_Q;
				Float Vc, Vs, Ve;
				if (m_PlantType == "C3") {
					computeA(Ci_sun, std::numeric_limits<Float>::infinity(), m_Vs_C3_sun, m_MM_consts_sun, m_Rd_sun, m_Vcmax_sun, m_Gamma_star_sun, Je, 0.2, 0.8, 1, A_sun, Ag_sun, Vc, Vs, Ve, CO2_per_electron_sun);
				}
				else if (m_PlantType == "C4") {
					computeA(Ci_sun, std::numeric_limits<Float>::infinity(), 0, 0, m_Rd_sun, m_Vcmax_sun, m_Gamma_star_sun, Je, 1.0 / 6, 0.8, m_Kpepcase_sun, A_sun, Ag_sun, Vc, Vs, Ve, CO2_per_electron_sun);
				}
			}
			Float sun_r = Float(SunPhotonNum) / (SunPhotonNum + ShadePhotonNum);
			Float shade_r = 1 - sun_r;
			A = A_sun * sun_r + A_shade * shade_r;
			Ag = Ag_sun * sun_r + Ag_shade * shade_r;
			Ci = Ci_sun * sun_r + Ci_shade * shade_r;
			//CO2_per_electron = CO2_per_electron_sun * sun_r + CO2_per_electron_shade * shade_r;

			if (hasFluor) {
				Float gs_shade = std::max(0.0, 1.6 * A_shade * m_ppm2bar / (m_Cs_shade - Ci_shade));
				Float gs_sun = std::max(0.0, 1.6 * A_sun * m_ppm2bar / (m_Cs_sun - Ci_sun));
				Float Ja_shade = Ag_shade / CO2_per_electron_shade;
				Float Ja_sun = Ag_sun / CO2_per_electron_sun;
				//Float rcw_shade = 41.598756906077355 / gs_shade;
				//Float rcw_sun = 41.598756906077355 / gs_sun;
				Float ps_shade = isnan(m_po0_shade) ? m_po0_shade : m_po0_shade * Ja_shade / (m_Je_Q_shade * m_Q);
				Float ps_sun = isnan(m_po0_sun) ? m_po0_sun : m_po0_sun * Ja_sun / (m_Je_Q_sun * m_Q);
				Float ps_rel_shade = std::max(0.0, 1 - ps_shade / m_po0_shade);
				Float ps_rel_sun = std::max(0.0, 1 - ps_sun / m_po0_sun);
				Float eta_shade, eta_sun, qE_shade, qE_sun, qQ_shade, qQ_sun, fs_shade, fs_sun, fo_shade, fo_sun, fm_shade, fm_sun, fo0_shade, fo0_sun, fm0_shade, fm0_sun, Kn_shade, Kn_sun;
				Fluorescencemodel(ps_shade, ps_rel_shade, 4, 0.05, m_Kd_shade, m_Kn0_shade, m_Knalpha_shade, m_Knbeta_shade, eta_shade, qE_shade, qQ_shade, fs_shade, fo_shade, fm_shade, fo0_shade, fm0_shade, Kn_shade);
				Fluorescencemodel(ps_sun, ps_rel_sun, 4, 0.05, m_Kd_sun, m_Kn0_sun, m_Knalpha_sun, m_Knbeta_sun, eta_sun, qE_sun, qQ_sun, fs_sun, fo_sun, fm_sun, fo0_sun, fm0_sun, Kn_sun);
				eta = eta_sun * sun_r + eta_shade * shade_r;
			}
		}
	}

	bio_param get_value_sun() const
	{
		bio_param bio_param_sun;
		bio_param_sun.PlantType = m_PlantType;
		bio_param_sun.Vcmax = m_Vcmax_sun;
		bio_param_sun.BallBerrySlope = m_BallBerrySlope_sun;
		bio_param_sun.BallBerry0 = m_BallBerry0_sun;
		bio_param_sun.Rd = m_Rd_sun;
		bio_param_sun.Kn0 = m_Kn0_sun;
		bio_param_sun.Knalpha = m_Knalpha_sun;
		bio_param_sun.Knbeta = m_Knbeta_sun;
		bio_param_sun.po0 = m_po0_sun;
		bio_param_sun.RH = m_RH_sun;
		bio_param_sun.Cs = m_Cs_sun;
		bio_param_sun.Gamma_star = m_Gamma_star_sun;
		bio_param_sun.MM_consts = m_MM_consts_sun;
		bio_param_sun.Vs_C3 = m_Vs_C3_sun;
		bio_param_sun.Je_Q = m_Je_Q_sun;
		bio_param_sun.Kpepcase = m_Kpepcase_sun;
		return bio_param_sun;
	}

	AABB getAABB() const {
		return m_shape->getAABB();
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "FvCB[" << endl
			<< "  PlantType = " << m_PlantType << "," << endl
			<< "  Vcmax = " << m_Vcmax_sun << ":" << m_Vcmax_shade << "," << endl
			<< "  BallBerrySlope = " << m_BallBerrySlope_sun << ":" << m_BallBerrySlope_shade << "," << endl
			<< "  BallBerry0 = " << m_BallBerry0_sun << ":" << m_BallBerry0_shade << "," << endl
			<< "  Rd = " << m_Rd_sun << ":" << m_Rd_shade << "," << endl
			<< "  Kn0 = " << m_Kn0_sun << ":" << m_Kn0_shade << "," << endl
			<< "  Knalpha = " << m_Knalpha_sun << ":" << m_Knalpha_shade << "," << endl
			<< "  Knbeta = " << m_Knbeta_sun << ":" << m_Knbeta_shade << "," << endl
			<< "  po0 = " << m_po0_sun << ":" << m_po0_shade << "," << endl
			<< "  Kd = " << m_Kd_sun << ":" << m_Kd_shade << "," << endl
			<< "  RH = " << m_RH_sun << ":" << m_RH_shade << "," << endl
			<< "  Cs = " << m_Cs_sun << ":" << m_Cs_shade << "," << endl
			<< "  Gamma_star = " << m_Gamma_star_sun << ":" << m_Gamma_star_shade << "," << endl
			<< "  MM_consts = " << m_MM_consts_sun << ":" << m_MM_consts_shade << "," << endl
			<< "  Vs_C3 = " << m_Vs_C3_sun << ":" << m_Vs_C3_shade << "," << endl
			<< "  Je_Q = " << m_Je_Q_sun << ":" << m_Je_Q_shade << "," << endl
			<< "  Kpepcase = " << m_Kpepcase_sun << ":" << m_Kpepcase_shade << "," << endl;
		if (m_shape)
			oss << m_shape->getSurfaceArea();
		else
			oss << "<no shape attached!>";
		oss << "," << endl
		    << "  medium = " << indent(m_medium.toString()) << endl
			<< "]";
		return oss.str();
	}

	// 赋值运算符
	FvCB& operator=(const FvCB& other) {
		if (this != &other) {
			m_PlantType = other.m_PlantType;
			m_Q = other.m_Q;
			m_ppm2bar = other.m_ppm2bar;
			m_isShade = other.m_isShade;
			m_Cs_shade = other.m_Cs_shade;
			m_Cs_sun = other.m_Cs_sun;
			m_Je_Q_shade = other.m_Je_Q_shade;
			m_Je_Q_sun = other.m_Je_Q_sun;
			m_Vs_C3_shade = other.m_Vs_C3_shade;
			m_MM_consts_shade = other.m_MM_consts_shade;
			m_Rd_shade = other.m_Rd_shade;
			m_Vcmax_shade = other.m_Vcmax_shade;
			m_Gamma_star_shade = other.m_Gamma_star_shade;
			m_Vs_C3_sun = other.m_Vs_C3_sun;
			m_MM_consts_sun = other.m_MM_consts_sun;
			m_Rd_sun = other.m_Rd_sun;
			m_Vcmax_sun = other.m_Vcmax_sun;
			m_Gamma_star_sun = other.m_Gamma_star_sun;
			m_Kpepcase_sun = other.m_Kpepcase_sun;
			m_po0_shade = other.m_po0_shade;
			m_po0_sun = other.m_po0_sun;
			m_Kd_shade = other.m_Kd_shade;
			m_Kn0_shade = other.m_Kn0_shade;
			m_Knalpha_shade = other.m_Knalpha_shade;
			m_Knbeta_shade = other.m_Knbeta_shade;
			m_Kd_sun = other.m_Kd_sun;
			m_Kn0_sun = other.m_Kn0_sun;
			m_Knalpha_sun = other.m_Knalpha_sun;
			m_Knbeta_sun = other.m_Knbeta_sun;
			m_trianglesArea = other.m_trianglesArea;
		}
		return *this;
	}

	MTS_DECLARE_CLASS()
public:

	std::string m_shape_name = "";
	std::string m_PlantType = "-";
	Float m_Vcmax_sun = 60;
	Float m_Vcmax_shade = 60;
	Float m_BallBerrySlope_sun = 8;
	Float m_BallBerrySlope_shade = 8;
	Float m_BallBerry0_sun = 0.01;
	Float m_BallBerry0_shade = 0.01;
	Float m_Rd_sun = 0.015;
	Float m_Rd_shade = 0.015;
	Float m_Kn0_sun = 2.48;
	Float m_Kn0_shade = 2.48;
	Float m_Knalpha_sun = 2.83;
	Float m_Knalpha_shade = 2.83;
	Float m_Knbeta_sun = 0.114;
	Float m_Knbeta_shade = 0.114;
	Float m_po0_sun = 0.114;
	Float m_po0_shade = 0.114;
	Float m_Kd_sun = 0.114;
	Float m_Kd_shade = 0.114;
	Float m_RH_sun = 0.26637910310002433;
	Float m_RH_shade = 0.2121938703953782;
	Float m_Cs_sun = 0.00037345;
	Float m_Cs_shade = 0.00036375;
	Float m_Gamma_star_sun = 7.791848289726934e-05;
	Float m_Gamma_star_shade = 7.087841338148617e-05;
	Float m_MM_consts_sun = 0.0021260405752797575;
	Float m_MM_consts_shade = 0.00178991495097149;
	Float m_Vs_C3_sun = 37.32817020379738;
	Float m_Vs_C3_shade = 38.44900575899531;
	Float m_Je_Q_sun = 0.37975272401375837;
	Float m_Je_Q_shade = 0.3841437004754738;
	Float m_Kpepcase_sun = 1689888.54128516;
	Float m_Kpepcase_shade = 1099337.1152328053;
	Spectrum m_kChlrel;

	Float* m_trianglesArea;
	int m_triangleCount;

	Float m_ppm2bar;
	Float m_Q;
	bool m_isShade;
};


MTS_IMPLEMENT_CLASS_S(FvCB, false, Bioemitter)
MTS_EXPORT_PLUGIN(FvCB, "Model FvCB");
MTS_NAMESPACE_END
