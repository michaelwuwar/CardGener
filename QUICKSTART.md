# 快速入门指南

## 最简单的使用方式（推荐）

如果你在安装pandas时遇到问题，使用简化版本即可：

### 1. 准备CSV文件

打开`sample_cards.csv`作为参考，或在Excel中创建新文件，包含以下列：

```
card_name, card_type, rules_text, cost, power, defense, art_path, class_type, artist, year
```

### 2. 运行生成器

```bash
python simple_generator.py sample_cards.csv
```

生成的JSON文件将保存在`output/`目录。

### 3. 自定义输出目录

```bash
python simple_generator.py my_cards.csv my_output
```

## 使用完整版本（需要pandas）

### 1. 安装依赖

```bash
pip install pandas openpyxl
```

### 2. 运行生成器

```bash
python card_generator.py sample_cards.csv
```

或使用Excel文件：

```bash
python card_generator.py my_cards.xlsx
```

## Excel/CSV 表格格式

| 列名 | 必需 | 说明 | 示例 |
|------|------|------|------|
| card_name | 是 | 卡牌名称 | "Shadow Strike" |
| card_type | 是 | 卡牌类型 | "Action - Attack" |
| rules_text | 是 | 规则文本 | "Deal 5 damage..." |
| cost | 是 | 费用 | "2" |
| power | 是 | 攻击力 | "5" |
| defense | 是 | 防御力 | "3" |
| art_path | 是 | 卡图路径 | "images/card.jpg" |
| class_type | 是 | 职业类型 | "ninja" |
| artist | 是 | 艺术家 | "John Doe" |
| year | 是 | 年份 | "2024" |

## 支持的职业类型

- `ninja` - 忍者
- `warrior` - 战士
- `wizard` - 法师
- `ranger` - 游侠
- `guardian` - 守护者

## 常见问题

### Q: 如何创建CSV文件？

A:
1. 打开Excel
2. 输入表头和数据
3. 文件 > 另存为 > 选择"CSV UTF-8(逗号分隔)(*.csv)"

### Q: 生成的JSON在哪里？

A: 默认在`output/`目录，可通过参数自定义。

### Q: 程序报错怎么办？

A:
1. 用`simple_generator.py`（不需要pandas）
2. 确保CSV文件编码为UTF-8
3. 检查`template.json`是否存在

### Q: 如何批量生成大量卡牌？

A: 直接在Excel/CSV中添加更多行，程序会自动处理所有行。

## 示例工作流

1. 复制`sample_cards.csv`为`my_cards.csv`
2. 在Excel中编辑`my_cards.csv`，添加你的卡牌数据
3. 保存为CSV UTF-8格式
4. 运行：`python simple_generator.py my_cards.csv`
5. 在`output/`目录查看生成的JSON文件
6. 将JSON文件导入CardConjurer网站

## 文件说明

- `simple_generator.py` - 简化版生成器（**推荐**，无需pandas）
- `card_generator.py` - 完整版生成器（需要pandas）
- `template.json` - JSON模板文件（不要修改，除非你知道在做什么）
- `sample_cards.csv` - 示例CSV文件（可作为模板）

---

**提示**：优先使用`simple_generator.py`，它不需要安装额外依赖，更简单快捷！
