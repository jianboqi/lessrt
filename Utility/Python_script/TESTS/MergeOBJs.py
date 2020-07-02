import argparse
import glob
import os

if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", nargs='*', help="Input file.", required=True)
    args = parse.parse_args()
    # 文件读入
    input_files = []
    component_num = [0]  # 记录端点编号
    for input_file in args.i:
        input_files += glob.glob(input_file)

    f = open(r'E:\test.obj', 'w')
    # 打开obj文件，存成数组
    for filename in input_files:
        with open(filename) as file_object:
            components = file_object.readlines()
            # 写入组分名称
            (filepath, tempfilename) = os.path.split(filename)
            (file_name, extension) = os.path.splitext(tempfilename)
            file_names = file_name.split('_')
            f.write("g " + str(file_names[1])+"\n")
            # 写入端点坐标以及序号
            i = 0
            for component in components:
                component = component.split()
                if component[0] == 'v':
                    i = i+1
                    component = ' '.join(component) + '\n'
                    f.write(component)
                if component[0] == 'f':
                    component[1] = str(int(component[1]) + int(component_num[-1]))
                    component[2] = str(int(component[2]) + int(component_num[-1]))
                    component[3] = str(int(component[3]) + int(component_num[-1]))
                    component = ' '.join(component) + '\n'
                    f.write(component)
            component_num.append(i)
            print(component_num)
    f.close()