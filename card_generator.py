#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CardConjurer卡牌批量生成器
从Excel表格批量生成CardConjurer格式的JSON卡牌文件
"""

import json
import os
from pathlib import Path
import pandas as pd
from typing import Dict, Any


class CardGenerator:
    """卡牌生成器类"""

    def __init__(self, template_path: str = "template.json"):
        """
        初始化生成器

        Args:
            template_path: JSON模板文件路径
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)

    def update_text_field(self, data: Dict[str, Any], field_name: str, value: str):
        """
        更新文本字段

        Args:
            data: JSON数据
            field_name: 字段名称
            value: 新值
        """
        if data.get('type') == 'text' and data.get('name') == field_name:
            data['text'] = value
            return True

        if 'children' in data:
            for child in data['children']:
                if self.update_text_field(child, field_name, value):
                    return True

        return False

    def update_image_field(self, data: Dict[str, Any], field_name: str, value: str):
        """
        更新图片字段

        Args:
            data: JSON数据
            field_name: 字段名称
            value: 新值
        """
        if data.get('type') == 'image' and data.get('name') == field_name:
            data['src'] = value
            return True

        if 'children' in data:
            for child in data['children']:
                if self.update_image_field(child, field_name, value):
                    return True

        return False

    def update_class_frame(self, data: Dict[str, Any], class_type: str):
        """
        更新职业框架

        Args:
            data: JSON数据
            class_type: 职业类型（如ninja, warrior等）
        """
        if data.get('type') == 'image' and 'Class' in data.get('name', ''):
            data['src'] = f"fab/frame/classes/{class_type.lower()}.png"
            data['thumb'] = f"fab/frame/classes/thumb-{class_type.lower()}.png"
            data['name'] = f"{class_type.title()} Class"
            return True

        if 'children' in data:
            for child in data['children']:
                if self.update_class_frame(child, class_type):
                    return True

        return False

    def generate_card(self, row: pd.Series) -> Dict[str, Any]:
        """
        从Excel行数据生成单张卡牌JSON

        Args:
            row: Excel行数据

        Returns:
            完整的卡牌JSON数据
        """
        # 深拷贝模板
        card_data = json.loads(json.dumps(self.template))

        # 更新文本字段
        self.update_text_field(card_data['data'], 'Title', str(row.get('card_name', '')))
        self.update_text_field(card_data['data'], 'Type', str(row.get('card_type', '')))
        self.update_text_field(card_data['data'], 'Rules', str(row.get('rules_text', '')))
        self.update_text_field(card_data['data'], 'Cost', str(row.get('cost', '')))
        self.update_text_field(card_data['data'], 'Left Stat', str(row.get('power', '')))
        self.update_text_field(card_data['data'], 'Right Stat', str(row.get('defense', '')))

        # 更新收藏信息
        artist = row.get('artist', 'Unknown Artist')
        year = row.get('year', '2024')
        collector_info = f"{artist} © {year} Legend Story Studios"
        self.update_text_field(card_data['data'], 'Collector Info', collector_info)

        # 更新图片
        art_path = row.get('art_path', '')
        if art_path:
            self.update_image_field(card_data['data'], 'Art', art_path)

        # 更新职业框架
        class_type = row.get('class_type', 'ninja')
        if class_type:
            self.update_class_frame(card_data['data'], class_type)

        return card_data

    def generate_from_excel(self, excel_path: str, output_dir: str = "output"):
        """
        从Excel文件批量生成卡牌JSON

        Args:
            excel_path: Excel文件路径（支持.xlsx, .xls, .csv）
            output_dir: 输出目录
        """
        # 读取Excel或CSV
        try:
            if excel_path.lower().endswith('.csv'):
                df = pd.read_csv(excel_path, encoding='utf-8')
            else:
                df = pd.read_excel(excel_path)
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # 生成卡牌
        success_count = 0

        for idx, row in df.iterrows():
            try:
                # 生成卡牌数据
                card_data = self.generate_card(row)

                # 生成文件名
                card_name = row.get('card_name', f'card_{idx+1}')
                # 清理文件名中的非法字符
                safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')

                # 保存JSON文件
                output_file = output_path / f"{safe_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(card_data, f, indent=4, ensure_ascii=False)

                success_count += 1
                print(f"✅ 已生成: {output_file}")

            except Exception as e:
                print(f"❌ 生成第 {idx+1} 张卡牌失败: {e}")

        print(f"\n🎉 完成！成功生成 {success_count}/{len(df)} 张卡牌")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='CardConjurer卡牌批量生成器')
    parser.add_argument('excel', help='Excel文件路径')
    parser.add_argument('-o', '--output', default='output', help='输出目录（默认: output）')
    parser.add_argument('-t', '--template', default='template.json', help='模板文件路径（默认: template.json）')

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.excel):
        print(f"❌ Excel文件不存在: {args.excel}")
        return

    if not os.path.exists(args.template):
        print(f"❌ 模板文件不存在: {args.template}")
        return

    # 生成卡牌
    generator = CardGenerator(args.template)
    generator.generate_from_excel(args.excel, args.output)


if __name__ == '__main__':
    main()
