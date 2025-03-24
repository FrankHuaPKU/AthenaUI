#!/bin/bash
#
# AthenaUI 依赖测试脚本
# 用于验证环境配置和依赖项是否满足要求
#

# 设置颜色代码
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

# 当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
USER_CONFIG_FILE="${ROOT_DIR}/user/current.user"

# 测试结果统计
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# 显示测试标题
function print_header() {
    echo "=============================================="
    echo "        AthenaUI 环境依赖测试工具"
    echo "=============================================="
    echo ""
}

# 测试通过消息
function test_pass() {
    echo -e "${GREEN}[通过]${NC} $1"
    PASS_COUNT=$((PASS_COUNT+1))
}

# 测试失败消息
function test_fail() {
    echo -e "${RED}[失败]${NC} $1"
    FAIL_COUNT=$((FAIL_COUNT+1))
}

# 测试警告消息
function test_warn() {
    echo -e "${YELLOW}[警告]${NC} $1"
    WARN_COUNT=$((WARN_COUNT+1))
}

# 测试配置文件
function test_config_file() {
    echo "测试配置文件..."
    
    if [ ! -f "$USER_CONFIG_FILE" ]; then
        test_fail "未找到用户配置文件：$USER_CONFIG_FILE"
        echo "请先运行 config.sh 创建配置文件。"
        return 1
    fi
    
    test_pass "用户配置文件存在"
    
    # 加载配置
    source "$USER_CONFIG_FILE"
    
    # 检查必要变量
    if [ -z "$ATHENA_PATH" ]; then
        test_fail "配置中缺少 ATHENA_PATH 变量"
        return 1
    fi
    
    if [ -z "$ATHENAUI_PATH" ]; then
        test_fail "配置中缺少 ATHENAUI_PATH 变量"
        return 1
    fi
    
    if [ -z "$SLURM_FLAG" ]; then
        test_fail "配置中缺少 SLURM_FLAG 变量"
        return 1
    fi
    
    if [ -z "$USERNAME" ]; then
        test_warn "配置中缺少 USERNAME 变量"
    fi
    
    test_pass "配置文件包含所有必要变量"
    
    # 测试路径是否存在
    if [ ! -d "$ATHENA_PATH" ]; then
        test_fail "Athena++路径不存在：$ATHENA_PATH"
        return 1
    fi
    
    if [ ! -d "$ATHENAUI_PATH" ]; then
        test_fail "AthenaUI路径不存在：$ATHENAUI_PATH"
        return 1
    fi
    
    test_pass "所有配置路径有效"
    
    return 0
}

# 测试Python环境
function test_python_env() {
    echo "测试Python环境..."
    
    # 加载Python模块（如果指定）
    if [ ! -z "$PYTHON_LOAD" ]; then
        eval $PYTHON_LOAD
    fi
    
    # 检查Python是否可用
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        test_fail "未找到Python命令"
        return 1
    fi
    
    # 确定Python命令
    PYTHON_CMD="python"
    if ! command -v python &> /dev/null && command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    fi
    
    test_pass "找到Python命令: $PYTHON_CMD"
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo "Python版本: $PYTHON_VERSION"
    
    # 检查curses模块
    if ! $PYTHON_CMD -c "import curses" 2> /dev/null; then
        test_warn "未找到Python curses模块，TUI功能将受限"
    else
        test_pass "Python curses模块可用"
    fi
    
    # 检查numpy模块
    if ! $PYTHON_CMD -c "import numpy" 2> /dev/null; then
        test_warn "未找到Python numpy模块，分析功能将受限"
    else
        test_pass "Python numpy模块可用"
    fi
    
    # 检查matplotlib模块
    if ! $PYTHON_CMD -c "import matplotlib" 2> /dev/null; then
        test_warn "未找到Python matplotlib模块，可视化功能将受限"
    else
        test_pass "Python matplotlib模块可用"
    fi
    
    return 0
}

