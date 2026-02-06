#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片拼接模块
将多张卡牌图片按照n×m网格拼接成大图，用于桌游模拟器
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image


class ImageStitcher:
    """图片拼接器类"""

    def __init__(self, card_width: int = 1500, card_height: int = 2100):
        """
        初始化拼接器

        Args:
            card_width: 单张卡牌宽度（像素）
            card_height: 单张卡牌高度（像素）
        """
        self.card_width = card_width
        self.card_height = card_height

    def load_images(self, image_paths: List[str]) -> List[Image.Image]:
        """
        加载图片列表

        Args:
            image_paths: 图片路径列表

        Returns:
            PIL Image对象列表
        """
        images = []
        for path in image_paths:
            try:
                img = Image.open(path)
                # 调整到统一尺寸
                img = img.resize((self.card_width, self.card_height), Image.Resampling.LANCZOS)
                images.append(img)
            except Exception as e:
                print(f"⚠️ 加载图片失败 {path}: {e}")
        return images

    def stitch_images(
        self,
        image_paths: List[str],
        rows: int,
        cols: int,
        output_path: str,
        spacing: int = 0,
        background_color: Tuple[int, int, int] = (255, 255, 255)
    ) -> bool:
        """
        拼接图片成网格

        Args:
            image_paths: 图片路径列表
            rows: 行数
            cols: 列数
            output_path: 输出文件路径
            spacing: 图片间距（像素）
            background_color: 背景颜色RGB

        Returns:
            是否成功拼接
        """
        try:
            # 加载图片
            images = self.load_images(image_paths)

            if not images:
                print("❌ 没有成功加载任何图片")
                return False

            # 计算需要的图片数量
            required_count = rows * cols
            if len(images) < required_count:
                print(f"⚠️ 图片数量不足: 需要 {required_count} 张，实际 {len(images)} 张")
                print(f"⚠️ 将使用空白填充")

            # 创建大图
            canvas_width = cols * self.card_width + (cols - 1) * spacing
            canvas_height = rows * self.card_height + (rows - 1) * spacing
            canvas = Image.new('RGB', (canvas_width, canvas_height), background_color)

            # 粘贴图片
            for idx in range(required_count):
                row = idx // cols
                col = idx % cols

                x = col * (self.card_width + spacing)
                y = row * (self.card_height + spacing)

                if idx < len(images):
                    canvas.paste(images[idx], (x, y))
                else:
                    # 创建空白卡牌
                    blank = Image.new('RGB', (self.card_width, self.card_height), (240, 240, 240))
                    canvas.paste(blank, (x, y))

            # 保存图片
            canvas.save(output_path, quality=95)
            print(f"✅ 拼接完成: {output_path}")
            print(f"   尺寸: {canvas_width}×{canvas_height} 像素")
            print(f"   网格: {rows}×{cols}")

            return True

        except Exception as e:
            print(f"❌ 拼接失败: {e}")
            return False

    def auto_stitch(
        self,
        image_dir: str,
        output_path: str,
        max_cols: int = 10,
        spacing: int = 0
    ) -> bool:
        """
        自动拼接目录中的所有图片

        Args:
            image_dir: 图片目录
            output_path: 输出文件路径
            max_cols: 最大列数
            spacing: 图片间距

        Returns:
            是否成功拼接
        """
        # 获取所有图片文件
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        image_paths = [
            str(p) for p in Path(image_dir).iterdir()
            if p.suffix.lower() in image_extensions
        ]

        if not image_paths:
            print(f"❌ 未找到图片文件: {image_dir}")
            return False

        # 排序确保顺序一致
        image_paths.sort()

        # 计算行列数
        total = len(image_paths)
        cols = min(total, max_cols)
        rows = (total + cols - 1) // cols

        print(f"找到 {total} 张图片，将拼接为 {rows}×{cols} 网格")

        return self.stitch_images(image_paths, rows, cols, output_path, spacing)

    def create_tabletop_simulator_deck(
        self,
        image_paths: List[str],
        output_dir: str,
        cards_per_sheet: int = 70,
        cols: int = 10
    ) -> List[str]:
        """
        为Tabletop Simulator创建卡牌组
        TTS推荐: 最大70张卡/页，10列×7行

        Args:
            image_paths: 图片路径列表
            output_dir: 输出目录
            cards_per_sheet: 每页卡牌数
            cols: 列数

        Returns:
            生成的大图路径列表
        """
        os.makedirs(output_dir, exist_ok=True)

        output_files = []
        total_images = len(image_paths)
        sheet_count = (total_images + cards_per_sheet - 1) // cards_per_sheet

        print(f"生成 {sheet_count} 张TTS卡牌页...")

        for sheet_idx in range(sheet_count):
            # 获取当前页的图片
            start_idx = sheet_idx * cards_per_sheet
            end_idx = min(start_idx + cards_per_sheet, total_images)
            sheet_images = image_paths[start_idx:end_idx]

            # 计算行数
            rows = (len(sheet_images) + cols - 1) // cols

            # 生成输出文件名
            output_file = os.path.join(output_dir, f"deck_sheet_{sheet_idx + 1}.png")

            # 拼接图片
            if self.stitch_images(sheet_images, rows, cols, output_file, spacing=0):
                output_files.append(output_file)

        return output_files


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='卡牌图片拼接工具')
    parser.add_argument('input_dir', help='输入图片目录')
    parser.add_argument('-o', '--output', default='stitched_output.png', help='输出文件路径')
    parser.add_argument('-r', '--rows', type=int, help='行数（可选，自动计算）')
    parser.add_argument('-c', '--cols', type=int, default=10, help='列数（默认: 10）')
    parser.add_argument('-s', '--spacing', type=int, default=0, help='图片间距（默认: 0）')
    parser.add_argument('--tts', action='store_true', help='生成TTS格式（10×7，每页70张）')
    parser.add_argument('--card-width', type=int, default=1500, help='卡牌宽度（默认: 1500）')
    parser.add_argument('--card-height', type=int, default=2100, help='卡牌高度（默认: 2100）')

    args = parser.parse_args()

    stitcher = ImageStitcher(card_width=args.card_width, card_height=args.card_height)

    if args.tts:
        # TTS模式
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        image_paths = [
            str(p) for p in Path(args.input_dir).iterdir()
            if p.suffix.lower() in image_extensions
        ]
        image_paths.sort()

        output_dir = Path(args.output).parent / 'tts_decks'
        sheets = stitcher.create_tabletop_simulator_deck(
            image_paths, str(output_dir), cards_per_sheet=70, cols=10
        )
        print(f"\n🎉 生成了 {len(sheets)} 张TTS卡牌页")

    else:
        # 普通拼接模式
        if args.rows:
            # 手动指定行列数
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
            image_paths = [
                str(p) for p in Path(args.input_dir).iterdir()
                if p.suffix.lower() in image_extensions
            ]
            image_paths.sort()
            stitcher.stitch_images(
                image_paths, args.rows, args.cols, args.output, args.spacing
            )
        else:
            # 自动拼接
            stitcher.auto_stitch(
                args.input_dir, args.output, max_cols=args.cols, spacing=args.spacing
            )


if __name__ == '__main__':
    main()
