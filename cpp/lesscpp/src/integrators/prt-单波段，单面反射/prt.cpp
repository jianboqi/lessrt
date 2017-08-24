#include <mitsuba/render/scene.h>
#include <iostream>
#include <fstream>
#include <ctime>
#include "prt_proc.h"
#include "Tools.h"
#define _TIME_STATS_
MTS_NAMESPACE_BEGIN
class PRT :public MonteCarloIntegrator
{
public:
	PRT(const Properties &props) : MonteCarloIntegrator(props) {
#if SPECTRUM_SAMPLES != 3
		m_NoDataValue = props.getFloat("NoDataValue", -1.0);
#endif
		m_shbands = 1;

		m_forceRecal = props.getBoolean("ForceRecal", false);
		m_maxOrder = props.getInteger("maxOrder", 3);
	}


	PRT(Stream *stream, InstanceManager *manager)
		: MonteCarloIntegrator(stream, manager) {
	}
	/// Serialize to a binary data stream
	void serialize(Stream *stream, InstanceManager *manager) const {
		MonteCarloIntegrator::serialize(stream, manager);
	}

	void do_precomputing(const Scene * scene)
	{
		//cout << lightCoeffs[0] << endl;
		//cout << lightCoeffs[0] * SH(0, 0, 0, 0) << endl;
		ProjectShadowed(scene);
	}

	bool preprocess(const Scene *scene, RenderQueue *queue, const RenderJob *job,
		int sceneResID, int sensorResID, int samplerResID) {
		Integrator::preprocess(scene, queue, job, sceneResID, sensorResID, samplerResID);
		// compute transfer vector
#ifdef _TIME_STATS_
		clock_t start, finish;
		double totaltime;
		start = clock();
#endif
		//srand(time(NULL));
		m_totalTriangleCount = this->getTrianbleCount(scene);
		// for each triangle, store a arra of coeffs.
		numbering_triangles(scene);
		shsampler = new SHSampler();
		SH_generate_samples(shsampler, 10);
		PrecomputeSHFunctions(shsampler, m_shbands);
		Tcoeffs = new float*[m_totalTriangleCount];
		lightCoeffs = new float[m_shbands*m_shbands];
		for (int i = 0; i < m_totalTriangleCount; i++)
		{
			Tcoeffs[i] = new float[m_shbands*m_shbands];
			for (int j = 0; j < m_shbands*m_shbands; j++)
			{
				Tcoeffs[i][j] = 0.0f;
			}
		}
		projectLightintoSH(lightCoeffs, shsampler, m_shbands, scene);
		//store visibility
		visibilities = new StoreVisibility[m_totalTriangleCount];
		for (int i = 0; i < m_totalTriangleCount; i++)
		{
			visibilities[i].number_of_directions = shsampler->number_of_samples;
			visibilities[i].visibility = new bool[shsampler->number_of_samples];
			visibilities[i].intersectionTriangle = new int[shsampler->number_of_samples];
		}

		highorderTcoeffs.reserve(m_maxOrder);
		//high order inilize
		for (int o = 0; o < m_maxOrder; o++)
		{
			highorderTcoeffs[o] = new float*[m_totalTriangleCount];
			for (int i = 0; i < m_totalTriangleCount; i++)
			{
				highorderTcoeffs[o][i] = new float[m_shbands*m_shbands];
				for (int j = 0; j < m_shbands*m_shbands; j++)
				{
					highorderTcoeffs[o][i][j] = 0.0f;
				}
			}
		}

		if (!m_forceRecal) //不强制计算
		{
			//首先判断是否有文件,若有则读取，若没有则计算再缓存
			fstream _file;
			_file.open(TCACHE_FILE_NAME, ios::in);
			if (!_file) //没有文件
			{
				cout << "No precomputed data found." << endl;
				do_precomputing(scene);
				cache_T(Tcoeffs, m_totalTriangleCount, m_shbands);
			}
			else
			{
				cout << "Precomputed data found." << endl;
				cout << "Start to reading..." << endl;
				read_cache_T(Tcoeffs, m_totalTriangleCount, m_shbands);
				cout << "Reading completed." << endl;
			}
		}
		else
		{
			cout << "Force to precompute." << endl;
			do_precomputing(scene);
			cache_T(Tcoeffs, m_totalTriangleCount, m_shbands);
		}

		if (m_maxOrder > 1)
		{
			cout << "High order scattering computing." << endl;
			for (int i = 1; i < m_maxOrder; i++)
			{
				if (i == 1)
				{
					HighOrderPrecomputing(scene, Tcoeffs, highorderTcoeffs[i-1]);
				}
				else
				{
					HighOrderPrecomputing(scene, highorderTcoeffs[i-2], highorderTcoeffs[i-1]);
				}
					
			}
			cout << "High order scattering completed." << endl;
		}
		
		



		//float *output = new float[triangleCount];
		//combine_coeffs(output, Tcoeffs, lightCoeffs, triangleCount, m_shbands*m_shbands);
		//write2file(output, 200, triangleCount, "output.txt");
		/*std::string filepath = "points.txt";
		std::ofstream out(filepath);

		out.close();*/
		/*delete[]lightCoeffs;
		for (int i = 0; i < this->getTrianbleCount(scene); i++)
		{
			delete[] Tcoeffs[i];
		}*/
#ifdef _TIME_STATS_
		finish = clock();
		totaltime = (double)(finish - start) / CLOCKS_PER_SEC;
		cout << "Precomputing costs " << totaltime << " seconds！" << endl;
#endif




		return true;
	}

