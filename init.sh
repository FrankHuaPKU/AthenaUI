#!/bin/bash
#
# AthenaUI 初始化脚本
# 用于加载用户配置、设置环境变量、添加命令路径到PATH
#

# 当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
USER_CONFIG_FILE="${SCRIPT_DIR}/user/current.user"
COMMANDS_DIR="${SCRIPT_DIR}/src/commands"

# ASCII艺术欢迎画面
function display_welcome() {
    echo "    _   _   _                       _   _ ___"
    echo "   /_\ | |_| |_  ___ _ _  __ _    | | | |_ _|"
    echo "  / _ \|  _| ' \/ -_) ' \/ _\` |_  | |_| || |"
    echo " /_/ \_\\__|_||_\___|_||_\__,_(_)  \___/|___|"
    echo ""
    echo "==========================================="
    echo " 欢迎使用 AthenaUI - Athena++的TUI框架"
    echo " 版本: v0.0 (框架搭建)"
    echo "==========================================="
    echo ""
}

# 检查用户配置文件
function check_config() {
    if [ ! -f "$USER_CONFIG_FILE" ]; then
        echo "错误: 未找到用户配置文件。请先运行 config.sh 完成配置。"
        return 1
    fi
    
    # 简单验证配置文件格式
    if ! grep -q "ATHENA_PATH" "$USER_CONFIG_FILE" || \
       ! grep -q "ATHENAUI_PATH" "$USER_CONFIG_FILE"; then
        echo "错误: 用户配置文件格式不正确。请检查 $USER_CONFIG_FILE"
        return 1
    fi
    
    return 0
}

# 加载用户配置
function load_config() {
    echo "正在加载用户配置..."
    
    # 导出配置变量到环境
    # 使用source命令加载配置文件中的变量
    source "$USER_CONFIG_FILE"
    
    # 验证关键变量是否加载
    if [ -z "$ATHENA_PATH" ] || [ -z "$ATHENAUI_PATH" ]; then
        echo "错误: 配置文件中缺少必要的路径设置。"
        return 1
    fi
    
    # 设置平台特定环境
    if [ "$SLURM_FLAG" = "ON" ]; then
        echo "已启用Slurm环境配置。"
        # 加载模块 (根据配置文件中的命令)
        if [ ! -z "$MPI_LOAD" ]; then eval $MPI_LOAD; fi
        if [ ! -z "$HDF5_LOAD" ]; then eval $HDF5_LOAD; fi
        if [ ! -z "$PYTHON_LOAD" ]; then eval $PYTHON_LOAD; fi
    else
        echo "使用本地环境配置。"
    fi
    
    return 0
}

# 设置命令路径
function setup_commands() {
    echo "配置命令路径..."
    
    # 确保命令目录中的脚本具有执行权限
    chmod +x ${COMMANDS_DIR}/*
    
    # 将命令目录添加到PATH
    export PATH="$COMMANDS_DIR:$PATH"
    
    return 0
}

# 显示可用命令
function list_commands() {
    echo "可用命令:"
    echo "  run  - 配置和运行新的模拟"
    echo "  slc  - 生成2D切片图"
    echo "  spc  - 绘制湍流谱"
    echo ""
}

# 主函数
function main() {
    display_welcome
    
    if ! check_config; then
        return 1
    fi
    
    if ! load_config; then
        return 1
    fi
    
    if ! setup_commands; then
        return 1
    fi
    
    list_commands
    
    echo "初始化完成！输入命令开始使用。"
    echo ""
    
    return 0
}

# 执行主函数
main 