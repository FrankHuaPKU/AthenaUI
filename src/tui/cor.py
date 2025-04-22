#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import os
import glob

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
    
    # 获取输出文件类型
    output_formats = get_output_formats()
    
    # 参数默认值
    output_format_index = 0
    outn = output_formats[output_format_index] if output_formats else "out2"  # 输出文件格式
    var = "B"  # 物理量默认为B
    t1 = ""    # 开始时间
    t2 = ""    # 结束时间
    
    # 当前选择的选项
    current_option = 0
    
    # 选项值列表（用于循环选择）
    var_options = ["rho", "vel", "B"]
    
    # 当前索引（用于循环选择）
    var_index = var_options.index(var)
    
    # 是否正在编辑某个字段
    editing_t1 = False
    editing_t2 = False
    
    while True:
        # 如果当前选中t1且不是正在编辑模式，自动进入编辑模式
        if current_option == 2 and not editing_t1:
            editing_t1 = True
            curses.curs_set(1)  # 显示光标
            curses.echo()  # 开启回显
        
        # 如果当前选中t2且不是正在编辑模式，自动进入编辑模式
        if current_option == 3 and not editing_t2:
            editing_t2 = True
            curses.curs_set(1)  # 显示光标
            curses.echo()  # 开启回显
        
        # 清屏
        stdscr.clear()
        
        # 获取屏幕大小
        height, width = stdscr.getmaxyx()
        
        # 绘制标题和边框
        title = "两点空间自关联函数计算配置"
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
        
        # 所有选项标签文本（供循环使用）
        option_labels = [
            "选择输出文件格式：",
            "物理量：",
            "开始时间：",
            "结束时间：",
            "确认"
        ]
        
        # 所有选项值（供循环使用）
        option_values = [
            outn,
            var,
            t1,
            t2,
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
            
            # 特殊处理编辑模式下的选项
            if (i == 2 and editing_t1 and i == current_option) or (i == 3 and editing_t2 and i == current_option):
                # 显示前缀和标签（粗体绿色）
                stdscr.attron(curses.A_BOLD)
                stdscr.addstr(line, 2, prefix + option_labels[i])
                stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(2))
                
                # 以白色显示输入的文本
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(option_values[i])
                stdscr.attroff(curses.color_pair(4))
            else:
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
            ("回车键：", True), ("确认当前参数", False), ("  ", False),
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
        
        # 处理编辑模式
        if editing_t1:
            # 处理编辑开始时间
            # 计算光标位置，考虑中文字符宽度
            cursor_x = 2 + calculate_display_width("> " + option_labels[2]) + len(t1)
            stdscr.move(option_lines[2], cursor_x)  # 光标位置
            # 获取用户输入
            key = stdscr.getch()
            
            # 处理特殊键
            if key == 10:  # 回车键
                # 结束编辑
                editing_t1 = False
                curses.noecho()
                curses.curs_set(0)
                current_option = 3  # 自动移到下一个选项
            elif key == 27:  # ESC键
                # 取消编辑并退出
                editing_t1 = False
                curses.noecho()
                curses.curs_set(0)
            elif key == curses.KEY_UP or key == curses.KEY_DOWN:
                # 上下方向键结束编辑并移动选项
                editing_t1 = False
                curses.noecho()
                curses.curs_set(0)
                
                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % len(option_labels)
                else:  # KEY_DOWN
                    current_option = (current_option + 1) % len(option_labels)
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                # 处理退格键
                if len(t1) > 0:
                    t1 = t1[:-1]
                    # 清除当前行并重新显示
                    stdscr.addstr(option_lines[2], 2, " " * (width - 4))  # 清空该行
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                    stdscr.addstr(option_lines[2], 2, "> " + option_labels[2])
                    stdscr.attroff(curses.A_BOLD)
                    stdscr.attroff(curses.color_pair(2))
                    stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                    stdscr.addstr(t1)
                    stdscr.attroff(curses.color_pair(4))
            elif 32 <= key <= 126:  # 可打印ASCII字符
                # 添加字符到开始时间
                t1 += chr(key)
                # 更新显示（用白色显示整个输入内容）
                stdscr.addstr(option_lines[2], 2, " " * (width - 4))  # 清空该行
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(option_lines[2], 2, "> " + option_labels[2])
                stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(2))
                stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                stdscr.addstr(t1)
                stdscr.attroff(curses.color_pair(4))
        elif editing_t2:
            # 处理编辑结束时间
            # 计算光标位置，考虑中文字符宽度
            cursor_x = 2 + calculate_display_width("> " + option_labels[3]) + len(t2)
            stdscr.move(option_lines[3], cursor_x)  # 光标位置
            # 获取用户输入
            key = stdscr.getch()
            
            # 处理特殊键
            if key == 10:  # 回车键
                # 结束编辑
                editing_t2 = False
                curses.noecho()
                curses.curs_set(0)
                current_option = 4  # 自动移到下一个选项
            elif key == 27:  # ESC键
                # 取消编辑并退出
                editing_t2 = False
                curses.noecho()
                curses.curs_set(0)
            elif key == curses.KEY_UP or key == curses.KEY_DOWN:
                # 上下方向键结束编辑并移动选项
                editing_t2 = False
                curses.noecho()
                curses.curs_set(0)
                
                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % len(option_labels)
                else:  # KEY_DOWN
                    current_option = (current_option + 1) % len(option_labels)
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                # 处理退格键
                if len(t2) > 0:
                    t2 = t2[:-1]
                    # 清除当前行并重新显示
                    stdscr.addstr(option_lines[3], 2, " " * (width - 4))  # 清空该行
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                    stdscr.addstr(option_lines[3], 2, "> " + option_labels[3])
                    stdscr.attroff(curses.A_BOLD)
                    stdscr.attroff(curses.color_pair(2))
                    stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                    stdscr.addstr(t2)
                    stdscr.attroff(curses.color_pair(4))
            elif 32 <= key <= 126:  # 可打印ASCII字符
                # 添加字符到结束时间
                t2 += chr(key)
                # 更新显示（用白色显示整个输入内容）
                stdscr.addstr(option_lines[3], 2, " " * (width - 4))  # 清空该行
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(option_lines[3], 2, "> " + option_labels[3])
                stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(2))
                stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                stdscr.addstr(t2)
                stdscr.attroff(curses.color_pair(4))
        else:
            # 获取按键
            key = stdscr.getch()
            
            # 按键处理
            if key == curses.KEY_UP:
                current_option = (current_option - 1) % len(option_labels)
            elif key == curses.KEY_DOWN:
                current_option = (current_option + 1) % len(option_labels)
            elif key == curses.KEY_LEFT:
                if current_option == 0:  # 输出文件格式
                    if output_formats:
                        output_format_index = (output_format_index - 1) % len(output_formats)
                        outn = output_formats[output_format_index]
                elif current_option == 1:  # 物理量
                    var_index = (var_index - 1) % len(var_options)
                    var = var_options[var_index]
            elif key == curses.KEY_RIGHT:
                if current_option == 0:  # 输出文件格式
                    if output_formats:
                        output_format_index = (output_format_index + 1) % len(output_formats)
                        outn = output_formats[output_format_index]
                elif current_option == 1:  # 物理量
                    var_index = (var_index + 1) % len(var_options)
                    var = var_options[var_index]
            elif key == 10:  # 回车键
                if current_option == 2:  # 开始时间
                    # 进入编辑模式（这里不做任何操作，因为下次循环开始时会自动进入编辑模式）
                    pass
                elif current_option == 3:  # 结束时间
                    # 进入编辑模式（这里不做任何操作，因为下次循环开始时会自动进入编辑模式）
                    pass
                elif current_option == 4:  # 确认按钮
                    # 启动计算
                    break
            elif key == 27:  # ESC键
                return  # 退出程序
    
    # 清理并恢复终端
    curses.endwin()
    
    # 构建命令，调用correlation.py脚本
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "post", "correlation.py")
    
    # 检查脚本是否存在
    if not os.path.exists(script_path):
        print(f"错误：未找到脚本文件 {script_path}")
        return
    
    # 构建命令行参数
    cmd_args = f"--outn={outn} --var={var}"
    
    # 添加时间区间参数
    if t1:
        cmd_args += f" --t1={t1}"
    if t2:
        cmd_args += f" --t2={t2}"
    
    # 是否在SLURM环境下运行
    slurm_flag = os.environ.get('SLURM_FLAG', 'OFF')
    if slurm_flag == 'ON':
        username = os.environ.get('USERNAME', '')
        cmd = f"srun -J {username} python {script_path} {cmd_args} && clear"
    else:
        cmd = f"python {script_path} {cmd_args} && clear"
    
    # 执行命令
    os.system(cmd)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"发生错误：{e}")