# 测试Athena++环境
function test_athena_env() {
    echo "测试Athena++环境..."
    
    # 检查Athena++源代码是否存在
    if [ ! -f "$ATHENA_PATH/src/athena.hpp" ]; then
        test_fail "未找到Athena++源代码文件：$ATHENA_PATH/src/athena.hpp"
        return 1
    fi
    
    test_pass "找到Athena++源代码"
    
    # 检查是否有已编译的Athena++
    if [ ! -f "$ATHENA_PATH/bin/athena" ] && [ ! -f "$ATHENA_PATH/bin/athena.exe" ]; then
        test_warn "未找到已编译的Athena++可执行文件，您可能需要先编译Athena++"
    else
        test_pass "找到已编译的Athena++可执行文件"
    fi
    
    return 0
}

# 测试MPI环境
function test_mpi_env() {
    echo "测试MPI环境..."
    
    # 加载MPI模块（如果指定）
    if [ ! -z "$MPI_LOAD" ]; then
        eval $MPI_LOAD
    fi
    
    # 检查mpirun命令
    if ! command -v mpirun &> /dev/null && ! command -v mpiexec &> /dev/null; then
        test_warn "未找到MPI命令(mpirun/mpiexec)，并行功能将受限"
        return 0
    fi
    
    # 确定MPI命令
    MPI_CMD="mpirun"
    if ! command -v mpirun &> /dev/null; then
        MPI_CMD="mpiexec"
    fi
    
    test_pass "找到MPI命令: $MPI_CMD"
    
    # 检查MPI版本
    MPI_VERSION=$($MPI_CMD --version 2>&1 | head -n 1)
    echo "MPI版本: $MPI_VERSION"
    
    return 0
}

# 测试Slurm环境（如果启用）
function test_slurm_env() {
    if [ "$SLURM_FLAG" = "ON" ]; then
        echo "测试Slurm环境..."
        
        # 检查srun命令
        if ! command -v srun &> /dev/null; then
            test_fail "未找到srun命令，但SLURM_FLAG已设置为ON"
            return 1
        fi
        
        test_pass "找到srun命令"
        
        # 检查slurm版本
        SLURM_VERSION=$(srun --version 2>&1 | head -n 1)
        echo "Slurm版本: $SLURM_VERSION"
    else
        echo "Slurm环境测试已跳过 (SLURM_FLAG = OFF)"
    fi
    
    return 0
}

# 测试HDF5环境
function test_hdf5_env() {
    echo "测试HDF5环境..."
    
    # 加载HDF5模块（如果指定）
    if [ ! -z "$HDF5_LOAD" ]; then
        eval $HDF5_LOAD
    fi
    
    # 检查h5dump命令
    if ! command -v h5dump &> /dev/null; then
        test_warn "未找到h5dump命令，HDF5支持可能不完整"
    else
        test_pass "找到h5dump命令"
        
        # 尝试获取HDF5版本
        HDF5_VERSION=$(h5dump --version 2>&1 | head -n 1)
        echo "HDF5版本: $HDF5_VERSION"
    fi
    
    # 检查Python的h5py模块
    if [ -n "$PYTHON_CMD" ]; then
        if ! $PYTHON_CMD -c "import h5py" 2> /dev/null; then
            test_warn "未找到Python h5py模块，HDF5文件处理将受限"
        else
            test_pass "Python h5py模块可用"
        fi
    fi
    
    return 0
}

# 显示测试结果摘要
function print_summary() {
    echo ""
    echo "=============================================="
    echo "               测试结果摘要"
    echo "=============================================="
    echo -e "通过: ${GREEN}$PASS_COUNT${NC}, 失败: ${RED}$FAIL_COUNT${NC}, 警告: ${YELLOW}$WARN_COUNT${NC}"
    echo ""
    
    if [ $FAIL_COUNT -eq 0 ]; then
        if [ $WARN_COUNT -eq 0 ]; then
            echo -e "${GREEN}所有测试通过！环境配置完整。${NC}"
        else
            echo -e "${YELLOW}测试通过，但有警告。部分功能可能受限。${NC}"
        fi
    else
        echo -e "${RED}测试失败。请解决上述问题后重试。${NC}"
    fi
    
    echo "=============================================="
}

# 主函数
function main() {
    print_header
    
    # 运行所有测试
    test_config_file
    if [ $? -ne 0 ]; then
        echo "配置文件测试失败，终止其他测试。"
        print_summary
        return 1
    fi
    
    test_python_env
    test_athena_env
    test_mpi_env
    test_slurm_env
    test_hdf5_env
    
    print_summary
    
    if [ $FAIL_COUNT -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# 执行主函数
main 