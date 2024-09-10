#pragma once

#include <mitsuba/render/scene.h>
#include <vector>

MTS_NAMESPACE_BEGIN
const Float C = 299792458.0;

//const std::vector<int> wavelengths({ 361, 596 });

class CircleBeamGridSampler {
public:
	CircleBeamGridSampler(int);
	void generate(); // precompute the samples
	void reset(); // start from 0 again
	Vector2 next();
	bool hasNext();
	size_t getSize() const;
private:
	int m_n;
	Float m_d;
	int m_k;
	int m_nn;

	std::vector<Vector2> m_preGeneratedSamples;
};
extern Float gaussian(Float r, Float sigmaSquare);

MTS_NAMESPACE_END


