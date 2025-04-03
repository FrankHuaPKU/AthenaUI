#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import os

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
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)   # 标题框颜色
    
    # 隐藏光标
    curses.curs_set(0)
    
    # 参数默认值
    caseDir = ""
    FP = "FP64"  # 默认为FP64
    EoS = "isothermal"  # 默认为isothermal
    rSolver = "HLLD"  # 默认为HLLD
    wallTimeLimit = "24"  # 默认为24小时
    
    # 当前选择的选项
    current_option = 0
    
    # 选项值列表（用于循环选择）
    fp_options = ["FP64", "FP32"]
    eos_options = ["isothermal", "adiabatic"]
    rsolver_options = ["HLLD", "LHLLD"]
    
    # 当前索引（用于循环选择）
    fp_index = 0
    eos_index = 0
    rsolver_index = 0
    
    # 当前是否正在编辑case名称
    editing_case_name = False
    
    while True:
        # 如果当前选中第一个选项且不是正在编辑模式，自动进入编辑模式
        if current_option == 0 and not editing_case_name:
            editing_case_name = True
            curses.curs_set(1)  # 显示光标
            curses.echo()  # 开启回显
        
        # 清屏
        stdscr.clear()
        
        # 获取屏幕大小
        height, width = stdscr.getmaxyx()
        
        # 绘制标题和边框
        title = "Athena++ 剪切盒模拟配置"
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
            "模拟case名称：",
            "量化精度：",
            "状态方程：",
            "Riemann求解器：",
            "运行时间限制：",
            "编辑input文件"
        ]
        
        # 所有选项值（供循环使用）
        option_values = [
            caseDir,
            FP,
            EoS,
            rSolver + (" (固定为HLLD)" if EoS == "isothermal" else ""),
            wallTimeLimit + " 小时",
            ""  # "编辑input文件"没有值
        ]
        
        # 绘制选项 - 从边框下面开始
        for i in range(len(option_labels)):
            if i == current_option:
                stdscr.attron(curses.color_pair(2))
                prefix = "> "
            else:
                stdscr.attron(curses.color_pair(1))
                prefix = "  "
            
            # 特殊处理第一个选项（当处于编辑模式时）
            if i == 0 and editing_case_name and i == current_option:
                # 显示前缀和标签（粗体绿色）
                stdscr.attron(curses.A_BOLD)
                stdscr.addstr(i + 4, 2, prefix + option_labels[i])  # +4 以给标题框留出空间
                stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(2))
                
                # 以白色显示输入的文本
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(option_values[i])
                stdscr.attroff(curses.color_pair(4))
            else:
                # 显示标签（粗体）
                stdscr.attron(curses.A_BOLD)
                stdscr.addstr(i + 4, 2, prefix + option_labels[i])  # +4 以给标题框留出空间
                stdscr.attroff(curses.A_BOLD)
                
                # 显示值（正常字体）
                if option_values[i]:  # 只有当值非空时才显示
                    stdscr.addstr(option_values[i])
                
                if i == current_option:
                    stdscr.attroff(curses.color_pair(2))
                else:
                    stdscr.attroff(curses.color_pair(1))
        
        # 绘制提示信息
        hints = [
            "上下方向键：选择不同选项",
            "左右方向键：修改选中选项的值",
            "回车键：确认当前选项/开始模拟",
            "ESC键：退出（可能有一点延迟）"
        ]
        
        for i, hint in enumerate(hints):
            stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
            
            # 分离冒号前后的内容，使冒号前的部分为粗体
            if "：" in hint:
                parts = hint.split("：", 1)
                stdscr.addstr(height - 5 + i, 2, parts[0] + "：")
                stdscr.attroff(curses.A_BOLD)  # 关闭粗体
                stdscr.addstr(parts[1])
            else:
                stdscr.addstr(height - 5 + i, 2, hint)
                stdscr.attroff(curses.A_BOLD)
            
            stdscr.attroff(curses.color_pair(3))
        
        # 刷新屏幕
        stdscr.refresh()
        
        # 如果正在编辑case名称，移动光标到输入位置
        if editing_case_name:
            stdscr.move(4, 17 + len(caseDir))  # 光标位置也需要调整
            # 获取用户输入
            key = stdscr.getch()
            
            # 处理特殊键
            if key == 10:  # 回车键
                # 结束编辑
                editing_case_name = False
                curses.noecho()
                curses.curs_set(0)
                current_option = 1  # 自动移到下一个选项
            elif key == 27:  # ESC键
                # 取消编辑并退出
                editing_case_name = False
                curses.noecho()
                curses.curs_set(0)
            elif key == curses.KEY_UP or key == curses.KEY_DOWN:
                # 上下方向键结束编辑并移动选项
                editing_case_name = False
                curses.noecho()
                curses.curs_set(0)
                
                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % len(option_labels)
                else:  # KEY_DOWN
                    current_option = (current_option + 1) % len(option_labels)
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                # 处理退格键
                if len(caseDir) > 0:
                    caseDir = caseDir[:-1]
                    # 清除当前行并重新显示
                    stdscr.addstr(4, 2, " " * (width - 4))  # 清空该行
                    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                    stdscr.addstr(4, 2, "> 模拟case名称：")
                    stdscr.attroff(curses.A_BOLD)
                    stdscr.attroff(curses.color_pair(2))
                    stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                    stdscr.addstr(caseDir)
                    stdscr.attroff(curses.color_pair(4))
            elif 32 <= key <= 126:  # 可打印ASCII字符
                # 添加字符到caseDir
                caseDir += chr(key)
                # 更新显示（用白色显示整个输入内容）
                stdscr.addstr(4, 2, " " * (width - 4))  # 清空该行
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(4, 2, "> 模拟case名称：")
                stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(2))
                stdscr.attron(curses.color_pair(4))  # 使用白色显示输入文本
                stdscr.addstr(caseDir)
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
                if current_option == 1:  # 量化精度
                    fp_index = (fp_index - 1) % len(fp_options)
                    FP = fp_options[fp_index]
                elif current_option == 2:  # 状态方程
                    eos_index = (eos_index - 1) % len(eos_options)
                    EoS = eos_options[eos_index]
                    # 如果状态方程是isothermal，则Riemann求解器只能是HLLD
                    if EoS == "isothermal":
                        rSolver = "HLLD"
                elif current_option == 3 and EoS != "isothermal":  # Riemann求解器（仅当状态方程不是isothermal时）
                    rsolver_index = (rsolver_index - 1) % len(rsolver_options)
                    rSolver = rsolver_options[rsolver_index]
                elif current_option == 4:  # 运行时间限制
                    try:
                        time_limit = int(wallTimeLimit)
                        if time_limit > 1:
                            wallTimeLimit = str(time_limit - 1)
                    except ValueError:
                        pass
            elif key == curses.KEY_RIGHT:
                if current_option == 1:  # 量化精度
                    fp_index = (fp_index + 1) % len(fp_options)
                    FP = fp_options[fp_index]
                elif current_option == 2:  # 状态方程
                    eos_index = (eos_index + 1) % len(eos_options)
                    EoS = eos_options[eos_index]
                    # 如果状态方程是isothermal，则Riemann求解器只能是HLLD
                    if EoS == "isothermal":
                        rSolver = "HLLD"
                elif current_option == 3 and EoS != "isothermal":  # Riemann求解器（仅当状态方程不是isothermal时）
                    rsolver_index = (rsolver_index + 1) % len(rsolver_options)
                    rSolver = rsolver_options[rsolver_index]
                elif current_option == 4:  # 运行时间限制
                    try:
                        time_limit = int(wallTimeLimit)
                        wallTimeLimit = str(time_limit + 1)
                    except ValueError:
                        wallTimeLimit = "24"  # 默认值
            elif key == 10:  # 回车键
                if current_option == 0:  # 模拟case名称
                    # 进入编辑模式（这里不做任何操作，因为下次循环开始时会自动进入编辑模式）
                    pass
                elif current_option == 5:  # 开始模拟
                    if not caseDir:
                        # 如果case名称为空，在底部显示错误信息
                        stdscr.addstr(height - 6, 2, "错误：请输入模拟case名称！", curses.A_BOLD)
                        stdscr.refresh()
                        stdscr.getch()  # 等待任意键继续
                    else:
                        # 启动模拟
                        break
            elif key == 27:  # ESC键
                return  # 退出程序
    
    # 清理并恢复终端
    curses.endwin()
    
    # 构建命令
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pgen", "shearingBox.sh")
    
    # 检查脚本是否存在
    if not os.path.exists(script_path):
        print(f"错误：未找到脚本文件 {script_path}")
        return
    
    # 设置环境变量，传递参数给shearingBox.sh
    os.environ["ATHENA_CASE_DIR"] = caseDir
    os.environ["ATHENA_FP"] = FP
    os.environ["ATHENA_EOS"] = EoS
    os.environ["ATHENA_RSOLVER"] = rSolver
    os.environ["ATHENA_WALL_TIME_LIMIT"] = wallTimeLimit
    
    # 使用os.execl启动bash并source脚本，保持环境变量和目录更改
    print(f"启动模拟，case名称：{caseDir}...")
    
    os.system(f"source {script_path} && cd $ATHENAUI_PATH/simulations/shearingBox/{caseDir}/ && /bin/bash")


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"发生错误：{e}")
