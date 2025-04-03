#!/bin/bash
#
# AthenaUI：剪切盒模拟
# 用于配置剪切盒模拟
#

# 从环境变量中读取参数
caseDir=${ATHENA_CASE_DIR}
FP=${ATHENA_FP:-"FP64"}         # 默认为FP64
EoS=${ATHENA_EOS:-"isothermal"} # 默认为isothermal
rSolver=${ATHENA_RSOLVER:-"HLLD"} # 默认为HLLD
wallTimeLimit=${ATHENA_WALL_TIME_LIMIT:-"24"} # 默认为24小时

# 打印参数，便于调试
echo "═════════════════════════════════════════"
echo "当前模拟参数："
echo "  • 模拟case名称：$caseDir"
echo "  • 量化精度：$FP"
echo "  • 状态方程：$EoS"
echo "  • Riemann求解器：$rSolver"
echo "  • 运行时间限制：$wallTimeLimit 小时"
echo "═════════════════════════════════════════"
echo ""

# source current.user文件获取配置
source user/current.user

# 切换到AthenaUI根目录
cd $ATHENAUI_PATH

# 新建case目录并初始化
mkdir -p $ATHENAUI_PATH/simulations/shearingBox/$caseDir/
rm -rf $ATHENAUI_PATH/simulations/shearingBox/$caseDir/athena
rm -rf $ATHENAUI_PATH/simulations/shearingBox/$caseDir/outputs/

# 如果用户选择了等温状态方程，则Riemann求解器只能是HLLD
if [ "$EoS" == "isothermal" ]; then
    rSolver="hlld"
fi

# 设置精度
if [ "$FP" == "FP32" ]; then
    FLOAT_FLAG="-float"
else
    FLOAT_FLAG=""
fi

# 检查目标case目录下是不是已经有input文件（比如不是第一次跑这个case）
if [ -e $ATHENAUI_PATH/simulations/shearingBox/$caseDir/athinput.hgb ]; then 
    
    # 提示input文件已存在，询问是否修改
    while true; do
    
        read -p "Input文件已存在。是否需要编辑？(y/n) " editFlag
 
        if [[ "$editFlag" == "n" ]]; then
            break
        elif [[ "$editFlag" == "y" ]]; then
            # 启动input文件编辑器 
            nano $ATHENAUI_PATH/simulations/shearingBox/$caseDir/athinput.hgb
            break
        else 
            echo "请输入y或n。"
        fi
        
    done

# 如果没有现存input文件，就要找一个模版作为修改的起点
else

    # 询问input文件目录，并检查输入目录是否合法，不合法则要求再次输入
    read -p "请设置input文件路径（输入'default'使用内置input，或输入已有case目录）：" inputDirectory
    
    # 反复询问，直到输入合法
    while true; do
    
        # 输入default，就调用Athena++内置input文件
        if [[ "$inputDirectory" == "default" ]]; then
            cp $ATHENA_PATH/inputs/mhd/athinput.hgb $ATHENAUI_PATH/simulations/shearingBox/$caseDir/
            break
            
        # 输入一个case目录，就调用这个case中的input文件
        elif [ -e "$ATHENAUI_PATH/simulations/shearingBox/$inputDirectory/athinput.hgb" ]; then 
            cp $ATHENAUI_PATH/simulations/shearingBox/$inputDirectory/athinput.hgb $ATHENAUI_PATH/simulations/shearingBox/$caseDir/
            break
        
        else
            read -p "未找到输入目录或目录无效。请提供有效的目录名：" inputDirectory
        fi
        
    done
    
    # 启动input文件编辑器 
    nano $ATHENAUI_PATH/simulations/shearingBox/$caseDir/athinput.hgb

fi

# 自动提取athinput.hgb文件中的参数
inputFile="$ATHENAUI_PATH/simulations/shearingBox/$caseDir/athinput.hgb"

# 自动提取 <mesh> 中的 nx1, nx2, nx3
nx1=$(awk '/<mesh>/,/<meshblock>/' $inputFile | grep 'nx1' | awk '{print $3}')
nx2=$(awk '/<mesh>/,/<meshblock>/' $inputFile | grep 'nx2' | awk '{print $3}')
nx3=$(awk '/<mesh>/,/<meshblock>/' $inputFile | grep 'nx3' | awk '{print $3}')

# 自动提取 <meshblock> 中的 nx1, nx2, nx3
MBx1=$(awk '/<meshblock>/,/<hydro>/' $inputFile | grep 'nx1' | awk '{print $3}')
MBx2=$(awk '/<meshblock>/,/<hydro>/' $inputFile | grep 'nx2' | awk '{print $3}')
MBx3=$(awk '/<meshblock>/,/<hydro>/' $inputFile | grep 'nx3' | awk '{print $3}')

# 打印提取的参数，用于检查
echo " "
echo "Mesh: $nx1 × $nx2 × $nx3"
echo "MeshBlock: $MBx1 × $MBx2 × $MBx3"
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
echo "根据输入文件，将为该模拟分配 $N 个计算节点和 $n 个核心。"
echo " "

sleep 2

# SBATCH设置的是分钟数，同时增加一分钟冗余
wallTimeLimitInMin=$(( wallTimeLimit * 60 + 1 ))

# 问题配置
cd $ATHENA_PATH
python configure.py -b --prob=hgb --flux=${rSolver,,} --eos=${EoS,,} -mpi -hdf5 $FLOAT_FLAG

# 编译，在case目录生成可执行文件
echo "编译Athena++..."
make clean
make -j EXE_DIR=$ATHENAUI_PATH/simulations/shearingBox/$caseDir/

# 切换到case目录 
cd $ATHENAUI_PATH/simulations/shearingBox/$caseDir/

# 创建提交作业脚本 job.sh 
cat << EOF > job.sh
#!/bin/bash

#SBATCH -J $USERNAME
#SBATCH -N $N
#SBATCH -n $n
#SBATCH -t $wallTimeLimitInMin

srun athena -i athinput.hgb -d outputs -t $wallTimeLimit:00:00
EOF

# 赋予job.sh可执行权限 
chmod +x job.sh

# 提交作业并提取作业ID
echo " "
echo "提交作业..."
output=$(sbatch job.sh)
jobID=$(echo $output | awk '{print $4}')

# 打印作业ID
echo "已提交Sbatch作业：$jobID"

# 确保slurm输出文件已经创建
slurmFile="slurm-${jobID}.out"

while [ ! -f "$slurmFile" ]; do
    sleep 0.1  # 等待文件生成
done

# 等待1秒钟，等文件多出现几行
sleep 1

# 清屏
# clear

# 监控模拟进度
mon

# 打印提示语，退出后还可以继续监控
echo " "
echo "要继续监控模拟进度，只需输入：mon"
echo " "
