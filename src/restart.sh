#!/bin/bash

# Athena++ restart脚本 rst.sh
# 用于重新启动一个已经结束的Athena++模拟case
# 作者：hyy
# 版本：1.0
# 创建时间：2024年4月17日

# 检查当前目录是否有Athena++ restart文件
if [ ! -d "outputs" ] || [ ! -f "athinput.hgb" ]; then
    echo "Error: Not a valid Athena++ simulation directory."
    exit 1
fi

# 检查outputs目录中是否有restart文件
if [ ! -f $(ls outputs/*.final.rst 2>/dev/null | head -n 1) ]; then
    echo "Error: Restart file not found in 'outputs' directory."
    echo "Please ensure the simulation has been run and a .rst file has been generated."
    exit 1
fi

# 获取最新的restart文件
RESTART_FILE=$(ls -t outputs/*.final.rst | head -n 1)
echo "Restart file found: $RESTART_FILE"

# -------设置时间限制-----------------------------------------------------
# 从环境变量读取时间上限
wallTimeLimit=${ATHENA_WALL_TIME_LIMIT:-24}

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 获取AthenaUI根目录 (脚本在src/目录下)
ATHENAUI_DIR="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# source current.user文件获取配置，使用绝对路径
source "$ATHENAUI_DIR/user/current.user"


# SBATCH 设置的是分钟数，同时增加一分钟冗余
wallTimeLimitInMin=$(( wallTimeLimit * 60 + 1 ))
# -------设置时间限制-----------------------------------------------------

# ----------------------------------------------------------------------------
# 自动提取 `athinput.hgb` 文件中的参数
inputFile="athinput.hgb"

# 自动提取 <mesh> 中的 nx1, nx2, nx3
nx1=$(awk '/<mesh>/,/<meshblock>/' $inputFile |grep 'nx1'| awk '{print $3}')
nx2=$(awk '/<mesh>/,/<meshblock>/' $inputFile |grep 'nx2'| awk '{print $3}')
nx3=$(awk '/<mesh>/,/<meshblock>/' $inputFile |grep 'nx3'| awk '{print $3}')

# 自动提取 <meshblock> 中的 nx1, nx2, nx3 (分别命名为MBx1, MBx2, MBx3)
MBx1=$(awk '/<meshblock>/,/<hydro>/' $inputFile |grep 'nx1'| awk '{print $3}')
MBx2=$(awk '/<meshblock>/,/<hydro>/' $inputFile |grep 'nx2'| awk '{print $3}')
MBx3=$(awk '/<meshblock>/,/<hydro>/' $inputFile |grep 'nx3'| awk '{print $3}')

# 打印提取的参数，用于检查参数
echo " "
echo "Mesh: $nx1 * $nx2 * $nx3"
echo "MeshBlock: $MBx1 * $MBx2 * $MBx3"
echo " "

# 计算总核数
n=$(( (nx1 * nx2 * nx3) / (MBx1 * MBx2 * MBx3) ))

# 计算所需节点数 
if (( n < 64 )); then # 如果不足64核，也要设置一整个节点
    N=1 
else 
    N=$(( n / 64 )) 
fi

# 输出计算结果
echo "According to the input file, $N compute node(s) and $n cores will be assigned for the simulation."
echo " "
# ----------------------------------------------------------------------------

# 处理新的tlim参数
TLIM_PARAM=""
if [ "${ATHENA_TLIM}" != "0" ]; then
    TLIM_PARAM="time/tlim=${ATHENA_TLIM}"
    echo "New tlim: ${ATHENA_TLIM}"
else
    echo "'tlim' not changed."
fi

# 处理新的output参数
NEW_OUTPUT_FLAG=${ATHENA_NEW_OUTPUT_FLAG:-0}
INPUT_EDITOR=${ATHENA_INPUT_EDITOR:-N/A}

if [ "$NEW_OUTPUT_FLAG" = "1" ]; then
    echo "将创建新的output配置"
    
    # 创建空白的athinput.new文件
    touch athinput.new
    
    # 根据编辑模式处理
    if [ "$INPUT_EDITOR" = "nano" ]; then
        echo "使用nano编辑器编辑athinput.new文件"
        nano athinput.new
    elif [ "$INPUT_EDITOR" = "manual" ]; then
        echo "请在编辑器中手动编辑athinput.new文件，完成后按回车继续"
        read -p "按回车键继续..." continue
    fi
    
    # 检查athinput.new是否为空
    if [ ! -s athinput.new ]; then
        echo "警告：athinput.new文件为空，将不使用新的output配置"
        NEW_OUTPUT_FLAG=0
        rm athinput.new
    fi
fi

# 预设作业名
jobName=$USERNAME


# 创建提交作业脚本 job.sh 
# 注意，会覆盖之前的 job.sh 脚本
rm -f job.sh # 先删掉原来的，保险

cat << EOF > job.sh
#!/bin/bash

#SBATCH -J $USERNAME
#SBATCH -N $N
#SBATCH -n $n
#SBATCH -t $wallTimeLimitInMin

EOF

# 根据参数构建restart命令
if [ "$NEW_OUTPUT_FLAG" = "1" ]; then
    # 使用新的output配置
    echo "srun athena -r $RESTART_FILE -i athinput.new -d outputs -t $wallTimeLimit:00:00 $TLIM_PARAM" >> job.sh
else
    # 不使用新的output配置
    if [ -n "$TLIM_PARAM" ]; then
        echo "srun athena -r $RESTART_FILE -d outputs -t $wallTimeLimit:00:00 $TLIM_PARAM" >> job.sh
    else
        echo "srun athena -r $RESTART_FILE -d outputs -t $wallTimeLimit:00:00" >> job.sh
    fi
fi

# 赋予job.sh可执行权限 
chmod +x job.sh

# 提交作业并提取作业ID
output=$(sbatch job.sh)
jobID=$(echo $output | awk '{print $4}')

# 打印作业ID
echo "Submitted batch job $jobID"

# 确保 slurm 输出文件已经创建
slurmFile="slurm-${jobID}.out"

while [ ! -f "$slurmFile" ]; do
    sleep 0.1  # 等待文件生成
done

# 等待1秒钟，等文件多出现几行
sleep 1


# 打印提示语，退出后还可以继续监控
echo " "
echo "To monitor the simulation progress, simply enter: mon"
echo " "
