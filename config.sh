#!/bin/bash
#
# AthenaUI 配置脚本
# 用于初始化用户配置文件和系统设置
#

# 当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# current.user 文件路径
USER_CONFIG_FILE="${SCRIPT_DIR}/user/current.user"
# example.user 文件路径
EXAMPLE_CONFIG_FILE="${SCRIPT_DIR}/user/example.user"

# 显示欢迎信息
echo "                                      "
echo "+====================================+"
echo "|                                    |"
echo "|       AthenaUI Configuration       |"
echo "|                                    |"
echo "+====================================+"
echo "                                      "
echo "This script will guide you through the configuration of AthenaUI."
echo "For customized configuration, please manually edit the 'user/current.user' file."
echo "-----------------------------------------------------------------------------------------"
echo ""

# 检查用户配置文件是否存在
if [ ! -f "$USER_CONFIG_FILE" ]; then
    echo "User configuration file not found. Creating new configuration file..."
    # 使用复制而不是创建空文件，以保留示例文件中的注释
    cp "$EXAMPLE_CONFIG_FILE" "$USER_CONFIG_FILE"
    echo "Configuration template created: $USER_CONFIG_FILE"
    echo ""
    
    # 使用nano编辑器打开配置文件
    ${EDITOR:-nano} "$USER_CONFIG_FILE"
    
    echo ""
    echo "Configuration file has been created."
else
    read -p "User configuration file found. Do you want to edit this file now? (y/n): " edit_choice
    if [[ $edit_choice == "y" || $edit_choice == "Y" ]]; then
        ${EDITOR:-nano} "$USER_CONFIG_FILE"
    fi
fi


# 加载配置并测试
echo ""
echo "Loading configuration and running tests..."

# 从用户配置文件中提取变量
source "$USER_CONFIG_FILE"

# 检查必要变量是否存在
if [ -z "$ATHENA_PATH" ] || [ -z "$ATHENAUI_PATH" ]; then
    echo "Error: Missing required path variables in configuration file."
    echo "Please ensure 'ATHENA_PATH' and 'ATHENAUI_PATH' are properly set."
    exit 1
fi

# 检查SLURM_FLAG变量并相应地检查其他变量
if [ -z "$SLURM_FLAG" ]; then
    echo "Warning: SLURM_FLAG not set, defaulting to OFF."
    SLURM_FLAG="OFF"
fi

if [ "$SLURM_FLAG" = "ON" ]; then
    # 当SLURM_FLAG为ON时，检查其他必要变量
    if [ -z "$USERNAME" ] || [ -z "$MPI_LOAD" ] || [ -z "$HDF5_LOAD" ] || [ -z "$PYTHON_LOAD" ]; then
        echo "Error: Slurm environment is enabled, but required environment variables are missing."
        echo "Please ensure the following variables are set:"
        echo "  USERNAME, MPI_LOAD, HDF5_LOAD, PYTHON_LOAD"
        exit 1
    fi
    
    # 加载模块
    echo "Loading modules..."
    echo "- MPI: $MPI_LOAD"
    eval $MPI_LOAD
    echo "- HDF5: $HDF5_LOAD"
    eval $HDF5_LOAD
    echo "- Python: $PYTHON_LOAD"
    eval $PYTHON_LOAD
    

else
    echo "Using local environment configuration (SLURM_FLAG=OFF)."
    echo "Skipping module loading steps."
fi

echo ""
echo "=============================================="

# 运行Athena++测试
echo ""
echo "Running Athena++ tests..."

# 检查Athena++路径是否有效
if [ ! -d "$ATHENA_PATH" ]; then
    echo "Error: Athena++ directory not found at $ATHENA_PATH"
    echo "Please check your configuration and try again."
    ${EDITOR:-nano} "$USER_CONFIG_FILE"
    exit 1
fi

# 测试结果标志
TEST_SUCCESS=true

# 根据SLURM_FLAG决定运行Python的方式
if [ "$SLURM_FLAG" = "ON" ]; then
    MPI="srun"
else
    MPI="mpirun"
fi

echo ""

# 进入测试目录
cd "$ATHENA_PATH/tst/regression"

# 执行测试
python run_tests.py mpi/mpi_linwave pgen/hdf5_reader_parallel shearingbox/mri2d --mpirun $MPI

# 返回原始目录
cd "$SCRIPT_DIR"

echo ""
echo "=============================================="
echo ""
echo "Tests completed. Please review the output above."
echo ""
echo "If the tests were successful, you can initialize the AthenaUI environment by running:"
echo "    source init.sh"
echo ""

# 设置执行权限
chmod +x "${SCRIPT_DIR}/init.sh"

echo "=============================================="