import os
import pandas as pd
import numpy as np

class DiffRenderConfig():
    def __init__(self):
        self.init_epoch = 0
        self.stop_epoch = 100
        self.initial_learning_rate = 0.1
        self.optimize_spp = 1024
        self.ref_brf_image_path = ""
        self.result_dir_path = ""
        self.shuffle_spectral_values = True
        self.shuffle_value_range = []
        self.resume = False
        self.resume_xlsx_name = ""
        self.optimize_params = []
        self.is_open_comparison_between_opt_and_origin = False
        self.use_field_data_simplify_opt = False
        self.simplify_opt_limit = [0.05, 0.05]
        self.image_bands_show = []
        self.image_diff_abs_bands = []

        self.sensor_observation_Zenith_Azimuth = []
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




    # def set_ref_brf_image_path(self, ref_brf_image_path):
    #     self.ref_brf_image_path = ref_brf_image_path
    #
    # def set_result_dir_path(self, result_dir_path):
    #     self.result_dir_path = result_dir_path