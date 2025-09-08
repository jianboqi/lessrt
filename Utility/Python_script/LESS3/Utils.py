# coding: utf-8
import numpy as np
from osgeo import gdal
import subprocess
import logging
import matplotlib.pyplot as plt
import os
import OpenEXR
import Imath
from scipy.stats import gaussian_kde
import xml.etree.ElementTree as ET

'''
Utils当前功能：
spherical_to_xyz_coords: 将球坐标转换为xyz坐标
load_RS_image: 加载ENVI遥感影像
save_image_as_envi: 将numpy三维数组保存为ENVI文件
numpy_to_exr: 将numpy三维数组保存为EXR文件
brf_image_pixel_scatter_plot: 绘制两个影像像素值的散点图
is_nvidia_gpu_present: 判断 nvidia gpu 是否可用
use_log: 使用日志记录信息
trans_LESS3_xml_correct: 用于将LESS3生成的xml文件中的<sensor>标签中的<to_world>更改正确,用main.xml修正LESS3.xml，将main.xml中的sensor的transform替换到LESS3.xml中的sensor的transform
custom_uv_generator: 自定义uv生成器

'''

class Utils(object):
    @staticmethod
    def spherical_to_xyz_coords(zenith_angle, azimuth_angle):
        """
        Convert a spherical coordinate to a xyz coordinates. 0 degree: north, 90 degree: east
        """
        theta = np.deg2rad(zenith_angle)
        phi = np.deg2rad(azimuth_angle)
        # x = np.sin(theta) * np.cos(phi)
        # z = np.sin(theta) * np.sin(phi)
        # y = -np.cos(theta)
        x = np.sin(theta) * np.sin(phi)
        z = -np.sin(theta) * np.cos(phi)
        y = -np.cos(theta)
        return [x, y, z]

    @staticmethod
    def load_RS_image(path):
        """
        加载ENVI遥感影像
        """
        data = gdal.Open(path)
        width = data.RasterXSize
        height = data.RasterYSize
        band_count = data.RasterCount
        # print('影像的波段数为：', band_count)
        # 读取图像数据
        image_data = np.zeros((height, width, band_count), dtype=np.float32)
        for i in range(band_count):
            band = data.GetRasterBand(i + 1)

            # description = band.GetDescription()
            # print(f"Band {i}: {description}")

            # 获取其他元数据
            band_data = band.ReadAsArray()
            image_data[:, :, i] = band_data

        # metadata = data.GetMetadata()
        # print(metadata)

        data = None
        # driver = gdal.GetDriverByName('PNG')
        # output_dataset = driver.CreateCopy('test.png', data)
        # output_dataset = None
        return image_data, height, width

    # save_image_as_envi是在反演实测数据时用的,不算通用
    @staticmethod
    def save_image_as_envi(image_data, file_path):
        # 创建ENVI格式的驱动
        driver = gdal.GetDriverByName('ENVI')
        # 获取影像的行列数和波段数===不通用
        rows, cols = image_data.shape[0], image_data.shape[1]
        bands = image_data.shape[2]
        # 创建新的ENVI文件
        out_dataset = driver.Create(file_path, cols, rows, bands, gdal.GDT_Float32)
        # 设置仿射变换参数和投影信息
        # out_dataset.SetGeoTransform(geotransform)
        # out_dataset.SetProjection(projection)
        # 写入数据
        for i in range(bands):
            out_band = out_dataset.GetRasterBand(i + 1)
            out_band.WriteArray(image_data[:, :, i])
            out_band.FlushCache()

        # 关闭文件
        out_dataset = None

    @staticmethod
    def downsample_average(image_data, scale_factor=2):
        '''
        对高光谱数据进行平均降采样
        :param
        image_data: 输入数据，形状为(height, width, bands)
        :param
        scale_factor: 降采样比例（整数），如2表示尺寸缩小为1 / 2
        :return: 降采样后的数据，形状为(height // scale_factor, width // scale_factor, bands)
        '''
        # 获取输入数据形状
        h, w, bands = image_data.shape

        # 计算输出形状，确保能被scale_factor整除
        new_h = h // scale_factor
        new_w = w // scale_factor

        # 重塑为分块格式 (new_h, scale_factor, new_w, scale_factor, bands)
        reshaped = image_data[:new_h * scale_factor, :new_w * scale_factor, :].reshape(new_h, scale_factor, new_w,
                                                                                       scale_factor, bands)

        # 对每个块计算平均值（沿scale_factor维度取平均）
        downsampled = reshaped.mean(axis=(1, 3))

        return downsampled

    @staticmethod
    def numpy_to_exr(numpy_array, exr_file_path):
        """
        将numpy三维数组保存为EXR文件

        :param numpy_array: 形状为 (height, width, channels) 的numpy数组
        :param exr_file_path: 保存EXR文件的路径
        """
        height, width, channels = numpy_array.shape

        # 创建EXR文件头
        header = OpenEXR.Header(width, height)

        # 定义通道数据类型，这里使用32位浮点数
        channel_type = Imath.PixelType(Imath.PixelType.FLOAT)

        # 设置每个通道的信息
        channel_data = {}
        for i in range(channels):
            channel_name = f"Band_{i + 1}"  # 动态生成通道名称，如 Band_1, Band_2,...
            channel_data[channel_name] = numpy_array[:, :, i].astype(np.float32).tobytes()
            header['channels'][channel_name] = Imath.Channel(channel_type)

        # 写入EXR文件
        # with OpenEXR.OutputFile(exr_file_path, header) as out_file:
        #     out_file.writePixels(channel_data)
        # 写入EXR文件
        out_file = OpenEXR.OutputFile(exr_file_path, header)
        try:
            out_file.writePixels(channel_data)
        finally:
            out_file.close()

    @staticmethod
    def brf_image_pixel_scatter_plot(reference_image, rendered_image, title="Comparison of Image Pixel Values", save_path=""):
        """
            绘制两个影像像素值的散点图，支持任意维度的图像。

            参数:
                reference_image (numpy.ndarray): 参考影像，任意维度的数组。
                rendered_image (numpy.ndarray): 渲染影像，任意维度的数组。
                title (str): 图表标题，默认为 "Comparison of Image Pixel Values"。

            注意：
                两个影像的形状必须相同。
        """
        # 检查影像形状是否一致
        if reference_image.shape != rendered_image.shape:
            raise ValueError("影像间的形状必须相同！")

        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score

        # 获取影像的像素值（展平所有维度）
        ref_pixels = reference_image.flatten()
        ren_pixels = rendered_image.flatten()

        min_val = min(ref_pixels.min(), ren_pixels.min())
        max_val = max(ref_pixels.max(), ren_pixels.max())

        use_gaosi = False

        # 计算数据点的密度 高斯
        if use_gaosi:
            values = np.vstack([ren_pixels, ref_pixels])
            kernel = gaussian_kde(values)
            density = kernel(values)


        # 绘制散点图
        plt.figure(figsize=(10, 10))
        plt.xlim(min_val, max_val)  # x轴的限制 散点图
        plt.ylim(min_val, max_val)  # y轴的限制
        # plt.scatter(ren_pixels, ref_pixels, color='blue', alpha=0.5, marker='.')  # label='estimated vs reference'
        # 高斯====
        if use_gaosi:
            scatter = plt.scatter(ren_pixels, ref_pixels, c=density, cmap='viridis', alpha=0.6, marker='.',
                                  edgecolor='none')
        else:
            temp_count = 10
            ren_pixels_scatter = ren_pixels
            ref_pixels_scatter = ref_pixels
            # 降采样，点数太多
            while len(ref_pixels_scatter) > 5000000:
                ren_pixels_scatter = ren_pixels[::temp_count]
                ref_pixels_scatter = ref_pixels[::temp_count]
                print("像素散点图降采样（散点过多）")
                temp_count *= 10
            plt.scatter(ren_pixels_scatter, ref_pixels_scatter, color='blue', alpha=0.5,
                        marker='.')  # label='estimated vs reference'


        # 计算R²值
        r2_score_value = r2_score(ref_pixels, ren_pixels)
        if r2_score_value > 0.9995:
            r2_score_value = 0.999
        # 计算线性回归函数
        model = LinearRegression()
        model.fit(ren_pixels.reshape(-1, 1), ref_pixels)  # 确保X是二维数组
        slope = model.coef_[0]  # 获取斜率
        intercept = model.intercept_  # 获取截距

        # 添加1:1线
        plt.plot([min_val, max_val], [min_val, max_val], color='green', linestyle='-', label='1:1 line')

        # 线性回归
        x_line = np.linspace(min_val, max_val, 100)
        y_line = slope * x_line + intercept
        plt.plot(x_line, y_line, color='red', linestyle='--',
                 label=f"y={slope:.3f}x{intercept:+.3f}, R\u00B2={r2_score_value:.3f}")

        # 添加图例
        from matplotlib.font_manager import FontProperties
        # 创建一个FontProperties对象来指定字体属性
        legend_props = FontProperties(family='Times New Roman', size=19)
        # 添加图例
        plt.legend(prop=legend_props)

        # 设置图表标题和坐标轴标签
        plt.title(title, font='Times New Roman', fontsize=30)
        # plt.title('Red Reflectance/Transmittance',font='Times New Roman', fontsize=30)
        plt.xlabel("Simulated Image", font='Times New Roman', fontsize=30)
        plt.ylabel("Reference/Measurement Image", font='Times New Roman', fontsize=30)
        plt.xticks(font='Times New Roman', fontsize=26)
        plt.yticks(font='Times New Roman', fontsize=26)
        # plt.axis('equal')
        # plt.grid(True)
        # 关闭所有图形窗口
        plt.savefig(save_path, dpi=600)
        # 显示图表
        # plt.show()
        plt.close()

        # plt.figure(figsize=(figsizex, figsizey))
        # plt.xlim(x_min, x_max)  # x轴的限制 散点图
        # plt.ylim(y_min, y_max)  # y轴的限制

    @staticmethod
    def image_diff_abs_plot(image1, image2, save_path):
        import matplotlib.cm as cm
        # 检查两个影像的形状是否一致
        if image1.shape != image2.shape:
            raise ValueError("两个影像的形状不一致")
        # 计算差的绝对值
        absolute_difference = np.abs(image1 - image2)
        # vmin = np.min(absolute_difference)
        vmax = np.max(absolute_difference)
        plt.imshow(np.clip(absolute_difference[:, :], 0, 1), cmap=cm.coolwarm, vmin=0, vmax=vmax)
        # 添加颜色条
        plt.colorbar(orientation='vertical')  # orientation参数控制颜色条的方向
        # look_pixel = 250
        # print("参考影像的像素值：", image_data[250, 100, :])
        # print("优化影像的像素值：", optimize_image[250, 100, :])
        # plt.title('image_rrmse_result')

        plt.axis('off')  # 一定要注意图像的范围大小，。。。。。。。。。。。。。。
        plt.savefig(save_path, dpi=600, bbox_inches='tight')  # 保存为PNG格式
        # plt.show()
        plt.close()



    @staticmethod
    def is_nvidia_gpu_present():
        """
        判断 nvidia gpu 是否可用
        """
        try:
            # 尝试执行nvidia-smi命令，并捕获输出
            subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            # 如果命令执行成功，说明NVIDIA GPU存在
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 如果命令执行失败，说明NVIDIA GPU不存在
            return False


    @staticmethod
    def use_log(log_path, log_name, level=logging.INFO):
        """
        使用日志记录信息
        """
        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        handler = logging.FileHandler(log_path + "/" + log_name + ".txt")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def trans_LESS3_xml_correct(xml_path):
        """
        用于将LESS3生成的xml文件中的<sensor>标签中的<to_world>更改正确,用main.xml修正LESS3.xml，将main.xml中的sensor的transform替换到LESS3.xml中的sensor的transform
        将LESS3.xml中的type=mixbsdf修改为blendbsdf，将reflectance和base_color的值乘以2
        """
        # 解析XML文件
        dir = os.path.dirname(xml_path)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        LESS_main_tree = ET.parse(dir + '/' + 'main.xml')
        LESS_main_root = LESS_main_tree.getroot()
        # 查找<sensor>标签
        sensor_tag = root.find('sensor')
        LESS_main_sensor_tag = LESS_main_root.find('sensor')
        # 查找<to_world>标签
        to_world_tag = sensor_tag.find('transform')
        LESS_main_to_world_tag = LESS_main_sensor_tag.find('transform')
        '''
        LESS3.xml中的<sensor>标签中的<to_world>标签的内容如下：
        <transform name="to_world">
            <rotate x="1" angle="89.999995674289"/>
            <rotate y="1" angle="3.5083540440521725e-15"/>
            <translate value="0.000000 3000.000000 0.000000"/>
        </transform>
        main.xml中的<sensor>标签中的<to_world>标签的内容如下：
        <transform name="toWorld">
            <scale x="310.0" y="310.0"/>
            <lookat origin="0.0,3000.0,0.0" target="0,0,0" up="0.00000,0,1.00000"/>
        </transform>
        '''
        # 将<to_world>标签的内容替换为main.xml中的<to_world>标签的内容
        to_world_tag.clear()
        for child in LESS_main_to_world_tag:
            to_world_tag.append(child)
        # 添加name="to_world"
        to_world_tag.set('name', 'to_world')


        '''
        LESS3.xml中的<bsdf>标签mixbsdf的内容如下：
        <bsdf type="mixbsdf" id="FREX_foliage_copy" name="FREX_foliage_copy">
            <bsdf type="twosided" name="twosided_id">
                <bsdf type="diffuse" name="diffuse_id1">
                    <texture type="irregular" name="reflectance">
                        <string name="wavelengths" value="442.948,490.448,560.4305,665.2445,681.556,709.1095,754.184,833.5,865.587,1242.5,1610.5,2120.0,2199.0"/>
                        <string name="values" value="0.048851,0.052006,0.105193,0.052954,0.051725,0.182420,0.498911,0.520089,0.521675,0.509786,0.420409,0.253921,0.269462"/>
                    </texture>
                </bsdf>
            </bsdf>
            <bsdf type="principledthin" name="principledthin_id">
                <texture type="irregular" name="base_color">
                    <string name="wavelengths" value="442.948,490.448,560.4305,665.2445,681.556,709.1095,754.184,833.5,865.587,1242.5,1610.5,2120.0,2199.0"/>
                    <string name="values" value="0.004224,0.008045,0.052475,0.011376,0.009375,0.121968,0.352701,0.375521,0.380813,0.392213,0.341348,0.228792,0.249032"/>
                </texture>
                <texture type="uniform" name="diff_trans">
                    <float name="value" value="2.000000"/>
                </texture>
                <integer name="specular_reflectance_sampling_rate" value="0"/>
                <integer name="specular_transmittance_sampling_rate" value="0"/>
                <texture type="uniform" name="roughness">
                    <float name="value" value="1.000000"/>
                </texture>
            </bsdf>
        </bsdf>
        
        '''

        # 查找<bsdf>标签，有很多个，需要找到所有type=mixbsdf的<bsdf>标签
        bsdf_tags = root.findall('bsdf')
        for bsdf_tag in bsdf_tags:
            if bsdf_tag.get('type') == 'mixbsdf':
                # 查找<bsdf>标签下的所有<bsdf>标签
                sub_bsdf_tags = bsdf_tag.findall('bsdf')
                for sub_bsdf_tag in sub_bsdf_tags:
                    if sub_bsdf_tag.get('type') == 'twosided':
                        # 查找<bsdf>标签下的所有<bsdf>标签
                        sub_sub_bsdf_tags = sub_bsdf_tag.findall('bsdf')
                        for sub_sub_bsdf_tag in sub_sub_bsdf_tags:
                            if sub_sub_bsdf_tag.get('type') == 'diffuse':
                                # 查找<bsdf>标签下的所有<texture>标签
                                texture_tags = sub_sub_bsdf_tag.findall('texture')
                                for texture_tag in texture_tags:
                                    if texture_tag.get('type') == 'irregular':
                                        # 查找<texture>标签下的所有<string>标签
                                        string_tags = texture_tag.findall('string')
                                        for string_tag in string_tags:
                                            if string_tag.get('name') == 'values':
                                                # 将<string>标签的value值乘以2
                                                string_tag.set('value', ','.join([str(float(value)*2) for value in string_tag.get('value').split(',')]))
                    elif sub_bsdf_tag.get('type') == 'principledthin':
                        # 查找<bsdf>标签下的所有<texture>标签
                        texture_tags = sub_bsdf_tag.findall('texture')
                        for texture_tag in texture_tags:
                            if texture_tag.get('type') == 'irregular':
                                string_tags = texture_tag.findall('string')
                                for string_tag in string_tags:
                                    if string_tag.get('name') == 'values':
                                        # 将<string>标签的value值乘以2
                                        string_tag.set('value', ','.join([str(float(value) * 2) for value in string_tag.get('value').split(',')]))
                # 将bsdf_tag修改为blendbsdf
                bsdf_tag.set('type', 'blendbsdf')
                # 在bsdf_tag下添加<float name="weight" value="0.5"/>
                weight_tag = ET.Element('float')
                weight_tag.set('name', 'weight')
                weight_tag.set('value', '0.5')
                bsdf_tag.append(weight_tag)



        # 保存修改后的XML文件,保存为LESS3_correct.xml
        tree.write(xml_path.replace('.xml', '_correct.xml'))
        print("LESS3_correct.xml文件已修改")

    @staticmethod
    def custom_uv_generator(input_obj, output_obj, texture_size=(100, 100), faces_per_texel=1):

        def read_obj(file_path):
            """读取OBJ文件的顶点和面（仅支持v和f指令）"""
            vertices = []  # 顶点坐标 (x,y,z)
            faces = []  # 面的顶点索引（0基）
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if parts[0] == 'v':
                        x, y, z = map(float, parts[1:4])
                        vertices.append((x, y, z))
                    elif parts[0] == 'f':
                        # 转换为0基索引（OBJ默认1基）
                        face_verts = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                        faces.append(face_verts)
            return vertices, faces

        def generate_uv_per_face(vertices, faces, texture_size=(100, 100), faces_per_texel=1):
            """
            为每个面生成唯一UV坐标，对应纹理数据中的单个纹素
            参数：
                vertices: 顶点列表
                faces: 面列表（每个面包含顶点索引）
                texture_size: 纹理尺寸 (H, W)，默认(100,100)
            返回：
                uv_coords: UV坐标列表 (u, v)
                uv_indices: 面的UV索引（与顶点索引对应）
            """
            H, W = texture_size
            num_faces = len(faces)

            # 计算需要的纹素数量
            if faces_per_texel <= 0:
                raise ValueError("faces_per_texel必须为正整数")

            # 如果每个纹素分配的面数大于总面数，则所有面共享1个纹素
            if faces_per_texel >= num_faces:
                num_texels_needed = 1
            else:
                # 向上取整计算需要的纹素数量
                num_texels_needed = (num_faces + faces_per_texel - 1) // faces_per_texel

            max_pixels = H * W
            # 检查所需纹素是否超过纹理容量
            if num_texels_needed > max_pixels:
                raise ValueError(
                    f"所需纹素数量({num_texels_needed})超过纹理最大容量({max_pixels})，请增大每个纹素分配的面数或增大纹理尺寸")

            uv_coords = []
            uv_indices = []
            mini_offset = [(-0.1/W, -0.1/H), (0.1/W, -0.1/H), (-0.1/W, 0.1/H), (0.1/W, 0.1/H)]
            # mini_offset = [(-0.4 / W, -0.4 / H), (0.4 / W, -0.4 / H), (0.4 / W, 0.4 / H), (-0.4 / W, 0.4 / H)]
            # mini_offset = [(-0.4 / W, 0.4 / H), (0.4 / W, 0.4 / H), (0.4 / W, -0.4 / H), (-0.4 / W, -0.4 / H)]

            for face_idx in range(num_faces):
                # 计算当前面所属的纹素组索引
                texel_group_idx = face_idx // faces_per_texel

                # 计算纹素索引 (i,j)（行优先）
                i = texel_group_idx // W  # 行索引（0~H-1）
                j = texel_group_idx % W  # 列索引（0~W-1）

                # 计算纹素中心的UV坐标
                u = (j + 0.5) / W  # 列→u轴，+0.5指向纹素中心
                v = (i + 0.5) / H  # 行→v轴，+0.5指向纹素中心

                # 当前面的顶点数量（3为三角形，4为四边形）
                face_verts = faces[face_idx]
                num_verts_in_face = len(face_verts)

                # 记录UV坐标（每个顶点使用带微小偏移的UV）
                base_uv_idx = len(uv_coords)
                for i in range(num_verts_in_face):
                    # uv_coords.append((u, v))
                    # offset = mini_offset[v_idx % len(mini_offset)]
                    uv_coords.append((u + mini_offset[i][0], v + mini_offset[i][1]))

                # 记录当前面的UV索引（与顶点索引顺序对应）
                uv_indices.append([base_uv_idx + k for k in range(num_verts_in_face)])

            return uv_coords, uv_indices

        def write_obj_with_uv(vertices, faces, uv_coords, uv_indices, output_path):
            """写入带UV坐标的OBJ文件"""
            with open(output_path, 'w') as f:
                # 写入顶点
                for v in vertices:
                    f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
                # 写入UV坐标（注意OBJ的v轴与纹理v轴相反，需翻转）
                for u, v in uv_coords:
                    f.write(f"vt {u:.6f} {1 - v:.6f}\n")  # 翻转v轴以匹配OBJ规范
                # 写入面（格式：顶点索引/UV索引）
                for face_verts, face_uvs in zip(faces, uv_indices):
                    face_str = "f "
                    for v_idx, uv_idx in zip(face_verts, face_uvs):
                        # OBJ索引为1基，需+1
                        face_str += f"{v_idx + 1}/{uv_idx + 1} "
                    f.write(face_str.strip() + "\n")

        vertices, faces = read_obj(input_obj)
        num_faces = len(faces)
        print(f"读取到 {len(vertices)} 个顶点，{len(faces)} 个面")

        try:
            # 确保faces_per_texel为正整数
            faces_per_texel = max(1, int(faces_per_texel))
            uv_coords, uv_indices = generate_uv_per_face(
                vertices, faces, texture_size, faces_per_texel)

            # 计算实际使用的纹素数量
            if faces_per_texel >= num_faces:
                used_texels = 1
            else:
                used_texels = (num_faces + faces_per_texel - 1) // faces_per_texel
            print(f"每个纹素分配 {faces_per_texel} 个面，共使用 {used_texels} 个纹素")

        except ValueError as e:
            print(f"错误：{e}")
            return

        write_obj_with_uv(vertices, faces, uv_coords, uv_indices, output_obj)
        print(f"已生成带UV的OBJ文件：{output_obj}")




    #
    # # 下面的函数用于测试
    # @staticmethod
    # def saveToHdr_no_transform(npArray, dstFilePath, wlist, output_format):
    #     dshape = npArray.shape
    #     if len(dshape) == 3:
    #         bandnum = dshape[2]
    #     else:
    #         bandnum = 1
    #     # 从hdrHeaderPath中提取投影信息
    #     if output_format == "ENVI":
    #         format = "ENVI"
    #     else:
    #         format = "GTiff"
    #         dstFilePath += ".tif"
    #     driver = gdal.GetDriverByName(format)
    #     dst_ds = driver.Create(dstFilePath, dshape[1], dshape[0], bandnum, gdal.GDT_Float32)
    #     #     npArray = linear_stretch_3d(npArray)
    #     if bandnum > 1:
    #         for i in range(1, bandnum + 1):
    #             dst_ds.GetRasterBand(i).WriteArray(npArray[:, :, i - 1])
    #     else:
    #         dst_ds.GetRasterBand(1).WriteArray(npArray)
    #     dst_ds = None
    #
    #     if output_format == "ENVI" and len(wlist) > 0:
    #         # wirte wavelength
    #         f = open(dstFilePath + ".hdr", 'r')
    #         text = f.read()
    #         f.close()
    #         wstr = "\nwavelength = {"
    #         for i in range(0, len(wlist)):
    #             wstr += wlist[i].split(":")[0] + ","
    #         wstr = wstr[0:len(wstr) - 1] + "}"
    #         f = open(dstFilePath + ".hdr", 'w')
    #         text = text + wstr
    #         f.write(text)
    #         f.close()
    #
    # # 下面的函数用于测试
    # @staticmethod
    # def radiance2brf(sim_dir, input_radiace_file="", output_brf_file=""):
    #     if input_radiace_file != "" and output_brf_file != "":
    #         sunirr = PostProcessing.readIrr(os.path.join(sim_dir, "Results", "Irradiance.txt"))
    #         if input_radiace_file == "" or output_brf_file == "":
    #             return
    #         else:
    #             if os.path.exists(input_radiace_file):
    #                 meanBRFs = PostProcessing.brf_single_img_processing(input_radiace_file, sunirr, output_brf_file)
    #     elif input_radiace_file == "" and output_brf_file == "":
    #         spectral_info_path = os.path.join(sim_dir, "Results", "spectral.txt")
    #         if os.path.exists(spectral_info_path):
    #             fs = open(spectral_info_path, "r")
    #             f = open(os.path.join(sim_dir, "Results", "spectral_BRF.txt"), 'w')
    #             sunirr = PostProcessing.readIrr(os.path.join(sim_dir, "Results", "Irradiance.txt"))
    #             for line in fs:
    #                 radiance_path = os.path.join(sim_dir, "Results", line)
    #                 if os.path.exists(radiance_path):
    #                     print("INFO: Processing Image: " + line)
    #                     output_file = radiance_path + "_BRF"
    #                     meanBRFs = PostProcessing.brf_single_img_processing(radiance_path, sunirr,
    #                                                                         output_file)  # mean BRF for each band
    #                     f.write(line + " ")
    #                     for i in range(0, len(meanBRFs)):
    #                         f.write("%.5f " % meanBRFs[i])
    #                     f.write("\n")
    #             f.close()
    #     else:
    #         print("Error: input or output file is not specified.")
    #         sys.exit()


if __name__ == '__main__':
    # test trans xml
    Utils.trans_LESS3_xml_correct(r"D:/LESS/LESS_project/scene/scene/MFGS-trans/Parameters/_scenefile/LESS3.xml")