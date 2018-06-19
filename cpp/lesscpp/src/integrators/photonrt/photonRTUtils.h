#pragma once
// providing some helper function for forward photon (path) tracing

#if !defined(_PHOTONRT_UTILS_)
#define _PHOTONRT_UTILS_
#include <cmath>
#include <vector>
using namespace std;

#define PHRT_M_PI 3.14159265358979323846

struct AngularDirection {
	double zenith_start, zenith_end;
	double azimuth_start, azimuth_end;
	double solidAngle;
public:
	AngularDirection(double zenith_start, double zenith_end,
		double azimuth_start,double azimuth_end,
		double solidAngle) {
		this->zenith_start = zenith_start;
		this->zenith_end = zenith_end;
		this->azimuth_start = azimuth_start;
		this->azimuth_end = azimuth_end;
		this->solidAngle = solidAngle;
	}
};

class PhotonRTUtils {
	/**
	* \brief partition the unit hemisphere into smaller patches with equal area
	* Ref: A general rule for disk and hemisphere partition into equal-area cells
	* \param NumberOfDirs
	*	Number of total directions
	*/
public:
	static void generationDiscreteDirections(int NumberOfDirs,
		vector<double> &accumulated_ZenithAngle, vector<vector<double>> &accumulated_azimuthAngle) {
		double r_i1 = 2 * std::sin(0.25*PHRT_M_PI);
		double theta_i1 = 0.5*PHRT_M_PI;
		int k_i1 = NumberOfDirs;

		double theta = 0, k = 0, r = 0;
		do {
			accumulated_ZenithAngle.insert(accumulated_ZenithAngle.begin(), theta_i1);
			theta = theta_i1 - 2 * std::sin(0.5*theta_i1)*std::sqrt(PHRT_M_PI / (double)k_i1);
			r = 2 * std::sin(0.5*theta);
			k = int(k_i1 * (r / r_i1)*(r / r_i1));
			//compute a new r and theta
			r = r_i1 * std::sqrt(k / (double)k_i1);
			theta = 2 * std::asin(0.5*r);

			int numOfDirectionInSector = k_i1 - k;
			double aziInterval = 2 * PHRT_M_PI / double(numOfDirectionInSector);
			vector<double> azi_each_sector;
			for (int i = 0; i < numOfDirectionInSector; i++) {
				double azimutStart = i * aziInterval;
				double azimuEnd = (i + 1)*aziInterval;
				double solidAngle = PHRT_M_PI * (r_i1*r_i1 - r * r) / (double)numOfDirectionInSector;
				//discreteDirections.push_back(new AngularDirection(theta, theta_i1, azimutStart, azimuEnd, solidAngle));
				azi_each_sector.push_back(azimuEnd);
			}
			accumulated_azimuthAngle.insert(accumulated_azimuthAngle.begin(), azi_each_sector);
			//update previous value
			k_i1 = k; r_i1 = r; theta_i1 = theta;
		} while (theta > 0);
	}
};

#endif