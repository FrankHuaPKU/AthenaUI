import argparse
import sys
import os

# 添加PyMRI库路径
pymri_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../PyMRI'))
sys.path.insert(0, pymri_path)

from pymri import *
import preprocess

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='湍流能谱计算工具')
    parser.add_argument('--outn', type=str, required=True, help='输出文件格式')
    parser.add_argument('--t1', type=float, help='开始时间')
    parser.add_argument('--t2', type=float, help='结束时间')
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    try:
        # 从输出文件中提取湍流场数据
        turbulence = preprocess.output2turbulence(args.outn, args.t1, args.t2)
        
        # 计算磁场能谱
        print("正在计算能谱...", flush=True)
        spc = EnergySpectra(turbulence)
        
        # 绘制能谱
        print("计算完成, 正在绘制能谱...", flush=True)
        spc.plot()
        
    except Exception as e:
        print(f"计算过程中发生错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()