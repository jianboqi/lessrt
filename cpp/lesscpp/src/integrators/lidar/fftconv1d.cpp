#include <stdio.h>
#include <string.h>
#include <algorithm>
#include <math.h>
#include <vector>

using namespace std;

const double PI = acos(-1.0);
const double eps = 1e-20;

double add(const double &a, const double &b) {
	if (abs(a + b) < eps * (abs(a) + abs(b))) return 0;
	return a + b;
}

/* kuangbin */
struct Complex {
	double x, y;
	Complex(double _x = 0.0, double _y = 0.0) {
		x = _x;
		y = _y;
	}
	Complex operator -(const Complex &b) const {
		return Complex(add(x, -b.x), add(y, -b.y));
	}
	Complex operator +(const Complex &b)const
	{
		return Complex(add(x, b.x), add(y, b.y));
	}
	Complex operator *(const Complex &b)const
	{
		return Complex(add(x*b.x, -y * b.y), add(x*b.y, y*b.x));
	}
};

void change(Complex y[], int len)
{
	int i, j, k;
	for (i = 1, j = len / 2; i < len - 1; i++)
	{
		if (i < j)swap(y[i], y[j]);
		k = len / 2;
		while (j >= k)
		{
			j -= k;
			k /= 2;
		}
		if (j < k)j += k;
	}
}

/*
* FFT
* len must be 2^k
* on==1 DFT, on==-1 IDFT
*/
void fft(Complex y[], int len, int on)
{
	change(y, len);
	for (int h = 2; h <= len; h <<= 1)
	{
		Complex wn(cos(-on * 2 * PI / h), sin(-on * 2 * PI / h));
		for (int j = 0; j < len; j += h)
		{
			Complex w(1, 0);
			for (int k = j; k < j + h / 2; k++)
			{
				Complex u = y[k];
				Complex t = w * y[k + h / 2];
				y[k] = u + t;
				y[k + h / 2] = u - t;
				w = w * wn;
			}
		}
	}
	if (on == -1)
		for (int i = 0; i < len; i++)
			y[i].x /= len;
}

/* conv */
template <typename T>
vector<T> conv(const vector<T> &s1, const vector<T> &s2, const std::string &mode = "same") {
	int len1 = s1.size();
	int len2 = s2.size();

	int len = 1;

	while (len < len1 * 2 || len < len2 * 2) len <<= 1;

	//cout << "fftconv1d" << endl;
	//cout << "len1 = " << len1 << endl;
	//cout << "len2 = " << len2 << endl;
	//cout << "len = " << len << endl;

	vector<Complex> x1, x2;
	for (int i = 0; i < len1; i++) {
		x1.push_back(Complex(s1[i], 0));
	}
	for (int i = len1; i < len; i++) {
		x1.push_back(Complex(0, 0));
	}
	for (int i = 0; i < len2; i++) {
		x2.push_back(Complex(s2[i], 0));
	}
	for (int i = len2; i < len; i++) {
		x2.push_back(Complex(0, 0));
	}
	// DFT
	fft(x1.data(), len, 1);
	fft(x2.data(), len, 1);
	for (int i = 0; i < len; i++) {
		x1[i] = x1[i] * x2[i];
	}
	fft(x1.data(), len, -1);

	vector<T> sum;
	if (mode == "same") {
		for (int i = len2 / 2; i < len2 / 2 + len1; i++) {
			//sum.push_back(fabs(x1[i].x < eps) ? 0 : x1[i].x);
			// TODO small -> zero
			sum.push_back(x1[i].x);
		}
		sum.resize(len1);
	}
	return sum;
}
