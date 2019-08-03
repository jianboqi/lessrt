/*
 * PulseGaussianFitting.cpp
 *
 *  Created on: 2017/12/6
 *      Author: Jianbo Qi
 */

#include "PulseGaussianFitting.h"
#include <math.h>
#include <iostream>
#define pi 3.141592653


vector<int> peaksDetectFisrtOrderZeroCrosssing(vector<double> y, double thres, int min_dist) {
    thres *= *max_element(y.begin(), y.end()) - *min_element(y.begin(), y.end());

    //first order difference
    vector<double> dy;
    for (size_t i = 1; i < y.size(); i++) {
        dy.push_back(y[i] - y[i - 1]);
    }

    vector<int> peaks;
    vector<double> peaks_amp;
    for(size_t i=0;i<dy.size()-1;i++){
        for(size_t j=i+1;j<dy.size();j++){
            if (dy[i] == 0) break;
            if(dy[j] !=0){
                if(dy[i] > 0 && dy[j] < 0 && y[i+1] > thres){
                    peaks.push_back(i+1);
                    peaks_amp.push_back(y[i+1]);
                }
                break;
            }
        }
    }

    //remove peaks which are too close to each other
    if (peaks.size() > 1 && min_dist > 1) {
        vector<bool> rem;
        for (size_t i = 0; i < y.size(); i++)
            rem.push_back(true);
        for (size_t i = 0; i < peaks.size(); i++)
            rem[peaks[i]] = false;

        vector<int> sorted_index = sort_indexes(peaks_amp);
        for (size_t i = 0; i < sorted_index.size(); i++) {
            int peaks_index = peaks[sorted_index[i]];
            if (!rem[peaks_index]) {
                int left = max(0, peaks_index - min_dist);
                int right = min((int)y.size() - 1, peaks_index + min_dist + 1);
                for (int j = left; j <= right; j++)
                    rem[j] = true;
                rem[peaks_index] = false;
            }
        }
        peaks.clear();
        for (size_t i = 0; i < y.size(); i++) {
            if (!rem[i]) {
                peaks.push_back(i);
            }
        }

    }
    return peaks;
}


//flexion points detection: used for estimating the parameters for each components
vector<vector<int>> flexion_detect(vector<double> y, vector<int> peaks) {
	vector<vector<int>> intervals;
	if (peaks.size() > 1) {
		for (size_t i = 0; i < peaks.size(); i++) {
			vector<int> interval;
			int peak_index = peaks[i];
			int li = peak_index;
			while (li > 0 && y[li - 1] <= y[li] && y[li - 1] != 0) {
				li -= 1;
			}
			int ri = peak_index;
			while (ri < (int)y.size() - 1 && y[ri + 1] <= y[ri] && y[ri + 1] != 0) {
				ri += 1;
			}
			interval.push_back(li);
			interval.push_back(ri);
			intervals.push_back(interval);
		}
	}
	else {
		vector<int> interval;
		interval.push_back(0);
		interval.push_back(y.size() - 1);
		intervals.push_back(interval);
	}
	return intervals;
}


double GaussianFunc(double x, double amp, double cen, double wid) {
    return (amp / (sqrt(2 * pi)*wid)) * exp(-(x - cen)*(x - cen) / (2 * wid*wid));
}


double CompositeGaussianFuncN(int number_of_peaks, double x, const double *par) {
    double re = 0;
    for (int i = 0; i < number_of_peaks; i++) {
        double amp = par[i*3 + 0];
        double cen = par[i*3 + 1];
        double wid = par[i*3 + 2];
        re += GaussianFunc(x, amp, cen, wid);
    }
    return re;
}

int GaussianSum(int m, int n, double *p, double *deviates,
	double **derivs, void *private_data) {
	int numPeaks = n / 3;
	/* Retrieve values of x, y and y_error from private structure */
	XYData* xydata = (XYData*)private_data;
	for (int i = 0; i < m; i++) {
		deviates[i] = (xydata->y[i] - CompositeGaussianFuncN(numPeaks, xydata->x[i], p)) / xydata->y_error[i];
	}
	return 0;
}

vector<double> guess(vector<double> x, vector<double> y) {
    vector<double>::iterator max_iterator = max_element(y.begin(), y.end());
    int index_maxy = distance(y.begin(), max_iterator);
    double maxy = *max_iterator;
    double miny = *min_element(y.begin(), y.end());
    double maxx = *max_element(x.begin(), x.end());
    double minx = *min_element(x.begin(), x.end());

    vector<double> par;
    double cen = x[index_maxy];
    double amp = (maxy - miny)*3.0;
    double wid = (maxx - minx) / 6.0;
    amp = amp*wid;

    par.push_back(amp);
    par.push_back(cen);
    par.push_back(wid);
    return par;
}
