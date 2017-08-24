#ifndef __TOOLS_H_
#define __TOOLS_H_
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

namespace lesstool{

	//void writeArray2File(float * arr, int size, std::string filepath)
	//{
	//	ofstream out(filepath);
	//	for (int i = 0; i < size; i = i + 3)
	//	{
	//		out << arr[i] << " ";
	//		out << arr[i+1] << " ";
	//		out << arr[i+2] << " ";
	//		out << endl;
	//	}
	//	out.close();
	//}
	//
	vector< string> split(string str, string pattern)
	{
		vector<string> ret;
		if (pattern.empty()) return ret;
		size_t start = 0, index = str.find_first_of(pattern, 0);
		while (index != str.npos)
		{
			if (start != index)
				ret.push_back(str.substr(start, index - start));
			start = index + 1;
			index = str.find_first_of(pattern, start);
		}
		if (!str.substr(start).empty())
			ret.push_back(str.substr(start));
		return ret;
	}

	vector< float> split2float(string str, string pattern)
	{
		vector<float> ret;
		if (pattern.empty()) return ret;
		size_t start = 0, index = str.find_first_of(pattern, 0);
		while (index != str.npos)
		{
			if (start != index)
				ret.push_back(atof(str.substr(start, index - start).c_str()));
			start = index + 1;
			index = str.find_first_of(pattern, start);
		}
		if (!str.substr(start).empty())
			ret.push_back(atof(str.substr(start).c_str()));
		return ret;
	}


	void writeArray2File(float** data, int* num, int block_num, std::string filepath)
	{
		ofstream out(filepath);
		for (int i = 0; i < block_num; i++)
		{
			for (int j = 0; j < num[i] * 3; j = j + 3)
			{
				out << data[i][j] << " ";
				out << data[i][j + 2] << " ";
				out << data[i][j + 1] << " ";
				out << endl;
			}
		}
		out.close();
	}

}
#endif