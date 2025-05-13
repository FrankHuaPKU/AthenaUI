#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import matplotlib.cm as cm

# 导入athena_read库
athena_path = os.environ.get('ATHENA_PATH', '')
if athena_path:
    sys.path.insert(0, os.path.join(athena_path, 'vis/python'))
    import athena_read
else:
    print("错误：环境变量ATHENA_PATH未设置，无法导入athena_read模块")
    sys.exit(1)

def find_files(outn, t1, t2):
    """查找满足时间区间条件的输出文件"""
    print("正在查询目标输出文件...", flush=True)
    
    # 获取当前路径
    current_path = os.getcwd()
    
    # 构建文件模式
    pattern = os.path.join(current_path, 'outputs', f'*.{outn}.*.athdf')
    
    # 获取所有匹配的文件
    files = glob.glob(pattern)
    if not files:
        print(f"错误：未找到任何与模式 {pattern} 匹配的文件", flush=True)
        return []
    
    # 解析每个文件的时间，筛选满足条件的文件
    filtered_files = []
    times = []
    
    for file in files:
        try:
            data = athena_read.athdf(file)
            time = data['Time']
            
            # 检查时间是否在范围内
            if t1 <= time and (t2 is None or time <= t2):
                filtered_files.append(file)
                times.append(time)
        except Exception as e:
            print(f"警告：读取文件 {file} 时出错：{e}", flush=True)
    
    # 按时间排序
    sorted_indices = np.argsort(times)
    sorted_files = [filtered_files[i] for i in sorted_indices]
    sorted_times = [times[i] for i in sorted_indices]
    
    if not sorted_files:
        print(f"错误：在时间区间 [{t1}, {t2 if t2 is not None else '∞'}] 内未找到任何有效文件", flush=True)
    else:
        print(f"在时间区间 [{t1}, {t2 if t2 is not None else '∞'}] 内找到 {len(sorted_files)} 个文件，开始计算关联函数：\n", flush=True)
    
    return sorted_files, sorted_times[0] if sorted_times else 0, sorted_times[-1] if sorted_times else 0

