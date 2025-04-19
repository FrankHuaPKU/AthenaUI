#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 获取AthenaUI根目录 (脚本在src/post/目录下)
ATHENAUI_DIR="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"

# source current.user文件获取配置，使用绝对路径
source "$ATHENAUI_DIR/user/current.user"

# 加载必要的环境模块
if [ -n "$MPI_LOAD" ]; then
    eval "$MPI_LOAD"
fi

if [ -n "$HDF5_LOAD" ]; then
    eval "$HDF5_LOAD"
fi

if [ -n "$PYTHON_LOAD" ]; then
    eval "$PYTHON_LOAD"
fi

# 提取环境变量
OUTPUT_FORMAT=${SLC_OUTPUT_FORMAT:-"out2"}
VAR=${SLC_VAR}
DIR=${SLC_DIR}
COLORMAP=${SLC_COLORMAP}
CASE_DIR=${SLC_CASE_DIR:-$(basename $(pwd))}
VMIN=${SLC_VMIN:-"-1"}
VMAX=${SLC_VMAX:-"1"}

# 创建输出目录
if [ "$DIR" == "1" ]; then
    DIR_NAME="x"
elif [ "$DIR" == "2" ]; then
    DIR_NAME="y"
else
    DIR_NAME="z"
fi

OUTPUT_DIR="slicePlots/${VAR}(${DIR_NAME}=0)"
mkdir -p "$OUTPUT_DIR"

echo " "
echo "参数设置:"
echo "  输出格式: $OUTPUT_FORMAT"
echo "  物理量: $VAR"
echo "  切片方向: $DIR_NAME"
echo "  颜色映射: $COLORMAP"
echo "  Case目录: $CASE_DIR"
echo "  输出目录: $OUTPUT_DIR/"
echo "  数据范围: $VMIN 到 $VMAX"
echo " "

# 添加Python的vis目录到PATH
PYTHON_PATH="$ATHENA_PATH/vis/python"
export PYTHONPATH="$PYTHON_PATH:$PYTHONPATH"

echo " "

# 创建批处理命令
cat > slc_job.sh << 'EOF'
#!/bin/bash

# 加载必要的环境模块
if [ -n "$HDF5_LOAD" ]; then
    eval "$HDF5_LOAD"
fi

if [ -n "$PYTHON_LOAD" ]; then
    eval "$PYTHON_LOAD"
fi

for file in outputs/*.${OUTPUT_FORMAT}.*.athdf; do
    echo "处理 $(basename $file) 中..."
    
    # 提取时间
    TIME=$(python -c "
import sys
sys.path.insert(0, '${PYTHON_PATH}')
import athena_read
data = athena_read.athdf('$file')
print('{:.2f}'.format(data['Time']))
")
    
    # 定义输出文件
    OUTPUT_FILE="${OUTPUT_DIR}/t=${TIME}(${CASE_DIR}).pdf"
    
    # 执行绘图命令
    python ${PYTHON_PATH}/plot_slice.py \
        $file \
        ${VAR} \
        "$OUTPUT_FILE" \
        --direction ${DIR} \
        --colormap ${COLORMAP} \
        --vmin=${VMIN} \
        --vmax=${VMAX}
done
EOF

# 替换变量
sed -i "s|\${OUTPUT_FORMAT}|${OUTPUT_FORMAT}|g" slc_job.sh
sed -i "s|\${PYTHON_PATH}|${PYTHON_PATH}|g" slc_job.sh
sed -i "s|\${OUTPUT_DIR}|${OUTPUT_DIR}|g" slc_job.sh
sed -i "s|\${CASE_DIR}|${CASE_DIR}|g" slc_job.sh
sed -i "s|\${VAR}|${VAR}|g" slc_job.sh
sed -i "s|\${DIR}|${DIR}|g" slc_job.sh
sed -i "s|\${COLORMAP}|${COLORMAP}|g" slc_job.sh
sed -i "s|\${VMIN}|${VMIN}|g" slc_job.sh
sed -i "s|\${VMAX}|${VMAX}|g" slc_job.sh
sed -i "s|\${PYTHON_LOAD}|${PYTHON_LOAD}|g" slc_job.sh
sed -i "s|\${HDF5_LOAD}|${HDF5_LOAD}|g" slc_job.sh

echo "开始绘制 $VAR 在 $DIR_NAME 方向的切片图..."

# 使用srun提交批处理作业
chmod +x slc_job.sh
srun -J $USERNAME bash slc_job.sh
rm slc_job.sh

echo "切片图绘制完成，已输出到 $OUTPUT_DIR 目录"
