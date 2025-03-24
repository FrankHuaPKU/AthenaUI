#!/bin/bash
#
# AthenaUI 配置脚本
# 用于初始化用户配置文件和系统设置
#

# 当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
USER_CONFIG_FILE="${SCRIPT_DIR}/user/current.user"
EXAMPLE_CONFIG_FILE="${SCRIPT_DIR}/user/example.user"

# 显示欢迎信息
echo "+============================================+"
echo "|                                            |"
echo "|        AthenaUI Configuration Script       |"
echo "|                                            |"
echo "+============================================+"
echo "                                              "
echo "This script will help you configure the AthenaUI environment."
echo "After configuration, you can modify the configuration by editing the 'user/current.user' file."
echo ""

# 检查用户配置文件是否存在
if [ ! -f "$USER_CONFIG_FILE" ]; then
    echo "未找到用户配置文件。正在创建新的配置文件..."
    # 使用复制而不是创建空文件，以保留示例配置中的注释
    cp "$EXAMPLE_CONFIG_FILE" "$USER_CONFIG_FILE"
    echo "已创建配置文件模板：$USER_CONFIG_FILE"
    echo "请按照提示填写配置信息。"
    echo ""
    
    # 使用默认编辑器打开配置文件
    ${EDITOR:-nano} "$USER_CONFIG_FILE"
    
    echo ""
    echo "配置文件已创建。您可以随时通过编辑 'user/current.user' 文件修改配置。"
else
    echo "已找到用户配置文件：$USER_CONFIG_FILE"
    echo "如需修改，请手动编辑该文件。"
fi

echo ""
echo "配置完成。建议运行依赖测试来验证配置："
echo "   bash test/dependency_test.sh"
echo ""
echo "初始化环境请运行："
echo "   source init.sh"
echo ""

# 设置执行权限
chmod +x "${SCRIPT_DIR}/init.sh"
chmod +x "${SCRIPT_DIR}/test/dependency_test.sh"

echo "已设置必要脚本的执行权限。"
echo "==============================================" 