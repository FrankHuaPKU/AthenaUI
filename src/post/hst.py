import os
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore

# 获取当前工作目录
current_dir = os.getcwd()

# 检查当前目录是否为一个合法的 Athena++ case 目录
# 一个简单的检查方法是查看是否存在 'outputs' 子目录
outputs_dir = os.path.join(current_dir, 'outputs')
if not os.path.isdir(outputs_dir):
    print(f"错误：当前目录 '{current_dir}' 不是一个有效的 Athena++ case 目录 (缺少 'outputs' 子目录)。")
    exit(1)

# 获取唯一的 .hst 文件
hst_files = [f for f in os.listdir(outputs_dir) if f.endswith('.hst')]
if not hst_files:
    print(f"错误：在 '{outputs_dir}' 目录下找不到 .hst 文件。")
    exit(1)
if len(hst_files) > 1:
    print(f"警告：在 '{outputs_dir}' 目录下找到多个 .hst 文件，将使用第一个文件：'{hst_files[0]}'")

hst_file = os.path.join(outputs_dir, hst_files[0])

# 读取文件，跳过前两行
try:
    data = np.loadtxt(hst_file, skiprows=2)
except Exception as e:
    print(f"读取文件 '{hst_file}' 时出错: {e}")
    exit(1)

# 提取时间数据
time_data = data[:, 0]  # 第一列是时间

# 提取物理量数据
var_data_list = data[:, 1:]  # 其余列是物理量

# 获取变量名
try:
    with open(hst_file, 'r') as file:
        lines = file.readlines()
    header_line = lines[1].strip()  # 第二行为变量名行，去除首尾空格
    header_items = header_line.strip('# ').split()  # 去除注释符 '#' 并按空格分割
except Exception as e:
    print(f"解析文件 '{hst_file}' 头部时出错: {e}")
    exit(1)

# 提取变量名，跳过时间列的变量名
var_names = []
for item in header_items[1:]:  # 跳过第一个元素，即时间列的变量名
    pos = item.find('=')
    if pos != -1:
        var_name = item[pos+1:]
        var_names.append(var_name)

# 获取当前case目录的名称
case_name = os.path.basename(current_dir)

# 定义输出目录
output_dir = os.path.join(current_dir, "hstPlots")
os.makedirs(output_dir, exist_ok=True)

# 遍历每个物理量并绘图
for i, var_name in enumerate(var_names):
    var_data = var_data_list[:, i]

    if i == 0:
        # 单轴绘图方案（线性坐标）
        plt.figure(figsize=(8, 6))
        plt.plot(time_data, var_data, color='black', linewidth=2, label=f'{var_name}')
        plt.ylim(bottom=0)  # 线性坐标下确保从 0 开始

        plt.xlabel('Time')
        plt.ylabel(var_name)
        plt.title(f'{case_name}')

        # 保存图像
        output_file = f"{var_name}({case_name}).pdf"
        plt.savefig(os.path.join(output_dir, output_file))
        plt.close()

    else:
        # 双轴绘图方案
        fig, ax1 = plt.subplots(figsize=(8, 6))

        # 对数坐标轴（左轴）
        ax1.plot(time_data, var_data, color='gray', linestyle='--', linewidth=2, label='Log Scale')
        ax1.set_xlabel('Time', fontsize=12)
        ax1.set_ylabel(f'{var_name} (Log Scale)', fontsize=12, color='black')
        ax1.set_yscale('log')  # 对数坐标
        ax1.tick_params(axis='y', labelcolor='black')

        # 线性坐标轴（右轴）
        ax2 = ax1.twinx()  # 创建共享 x 轴的副轴
        ax2.plot(time_data, var_data, color='black', linewidth=3, label='Linear Scale')

        # 计算线性坐标轴范围
        linear_max = np.max(var_data[len(var_data) // 2:])  # 后半部分的最大值
        linear_ylim_upper = linear_max * 1.2  # 上限为最大值的 1.5 倍
        # 处理 NaN 或 Inf 值
        if np.isfinite(linear_ylim_upper):
             ax2.set_ylim(bottom=0, top=linear_ylim_upper)
        else:
             ax2.set_ylim(bottom=0) # 如果计算结果无效，则不设置上限

        ax2.set_ylabel(f'{var_name} (Linear Scale)', fontsize=12, color='black')
        ax2.tick_params(axis='y', labelcolor='black')

        # 添加图例
        ax1.legend(loc='lower right', bbox_to_anchor=(1, 0.07))
        ax2.legend(loc='lower right', bbox_to_anchor=(1, 0))

        # 添加标题并调整位置
        # y参数控制标题到顶部的距离，值越小距离越大
        fig.suptitle(f'{case_name}', fontsize=14, y=0.97) 
        plt.subplots_adjust(bottom=0.10, top=0.92)
        # plt.subplots_adjust(top=0.88)  # 调整上边距，为标题留出空间
        # fig.tight_layout()

        # 保存图像
        output_file = f"{var_name}({case_name}).pdf"
        plt.savefig(os.path.join(output_dir, output_file))
        plt.close()

print(f"\nHistory Plots saved.\n")
