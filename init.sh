#!/bin/bash
#
# AthenaUI初始化脚本
# 用于配置环境变量、自定义命令和git设置
#

# 获取当前脚本所在的目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 最开始检测是否在AthenaUI目录下
if [[ "$PWD" == *"/AthenaUI"* ]]; then
    # 找到当前用户的AthenaUI目录
    ATHENAUI_DIR=$(dirname "$PWD")
    if [[ "$PWD" == *"/AthenaUI" ]]; then
        ATHENAUI_DIR="$PWD"
    else
        # 如果在AthenaUI的子目录，则向上查找AthenaUI根目录
        CURRENT_DIR="$PWD"
        while [[ "$CURRENT_DIR" != "/" && ! "$CURRENT_DIR" =~ .*AthenaUI$ ]]; do
            CURRENT_DIR=$(dirname "$CURRENT_DIR")
        done
        
        if [[ "$CURRENT_DIR" =~ .*AthenaUI$ ]]; then
            ATHENAUI_DIR="$CURRENT_DIR"
        else
            return 1
        fi
    fi
    
    # 切换到AthenaUI根目录
    # cd "$ATHENAUI_DIR"
else
    return 1
fi

# 显示欢迎信息
echo "╔═══════════════════════════════════════════╗"
echo "║                                           ║"
echo "║    Welcome to AthenaUI! Version: 0.2.0    ║"
echo "║                                           ║"
echo "╚═══════════════════════════════════════════╝"

# 加载用户配置文件
USER_CONFIG="$ATHENAUI_DIR/user/current.user"

if [ -f "$USER_CONFIG" ]; then
    source "$USER_CONFIG"
else
    echo "警告：未找到用户配置文件，请确保$USER_CONFIG存在"
fi

# -------自定义命令-----------------------------------------------------

# mon命令：监控SLURM作业
alias mon="
    watch -n 0.1 '
        echo \"slurm.out File:\";
        echo \"\";
        slurmFile=\$(ls -t slurm-*.out 2>/dev/null | head -n1);
        if [ -n \"\$slurmFile\" ]; then
            tail -n 10 \"\$slurmFile\";
        else
            echo \"Slurm output files not found.\";
        fi;
        echo \"\";
        echo \"Press Ctrl + C to exit.\"
    '
"

# run命令：启动Athena++模拟，调用run.py
alias run="python $ATHENAUI_DIR/src/tui/run.py"

# rst命令：继续运行Athena++模拟，调用rst.py
alias rst="python $ATHENAUI_DIR/src/tui/rst.py"

# hst命令：绘制历史数据图，调用hst.py
alias hst="srun -J $USERNAME python $ATHENAUI_DIR/src/post/hst.py"

# slc命令：绘制流场切片图，调用slc.py
alias slc="python $ATHENAUI_DIR/src/tui/slc.py"

# cor命令：计算两点空间自关联函数，调用cor.py
alias cor="python $ATHENAUI_DIR/src/tui/cor.py"

# spc命令：绘制能谱，调用spc.py
alias spc="python $ATHENAUI_DIR/src/tui/spc.py"

# 用户名命令：切换到对应用户目录
if [ -n "$USERNAME" ]; then
    alias $USERNAME="cd $ATHENAUI_PATH"
fi


# -------显示功能列表-----------------------------------------------------
cat << EOF

Available commands:
  run: 启动新的模拟case(仅支持剪切盒)     mon: 监控当前模拟case运行进度
  rst: 继续运行已有模拟case               hst: 绘制物理量随时间变化的曲线图
  slc: 绘制流场的切片图                   spc: 绘制能谱图
  cor: 计算两点空间关联函数
EOF

# cor：计算两点空间关联函数