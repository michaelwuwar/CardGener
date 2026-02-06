#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI图片生成模块
使用免费API生成卡牌图片
"""

import os
import base64
import time
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
        height: int = 1024
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
        update_json: bool = True
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
        import json

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

                if self.generate_and_save(prompt, output_path):
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
    parser.add_argument('--api', default='pollinations', choices=['pollinations', 'stability'], help='API类型')
    parser.add_argument('--width', type=int, default=1024, help='图片宽度')
    parser.add_argument('--height', type=int, default=1024, help='图片高度')

    args = parser.parse_args()

    generator = AIImageGenerator(api_type=args.api)

    if args.json_dir:
        # 批量模式
        count = generator.enhance_existing_cards(args.json_dir, args.output_dir, update_json=True)
        print(f"\n🎉 成功生成 {count} 张图片")
    elif args.prompt:
        # 单张模式
        generator.generate_and_save(args.prompt, args.output, args.width, args.height)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
