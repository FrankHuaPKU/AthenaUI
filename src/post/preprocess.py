#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import numpy as np

# 导入athena_read库
athena_path = os.environ.get('ATHENA_PATH', '')
if athena_path:
    sys.path.insert(0, os.path.join(athena_path, 'vis/python'))
    import athena_read
else:
    print("Error: Environment variable ATHENA_PATH not found, failed to import athena_read")
    sys.exit(1)

def find_files(outn, t1, t2):
    """
    查找满足时间区间条件的输出文件
    
    参数:
        outn (str): 输出文件格式，例如out2
        t1 (float): 起始时间
        t2 (float): 结束时间，如果为None则不设上限
        
    返回:
        list: 满足条件的文件列表
        list: 满足条件的时间列表
    """
    print(f"\nSearching for target files...", flush=True)
    
    # 获取当前路径
    current_path = os.getcwd()
    
    # 构建文件模式
    pattern = os.path.join(current_path, 'outputs', f'*.{outn}.*.athdf')
    
    # 获取所有匹配的文件
    all_outn_files = glob.glob(pattern)
    if not all_outn_files:
        print(f"Error: No files found matching {pattern}", flush=True)
        return [], 0, 0
    
    # 解析每个文件的时间，筛选满足条件的文件
    files = []
    times = []
    
    for file in all_outn_files:
        try:
            data = athena_read.athdf(file)
            time = data['Time']
            
            # 检查时间是否在范围内
            if t1 <= time and (t2 is None or time <= t2):
                files.append(file)
                times.append(time)
                
        except Exception as e:
            print(f"Warning: Error reading file {file}: {e}", flush=True)
    
    if not files:
        print(f"Error: No files found in time range [{t1}, {t2 if t2 is not None else '∞'}]", flush=True)
    else:
        print(f"Found {len(files)} files in time range [{t1}, {t2 if t2 is not None else '∞'}]", flush=True)
    
    # 返回文件列表和时间列表
    return files, times

def get_grid_info(outn):
    """
    提取网格参数信息
    
    参数:
        outn (str): 输出文件格式，例如out2
        
    返回:
        list: [Lx, Ly, Lz] 模拟box尺寸
    """
    print(f"\n正在提取网格信息：", flush=True)
    
    # 获取当前路径
    current_path = os.getcwd()
    
    # 查找参考文件
    grid_info_file = os.path.join(current_path, 'outputs', f'*.{outn}.00000.athdf')
    grid_files = glob.glob(grid_info_file)
    
    if not grid_files:
        print(f"错误：无法找到用于读取网格信息的参考文件: {grid_info_file}", flush=True)
        return None
    
    try:
        data = athena_read.athdf(grid_files[0])

        x1min, x1max = data['RootGridX1'][: -1]
        x2min, x2max = data['RootGridX2'][: -1]
        x3min, x3max = data['RootGridX3'][: -1]

        Nx, Ny, Nz = data['RootGridSize']
        
        Lx = x1max - x1min
        Ly = x2max - x2min
        Lz = x3max - x3min

        print(f"   Lx * Ly * Lz = {Lx} * {Ly} * {Lz};  Nx * Ny * Nz = {Nx} * {Ny} * {Nz}\n", flush=True)
        
        box = [Lx, Ly, Lz]
        return box

    except Exception as e:
        print(f"Error: fail to read grid information: {e}", flush=True)
        return None

if __name__ == '__main__':
    # 模块测试代码
    import argparse
    
    parser = argparse.ArgumentParser(description='Athena++输出文件预处理工具')
    parser.add_argument('--outn', type=str, required=True, help='输出文件格式，例如out2')
    parser.add_argument('--t1', type=float, default=0, help='起始时间，默认为0')
    parser.add_argument('--t2', type=float, default=None, help='结束时间，默认为无穷大')
    
    args = parser.parse_args()
    
    # 测试网格信息提取
    box = get_grid_info(args.outn)
    if box is None:
        sys.exit(1)
        
    # 测试文件查找
    files, times = find_files(args.outn, args.t1, args.t2)
    if not files:
        sys.exit(1)
