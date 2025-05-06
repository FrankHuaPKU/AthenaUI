#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
预处理模块, 用于从Athena++输出文件中提取数据

主要功能: 
1. 提取box尺寸
2. 提取物理场数据（密度场、速度场、磁场）
3. 将数据转换为ScalarField和VectorField对象
4. 构建Turbulence对象
"""

import sys
import os
import glob
from typing import List, Tuple, Optional, Union
import numpy as np

# 导入athena_read库
athena_path = os.environ.get('ATHENA_PATH', '')
if athena_path:
    sys.path.insert(0, os.path.join(athena_path, 'vis/python'))
    try:
        import athena_read
    except ImportError as e:
        print(f"错误: 无法导入athena_read模块: {e}", flush=True)
        sys.exit(1)
else:
    print("错误: 未找到环境变量ATHENA_PATH, 无法导入athena_read", flush=True)
    sys.exit(1)

# 导入PyMRI库中的数据类型
from pymri import ScalarField, VectorField, Turbulence


def get_qshear() -> Optional[float]:
    """从athinput文件中提取qshear值
    
    返回:
        Optional[float]: qshear值, 如果提取失败则返回None
    """
    
    # 获取当前路径
    current_path = os.getcwd()
    
    # 查找athinput文件
    athinput_pattern = os.path.join(current_path, 'athinput.*')
    athinput_file = glob.glob(athinput_pattern)[0] # 只取第一个文件
    
    if not os.path.exists(athinput_file):
        print("错误: 无法找到athinput文件", flush=True)
        return None
    
    try:
        # 读取athinput文件
        with open(athinput_file, 'r') as f:
            lines = f.readlines()
            
        # 查找<orbital_advection>部分
        found_section = False
        for line in lines:
            if '<orbital_advection>' in line:
                found_section = True
                continue
            if found_section and 'qshear' in line:
                # 提取qshear值
                qshear = float(line.split('=')[1].split('#')[0].strip())
                print(f"剪切参数: q = {qshear}\n", flush=True)
                return qshear
                
        print("错误: 在athinput文件中未找到qshear值", flush=True)
        return None
        
    except Exception as e:
        print(f"错误: 读取athinput文件时出错: {e}", flush=True)
        return None

def get_box(outn: str) -> Optional[List[float]]:
    """提取模拟box的尺寸信息
    
    参数:
        outn (str): 输出文件格式, 例如out2
        
    返回:
        Optional[List[float]]: [Lx, Ly, Lz] 模拟box尺寸, 如果提取失败则返回None
    """
    print("\n网格信息: ", flush=True)
    
    # 获取当前路径
    current_path = os.getcwd()
    
    # 查找参考文件
    file00000pattern = os.path.join(current_path, 'outputs', f'*.{outn}.00000.athdf')
    file00000 = glob.glob(file00000pattern)[0]
    
    if not file00000:
        print(f"错误: 未找到输出文件: {file00000pattern}", flush=True)
        return None
    
    try:
        data = athena_read.athdf(file00000)

        # 提取网格范围
        x1min, x1max = data['RootGridX1'][:-1].astype(np.float64)
        x2min, x2max = data['RootGridX2'][:-1].astype(np.float64)
        x3min, x3max = data['RootGridX3'][:-1].astype(np.float64)

        # 提取网格大小
        Nx, Ny, Nz = data['RootGridSize']
        
        # 计算box尺寸
        Lx = float(x1max - x1min)
        Ly = float(x2max - x2min)
        Lz = float(x3max - x3min)

        print(f"   Lx * Ly * Lz = {Lx} * {Ly} * {Lz}", flush=True)
        print(f"   Nx * Ny * Nz = {Nx} * {Ny} * {Nz}\n", flush=True)
        
        return [Lx, Ly, Lz]

    except Exception as e:
        print(f"错误: 读取网格信息时出错: {e}", flush=True)
        return None

def output2turbulence(outn: str, t1: float, t2: Optional[float] = None) -> Optional[Turbulence]:
    """从输出文件中提取所有物理场数据并构建Turbulence对象
    
    参数:
        outn (str): 输出文件格式, 例如out2
        t1 (float): 起始时间
        t2 (Optional[float]): 结束时间, 如果为None则不设上限
        
    返回:
        Optional[Turbulence]: Turbulence对象, 如果提取失败则返回None
    """
    print("正在提取物理场数据...", flush=True)
    
    # 获取box尺寸
    box = get_box(outn)
        
    # 获取剪切参量q
    q = get_qshear()
        
    # 获取当前路径和case名
    current_path = os.getcwd()
    case = os.path.basename(current_path)
    
    # 构建文件模式
    pattern = os.path.join(current_path, 'outputs', f'*.{outn}.*.athdf')
    
    # 获取所有匹配的文件
    outn_files = sorted(glob.glob(pattern))
    if not outn_files:
        print(f"错误: 未找到任何形如 {pattern} 的文件", flush=True)
        return None
    
    # 存储提取的数据
    rhos : List[ScalarField] = []
    Vs   : List[VectorField] = []
    Bs   : List[VectorField] = []
    times: List[float]       = []
    
    # 遍历所有输出文件, 提取目标数据
    for file in outn_files:
        try:
            data = athena_read.athdf(file)
            time = float(data['Time'])
            
            # 检查时间是否在范围内
            if t1 <= time and (t2 is None or time <= t2):
                try:
                    # 提取密度场
                    rho_data = data['rho'].astype(np.float64)
                    rho_data = np.transpose(rho_data, (2, 1, 0)) # 将数据从 (z, y, x) 转换为 (x, y, z)
                    rho = ScalarField(rho_data, box)
                    
                    # 提取速度场
                    vx = data['vel1'].astype(np.float64)
                    vy = data['vel2'].astype(np.float64)
                    vz = data['vel3'].astype(np.float64)
                    vx = np.transpose(vx, (2, 1, 0)) # 将数据从 (z, y, x) 转换为 (x, y, z)
                    vy = np.transpose(vy, (2, 1, 0))
                    vz = np.transpose(vz, (2, 1, 0))
                    V = VectorField(vx, vy, vz, box)
                    
                    # 提取磁场
                    Bx = data['Bcc1'].astype(np.float64)
                    By = data['Bcc2'].astype(np.float64)
                    Bz = data['Bcc3'].astype(np.float64)
                    Bx = np.transpose(Bx, (2, 1, 0)) # 将数据从 (z, y, x) 转换为 (x, y, z)
                    By = np.transpose(By, (2, 1, 0))
                    Bz = np.transpose(Bz, (2, 1, 0))
                    B = VectorField(Bx, By, Bz, box)
                    
                    # 存储数据
                    rhos.append(rho)
                    Vs.append(V)
                    Bs.append(B)
                    times.append(time)
                    
                except KeyError as e:
                    print(f"警告: 文件 {file} 中缺少必要的物理量: {e}", flush=True)
                    continue
                
        except Exception as e:
            print(f"警告: 读取文件 {file} 时出错: {e}", flush=True)
            continue
    
    if not times:
        print(f"错误: 在时间范围 [{t1}, {t2 if t2 is not None else '∞'}] 内未找到有效数据", flush=True)
        return None
    else:
        print(f"已提取 {len(times)} 个时间切片的数据, 时间范围: [{min(times)}, {max(times)}]\n", flush=True)
    
    # 构建并返回Turbulence对象
    try:
        turbulence = Turbulence(case, rhos, Vs, Bs, times, q, 'isothermal')
        return turbulence
    except Exception as e:
        print(f"错误: 构建Turbulence对象时出错: {e}", flush=True)
        return None


def test():
    '''
    模块测试代码

    测试命令: 在case目录中调用 python ../../../src/post/preprocess.py
    '''
    outn = 'prim'
    t1 = 50
    t2 = 100

    turbulence = output2turbulence(outn, t1, t2)

    print(f'q: {turbulence.q}\n')
    
    '''
    print(f'avgBys: {[f"{avg[1]:.3g}" for avg in turbulence.avgBs]}\n')

    print(f'KEs: {[f"{x:.3g}" for x in turbulence.KEs]}\n')

    print(f'MEs: {[f"{x:.3g}" for x in turbulence.MEs]}\n')

    print(f'density fluctuations: {[f"{x:.3g}" for x in turbulence.density_fluctuations]}\n')
    '''

    avgBys = [avg[1] for avg in turbulence.avgBs]

    print(f'avgBy: {np.mean(avgBys)} ± {np.std(avgBys)}\n')

    print(f'KE: {np.mean(turbulence.KEs)} ± {np.std(turbulence.KEs)}\n')

    print(f'ME: {np.mean(turbulence.MEs)} ± {np.std(turbulence.MEs)}\n')

    dens_flucts = turbulence.density_fluctuations
    print(f'density fluctuation: {np.mean(dens_flucts)} ± {np.std(dens_flucts)}\n')


if __name__ == '__main__':

    test()
