#include <mitsuba\render\util.h>
#include "../converter/converter.h"
#if defined(__WINDOWS__)
#include <mitsuba/core/getopt.h>
#endif

class ConsoleGeometryConverter : public GeometryConverter {
public:
	inline ConsoleGeometryConverter() {
	}

	fs::path locateResource(const fs::path &resource) {
		return fs::path();
	}
};

MTS_NAMESPACE_BEGIN

class OBJ2Serialized : public Utility
{
	int run(int argc, char **argv){
		cout << "hello world";
		/*ConsoleGeometryConverter converter;
		converter.convert(argv[optind], "", argv[optind + 1], argc > optind + 2 ? argv[optind + 2] : "");*/

		return 0;
	}
	MTS_DECLARE_UTILITY()
};
MTS_EXPORT_UTILITY(OBJ2Serialized, "Convert from Obj to serialized.")
MTS_NAMESPACE_END