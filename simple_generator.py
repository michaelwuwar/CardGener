#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版卡牌生成器（不需要pandas）
直接从CSV文件生成JSON卡牌
"""

import json
import csv
from pathlib import Path


def load_template(template_path="template.json"):
    """加载JSON模板"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_field(data, field_type, field_name, value):
    """递归更新字段"""
    if data.get('type') == field_type and data.get('name') == field_name:
        if field_type == 'text':
            data['text'] = value
        elif field_type == 'image':
            data['src'] = value
        return True

    if 'children' in data:
        for child in data['children']:
            if update_field(child, field_type, field_name, value):
                return True
    return False


def update_class_frame(data, class_type):
    """更新职业框架"""
    if data.get('type') == 'image' and 'Class' in data.get('name', ''):
        data['src'] = f"fab/frame/classes/{class_type.lower()}.png"
        data['thumb'] = f"fab/frame/classes/thumb-{class_type.lower()}.png"
        data['name'] = f"{class_type.title()} Class"
        return True

    if 'children' in data:
        for child in data['children']:
            if update_class_frame(child, class_type):
                return True
    return False


def generate_card(template, row):
    """从CSV行生成卡牌"""
    # 深拷贝模板
    card = json.loads(json.dumps(template))

    # 更新文本字段
    update_field(card['data'], 'text', 'Title', row.get('card_name', ''))
    update_field(card['data'], 'text', 'Type', row.get('card_type', ''))
    update_field(card['data'], 'text', 'Rules', row.get('rules_text', ''))
    update_field(card['data'], 'text', 'Cost', row.get('cost', ''))
    update_field(card['data'], 'text', 'Left Stat', row.get('power', ''))
    update_field(card['data'], 'text', 'Right Stat', row.get('defense', ''))

    # 更新收藏信息
    artist = row.get('artist', 'Unknown Artist')
    year = row.get('year', '2024')
    collector_info = f"{artist} © {year} Legend Story Studios"
    update_field(card['data'], 'text', 'Collector Info', collector_info)

    # 更新图片
    art_path = row.get('art_path', '')
    if art_path:
        update_field(card['data'], 'image', 'Art', art_path)

    # 更新职业框架
    class_type = row.get('class_type', 'ninja')
    if class_type:
        update_class_frame(card['data'], class_type)

    return card


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python simple_generator.py <CSV文件> [输出目录]")
        print("示例: python simple_generator.py sample_cards.csv output")
        return

    csv_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"

    # 检查文件
    if not Path(csv_file).exists():
        print(f"[ERROR] CSV文件不存在: {csv_file}")
        return

    if not Path("template.json").exists():
        print("[ERROR] 模板文件template.json不存在")
        return

    # 加载模板
    template = load_template()

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 读取CSV并生成卡牌
    success_count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader):
            try:
                # 生成卡牌
                card = generate_card(template, row)

                # 生成文件名
                card_name = row.get('card_name', f'card_{idx+1}')
                safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')

                # 保存文件
                output_file = output_path / f"{safe_name}.json"
                with open(output_file, 'w', encoding='utf-8') as out:
                    json.dump(card, out, indent=4, ensure_ascii=False)

                success_count += 1
                print(f"[OK] 已生成: {output_file}")

            except Exception as e:
                print(f"[ERROR] 生成第 {idx+1} 张卡牌失败: {e}")

    print(f"\n完成！成功生成 {success_count} 张卡牌")


if __name__ == '__main__':
    main()
