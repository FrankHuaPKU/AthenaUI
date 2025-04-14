#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import os
import getpass

def calculate_display_width(text):
    """计算字符串在终端中的实际显示宽度（考虑中文字符宽度为2）"""
    width = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
            width += 2
        else:
            width += 1
    return width

def main(stdscr):
    # 初始化颜色
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 标题
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 选中项
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # 提示信息
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 输入文本颜色
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)   # 标题框颜色（绿色）
    
    # 隐藏光标
    curses.curs_set(0)
    
    # 参数默认值
    tlim = ""  # 默认为空
    wallTimeLimit = "24"  # 默认为24小时
    newOutputFlag = False  # 默认为no
    inputEditor = "N/A"  # 默认为N/A
    newOutputTemplate = "" # 新增：output模板名称
    
    # 当前选择的选项
    current_option = 0
    
    # 选项值列表（用于循环选择）
    yes_no_options = [False, True]  # False = No, True = Yes
    editor_options = ["N/A", "manual", "nano"]
    
    # 当前索引（用于循环选择）
    yes_no_index = 0
    editor_index = 0
    
    # 是否正在编辑某个字段
    editing_tlim = False
    editing_new_output_template = False # 新增：是否在编辑output模板
    
    while True:
        # 如果当前选中第一个选项且不是正在编辑模式，自动进入编辑模式
        if current_option == 0 and not editing_tlim:
            editing_tlim = True
            curses.curs_set(1)  # 显示光标
            curses.echo()  # 开启回显
        
        elif current_option == 3 and newOutputFlag and not editing_new_output_template:
             editing_new_output_template = True
             curses.curs_set(1)  # 显示光标
             curses.echo()  # 开启回显
        
        # 清屏
        stdscr.clear()
        
        # 获取屏幕大小
        height, width = stdscr.getmaxyx()
        
        # 绘制标题和边框
        title = "Athena++ Configuration for Restart"
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
            "模拟终止时间：",
            "运行时间上限：",
            "是否需要调用新output：",
            "选择新output模板（默认为空文件，或输入一个现有case）：",
            "input文件编辑模式（无需编辑选N/A）：",
            "确认"
        ]
        
        # 所有选项值（供循环使用）
        option_values = [
            tlim,
            wallTimeLimit + " 小时",
            "Yes" if newOutputFlag else "No",
            "N/A" if not newOutputFlag else newOutputTemplate,
            inputEditor + (" (固定为N/A)" if not newOutputFlag else ""),
            ""  # "确认"没有值
        ]
        
        # 计算每个选项的行号（考虑确认按钮前的空行）
        option_lines = []
        line_count = 4  # 起始行号，边框占据了前3行
        
        for i in range(len(option_labels)):
            # 在"确认"按钮前添加一个空行
            if i == 5:  # "确认"按钮的索引现在是5
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
                # 如果不需要新output，则模板和编辑器选项显示为灰色（不可选状态）
                if not newOutputFlag and (i == 3 or i == 4):
                    stdscr.attron(curses.A_DIM)
            
            # 特殊处理编辑模式下的选项
            if i == 0 and editing_tlim and i == current_option:
                # 显示前缀和标签（粗体绿色）
                stdscr.attron(curses.A_BOLD)
                stdscr.addstr(line, 2, prefix + option_labels[i])
                stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(2))
                
                # 以白色显示输入的文本
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(option_values[i])
                stdscr.attroff(curses.color_pair(4))
            elif i == 3 and editing_new_output_template and i == current_option: # 新增编辑output模板逻辑
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
                    # 移除灰色状态
                    if not newOutputFlag and (i == 3 or i == 4):
                        stdscr.attroff(curses.A_DIM)
        
        # 绘制提示信息（单行）
        stdscr.attron(curses.color_pair(3))
        hint_y = height - 2 # 在倒数第二行显示提示
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
        if editing_tlim:
            # 处理编辑tlim
            stdscr.move(option_lines[0], 17 + len(tlim))  # 光标位置修正为17（向右一格）
            # 获取用户输入
            key = stdscr.getch()
            
            # 处理特殊键
            if key == 10:  # 回车键
                # 结束编辑
                editing_tlim = False
                curses.noecho()
                curses.curs_set(0)
                current_option = 1  # 自动移到下一个选项
            elif key == 27:  # ESC键
                # 取消编辑并退出
                editing_tlim = False
                curses.noecho()
                curses.curs_set(0)
            elif key == curses.KEY_UP or key == curses.KEY_DOWN:
                # 上下方向键结束编辑并移动选项
                editing_tlim = False
                curses.noecho()
                curses.curs_set(0)
                
                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % len(option_labels)
                else:  # KEY_DOWN
                    current_option = (current_option + 1) % len(option_labels)
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                # 处理退格键
                if len(tlim) > 0:
                    tlim = tlim[:-1]
                    # 清除当前行并重新显示
                    stdscr.addstr(option_lines[0], 2, " " * (width - 4))  # 清空该行
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                    stdscr.addstr(option_lines[0], 2, "> 模拟终止时间：")
                    stdscr.attroff(curses.A_BOLD)
                    stdscr.attroff(curses.color_pair(2))
                    stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                    stdscr.addstr(tlim)
                    stdscr.attroff(curses.color_pair(4))
            elif 32 <= key <= 126:  # 可打印ASCII字符
                # 添加字符到tlim
                tlim += chr(key)
                # 更新显示（用白色显示整个输入内容）
                stdscr.addstr(option_lines[0], 2, " " * (width - 4))  # 清空该行
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(option_lines[0], 2, "> 模拟终止时间：")
                stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(2))
                stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                stdscr.addstr(tlim)
                stdscr.attroff(curses.color_pair(4))
        elif editing_new_output_template: # 新增output模板编辑逻辑
            # 处理编辑 newOutputTemplate
            output_template_start_col = 57 # 硬编码起始列
            stdscr.move(option_lines[3], output_template_start_col + len(newOutputTemplate)) # 使用硬编码值 + 当前输入长度
            # 获取用户输入
            key = stdscr.getch()
            
            # 处理特殊键
            if key == 10:  # 回车键
                # 结束编辑
                editing_new_output_template = False
                curses.noecho()
                curses.curs_set(0)
                current_option = 4  # 自动移到下一个选项
            elif key == 27:  # ESC键
                # 取消编辑并退出
                editing_new_output_template = False
                curses.noecho()
                curses.curs_set(0)
            elif key == curses.KEY_UP or key == curses.KEY_DOWN:
                # 上下方向键结束编辑并移动选项
                editing_new_output_template = False
                curses.noecho()
                curses.curs_set(0)
                
                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % len(option_labels)
                else:  # KEY_DOWN
                    current_option = (current_option + 1) % len(option_labels)
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                # 处理退格键
                if len(newOutputTemplate) > 0:
                    newOutputTemplate = newOutputTemplate[:-1]
                    # 清除当前行并重新显示
                    stdscr.addstr(option_lines[3], 2, " " * (width - 4))  # 清空该行
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                    stdscr.addstr(option_lines[3], 2, "> " + option_labels[3])
                    stdscr.attroff(curses.A_BOLD)
                    stdscr.attroff(curses.color_pair(2))
                    stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                    stdscr.addstr(newOutputTemplate)
                    stdscr.attroff(curses.color_pair(4))
            elif 32 <= key <= 126:  # 可打印ASCII字符
                # 添加字符到newOutputTemplate
                newOutputTemplate += chr(key)
                # 更新显示（用白色显示整个输入内容）
                stdscr.addstr(option_lines[3], 2, " " * (width - 4))  # 清空该行
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(option_lines[3], 2, "> " + option_labels[3])
                stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(2))
                stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                stdscr.addstr(newOutputTemplate)
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
                if current_option == 1:  # 运行时间上限
                    try:
                        time_limit = int(wallTimeLimit)
                        if time_limit > 1:
                            wallTimeLimit = str(time_limit - 1)
                    except ValueError:
                        pass
                elif current_option == 2:  # 是否需要调用新output
                    yes_no_index = (yes_no_index - 1) % len(yes_no_options)
                    newOutputFlag = yes_no_options[yes_no_index]
                    # 如果设置为No，强制inputEditor为N/A，并清空模板
                    if not newOutputFlag:
                        inputEditor = "N/A"
                        editor_index = 0
                        newOutputTemplate = "" # 清空模板
                elif current_option == 4 and newOutputFlag:  # input文件编辑模式（仅当需要新output时可选）
                    editor_index = (editor_index - 1) % len(editor_options)
                    inputEditor = editor_options[editor_index]
            elif key == curses.KEY_RIGHT:
                if current_option == 1:  # 运行时间上限
                    try:
                        time_limit = int(wallTimeLimit)
                        wallTimeLimit = str(time_limit + 1)
                    except ValueError:
                        wallTimeLimit = "24"  # 默认值
                elif current_option == 2:  # 是否需要调用新output
                    yes_no_index = (yes_no_index + 1) % len(yes_no_options)
                    newOutputFlag = yes_no_options[yes_no_index]
                    # 如果设置为No，强制inputEditor为N/A，并清空模板
                    if not newOutputFlag:
                        inputEditor = "N/A"
                        editor_index = 0
                        newOutputTemplate = "" # 清空模板
                elif current_option == 4 and newOutputFlag:  # input文件编辑模式（仅当需要新output时可选）
                    editor_index = (editor_index + 1) % len(editor_options)
                    inputEditor = editor_options[editor_index]
            elif key == 10:  # 回车键
                if current_option == 0:  # 模拟终止时间
                    # 进入编辑模式（下次循环会自动进入）
                    pass
                elif current_option == 3 and newOutputFlag: # 新增：output模板（仅当需要时）
                     # 进入编辑模式（下次循环会自动进入）
                    pass
                elif current_option == 5:  # 确认按钮 (索引改为5)
                    # 启动模拟
                    break
            elif key == 27:  # ESC键
                return  # 退出程序
    
    # 清理并恢复终端
    curses.endwin()
    
    # 清屏并重置终端状态，解决命令行覆盖问题
    os.system('clear')
    
    # 如果需要调用新output，处理athinput.new文件
    if newOutputFlag:
        current_dir = os.getcwd()  # 获取当前目录
        
        # 如果指定了模板目录
        if newOutputTemplate:
            # 构建模板目录路径（假设在simulations/shearingBox/下）
            template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                       "..", "simulations", "shearingBox", newOutputTemplate)
            template_file = os.path.join(template_dir, "athinput.new")
            
            # 检查目录和文件是否存在
            if os.path.exists(template_dir):
                if os.path.exists(template_file):
                    # 复制文件到当前目录
                    import shutil
                    try:
                        shutil.copy(template_file, os.path.join(current_dir, "athinput.new"))
                        print(f"athinput.new duplicated.")
                    except Exception as e:
                        print(f"复制文件失败: {e}")
                else:
                    print(f"警告: 在 {template_dir} 中未找到 athinput.new 文件，将创建空白文件")
                    # 创建空白文件
                    with open(os.path.join(current_dir, "athinput.new"), "w") as f:
                        pass
            else:
                print(f"错误: 模板目录 {template_dir} 不存在，将创建空白文件")
                # 创建空白文件
                with open(os.path.join(current_dir, "athinput.new"), "w") as f:
                    pass
        else:
            # 如果未指定模板，创建空白的athinput.new文件
            print("Creating new athinput.new file...")
            with open(os.path.join(current_dir, "athinput.new"), "w") as f:
                pass

    # 构建命令
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rst.sh")
    
    # 检查脚本是否存在
    if not os.path.exists(script_path):
        print(f"错误：未找到脚本文件 {script_path}")
        return
    
    # 设置环境变量，传递参数给rst.sh
    if tlim:
        os.environ["ATHENA_TLIM"] = tlim
    else:
        os.environ["ATHENA_TLIM"] = "0"  # 0表示不修改tlim
    
    os.environ["ATHENA_WALL_TIME_LIMIT"] = wallTimeLimit
    os.environ["ATHENA_NEW_OUTPUT_FLAG"] = "1" if newOutputFlag else "0"
    os.environ["ATHENA_INPUT_EDITOR"] = inputEditor
    os.environ["ATHENA_NEW_OUTPUT_TEMPLATE"] = newOutputTemplate # 新增：传递模板名称
    
    # 使用与run.py相同的方式执行脚本
    os.system(f"source {script_path} && /bin/bash")


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("程序被用户中断")
        curses.endwin()  # 确保在中断时也恢复终端
        os.system('clear')  # 清屏
    except Exception as e:
        print(f"发生错误：{e}")
        curses.endwin()  # 确保在异常时也恢复终端
        os.system('clear')  # 清屏
