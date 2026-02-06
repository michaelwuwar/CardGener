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
            "download.default_directory": os.path.abspath(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        # Improve handling on some platforms
        prefs.setdefault("profile.default_content_settings.popups", 0)
        prefs.setdefault("safebrowsing.disable_download_protection", True)
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

            # 页面使用自定义的 drag-drop-upload 组件，包含一个文件输入框
            # 尝试通过 input[type=file] 上传 JSON 文件（优先针对 filetext="Card" 的上传器）
            try:
                wrapper = None
                try:
                    # 仅定位特定上传组件，不执行点击
                    wrapper = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'drag-drop-upload[filetext="Card"]'))
                    )
                except Exception:
                    # 回退到通用上传器选择器（仅定位，不点击）
                    try:
                        wrapper = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "drag-drop-upload, .file-upload, [class*='file-upload']"))
                        )
                    except Exception:
                        wrapper = None

                abs_path = os.path.abspath(json_path)
                file_input = None
                if wrapper:
                    try:
                        file_input = wrapper.find_element(By.CSS_SELECTOR, "input[type='file']")
                    except Exception:
                        file_input = None
                if file_input is None:
                    file_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                    )

                file_input.send_keys(abs_path)
                time.sleep(0.5)

                # 触发组件的 change/drop 事件以模拟拖拽，让组件识别已选文件
                try:
                    if wrapper:
                        try:
                            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", wrapper)
                        except Exception:
                            pass
                        try:
                            self.driver.execute_script(
                                "var dt=new DataTransfer(); for(var i=0;i<arguments[0].files.length;i++){dt.items.add(arguments[0].files[i]);} arguments[1].dispatchEvent(new DragEvent('drop',{dataTransfer:dt,bubbles:true}));",
                                file_input,
                                wrapper,
                            )
                        except Exception:
                            try:
                                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", file_input)
                            except Exception:
                                pass
                    else:
                        script = '''
var drop = document.querySelector(arguments[0]);
var input = document.querySelector("input[type=file]");
if(!input) return 'no-input';
var dt = new DataTransfer();
for(var i=0;i<input.files.length;i++){ dt.items.add(input.files[i]); }
if(drop){
  try{ drop.dispatchEvent(new Event('change', {bubbles:true})); }catch(e){}
  try{ drop.dispatchEvent(new DragEvent('drop', {dataTransfer: dt, bubbles:true})); }catch(e){}
  return 'dropped';
}
return 'no-drop';
'''
                        try:
                            self.driver.execute_script(script, "drag-drop-upload, .file-upload, [class*='file-upload']")
                        except Exception:
                            try:
                                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", file_input)
                            except Exception:
                                pass
                except Exception:
                    pass

                time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ 未能通过 file input 上传：{e}，尝试回退方案...")
                # 回退到 textarea 注入（兼容旧实现）
                try:
                    json_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[type='text']"))
                    )
                    json_input.clear()
                    json_input.send_keys(json_content)
                    time.sleep(1)
                except Exception as e2:
                    # 最后一招：使用 JS 注入到 textarea（如果存在）
                    try:
                        script = f"var ta = document.querySelector('textarea'); if(ta) ta.value = `{json_content}`;"
                        self.driver.execute_script(script)
                        time.sleep(1)
                    except Exception as e3:
                        print(f"❌ 注入 JSON 失败: {e3}")
                        return False

            # 有些页面在文件选择后需要点击确认或 Load 按钮，尝试点击常见的按钮
            try:
                confirm_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'Load') or contains(., 'OK') or contains(., 'Confirm')]")
                    )
                )
                confirm_button.click()
                time.sleep(2)
            except Exception:
                # 如果没有确认按钮，也可能已自动加载
                pass

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

            # 查找下载/保存按钮，页面使用 Material 按钮，文本为 Save Image
            try:
                download_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[.//mat-icon[contains(normalize-space(.),'download')] or contains(normalize-space(.),'Save Image') or contains(., 'Save Image')]")
                    )
                )
                download_button.click()
            except Exception:
                # 回退：旧站点可能使用 'Download' 或 'Export' 文本
                try:
                    download_button = wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(., 'Download') or contains(., 'Export')]")
                        )
                    )
                    download_button.click()
                except Exception as e:
                    print(f"❌ 未找到下载按钮: {e}")
                    return False

            # 等待并查找下载完成的文件（优先在 self.download_dir，其次尝试系统默认 Downloads）
            wait_time = 15
            poll_interval = 0.5
            end_time = time.time() + wait_time

            def find_new_file(search_dir, since_ts):
                exts = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
                candidates = []
                try:
                    for p in Path(search_dir).glob('*'):
                        try:
                            if p.is_file() and p.suffix.lower() in exts and os.path.getmtime(p) >= since_ts:
                                candidates.append(p)
                        except Exception:
                            continue
                except Exception:
                    return None
                if not candidates:
                    return None
                candidates.sort(key=os.path.getmtime, reverse=True)
                return candidates[0]

            # 记录点击前时间戳，寻找之后产生的新文件
            since_ts = time.time() - 1

            latest_file = None
            while time.time() < end_time and latest_file is None:
                # 优先检查目标下载目录
                latest_file = find_new_file(self.download_dir, since_ts)
                if latest_file:
                    break
                # 回退检查当前用户 Downloads 目录（Windows 常用位置）
                try:
                    user_download = os.path.join(os.path.expanduser('~'), 'Downloads')
                    latest_file = find_new_file(user_download, since_ts)
                    if latest_file:
                        break
                except Exception:
                    pass

                time.sleep(poll_interval)

            if not latest_file:
                print("❌ 未检测到下载的图片文件")
                return False

            # 确保目标目录存在
            os.makedirs(self.download_dir, exist_ok=True)
            new_name = Path(self.download_dir) / f"{output_name}{latest_file.suffix}"
            try:
                # 如果源路径与目标路径相同，直接返回成功
                try:
                    if latest_file.resolve() == new_name.resolve():
                        print(f"✅ 已下载（原地）: {new_name}")
                        return True
                except Exception:
                    # resolve 可能失败于不存在的文件，继续处理
                    pass

                # 如果目标已存在且不是源文件，先删除目标再移动
                if new_name.exists():
                    new_name.unlink()

                latest_file.replace(new_name)
                print(f"✅ 已下载并移动: {new_name}")
                return True
            except Exception as e:
                print(f"❌ 重命名/移动下载文件失败: {e}")
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
