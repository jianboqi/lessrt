#include <mitsuba/render/scene.h>
#include "lidarutils.h"

MTS_NAMESPACE_BEGIN

CircleBeamGridSampler::CircleBeamGridSampler(int n) : m_n(n), m_d(2.0 / n), m_k(0), m_nn(n * n) {}

/// <summary>
/// precompute samples
/// </summary>
void CircleBeamGridSampler::generate() {
	for (int k=0; k < m_nn; k++) {
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
	return m_preGeneratedSamples[m_k++];
}

bool CircleBeamGridSampler::hasNext() {
	return m_k < m_preGeneratedSamples.size();
}

size_t CircleBeamGridSampler::getSize() const {
	return m_preGeneratedSamples.size();
}


MTS_NAMESPACE_END