def calculate_correlation(files, var):
    """计算指定物理量的两点空间自关联函数"""
    if not files:
        return None
    
    all_correlations = []
    
    for file in files:
        try:
            print(f"正在处理：{os.path.basename(file)}", flush=True)
            sys.stdout.flush()  # 强制刷新输出
            # 读取数据
            data = athena_read.athdf(file)
            
            if var == 'rho':
                # 密度自关联函数
                rho = data['rho']
                # 转置数组以匹配 (x, y, z) 顺序
                rho = np.transpose(rho, (2, 1, 0))
                corr = signal.correlate(rho, rho, mode='same', method='auto')
                # 归一化
                corr = corr / corr[corr.shape[0]//2, corr.shape[1]//2, corr.shape[2]//2]
                all_correlations.append(corr)
            
            elif var == 'vel':
                # 速度自关联函数（三分量求和）
                Vx = data['vel1']
                Vy = data['vel2']
                Vz = data['vel3']
                # 转置数组以匹配 (x, y, z) 顺序
                Vx = np.transpose(Vx, (2, 1, 0))
                Vy = np.transpose(Vy, (2, 1, 0))
                Vz = np.transpose(Vz, (2, 1, 0))
                
                corr_x = signal.correlate(Vx, Vx, mode='same', method='auto')
                corr_y = signal.correlate(Vy, Vy, mode='same', method='auto')
                corr_z = signal.correlate(Vz, Vz, mode='same', method='auto')
                
                corr = corr_x + corr_y + corr_z
                # 归一化
                corr = corr / corr[corr.shape[0]//2, corr.shape[1]//2, corr.shape[2]//2]
                all_correlations.append(corr)
            
            elif var == 'B':
                # 磁场自关联函数（三分量求和）
                try:
                    Bx = data['Bcc1']
                    By = data['Bcc2']
                    Bz = data['Bcc3']
                    # 转置数组以匹配 (x, y, z) 顺序
                    Bx = np.transpose(Bx, (2, 1, 0))
                    By = np.transpose(By, (2, 1, 0))
                    Bz = np.transpose(Bz, (2, 1, 0))
                    
                    corr_x = signal.correlate(Bx, Bx, mode='same', method='auto')
                    corr_y = signal.correlate(By, By, mode='same', method='auto')
                    corr_z = signal.correlate(Bz, Bz, mode='same', method='auto')
                    
                    corr = corr_x + corr_y + corr_z
                    # 归一化
                    corr = corr / corr[corr.shape[0]//2, corr.shape[1]//2, corr.shape[2]//2]
                    all_correlations.append(corr)
                except KeyError:
                    # 尝试使用替代变量名
                    try:
                        Bx = data['B1']
                        By = data['B2']
                        Bz = data['B3']
                        # 转置数组以匹配 (x, y, z) 顺序
                        Bx = np.transpose(Bx, (2, 1, 0))
                        By = np.transpose(By, (2, 1, 0))
                        Bz = np.transpose(Bz, (2, 1, 0))
                        
                        corr_x = signal.correlate(Bx, Bx, mode='same', method='auto')
                        corr_y = signal.correlate(By, By, mode='same', method='auto')
                        corr_z = signal.correlate(Bz, Bz, mode='same', method='auto')
                        
                        corr = corr_x + corr_y + corr_z
                        # 归一化
                        corr = corr / corr[corr.shape[0]//2, corr.shape[1]//2, corr.shape[2]//2]
                        all_correlations.append(corr)
                    except KeyError as e:
                        print(f"错误：未找到磁场数据：{e}", flush=True)
        
        except Exception as e:
            print(f"警告：处理文件 {file} 时出错：{e}", flush=True)
    
    # 计算平均关联函数
    if all_correlations:
        corr_avg = np.mean(all_correlations, axis=0)
        return corr_avg
    else:
        return None

def create_directories(t_start, t_end):
    """创建保存图形的目录"""
    output_dir = os.path.join('corrPlots', f'avg({t_start:.2f}-{t_end:.2f})')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def plot_2d_slices(corr, t_start, t_end, case_name, var, Lx, Ly, Lz):
    """绘制2D切片图"""
    if corr is None:
        return
    
    # 获取输出目录
    output_dir = os.path.join('corrPlots', f'avg({t_start:.2f}-{t_end:.2f})')
    
    # 获取数组中心位置
    center = np.array(corr.shape) // 2
    
    # 创建三个切片图
    file_names = [f'{var}-xSlice({t_start:.2f}-{t_end:.2f}).pdf', 
                  f'{var}-ySlice({t_start:.2f}-{t_end:.2f}).pdf', 
                  f'{var}-zSlice({t_start:.2f}-{t_end:.2f}).pdf']
    
    # 为不同切片设置不同的图片比例
    figsize_list = [(10, 4), (10, 8), (10, 4)]  # 分别对应x, y, z切片
    
    for i in range(3):
        plt.figure(figsize=figsize_list[i])
        
        if i == 0:
            # X切片 (YZ平面)
            slice_data = corr[center[0], :, :]
            extent = [-Ly/2, Ly/2, -Lz/2, Lz/2]
            plt.imshow(slice_data, origin='lower', cmap='tab20c', extent=extent, aspect='equal')
            plt.xlabel('Δy')
            plt.ylabel('Δz')
        elif i == 1:
            # Y切片 (XZ平面)
            slice_data = corr[:, center[1], :]
            extent = [-Lx/2, Lx/2, -Lz/2, Lz/2]
            plt.imshow(slice_data, origin='lower', cmap='tab20c', extent=extent, aspect='equal')
            plt.xlabel('Δx')
            plt.ylabel('Δz')
        else:
            # Z切片 (XY平面)
            slice_data = corr[:, :, center[2]]
            extent = [-Ly/2, Ly/2, -Lx/2, Lx/2]  # 交换x和y轴
            plt.imshow(slice_data.T, origin='lower', cmap='tab20c', extent=extent, aspect='equal')  # 转置数据并交换轴
            plt.xlabel('Δy')
            plt.ylabel('Δx')
        
        plt.colorbar(label='Correlation')
        plt.title(f'Correlation Function: {var}')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, file_names[i]))
        plt.close()

def plot_1d_slices(corr, t_start, t_end, case_name, var, Lx, Ly, Lz, Nx, Ny, Nz):
    """绘制1D切片图（只显示正半轴，三个方向在同一张图中）"""
    if corr is None:
        return
    
    # 获取输出目录
    output_dir = os.path.join('corrPlots', f'avg({t_start:.2f}-{t_end:.2f})')
    
    # 获取数组中心位置
    center = np.array(corr.shape) // 2
    
    # 创建一张图
    plt.figure(figsize=(10, 6))
    
    # 设置网格为虚线
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # X方向（只取正半轴）
    x_coords = np.linspace(0, Lx/2, Nx//2)
    y_x = corr[center[0]:, center[1], center[2]]
    plt.plot(x_coords, y_x, 'r-', label='x axis', linewidth=1.5)
    
    # Y方向（只取正半轴）
    y_coords = np.linspace(0, Ly/2, Ny//2)
    y_y = corr[center[0], center[1]:, center[2]]
    plt.plot(y_coords, y_y, 'b-', label='y axis', linewidth=1.5)
    
    # Z方向（只取正半轴）
    z_coords = np.linspace(0, Lz/2, Nz//2)
    y_z = corr[center[0], center[1], center[2]:]
    plt.plot(z_coords, y_z, 'k-', label='z axis', linewidth=1.5)
    
    # 设置标签和字体大小
    plt.xlabel('Δr', fontsize=12)
    plt.ylabel('Correlation', fontsize=12)
    plt.title(f'Correlation Function: {var} ({case_name})')
    
    # 设置图例
    plt.legend(fontsize=12, frameon=True)
    
    # 设置刻度标签大小
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(os.path.join(output_dir, f'{var}-1DSlices({t_start:.2f}-{t_end:.2f}).pdf'))
    plt.close()
    

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='计算两点空间自关联函数')
    parser.add_argument('--outn', type=str, required=True, help='输出文件格式，例如out2')
    parser.add_argument('--var', type=str, required=True, choices=['rho', 'vel', 'B'], help='物理量，可选rho, vel, B')
    parser.add_argument('--t1', type=float, default=0, help='起始时间，默认为0')
    parser.add_argument('--t2', type=float, default=None, help='结束时间，默认为无穷大')
    
    args = parser.parse_args()
    
    # 获取当前case名称
    current_dir = os.getcwd()
    case_name = os.path.basename(current_dir)

    print(f"\n正在提取网格信息...", flush=True)
    
    # 获取网格信息 (读取第一个文件)
    grid_info_file = os.path.join(current_dir, 'outputs', f'*.{args.outn}.00000.athdf')
    grid_files = glob.glob(grid_info_file)
    if not grid_files:
        print(f"错误：无法找到用于读取网格信息的参考文件: {grid_info_file}", flush=True)
        return
    
    try:
        grid_data = athena_read.athdf(grid_files[0])

        x1min, x1max = grid_data['RootGridX1'][: -1]
        x2min, x2max = grid_data['RootGridX2'][: -1]
        x3min, x3max = grid_data['RootGridX3'][: -1]

        Nx, Ny, Nz = grid_data['RootGridSize']
        
        Lx = x1max - x1min
        Ly = x2max - x2min
        Lz = x3max - x3min

        print(f"   Lx * Ly * Lz = {Lx} * {Ly} * {Lz};  Nx * Ny * Nz = {Nx} * {Ny} * {Nz}\n", flush=True)

    except Exception as e:
        print(f"错误：读取网格信息时出错: {e}", flush=True)
        return

    
    # 查找输出文件
    files, t_start, t_end = find_files(args.outn, args.t1, args.t2)
    
    if not files:
        print("未找到满足条件的文件，退出计算", flush=True)
        return
    
    # 创建输出目录
    output_dir = create_directories(t_start, t_end)
    
    # 计算关联函数
    corr = calculate_correlation(files, args.var)
    
    if corr is None:
        print("关联函数计算失败，退出计算", flush=True)
        return
    
    print("正在绘图...", flush=True)

    # 绘制2D切片图
    plot_2d_slices(corr, t_start, t_end, case_name, args.var, Lx, Ly, Lz)
    
    # 绘制1D曲线图
    plot_1d_slices(corr, t_start, t_end, case_name, args.var, Lx, Ly, Lz, Nx, Ny, Nz)
    
    print(f"计算完成！关联函数图已保存。", flush=True)
