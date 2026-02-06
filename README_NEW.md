# CardGener - 强大的卡牌批量生成工具

从Excel表格批量生成CardConjurer格式的JSON卡牌文件，支持自动导入、AI图片生成、图片拼接等多种功能。

## ✨ 核心功能

### 🎴 基础功能
- ✅ 从Excel/CSV批量导入卡牌数据
- ✅ 自动生成符合CardConjurer格式的JSON文件
- ✅ 支持多种职业框架（ninja, warrior, wizard等）
- ✅ 灵活的字段映射系统
- ✅ 中文支持

### 🚀 高级功能

#### 1. 批量导入到CardConjurer（自动化）
- 🌐 一键批量导入JSON到 https://cardconjurer.com/creator
- 📥 自动下载生成的卡牌图片
- ⚙️ 支持无头模式后台运行

#### 2. 图片拼接（Tabletop Simulator支持）
- 🎨 将多张卡牌图片按n×m网格拼接成大图
- 🎮 完美支持Tabletop Simulator（10×7标准布局）
- 📏 可自定义行列数和间距
- 🖼️ 自动调整图片尺寸

#### 3. AI功能（MCP集成）
- 🤖 MCP（Model Context Protocol）服务器
- 💬 通过自然语言快速生成大量卡牌
- 🔌 允许其他AI工具接入使用
- 📝 简化桌游设计开发流程

#### 4. AI图片生成
- 🎨 自动生成卡牌艺术图片
- 🆓 使用免费API（Pollinations AI）
- ⚡ 批量处理支持
- 🔄 自动更新JSON中的图片路径

#### 5. 图形界面（GUI）
- 🖥️ 友好的图形界面
- 📊 多标签页设计，功能分类清晰
- 📝 实时日志输出
- 🎯 简单易用，无需命令行

## 📦 安装

### 基础安装

```bash
# 克隆仓库
git clone https://github.com/michaelwuwar/CardGener.git
cd CardGener

# 安装依赖
pip install -r requirements.txt
```

### 可选依赖

```bash
# 如果需要使用CardConjurer自动导入功能
pip install selenium
# 还需要下载ChromeDriver: https://chromedriver.chromium.org/

# 如果需要使用AI图片生成
pip install requests Pillow
```

## 🎮 使用方法

### 方法1: 图形界面（推荐）

```bash
python gui.py
```

在GUI中选择对应的功能标签页，填写参数即可使用。

### 方法2: 命令行

#### 基础生成（Excel/CSV → JSON）

```bash
# 从Excel生成JSON
python card_generator.py sample_cards.csv -o output

# 指定模板
python card_generator.py my_cards.xlsx -t custom_template.json
```

#### CardConjurer自动导入

```bash
# 批量导入JSON并下载图片
python cardconjurer_automation.py output -o downloaded_images

# 使用无头模式
python cardconjurer_automation.py output --headless
```

#### 图片拼接

```bash
# 自动拼接（10列）
python image_stitcher.py downloaded_images -o stitched.png

# TTS模式（10×7，每页70张）
python image_stitcher.py downloaded_images -o deck.png --tts

# 自定义行列
python image_stitcher.py images -r 5 -c 7 -s 10 -o output.png
```

#### AI图片生成

```bash
# 为JSON文件批量生成AI图片
python ai_image_generator.py --json-dir output --output-dir generated_art

# 使用Stability AI（需要API密钥）
export STABILITY_API_KEY=your_api_key
python ai_image_generator.py --json-dir output --api stability
```

#### MCP服务器

```bash
# 启动MCP服务器
python mcp_server.py

# 测试模式
python mcp_server.py --test
```

## 📋 Excel/CSV表格格式

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

### 支持的职业类型

- `ninja` - 忍者
- `warrior` - 战士
- `wizard` - 法师
- `ranger` - 游侠
- `guardian` - 守护者

## 🔧 配置MCP服务器（供AI工具使用）

在Claude Desktop或其他支持MCP的AI工具中配置：

