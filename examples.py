#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CardGener示例脚本
演示完整的工作流程
"""

import os
import sys


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def example_basic_generation():
    """示例1: 基础JSON生成"""
    print_section("示例1: 基础JSON生成")

    print("功能: 从Excel/CSV生成CardConjurer JSON文件")
    print("\n命令:")
    print("  python card_generator.py sample_cards.csv -o output")
    print("\n说明:")
    print("  - 读取CSV文件中的卡牌数据")
    print("  - 生成JSON文件到output目录")
    print("  - 每张卡一个JSON文件")
    print("\n预期输出:")
    print("  output/")
    print("  ├── Shadow_Strike.json")
    print("  ├── Warriors_Shield.json")
    print("  └── Frostbite.json")


def example_image_stitching():
    """示例2: 图片拼接"""
    print_section("示例2: 图片拼接")

    print("功能: 将多张卡牌图片拼接成大图")
    print("\n场景A - 普通拼接:")
    print("  python image_stitcher.py downloaded_images -o stitched.png -c 10")
    print("  说明: 10列自动计算行数")
    print("\n场景B - TTS模式:")
    print("  python image_stitcher.py downloaded_images --tts")
    print("  说明: 生成10×7布局，每页70张，适用于Tabletop Simulator")
    print("\n场景C - 自定义布局:")
    print("  python image_stitcher.py images -r 5 -c 7 -s 10 -o deck.png")
    print("  说明: 5行7列，间距10像素")


def example_ai_generation():
    """示例3: AI图片生成"""
    print_section("示例3: AI图片生成")

    print("功能: 使用免费AI API生成卡牌艺术图片")
    print("\n方法1 - 批量生成:")
    print("  python ai_image_generator.py --json-dir output --output-dir art")
    print("  说明: 为output目录中所有JSON生成图片")
    print("\n方法2 - 单张生成:")
    print("  python ai_image_generator.py --prompt 'ninja warrior' -o ninja.png")
    print("  说明: 从提示词生成单张图片")
    print("\n支持的API:")
    print("  - Pollinations AI (免费，默认)")
    print("  - Stability AI (需要API密钥)")


def example_cardconjurer_automation():
    """示例4: CardConjurer自动化"""
    print_section("示例4: CardConjurer自动化")

    print("功能: 自动导入JSON到CardConjurer并下载图片")
    print("\n注意: 需要安装selenium和ChromeDriver")
    print("  pip install selenium")
    print("  下载: https://chromedriver.chromium.org/")
    print("\n基础用法:")
    print("  python cardconjurer_automation.py output -o downloaded_images")
    print("\n无头模式:")
    print("  python cardconjurer_automation.py output --headless")
    print("\n工作流程:")
    print("  1. 打开Chrome浏览器")
    print("  2. 访问CardConjurer网站")
    print("  3. 逐个加载JSON文件")
    print("  4. 下载生成的图片")


def example_mcp_server():
    """示例5: MCP服务器"""
    print_section("示例5: MCP服务器（AI集成）")

    print("功能: 允许AI工具通过自然语言生成卡牌")
    print("\n配置Claude Desktop:")
    print('  编辑配置文件（macOS）:')
    print('  ~/Library/Application Support/Claude/claude_desktop_config.json')
    print('\n  添加:')
    print('  {')
    print('    "mcpServers": {')
    print('      "card-generator": {')
    print('        "command": "python",')
    print('        "args": ["/path/to/CardGener/mcp_server.py"]')
    print('      }')
    print('    }')
    print('  }')
    print("\n测试服务器:")
    print("  python mcp_server.py --test")
    print("\n在Claude中使用:")
    print('  "请用card-generator创建一张忍者卡牌..."')


def example_gui():
    """示例6: GUI界面"""
    print_section("示例6: GUI界面")

    print("功能: 图形界面，集成所有功能")
    print("\n启动GUI:")
    print("  python gui.py")
    print("\n界面包含:")
    print("  - 基础生成标签页")
    print("  - CardConjurer导入标签页")
    print("  - 图片拼接标签页")
    print("  - AI图片生成标签页")
    print("\n特点:")
    print("  - 文件选择对话框")
    print("  - 实时日志输出")
    print("  - 后台线程处理")
    print("  - 进度提示")


def example_complete_workflow():
    """示例7: 完整工作流"""
    print_section("示例7: 完整工作流")

    print("场景: 从零开始创建一套卡牌并导入TTS")
    print("\n步骤1 - 准备数据:")
    print("  在Excel中创建my_cards.xlsx，包含卡牌数据")
    print("\n步骤2 - 生成JSON:")
    print("  python card_generator.py my_cards.xlsx -o my_deck")
    print("\n步骤3 - 生成AI图片（可选）:")
    print("  python ai_image_generator.py --json-dir my_deck --output-dir art")
    print("\n步骤4 - 导入CardConjurer:")
    print("  python cardconjurer_automation.py my_deck -o images")
    print("\n步骤5 - 拼接为TTS格式:")
    print("  python image_stitcher.py images --tts")
    print("\n步骤6 - 导入TTS:")
    print("  将images/tts_decks/中的图片导入Tabletop Simulator")
    print("\n完成！")


def example_python_api():
    """示例8: Python API使用"""
    print_section("示例8: 在Python中使用")

    print("示例代码:")
    print("\n# 1. 生成单张卡牌")
    print("from card_generator import CardGenerator")
    print("import pandas as pd")
    print("")
    print("generator = CardGenerator('template.json')")
    print("card_data = pd.Series({")
    print("    'card_name': 'Shadow Strike',")
    print("    'card_type': 'Action - Attack',")
    print("    'rules_text': 'Deal 5 damage...',")
    print("    'cost': '2',")
    print("    'power': '5',")
    print("    'defense': '3',")
    print("    'class_type': 'ninja'")
    print("})")
    print("json_data = generator.generate_card(card_data)")
    print("")
    print("# 2. 拼接图片")
    print("from image_stitcher import ImageStitcher")
    print("")
    print("stitcher = ImageStitcher()")
    print("stitcher.auto_stitch('images', 'output.png', max_cols=10)")
    print("")
    print("# 3. AI图片生成")
    print("from ai_image_generator import AIImageGenerator")
    print("")
    print("generator = AIImageGenerator(api_type='pollinations')")
    print("generator.generate_and_save('ninja warrior', 'ninja.png')")


def main():
    """主函数"""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  CardGener - 卡牌批量生成工具示例".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # 显示所有示例
        example_basic_generation()
        example_image_stitching()
        example_ai_generation()
        example_cardconjurer_automation()
        example_mcp_server()
        example_gui()
        example_complete_workflow()
        example_python_api()
    else:
        # 显示菜单
        print("\n选择要查看的示例:")
        print("  1. 基础JSON生成")
        print("  2. 图片拼接")
        print("  3. AI图片生成")
        print("  4. CardConjurer自动化")
        print("  5. MCP服务器")
        print("  6. GUI界面")
        print("  7. 完整工作流")
        print("  8. Python API使用")
        print("  0. 查看所有示例")
        print("\n使用: python examples.py --all  (查看所有)")
        print("或直接运行查看菜单")

        print_section("快速开始")
        print("最简单的使用方式:")
        print("  1. 启动GUI: python gui.py")
        print("  2. 或使用命令行: python card_generator.py sample_cards.csv")

    print("\n" + "=" * 60)
    print("详细文档:")
    print("  - README_NEW.md - 完整功能说明")
    print("  - USAGE_GUIDE.md - 详细使用指南")
    print("  - GitHub: https://github.com/michaelwuwar/CardGener")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
