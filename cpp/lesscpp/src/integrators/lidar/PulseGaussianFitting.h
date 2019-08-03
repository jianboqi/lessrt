/*
 * PulseGaussianFitting.h
 *
 *  Created on: 2017/12/5
 *      Author: Jianbo Qi
 */

#ifndef PULSE_GAUSSIAN_FITTING_H_
#define PULSE_GAUSSIAN_FITTING_H_
#include <vector>
#include <algorithm>
using namespace std;

struct XYData {
	double *x;
	double *y;
	double *y_error;
};

/*
* Basic sort function used to sort a vector and return the indices
*/
template <typename T>
vector<int> sort_indexes(const vector<T> &v) {

    // initialize original index locations
    vector<int> idx(v.size());
    for (size_t i = 0; i < idx.size(); i++) {
        idx[i] = i;
    }
    // sort indexes based on comparing values in v
    sort(idx.begin(), idx.end(),
        [&v](int i1, int i2) {return v[i1] > v[i2]; });

    return idx;
}

/*
* y:        1D amplitude data to search for peaks.
* thres:    between [0., 1.]
            Normalized threshold. Only the peaks with amplitude higher than the
            threshold will be detected.
* min_dist: Minimum distance between each detected peak. The peak with the highest
            amplitude is preferred to satisfy this constraint.
*/
vector<int> peaksDetectFisrtOrderZeroCrosssing(vector<double> y, double thres = 0.1, int min_dist = 5);

vector<double> remove_dulplicate(vector<double> y);

//flexion points detection: used for estimating the parameters for each components
vector<vector<int>> flexion_detect(vector<double> y, vector<int> peaks);

// par[0]: amp; par[1]: cen; par[2]: wid
double GaussianFunc(double x, double amp, double cen, double wid);


/* A composite version of Gaussian function with N components
*  par: [amp1, cen1, wid1, amp2, cen2, wid2,...]
*/
double CompositeGaussianFuncN(double x, const double *par);


/**
 * Gaussian function for mpfit
 */
int GaussianSum(int m, int n, double *p, double *deviates,
		double **derivs, void *private_data);

// guess initial parameters for a peak: amp, cen, wid
vector<double> guess(vector<double> x, vector<double> y);

#endif /* PULSE_GAUSSIAN_FITTING_H_ */
