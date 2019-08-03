#include <mitsuba/render/scene.h>
#include "lidarutils.h"

MTS_NAMESPACE_BEGIN

CircleBeamGridSampler::CircleBeamGridSampler(int n) : m_n(n), m_d(2.0 / n), m_k(0), m_nn(n * n) {}

Vector2 CircleBeamGridSampler::next() {
	int i;
	int j;
	Float x;
	Float y;
	Vector2 v;

	for (; m_k < m_nn; m_k++) {
		i = m_k % m_n;
		j = m_k / m_n;
		x = -1.0 + m_d * i;
		y = -1.0 + m_d * j;
		v = Vector2(x, y);
		if (v.length() < 1.0) {
			m_k++;
			break;
		}
	}

	return v;
}

bool CircleBeamGridSampler::hasNext() {
	return m_k < m_nn;
}


MTS_NAMESPACE_END
