#ifndef __TOOLS_H_
#define __TOOLS_H_
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

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
void writeArray2File(float** data, int* num, int block_num, std::string filepath)
{
	ofstream out(filepath);
	for (int i = 0; i < block_num; i++)
	{
		for (int j = 0; j < num[i]*3; j = j+3)
		{
			out << data[i][j] << " ";
			out << data[i][j+2] << " ";
			out << data[i][j+1] << " ";
			out << endl;
		}
	}
	out.close();
}

#endif