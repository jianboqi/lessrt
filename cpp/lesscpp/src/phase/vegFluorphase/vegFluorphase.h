#ifndef _VEGFLUORPHASE_H_
#define _VEGFLUORPHASE_H_
#include <mitsuba/render/scene.h>
#include <mitsuba/core/math.h>
#include <vector>
using namespace std;
MTS_NAMESPACE_BEGIN

#define PHRT_M_PI 3.14159265358979323846

vector<double> gauss_quad_pos{ -0.9739,-0.8651,-0.6794,-0.4334,-0.1489,0.1489,0.4334,0.6794,0.8651,0.9739 };
vector<double> gauss_quad_coeff{ 0.0667,0.1495,0.2191,0.2693,0.2955,0.2955,0.2693,0.2191,0.1495,0.0667 };

vector<double> gauss_quad8_pos{ -0.9603,-0.7967,-0.5255,-0.1834,0.1834,0.5255,0.7967,0.9603 };
vector<double> gauss_quad8_coeff{ 0.1012,0.2224,0.3137,0.3627,0.3627,0.3137,0.2224,0.1012 };

vector<double> gauss_quad6_pos{ -0.9325,-0.6612,- 0.2386,0.2386,0.6612,0.9325 };
vector<double> gauss_quad6_coeff{ 0.1713,0.3608,0.4679,0.4679,0.3608,0.1713 };

class VegFluorPhaseHelper {
public:
	VegFluorPhaseHelper() {}
	VegFluorPhaseHelper(std::string ladType) :m_ladType(ladType) {}
	
	/// <summary>
	/// Generate directions
	/// </summary>
	/// <param name="NumberOfDirs"></param>
	/// <param name="accumulated_ZenithAngle"></param>
	/// <param name="accumulated_azimuthAngle"></param>
	static void generationDiscreteDirections(int NumberOfDirs,
		vector<double>& accumulated_ZenithAngle, vector<vector<double>>& accumulated_azimuthAngle) {
		double r_i1 = 2 * std::sin(0.25 * PHRT_M_PI);
		double theta_i1 = 0.5 * PHRT_M_PI;
		int k_i1 = NumberOfDirs;

		double theta = 0, k = 0, r = 0;
		do {
			accumulated_ZenithAngle.insert(accumulated_ZenithAngle.begin(), theta_i1);
			theta = theta_i1 - 2 * std::sin(0.5 * theta_i1) * std::sqrt(PHRT_M_PI / (double)k_i1);
			r = 2 * std::sin(0.5 * theta);
			k = int(k_i1 * (r / r_i1) * (r / r_i1));
			//compute a new r and theta
			r = r_i1 * std::sqrt(k / (double)k_i1);
			theta = 2 * std::asin(0.5 * r);

			int numOfDirectionInSector = k_i1 - k;
			double aziInterval = 2 * PHRT_M_PI / double(numOfDirectionInSector);
			vector<double> azi_each_sector;
			for (int i = 0; i < numOfDirectionInSector; i++) {
				double azimutStart = i * aziInterval;
				double azimuEnd = (i + 1) * aziInterval;
				double solidAngle = PHRT_M_PI * (r_i1 * r_i1 - r * r) / (double)numOfDirectionInSector;
				//discreteDirections.push_back(new AngularDirection(theta, theta_i1, azimutStart, azimuEnd, solidAngle));
				azi_each_sector.push_back(azimuEnd);
			}
			accumulated_azimuthAngle.insert(accumulated_azimuthAngle.begin(), azi_each_sector);
			//update previous value
			k_i1 = k; r_i1 = r; theta_i1 = theta;
		} while (theta > 0);
	}

	Float GFunc(Vector& incDir) {
		Float GValue = 0;
		double theta_step = 0.5 / 180.0 * M_PI_DBL;
		int num = (int)(0.5 * M_PI_DBL / theta_step);

		Float cosTheta = absDot(Vector(0, 1, 0), incDir);  //zenith angle (cos) of incident ray
		Float Theta = math::safe_acos(cosTheta);
		Float cotTheta = 1 / tan(Theta);


		if (m_ladType == "Spherical") {
			for (int i = 0; i < num; i++) {
				Float center = (i + 0.5) * theta_step;
				Float cosThetaL = cos(center);
				Float cotThetaL = 1 / tan(center);
				Float cotThetaThetaL = cotTheta * cotThetaL;
				Float phi = math::safe_acos(cotThetaThetaL);
				Float A = 0;
				if (abs(cotThetaThetaL) > 1) {
					A = cosTheta * cosThetaL;
				}
				else {
					A = cosTheta * cosThetaL * (1 + 2 / M_PI_DBL * (tan(phi) - phi));
				}
				GValue += sin(center) * A * theta_step;
			}
		}
		return GValue;
	}

public:
	std::string m_ladType;
};


MTS_NAMESPACE_END
#endif // !_VegFluorPHASE_H_

