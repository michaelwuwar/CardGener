# CardGener 使用指南

本指南详细介绍CardGener的各项功能和使用方法。

## 目录

1. [快速开始](#快速开始)
2. [基础功能](#基础功能)
3. [高级功能](#高级功能)
4. [MCP集成](#mcp集成)
5. [故障排除](#故障排除)

## 快速开始

### 安装

```bash
git clone https://github.com/michaelwuwar/CardGener.git
cd CardGener
pip install -r requirements.txt
```

### 最简单的使用方式

```bash
# 启动GUI
python gui.py
```

### 命令行快速使用

```bash
# 1. 从CSV生成JSON
python card_generator.py sample_cards.csv

# 2. 查看生成的文件
ls output/
```

## 基础功能

### 1. Excel/CSV转JSON

#### 准备Excel文件

在Excel中创建包含以下列的表格：

| card_name | card_type | rules_text | cost | power | defense | art_path | class_type | artist | year |
|-----------|-----------|------------|------|-------|---------|----------|------------|--------|------|
| Shadow Strike | Action - Attack | Deal 5 damage... | 2 | 5 | 3 | art/shadow.jpg | ninja | John | 2024 |

#### 生成JSON

```bash
# 基础用法
python card_generator.py my_cards.xlsx

# 指定输出目录
python card_generator.py my_cards.xlsx -o my_output

# 使用自定义模板
python card_generator.py my_cards.xlsx -t my_template.json
```

#### 输出结果

生成的JSON文件将保存在`output/`目录（或指定目录），每张卡一个JSON文件。

### 2. 使用简化版生成器

如果不想安装pandas：

```bash
python simple_generator.py sample_cards.csv
```

## 高级功能

### 1. CardConjurer自动导入

自动将生成的JSON导入到CardConjurer网站并下载图片。

#### 前提条件

```bash
pip install selenium
# 下载ChromeDriver: https://chromedriver.chromium.org/
```

#### 使用方法

```bash
# 基础用法
python cardconjurer_automation.py output

# 指定下载目录
python cardconjurer_automation.py output -o downloaded_images

# 无头模式（后台运行）
python cardconjurer_automation.py output --headless
```

#### 工作流程

1. 自动打开Chrome浏览器
2. 访问CardConjurer网站
3. 逐个加载JSON文件
4. 下载生成的卡牌图片
5. 保存到指定目录

#### 注意事项

- 需要稳定的网络连接
- CardConjurer网站可能会更新，导致自动化失效
- 建议先手动测试一两个文件

### 2. 图片拼接

将多张卡牌图片拼接成大图，适用于Tabletop Simulator等桌游模拟器。

#### 自动拼接

```bash
# 自动计算行列（最大10列）
python image_stitcher.py downloaded_images -o stitched.png

# 指定列数
python image_stitcher.py downloaded_images -o output.png -c 8
```

#### TTS模式

Tabletop Simulator推荐使用10×7布局，每页最多70张卡：

```bash
python image_stitcher.py downloaded_images --tts
```

这会在`downloaded_images/tts_decks/`目录生成多个大图，每个最多70张卡。

#### 自定义布局

```bash
# 5行7列，间距10像素
python image_stitcher.py images -r 5 -c 7 -s 10 -o deck.png

# 自定义卡牌尺寸
python image_stitcher.py images --card-width 1500 --card-height 2100 -o deck.png
```

#### 参数说明

- `-r, --rows`: 行数
- `-c, --cols`: 列数（默认10）
- `-s, --spacing`: 图片间距（默认0）
- `--tts`: TTS模式
- `--card-width`: 单张卡牌宽度
- `--card-height`: 单张卡牌高度

### 3. AI图片生成

使用免费的AI API为卡牌生成艺术图片。

#### 基础用法

```bash
# 为现有JSON生成图片
python ai_image_generator.py --json-dir output --output-dir art

# 生成单张图片
python ai_image_generator.py --prompt "ninja warrior in shadows" -o ninja.png
```

#### 使用Pollinations AI（免费）

```bash
python ai_image_generator.py --json-dir output --api pollinations
```

#### 使用Stability AI（需要API密钥）

```bash
export STABILITY_API_KEY=your_api_key_here
python ai_image_generator.py --json-dir output --api stability
```

#### 工作原理

1. 读取JSON文件中的卡牌数据
2. 根据卡牌名称、类型、规则文本生成提示词
3. 调用AI API生成图片
4. 保存图片并更新JSON中的art_path

#### 提示词生成规则

- 根据职业类型添加风格（ninja → 忍者风格）
- 从规则文本提取关键词（damage → 动作场景）
- 自动添加"fantasy card game art"等修饰词

### 4. MCP服务器

允许AI工具（如Claude Desktop）通过自然语言生成卡牌。

#### 配置Claude Desktop

编辑配置文件：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

添加：

```json
{
  "mcpServers": {
    "card-generator": {
      "command": "python",
      "args": ["/absolute/path/to/CardGener/mcp_server.py"],
      "env": {}
    }
  }
}
```

#### 重启Claude Desktop

配置后重启Claude Desktop，即可使用MCP工具。

#### 使用示例

在Claude Desktop中：

```
请使用card-generator工具创建一张忍者卡牌：
- 名称：暗影突袭
- 类型：Action - Attack
- 规则：造成5点伤害，如果命中则抽一张卡
- 费用：2，攻击力：5，防御力：3
```

Claude会自动调用MCP工具生成卡牌JSON。

#### 测试MCP服务器

```bash
python mcp_server.py --test
```

### 5. GUI界面

图形界面集成了所有功能，无需命令行。

#### 启动GUI

```bash
python gui.py
```

#### 功能标签页

1. **基础生成**：Excel/CSV → JSON
2. **CardConjurer导入**：自动导入和下载
3. **图片拼接**：拼接为大图
4. **AI图片生成**：AI生成卡牌艺术

每个标签页都有：
- 文件/目录选择
- 参数配置
- 执行按钮
- 实时日志输出

## 完整工作流示例

### 场景：从零开始创建一套卡牌

#### 步骤1：准备数据

在Excel中创建`my_cards.xlsx`：

```
card_name, card_type, rules_text, cost, power, defense, art_path, class_type, artist, year
Blade Dance, Action - Attack, "Deal 4 damage. Go again.", 1, 4, 2, , ninja, AI, 2024
Iron Wall, Defense Reaction, "Prevent the next 5 damage.", 2, 0, 5, , warrior, AI, 2024
```

#### 步骤2：生成JSON

```bash
python card_generator.py my_cards.xlsx -o my_deck
```

#### 步骤3：生成AI图片

```bash
python ai_image_generator.py --json-dir my_deck --output-dir my_deck_art
```

#### 步骤4：导入CardConjurer并下载

```bash
python cardconjurer_automation.py my_deck -o my_deck_images
```

#### 步骤5：拼接为TTS格式

```bash
python image_stitcher.py my_deck_images --tts
```

#### 步骤6：导入TTS

将`my_deck_images/tts_decks/`中的图片导入Tabletop Simulator。

## MCP集成

### 可用工具

#### 1. generate_card

生成单张卡牌。

**输入：**
```json
{
  "card_name": "Shadow Strike",
  "card_type": "Action - Attack",
  "rules_text": "Deal 5 damage...",
  "cost": "2",
  "power": "5",
  "defense": "3",
  "class_type": "ninja"
}
```

#### 2. generate_cards_batch

批量生成卡牌。

**输入：**
```json
{
  "cards": [
    {"card_name": "Card 1", ...},
    {"card_name": "Card 2", ...}
  ],
  "output_dir": "output"
}
```

#### 3. parse_natural_language

从自然语言生成卡牌数据。

**输入：**
```json
{
  "description": "Create a ninja card called Shadow Strike that costs 2..."
}
```

### 在Python中使用MCP服务器

```python
from mcp_server import CardGeneratorMCPServer

server = CardGeneratorMCPServer('template.json')

# 解析自然语言
result = server.handle_tool_call('parse_natural_language', {
    'description': 'Create a warrior card with 5 defense'
})

print(result['card_data'])
```

## 故障排除

### 问题1：GUI无法启动

**症状：** 运行`python gui.py`报错

**解决方案：**
```bash
# Linux
sudo apt-get install python3-tk

# macOS (应该已预装)
brew install python-tk

# Windows (应该已预装)
# 如果缺失，重新安装Python并勾选tcl/tk
```

### 问题2：CardConjurer自动化不工作

**症状：** Selenium报错或无法找到元素

**解决方案：**
1. 检查ChromeDriver版本是否匹配Chrome浏览器
2. 更新selenium：`pip install --upgrade selenium`
3. CardConjurer网站可能更新了结构，需要修改代码中的选择器

### 问题3：AI图片生成失败

**症状：** 请求超时或API错误

**解决方案：**
1. 检查网络连接
2. Pollinations可能有速率限制，等待后重试
3. 尝试使用Stability AI（需要API密钥）

### 问题4：图片拼接尺寸不对

**症状：** 拼接后的图片卡牌尺寸不匹配

**解决方案：**
```bash
# 指定标准卡牌尺寸
python image_stitcher.py images --card-width 1500 --card-height 2100 -o output.png
```

### 问题5：Excel读取中文乱码

**症状：** 生成的JSON中中文显示为乱码

**解决方案：**
1. 确保Excel另存为时选择"CSV UTF-8"格式
2. 或使用`.xlsx`格式而非`.csv`

### 问题6：MCP服务器无响应

**症状：** Claude Desktop无法连接MCP服务器

**解决方案：**
1. 检查配置文件路径是否为绝对路径
2. 确保Python在PATH中
3. 查看Claude Desktop日志（帮助 → 查看日志）
4. 测试服务器：`python mcp_server.py --test`

## 高级配置

### 自定义模板

编辑`template.json`修改卡牌布局：

```json
{
  "width": 1500,
  "height": 2100,
  "data": {
    "children": [
      {
        "type": "text",
        "name": "Title",
        "x": 285,
        "y": 144,
        ...
      }
    ]
  }
}
```

### 环境变量

```bash
# Stability AI API密钥
export STABILITY_API_KEY=your_key

# 自定义模板路径
export CARD_TEMPLATE=/path/to/template.json
```

### 批处理脚本

创建`batch_process.sh`：

```bash
#!/bin/bash
python card_generator.py input.xlsx -o output
python ai_image_generator.py --json-dir output --output-dir art
python cardconjurer_automation.py output -o images
python image_stitcher.py images --tts
echo "完成！"
```

## 性能优化

### 批量处理大量卡牌

```python
# 分批处理，避免内存占用过高
import pandas as pd
from card_generator import CardGenerator

generator = CardGenerator()
df = pd.read_excel('large_file.xlsx')

batch_size = 100
for i in range(0, len(df), batch_size):
    batch = df[i:i+batch_size]
    # 处理批次
```

### 并行生成AI图片

由于API速率限制，建议串行生成，但可以调整延迟：

```bash
# 修改ai_image_generator.py中的delay参数
# 默认2秒，可以根据API限制调整
```

## 贡献指南

欢迎贡献！请：

1. Fork仓库
2. 创建功能分支
3. 提交Pull Request

## 更新日志

### v1.0.0
- ✅ 基础JSON生成
- ✅ CardConjurer自动导入
- ✅ 图片拼接（TTS支持）
- ✅ AI图片生成
- ✅ MCP服务器
- ✅ GUI界面
- ✅ GitHub Actions自动打包

## 许可证

MIT License - 仅供学习和个人使用

---

**需要帮助？** 请在GitHub上提交Issue：
https://github.com/michaelwuwar/CardGener/issues
