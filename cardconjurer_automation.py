#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CardConjurer自动化模块
支持批量导入JSON到CardConjurer并自动下载生成的图片
"""

import os
import time
from pathlib import Path
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class CardConjurerAutomation:
    """CardConjurer自动化类"""

    def __init__(self, headless: bool = False, download_dir: Optional[str] = None):
        """
        初始化自动化工具

        Args:
            headless: 是否无头模式运行
            download_dir: 下载目录路径
        """
        self.headless = headless
        self.download_dir = download_dir or os.path.join(os.getcwd(), "downloaded_images")
        self.driver = None

    def setup_driver(self):
        """设置Chrome驱动"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")

        # 设置下载目录
        os.makedirs(self.download_dir, exist_ok=True)
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # 其他设置
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)

    def load_json_to_cardconjurer(self, json_path: str) -> bool:
        """
        加载JSON文件到CardConjurer

        Args:
            json_path: JSON文件路径

        Returns:
            是否成功加载
        """
        try:
            # 打开CardConjurer创建器
            self.driver.get("https://cardconjurer.com/creator/")

            # 等待页面加载
            wait = WebDriverWait(self.driver, 10)

            # 读取JSON内容
            with open(json_path, 'r', encoding='utf-8') as f:
                json_content = f.read()

            # 查找并点击"Load"按钮
            # 注意: 这些选择器可能需要根据实际网站结构调整
            try:
                load_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load')]"))
                )
                load_button.click()
                time.sleep(1)
            except:
                print("⚠️ 未找到Load按钮，尝试其他方法...")

            # 查找JSON输入框并粘贴内容
            try:
                json_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[type='text']"))
                )
                json_input.clear()
                json_input.send_keys(json_content)
                time.sleep(1)
            except:
                # 尝试使用JavaScript注入
                script = f"document.querySelector('textarea').value = `{json_content}`;"
                self.driver.execute_script(script)
                time.sleep(1)

            # 点击确认按钮
            try:
                confirm_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Confirm')]"))
                )
                confirm_button.click()
                time.sleep(2)
            except:
                print("⚠️ 未找到确认按钮")

            return True

        except Exception as e:
            print(f"❌ 加载JSON失败: {e}")
            return False

    def download_card_image(self, output_name: str) -> bool:
        """
        下载当前卡牌图片

        Args:
            output_name: 输出文件名（不含扩展名）

        Returns:
            是否成功下载
        """
        try:
            wait = WebDriverWait(self.driver, 10)

            # 查找下载按钮
            # 注意: 选择器需要根据实际网站结构调整
            download_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download') or contains(text(), 'Export')]"))
            )
            download_button.click()

            # 等待下载完成
            time.sleep(3)

            # 重命名下载的文件
            # 这部分逻辑需要根据实际下载文件名进行调整
            download_files = sorted(Path(self.download_dir).glob("*"), key=os.path.getmtime, reverse=True)
            if download_files:
                latest_file = download_files[0]
                new_name = Path(self.download_dir) / f"{output_name}.png"
                if latest_file.exists():
                    latest_file.rename(new_name)
                    print(f"✅ 已下载: {new_name}")
                    return True

            return False

        except Exception as e:
            print(f"❌ 下载图片失败: {e}")
            return False

    def batch_import_and_download(self, json_files: List[str]) -> int:
        """
        批量导入JSON文件并下载图片

        Args:
            json_files: JSON文件路径列表

        Returns:
            成功处理的数量
        """
        success_count = 0

        try:
            self.setup_driver()

            for json_file in json_files:
                print(f"\n处理: {json_file}")

                # 加载JSON
                if self.load_json_to_cardconjurer(json_file):
                    # 下载图片
                    file_name = Path(json_file).stem
                    if self.download_card_image(file_name):
                        success_count += 1
                    else:
                        print(f"⚠️ 下载失败: {json_file}")
                else:
                    print(f"⚠️ 加载失败: {json_file}")

                # 短暂延迟避免请求过快
                time.sleep(1)

        except Exception as e:
            print(f"❌ 批量处理出错: {e}")
        finally:
            if self.driver:
                self.driver.quit()

        return success_count

    def __enter__(self):
        """上下文管理器入口"""
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if self.driver:
            self.driver.quit()


def main():
    """主函数示例"""
    import argparse

    parser = argparse.ArgumentParser(description='CardConjurer自动化工具')
    parser.add_argument('json_dir', help='JSON文件目录')
    parser.add_argument('-o', '--output', default='downloaded_images', help='输出目录')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')

    args = parser.parse_args()

    # 获取所有JSON文件
    json_files = list(Path(args.json_dir).glob("*.json"))

    if not json_files:
        print(f"❌ 未找到JSON文件: {args.json_dir}")
        return

    print(f"找到 {len(json_files)} 个JSON文件")

    # 批量处理
    automation = CardConjurerAutomation(headless=args.headless, download_dir=args.output)
    success_count = automation.batch_import_and_download(json_files)

    print(f"\n🎉 完成！成功处理 {success_count}/{len(json_files)} 张卡牌")


if __name__ == '__main__':
    main()
