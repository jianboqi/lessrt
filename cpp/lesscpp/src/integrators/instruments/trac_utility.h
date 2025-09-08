#pragma once
#ifndef TRAC_UTILITY_H_
#define TRAC_UTILITY_H_
#include <mitsuba/render/scene.h>
#include <vector>
MTS_NAMESPACE_BEGIN

class CircleBeamGridSampler {
public:
	CircleBeamGridSampler(int);
	void generate(); // precompute the samples
	void reset(); // start from 0 again
	Vector2 next();
	bool hasNext();
	int getSampleSize();
private:
	int m_n;
	Float m_d;
	int m_k;
	int m_nn;

	std::vector<Vector2> m_preGeneratedSamples;

};

CircleBeamGridSampler::CircleBeamGridSampler(int n) : m_n(n), m_d(2.0 / n), m_k(0), m_nn(n* n) {}

/// <summary>
/// precompute samples
/// </summary>
void CircleBeamGridSampler::generate() {
	for (int k = 0; k < m_nn; k++) {
		int i = k % m_n;
		int j = k / m_n;
		Float x = -1.0 + m_d * i;
		Float y = -1.0 + m_d * j;
		Vector2 v = Vector2(x, y);
		if (v.length() < 1.0 + Epsilon) {
			m_preGeneratedSamples.push_back(v);
		}
	}
}

void CircleBeamGridSampler::reset() {
	m_k = 0;
}

Vector2 CircleBeamGridSampler::next() {
	m_k++;
	return m_preGeneratedSamples[m_k];
}

int CircleBeamGridSampler::getSampleSize() {
	return  m_preGeneratedSamples.size();
}

bool CircleBeamGridSampler::hasNext() {
	return m_k < m_preGeneratedSamples.size();
}

MTS_NAMESPACE_END
#endif // !TRAC_UTILITY_H_

