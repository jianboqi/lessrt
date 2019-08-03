#include "lidarutils.h"
#include <mitsuba/render/scene.h>

MTS_NAMESPACE_BEGIN

Float gaussian(Float r, Float sigmaSquare) {
	return std::exp(-0.5 * r * r / sigmaSquare);
}

MTS_NAMESPACE_END