```json
{
  "mcpServers": {
    "card-generator": {
      "command": "python",
      "args": ["/path/to/CardGener/mcp_server.py"],
      "env": {}
    }
  }
}
```

## 🎯 完整工作流示例

### 场景：设计一套新卡牌并导入TTS

1. **准备数据**
   ```bash
   # 在Excel中创建卡牌数据，保存为my_cards.xlsx
   ```

2. **生成JSON**
   ```bash
   python card_generator.py my_cards.xlsx -o output
   ```

3. **生成AI图片**（可选）
   ```bash
   python ai_image_generator.py --json-dir output --output-dir art
   ```

4. **导入CardConjurer并下载**
   ```bash
   python cardconjurer_automation.py output -o images
   ```

5. **拼接为TTS格式**
   ```bash
   python image_stitcher.py images --tts
   ```

6. **完成！**
   - JSON文件在 `output/` 目录
   - 下载的图片在 `images/` 目录
   - TTS卡牌组在 `images/tts_decks/` 目录

## 🖥️ 系统要求

- Python 3.8+
- Windows / macOS / Linux

### 依赖包
- pandas - Excel数据处理
- openpyxl - Excel文件读写
- Pillow - 图片处理
- selenium - Web自动化（可选）
- requests - HTTP请求

## 📦 打包与分发

### 使用PyInstaller打包GUI

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包为单文件可执行程序
pyinstaller --name=CardGener --onefile --windowed gui.py

# 输出在dist/目录
```

### GitHub Actions自动构建

本项目已配置GitHub Actions，每次push到main分支或创建tag时自动构建：

- 支持Windows、macOS、Linux
- 自动运行测试
- 自动打包可执行文件
- Tag推送时自动创建Release

创建新版本：
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🤝 MCP工具说明

本项目实现了MCP（Model Context Protocol）服务器，提供以下工具：

### 1. `generate_card`
生成单张卡牌

**参数：**
- `card_name`: 卡牌名称
- `card_type`: 卡牌类型
- `rules_text`: 规则文本
- `cost`, `power`, `defense`: 数值
- `art_path`, `class_type`, `artist`, `year`: 其他属性

### 2. `generate_cards_batch`
批量生成卡牌

**参数：**
- `cards`: 卡牌数据数组
- `output_dir`: 输出目录

### 3. `parse_natural_language`
解析自然语言为卡牌数据

**参数：**
- `description`: 自然语言描述

**示例：**
```
"Create a ninja card called Shadow Strike that costs 2 and deals 5 damage with 3 defense"
```

## 🐛 常见问题

### Q: GUI无法启动？
A: 确保已安装tkinter（Python标准库，通常已包含）。Linux用户可能需要：
```bash
sudo apt-get install python3-tk
```

### Q: CardConjurer自动化不工作？
A:
1. 确保已安装selenium和ChromeDriver
2. ChromeDriver版本需要匹配Chrome浏览器版本
3. 网站结构可能变化，需要更新选择器

### Q: AI图片生成失败？
A:
1. 检查网络连接
2. Pollinations API免费但可能有速率限制
3. 可以尝试使用Stability AI（需要API密钥）

### Q: 图片拼接尺寸不对？
A: 在`image_stitcher.py`中调整`card_width`和`card_height`参数：
```bash
python image_stitcher.py input --card-width 1500 --card-height 2100
```

## 📄 许可证

本工具仅供学习和个人使用。生成的卡牌应标注"UNOFFICIAL CARD - NOT FOR SALE"。

## 🙏 致谢

- [CardConjurer](https://cardconjurer.com/) - 卡牌设计工具
- [Flesh and Blood TCG](https://fabtcg.com/) - 游戏框架参考
- [Pollinations AI](https://pollinations.ai/) - 免费AI图片生成
- [Tabletop Simulator](https://www.tabletopsimulator.com/) - 桌游模拟器

## 📧 联系方式

如有问题或建议，请提交Issue或Pull Request。

---

**提示**：本工具生成的卡牌仅供原型设计和测试使用，不得用于商业目的。
