#pragma once

#include <mitsuba/render/scene.h>
#include <vector>

MTS_NAMESPACE_BEGIN
const Float C = 299792458.0;

const std::vector<int> wavelengths({ 361, 596 });

class CircleBeamGridSampler {
public:
	CircleBeamGridSampler(int);
	Vector2 next();
	bool hasNext();
private:
	int m_n;
	Float m_d;
	int m_k;
	int m_nn;
};
extern Float gaussian(Float r, Float sigmaSquare);

MTS_NAMESPACE_END


