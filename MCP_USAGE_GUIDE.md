# CardGener MCP Server 使用指南

## 概述

CardGener MCP (Model Context Protocol) Server 为AI模型提供了与CardGener卡牌生成器的集成接口。所有操作参数都由AI生成并传入，实现完全自动化的卡牌生成流程。

## 主要特性

✅ **AI参数生成** - 所有卡牌参数由AI自动生成
✅ **三大工具** - 单卡生成、批量生成、自然语言解析
✅ **MCP标准** - 完全符合Model Context Protocol规范
✅ **灵活集成** - 可与Claude Desktop等AI客户端无缝集成

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

这会安装以下依赖：
- `pandas` - 数据处理
- `openpyxl` - Excel文件支持
- `mcp` - Model Context Protocol SDK

### 2. 验证安装

```bash
python mcp_server.py
```

应该看到：
```
🚀 Starting CardGener MCP Server...
📝 All operation parameters are AI-generated
```

## MCP工具说明

### 1. generate_card - 生成单张卡牌

**功能**：根据AI提供的完整参数生成单张CardConjurer格式的JSON卡牌。

**必需参数（由AI生成）**：
- `card_name` - 卡牌名称
- `card_type` - 卡牌类型（如"Action - Attack"）
- `rules_text` - 规则文本
- `cost` - 费用值
- `power` - 攻击力（左侧数值）
- `defense` - 防御力（右侧数值）
- `class_type` - 职业类型（ninja, warrior, wizard等）

**可选参数（由AI生成）**：
- `art_path` - 卡图路径或URL
- `artist` - 艺术家名称（默认："Unknown Artist"）
- `year` - 版权年份（默认："2024"）
- `output_path` - 输出目录（默认："output"）
- `template_path` - 自定义模板路径

**示例调用**：

```json
{
  "tool": "generate_card",
  "parameters": {
    "card_name": "Shadow Strike",
    "card_type": "Action - Attack",
    "rules_text": "Deal 5 damage to target hero. Go again.",
    "cost": "2",
    "power": "5",
    "defense": "3",
    "art_path": "images/shadow_strike.jpg",
    "class_type": "ninja",
    "artist": "John Doe",
    "year": "2024",
    "output_path": "output"
  }
}
```

**返回结果**：

```json
{
  "status": "success",
  "message": "✅ Card 'Shadow Strike' generated successfully",
  "file_path": "output/Shadow_Strike.json",
  "card_data": { ... }
}
```

### 2. generate_cards_batch - 批量生成卡牌

**功能**：从AI提供的卡牌定义列表批量生成多张卡牌。

**必需参数（由AI生成）**：
- `cards` - 卡牌参数对象数组，每个对象包含完整的卡牌参数

**可选参数（由AI生成）**：
- `output_path` - 所有卡牌的输出目录
- `template_path` - 自定义模板路径

**示例调用**：

```json
{
  "tool": "generate_cards_batch",
  "parameters": {
    "cards": [
      {
        "card_name": "Ninja Strike",
        "card_type": "Action - Attack",
        "rules_text": "Deal 5 damage.",
        "cost": "2",
        "power": "5",
        "defense": "3",
        "art_path": "",
        "class_type": "ninja",
        "artist": "Artist A",
        "year": "2024"
      },
      {
        "card_name": "Warrior's Shield",
        "card_type": "Action - Defense",
        "rules_text": "Prevent 4 damage.",
        "cost": "1",
        "power": "0",
        "defense": "4",
        "art_path": "",
        "class_type": "warrior",
        "artist": "Artist B",
        "year": "2024"
      }
    ],
    "output_path": "output/batch_test"
  }
}
```

**返回结果**：

```json
{
  "status": "completed",
  "total_cards": 2,
  "successful": 2,
  "failed": 0,
  "message": "🎉 Generated 2/2 cards successfully",
  "results": [
    {
      "index": 0,
      "card_name": "Ninja Strike",
      "status": "success",
      "file_path": "output/batch_test/Ninja_Strike.json"
    },
    {
      "index": 1,
      "card_name": "Warrior's Shield",
      "status": "success",
      "file_path": "output/batch_test/Warriors_Shield.json"
    }
  ]
}
```

### 3. parse_natural_language - 自然语言解析

**功能**：解析自然语言描述，提取结构化的卡牌参数。AI可以使用此工具将文本描述转换为结构化参数，然后调用`generate_card`。

**必需参数（由AI生成）**：
- `description` - 自然语言卡牌描述

**可选参数（由AI生成）**：
- `context` - 额外的上下文提示（游戏类型、卡组、稀有度等）

**示例调用**：

```json
{
  "tool": "parse_natural_language",
  "parameters": {
    "description": "Create a ninja attack card called Shadow Strike that costs 2 resources, deals 5 damage with 3 defense",
    "context": {
      "game_type": "Flesh and Blood",
      "card_set": "Custom Set",
      "rarity": "Common"
    }
  }
}
```

**AI工作流程**：
1. 调用`parse_natural_language`理解描述
2. AI从返回的建议中提取参数
3. AI调用`generate_card`生成实际卡牌

## 与Claude Desktop集成

### 配置步骤

