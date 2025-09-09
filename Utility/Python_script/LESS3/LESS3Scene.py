# coding: utf-8
import mitsuba as mi
import drjit as dr
from LESS3Sensor import LESS3Sensor
from LESS3Illumination import LESS3Illumination
from LESS3Landscape import LESS3Landscape
import os
import numpy as np
from Utils import Utils
from DiffRenderConfig import DiffRenderConfig
import matplotlib.pyplot as plt
import pandas as pd
import logging
import math

class LESS3Scene(object):
    def __init__(self, less_scene):
        self.less_scene = less_scene
        # self.result_folder_path = os.path.dirname(self.less_scene.get_sim().get_dist_file())
        self.__dist_file = self.less_scene.get_sim().get_dist_file()
        self.brf_image_path = ""

    def render(self, xml_file="", n_dict=None, export_xml=False):
        scene_dict = self.__load_less3scene_dict()
        if xml_file == "" and n_dict is None and export_xml==True:
            scene = mi.load_dict(scene_dict)
            # export xml file- has bug
            mi.xml.dict_to_xml(scene_dict,
                               (os.path.join(self.less_scene.get_sim().get_parameters_dir(), "_scenefile",
                                             "LESS3.xml")))
            Utils.trans_LESS3_xml_correct(os.path.join(self.less_scene.get_sim().get_parameters_dir(), "_scenefile",
                                             "LESS3.xml"))
            # print(scene_dict)
            # print(type(scene_dict))
        elif xml_file == "" and isinstance(n_dict, dict):
            scene = mi.load_dict(n_dict)
        elif xml_file != "" and n_dict is None:
            scene = mi.load_file(xml_file)
        else:
            scene = mi.load_dict(scene_dict)

        img = mi.render(scene)

        from PostProcessing import RasterHelper, PostProcessing
        image_LESS3_ref = np.array(img)
        if image_LESS3_ref.shape[2] == 1:
            image_LESS3_ref = image_LESS3_ref[:, :, 0]
        # if self.less_scene.get_sim().get_dist_file() != "":
        #     distFile = self.less_scene.get_sim().get_dist_file()
        #     folder_path = os.path.dirname(distFile)
        #     file_name = os.path.basename(distFile)

        self.__init_dist_file()
        folder_path = os.path.dirname(self.__dist_file)
        file_name = os.path.basename(self.__dist_file)
        new_distFile = folder_path + "/" + file_name + "_LESS3"
        np.save(new_distFile, image_LESS3_ref)
        wlist = list(self.less_scene.get_sensor().get_spectral_bands().split(","))
        data = np.load(new_distFile + ".npy")
        RasterHelper.saveToHdr_no_transform(data, new_distFile, wlist, output_format="ENVI")
        del data
        if os.path.exists(new_distFile + ".npy"):
            os.remove(new_distFile + ".npy")
        # dir = self.less_scene.get_sim().get_sim_dir()
        # 读取几何条件，这里太阳天顶角
        solar_zenith_angle_rad = np.deg2rad(self.less_scene.get_illumination().sun_zenith)
        # 计算余弦值
        cos_solar_zenith = np.cos(solar_zenith_angle_rad)
        # 太阳BOA辐照度other format
        # BOA_sun_irradiance = np.array([float(x) * cos_solar_zenith for x in scene_dict["emitter"]['irradiance']['values'].split(',')])
        if not isinstance(scene_dict["emitter"]['irradiance']['value'], float):
            BOA_sun_irradiance = np.array(
                [float(x[1]) * cos_solar_zenith for x in scene_dict["emitter"]['irradiance']['value']])
        else:
            BOA_sun_irradiance = np.array([scene_dict["emitter"]['irradiance']['value'] * cos_solar_zenith])
        BOA_SUN_SKY_str = "BOA_SUN "
        for i in range(len(BOA_sun_irradiance)):
            BOA_SUN_SKY_str += str(BOA_sun_irradiance[i]) + " "

        if "emitter_sky" in scene_dict:
            BOA_SUN_SKY_str += "\nBOA_SKY "
            if not isinstance(scene_dict["emitter_sky"]['radiance']['value'], float):
                BOA_sky_irradiance = np.array(
                    [float(x[1]) * math.pi for x in scene_dict["emitter_sky"]['radiance']['value']])
            else:
                BOA_sky_irradiance = np.array([scene_dict["emitter_sky"]['radiance']['value'] * math.pi])
            for i in range(len(BOA_sky_irradiance)):
                BOA_SUN_SKY_str += str(BOA_sky_irradiance[i]) + " "
        with open(os.path.join(folder_path, 'Irradiance.txt'), 'w') as irr_file:
            irr_file.write("Irradiance on the horizontal plane (W/m2/nm)\n")
            irr_file.write(BOA_SUN_SKY_str)

        PostProcessing.radiance2brf(self.less_scene.get_sim().get_sim_dir(), new_distFile, new_distFile + "_BRF")
        self.brf_image_path = new_distFile + "_BRF"
        # self.__test_LESS3_LESS()
        if img.shape[0] == 1 and img.shape[1] == 1:
            pass
        else:
            mi.util.write_bitmap("test.png", img[:,:,0])
        del img
        # if os.path.exists("test.png"):
        #     os.remove('test.png')



    def render_diff_spectrum_test(self, diff_render_config: DiffRenderConfig):
        raise Exception("备份代码--render_diff_spectrum")
        scene_dict = self.__load_less3scene_dict()
        # mi.xml.dict_to_xml(scene_dict, (os.path.join(self.less_scene.get_sim().get_parameters_dir(), "_scenefile", "LESS3.xml")))
        # del scene_dict['terrain']
        per_optimize_result_dir = diff_render_config.result_dir_path
        optimize_spp = diff_render_config.optimize_spp

        if not os.path.exists(per_optimize_result_dir):
            os.makedirs(per_optimize_result_dir)

        if Utils.is_nvidia_gpu_present():
            mi.set_variant("cuda_ad_spectral")
            scene_dict['integrator']['type'] = 'prb'
            pass
        else:
            raise Exception("Nvidia GPU is not present")

        diff_render_log = Utils.use_log(per_optimize_result_dir, "diff_render_log")

        spectral_bands = list(map(lambda x: float(x.split(":")[0]),
                                  self.less_scene.get_sim().get_scene().get_sensor().get_spectral_bands().split(
                                      ",")))

        origin_params_result = {'wavelength': spectral_bands}
        optimize_params_result = {'wavelength': spectral_bands}

        optimize_params = diff_render_config.optimize_params

        all_optimize_spectral_params = []
        optimize_spectral_params_output_names = []
        all_optimize_spectral_params_first_item = []

        scene = mi.load_dict(scene_dict)
        params = mi.traverse(scene)
        # print(params)

        if len(spectral_bands) > 1:
            params.keep(r'.*\.*\.values')
            # print(params)
        else:
            params.keep(r'.*\.*\.value')
            # print(params)

        for every_spectral_param in params:
            first_spectral_keys = every_spectral_param[0]
            first_spectral_keys_length = len(first_spectral_keys.split("."))
            first_item = first_spectral_keys.split(".")[0]
            # 自行调整想要优化的参数
            if first_item == 'sensor' or first_item == 'emitter':
                continue
            second_item = first_spectral_keys.split(".")[1]
            third_item = first_spectral_keys.split(".")[2]
            all_optimize_spectral_params.append(first_spectral_keys)
            all_optimize_spectral_params_first_item.append(first_item)
            if first_spectral_keys_length == 3:
                optimize_spectral_params_output_names.append(first_item + "_Reflectance(Front)")
                pass
            elif first_spectral_keys_length == 4:
                if third_item == 'base_color':
                    optimize_spectral_params_output_names.append(first_item + "_Transmittance")
                elif second_item == 'brdf_0' and third_item == 'reflectance':
                    optimize_spectral_params_output_names.append(first_item + "_Reflectance")
                elif second_item == 'brdf_1' and third_item == 'reflectance':
                    optimize_spectral_params_output_names.append(first_item + "_Reflectance(Back)")
                    temp_index = optimize_spectral_params_output_names.index(first_item + "_Reflectance")
                    optimize_spectral_params_output_names[temp_index] = first_item + "_Reflectance(Front)"
                    raise Exception("currently, not test")
                pass
            elif first_spectral_keys_length == 5:
                if third_item == 'brdf_0':
                    optimize_spectral_params_output_names.append(first_item + "_Reflectance")
                elif third_item == 'brdf_1':
                    optimize_spectral_params_output_names.append(first_item + "_Reflectance(Back)")
                    temp_index = optimize_spectral_params_output_names.index(first_item + "_Reflectance")
                    optimize_spectral_params_output_names[temp_index] = first_item + "_Reflectance(Front)"
                    raise Exception("currently, not test")
                pass

            # if second_item == 'reflectance':
            #     optimize_spectral_params_output_names.append(first_item + "_Reflectance(Front)")
            #     pass
            # elif second_item == 'brdf_0':
            #     if third_item == 'brdf_0':
            #         optimize_spectral_params_output_names.append(first_item + "_Reflectance")
            #         pass
            #     elif third_item == 'brdf_1':
            #         optimize_spectral_params_output_names.append(first_item + "_Reflectance(Back)")
            #         temp_index = optimize_spectral_params_output_names.index(first_item + "_Reflectance")
            #         optimize_spectral_params_output_names[temp_index] = first_item + "_Reflectance(Front)"
            #
            #         raise Exception("currently, not test")
            #         pass
            #     elif third_item == 'reflectance':
            #         optimize_spectral_params_output_names.append(first_item + "_Reflectance")
            #         pass
            #     pass
            # elif second_item == 'brdf_1':
            #     if third_item == 'base_color':
            #         optimize_spectral_params_output_names.append(first_item + "_Transmittance")
            #         pass
            #     elif third_item == 'reflectance':
            #         optimize_spectral_params_output_names.append(first_item + "_Reflectance(Back)")
            #         temp_index = optimize_spectral_params_output_names.index(first_item + "_Reflectance")
            #         optimize_spectral_params_output_names[temp_index] = first_item + "_Reflectance(Front)"
            #         pass
            #     pass

        if len(optimize_params) == 0:
            optimize_params = all_optimize_spectral_params
        elif len(optimize_params) > 0:
            if all(item in set(all_optimize_spectral_params_first_item) for item in optimize_params) is not True:
                raise Exception("your input of optimized parameters has error")
            select_optimize_params_temp = []
            select_optimize_params_output_names_temp = []
            # for i, per_optimize_spectral_param in enumerate(all_optimize_spectral_params):
            #     # birch_branch.reflectance.values = per_optimize_spectral_param
            #     if per_optimize_spectral_param.split(".")[0] in set(optimize_params):
            #         select_optimize_params_temp.append(per_optimize_spectral_param)
            #     else:
            #         optimize_spectral_params_output_names.remove(i)
            for i in range(len(optimize_params)):
                optimize_params[i]
                for index, value in enumerate(all_optimize_spectral_params_first_item):
                    if value == optimize_params[i]:
                        select_optimize_params_temp.append(all_optimize_spectral_params[index])
                        select_optimize_params_output_names_temp.append(optimize_spectral_params_output_names[index])

            optimize_params = select_optimize_params_temp
            optimize_spectral_params_output_names = select_optimize_params_output_names_temp

        if diff_render_config.use_field_data_simplify_opt:
            transmittance_indexs = []
            transmittance_names = []
            transmittance_to_reflectance_index = []
            for index, opt_param in enumerate(optimize_spectral_params_output_names):
                if opt_param.rsplit('_', 1)[1] == 'Transmittance':
                    transmittance_indexs.append(index)
                    transmittance_names.append(opt_param.rsplit('_', 1)[0])
            for transmittance_param in transmittance_names:
                for index, opt_param in enumerate(optimize_spectral_params_output_names):
                    if opt_param.rsplit('_', 1)[0] == transmittance_param:
                        if opt_param.rsplit('_', 1)[1] == 'Reflectance' or opt_param.rsplit('_', 1)[1] == 'Reflectance(Front)':
                            transmittance_to_reflectance_index.append(index)
            del transmittance_names
            if len(transmittance_indexs)==0 or len(transmittance_to_reflectance_index)==0:
                diff_render_config.use_field_data_simplify_opt = False

        if len(diff_render_config.shuffle_value_range) == 2:
            shuffle_low_value = diff_render_config.shuffle_value_range[0]
            shuffle_high_value = diff_render_config.shuffle_value_range[1]
        else:
            shuffle_low_value = 0.1
            shuffle_high_value = 0.2
        import random
        for i in range(len(optimize_params)):
            # print(optimize_params[i], params[optimize_params[i]])
            origin_params_result[optimize_spectral_params_output_names[i]] = dr.cuda.ad.Float.copy_(params[optimize_params[i]])
            if diff_render_config.resume is False and diff_render_config.shuffle_spectral_values is True:
                params[optimize_params[i]] = [random.uniform(shuffle_low_value, shuffle_high_value) for _ in range(len(spectral_bands))]
                pass
            elif diff_render_config.resume is True:
                # df = pd.DataFrame()
                # df = load_excel_file(df, diff_render_config.resume_xlsx_name)
                df = pd.read_excel(diff_render_config.resume_xlsx_name)
                params[optimize_params[i]] = np.array(df[optimize_spectral_params_output_names[i]])
                # print('加载后的参数', optimize_params[i], params[optimize_params[i]])
                ## =================================下面这里自行添加测试===============================##
                # params[optimize_params[2]] = [random.uniform(0.1, 0.2) for _ in range(len(spectral_bands))]

                ## =================================添加测试结束===============================##


        origin_params_DataFrame = pd.DataFrame(origin_params_result)
        origin_params_DataFrame.to_excel(per_optimize_result_dir + '/origin_params.xlsx', index=False)

        params.update()  # 更新成更改后的参数

        ## =================================下面这里自行添加测试===============================##
        # optimize_params = optimize_params[2:]
        # optimize_spectral_params_output_names = optimize_spectral_params_output_names[2:]

        ## =================================添加测试结束===============================##

        # load BRF image
        ref_brf_image, image_height, image_width = Utils.load_RS_image(diff_render_config.ref_brf_image_path)
        ref_brf_image = dr.cuda.ad.TensorXf(ref_brf_image)

        opt_temp_image = mi.render(scene) * dr.pi
        # 读取几何条件，这里太阳天顶角
        solar_zenith_angle_rad = np.deg2rad(self.less_scene.get_illumination().sun_zenith)
        # 计算余弦值
        cos_solar_zenith = np.cos(solar_zenith_angle_rad)
        # 太阳BOA辐照度other format
        # BOA_sun_irradiance = np.array([float(x) * cos_solar_zenith for x in scene_dict["emitter"]['irradiance']['values'].split(',')])
        BOA_sun_irradiance = np.array(
            [float(x[1]) * cos_solar_zenith for x in scene_dict["emitter"]['irradiance']['value']])
        # 将一维数组重塑为形状为[1, 13]的二维数组
        reshaped_array = BOA_sun_irradiance.reshape(1, -1)
        # 将二维数组在第一个维度（行）上重复500*500次，形成形状为[500*500, 13]的数组
        tiled_array = np.tile(reshaped_array,(image_height * image_width, 1))
        # 将结果重塑为形状为[500, 500, 13]的三维数组
        final_array = tiled_array.reshape(image_height, image_width, len(BOA_sun_irradiance))
        final_irradiance_tensorxf = dr.cuda.ad.TensorXf(final_array)
        # final_irradiance_tensorxf = dr.scalar.TensorXf(final_array)
        opt_brf_image = opt_temp_image / final_irradiance_tensorxf

        if len(spectral_bands) < 3:
            mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"ref_image_band-1_epoch-{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}.png"), ref_brf_image[:, :, 0])
            mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"init_image_band-1_epoch-{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}.png"), opt_brf_image[:, :, 0])
        else:
            if len(diff_render_config.image_bands_show) == 3:
                mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"ref_image_band-3_epoch-{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}.png"),
                                     ref_brf_image[:, :, [diff_render_config.image_bands_show[0], diff_render_config.image_bands_show[1], diff_render_config.image_bands_show[2]]])
                mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"init_image_band-3_epoch-{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}.png"),
                                     opt_brf_image[:, :, [diff_render_config.image_bands_show[0], diff_render_config.image_bands_show[1], diff_render_config.image_bands_show[2]]])
            else:
                mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"ref_image_band-3_epoch-{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}.png"), ref_brf_image[:, :, [2,1,0]])
                mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"init_image_band-3_epoch-{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}.png"), opt_brf_image[:, :, [2,1,0]])

        if not os.path.exists(os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison")):
            os.makedirs(os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison"))
        Utils.brf_image_pixel_scatter_plot(np.array(ref_brf_image), np.array(opt_brf_image),
                                           save_path=os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison",
                                                                  f'init_Image_Camparison_result_epoch-{diff_render_config.init_epoch}.png'))
        # if len(diff_render_config.image_diff_abs_bands) > 0:
        #     for i in diff_render_config.image_diff_abs_bands:
        #         Utils.image_diff_abs_plot(np.array(ref_brf_image[:,:,i]), np.array(opt_brf_image[:,:,i]), os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison", f"per_pixel_diffabs_epoch-{diff_render_config.init_epoch}_band{i+1}.png"))

        opt = mi.ad.Adam(lr=diff_render_config.initial_learning_rate, mask_updates=True)

        for i in range(len(optimize_params)):
            opt[optimize_params[i]] = params[optimize_params[i]]

        params.update(opt)
        all_epoch_all_params_every_bands_rmse = []
        loss_list = []
        lowest_loss = 10000
        best_epoch = 0
        for it in range(diff_render_config.init_epoch, diff_render_config.stop_epoch):
            #     for m in range(len(optimize_param)):
            #         opt.set_learning_rate({optimize_param[m]: lr * forward_grad_factor[m]})

            # Perform a (noisy) differentiable rendering of the scene
            print(f'第{it}轮')
            diff_render_log.info(f'第{it}轮,开始渲染 ')
            image_radiance = mi.render(scene, params, spp=diff_render_config.optimize_spp)
            # Evaluate the objective function from the current rendered image

            opt_brf_image = (image_radiance * dr.pi) / final_irradiance_tensorxf
            diff_render_log.info(' 计算损失 ')
            loss = dr.mean(dr.sqr(opt_brf_image - ref_brf_image))

            # Backpropagate through the rendering process
            diff_render_log.info('开始反向传播')
            dr.backward(loss)

            if loss[0] < lowest_loss:
                lowest_loss = loss[0]
                best_epoch = it

            # Optimizer: take a gradient descent step
            # diff_render_log.info('计算新的参数')
            opt.step()
            # Post-process the optimized parameters to ensure legal color values.
            # diff_render_log.info('限制参数大小')
            for j in range(len(optimize_params)):
                opt[optimize_params[j]] = dr.clamp(opt[optimize_params[j]], 0.0 + random.uniform(0.00001, 0.00002),
                                                  1 - random.uniform(0.00001, 0.00002))

            # diff_render_log.info('加载新的参数')
            params.update(opt)

            # print(f"{optimize_param[i]}:grad={dr.grad(opt[optimize_param[i]])}")
            # opt.reset(optimize_param[i])
            if diff_render_config.use_field_data_simplify_opt:
                # params[f'mean_leaf{i}.bsdf_1.base_color.values'] = [x for x in
                #                                                     params[optimize_param[i - 1]]]
                for trans_index in range(len(transmittance_indexs)):
                    # params[optimize_params[transmittance_indexs[trans_index]]] = params[optimize_params[transmittance_to_reflectance_index[trans_index]]]
                    params[optimize_params[transmittance_indexs[trans_index]]] = np.clip(params[optimize_params[transmittance_indexs[trans_index]]],
                                                                                         params[optimize_params[transmittance_to_reflectance_index[trans_index]]] - diff_render_config.simplify_opt_limit[0],
                                                                                         params[optimize_params[transmittance_to_reflectance_index[trans_index]]] + diff_render_config.simplify_opt_limit[1]
                                                                                         )

            current_epoch_all_params_every_bands_rmse = [0] * len(spectral_bands)
            current_epoch_all_params_every_bands_rrmse = [0] * len(spectral_bands)
            if it % 1 == 0:
                # diff_render_log.info('将新参数写入excel中')
                params_diff_value = 0.000000
                for i in range(len(optimize_params)):
                    # print(optimize_param[i], params[optimize_param[i]])
                    optimize_params_result[optimize_spectral_params_output_names[i]] = dr.cuda.ad.Float.copy_(params[optimize_params[i]])
                    # print(type(params[optimize_param[i]]), type(true_params_result[optimize_param[i]]))
                    # optimize_params_result[optimize_param[i]] = params[optimize_param[i]]
                    if diff_render_config.is_open_comparison_between_opt_and_origin:
                        temp_value = optimize_params_result[optimize_spectral_params_output_names[i]] - origin_params_result[
                            optimize_spectral_params_output_names[i]]
                        print(optimize_params[i], optimize_spectral_params_output_names[i], 'Maximum_difference：'
                              , max(abs(temp_value))
                              , 'optimize - origin :', temp_value)
                        params_diff_value = max(max(abs(temp_value)), params_diff_value)
                        current_epoch_all_params_every_bands_rmse = [current_epoch_all_params_every_bands_rmse[i_band] + (temp_value[i_band]**2) for i_band in range(len(spectral_bands))]
                        current_epoch_all_params_every_bands_rrmse = [current_epoch_all_params_every_bands_rrmse[i_band] + (optimize_params_result[optimize_spectral_params_output_names[i]][i_band]**2) for i_band in range(len(spectral_bands))]
                if diff_render_config.is_open_comparison_between_opt_and_origin:
                    current_epoch_all_params_every_bands_rrmse = [np.sqrt((current_epoch_all_params_every_bands_rmse[i_band]/len(optimize_params)/current_epoch_all_params_every_bands_rrmse[i_band])) for i_band in range(len(spectral_bands))]
                    current_epoch_all_params_every_bands_rmse = [
                        np.sqrt(current_epoch_all_params_every_bands_rmse[i_band] / len(optimize_params)) for i_band in
                        range(len(spectral_bands))]
                    print('params_diff_value:', params_diff_value)
                    diff_render_log.info(f"params_diff_value: {params_diff_value}")
                optimize_params_result1 = pd.DataFrame(optimize_params_result)
                optimize_params_result1.to_excel(per_optimize_result_dir + '/optimize_params_' + str(it) + '.xlsx',
                                                 index=False)

                # print(optimize_param[i - 1], params[optimize_param[i - 1]])
                # print(f'mean_leaf{i}.bsdf_1.base_color.values', params[f'mean_leaf{i}.bsdf_1.base_color.values'])
            # if diff_render_config.use_field_data_simplify_opt:
            #     # params[f'mean_leaf{i}.bsdf_1.base_color.values'] = [x for x in
            #     #                                                     params[optimize_param[i - 1]]]
            #     for trans_index in range(len(transmittance_indexs)):
            #         params[optimize_params[transmittance_indexs[trans_index]]] = params[
            #             optimize_params[transmittance_to_reflectance_index[trans_index]]]

            # Track the difference between the current color and the true value
            if diff_render_config.is_open_comparison_between_opt_and_origin:
                all_epoch_all_params_every_bands_rmse.append(current_epoch_all_params_every_bands_rmse)
                diff_render_log.info(f"当前各波段rmse:\n{current_epoch_all_params_every_bands_rmse}")
                diff_render_log.info(f"当前各波段rrmse:\n{current_epoch_all_params_every_bands_rrmse}")
            loss_list.append(loss[0])
            diff_render_log.info(f"已完成第{it}轮的迭代，loss = {loss[0]:.15f}\n")

        print('\nOptimization complete.')
        diff_render_log.info(f"\nbest_epoch = {best_epoch}  lowest_loss = {lowest_loss}")
        diff_render_log.info(f"\nOptimization complete.")

        # plot rmse for different bands if is_open_comparison_between_opt_and_origin=True
        if diff_render_config.is_open_comparison_between_opt_and_origin:
            print("Start generating RMSE iteration graph")
            if not os.path.exists(os.path.join(per_optimize_result_dir, "Parameters_RMSE_linegraph")):
                os.makedirs(os.path.join(per_optimize_result_dir, "Parameters_RMSE_linegraph"))

            all_epoch_all_params_every_bands_rmse = np.array(all_epoch_all_params_every_bands_rmse)
            every_band_epochs_rmse = {}
            for i in range(len(spectral_bands)):
                every_band_epochs_rmse[f"band{i+1}"] = all_epoch_all_params_every_bands_rmse[:, i]
                plt.figure(figsize=(10, 8))
                plt.plot([k for k in range(0, diff_render_config.stop_epoch - diff_render_config.init_epoch)], every_band_epochs_rmse[f"band{i+1}"])
                # plt.plot([x_min, x_max],
                #          [y_min, y_max], color='green', linestyle='-', label='1:1 line')
                plt.title(f'Band{i+1} Parameters RMSE', font='Times New Roman', fontsize=30)
                plt.xlabel('Iteration', font='Times New Roman', fontsize=30)
                plt.ylabel('RMSE', font='Times New Roman', fontsize=30)
                plt.xticks(font='Times New Roman', fontsize=26)
                plt.yticks(font='Times New Roman', fontsize=26)
                plt.savefig(os.path.join(per_optimize_result_dir, 'Parameters_RMSE_linegraph', f'Band{i+1}_Parameters_RMSE_{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}'), dpi=600)
                # 关闭图形
                plt.close()

            plt.figure(figsize=(10, 8))
            plt.title(f'All Bands Parameters RMSE', font='Times New Roman', fontsize=30)
            plt.xlabel('Iteration', font='Times New Roman', fontsize=30)
            plt.ylabel('RMSE', font='Times New Roman', fontsize=30)
            plt.xticks(font='Times New Roman', fontsize=26)
            plt.yticks(font='Times New Roman', fontsize=26)
            color = [
                '#0000FF', '#00FF00', '#FF0000', '#FFFF00', '#00FFFF', '#FF00FF',
                '#800000', '#008000', '#000080', '#808000', '#008080', '#800080',
                '#FF6666', '#66FF66', '#6666FF', '#99FFFF', '#66FFFF', '#CC6640',
                '#996633', '#339966', '#663399', '#339933', '#993399', '#339999',
                '#FFCC99', '#99FFCC', '#CC99FF', '#FFCC66', '#66FFCC', '#CC66FF',
                '#CC9966', '#66CC99', '#9966CC', '#CC9966', '#66CC99', '#000000',
                '#FF9999', '#99FF99', '#9930FF', '#FFFF99', '#9948FF', '#FF99FF'
            ]
            for i in range(len(spectral_bands)):
                every_band_epochs_rmse[f"band{i + 1}"] = all_epoch_all_params_every_bands_rmse[:, i]
                plt.plot([k for k in range(0, diff_render_config.stop_epoch - diff_render_config.init_epoch)],
                         every_band_epochs_rmse[f"band{i + 1}"], color=color[i], label=f"band{i+1}")

            # 创建一个FontProperties对象来指定字体属性
            from matplotlib.font_manager import FontProperties
            legend_props = FontProperties(family='Times New Roman', size=19)
            # 添加图例
            plt.legend(prop=legend_props)
            plt.savefig(os.path.join(per_optimize_result_dir, 'Parameters_RMSE_linegraph', f'AllBand_Parameters_RMSE_{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}'),
                        dpi=600)
            plt.close()
            print("RMSE iteration graph generated successfully")

        print(f"generate some image")

        plt.figure(figsize=(10, 8))
        plt.title(f'Loss', font='Times New Roman', fontsize=30)
        plt.xlabel('Iteration', font='Times New Roman', fontsize=30)
        plt.ylabel('MSE(Loss)', font='Times New Roman', fontsize=30)
        plt.xticks(font='Times New Roman', fontsize=26)
        plt.yticks(font='Times New Roman', fontsize=26)
        # plt.plot([k for k in range(diff_render_config.init_epoch, diff_render_config.stop_epoch)],
        #          loss_list)
        plt.plot([k for k in range(0, diff_render_config.stop_epoch - diff_render_config.init_epoch)],
                 loss_list)
        plt.savefig(os.path.join(per_optimize_result_dir, 'Loss'), dpi=600)

        image_radiance = mi.render(scene, params)
        opt_brf_image = (image_radiance * dr.pi) / final_irradiance_tensorxf


        Utils.brf_image_pixel_scatter_plot(np.array(ref_brf_image), np.array(opt_brf_image),
                                           save_path=os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison",
                                                                  f'final_Image_Camparison_result_epoch-{diff_render_config.stop_epoch - 1}.png'))

        if len(spectral_bands) < 3:
            mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"final_image_band-1_epoch-{diff_render_config.stop_epoch - 1}.png"), opt_brf_image[:, :, 0])
        else:
            if len(diff_render_config.image_bands_show) == 3:
                mi.util.write_bitmap(os.path.join(per_optimize_result_dir,
                                                  f"final_image_band-3_epoch-{diff_render_config.stop_epoch - 1}.png"),
                                     opt_brf_image[:, :, [diff_render_config.image_bands_show[0], diff_render_config.image_bands_show[1], diff_render_config.image_bands_show[2]]])
            else:
                mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"final_image_band-3_epoch-{diff_render_config.stop_epoch - 1}.png"), opt_brf_image[:, :, [2,1,0]])

        plt.close()
        print("successful")

        # scene = mi.load_dict(scene_dict)
        # img = mi.render(scene)

    # 将多角度反演分出来，主要是为了测试，后面可以与render_diff_spectrum合并在一起
    def render_diff_spectrum(self, diff_render_config: DiffRenderConfig):
        init_epoch = diff_render_config.init_epoch
        stop_epoch = diff_render_config.stop_epoch

        scene_dict = self.__load_less3scene_dict()
        # 测试用===============================
        # del scene_dict['terrain']
        # texture_checkerboard = {
        #     'type': 'checkerboard'
        #     # 'color0': [0.1, 0.1, 0.1],
        #     # 'color1': [0.5, 0.5, 0.5]
        # }
        # texture_data = np.random.rand(100, 100, 1).astype(np.float32)
        # texture_dict_bitmap = {
        #     'type': 'bitmap',
        #     'raw': True,
        #     'data': texture_data
        # }
        # scene_dict["dark_soil_mollisol"]["reflectance"] = texture_dict_bitmap
        # ====================================
        if Utils.is_nvidia_gpu_present():
            mi.set_variant("cuda_ad_spectral")
            scene_dict['integrator']['type'] = 'prb'
            pass
        else:
            raise Exception("Nvidia GPU is not present")

        if isinstance(diff_render_config.ref_brf_image_path, str):
            diff_render_config.ref_brf_image_path = [diff_render_config.ref_brf_image_path]
        sensors = []
        sensor_dict = scene_dict["sensor"]
        if self.less_scene.get_sensor().sensor_type == "orthographic":
            if len(diff_render_config.ref_brf_image_path) == 1 and len(
                    diff_render_config.sensor_observation_Zenith_Azimuth) == 0:
                # 根据影像添加当前sim场景的天顶角和方位角
                diff_render_config.sensor_observation_Zenith_Azimuth.append(
                    [self.less_scene.get_observation().obs_zenith, self.less_scene.get_observation().obs_azimuth])
            if len(diff_render_config.ref_brf_image_path) == len(diff_render_config.sensor_observation_Zenith_Azimuth):
                pass
            else:
                raise Exception("The number of images does not match the number of zenith angles and azimuth angles")
            for sensor_obs_zenith_azimuth in diff_render_config.sensor_observation_Zenith_Azimuth:
                sensor_obs_zenith = sensor_obs_zenith_azimuth[0]
                sensor_obs_azimuth = sensor_obs_zenith_azimuth[1]
                obs_radius = self.less_scene.get_observation().obs_R
                # obs_zenith = self.sensor.get_sim().get_scene().get_observation().obs_zenith
                # obs_azimuth = self.sensor.get_sim().get_scene().get_observation().obs_azimuth
                x, y, z, target_x, target_y, target_z, phi = 0, 0, 0, 0, 0, 0, 0
                theta = float(sensor_obs_zenith) / 180.0 * np.pi
                phi_degree = float(sensor_obs_azimuth)
                phi = -(phi_degree - 90) / 180.0 * np.pi
                x = -obs_radius * np.sin(theta) * np.cos(phi) + target_x
                z = obs_radius * np.sin(theta) * np.sin(phi) + target_z
                y = obs_radius * np.cos(theta) + target_y

                if abs(x - target_x) < 0.00000001 and abs(z - target_z) < 0.00000001:
                    x1 = np.cos(phi)
                    z1 = -np.sin(phi)
                else:
                    xx, yy, zz = target_x - x, target_y - y, target_z - z
                    x1 = -xx * yy / (xx * xx + zz * zz)
                    z1 = -yy * zz / (xx * xx + zz * zz)

                sensor_scale_max = max(self.less_scene.get_sensor().sub_region_width, self.less_scene.get_sensor().sub_region_height)
                to_world_dict = {
                    'to_world': mi.ScalarTransform4f().look_at(
                        origin=[x, y, z],
                        target=[target_x, target_y, target_z],
                        up=[x1, 1, z1]
                    ) @ mi.ScalarTransform4f().scale(
                        [sensor_scale_max * 0.5, sensor_scale_max * 0.5, 1])
                }
                sensor_dict["to_world"] = to_world_dict["to_world"]
                # print(sensor_dict)
                sensors.append(mi.load_dict(sensor_dict))
        elif self.less_scene.get_sensor().sensor_type == "perspective":
            if len(diff_render_config.ref_brf_image_path) == 1 and len(
                    diff_render_config.sensor_observation_perspective) == 0:
                diff_render_config.sensor_observation_perspective.append(
                    [self.less_scene.get_observation().obs_o_x, self.less_scene.get_observation().obs_o_y,
                     self.less_scene.get_observation().obs_o_z,
                     self.less_scene.get_observation().obs_t_x, self.less_scene.get_observation().obs_t_y,
                     self.less_scene.get_observation().obs_t_z])

            if len(diff_render_config.ref_brf_image_path) == len(diff_render_config.sensor_observation_perspective):
                pass
            else:
                raise Exception("The number of images does not match the number of perspective angles")
            for sensor_obs_xyz_target_xyz in diff_render_config.sensor_observation_perspective:
                obs_o_x = sensor_obs_xyz_target_xyz[0]
                obs_o_y = sensor_obs_xyz_target_xyz[1]
                obs_o_z = sensor_obs_xyz_target_xyz[2]
                obs_t_x = sensor_obs_xyz_target_xyz[3]
                obs_t_y = sensor_obs_xyz_target_xyz[4]
                obs_t_z = sensor_obs_xyz_target_xyz[5]
                scene_width = self.less_scene.get_landscape().get_terrain().extent_width
                scene_height = self.less_scene.get_landscape().get_terrain().extent_height

                x = scene_width * 0.5 - obs_o_x
                z = scene_height * 0.5 - obs_o_y
                y = obs_o_z
                target_x = scene_width * 0.5 - obs_t_x
                target_y = obs_t_z
                target_z = scene_height * 0.5 - obs_t_y
                if self.less_scene.get_observation().relative_height:
                    raise Exception("Relative height is not supported")
                    # y += self.getCameraAltitudeHeight(main_scene_xml_file_prifix, x, z)
                    # target_y += self.getCameraAltitudeHeight(main_scene_xml_file_prifix, x, z)
                phi = -(180 - 90) / 180.0 * np.pi

                if abs(x - target_x) < 0.00000001 and abs(z - target_z) < 0.00000001:
                    x1 = np.cos(phi)
                    z1 = -np.sin(phi)
                    # lookat_node.setAttribute("up", "%.5f" % upx + "," + "0" + "," + "%.5f" % upz)
                    # raise Exception("camera position and target position are the same, please check the camera position and target position")
                else:
                    xx, yy, zz = target_x - x, target_y - y, target_z - z
                    x1 = -xx * yy / (xx * xx + zz * zz)
                    z1 = -yy * zz / (xx * xx + zz * zz)

                to_world_dict = {
                    'to_world': mi.ScalarTransform4f().look_at(
                        origin=[x, y, z],
                        target=[target_x, target_y, target_z],
                        up=[x1, 1, z1]
                    )
                }

                sensor_dict["to_world"] = to_world_dict["to_world"]
                # print(sensor_dict)
                sensors.append(mi.load_dict(sensor_dict))
        else:
            raise Exception("Sensor type is not supported")

        # mi.xml.dict_to_xml(scene_dict, (os.path.join(self.less_scene.get_sim().get_parameters_dir(), "_scenefile", "LESS3.xml")))
        # del scene_dict['terrain']
        per_optimize_result_dir = diff_render_config.result_dir_path
        optimize_spp = diff_render_config.optimize_spp

        if not os.path.exists(per_optimize_result_dir):
            os.makedirs(per_optimize_result_dir)

        diff_render_log = Utils.use_log(per_optimize_result_dir, "diff_render_log")

        spectral_bands = list(map(lambda x: float(x.split(":")[0]),
                                  self.less_scene.get_sim().get_scene().get_sensor().get_spectral_bands().split(
                                      ",")))

        origin_params_result = {'wavelength': spectral_bands}
        optimize_params_result = {'wavelength': spectral_bands}

        optimize_params = diff_render_config.optimize_params

        all_optimize_spectral_params = []
        optimize_spectral_params_output_names = []
        all_optimize_spectral_params_first_item = []



        scene = mi.load_dict(scene_dict)
        params = mi.traverse(scene)
        # 调试测试=============================================
        # print(params)
        # =============================================
        if len(spectral_bands) > 1:
            params.keep(['.*\.*\.values'])
            # params.keep(['.*\.*\.values', '.*\.*\.value', '.*\.*\.data'])
            # print(params)
        else:
            params.keep(['.*\.*\.value'])
            # params.keep(['.*\.*\.value', '.*\.*\.data'])
            # print(params)
        # 调试测试=============================================
        # print(params)
        # =============================================

        for every_spectral_param in params:
            first_spectral_keys = every_spectral_param[0]
            first_spectral_keys_length = len(first_spectral_keys.split("."))
            first_item = first_spectral_keys.split(".")[0]
            # 自行调整想要优化的参数
            if first_item == 'sensor' or first_item == 'emitter':
                continue
            second_item = first_spectral_keys.split(".")[1]
            third_item = first_spectral_keys.split(".")[2]
            all_optimize_spectral_params.append(first_spectral_keys)
            all_optimize_spectral_params_first_item.append(first_item)
            if first_spectral_keys_length == 3:
                optimize_spectral_params_output_names.append(first_item + "_Reflectance(Front)")
                pass
            elif first_spectral_keys_length == 4:
                if third_item == 'base_color':
                    optimize_spectral_params_output_names.append(first_item + "_Transmittance")
                elif second_item == 'brdf_0' and third_item == 'reflectance':
                    optimize_spectral_params_output_names.append(first_item + "_Reflectance")
                elif second_item == 'brdf_1' and third_item == 'reflectance':
                    optimize_spectral_params_output_names.append(first_item + "_Reflectance(Back)")

                    temp_index = optimize_spectral_params_output_names.index(first_item + "_Reflectance")
                    optimize_spectral_params_output_names[temp_index] = first_item + "_Reflectance(Front)"
                    raise Exception("currently, not test")
                pass
            elif first_spectral_keys_length == 5:
                if third_item == 'brdf_0':
                    optimize_spectral_params_output_names.append(first_item + "_Reflectance")
                elif third_item == 'brdf_1':
                    optimize_spectral_params_output_names.append(first_item + "_Reflectance(Back)")
                    temp_index = optimize_spectral_params_output_names.index(first_item + "_Reflectance")
                    optimize_spectral_params_output_names[temp_index] = first_item + "_Reflectance(Front)"
                    raise Exception("currently, not test")
                pass

        if len(optimize_params) == 0:
            optimize_params = all_optimize_spectral_params
        elif len(optimize_params) > 0:
            if all(item in set(all_optimize_spectral_params_first_item) for item in optimize_params) is not True:
                raise Exception("your input of optimized parameters has error")
            select_optimize_params_temp = []
            select_optimize_params_output_names_temp = []
            # for i, per_optimize_spectral_param in enumerate(all_optimize_spectral_params):
            #     # birch_branch.reflectance.values = per_optimize_spectral_param
            #     if per_optimize_spectral_param.split(".")[0] in set(optimize_params):
            #         select_optimize_params_temp.append(per_optimize_spectral_param)
            #     else:
            #         optimize_spectral_params_output_names.remove(i)
            for i in range(len(optimize_params)):
                # optimize_params[i]
                for index, value in enumerate(all_optimize_spectral_params_first_item):
                    if value == optimize_params[i]:
                        select_optimize_params_temp.append(all_optimize_spectral_params[index])
                        select_optimize_params_output_names_temp.append(optimize_spectral_params_output_names[index])

            optimize_params = select_optimize_params_temp
            optimize_spectral_params_output_names = select_optimize_params_output_names_temp

        # 测试用===========================================
        # optimize_spectral_params_output_names = ["bitmap_texture"]
        # ===========================================

        if diff_render_config.use_field_data_simplify_opt:
            transmittance_indexs = []
            transmittance_names = []
            transmittance_to_reflectance_index = []
            for index, opt_param in enumerate(optimize_spectral_params_output_names):
                if opt_param.rsplit('_', 1)[1] == 'Transmittance':
                    transmittance_indexs.append(index)
                    transmittance_names.append(opt_param.rsplit('_', 1)[0])
            for transmittance_param in transmittance_names:
                for index, opt_param in enumerate(optimize_spectral_params_output_names):
                    if opt_param.rsplit('_', 1)[0] == transmittance_param:
                        if opt_param.rsplit('_', 1)[1] == 'Reflectance' or opt_param.rsplit('_', 1)[1] == 'Reflectance(Front)':
                            transmittance_to_reflectance_index.append(index)
            del transmittance_names
            if len(transmittance_indexs)==0 or len(transmittance_to_reflectance_index)==0:
                diff_render_config.use_field_data_simplify_opt = False

        if len(diff_render_config.shuffle_value_range) == 2:
            shuffle_low_value = diff_render_config.shuffle_value_range[0]
            shuffle_high_value = diff_render_config.shuffle_value_range[1]
        else:
            shuffle_low_value = 0.1
            shuffle_high_value = 0.2
        import random
        for i in range(len(optimize_params)):
            # print(optimize_params[i], params[optimize_params[i]])
            origin_params_result[optimize_spectral_params_output_names[i]] = dr.cuda.ad.Float.copy_(params[optimize_params[i]])
            # origin_params_result[optimize_spectral_params_output_names[i]] = dr.eval(dr.copy(params[optimize_params[i]]))
            if diff_render_config.resume is False and diff_render_config.shuffle_spectral_values is True:
                params[optimize_params[i]] = [random.uniform(shuffle_low_value, shuffle_high_value) for _ in range(len(spectral_bands))]
                pass
            elif diff_render_config.resume is True:
                # df = pd.DataFrame()
                # df = load_excel_file(df, diff_render_config.resume_xlsx_name)
                df = pd.read_excel(diff_render_config.resume_xlsx_name)
                params[optimize_params[i]] = np.array(df[optimize_spectral_params_output_names[i]])
                # print('加载后的参数', optimize_params[i], params[optimize_params[i]])
                ## =================================下面这里自行添加测试===============================##
                # params[optimize_params[2]] = [random.uniform(0.1, 0.2) for _ in range(len(spectral_bands))]

                ## =================================添加测试结束===============================##


        origin_params_DataFrame = pd.DataFrame(origin_params_result)
        origin_params_DataFrame.to_excel(per_optimize_result_dir + '/origin_params.xlsx', index=False)

        params.update()  # 更新成更改后的参数

        ## =================================下面这里自行添加测试===============================##
        # optimize_params = optimize_params[2:]
        # optimize_spectral_params_output_names = optimize_spectral_params_output_names[2:]

        ## =================================添加测试结束===============================##

        # load BRF image
        ref_brf_images = []
        for image_index in diff_render_config.ref_brf_image_path:
            if isinstance(image_index, str):
                ref_brf_image, image_height, image_width = Utils.load_RS_image(image_index)
                ref_brf_image = dr.cuda.ad.TensorXf(ref_brf_image)
                ref_brf_images.append(ref_brf_image)
            elif isinstance(image_index, np.ndarray):
                image_height = image_index.shape[0]
                image_width = image_index.shape[1]
                ref_brf_image = dr.cuda.ad.TensorXf(image_index)
                ref_brf_images.append(ref_brf_image)
            else:
                raise Exception("参考影像输入有误")

        # 读取几何条件，这里太阳天顶角
        solar_zenith_angle_rad = np.deg2rad(self.less_scene.get_illumination().sun_zenith)
        # 计算余弦值
        cos_solar_zenith = np.cos(solar_zenith_angle_rad)
        # 太阳BOA辐照度other format
        # BOA_sun_irradiance = np.array([float(x) * cos_solar_zenith for x in scene_dict["emitter"]['irradiance']['values'].split(',')])
        # 可以选择读取irradiance.txt,目前没有加,之后可以改
        if not isinstance(scene_dict["emitter"]['irradiance']['value'], float):
            BOA_sun_irradiance = np.array(
                [float(x[1]) * cos_solar_zenith for x in scene_dict["emitter"]['irradiance']['value']])
        else:
            BOA_sun_irradiance = np.array([scene_dict["emitter"]['irradiance']['value'] * cos_solar_zenith])
        BOA_irradiance = BOA_sun_irradiance
        if "emitter_sky" in scene_dict:
            if not isinstance(scene_dict["emitter_sky"]['radiance']['value'], float):
                BOA_sky_irradiance = np.array(
                    [float(x[1]) * math.pi for x in scene_dict["emitter_sky"]['radiance']['value']])
            else:
                BOA_sky_irradiance = np.array([scene_dict["emitter_sky"]['radiance']['value'] * math.pi])
            BOA_irradiance += BOA_sky_irradiance
        # 将一维数组重塑为形状为[1, 13]的二维数组
        reshaped_array = BOA_irradiance.reshape(1, -1)
        # 将二维数组在第一个维度（行）上重复500*500次，形成形状为[500*500, 13]的数组
        tiled_array = np.tile(reshaped_array,(image_height * image_width, 1))
        # 将结果重塑为形状为[500, 500, 13]的三维数组
        final_array = tiled_array.reshape(image_height, image_width, len(BOA_irradiance))
        final_irradiance_tensorxf = dr.cuda.ad.TensorXf(final_array)
        # final_irradiance_tensorxf = dr.scalar.TensorXf(final_array)

        opt_temp_images = [mi.render(scene, sensor=sensor) * dr.pi for sensor in sensors]
        opt_brf_images = [opt_temp_image / final_irradiance_tensorxf for opt_temp_image in opt_temp_images]

        for i in range(len(diff_render_config.ref_brf_image_path)):
            Utils.save_image_as_envi(np.array(ref_brf_images)[i], os.path.join(per_optimize_result_dir, f"ref_brf_{i}"))
            Utils.save_image_as_envi(np.array(opt_brf_images)[i], os.path.join(per_optimize_result_dir, f"opt_brf_init_{i}"))

        if image_height == 1 and image_width == 1:
            pass
        else:
            for i in range(len(diff_render_config.ref_brf_image_path)):
                if len(spectral_bands) < 3:
                    mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"ref_image_band-1_epoch-{init_epoch}-{stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"), np.array(ref_brf_images)[i][:, :, 0])
                    mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"init_image_band-1_epoch-{init_epoch}-{stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"), np.array(opt_brf_images)[i][:, :, 0])
                else:
                    if len(diff_render_config.image_bands_show) == 3:
                        mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"ref_image_band-3_epoch-{init_epoch}-{stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"),
                                             np.array(ref_brf_images)[i][:, :, [diff_render_config.image_bands_show[0], diff_render_config.image_bands_show[1], diff_render_config.image_bands_show[2]]])
                        mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"init_image_band-3_epoch-{init_epoch}-{stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"),
                                             np.array(opt_brf_images[i])[:, :, [diff_render_config.image_bands_show[0], diff_render_config.image_bands_show[1], diff_render_config.image_bands_show[2]]])
                    else:
                        mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"ref_image_band-3_epoch-{init_epoch}-{stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"), np.array(ref_brf_images)[i][:, :, [2,1,0]])
                        mi.util.write_bitmap(os.path.join(per_optimize_result_dir, f"init_image_band-3_epoch-{init_epoch}-{stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"), np.array(opt_brf_images)[i][:, :, [2,1,0]])

                # if not os.path.exists(os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison")):
                #     os.makedirs(os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison"))
                # Utils.brf_image_pixel_scatter_plot(np.array(ref_brf_images[i]), np.array(opt_brf_images[i]),
                #                                    save_path=os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison",
                #                                                           f'init_Image_Camparison_result_epoch-{init_epoch}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png'))

                # if len(diff_render_config.image_diff_abs_bands) > 0:
                #     for k in diff_render_config.image_diff_abs_bands:
                #         Utils.image_diff_abs_plot(np.array(ref_brf_images[i][:,:,k]), np.array(opt_brf_images[i][:,:,k]), os.path.join(per_optimize_result_dir,
                #                                                                                                                        "Image_Pixel_Comparison",
                #                                                                                                                        f"init_per_pixel_diffabs_epoch-{init_epoch}_band{k+1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"))


        opt = mi.ad.Adam(lr=diff_render_config.initial_learning_rate, mask_updates=True)
        # opt = mi.ad.Adam(lr=diff_render_config.initial_learning_rate, mask_updates=False)

        for i in range(len(optimize_params)):
            opt[optimize_params[i]] = params[optimize_params[i]]

        params.update(opt)
        all_epoch_all_params_every_bands_rmse = []
        loss_list = []
        lowest_loss = 10000
        best_epoch = 0
        for it in range(diff_render_config.init_epoch, diff_render_config.stop_epoch):
            #     for m in range(len(optimize_param)):
            #         opt.set_learning_rate({optimize_param[m]: lr * forward_grad_factor[m]})

            # Perform a (noisy) differentiable rendering of the scene
            print(f'第{it}轮')
            diff_render_log.info(f'第{it}轮,开始渲染 ')
            total_loss = mi.Float(0.0)
            # Evaluate the objective function from the current rendered image
            for sensor_ind in range(len(sensors)):
                image_radiance = mi.render(scene, params, spp=diff_render_config.optimize_spp, sensor=sensors[sensor_ind])
                opt_brf_image = (image_radiance * dr.pi) / final_irradiance_tensorxf
                diff_render_log.info(' 计算损失 ')
                loss = dr.mean(dr.sqr(opt_brf_image - ref_brf_images[sensor_ind]))

                # Backpropagate through the rendering process
                diff_render_log.info('开始反向传播')
                dr.backward(loss)

                # diff_render_log.info('计算新的参数')
                opt.step()
                # print('loss',loss)
                # print('loss[0]',loss[0])

                total_loss += loss
            #     print('total_loss',total_loss)
            # print('total_loss', total_loss)
            if total_loss[0] < lowest_loss:
                lowest_loss = total_loss[0]
                best_epoch = it

            # Optimizer: take a gradient descent step

            # Post-process the optimized parameters to ensure legal color values.
            # diff_render_log.info('限制参数大小')
            for j in range(len(optimize_params)):
                opt[optimize_params[j]] = dr.clamp(opt[optimize_params[j]], 0.0 + random.uniform(0.00001, 0.00002),
                                                  1 - random.uniform(0.00001, 0.00002))

            # diff_render_log.info('加载新的参数')
            params.update(opt)

            # print(f"{optimize_param[i]}:grad={dr.grad(opt[optimize_param[i]])}")
            # opt.reset(optimize_param[i])
            if diff_render_config.use_field_data_simplify_opt:
                # params[f'mean_leaf{i}.bsdf_1.base_color.values'] = [x for x in
                #                                                     params[optimize_param[i - 1]]]
                for trans_index in range(len(transmittance_indexs)):
                    # params[optimize_params[transmittance_indexs[trans_index]]] = params[optimize_params[transmittance_to_reflectance_index[trans_index]]]
                    params[optimize_params[transmittance_indexs[trans_index]]] = np.clip(params[optimize_params[transmittance_indexs[trans_index]]],
                                                                                         params[optimize_params[transmittance_to_reflectance_index[trans_index]]] - diff_render_config.simplify_opt_limit[0],
                                                                                         params[optimize_params[transmittance_to_reflectance_index[trans_index]]] + diff_render_config.simplify_opt_limit[1]
                                                                                         )

            current_epoch_all_params_every_bands_rmse = [0] * len(spectral_bands)
            current_epoch_all_params_every_bands_rrmse = [0] * len(spectral_bands)
            if it % 1 == 0:
                # diff_render_log.info('将新参数写入excel中')
                params_diff_value = 0.000000
                for i in range(len(optimize_params)):
                    # print(optimize_param[i], params[optimize_param[i]])
                    optimize_params_result[optimize_spectral_params_output_names[i]] = dr.cuda.ad.Float.copy_(params[optimize_params[i]])  # mit3.5
                    # optimize_params_result[optimize_spectral_params_output_names[i]] = dr.copy(params[optimize_params[i]])
                    # print(type(params[optimize_param[i]]), type(true_params_result[optimize_param[i]]))
                    # optimize_params_result[optimize_param[i]] = params[optimize_param[i]]
                    if diff_render_config.is_open_comparison_between_opt_and_origin:
                        temp_value = optimize_params_result[optimize_spectral_params_output_names[i]] - origin_params_result[
                            optimize_spectral_params_output_names[i]]

                        params_diff_value = max(max(abs(temp_value)), params_diff_value)
                        current_epoch_all_params_every_bands_rmse = [current_epoch_all_params_every_bands_rmse[i_band] + (temp_value[i_band]**2) for i_band in range(len(spectral_bands))]
                        current_epoch_all_params_every_bands_rrmse = [current_epoch_all_params_every_bands_rrmse[i_band] + (optimize_params_result[optimize_spectral_params_output_names[i]][i_band]**2) for i_band in range(len(spectral_bands))]
                if diff_render_config.is_open_comparison_between_opt_and_origin:
                    current_epoch_all_params_every_bands_rrmse = [np.sqrt((current_epoch_all_params_every_bands_rmse[i_band]/len(optimize_params)/current_epoch_all_params_every_bands_rrmse[i_band])) for i_band in range(len(spectral_bands))]
                    current_epoch_all_params_every_bands_rmse = [
                        np.sqrt(current_epoch_all_params_every_bands_rmse[i_band] / len(optimize_params)) for i_band in
                        range(len(spectral_bands))]

                    diff_render_log.info(f"params_diff_value: {params_diff_value}")
                optimize_params_result1 = pd.DataFrame(optimize_params_result)
                optimize_params_result1.to_excel(per_optimize_result_dir + '/optimize_params_' + str(it) + '.xlsx',
                                                 index=False)

                # print(optimize_param[i - 1], params[optimize_param[i - 1]])
                # print(f'mean_leaf{i}.bsdf_1.base_color.values', params[f'mean_leaf{i}.bsdf_1.base_color.values'])
            # if diff_render_config.use_field_data_simplify_opt:
            #     # params[f'mean_leaf{i}.bsdf_1.base_color.values'] = [x for x in
            #     #                                                     params[optimize_param[i - 1]]]
            #     for trans_index in range(len(transmittance_indexs)):
            #         params[optimize_params[transmittance_indexs[trans_index]]] = params[
            #             optimize_params[transmittance_to_reflectance_index[trans_index]]]

            # Track the difference between the current color and the true value
            if diff_render_config.is_open_comparison_between_opt_and_origin:
                all_epoch_all_params_every_bands_rmse.append(current_epoch_all_params_every_bands_rmse)
                diff_render_log.info(f"当前各波段rmse:\n{current_epoch_all_params_every_bands_rmse}")
                diff_render_log.info(f"当前各波段rrmse:\n{current_epoch_all_params_every_bands_rrmse}")
            loss_list.append(total_loss[0])
            diff_render_log.info(f"已完成第{it}轮的迭代，total_loss = {total_loss[0]:.15f}\n")

        print('\nOptimization complete.')
        diff_render_log.info(f"\nbest_epoch = {best_epoch}  lowest_loss = {lowest_loss}")
        diff_render_log.info(f"\nOptimization complete.")

        # plot rmse for different bands if is_open_comparison_between_opt_and_origin=True
        if False:
            print("Start generating RMSE iteration graph")
            if not os.path.exists(os.path.join(per_optimize_result_dir, "Parameters_RMSE_linegraph")):
                os.makedirs(os.path.join(per_optimize_result_dir, "Parameters_RMSE_linegraph"))

            all_epoch_all_params_every_bands_rmse = np.array(all_epoch_all_params_every_bands_rmse)
            every_band_epochs_rmse = {}
            # for i in range(len(spectral_bands)):
            #     every_band_epochs_rmse[f"band{i+1}"] = all_epoch_all_params_every_bands_rmse[:, i]
            #     plt.figure(figsize=(12, 10))
            #     plt.plot([k for k in range(0, diff_render_config.stop_epoch - diff_render_config.init_epoch)], every_band_epochs_rmse[f"band{i+1}"])
            #     # plt.plot([x_min, x_max],
            #     #          [y_min, y_max], color='green', linestyle='-', label='1:1 line')
            #     plt.title(f'Parameters RMSE', font='Times New Roman', fontsize=30)
            #     plt.xlabel('Iteration', font='Times New Roman', fontsize=30)
            #     plt.ylabel('RMSE', font='Times New Roman', fontsize=30)
            #     plt.xticks(font='Times New Roman', fontsize=26)
            #     plt.yticks(font='Times New Roman', fontsize=26)
            #     plt.savefig(os.path.join(per_optimize_result_dir, 'Parameters_RMSE_linegraph', f'Band{i+1}_Parameters_RMSE_{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}'), dpi=600)
            #     # 关闭图形
            #     plt.close()

            plt.figure(figsize=(12, 10))
            plt.title(f'All Bands Parameters RMSE', font='Times New Roman', fontsize=30)
            plt.xlabel('Iteration', font='Times New Roman', fontsize=30)
            plt.ylabel('RMSE', font='Times New Roman', fontsize=30)
            plt.xticks(font='Times New Roman', fontsize=26)
            plt.yticks(font='Times New Roman', fontsize=26)
            color = [
                '#0000FF', '#00FF00', '#FF0000', '#FFFF00', '#00FFFF', '#FF00FF',
                '#800000', '#008000', '#000080', '#808000', '#008080', '#800080',
                '#FF6666', '#66FF66', '#6666FF', '#99FFFF', '#66FFFF', '#CC6640',
                '#996633', '#339966', '#663399', '#339933', '#993399', '#339999',
                '#FFCC99', '#99FFCC', '#CC99FF', '#FFCC66', '#66FFCC', '#CC66FF',
                '#CC9966', '#66CC99', '#9966CC', '#CC9966', '#66CC99', '#000000',
                '#FF9999', '#99FF99', '#9930FF', '#FFFF99', '#9948FF', '#FF99FF',
                # 补充的颜色
                '#FF5733', '#33FF57', '#3357FF', '#F3FF33', '#33FFF3', '#F333FF',
                '#804000', '#408000', '#004080', '#800040', '#400080', '#008040',
                '#FFA500', '#00A5FF', '#A500FF', '#FF00A5', '#00FFA5', '#A5FF00',
                '#8B4513', '#458B00', '#008B8B', '#8B008B', '#8B0000', '#008B00',
                '#CD5C5C', '#5CCD5C', '#5C5CCD', '#CDCD5C', '#5CCDCD', '#CD5CCD',
                '#D2691E', '#69D21E', '#1E69D2', '#D21E69', '#1ED269', '#691ED2',
                # 补充的颜色
                '#FFE4E1', '#E6E6FA', '#FFF0F5', '#F0F8FF', '#F5F5F5', '#F5F5DC', '#F0FFF0', '#F0FFFF',
                '#F8F8FF', '#FFFACD', '#FAFAD2', '#DCDCDC', '#E0FFFF', '#FAEBD7', '#FFEFD5', '#FFE4B5',
                '#FFDEAD', '#F5DEB3', '#DEB887', '#D2B48C', '#BC8F8F', '#F4A460', '#DAA520', '#B8860B',
                '#CD853F', '#D2691E', '#8B4513', '#A0522D', '#A52A2A', '#8B0000', '#800000', '#FF6347',
                '#FF4500', '#FF8C00', '#FFA500', '#FFD700', '#FFFF00', '#FFFFE0', '#FFFACD', '#FAFAD2',
                '#FFFFF0', '#F0FFF0', '#7CFC00', '#7FFF00', '#ADFF2F', '#00FF00', '#32CD32', '#98FB98',
                '#90EE90', '#8FBC8F', '#3CB371', '#2E8B57', '#228B22', '#008000', '#006400', '#9ACD32',
                '#6B8E23', '#556B2F', '#808000', '#BDB76B', '#F0E68C', '#FFFFE0', '#00CED1', '#40E0D0',
                '#48D1CC', '#00FFFF', '#00FFFF', '#E0FFFF', '#AFEEEE', '#7FFFD4', '#4682B4', '#B0C4DE',
                '#87CEFA', '#87CEEB', '#00BFFF', '#1E90FF', '#ADD8E6', '#87CEEB', '#0000CD', '#00008B',
                '#000080', '#191970', '#4169E1', '#6495ED', '#87CEFA', '#B0C4DE', '#4682B4', '#5F9EA0',
                '#6495ED', '#1E90FF', '#7B68EE', '#9370DB', '#8A2BE2', '#9400D3', '#800080', '#4B0082',
                '#800080', '#D8BFD8', '#DDA0DD', '#EE82EE', '#FF00FF', '#FF00FF', '#DA70D6', '#C71585',
                '#DB7093', '#FF69B4', '#FFB6C1', '#FFC0CB', '#FA8072', '#FF6347', '#FF4500', '#FF8C00',
                '#FFA500', '#FFD700', '#FFFF00', '#9ACD32', '#32CD32', '#00FF00', '#00CED1', '#1E90FF',
                '#9370DB', '#FF69B4', '#8B4513', '#F4A460', '#DAA520', '#B8860B', '#CD853F', '#D2691E'
            ]
            for i in range(len(spectral_bands)):
                every_band_epochs_rmse[f"band{i + 1}"] = all_epoch_all_params_every_bands_rmse[:, i]
                plt.plot([k for k in range(0, diff_render_config.stop_epoch - diff_render_config.init_epoch)],
                         every_band_epochs_rmse[f"band{i + 1}"], color=color[i], label=f"band{i+1}")

            # 创建一个FontProperties对象来指定字体属性
            from matplotlib.font_manager import FontProperties
            legend_props = FontProperties(family='Times New Roman', size=19)
            # 添加图例
            plt.legend(prop=legend_props)
            plt.savefig(os.path.join(per_optimize_result_dir, 'Parameters_RMSE_linegraph', f'AllBand_Parameters_RMSE_{diff_render_config.init_epoch}-{diff_render_config.stop_epoch - 1}'),
                        dpi=600)
            plt.close()
            print("RMSE iteration graph generated successfully")

        print(f"generate some image")

        plt.figure(figsize=(10, 8))
        plt.title(f'Loss', font='Times New Roman', fontsize=30)
        plt.xlabel('Iteration', font='Times New Roman', fontsize=30)
        plt.ylabel('MSE(Loss)', font='Times New Roman', fontsize=30)
        plt.xticks(font='Times New Roman', fontsize=26)
        plt.yticks(font='Times New Roman', fontsize=26)
        # plt.plot([k for k in range(diff_render_config.init_epoch, diff_render_config.stop_epoch)],
        #          loss_list)
        plt.plot([k for k in range(0, diff_render_config.stop_epoch - diff_render_config.init_epoch)],
                 loss_list)
        plt.savefig(os.path.join(per_optimize_result_dir, 'Loss'), dpi=600)

        plt.close()

        images_radiance = [mi.render(scene, params, sensor=sensor) for sensor in
                           sensors]
        # Evaluate the objective function from the current rendered image
        opt_brf_images = [(image_radiance * dr.pi) / final_irradiance_tensorxf for image_radiance in images_radiance]

        for i in range(len(diff_render_config.ref_brf_image_path)):
            Utils.save_image_as_envi(np.array(opt_brf_images)[i], os.path.join(per_optimize_result_dir, f"opt_brf_final_{i}"))

        if image_height == 1 and image_width == 1:
            pass
        else:
            for i in range(len(diff_render_config.ref_brf_image_path)):

                # Utils.brf_image_pixel_scatter_plot(np.array(ref_brf_images[i]), np.array(opt_brf_images[i]),
                #                                    save_path=os.path.join(per_optimize_result_dir, "Image_Pixel_Comparison",
                #                                                           f'final_Image_Camparison_result_epoch-{diff_render_config.stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png'))

                # if len(diff_render_config.image_diff_abs_bands) > 0:
                #     for k in diff_render_config.image_diff_abs_bands:
                #         Utils.image_diff_abs_plot(np.array(ref_brf_images[i][:,:,k]), np.array(opt_brf_images[i][:,:,k]), os.path.join(per_optimize_result_dir,
                #                                                                                                                        "Image_Pixel_Comparison",
                #                                                                                                                        f"final_per_pixel_diffabs_epoch-{diff_render_config.stop_epoch-1}_band{k+1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"))

                if len(spectral_bands) < 3:
                    mi.util.write_bitmap(os.path.join(per_optimize_result_dir,
                                                      f"final_image_band-1_epoch-{diff_render_config.stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"),
                                         opt_brf_images[i][:, :, 0])
                else:
                    if len(diff_render_config.image_bands_show) == 3:
                        mi.util.write_bitmap(os.path.join(per_optimize_result_dir,
                                                          f"final_image_band-3_epoch-{diff_render_config.stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"),
                                             opt_brf_images[i][:, :, [diff_render_config.image_bands_show[0], diff_render_config.image_bands_show[1], diff_render_config.image_bands_show[2]]])
                    else:
                        mi.util.write_bitmap(os.path.join(per_optimize_result_dir,
                                                          f"final_image_band-3_epoch-{diff_render_config.stop_epoch - 1}_VZ{diff_render_config.sensor_observation_Zenith_Azimuth[i][0]}_VA{diff_render_config.sensor_observation_Zenith_Azimuth[i][1]}.png"),
                                             opt_brf_images[i][:, :, [2,1,0]])


        print("successful")

    def __load_less3scene_dict(self):

        Illumination = LESS3Illumination(self.less_scene.get_illumination())
        scene = {
            "type": "scene",
            "integrator": {
                "type": "path",
                "max_depth": 100,
                "rr_depth": 5,
                "hide_emitters": True
            },
            "sensor": LESS3Sensor(self.less_scene.get_sensor()).get_dict(),
            "emitter": Illumination.get_sun_dict(),
        }
        # temp_test = mi.load_dict(LESS3Sensor(self.less_scene.get_sensor()).get_dict())
        # temp_test = mi.load_dict(LESS3Illumination(self.less_scene.get_illumination()).get_dict())
        shape_group_list, instance_list, terrain_dict, spectrum_dict_list = LESS3Landscape(self.less_scene.get_landscape()).get_dict()
        for spectrum_dict in spectrum_dict_list:
            for spectrum_name in spectrum_dict:
                scene[spectrum_name] = spectrum_dict[spectrum_name]
        shapegroup_prefixes_set = set()
        for shape_group in shape_group_list:
            for shape_group_name in shape_group:
                scene[shape_group_name] = shape_group[shape_group_name]
                shapegroup_prefixes_set.add(shape_group_name.split('_')[0])
        instance_prefixes = set()
        for instance in instance_list:
            for instance_name in instance:
                scene[instance_name] = instance[instance_name]
                instance_prefixes.add(instance_name.split('_')[0])
        shapegroup_to_delete = shapegroup_prefixes_set - instance_prefixes
        for shapegroup_prefix in shapegroup_to_delete:
            del scene[f"{shapegroup_prefix}_shapegroup"]



        for terrain_name in terrain_dict:
            scene[terrain_name] = terrain_dict[terrain_name]

        # Illumination.sky_irr = [(600, 0.5),(900, 0.3)]
        if all(v > 0 for _, v in Illumination.sky_irr):
            scene["emitter_sky"] = Illumination.get_sky_dict()
            band_num = len(Illumination.sun_irr)
            temp_spectrum = [(a, np.random.uniform(1e-8, 2e-8)) for a, _ in Illumination.sun_irr]
            terrain_dict_temp = {
                "type": "rectangle",
                "bsdf": {
                    'type': 'spectrum',
                    'value': temp_spectrum
                },
                'to_world': mi.ScalarTransform4f().rotate([1, 0, 0], -90).scale(
                    [10000000000000000, 10000000000000000, 1]).translate([0, -0.01, 0]),
                'flip_normals': True
            }
            scene["terrain_sky"] = terrain_dict_temp


        # if all(abs(x) > 1e-9 for x in Illumination.sky_irr):


        # 450:1,560:1,650:1,730:1,840:1
        # texture_data = np.random.rand(100, 100, 3).astype(np.float32)
        # texture_data[:, :, :] = 1.0
        # print(texture_data)
        # 生成数值从1-50000的100，100，5的
        # texture_data[:, :, :] = 0.0
        # texture_dict_bitmap = {
        #     'type': 'gridvolume',
        #     'raw': True,
        #     'data': texture_data
        # }
        # max_extent = max(self.less_scene.get_landscape().get_terrain().get_extent_height() * 0.5, self.less_scene.get_landscape().get_terrain().get_extent_width() * 0.5)
        # mi.set_variant("cuda_ad_spectral")

        # scene["emitter1"] = {
        #     'type': 'constant',
        #     'radiance': {
        #         'type': 'irregular',
        #         'wavelengths': '450.0,560.0,650.0,730.0,840.0',
        #         'values': '0.0486,0.1535,0.2280,0.2860,0.3339'
        #     }
        # }

        # scene["sensor"]["to_world"] = mi.ScalarTransform4f().look_at(
        #             origin=[5, 1, 5],
        #             target=[5, 2, 5],
        #             up=[1, 0, 0])

        # print(scene["dark_soil_mollisol"]["reflectance"])
        # scene["emitter2"] = {
        #     'type': 'constant',
        #     'radiance': {
        #         # 'type': 'spectrum',
        #         'value': 1.0,
        #     }
        # }

        return scene


    def __test_LESS3_LESS(self):
        from Utils import Utils
        import matplotlib.pyplot as plt
        image_data = Utils.load_RS_image(os.path.dirname(self.less_scene.get_sim().get_dist_file()) + "/" + os.path.basename(self.less_scene.get_sim().get_dist_file()) + "_BRF")
        image_LESS3_brf_ref = Utils.load_RS_image(os.path.dirname(self.less_scene.get_sim().get_dist_file()) + "/" + os.path.basename(self.less_scene.get_sim().get_dist_file()) + "_LESS3" + "_BRF")
        loss = np.mean((image_data - image_LESS3_brf_ref) ** 2)  # TypeError: only length-1 arrays can be converted to Python scalars
        print(loss)
        for i in range(image_data.shape[2]):
            loss = np.mean((image_data[:, :, i] - image_LESS3_brf_ref[:, :, i]) ** 2)
            print(f"band{i+1} mse", loss)
            print(f"band{i+1} rmse:", np.sqrt(loss))

        plt.imshow(image_data[:,:,0]*15, vmin=0, vmax=1, cmap='gray')
        plt.show()
        plt.imshow(image_LESS3_brf_ref[:,:,0]*15, vmin=0, vmax=1, cmap='gray')
        plt.show()

        pass


    def dict_to_xml(self):
        scene_dict = self.__load_less3scene_dict()
        mi.xml.dict_to_xml(scene_dict,
                           (os.path.join(self.less_scene.get_sim().get_parameters_dir(), "_scenefile", "LESS3.xml")))

    def get_dict(self):
        scene_dict = self.__load_less3scene_dict()
        return scene_dict

    # 初始化默认文件名
    def __init_dist_file(self):
        if self.__dist_file != "":
            return
        thermal_img_prefix = "thermal_"
        spectral_img_prefix = "spectral_"
        photon_tracing_img_prefix = "photontracing_"

        distFileName = ""
        imgPrefix = ""
        sensor = self.less_scene.get_sensor()
        obs = self.less_scene.get_observation()
        if sensor.thermal_radiation:
            imgPrefix = thermal_img_prefix
        else:
            imgPrefix = spectral_img_prefix

        if sensor.sensor_type == "orthographic":
            distFileName = imgPrefix + "VZ=" + str(obs.obs_zenith) + \
                           "_VA=" + str(obs.obs_azimuth)
            distFileName = distFileName.replace(".", "_")
        if sensor.sensor_type == "perspective" or sensor.sensor_type == "CircularFisheye":
            ox, oy, oz, tx, ty, tz = obs.obs_o_x, obs.obs_o_y, obs.obs_o_z, obs.obs_t_x, obs.obs_t_y, obs.obs_t_z
            distFileName = imgPrefix + "ox=%.2f_oy=%.2f_oz=%.2f_tx=%.2f_ty=%.2f_tz=%.2f" % (ox, oy, oz, tx, ty, tz)
            distFileName = distFileName.replace(".", "_")

        if sensor.sensor_type == "PhotonTracing":
            distFileName = photon_tracing_img_prefix + str(sensor.sun_ray_resolution).replace(".", "_")
        self.__dist_file = os.path.join(self.less_scene.get_sim().get_sim_dir(), "Results", distFileName)