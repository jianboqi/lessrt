#if !defined(__TOOLS_H_)
#define __TOOLS_H_
#include <iostream>
#include <fstream>
#include <string>
#include <sstream> 



#include <iomanip> 
#include <mitsuba/render/scene.h>
using namespace std;
MTS_NAMESPACE_BEGIN
#define TCACHE_DIRECT_FILE_NAME "Td.cache"
#define TCACHE_HO_FILE_NAME "Th"

void write2file(float*output, int width, int size, std::string filepath)
{
	ofstream out(filepath);
	for (int i = 1; i < size+1; i++)
	{
		out << output[i-1] << " ";
		if (i % width == 0)
			out << endl;
	}
	out.close();

}
string int2str(const int int_temp)
{
	string string_temp;
	stringstream stream;
	stream << int_temp;
	string_temp = stream.str();   //此处也可以用 stream>>string_temp  
	return string_temp;
}

//void cache_Th(std::vector<std::vector<Spectrum*> > &highorderTcoeffs, int bands)
//{
//	ofstream out(TCACHE_HO_FILE_NAME);
//	for (int h = 0; h < highorderTcoeffs.size(); h++)
//	{
//		for (int i = 0; i < highorderTcoeffs[h].size(); i++)
//		{
//			for (int j = 0; j < bands*bands; j++)
//			{
//				for (int b = 0; b < SPECTRUM_SAMPLES; b++)
//				{
//					out << highorderTcoeffs[h][i][j][b] << " ";
//				}
//			}
//			out << endl;
//		}
//		out << "new" << endl;
//	}
//	
//	out.close();
//}

//void read_cache_Th(std::vector<std::vector<Spectrum*> > &highorderTcoeffs, int bands)
//{
//	ifstream fin(TCACHE_HO_FILE_NAME, ios::in);
//	char line[500];
//	size_t lineIndex = 0;
//	int orderindex = 0;
//	string x;
//	while (fin.getline(line, sizeof(line)))
//	{
//		if (line == "new")
//		{
//			orderindex++;
//			lineIndex = 0;
//		}
//
//		stringstream words(line);
//		for (int j = 0; j < bands*bands; j++)
//		{
//			Spectrum s;
//			for (int i = 0; i < SPECTRUM_SAMPLES; i++)
//			{
//				words >> x;
//				s[i] = atof(x.c_str());
//			}
//			highorderTcoeffs[orderindex][lineIndex][j] = s;
//		}
//		lineIndex++;
//	}
//	fin.close();
//}


void cache_Td(std::vector<Spectrum*> &Tcoeffs, int bands, string output_file = TCACHE_DIRECT_FILE_NAME)
{
	ofstream out(output_file);
	out.setf(ios::fixed, ios::floatfield);  // 设定为 fixed 模式，以小数点表示浮点数  
	out.precision(6);  // 设置精度 2  
	for (int i = 0; i < Tcoeffs.size(); i++)
	{
		for (int j = 0; j < bands*bands; j++)
		{
			for (int b = 0; b < SPECTRUM_SAMPLES; b++)
			{
				out << Tcoeffs[i][j][b] << " ";
			}
		}
		out << endl;
	}
	out.close();
}

void read_cache_Td(std::vector<Spectrum*> &Tcoeffs, int bands, string input_file = TCACHE_DIRECT_FILE_NAME)
{
	std::ifstream fin(input_file, ios::in);
	char line[500];
	size_t lineIndex = 0;
	string x;
	while (fin.getline(line, sizeof(line)))
	{
		stringstream words(line);
		for (int j = 0; j < bands*bands; j++)
		{
			Spectrum s;
			for (int i = 0; i < SPECTRUM_SAMPLES; i++)
			{
				words >> x;
				s[i] = atof(x.c_str());
			}
			Tcoeffs[lineIndex][j] = s;
		}
		lineIndex++;
	}
	fin.close();
}

void cache_Th(std::vector<std::vector<Spectrum*> > &highorderTcoeffs, int bands)
{
	for (int h = 0; h < highorderTcoeffs.size(); h++)
	{
		std::string output_name = TCACHE_HO_FILE_NAME + int2str(h) + ".cache";
		cache_Td(highorderTcoeffs[h], bands, output_name);
	}
}

void read_cache_Th(std::vector<std::vector<Spectrum*> > &highorderTcoeffs, int bands)
{
	for (int h = 0; h < highorderTcoeffs.size(); h++)
	{
		std::string input_name = TCACHE_HO_FILE_NAME + int2str(h) + ".cache";
		cache_Td(highorderTcoeffs[h], bands, input_name);
	}
}



void write_Td(std::vector<Spectrum*> &Tcoeffs, int coeffCount, float scale = 1)
{
	ofstream out("Td.txt");
	for (int ii = 0; ii < Tcoeffs.size(); ii++)
	{
		for (int i = 0; i < coeffCount; i++)
		{
			for (int j = 0; j < SPECTRUM_SAMPLES; j++)
			{
				out << Tcoeffs[ii][i][j] << " ";
			}
		}
		out << endl;
	}
	out.close();
}

MTS_NAMESPACE_END
#endif