1. **找到Claude Desktop配置文件**：
   - Linux/Mac: `~/.config/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **添加CardGener MCP服务器配置**：

```json
{
  "mcpServers": {
    "cardgener": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/absolute/path/to/CardGener"
    }
  }
}
```

**重要**：将`/absolute/path/to/CardGener`替换为您的CardGener目录的绝对路径。

3. **重启Claude Desktop**

4. **验证集成**：
   在Claude Desktop中询问："Can you generate a card using the cardgener tools?"

### 使用示例

与Claude Desktop对话示例：

**用户**：
> "Please generate a ninja card called 'Phantom Slash' that costs 3 resources, deals 7 damage with 2 defense. The rules text should be: 'If this hits, draw a card. Go again.'"

**Claude**（使用MCP工具）：
```
我将使用generate_card工具生成这张卡牌...

[调用 generate_card 工具]
{
  "card_name": "Phantom Slash",
  "card_type": "Action - Attack",
  "rules_text": "If this hits, draw a card. Go again.",
  "cost": "3",
  "power": "7",
  "defense": "2",
  "class_type": "ninja",
  "output_path": "output"
}

✅ 卡牌已成功生成！
文件保存在：output/Phantom_Slash.json
```

## 支持的职业类型

MCP服务器支持以下职业（class_type）：

- `ninja` - 忍者
- `warrior` - 战士
- `wizard` - 法师
- `ranger` - 游侠
- `guardian` - 守护者
- `brute` - 野蛮人
- `mechanologist` - 机械师
- `runeblade` - 符文剑士
- `merchant` - 商人
- `illusionist` - 幻术师

## 工作流程示例

### 场景1：生成单张自定义卡牌

```python
# AI自动执行以下流程：

1. 理解用户需求
2. 生成所有必需参数：
   - card_name: "Lightning Bolt"
   - card_type: "Action - Attack"
   - rules_text: "Deal 4 damage. If you control a wizard, deal 6 instead."
   - cost: "2"
   - power: "4"
   - defense: "3"
   - class_type: "wizard"
3. 调用generate_card工具
4. 返回生成结果
```

### 场景2：批量生成卡牌套牌

```python
# AI自动执行以下流程：

1. 理解用户想要生成一套完整卡组
2. 设计多张卡牌，为每张生成完整参数
3. 将所有卡牌参数组织成数组
4. 调用generate_cards_batch工具
5. 报告生成统计
```

### 场景3：从文本描述生成

```python
# AI工作流程：

1. 用户提供自然语言描述
2. AI解析描述，提取所有卡牌属性
3. AI将提取的信息转换为结构化参数
4. 调用generate_card生成卡牌
5. 返回结果
```

## 文件输出

所有生成的JSON文件：
- 默认保存在`output/`目录
- 文件名基于卡牌名称（特殊字符被清理）
- 格式：`{Card_Name}.json`
- 编码：UTF-8
- 缩进：4空格

## 错误处理

MCP服务器会返回友好的错误信息：

```json
{
  "status": "error",
  "message": "❌ Failed to generate card: Missing required field 'card_name'"
}
```

常见错误：
- 缺少必需参数
- 模板文件不存在
- 无效的职业类型
- 文件系统权限问题

## 技术架构

```
AI Client (Claude Desktop)
    ↓ MCP Protocol
CardGener MCP Server
    ↓ Parameters (AI-generated)
Card Generator Logic
    ↓ JSON Output
CardConjurer Files
```

## 性能考虑

- 单卡生成：< 100ms
- 批量生成：约10-50ms/卡（取决于模板大小）
- 文件I/O：异步处理，不阻塞AI响应

## 高级用法

### 自定义模板

AI可以指定自定义模板：

```json
{
  "card_name": "Custom Card",
  "template_path": "custom_templates/alternative.json",
  ...
}
```

### 输出目录组织

AI可以为不同批次创建不同目录：

```json
{
  "output_path": "output/ninja_deck",
  ...
}
```

## 开发和测试

### 手动测试MCP服务器

虽然服务器设计为通过MCP协议使用，但可以进行基本测试：

```bash
# 启动服务器（会等待MCP输入）
python mcp_server.py
```

### 集成测试

使用MCP客户端或Claude Desktop进行完整集成测试。

## 故障排查

### 问题：服务器无法启动

**解决方案**：
```bash
# 检查MCP SDK是否安装
pip list | grep mcp

# 重新安装
pip install --upgrade mcp
```

### 问题：工具在Claude Desktop中不可见

**解决方案**：
1. 检查配置文件路径是否正确
2. 确认`cwd`是绝对路径
3. 重启Claude Desktop
4. 查看Claude Desktop日志

### 问题：生成的卡牌缺少字段

**解决方案**：
- 确保template.json存在且完整
- 验证所有必需参数都已提供
- 检查字段名称拼写

## 未来增强

计划中的功能：
- [ ] 图片生成集成（AI生成卡图）
- [ ] 卡牌平衡性检查
- [ ] 批量导出为PDF
- [ ] Web UI预览
- [ ] 更多游戏系统支持

## 许可证

本MCP服务器遵循与CardGener主项目相同的许可证。生成的卡牌仅供个人学习和原型设计使用。

## 联系和支持

如有问题或建议，请在GitHub仓库提交Issue。

---

**版本**: 1.0.0
**更新日期**: 2024
**MCP协议版本**: 0.9.0+
