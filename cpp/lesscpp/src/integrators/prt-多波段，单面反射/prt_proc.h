#if !defined(__PRT_PROC_H_)
#define __PRT_PROC_H_
#include <mitsuba/render/scene.h>

MTS_NAMESPACE_BEGIN

#define PI 3.141592653

struct Spherical
{
	float theta;
	float phi;
};
struct SHSample
{
	Spherical sph_coord;
	Vector3f cartesian_coord;
	float* sh_functions;
};

struct SHSampler
{
	SHSample* shsamples;
	int number_of_samples;
};

struct StoreVisibility
{
	int number_of_directions;//equals to number_of_samples
	bool *visibility; // if true, visibility = 1
	int *intersectionTriangle; //每个方向所交的三角形
};

float Random()
{
	float random = (float)(rand() % 1000) / 1000.0f;
	return random;
}
void SH_generate_samples(SHSampler* shsampler, int sqrt_n_samples)
{
	SHSample* shsamples = new SHSample[sqrt_n_samples*sqrt_n_samples];
	shsampler->shsamples = shsamples;
	shsampler->number_of_samples = sqrt_n_samples*sqrt_n_samples;
	double oneoverN = 1.0 / float(sqrt_n_samples);
	for (int i = 0; i < sqrt_n_samples; i++)
	{
		for (int j = 0; j < sqrt_n_samples; j++)
		{
			double xx = (i + Random()) * oneoverN; // do not reuse results
			double yy = (j + Random()) * oneoverN; // each sample must be random
			float theta = 2 * acos(sqrt(1 - xx));
			float phi = 2 * PI*yy;
			float x = -sin(theta)*cos(phi);
			float z = sin(theta)*sin(phi);
			float y = cos(theta);
			int k = i*sqrt_n_samples + j;
			shsampler->shsamples[k].sph_coord.theta = theta;
			shsampler->shsamples[k].sph_coord.phi = phi;
			shsampler->shsamples[k].cartesian_coord = Vector3f(x, y, z);
			shsampler->shsamples[k].sh_functions = NULL;
		}
	}
}

double P(int l, int m, double x)
{
	// evaluate an Associated Legendre Polynomial P(l,m,x) at x
	double pmm = 1.0;
	if (m > 0) {
		double somx2 = sqrt((1.0 - x)*(1.0 + x));
		double fact = 1.0;
		for (int i = 1; i <= m; i++) {
			pmm *= (-fact) * somx2;
			fact += 2.0;
		}
	}
	if (l == m) return pmm;
	double pmmp1 = x * (2.0*m + 1.0) * pmm;
	if (l == m + 1) return pmmp1;
	double pll = 0.0;
	for (int ll = m + 2; ll <= l; ++ll) {
		pll = ((2.0*ll - 1.0)*x*pmmp1 - (ll + m - 1.0)*pmm) / (ll - m);
		pmm = pmmp1;
		pmmp1 = pll;
	}
	return pll;
}

float factorial(int n)
{
	if (n <= 1)
		return(1);
	else
		return(n * factorial(n - 1));
}
double K(int l, int m)
{
	// renormalisation constant for SH function
	double temp = ((2.0*l + 1.0)*factorial(l - m)) / (4.0*PI*factorial(l + m));
	return sqrt(temp);
}
double SH(int l, int m, double theta, double phi)
{
	// return a point sample of a Spherical Harmonic basis function
	// l is the band, range [0..N]
	// m in the range [-l..l]
	// theta in the range [0..Pi]
	// phi in the range [0..2*Pi]
	const double sqrt2 = sqrt(2.0);
	if (m == 0) return K(l, 0)*P(l, m, cos(theta));
	else if (m>0) return sqrt2*K(l, m)*cos(m*phi)*P(l, m, cos(theta));
	else return sqrt2*K(l, -m)*sin(-m*phi)*P(l, -m, cos(theta));
}

void PrecomputeSHFunctions(SHSampler *shsampler, int bands)
{
	for (int i = 0; i < shsampler->number_of_samples; i++)
	{
		float* sh_functions = new float[bands*bands];
		shsampler->shsamples[i].sh_functions = sh_functions;
		float theta = shsampler->shsamples[i].sph_coord.theta;
		float phi = shsampler->shsamples[i].sph_coord.phi;
		for (int l = 0; l < bands; l++)
		{
			for (int m = -l; m <= l; m++)
			{
				int j = l*(l + 1) + m;
				sh_functions[j] = SH(l, m, theta, phi);
			}
		}
	}
}

Spectrum LightProbeAccess(Vector3f coord, const Scene* scene)
{
	RayDifferential ray;
	ray.setOrigin(Point(0, 0, 0));
	ray.setDirection(coord);
	Spectrum value = scene->evalEnvironment(ray);
	return value;
}

void projectLightintoSH(Spectrum* coeffs, SHSampler* shsampler, int bands, const Scene* scene) //only for one band
{
	for (int i = 0; i < bands*bands; i++)
	{
		coeffs[i] = Spectrum(0.0);
	}
	for (int i = 0; i < shsampler->number_of_samples; i++)
	{
		Vector3f& direction = shsampler->shsamples[i].cartesian_coord;
		Spectrum directionRadiance = LightProbeAccess(direction, scene);
		for (int j = 0; j < bands*bands; j++)
		{
			float sh_function = shsampler->shsamples[i].sh_functions[j];
			coeffs[j] += directionRadiance*sh_function;
		}
	}

	float weight = 4.0f*PI;
	float scale = weight / shsampler->number_of_samples;
	for (int i = 0; i < bands*bands; i++)
	{
		coeffs[i] *= scale;
	}
}

void envaluateLightProjectionAccuracy(Spectrum* coeffs, SHSampler* shsampler, int bands, const Scene* scene)
{
	Spectrum rmse = Spectrum(0.0);
	for (int i = 0; i < shsampler->number_of_samples; i++)
	{
		Vector3f& direction = shsampler->shsamples[i].cartesian_coord;
		Spectrum directionRadiance = LightProbeAccess(direction, scene);
		Spectrum estimatedRadiance_each_direction = Spectrum(0.0); // for envaluate the performance of SH for approximate light
		for (int j = 0; j < bands*bands; j++)
		{
			float sh_function = shsampler->shsamples[i].sh_functions[j];
			estimatedRadiance_each_direction += coeffs[j] * sh_function;
		}
		Spectrum diff = estimatedRadiance_each_direction - directionRadiance;
		rmse += diff*diff;
	}
	rmse /= shsampler->number_of_samples;
	rmse = rmse.sqrt();
	cout << "Income radiance estimation RMSE: ";
	for (int i = 0; i < SPECTRUM_SAMPLES; i++)
	{
		cout << rmse[i] << " ";
	}
	cout << endl;
}



void combine_coeffs(float* output, float ** Tcoeffs, float * lightCoeff, int triangleCount, int coeffCount, float scale = 1)
{
	for (int i = 0; i < triangleCount; i++)
	{
		output[i] = 0;
	}
	//ofstream out("T.txt");

	for (int i = 0; i < triangleCount; i++)
	{
		for (int j = 0; j < coeffCount; j++)
		{
			//		out << Tcoeffs[i][j] << " ";
			output[i] += Tcoeffs[i][j] * lightCoeff[j];
		}
		//	out << endl;
		output[i] *= scale;
	}
	//	out.close();
}

MTS_NAMESPACE_END
#endif