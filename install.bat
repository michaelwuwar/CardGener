@echo off
REM CardGener Windows 安装脚本

echo ==================================
echo   CardGener 安装向导
echo ==================================
echo.

REM 检查Python
echo 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python。请先安装Python 3.8或更高版本。
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo ✅ Python已安装

REM 安装依赖
echo.
echo 安装依赖...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo ✅ 依赖安装成功

REM 创建目录
echo.
echo 创建测试目录...
if not exist "output" mkdir output
if not exist "downloaded_images" mkdir downloaded_images
if not exist "generated_art" mkdir generated_art
if not exist "test_output" mkdir test_output

echo ✅ 测试目录已创建

REM 测试基础功能
echo.
echo ==================================
echo   测试安装
echo ==================================
echo.

if exist "sample_cards.csv" (
    echo 测试基础生成...
    python card_generator.py sample_cards.csv -o test_output
    if errorlevel 1 (
        echo ⚠️  基础生成测试失败
    ) else (
        echo ✅ 基础生成功能正常
    )
) else (
    echo ⚠️  未找到sample_cards.csv，跳过测试
)

echo.
echo ==================================
echo   安装完成！
echo ==================================
echo.
echo 快速开始:
echo   1. 启动GUI:        python gui.py
echo   2. 查看示例:        python examples.py --all
echo   3. 生成卡牌:        python card_generator.py sample_cards.csv
echo.
echo 详细文档:
echo   - README_NEW.md
echo   - USAGE_GUIDE.md
echo.
echo 可选功能:
echo   - CardConjurer自动化需要安装: pip install selenium
echo   - 并下载ChromeDriver
echo.
echo 祝使用愉快！
pause
