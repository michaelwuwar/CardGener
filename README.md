# CardConjurer 卡牌批量生成器

从Excel表格批量生成CardConjurer格式的JSON卡牌文件，专为Flesh and Blood TCG设计。

## 功能特点

- ✅ 从Excel批量导入卡牌数据
- ✅ 自动生成符合CardConjurer格式的JSON文件
- ✅ 支持多种职业框架（ninja, warrior, wizard等）
- ✅ 灵活的字段映射系统
- ✅ 中文支持

## 目录结构

```
CardGener/
├── card_generator.py          # 主程序
├── template.json              # JSON模板文件
├── requirements.txt           # Python依赖
├── create_sample_excel.py     # 创建示例Excel脚本
├── sample_cards.xlsx          # 示例Excel文件（运行脚本后生成）
└── README.md                  # 本文件
```

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 创建示例Excel文件（可选）

```bash
python create_sample_excel.py
```

## Excel表格格式

Excel文件需要包含以下列（必需）：

| 列名 | 说明 | 示例 |
|------|------|------|
| **card_name** | 卡牌名称 | "Shadow Strike" |
| **card_type** | 卡牌类型 | "Action - Attack" |
| **rules_text** | 规则文本 | "Deal 5 damage..." |
| **cost** | 费用值 | "2" |
| **power** | 攻击力（左侧数值） | "5" |
| **defense** | 防御力（右侧数值） | "3" |
| **art_path** | 卡图路径 | "images/card.jpg" |
| **class_type** | 职业类型 | "ninja" |
| **artist** | 艺术家名称 | "John Doe" |
| **year** | 年份 | "2024" |

### 支持的职业类型

- `ninja` - 忍者
- `warrior` - 战士
- `wizard` - 法师
- `ranger` - 游侠
- `guardian` - 守护者
- 等（根据CardConjurer支持的职业）

## 使用方法

### 基础用法

```bash
python card_generator.py sample_cards.xlsx
```

这将读取`sample_cards.xlsx`并在`output/`目录生成JSON文件。

### 指定输出目录

```bash
python card_generator.py sample_cards.xlsx -o my_cards
```

### 使用自定义模板

```bash
python card_generator.py sample_cards.xlsx -t my_template.json
```

### 完整参数

```bash
python card_generator.py <Excel文件> [-o 输出目录] [-t 模板文件]
```

## 使用示例

### 1. 准备Excel文件

创建`my_cards.xlsx`，包含你的卡牌数据：

| card_name | card_type | rules_text | cost | power | defense | art_path | class_type | artist | year |
|-----------|-----------|------------|------|-------|---------|----------|------------|--------|------|
| Ninja Strike | Action - Attack | Deal 5 damage... | 2 | 5 | 3 | images/ninja.jpg | ninja | John | 2024 |

### 2. 运行生成器

```bash
python card_generator.py my_cards.xlsx
```

### 3. 查看输出

生成的JSON文件位于`output/`目录：
```
output/
├── Ninja_Strike.json
├── Warriors_Shield.json
└── ...
```

### 4. 导入CardConjurer

将生成的JSON文件导入到CardConjurer网站使用。

## 自定义模板

如果需要修改卡牌布局或样式，可以编辑`template.json`文件。

主要可修改项：
- 卡牌尺寸 (`width`, `height`)
- 文本字段位置和样式
- 图片位置和尺寸
- 字体和颜色

## 注意事项

1. **图片路径**：`art_path`需要是CardConjurer可访问的路径（URL或相对路径）
2. **职业框架**：确保`class_type`对应的框架图片存在于CardConjurer模板中
3. **文件名**：生成的JSON文件名基于卡牌名称，特殊字符会被清理
4. **Excel格式**：支持`.xlsx`格式（推荐）和`.xls`格式

## 常见问题

### Q: 生成的JSON文件无法在CardConjurer中打开？

A: 检查模板路径是否正确，确保`template.json`中的依赖路径有效。

### Q: 如何批量处理大量卡牌？

A: 直接在Excel中添加更多行，程序会自动处理所有行。

### Q: 可以自定义更多字段吗？

A: 可以！修改`card_generator.py`中的`generate_card`方法，添加你需要的字段映射。

### Q: 支持其他卡牌游戏吗？

A: 理论上支持，只需替换`template.json`为目标游戏的模板即可。

## 技术栈

- **Python 3.8+**
- **pandas** - Excel数据处理
- **openpyxl** - Excel文件读写

## 许可证

本工具仅供学习和个人使用。生成的卡牌应标注"UNOFFICIAL CARD - NOT FOR SALE"。

## 联系方式

如有问题或建议，请提交Issue。

---

**提示**：本工具生成的卡牌仅供原型设计和测试使用，不得用于商业目的。