	size_t getTrianbleCount(const Scene *scene)
	{
		size_t triangle_count = 0;
		std::vector<TriMesh*> trismeshs = scene->getMeshes();
		for (int i = 0; i < trismeshs.size(); i++)
		{
			TriMesh* trimesh = trismeshs[i];
			triangle_count += trimesh->getTriangleCount();
		}
		return triangle_count;
	}

	void numbering_triangles(const Scene *scene)
	{
		size_t triIndex = 0;
		std::vector<TriMesh*> trismeshs = scene->getMeshes();
		for (int i = 0; i < trismeshs.size(); i++)
		{
			TriMesh* trimesh = trismeshs[i];
			Triangle * trilist = trimesh->getTriangles();
			for (int j = 0; j < trimesh->getTriangleCount(); j++)
			{
				Triangle &tri = trilist[j];
				tri.t_idx = triIndex;
				triIndex++;
			}
		}
	}

	Normal ComputeTriNormal(Point p0, Point p1, Point p2)
	{
		Vector sideA = p1 - p0, sideB = p2 - p0;
		return  normalize(Normal(normalize(cross(sideA, sideB))));
	}

	float dot(Normal n, Vector v)
	{
		return n.x*v.x + n.y*v.y + n.z*v.z;
	}

	inline float max(float a, float b)
	{
		if (a >= b)
		{
			return a;
		}
		else
		{
			return b;
		}
	}
	void ProjectShadowed(const Scene *scene)
	{
		std::vector<TriMesh*> trismeshs = scene->getMeshes();
		for (int i = 0; i < trismeshs.size(); i++)
		{
			TriMesh* trimesh = trismeshs[i];
			size_t triangleCount = trimesh->getTriangleCount();
			Triangle * trilist = trimesh->getTriangles();
			Point* vertexs = trimesh->getVertexPositions();
			const BSDF *bsdf = trimesh->getBSDF();
#pragma omp parallel for
			for (int j = 0; j < triangleCount; j++)
			{
				Triangle &tri = trilist[j];
				size_t triIndex = tri.t_idx;
				Point center_point = (vertexs[tri.idx[0]] + vertexs[tri.idx[1]] + vertexs[tri.idx[2]]) / 3.0;
				//out << center_point[0] << " " << center_point[1] << " " << center_point[2] << endl;
				Normal triNormal = ComputeTriNormal(vertexs[tri.idx[0]], vertexs[tri.idx[1]], vertexs[tri.idx[2]]);
				for (int s = 0; s < shsampler->number_of_samples; s++)
				{
					//cout << s << endl;
					SHSample shsample = shsampler->shsamples[s];
					//测试相交，visibility
					Ray ray;
					ray.setOrigin(center_point);
					ray.setDirection(shsample.cartesian_coord);
					Intersection its;
					bool isIntersected = scene->rayIntersect(ray, its); 
					visibilities[triIndex].visibility[s] = (!isIntersected);
					if (!isIntersected)
					{
						float cosine_term = max(0,dot(triNormal, shsample.cartesian_coord));
						for (int k = 0; k < m_shbands*m_shbands; k++)
						{
							float sh_function = shsample.sh_functions[k];
							Intersection its_tmp;
							its_tmp.p = center_point;
							BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, 1), Vector(0, 0, 1));
							bRecref.typeMask = bsdf->EDiffuseReflection;
							Spectrum ref = bsdf->eval(bRecref);
							Tcoeffs[triIndex][k] += ref[0]*sh_function*cosine_term;
						}
					}
					else
					{
						//保存相交的三角形，为高次散射计算所使用
						const TriMesh *trimeshtmp = static_cast<const TriMesh *>(its.shape);
						const Triangle &tritmp = trimeshtmp->getTriangles()[its.primIndex];
						visibilities[triIndex].intersectionTriangle[s] = tritmp.t_idx;
					}
				}
			}
		}
		float weight = 4.0f*PI;
		//float weight = 1;
		float scale = weight / shsampler->number_of_samples;
		for (int i = 0; i < m_totalTriangleCount; i++)
		{
			for (int j = 0; j < m_shbands*m_shbands; j++)
			{
				Tcoeffs[i][j] *= scale;
			}
		}
	}

	// compute nextOrder from preOrder
	void HighOrderPrecomputing(const Scene* scene, float** preOrder, float **nextOrder)
	{
		std::vector<TriMesh*> trismeshs = scene->getMeshes();
		for (int i = 0; i < trismeshs.size(); i++)
		{
			TriMesh* trimesh = trismeshs[i];
			size_t triangleCount = trimesh->getTriangleCount();
			Triangle * trilist = trimesh->getTriangles();
			Point* vertexs = trimesh->getVertexPositions();
			const BSDF *bsdf = trimesh->getBSDF();
#pragma omp parallel for
			for (int j = 0; j < triangleCount; j++)
			{
				Triangle &tri = trilist[j];
				size_t triIndex = tri.t_idx;
				Point center_point = (vertexs[tri.idx[0]] + vertexs[tri.idx[1]] + vertexs[tri.idx[2]]) / 3.0;
				//out << center_point[0] << " " << center_point[1] << " " << center_point[2] << endl;
				Normal triNormal = ComputeTriNormal(vertexs[tri.idx[0]], vertexs[tri.idx[1]], vertexs[tri.idx[2]]);
				for (int s = 0; s < shsampler->number_of_samples; s++)
				{
					SHSample shsample = shsampler->shsamples[s];
					size_t intersectedTriIdx = visibilities[triIndex].intersectionTriangle[s];
					float cosine_term = max(0, dot(triNormal, shsample.cartesian_coord));
					bool directionVisibility = !visibilities[triIndex].visibility[s];
					if (directionVisibility)
					{
						for (int k = 0; k < m_shbands*m_shbands; k++)
						{
							Intersection its_tmp;
							its_tmp.p = center_point;
							BSDFSamplingRecord bRecref(its_tmp, Vector(0, 0, 1), Vector(0, 0, 1));
							bRecref.typeMask = bsdf->EDiffuseReflection;
							Spectrum ref = bsdf->eval(bRecref);
							nextOrder[triIndex][k] += ref[0] * preOrder[intersectedTriIdx][k] * cosine_term;
						}
					}
					
				}
			}
		}

		float weight = 4.0f*PI;
		//float weight = 1;
		float scale = weight / shsampler->number_of_samples;
		for (int i = 0; i < m_totalTriangleCount; i++)
		{
			for (int j = 0; j < m_shbands*m_shbands; j++)
			{
				nextOrder[i][j] *= scale;
			}
		}

	}


	Spectrum Li(const RayDifferential &r, RadianceQueryRecord &rRec) const {
		/* Some aliases and local variables */
		const Scene *scene = rRec.scene;
		Intersection &its = rRec.its;
		RayDifferential ray(r);
		Spectrum Li(0.0f);

		/* Perform the first ray intersection (or ignore if the
		intersection has already been provided). */
		rRec.rayIntersect(ray);
		ray.mint = Epsilon;

		if (!its.isValid()) { //no intersection
			
				if (m_hideEmitters)
				{
					#if SPECTRUM_SAMPLES != 3
						Li = Spectrum(m_NoDataValue);
					#else
						Li = Spectrum(0);
					#endif
				}
				else
				{
					Li += scene->evalEnvironment(ray);
				}
		}
		else
		{
			const TriMesh *trimesh = static_cast<const TriMesh *>(its.shape);
			const Triangle &tri = trimesh->getTriangles()[its.primIndex];
			/*const Point* vertexs = trimesh->getVertexPositions();
			ofstream out("intersected.txt", ios::app);
			Point center_point = (vertexs[tri.idx[0]] + vertexs[tri.idx[1]] + vertexs[tri.idx[2]]) / 3.0;
			out << center_point.x << " " << center_point.y << " " << center_point.z << endl;
			out.close();*/
			float *tranCoeff = Tcoeffs[tri.t_idx];
			float radiance = 0;
			for (int i = 0; i < m_shbands*m_shbands; i++)
			{
				radiance += tranCoeff[i] * lightCoeffs[i];
			}
			Li += Spectrum(radiance);

			//high order scattering
			if (m_maxOrder > 1)
			{
				for (int i = 0; i < m_maxOrder; i++)
				{
					float *tranCoeff = highorderTcoeffs[i][tri.t_idx];
					float radiance = 0;
					for (int j = 0; j < m_shbands*m_shbands; j++)
					{
						radiance += tranCoeff[j] * lightCoeffs[j];
					}
					Li += Spectrum(radiance);
				}
			}

			
		}
		return Li;
	}

	void cancel() {
		Scheduler::getInstance()->cancel(m_process);
	}
	~PRT()
	{
		delete[]lightCoeffs;


		for (int i = 0; i < m_totalTriangleCount; i++)
		{
		delete[] Tcoeffs[i];
		}

		for (int i = 0; i < m_totalTriangleCount; i++)
		{
			delete[] visibilities[i].visibility;
			delete[] visibilities[i].intersectionTriangle;
		}


		for (int o = 0; o < m_maxOrder; o++)
		{
			for (int i = 0; i < m_totalTriangleCount; i++)
			{
				delete[] highorderTcoeffs[o][i];
			}
		}
	}

	MTS_DECLARE_CLASS()
private:
	ref<ParallelProcess> m_process;
	float * lightCoeffs;
	float** Tcoeffs; //first order
	std::vector<float **> highorderTcoeffs; // larger than 1st order
	StoreVisibility *visibilities;// a list to store visibility for each triangle.
	int m_shbands;
	bool m_forceRecal;
	size_t m_totalTriangleCount;
	SHSampler* shsampler;
	int m_maxOrder; //最大散射次数 最少为1

#if SPECTRUM_SAMPLES != 3
protected:
	float m_NoDataValue;
#endif
};
MTS_IMPLEMENT_CLASS_S(PRT, false, MonteCarloIntegrator)
MTS_EXPORT_PLUGIN(PRT, "PRT Model");
MTS_NAMESPACE_END