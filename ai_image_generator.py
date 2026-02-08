#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI图片生成模块
使用免费API生成卡牌图片
"""

import os
import base64
import time
import json
from typing import Optional
from pathlib import Path
import requests
from io import BytesIO


class AIImageGenerator:
    """AI图片生成器类"""

    def __init__(self, api_type: str = "pollinations"):
        """
        初始化AI图片生成器

        Args:
            api_type: API类型 (pollinations, craiyon, etc.)
        """
        self.api_type = api_type
        self.cache_dir = "generated_images_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def generate_with_pollinations(self, prompt: str, width: int = 1024, height: int = 1024) -> Optional[bytes]:
        """
        使用Pollinations AI生成图片（免费）

        Args:
            prompt: 图片描述
            width: 宽度
            height: 高度

        Returns:
            图片字节数据或None
        """
        try:
            # Pollinations API endpoint
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt, safe='')}"
            params = {
                "width": width,
                "height": height,
                "nologo": "true"
            }

            print(f"🎨 生成图片: {prompt[:50]}...")

            response = requests.get(url, params=params, timeout=60)

            if response.status_code == 200:
                print(f"✅ 图片生成成功")
                return response.content
            else:
                print(f"❌ 生成失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 生成图片时出错: {e}")
            return None

    def generate_with_stability(self, prompt: str, api_key: Optional[str] = None) -> Optional[bytes]:
        """
        使用Stability AI生成图片（需要API密钥）

        Args:
            prompt: 图片描述
            api_key: Stability AI API密钥

        Returns:
            图片字节数据或None
        """
        if not api_key:
            api_key = os.environ.get("STABILITY_API_KEY")

        if not api_key:
            print("⚠️ 未设置STABILITY_API_KEY环境变量")
            return None

    def generate_with_huggingface(
        self,
        prompt: str,
        model: str = "stabilityai/stable-diffusion-2",
        api_key: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> Optional[bytes]:
        """
        使用 Hugging Face 推理 API 生成图片（需 API token，可试用免费额度）

        返回图片字节或 None。
        """
        if not api_key:
            api_key = os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY")

        if not api_key:
            print("⚠️ 未设置 Hugging Face API key (环境变量 HF_API_KEY 或 HUGGINGFACE_API_KEY)")
            return None

        url = f"https://api-inference.huggingface.co/models/{model}"

        headers = {"Authorization": f"Bearer {api_key}"}

        payload = {
            "inputs": prompt,
            "options": {"wait_for_model": True},
            "parameters": {"width": width, "height": height}
        }

        try:
            print(f"🎨 使用 Hugging Face ({model}) 生成图片...")
            response = requests.post(url, headers=headers, json=payload, timeout=120)

            # 如果直接返回二进制图像（Content-Type: image/*）
            ctype = response.headers.get("content-type", "")
            if ctype.startswith("image"):
                print("✅ 图片生成成功 (Hugging Face)")
                return response.content

            # 否则尝试解析 JSON 中的 base64 字符串
            try:
                data = response.json()
            except Exception:
                print(f"❌ Hugging Face 返回错误: HTTP {response.status_code}")
                return None

            # 常见返回可能带有 base64 字符串字段
            # 搜索第一个看起来像 base64 的值
            def find_base64(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        res = find_base64(v)
                        if res:
                            return res
                elif isinstance(obj, list):
                    for v in obj:
                        res = find_base64(v)
                        if res:
                            return res
                elif isinstance(obj, str):
                    # 简单判断是否为 base64（数据较长且只包含 base64 字符）
                    if len(obj) > 200 and all(c.isalnum() or c in "+/=\n\r" for c in obj):
                        return obj
                return None

            b64 = find_base64(data)
            if b64:
                try:
                    image_data = base64.b64decode(b64)
                    print("✅ 图片生成成功 (Hugging Face - base64)")
                    return image_data
                except Exception:
                    pass

            print(f"❌ Hugging Face 生成失败或无有效图像: HTTP {response.status_code}")
            return None

        except Exception as e:
            print(f"❌ 使用 Hugging Face 生成时出错: {e}")
            return None

    def generate_with_modelscope(
        self,
        prompt: str,
        model: str = "damo/text-to-image",
        api_key: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> Optional[bytes]:
        """
        使用 ModelScope 文生图（Z-Image 等）API。需要在环境变量 MODELSCOPE_API_KEY 中设置 token，或传入 api_key。

        注意：ModelScope 的模型名可能需要调整为可用的 text-to-image 模型（例如 Z-Image-Turbo 的具体标识）。
        """
        if not api_key:
            api_key = os.environ.get("MODELSCOPE_API_KEY")

        if not api_key:
            print("⚠️ 未设置 MODELSCOPE_API_KEY 环境变量")
            return None

        url = f"https://api.modelscope.cn/api/v1/models/{model}/invoke"

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        payload = {"input": prompt, "parameters": {"width": width, "height": height}}

        try:
            print(f"🎨 使用 ModelScope ({model}) 生成图片...")
            response = requests.post(url, headers=headers, json=payload, timeout=120)

            ctype = response.headers.get("content-type", "")
            if ctype.startswith("image"):
                print("✅ 图片生成成功 (ModelScope)")
                return response.content

            # 尝试解析 JSON，寻找 base64 图像
            data = response.json()
            # 常见 ModelScope 返回可能在 outputs 或 data 字段
            candidates = []
            if isinstance(data, dict):
                for k in ("outputs", "output", "data", "result"):
                    v = data.get(k)
                    if v:
                        candidates.append(v)

            def find_b64(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        res = find_b64(v)
                        if res:
                            return res
                elif isinstance(obj, list):
                    for v in obj:
                        res = find_b64(v)
                        if res:
                            return res
                elif isinstance(obj, str):
                    if len(obj) > 200 and all(c.isalnum() or c in "+/=\n\r" for c in obj):
                        return obj
                return None

            b64 = None
            for cand in candidates:
                b64 = find_b64(cand)
                if b64:
                    break

            if b64:
                try:
                    image_data = base64.b64decode(b64)
                    print("✅ 图片生成成功 (ModelScope - base64)")
                    return image_data
                except Exception:
                    pass

            print(f"❌ ModelScope 返回但未找到图像: HTTP {response.status_code}")
            return None

        except Exception as e:
            print(f"❌ 使用 ModelScope 生成时出错: {e}")
            return None

    def generate_with_modelscope_inference(
        self,
        prompt: str,
        model: str = "Qwen/Qwen-Image",
        api_key: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        poll_interval: int = 5,
    ) -> Optional[bytes]:
        """
        使用 ModelScope 推理异步接口 (api-inference.modelscope.cn) 生成图片。

        示例流程参考：POST /v1/images/generations -> poll /v1/tasks/{task_id} -> 获取 data['output_images'][0]
        返回图片字节或 None。
        """
        if not api_key:
            api_key = os.environ.get("MODELSCOPE_SDK_TOKEN") or os.environ.get("MODELSCOPE_API_KEY")

        if not api_key:
            print("⚠️ 未设置 ModelScope SDK token (环境变量 MODELSCOPE_SDK_TOKEN 或 MODELSCOPE_API_KEY)")
            return None

        base_url = "https://api-inference.modelscope.cn/"

        common_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "width": width,
            "height": height,
        }

        try:
            print(f"🎨 使用 ModelScope 推理接口 ({model}) 生成图片 (异步)...")
            resp = requests.post(
                f"{base_url}v1/images/generations",
                headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                timeout=30,
            )
            resp.raise_for_status()
            task_id = resp.json().get("task_id")
            if not task_id:
                print("❌ 未返回 task_id")
                return None

            # 轮询任务
            while True:
                result = requests.get(
                    f"{base_url}v1/tasks/{task_id}",
                    headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
                    timeout=30,
                )
                result.raise_for_status()
                data = result.json()

                status = data.get("task_status")
                if status == "SUCCEED":
                    output_images = data.get("output_images") or []
                    if not output_images:
                        print("❌ 任务成功但未返回图片 URL")
                        return None

                    image_url = output_images[0]
                    img_resp = requests.get(image_url, timeout=60)
                    img_resp.raise_for_status()
                    print("✅ 图片生成成功 (ModelScope 推理)")
                    return img_resp.content

                if status == "FAILED":
                    print("❌ Image Generation Failed.")
                    return None

                time.sleep(poll_interval)

        except Exception as e:
            print(f"❌ 使用 ModelScope 推理接口时出错: {e}")
            return None

        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30
            }

            print(f"🎨 使用Stability AI生成图片...")

            response = requests.post(url, json=payload, headers=headers, timeout=120)

            if response.status_code == 200:
                data = response.json()
                if data.get("artifacts"):
                    image_data = base64.b64decode(data["artifacts"][0]["base64"])
                    print(f"✅ 图片生成成功")
                    return image_data

            print(f"❌ 生成失败: {response.status_code}")
            return None

        except Exception as e:
            print(f"❌ 生成图片时出错: {e}")
            return None

    def generate_card_art_prompt(self, card_data: dict) -> str:
        """
        从卡牌数据生成图片提示词

        Args:
            card_data: 卡牌数据字典

        Returns:
            图片生成提示词
        """
        card_name = card_data.get("card_name", "")
        card_type = card_data.get("card_type", "")
        rules_text = card_data.get("rules_text", "")
        class_type = card_data.get("class_type", "")

        # 构建提示词
        prompt_parts = []

        # 添加类型相关的风格
        class_styles = {
            "ninja": "stealthy ninja, shadowy figure, dark atmosphere",
            "warrior": "brave warrior, armored fighter, epic battlefield",
            "wizard": "mystical wizard, magical energy, arcane symbols",
            "ranger": "skilled ranger, nature background, bow and arrow",
            "guardian": "protective guardian, shield and armor, defensive stance"
        }

        if class_type in class_styles:
            prompt_parts.append(class_styles[class_type])

        # 添加卡牌名称
        if card_name:
            prompt_parts.append(f"themed around {card_name}")

        # 添加动作描述（从规则文本提取）
        if "damage" in rules_text.lower():
            prompt_parts.append("dynamic action scene")
        elif "defense" in rules_text.lower() or "prevent" in rules_text.lower():
            prompt_parts.append("defensive posture")

        # 添加艺术风格
        prompt_parts.append("fantasy card game art")
        prompt_parts.append("high quality")
        prompt_parts.append("detailed illustration")

        prompt = ", ".join(prompt_parts)
        return prompt

    def generate_and_save(
        self,
        prompt: str,
        output_path: str,
        width: int = 1024,
        height: int = 1024,
        poll_interval: int = 5,
    ) -> bool:
        """
        生成并保存图片

        Args:
            prompt: 图片描述
            output_path: 输出路径
            width: 宽度
            height: 高度

        Returns:
            是否成功
        """
        # 使用选择的API生成图片
        if self.api_type == "pollinations":
            image_data = self.generate_with_pollinations(prompt, width, height)
        elif self.api_type == "stability":
            image_data = self.generate_with_stability(prompt)
        elif self.api_type == "huggingface":
            model = getattr(self, 'api_model', None) or "stabilityai/stable-diffusion-2"
            api_key = getattr(self, 'api_key', None)
            image_data = self.generate_with_huggingface(prompt, model=model, api_key=api_key, width=width, height=height)
        elif self.api_type == "modelscope":
            model = getattr(self, 'api_model', None) or "damo/text-to-image"
            api_key = getattr(self, 'api_key', None)
            image_data = self.generate_with_modelscope(prompt, model=model, api_key=api_key, width=width, height=height)
        elif self.api_type == "modelscope_inference":
            model = getattr(self, 'api_model', None) or "Qwen/Qwen-Image"
            api_key = getattr(self, 'api_key', None)
            poll = getattr(self, 'poll_interval', poll_interval)
            image_data = self.generate_with_modelscope_inference(prompt, model=model, api_key=api_key, width=width, height=height, poll_interval=poll)
        else:
            print(f"❌ 不支持的API类型: {self.api_type}")
            return False

        if image_data:
            try:
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                print(f"✅ 图片已保存: {output_path}")
                return True
            except Exception as e:
                print(f"❌ 保存图片失败: {e}")
                return False

        return False

    def batch_generate_card_art(
        self,
        cards_data: list,
        output_dir: str,
        delay: float = 2.0
    ) -> dict:
        """
        批量为卡牌生成艺术图片

        Args:
            cards_data: 卡牌数据列表
            output_dir: 输出目录
            delay: 请求间延迟（秒）

        Returns:
            结果字典 {card_name: image_path}
        """
        os.makedirs(output_dir, exist_ok=True)

        results = {}

        for idx, card_data in enumerate(cards_data):
            card_name = card_data.get("card_name", f"card_{idx}")
            safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')

            output_path = os.path.join(output_dir, f"{safe_name}.png")

            # 生成提示词
            prompt = self.generate_card_art_prompt(card_data)

            print(f"\n[{idx + 1}/{len(cards_data)}] 生成 {card_name}...")
            print(f"提示词: {prompt}")

            # 生成图片
            if self.generate_and_save(prompt, output_path):
                results[card_name] = output_path
            else:
                print(f"⚠️ 跳过 {card_name}")

            # 延迟避免请求过快
            if idx < len(cards_data) - 1:
                time.sleep(delay)

        return results

    def enhance_existing_cards(
        self,
        json_dir: str,
        output_dir: str,
        update_json: bool = False,
        width: int = 1024,
        height: int = 1024,
        poll_interval: int = 5,
        skip_if_exists: bool = True,
    ) -> int:
        """
        为现有卡牌JSON生成图片并更新art_path

        Args:
            json_dir: JSON文件目录
            output_dir: 图片输出目录
            update_json: 是否更新JSON中的art_path

        Returns:
            成功生成的数量
        """
        json_files = list(Path(json_dir).glob("*.json"))

        if not json_files:
            print(f"❌ 未找到JSON文件: {json_dir}")
            return 0

        print(f"找到 {len(json_files)} 个JSON文件")

        os.makedirs(output_dir, exist_ok=True)

        success_count = 0

        for json_file in json_files:
            try:
                # 读取JSON
                with open(json_file, 'r', encoding='utf-8') as f:
                    card_json = json.load(f)

                # 提取卡牌数据
                card_data = self.extract_card_data_from_json(card_json)

                # 生成图片
                card_name = card_data.get("card_name", json_file.stem)
                safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')

                output_path = os.path.join(output_dir, f"{safe_name}.png")

                prompt = self.generate_card_art_prompt(card_data)

                print(f"\n生成 {card_name}...")

                # 如果目标图片已存在且用户选择跳过，则直接跳过该卡牌
                if skip_if_exists and os.path.exists(output_path):
                    print(f"⚠️ 图片已存在，跳过: {output_path}")
                    # 不更新 JSON，也不计入成功数
                    continue

                if self.generate_and_save(prompt, output_path, width=width, height=height, poll_interval=poll_interval):
                    success_count += 1

                    # 更新JSON中的art_path
                    if update_json:
                        self.update_json_art_path(card_json, output_path)
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(card_json, f, indent=4, ensure_ascii=False)
                        print(f"✅ 已更新JSON: {json_file}")

                time.sleep(2.0)  # 延迟

            except Exception as e:
                print(f"❌ 处理失败 {json_file}: {e}")

        return success_count

    def extract_card_data_from_json(self, card_json: dict) -> dict:
        """从CardConjurer JSON提取卡牌数据"""
        card_data = {}

        def find_text_field(data, field_name):
            if isinstance(data, dict):
                if data.get('type') == 'text' and data.get('name') == field_name:
                    return data.get('text', '')
                if 'children' in data:
                    for child in data['children']:
                        result = find_text_field(child, field_name)
                        if result:
                            return result
            return ''

        data = card_json.get('data', {})
        card_data['card_name'] = find_text_field(data, 'Title')
        card_data['card_type'] = find_text_field(data, 'Type')
        card_data['rules_text'] = find_text_field(data, 'Rules')
        card_data['class_type'] = 'ninja'  # 默认值

        return card_data

    def update_json_art_path(self, card_json: dict, art_path: str):
        """更新JSON中的art_path"""
        def update_image_field(data, art_path):
            if isinstance(data, dict):
                if data.get('type') == 'image' and data.get('name') == 'Art':
                    data['src'] = art_path
                    return True
                if 'children' in data:
                    for child in data['children']:
                        if update_image_field(child, art_path):
                            return True
            return False

        update_image_field(card_json.get('data', {}), art_path)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='AI卡牌图片生成器')
    parser.add_argument('--prompt', type=str, help='图片描述')
    parser.add_argument('-o', '--output', default='generated_art.png', help='输出文件路径')
    parser.add_argument('--json-dir', type=str, help='JSON文件目录（批量模式）')
    parser.add_argument('--output-dir', default='generated_art', help='输出目录（批量模式）')
    parser.add_argument('--api', default='pollinations', choices=['pollinations', 'stability', 'huggingface', 'modelscope', 'modelscope_inference'], help='API类型')
    parser.add_argument('--width', type=int, default=1024, help='图片宽度')
    parser.add_argument('--height', type=int, default=1024, help='图片高度')
    parser.add_argument('--poll-interval', type=int, default=5, help='ModelScope 推理轮询间隔（秒）')

    parser.add_argument('--api-key', type=str, default=None, help='API 密钥 (Hugging Face: HF_API_KEY, ModelScope: MODELSCOPE_API_KEY)')
    parser.add_argument('--model', type=str, default=None, help='指定模型（Hugging Face 或 ModelScope 的模型标识）')

    args = parser.parse_args()

    generator = AIImageGenerator(api_type=args.api)

    # 将可选的 api_key / model 传入 generator，方法会读取这些属性
    if args.api_key:
        generator.api_key = args.api_key
    if args.model:
        generator.api_model = args.model

    if args.json_dir:
        # 批量模式（注意：默认不会修改 JSON 中的 art_path，因为 CardConjurer 仅接受 URL）
        count = generator.enhance_existing_cards(
            args.json_dir,
            args.output_dir,
            update_json=False,
            width=args.width,
            height=args.height,
            poll_interval=args.poll_interval,
        )
        print(f"\n🎉 成功生成 {count} 张图片")
    elif args.prompt:
        # 单张模式
        generator.generate_and_save(args.prompt, args.output, args.width, args.height)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
