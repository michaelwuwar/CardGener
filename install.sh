#!/bin/bash
# CardGener 安装脚本

echo "=================================="
echo "  CardGener 安装向导"
echo "=================================="
echo ""

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
if [ -z "$python_version" ]; then
    echo "❌ 未找到Python 3。请先安装Python 3.8或更高版本。"
    exit 1
fi
echo "✅ Python版本: $python_version"

# 安装基础依赖
echo ""
echo "安装基础依赖..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 基础依赖安装成功"
else
    echo "❌ 依赖安装失败，请检查网络连接"
    exit 1
fi

# 提示可选依赖
echo ""
echo "=================================="
echo "  可选功能"
echo "=================================="
echo ""
echo "所有基础功能已安装！"
echo ""
echo "可选功能（需要额外安装）:"
echo ""
echo "1. CardConjurer自动化"
echo "   pip install selenium"
echo "   并下载ChromeDriver: https://chromedriver.chromium.org/"
echo ""
echo "2. 使用Stability AI API"
echo "   需要API密钥，设置环境变量:"
echo "   export STABILITY_API_KEY=your_key"
echo ""

# 创建测试目录
echo "创建测试目录..."
mkdir -p output
mkdir -p downloaded_images
mkdir -p generated_art
mkdir -p test_output

echo "✅ 测试目录已创建"

# 测试基础功能
echo ""
echo "=================================="
echo "  测试安装"
echo "=================================="
echo ""

if [ -f "sample_cards.csv" ]; then
    echo "测试基础生成..."
    python3 card_generator.py sample_cards.csv -o test_output

    if [ $? -eq 0 ]; then
        echo "✅ 基础生成功能正常"
    else
        echo "⚠️  基础生成测试失败"
    fi
else
    echo "⚠️  未找到sample_cards.csv，跳过测试"
fi

echo ""
echo "=================================="
echo "  安装完成！"
echo "=================================="
echo ""
echo "快速开始:"
echo "  1. 启动GUI:        python3 gui.py"
echo "  2. 查看示例:        python3 examples.py --all"
echo "  3. 生成卡牌:        python3 card_generator.py sample_cards.csv"
echo ""
echo "详细文档:"
echo "  - README_NEW.md"
echo "  - USAGE_GUIDE.md"
echo ""
echo "祝使用愉快！"
