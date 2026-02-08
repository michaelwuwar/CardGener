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
from selenium.common.exceptions import TimeoutException
from PIL import Image


class CardConjurerAutomation:
    """CardConjurer自动化类"""
    CREATOR_URL = "https://cardconjurer.com/creator/"

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
            # 仅在当前不是创建器页面时导航（允许调用方先预加载页面并在每次导入前刷新）
            creator = getattr(self, 'CREATOR_URL', "https://cardconjurer.com/creator/")
            try:
                if not self.driver.current_url.startswith(creator):
                    self.driver.get(creator)
            except Exception:
                # 如果 current_url 不可用或其它问题，做一次导航以确保处于目标页面
                self.driver.get(creator)

            # 等待页面加载完成并等待上传器或文本区域出现（防止第一次导入过早执行）
            wait = WebDriverWait(self.driver, 6)
            try:
                wait.until(lambda d: d.execute_script("return document.readyState") == 'complete')
            except TimeoutException:
                pass

            try:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "drag-drop-upload, textarea, input[type='file'], .file-upload"))
                )
            except TimeoutException:
                # 如果没有检测到这些元素，短暂回退等待以提高兼容性
                time.sleep(1)

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

                abs_path = os.path.abspath(str(json_path))
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

            # 等待卡牌内容准备就绪（Save/Download 按钮出现，或 canvas/img 渲染完成）
            try:
                if not self._wait_for_card_ready(timeout=6):
                    # 最后尝试给页面多一点时间，但不要无限等待
                    time.sleep(1)
            except Exception:
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

    def _wait_for_card_ready(self, timeout: int = 6) -> bool:
        """
        等待页面上卡牌渲染完成的通用检查：
        - 查找可点击的 Save/Download/Export 按钮
        - 或者页面包含 canvas 元素
        - 或者存在已加载的 img（naturalWidth > 50）

        返回 True 表示已就绪，False 表示超时。
        """
        if not self.driver:
            return False

        end_time = time.time() + int(timeout)
        poll = 0.5

        check_script = (
            "var btns = Array.from(document.querySelectorAll('button'));"
            "for(var i=0;i<btns.length;i++){var t=(btns[i].innerText||btns[i].textContent||'').trim();"
            "if(/Save Image|Save|Download|Export|Export Image|Export PNG/i.test(t)) return true;}"
            "if(document.querySelector('canvas')) return true;"
            "var imgs = Array.from(document.images); for(var j=0;j<imgs.length;j++){ if(imgs[j].naturalWidth && imgs[j].naturalWidth>50) return true;}"
            "return false;"
        )

        while time.time() < end_time:
            try:
                ok = self.driver.execute_script(check_script)
                if ok:
                    return True
            except Exception:
                # 忽略脚本执行错误，继续重试
                pass
            time.sleep(poll)

        return False

    def overlay_art_on_card_with_bounds(self, base_card_path: str, art_path: str, bounds: dict, output_path: Optional[str] = None) -> bool:
        """
        将艺术图按 JSON 中的 bounds 放置并保存。

        bounds: dict 应包含 x, y, width, height, 可选 type('fill'|'fit'), horizontal, vertical。
        """
        try:
            base = Image.open(base_card_path).convert('RGBA')
            art = Image.open(art_path).convert('RGBA')

            bw, bh = base.size

            bx = int(bounds.get('x', 0))
            by = int(bounds.get('y', 0))
            bwidth = int(bounds.get('width', bw))
            bheight = int(bounds.get('height', bh))

            # 计算按 type 缩放：'fill' 为 cover，其他为 contain
            aw, ah = art.size
            if bounds.get('type') == 'fill':
                scale = max(bwidth / aw, bheight / ah)
            else:
                scale = min(bwidth / aw, bheight / ah, 1.0)

            new_w = max(1, int(aw * scale))
            new_h = max(1, int(ah * scale))
            art_resized = art.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # 根据 horizontal/vertical 对齐
            horiz = bounds.get('horizontal', 'center')
            vert = bounds.get('vertical', 'center')

            if horiz == 'left':
                ax = bx
            elif horiz == 'right':
                ax = bx + bwidth - new_w
            else:
                ax = bx + (bwidth - new_w) // 2

            if vert == 'top':
                ay = by
            elif vert == 'bottom':
                ay = by + bheight - new_h
            else:
                ay = by + (bheight - new_h) // 2

            # 将 art 放在底层，然后把 base 盖在上面（保持卡牌前景覆盖）
            composed = Image.new('RGBA', base.size, (0, 0, 0, 0))
            composed.paste(art_resized, (ax, ay), art_resized)
            composed.paste(base, (0, 0), base)

            target = output_path or base_card_path
            out_dir = os.path.dirname(target)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            if target.lower().endswith('.png'):
                composed.save(target)
            else:
                composed.convert('RGB').save(target)

            print(f"✅ 已按 bounds 叠加并保存: {target}")
            return True
        except Exception as e:
            print(f"❌ 按 bounds 叠加失败 ({base_card_path} <- {art_path}): {e}")
            return False

    def overlay_art_on_card(self, base_card_path: str, art_path: str, output_path: Optional[str] = None, margin_ratio: float = 0.05) -> bool:
        """
        退化的居中叠加行为（当 JSON bounds 不可用时使用）。
        """
        try:
            base = Image.open(base_card_path).convert("RGBA")
            art = Image.open(art_path).convert("RGBA")

            bw, bh = base.size
            max_w = int(bw * (1.0 - 2 * margin_ratio))
            max_h = int(bh * (1.0 - 2 * margin_ratio))

            aw, ah = art.size
            scale = min(max_w / aw, max_h / ah, 1.0)
            new_w = max(1, int(aw * scale))
            new_h = max(1, int(ah * scale))
            art_resized = art.resize((new_w, new_h), Image.Resampling.LANCZOS)

            x = (bw - new_w) // 2
            y = (bh - new_h) // 2

            # 将 art 放在底层，再把 base 盖上（保证卡牌在上层）
            composed = Image.new('RGBA', base.size, (0, 0, 0, 0))
            composed.paste(art_resized, (x, y), art_resized)
            composed.paste(base, (0, 0), base)

            target = output_path or base_card_path
            out_dir = os.path.dirname(target)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            if target.lower().endswith('.png'):
                composed.save(target)
            else:
                composed.convert('RGB').save(target)

            print(f"✅ 已将艺术图叠加并保存: {target}")
            return True
        except Exception as e:
            print(f"❌ 叠加艺术图失败 ({base_card_path} <- {art_path}): {e}")
            return False

    def overlay_generated_art(self, art_dir: str, source_dir: Optional[str] = None, json_dir: Optional[str] = None, inplace: bool = True, margin_ratio: float = 0.05) -> int:
        """
        批量将 art_dir 中的本地生成图片叠加到 source_dir（默认为 self.download_dir）中的卡牌图片上。

        优先使用 json_dir 中的 JSON 来读取 Art 的 bounds 以精确定位；找不到 JSON 时退回到居中叠加。
        """
        src = source_dir or self.download_dir
        count = 0
        try:
            art_dir_p = Path(art_dir)
            src_p = Path(src)
            json_p = Path(json_dir) if json_dir else None

            if not art_dir_p.exists() or not src_p.exists():
                print(f"❌ 指定目录不存在: art_dir={art_dir} source_dir={src}")
                return 0

            # map art files by stem
            art_files = {p.stem: p for p in art_dir_p.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')}

            # map json bounds by stem when available
            json_bounds = {}
            if json_p and json_p.exists():
                for jp in json_p.glob('*.json'):
                    try:
                        import json as _json
                        data = _json.loads(jp.read_text(encoding='utf-8'))
                        # 寻找 Art image 的 bounds
                        def find_art_bounds(obj):
                            if isinstance(obj, dict):
                                if obj.get('type') == 'image' and obj.get('name') == 'Art':
                                    return obj.get('bounds')
                                for v in obj.get('children', []):
                                    res = find_art_bounds(v)
                                    if res:
                                        return res
                            return None

                        b = find_art_bounds(data.get('data', {}))
                        if b:
                            json_bounds[jp.stem] = b
                    except Exception:
                        continue

            for base_file in src_p.iterdir():
                if base_file.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
                    continue
                stem = base_file.stem

                # find matching art
                art_path = art_files.get(stem)
                if not art_path:
                    # try fuzzy match
                    for k, v in art_files.items():
                        if k.startswith(stem) or stem.startswith(k):
                            art_path = v
                            break

                if not art_path:
                    continue

                target = str(base_file) if inplace else str(base_file.with_name(f"{base_file.stem}_with_art{base_file.suffix}"))

                # if we have bounds for this stem, use it
                bounds = json_bounds.get(stem)
                if bounds:
                    ok = self.overlay_art_on_card_with_bounds(str(base_file), str(art_path), bounds, target)
                else:
                    ok = self.overlay_art_on_card(str(base_file), str(art_path), target, margin_ratio=margin_ratio)

                if ok:
                    count += 1

            print(f"🎉 完成叠加: 成功处理 {count} 张图片")
            return count

        except Exception as e:
            print(f"❌ 批量叠加失败: {e}")
            return count

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

            # 预先加载一次创建器页面，给页面额外时间完成首次加载（可避免首条导入过早触发的问题）
            try:
                creator = getattr(self, 'CREATOR_URL', "https://cardconjurer.com/creator/")
                self.driver.get(creator)
                initial_wait = WebDriverWait(self.driver, 6)
                try:
                    initial_wait.until(lambda d: d.execute_script("return document.readyState") == 'complete')
                except Exception:
                    pass
                try:
                    initial_wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "drag-drop-upload, textarea, input[type='file'], .file-upload"))
                    )
                except Exception:
                    time.sleep(1)
                # 额外短暂停顿让页面内部脚本稳定
                time.sleep(1)
            except Exception:
                pass

            wait = WebDriverWait(self.driver, 6)

            for json_file in json_files:
                print(f"\n处理: {json_file}")

                # 在处理每个 JSON 前刷新页面以确保上传器处于可交互状态
                try:
                    self.driver.refresh()
                    try:
                        wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "drag-drop-upload, textarea, input[type='file'], .file-upload"))
                        )
                    except Exception:
                        time.sleep(0.5)
                except Exception:
                    # 刷新失败则继续尝试直接导入
                    pass

                # 加载JSON（函数内部只在非创建器页面时导航）
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
    parser.add_argument('--overlay-dir', default=None, help='本地生成图片目录，用于覆盖下载的卡牌图（按文件名stem匹配）')

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

    # 如果用户指定了本地生成艺术图目录，则尝试叠加到已下载的卡牌图片上
    if args.overlay_dir:
        try:
            overlayed = automation.overlay_generated_art(args.overlay_dir, source_dir=args.output, json_dir=args.json_dir, inplace=True)
            print(f"\n🎨 叠加完成: {overlayed} 张图片已被覆盖")
        except Exception as e:
            print(f"⚠️ 叠加步骤出错: {e}")


if __name__ == '__main__':
    main()
