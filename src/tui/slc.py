#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import os
import glob
import sys
import re
import numpy as np

def get_athena_path():
    """获取Athena++安装路径"""
    athena_path = os.environ.get('ATHENA_PATH')
    
    if athena_path is None:
        # 如果路径未指定，尝试使用默认路径
 
        print("错误：无法确定Athena++安装路径")
        print("请设置ATHENA_PATH环境变量")
        sys.exit(1)
    
    return athena_path

def calculate_display_width(text):
    """计算字符串在终端中的实际显示宽度（考虑中文字符宽度为2）"""
    width = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
            width += 2
        else:
            width += 1
    return width

def get_output_formats():
    """获取outputs目录中所有输出文件格式"""
    try:
        # 搜索所有athdf文件
        athdf_files = glob.glob('outputs/*.*.*.athdf')
        formats = []

        # 提取文件格式部分
        for file in athdf_files:
            parts = os.path.basename(file).split('.')
            if len(parts) >= 4:
                format_part = parts[1]  # 例如"out2"
                if format_part not in formats:
                    formats.append(format_part)
        
        return formats if formats else ["out2"]  # 如果没有找到，默认为out2
    except Exception:
        return ["out2"]  # 出错时返回默认值

def get_files_with_format(output_format):
    """获取指定格式的所有文件"""
    try:
        return sorted(glob.glob(f'outputs/*.{output_format}.*.athdf'))
    except Exception:
        return []

def calculate_data_range(files, var, athena_path):
    """计算数据范围"""
    print("正在分析数据范围...")
    
    try:
        # 检查athena_path是否有效
        if not athena_path:
            print("错误: ATHENA_PATH未设置或为空")
            return -1, 1
            
        # 导入必要的库
        python_path = os.path.join(athena_path, 'vis', 'python')
        sys.path.insert(0, python_path)
        
        import athena_read
        
        # 计算vmin和vmax
        min_values = []
        max_values = []
        sum_values = 0
        count = 0
        
        for file in files:
            try:
                data = athena_read.athdf(file)
                if var in data:
                    var_data = data[var]
                    min_values.append(var_data.min())
                    max_values.append(var_data.max())
                    if var == "rho":
                        sum_values += var_data.mean()
                        count += 1
            except Exception as e:
                print(f"处理文件 {file} 时出错: {e}")
        
        # 根据物理量计算vmin和vmax
        if min_values and max_values:
            min_value = min(min_values)
            max_value = max(max_values)
            
            if var == "rho":
                avg_rho = sum_values / count if count > 0 else (min_value + max_value) / 2
                delta_rho = max(max_value - avg_rho, avg_rho - min_value)
                vmin = avg_rho - delta_rho
                vmax = avg_rho + delta_rho
            else:
                max_delta = max(abs(max_value), abs(min_value))
                vmin = -max_delta
                vmax = max_delta
                
            print(f"vmin = {vmin}, vmax = {vmax}")
            return vmin, vmax
    except Exception as e:
        print(f"计算数据范围时出错: {e}")
    
    # 如果计算失败，使用默认值
    print("使用默认数据范围: -1 到 1")
    return -1, 1

