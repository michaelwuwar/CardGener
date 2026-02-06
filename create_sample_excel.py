#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例Excel文件
"""

import pandas as pd

# 示例卡牌数据
sample_data = [
    {
        'card_name': 'Shadow Strike',
        'card_type': 'Action - Attack',
        'rules_text': 'Deal 5 damage to target hero. If this attack hits, draw a card.',
        'cost': '2',
        'power': '5',
        'defense': '3',
        'art_path': 'images/shadow_strike.jpg',
        'class_type': 'ninja',
        'artist': 'John Doe',
        'year': '2024'
    },
    {
        'card_name': 'Warrior\'s Shield',
        'card_type': 'Defense Reaction',
        'rules_text': 'Prevent the next 4 damage that would be dealt to your hero this turn.',
        'cost': '1',
        'power': '0',
        'defense': '4',
        'art_path': 'images/warrior_shield.jpg',
        'class_type': 'warrior',
        'artist': 'Jane Smith',
        'year': '2024'
    },
    {
        'card_name': 'Frostbite',
        'card_type': 'Action - Attack',
        'rules_text': 'If this attack hits, freeze target hero (their next action costs 1 more).',
        'cost': '3',
        'power': '6',
        'defense': '2',
        'art_path': 'images/frostbite.jpg',
        'class_type': 'wizard',
        'artist': 'Alex Chen',
        'year': '2024'
    }
]

# 创建DataFrame
df = pd.DataFrame(sample_data)

# 保存为Excel文件
df.to_excel('sample_cards.xlsx', index=False, engine='openpyxl')

print("✅ 示例Excel文件已创建: sample_cards.xlsx")
