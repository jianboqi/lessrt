import os
import pandas as pd
import numpy as np

class DiffRenderConfig():
    def __init__(self):
        self.init_epoch = 0  # 初始轮
        self.stop_epoch = 100  # 终止轮
        self.initial_learning_rate = 0.1  # 学习率
        self.optimize_spp = 1024  # 优化时渲染的采样数
        self.ref_brf_image_path = ""  # 参考的brf影像路径,也可写成列表["","","",""]
        self.result_dir_path = ""  # 输出结果的路径
        self.shuffle_spectral_values = True  # 是否随机初始的待反演参数
        self.shuffle_value_range = []  # 如果为空，则使用默认的随机初始化参数, 0.1-0.2
        self.resume = False  # 是否加载上次的结果
        self.resume_xlsx_name = ""  # 加载上次结果的xlsx路径
        self.optmize_params = []  # 待反演的参数，可以从LESS界面中挑选待反演参数
        self.is_oepn_comparison_between_opt_and_origin = False  # 是否打开原本初始的参数与待反演参数的过程比较
        self.use_field_data_simplify_opt = False  # 实测数据反演时选择是否简化优化，一般使用实测数据时，并且对于叶子这种有透射率的，将这个选项改为True,则将透射率限制在反射率周围,简化模型(减少受误差的影响)
        self.simplify_opt_limit = [0.05, 0.05] # 格式为[0.1,0.1](下限和上限),只有use_field_data_simplify_opt=True可用
        self.image_bands_show = [] # 如果设置了，会读取该列表的前三个值作为RGB显示影像，如果没设置，会默认前三个波段或单波段
        self.image_diff_abs_bands = [] # 若为空，则不生成，输入0,1,2,3可以生成第0，1，2，3波段影像的差的绝对值。

        # 多角度反演会用到
        # 正射相机：[[天顶角1,方位角1],[天顶角2,方位角2],[天顶角3,方位角3]],与LESS里Observation设置一致,目前不支持调整高度
        self.sensor_observation_Zenith_Azimuth = []
        # 透视相机：[[camera_position_x,camera_position_y,camera_position_z,target_x, target_y, target_z],
        # [camera_position_x1,camera_position_y1,camera_position_z1,target_x1, target_y1, target_z1]]
        self.sensor_observation_perspective = []


        pass

    @staticmethod
    def plot_every_band_result_test_city(result_dir, true_params_path, optimize_params_path):
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        df1 = pd.read_excel(true_params_path)
        df2 = pd.read_excel(optimize_params_path)

        # 获取每列标题
        column_titles = df1.columns.tolist()

        # 获取总共的标题个数
        num_columns = len(column_titles)

        # 获取每列的长度
        column_lengths = df1.apply(len).tolist()
        band_num = column_lengths[0]

        # 打印每列标题及其对应的长度
        for title, length in zip(column_titles, column_lengths):
            print(f"{title}: {length}")

        if not all(x == column_lengths[0] for x in column_lengths):
            raise ValueError("Column lengths do not match")

        # 打印每列标题及总共的标题个数
        # print("每列标题：", column_titles)
        # print("总共的标题个数：", num_columns)

        true_params = np.zeros((num_columns, column_lengths[0]))
        optimized_params = np.zeros((num_columns, column_lengths[0]))

        for i in range(num_columns):
            true_params[i] = (df1[column_titles[i]]).values
            optimized_params[i] = (df2[column_titles[i]]).values

        x_min = 0.0
        x_max = 1.0
        y_min = 0.0
        y_max = 1.0
        figsizex = 10
        figsizey = 8
        import matplotlib.pyplot as plt
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        # 每个波段的，这个好像没什么必要======================================
        # for k in range(band_num):
        #     optimized_reflectance = np.array(optimized_params[1:, k])  # 用您的数据替换这里的 这里表示把波段的一列去掉，获得其他的数据
        #     reference_reflectance = np.array(true_params[1:, k])  # 用您的数据替换这里的
        #
        #     plt.figure(figsize=(figsizex, figsizey))
        #     plt.xlim(x_min, x_max)  # x轴的限制 散点图
        #     plt.ylim(y_min, y_max)  # y轴的限制
        #
        #     # 计算R²值
        #     r2_score_value = r2_score(reference_reflectance, optimized_reflectance)
        #     if r2_score_value > 0.9995:
        #         r2_score_value = 0.999
        #     print(f"band:{k+1}")
        #     # 打印R²值
        #     print(f"R^2 score: {r2_score_value}")
        #
        #     # 绘制散点图
        #     plt.scatter(optimized_reflectance, reference_reflectance, color='blue', label='estimated vs reference')
        #
        #     # 计算线性回归函数
        #     model = LinearRegression()
        #     model.fit(optimized_reflectance.reshape(-1, 1), reference_reflectance)  # 确保X是二维数组
        #     slope = model.coef_[0]  # 获取斜率
        #     intercept = model.intercept_  # 获取截距
        #
        #     # 绘制线性回归线
        #     # print(min(optimized_reflectance), max(optimized_reflectance))
        #     # x_line = np.linspace(min(optimized_reflectance), max(optimized_reflectance), 100)
        #     # 延长虚线
        #     x_line = np.linspace(x_min, x_max, 100)
        #     y_line = slope * x_line + intercept
        #     print('斜率和截距：', slope, intercept)
        #     # plt.plot(x_line, y_line, color='red', linestyle='--', label='Linear Regression')
        #
        #     # 绘制1:1线
        #     # plt.plot([min(reference_reflectance), max(reference_reflectance)], [min(reference_reflectance), max(reference_reflectance)], color='green', linestyle='-', label='1:1 line')
        #     plt.plot([x_min, x_max],
        #              [y_min, y_max], color='green', linestyle='-', label='1:1 line')
        #
        #     # plt.plot(x_line, y_line, color='red', linestyle='--', label=f"y={slope:.5f}x{intercept:.5f}, R\u00B2={r2_score_value:.5f}")
        #     plt.plot(x_line, y_line, color='red', linestyle='--',
        #              label=f"y={slope:.3f}x{intercept:+.3f}, R\u00B2={r2_score_value:.3f}")
        #
        #     # 添加图例
        #     from matplotlib.font_manager import FontProperties
        #     # 创建一个FontProperties对象来指定字体属性
        #     legend_props = FontProperties(family='Times New Roman', size=19)
        #     # 添加图例
        #     plt.legend(prop=legend_props)
        #
        #     # 设置图表标题和坐标轴标签
        #     plt.title(f'Band{k + 1} Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        #     # plt.title('Red Reflectance/Transmittance',font='Times New Roman', fontsize=30)
        #     plt.xlabel('Estimated Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        #     plt.ylabel('Reference Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        #     plt.xticks(font='Times New Roman', fontsize=26)
        #     plt.yticks(font='Times New Roman', fontsize=26)
        #     plt.savefig(os.path.join(result_dir, f'band{k + 1}_result.png'), dpi=600)
        #     # # 显示图表
        #     # plt.show()
        #     plt.close()

        # 将所有波段的结果合并=================================================================================================
        # =================================================================================================================
        # =================================================================================================================
        optimized_reflectance_all = np.array(optimized_params[1:, :])  # 用您的数据替换这里的
        reference_reflectance_all = np.array(true_params[1:, :])  # 用您的数据替换这里的
        optimized_reflectance = optimized_reflectance_all.flatten()
        reference_reflectance = reference_reflectance_all.flatten()
        # 场景5区分========================================================  可自行选定想要的不同的散点图的设置
        # optimized_reflectance_branch = optimized_reflectance_all[[0, 3, 6, 9]]
        # optimized_reflectance_leaf = optimized_reflectance_all[[1, 2, 4, 5, 7, 8, 10, 11]]
        # optimized_reflectance_soil = optimized_reflectance_all[12:, :]
        # reference_reflectance_branch = reference_reflectance_all[[0, 3, 6, 9]]
        # reference_reflectance_leaf = reference_reflectance_all[[1, 2, 4, 5, 7, 8, 10, 11]]
        # reference_reflectance_soil = reference_reflectance_all[12:, :]
        # optimized_reflectance_0 = optimized_reflectance_all[[0,1]]
        # optimized_reflectance_1 = optimized_reflectance_all[[2,3]]
        # optimized_reflectance_2 = optimized_reflectance_all[[4,5]]
        # optimized_reflectance_3 = optimized_reflectance_all[[6,7]]
        # # city场景
        exclude_numbers = [68,69]
        wall_index = [30, 38, 35, 6, 4, 9, 8, 26, 24, 20, 13, 76, 73, 82, 79, 65, 67, 66, 59, 56, 64, 61, 53, 51, 54, 41, 40, 46, 43, 33, 31, 39, 36, 7, 5, 23, 18, 1, 21, 14, 12, 16, 15, 93, 87, 86]
        roof_index = [i for i in range(1, 95) if i not in wall_index and i not in exclude_numbers]
        for kkk in range(len(wall_index)):
            if wall_index[kkk] > 69:
                wall_index[kkk] = wall_index[kkk] - 3
            else:
                wall_index[kkk] = wall_index[kkk] - 1
        for kkk in range(len(roof_index)):
            if roof_index[kkk] > 69:
                roof_index[kkk] = roof_index[kkk] - 3
            else:
                roof_index[kkk] = roof_index[kkk] - 1
        optimized_reflectance_wall = optimized_reflectance_all[wall_index]
        optimized_reflectance_roof = optimized_reflectance_all[roof_index]
        optimized_reflectance_soil = optimized_reflectance_all[[-1]]

        # optimized_reflectance_branch = optimized_reflectance_branch.flatten()
        # optimized_reflectance_leaf = optimized_reflectance_leaf.flatten()
        # optimized_reflectance_soil = optimized_reflectance_soil.flatten()
        # reference_reflectance_branch = reference_reflectance_branch.flatten()
        # reference_reflectance_leaf = reference_reflectance_leaf.flatten()
        # reference_reflectance_soil = reference_reflectance_soil.flatten()
        # reference_reflectance_0 = reference_reflectance_all[[0,1]]
        # reference_reflectance_1 = reference_reflectance_all[[2,3]]
        # reference_reflectance_2 = reference_reflectance_all[[4,5]]
        # reference_reflectance_3 = reference_reflectance_all[[6,7]]
        # # city场景
        reference_reflectance_wall = reference_reflectance_all[wall_index]
        reference_reflectance_roof = reference_reflectance_all[roof_index]
        reference_reflectance_soil = reference_reflectance_all[[-1]]

        # optimized_reflectance = np.array(optimized_params[1:,4])  # 用您的数据替换这里的
        # reference_reflectance = np.array(true_params[1:,4])  # 用您的数据替换这里的
        plt.figure(figsize=(figsizex, figsizey))
        plt.xlim(x_min, x_max)  # x轴的限制 散点图
        plt.ylim(y_min, y_max)  # y轴的限制

        # 计算R²值
        r2_score_value = r2_score(reference_reflectance, optimized_reflectance)

        if r2_score_value > 0.9995:
            r2_score_value = 0.999

        # 打印R²值
        print(f"R^2 score: {r2_score_value}")

        # 绘制散点图
        # 不区分场景5等其他点
        # plt.scatter(optimized_reflectance, reference_reflectance, color='blue', label='estimated vs reference')
        # plt.scatter(optimized_reflectance, reference_reflectance, color='blue', label='estimated vs measured')
        # 仅限场景5区分点                # 可自行选定想要的不同的散点图的设置
        # plt.scatter(optimized_reflectance_branch, reference_reflectance_branch, color='blue', label='branch')
        # plt.scatter(optimized_reflectance_leaf, reference_reflectance_leaf, color='pink', label='leaf')
        # plt.scatter(optimized_reflectance_soil, reference_reflectance_soil, color='brown', label='soil')

        # plt.scatter(optimized_reflectance_0, reference_reflectance_0, marker='o',color='blue', s=50, label='BK')
        # plt.scatter(optimized_reflectance_1, reference_reflectance_1, marker='s', color='green', s=50, label='LZ')
        # plt.scatter(optimized_reflectance_2, reference_reflectance_2, marker='^', color='red', s=50, label='HY')
        # plt.scatter(optimized_reflectance_3, reference_reflectance_3, marker='D', color='purple', s=50, label='JS')
        # # city场景
        plt.scatter(optimized_reflectance_soil, reference_reflectance_soil, color='green', s=50, label='ground')
        plt.scatter(optimized_reflectance_wall, reference_reflectance_wall, color='red', s=50, label='side wall')
        plt.scatter(optimized_reflectance_roof, reference_reflectance_roof, color='blue', s=50, label='roof')


        # 设置网格 可选择去掉
        # plt.grid(True, linestyle='--', alpha=0.6)

        # plt.scatter(optimized_reflectance_leaf, reference_reflectance_leaf, color='pink', label='leaf')
        # plt.scatter(optimized_reflectance_branch, reference_reflectance_branch, color='blue', label='branch')

        # 计算线性回归函数
        model = LinearRegression()
        model.fit(optimized_reflectance.reshape(-1, 1), reference_reflectance)  # 确保X是二维数组
        slope = model.coef_[0]  # 获取斜率
        intercept = model.intercept_  # 获取截距

        # 绘制线性回归线
        print(min(optimized_reflectance), max(optimized_reflectance))
        # x_line = np.linspace(min(optimized_reflectance), max(optimized_reflectance), 100)
        # 延长虚线
        x_line = np.linspace(x_min, x_max, 100)
        y_line = slope * x_line + intercept
        print('斜率和截距：', slope, intercept)
        # plt.plot(x_line, y_line, color='red', linestyle='--', label='Linear Regression')

        # 绘制1:1线
        # plt.plot([min(reference_reflectance), max(reference_reflectance)], [min(reference_reflectance), max(reference_reflectance)], color='green', linestyle='-', label='1:1 line')
        plt.plot([x_min, x_max],
                 [y_min, y_max], color='green', linestyle='-', label='1:1 line')

        # plt.plot(x_line, y_line, color='red', linestyle='--', label=f"y={slope:.5f}x{intercept:.5f}, R\u00B2={r2_score_value:.5f}")
        plt.plot(x_line, y_line, color='red', linestyle='--',
                 label=f"y={slope:.3f}x{intercept:+.3f}, R\u00B2={r2_score_value:.3f}")

        # 添加图例
        from matplotlib.font_manager import FontProperties
        # 创建一个FontProperties对象来指定字体属性
        legend_props = FontProperties(family='Times New Roman', size=19)
        # 添加图例
        plt.legend(prop=legend_props)

        # 设置图表标题和坐标轴标签
        plt.title(f'All Band Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # plt.title('Red Reflectance/Transmittance',font='Times New Roman', fontsize=30)
        plt.xlabel('Estimated Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # 自行更改题目=========================
        plt.ylabel('Reference Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # plt.ylabel('Measured Reflectance/Transmittance', font='Times New Roman', fontsize=30)  # 实测数据注释===================
        plt.xticks(font='Times New Roman', fontsize=26)
        plt.yticks(font='Times New Roman', fontsize=26)
        plt.savefig(os.path.join(result_dir, f'allband_result.png'), dpi=600)
        # 显示图表
        # plt.show()
        plt.close()


    @staticmethod
    def plot_every_band_result(result_dir, true_params_path, optimize_params_path):
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        df1 = pd.read_excel(true_params_path)
        df2 = pd.read_excel(optimize_params_path)

        # 获取每列标题
        column_titles = df1.columns.tolist()

        # 获取总共的标题个数
        num_columns = len(column_titles)

        # 获取每列的长度
        column_lengths = df1.apply(len).tolist()
        band_num = column_lengths[0]

        # 打印每列标题及其对应的长度
        for title, length in zip(column_titles, column_lengths):
            print(f"{title}: {length}")

        if not all(x == column_lengths[0] for x in column_lengths):
            raise ValueError("Column lengths do not match")

        # 打印每列标题及总共的标题个数
        # print("每列标题：", column_titles)
        # print("总共的标题个数：", num_columns)

        true_params = np.zeros((num_columns, column_lengths[0]))
        optimized_params = np.zeros((num_columns, column_lengths[0]))

        for i in range(num_columns):
            true_params[i] = (df1[column_titles[i]]).values
            optimized_params[i] = (df2[column_titles[i]]).values

        x_min = 0.0
        x_max = 1.0
        y_min = 0.0
        y_max = 1.0
        figsizex = 10
        figsizey = 8
        import matplotlib.pyplot as plt
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        # 每个波段的，这个好像没什么必要======================================
        # for k in range(band_num):
        #     optimized_reflectance = np.array(optimized_params[1:, k])  # 用您的数据替换这里的 这里表示把波段的一列去掉，获得其他的数据
        #     reference_reflectance = np.array(true_params[1:, k])  # 用您的数据替换这里的
        #
        #     plt.figure(figsize=(figsizex, figsizey))
        #     plt.xlim(x_min, x_max)  # x轴的限制 散点图
        #     plt.ylim(y_min, y_max)  # y轴的限制
        #
        #     # 计算R²值
        #     r2_score_value = r2_score(reference_reflectance, optimized_reflectance)
        #     if r2_score_value > 0.9995:
        #         r2_score_value = 0.999
        #     print(f"band:{k+1}")
        #     # 打印R²值
        #     print(f"R^2 score: {r2_score_value}")
        #
        #     # 绘制散点图
        #     plt.scatter(optimized_reflectance, reference_reflectance, color='blue', label='estimated vs reference')
        #
        #     # 计算线性回归函数
        #     model = LinearRegression()
        #     model.fit(optimized_reflectance.reshape(-1, 1), reference_reflectance)  # 确保X是二维数组
        #     slope = model.coef_[0]  # 获取斜率
        #     intercept = model.intercept_  # 获取截距
        #
        #     # 绘制线性回归线
        #     # print(min(optimized_reflectance), max(optimized_reflectance))
        #     # x_line = np.linspace(min(optimized_reflectance), max(optimized_reflectance), 100)
        #     # 延长虚线
        #     x_line = np.linspace(x_min, x_max, 100)
        #     y_line = slope * x_line + intercept
        #     print('斜率和截距：', slope, intercept)
        #     # plt.plot(x_line, y_line, color='red', linestyle='--', label='Linear Regression')
        #
        #     # 绘制1:1线
        #     # plt.plot([min(reference_reflectance), max(reference_reflectance)], [min(reference_reflectance), max(reference_reflectance)], color='green', linestyle='-', label='1:1 line')
        #     plt.plot([x_min, x_max],
        #              [y_min, y_max], color='green', linestyle='-', label='1:1 line')
        #
        #     # plt.plot(x_line, y_line, color='red', linestyle='--', label=f"y={slope:.5f}x{intercept:.5f}, R\u00B2={r2_score_value:.5f}")
        #     plt.plot(x_line, y_line, color='red', linestyle='--',
        #              label=f"y={slope:.3f}x{intercept:+.3f}, R\u00B2={r2_score_value:.3f}")
        #
        #     # 添加图例
        #     from matplotlib.font_manager import FontProperties
        #     # 创建一个FontProperties对象来指定字体属性
        #     legend_props = FontProperties(family='Times New Roman', size=19)
        #     # 添加图例
        #     plt.legend(prop=legend_props)
        #
        #     # 设置图表标题和坐标轴标签
        #     plt.title(f'Band{k + 1} Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        #     # plt.title('Red Reflectance/Transmittance',font='Times New Roman', fontsize=30)
        #     plt.xlabel('Estimated Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        #     plt.ylabel('Reference Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        #     plt.xticks(font='Times New Roman', fontsize=26)
        #     plt.yticks(font='Times New Roman', fontsize=26)
        #     plt.savefig(os.path.join(result_dir, f'band{k + 1}_result.png'), dpi=600)
        #     # # 显示图表
        #     # plt.show()
        #     plt.close()

        # 将所有波段的结果合并=================================================================================================
        # =================================================================================================================
        # =================================================================================================================
        optimized_reflectance_all = np.array(optimized_params[1:, :])  # 用您的数据替换这里的
        reference_reflectance_all = np.array(true_params[1:, :])  # 用您的数据替换这里的
        optimized_reflectance = optimized_reflectance_all.flatten()
        reference_reflectance = reference_reflectance_all.flatten()
        # 场景5区分========================================================  可自行选定想要的不同的散点图的设置

        # optimized_reflectance = np.array(optimized_params[1:,4])  # 用您的数据替换这里的
        # reference_reflectance = np.array(true_params[1:,4])  # 用您的数据替换这里的
        plt.figure(figsize=(figsizex, figsizey))
        plt.xlim(x_min, x_max)  # x轴的限制 散点图
        plt.ylim(y_min, y_max)  # y轴的限制

        # 计算R²值
        r2_score_value = r2_score(reference_reflectance, optimized_reflectance)

        if r2_score_value > 0.9995:
            r2_score_value = 0.999

        # 打印R²值
        print(f"R^2 score: {r2_score_value}")

        # 绘制散点图
        # 不区分场景5等其他点
        # plt.scatter(optimized_reflectance, reference_reflectance, color='blue', label='estimated vs reference')
        plt.scatter(optimized_reflectance, reference_reflectance, color='blue', label='estimated vs measured')

        # 设置网格 可选择去掉
        # plt.grid(True, linestyle='--', alpha=0.6)

        # plt.scatter(optimized_reflectance_leaf, reference_reflectance_leaf, color='pink', label='leaf')
        # plt.scatter(optimized_reflectance_branch, reference_reflectance_branch, color='blue', label='branch')

        # 计算线性回归函数
        model = LinearRegression()
        model.fit(optimized_reflectance.reshape(-1, 1), reference_reflectance)  # 确保X是二维数组
        slope = model.coef_[0]  # 获取斜率
        intercept = model.intercept_  # 获取截距

        # 绘制线性回归线
        print(min(optimized_reflectance), max(optimized_reflectance))
        # x_line = np.linspace(min(optimized_reflectance), max(optimized_reflectance), 100)
        # 延长虚线
        x_line = np.linspace(x_min, x_max, 100)
        y_line = slope * x_line + intercept
        print('斜率和截距：', slope, intercept)
        # plt.plot(x_line, y_line, color='red', linestyle='--', label='Linear Regression')

        # 绘制1:1线
        # plt.plot([min(reference_reflectance), max(reference_reflectance)], [min(reference_reflectance), max(reference_reflectance)], color='green', linestyle='-', label='1:1 line')
        plt.plot([x_min, x_max],
                 [y_min, y_max], color='green', linestyle='-', label='1:1 line')

        # plt.plot(x_line, y_line, color='red', linestyle='--', label=f"y={slope:.5f}x{intercept:.5f}, R\u00B2={r2_score_value:.5f}")
        plt.plot(x_line, y_line, color='red', linestyle='--',
                 label=f"y={slope:.3f}x{intercept:+.3f}, R\u00B2={r2_score_value:.3f}")

        # 添加图例
        from matplotlib.font_manager import FontProperties
        # 创建一个FontProperties对象来指定字体属性
        legend_props = FontProperties(family='Times New Roman', size=19)
        # 添加图例
        plt.legend(prop=legend_props)

        # 设置图表标题和坐标轴标签
        plt.title(f'All Band Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # plt.title('Red Reflectance/Transmittance',font='Times New Roman', fontsize=30)
        plt.xlabel('Estimated Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # 自行更改题目=========================
        plt.ylabel('Reference Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # plt.ylabel('Measured Reflectance/Transmittance', font='Times New Roman', fontsize=30)  # 实测数据注释===================
        plt.xticks(font='Times New Roman', fontsize=26)
        plt.yticks(font='Times New Roman', fontsize=26)
        plt.savefig(os.path.join(result_dir, f'allband_result.png'), dpi=600)
        # 显示图表
        # plt.show()
        plt.close()


    @staticmethod
    def plot_every_band_result_hldata(result_dir, true_params_path, optimize_params_path):
        '''
        用于特定的论文返修2025-08-20时返修结果的数据
        '''
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        df1 = pd.read_excel(true_params_path)
        df2 = pd.read_excel(optimize_params_path)

        # 获取每列标题
        column_titles = df1.columns.tolist()

        # 获取总共的标题个数
        num_columns = len(column_titles)

        # 获取每列的长度
        column_lengths = df1.apply(len).tolist()
        band_num = column_lengths[0]

        # 打印每列标题及其对应的长度
        for title, length in zip(column_titles, column_lengths):
            print(f"{title}: {length}")

        if not all(x == column_lengths[0] for x in column_lengths):
            raise ValueError("Column lengths do not match")

        # 打印每列标题及总共的标题个数
        # print("每列标题：", column_titles)
        # print("总共的标题个数：", num_columns)

        true_params = np.zeros((num_columns, column_lengths[0]))
        optimized_params = np.zeros((num_columns, column_lengths[0]))

        for i in range(num_columns):
            true_params[i] = (df1[column_titles[i]]).values
            optimized_params[i] = (df2[column_titles[i]]).values

        x_min = 0.0
        x_max = 1.0
        y_min = 0.0
        y_max = 1.0
        figsizex = 10
        figsizey = 8
        import matplotlib.pyplot as plt
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score

        # 将所有波段的结果合并=================================================================================================
        # =================================================================================================================
        # =================================================================================================================
        optimized_reflectance_all = np.array(optimized_params[1:, :])  # 用您的数据替换这里的
        reference_reflectance_all = np.array(true_params[1:, :])  # 用您的数据替换这里的
        optimized_reflectance = optimized_reflectance_all.flatten()
        reference_reflectance = reference_reflectance_all.flatten()
        # 场景5区分========================================================  可自行选定想要的不同的散点图的设置

        # optimized_reflectance = np.array(optimized_params[1:,4])  # 用您的数据替换这里的
        # reference_reflectance = np.array(true_params[1:,4])  # 用您的数据替换这里的
        optimized_reflectance_L1 = optimized_reflectance_all[[0]]
        optimized_reflectance_L2 = optimized_reflectance_all[[1]]
        optimized_reflectance_L3 = optimized_reflectance_all[[2]]
        optimized_reflectance_L4 = optimized_reflectance_all[[3]]
        optimized_reflectance_L5 = optimized_reflectance_all[[4]]
        optimized_reflectance_L6 = optimized_reflectance_all[[5]]

        reference_reflectance_L1 = reference_reflectance_all[[0]]
        reference_reflectance_L2 = reference_reflectance_all[[1]]
        reference_reflectance_L3 = reference_reflectance_all[[2]]
        reference_reflectance_L4 = reference_reflectance_all[[3]]
        reference_reflectance_L5 = reference_reflectance_all[[4]]
        reference_reflectance_L6 = reference_reflectance_all[[5]]
        plt.figure(figsize=(figsizex, figsizey))
        plt.xlim(x_min, x_max)  # x轴的限制 散点图
        plt.ylim(y_min, y_max)  # y轴的限制

        # 计算R²值
        r2_score_value = r2_score(reference_reflectance, optimized_reflectance)

        if r2_score_value > 0.9995:
            r2_score_value = 0.999

        # 打印R²值
        print(f"R^2 score: {r2_score_value}")

        # 绘制散点图
        # 不区分场景5等其他点
        # plt.scatter(optimized_reflectance, reference_reflectance, color='blue', label='estimated vs reference')
        # plt.scatter(optimized_reflectance, reference_reflectance, color='blue', label='estimated vs measured')

        # 设置网格 可选择去掉
        # plt.grid(True, linestyle='--', alpha=0.6)

        # plt.scatter(optimized_reflectance_leaf, reference_reflectance_leaf, color='pink', label='leaf')
        # plt.scatter(optimized_reflectance_branch, reference_reflectance_branch, color='blue', label='branch')
        plt.scatter(optimized_reflectance_L1, reference_reflectance_L1, marker='o',color='blue', s=50, label='layer1')
        plt.scatter(optimized_reflectance_L2, reference_reflectance_L2, marker='s', color='pink', s=50, label='layer2')
        plt.scatter(optimized_reflectance_L3, reference_reflectance_L3, marker='^', color='black', s=50, label='layer3')
        plt.scatter(optimized_reflectance_L4, reference_reflectance_L4, marker='D', color='purple', s=50, label='layer4')
        plt.scatter(optimized_reflectance_L5, reference_reflectance_L5, marker='P', color='gray', s=50, label='layer5')
        plt.scatter(optimized_reflectance_L6, reference_reflectance_L6, marker='H', color='orange', s=50,
                    label='layer6')

        # 计算线性回归函数
        model = LinearRegression()
        model.fit(optimized_reflectance.reshape(-1, 1), reference_reflectance)  # 确保X是二维数组
        slope = model.coef_[0]  # 获取斜率
        intercept = model.intercept_  # 获取截距

        # 绘制线性回归线
        print(min(optimized_reflectance), max(optimized_reflectance))
        # x_line = np.linspace(min(optimized_reflectance), max(optimized_reflectance), 100)
        # 延长虚线
        x_line = np.linspace(x_min, x_max, 100)
        y_line = slope * x_line + intercept
        print('斜率和截距：', slope, intercept)
        # plt.plot(x_line, y_line, color='red', linestyle='--', label='Linear Regression')

        # 绘制1:1线
        # plt.plot([min(reference_reflectance), max(reference_reflectance)], [min(reference_reflectance), max(reference_reflectance)], color='green', linestyle='-', label='1:1 line')
        plt.plot([x_min, x_max],
                 [y_min, y_max], color='green', linestyle='-', label='1:1 line')

        # plt.plot(x_line, y_line, color='red', linestyle='--', label=f"y={slope:.5f}x{intercept:.5f}, R\u00B2={r2_score_value:.5f}")
        plt.plot(x_line, y_line, color='red', linestyle='--',
                 label=f"y={slope:.3f}x{intercept:+.3f}, R\u00B2={r2_score_value:.3f}")

        # 添加图例
        from matplotlib.font_manager import FontProperties
        # 创建一个FontProperties对象来指定字体属性
        legend_props = FontProperties(family='Times New Roman', size=16)
        # 添加图例
        plt.legend(prop=legend_props)

        # 设置图表标题和坐标轴标签
        plt.title(f'All Band Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # plt.title('Red Reflectance/Transmittance',font='Times New Roman', fontsize=30)
        plt.xlabel('Estimated Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # 自行更改题目=========================
        plt.ylabel('Reference Reflectance/Transmittance', font='Times New Roman', fontsize=30)
        # plt.ylabel('Measured Reflectance/Transmittance', font='Times New Roman', fontsize=30)  # 实测数据注释===================
        plt.xticks(font='Times New Roman', fontsize=26)
        plt.yticks(font='Times New Roman', fontsize=26)
        plt.savefig(os.path.join(result_dir, f'allband_result.png'), dpi=600)
        # 显示图表
        # plt.show()
        plt.close()


    # def set_ref_brf_image_path(self, ref_brf_image_path):
    #     self.ref_brf_image_path = ref_brf_image_path
    #
    # def set_result_dir_path(self, result_dir_path):
    #     self.result_dir_path = result_dir_path