def main(stdscr):
    # 初始化颜色
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 标题
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 选中项
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # 提示信息
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 输入文本颜色
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)   # 标题框颜色
    
    # 隐藏光标
    curses.curs_set(0)
    
    # 获取可用的输出格式
    output_formats = get_output_formats()
    output_format_index = 0
    output_format = output_formats[output_format_index] if output_formats else "out2"
    
    # 参数默认值
    var_options = ["rho", "vel1", "vel2", "vel3", "Bcc1", "Bcc2", "Bcc3"]
    var_index = 0
    var = var_options[var_index]
    
    dir_options = ["x", "y", "z"]
    dir_index = 0
    dir = dir_options[dir_index]
    
    cmap_options = ["RdBu", "seismic", "bwr", "coolwarm"]
    cmap_index = 0
    cmap = cmap_options[cmap_index]
    
    # 当前选择的选项
    current_option = 0
    
    while True:
        # 清屏
        stdscr.clear()
        
        # 获取屏幕大小
        height, width = stdscr.getmaxyx()
        
        # 绘制标题和边框
        title = "Athena++ Slice Plot Configuration"
        display_width = calculate_display_width(title)
        title_padding = 6  # 标题左右的填充空间
        box_width = display_width + title_padding * 2
        box_start_x = (width - box_width) // 2
        
        # 绘制边框 - 使用 Unicode 字符绘制漂亮的边框
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        
        # 绘制顶部边框
        stdscr.addstr(0, box_start_x, "╔" + "═" * (box_width - 2) + "╗")
        
        # 绘制中间标题行
        title_start = box_start_x + (box_width - display_width) // 2
        stdscr.addstr(1, box_start_x, "║" + " " * (box_width - 2) + "║")
        stdscr.addstr(1, title_start, title)
        
        # 绘制底部边框
        stdscr.addstr(2, box_start_x, "╚" + "═" * (box_width - 2) + "╝")
        
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
        
        # 选项标签文本
        option_labels = [
            "选择输出文件格式：",
            "绘图物理量：",
            "切片方向：",
            "颜色映射：",
            "确认"
        ]
        
        # 选项值
        option_values = [
            output_format,
            var,
            dir,
            cmap,
            ""  # "确认"没有值
        ]
        
        # 计算每个选项的行号（考虑确认按钮前的空行）
        option_lines = []
        line_count = 4  # 起始行号，边框占据了前3行
        
        for i in range(len(option_labels)):
            # 在"确认"按钮前添加一个空行
            if i == 4:  # "确认"按钮的索引
                line_count += 1
            
            option_lines.append(line_count)
            line_count += 1
        
        # 绘制选项 - 从边框下面开始
        for i in range(len(option_labels)):
            line = option_lines[i]
            
            if i == current_option:
                stdscr.attron(curses.color_pair(2))
                prefix = "> "
            else:
                stdscr.attron(curses.color_pair(1))
                prefix = "  "
            
            # 显示标签（粗体）
            stdscr.attron(curses.A_BOLD)
            stdscr.addstr(line, 2, prefix + option_labels[i])
            stdscr.attroff(curses.A_BOLD)
            
            # 显示值（正常字体）
            if option_values[i]:  # 只有当值非空时才显示
                stdscr.addstr(option_values[i])
            
            if i == current_option:
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.attroff(curses.color_pair(1))
        
        # 绘制提示信息（单行）
        stdscr.attron(curses.color_pair(3))
        hint_y = height - 2  # 在倒数第二行显示提示
        hint_x = 2
        
        hints_parts = [
            ("上下方向键：", True), ("选择不同参数", False), ("  ", False),
            ("左右方向键：", True), ("修改参数的值", False), ("  ", False),
            ("回车键：", True), ("确认", False), ("  ", False),
            ("ESC键或Ctrl+C：", True), ("退出", False)
        ]
        
        for text, is_bold in hints_parts:
            if is_bold:
                stdscr.attron(curses.A_BOLD)
                stdscr.addstr(hint_y, hint_x, text)
                stdscr.attroff(curses.A_BOLD)
            else:
                stdscr.addstr(hint_y, hint_x, text)
            hint_x += calculate_display_width(text) # 更新 x 坐标

        stdscr.attroff(curses.color_pair(3))
        
        # 刷新屏幕
        stdscr.refresh()
        
        # 获取按键
        key = stdscr.getch()
        
        # 按键处理
        if key == curses.KEY_UP:
            current_option = (current_option - 1) % len(option_labels)
        elif key == curses.KEY_DOWN:
            current_option = (current_option + 1) % len(option_labels)
        elif key == curses.KEY_LEFT:
            if current_option == 0:  # 输出文件格式
                output_format_index = (output_format_index - 1) % len(output_formats)
                output_format = output_formats[output_format_index]
            elif current_option == 1:  # 绘图物理量
                var_index = (var_index - 1) % len(var_options)
                var = var_options[var_index]
            elif current_option == 2:  # 切片方向
                dir_index = (dir_index - 1) % len(dir_options)
                dir = dir_options[dir_index]
            elif current_option == 3:  # 颜色映射
                cmap_index = (cmap_index - 1) % len(cmap_options)
                cmap = cmap_options[cmap_index]
        elif key == curses.KEY_RIGHT:
            if current_option == 0:  # 输出文件格式
                output_format_index = (output_format_index + 1) % len(output_formats)
                output_format = output_formats[output_format_index]
            elif current_option == 1:  # 绘图物理量
                var_index = (var_index + 1) % len(var_options)
                var = var_options[var_index]
            elif current_option == 2:  # 切片方向
                dir_index = (dir_index + 1) % len(dir_options)
                dir = dir_options[dir_index]
            elif current_option == 3:  # 颜色映射
                cmap_index = (cmap_index + 1) % len(cmap_options)
                cmap = cmap_options[cmap_index]
        elif key == 10:  # 回车键
            if current_option == 4:  # 确认按钮
                # 启动绘图
                break
        elif key == 27:  # ESC键
            return  # 退出程序
    
    # 清理并恢复终端
    curses.endwin()
    
    # 获取指定格式的文件
    files = get_files_with_format(output_format)
    if not files:
        print(f"错误：未找到格式为{output_format}的文件")
        return
    
    # 优先使用命令行参数指定的路径
    athena_path = get_athena_path()
    
    # 获取当前case目录名
    caseDir = os.path.basename(os.getcwd())
    
    # 将方向转换为plot_slice.py使用的参数
    dir_num = "1" if dir == "x" else ("2" if dir == "y" else "3")
    
    # 计算数据范围
    vmin, vmax = calculate_data_range(files, var, athena_path)
    
    # 找到slc.sh脚本路径
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    slc_script = os.path.join(script_dir, "post", "slice.sh")
    
    if not os.path.exists(slc_script):
        print(f"错误：未找到脚本 {slc_script}")
        return
    
    # 设置参数
    os.environ["ATHENA_PATH"] = athena_path
    os.environ["SLC_OUTPUT_FORMAT"] = output_format
    os.environ["SLC_VAR"] = var
    os.environ["SLC_DIR"] = dir_num
    os.environ["SLC_COLORMAP"] = cmap
    os.environ["SLC_CASE_DIR"] = caseDir
    os.environ["SLC_VMIN"] = str(vmin)
    os.environ["SLC_VMAX"] = str(vmax)
    
    # 调用slc.sh脚本
    print("正在启动绘图流程...")
    cmd = f"source {slc_script} && clear"
    os.system(cmd)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"发生错误：{e}")
