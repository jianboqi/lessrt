#pragma once
// providing some helper function for forward photon (path) tracing

#if !defined(_PHOTONRT_UTILS_)
#define _PHOTONRT_UTILS_
#include <cmath>
#include <vector>
using namespace std;

#define PHRT_M_PI 3.14159265358979323846

struct AngularDirection {
public:
	double center_zenith, center_azimuth; // rad
	double angleInterval; //rad

public:
	AngularDirection(){}
	AngularDirection(double center_zenith, double center_azimuth,
		double angleInterval) {
		this->center_zenith = center_zenith;
		this->center_azimuth = center_azimuth;
		this->angleInterval = angleInterval;
		costerm = std::cos(0.5*angleInterval);
		cx = std::sin(center_zenith)*std::cos(center_azimuth);
		cy = std::sin(center_zenith)*std::sin(center_azimuth);
		cz = std::cos(center_zenith);
	}
	double solidAngle() {
		double h = 1 - costerm;
		double a = std::sin(0.5*angleInterval);
		return PHRT_M_PI * (h*h + a * a);
	}
	//to determine if (zenith, azimuth) is inside this angular sector
	bool isInside(double zenith, double azimuth) {
		double x, y, z;
		x = std::sin(zenith)*std::cos(azimuth);
		y = std::sin(zenith)*std::sin(azimuth);
		z = std::cos(zenith);
		double dotproduct = cx * x + cy * y + cz * z;
		if (dotproduct >= costerm) {
			return true;
		}
		else {
			return false;
		}
	}

	std::string toString() {
		std::ostringstream oss;
		oss << "AngularDirection:[" << endl;
		oss << "Center Zenith: " << center_zenith << endl;
		oss << "Center Azimuth: " << center_azimuth << endl;
		oss << "Angle Interval: " << angleInterval << endl;
		oss << "Solid Angle: " << solidAngle() << endl;
		oss << "]" << endl;;
		return oss.str();
	}
protected:
	double costerm;
	double cx, cy, cz;
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