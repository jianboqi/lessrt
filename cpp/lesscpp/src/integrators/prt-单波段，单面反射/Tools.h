#ifndef __TOOLS_H_
#define __TOOLS_H_
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <iomanip> 
using namespace std;

#define TCACHE_FILE_NAME "T.cache"

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

void cache_T(float** Tcoeffs, int size, int bands)
{
	ofstream out(TCACHE_FILE_NAME);
	for (int i = 0; i < size; i++)
	{
		for (int j = 0; j < bands*bands; j++)
		{
			out << Tcoeffs[i][j] << " ";
		}
		out << endl;
	}
	out.close();
}

void read_cache_T(float** Tcoeffs, int size, int bands)
{
	std::ifstream fin(TCACHE_FILE_NAME, ios::in);
	char line[500];
	int lineindex = 0;
	string x;
	while (fin.getline(line, sizeof(line)))
	{
		stringstream words(line);
		for (int j = 0; j < bands*bands; j++)
		{
			words >> x;
			Tcoeffs[lineindex][j] = atof(x.c_str());
		}
		lineindex++;
	}

}


#endif