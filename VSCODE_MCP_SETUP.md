# VSCode GitHub Copilot MCP 配置指南

## 问题分析

如果 MCP 服务器启动了但工具列表不显示,可能的原因:1. VSCode MCP 配置不正确
2. Python 环境路径问题
3. 工作目录设置问题
4. 服务器返回的工具格式问题

## 完整配置步骤

### 1. 找到 VSCode 设置文件

Windows 路径: `%APPDATA%\Code\User\settings.json`

或在 VSCode 中:
1. 打开命令面板 (Ctrl+Shift+P)
2. 输入 "Preferences: Open User Settings (JSON)"

### 2. 添加 MCP 服务器配置

在 `settings.json` 中添加:

```json
{
  "mcpServers": {
    "cardgener": {
      "command": "python",
      "args": [
        "c:\\Users\\Public\\Documents\\OtherProjects\\CardGener\\mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "c:\\Users\\Public\\Documents\\OtherProjects\\CardGener",
        "PYTHONUNBUFFERED": "1"
      },
      "cwd": "c:\\Users\\Public\\Documents\\OtherProjects\\CardGener"
    }
  }
}
```

**重要**: 使用绝对路径!

### 3. 检查 Python 路径

确保可以在命令行运行:
```bash
python c:\Users\Public\Documents\OtherProjects\CardGener\mcp_server.py
```

如果需要使用特定的 Python 版本:
```json
{
  "mcpServers": {
    "cardgener": {
      "command": "C:\\Python39\\python.exe",  // 使用完整路径
      "args": ["c:\\Users\\Public\\Documents\\OtherProjects\\CardGener\\mcp_server.py"],
      "cwd": "c:\\Users\\Public\\Documents\\OtherProjects\\CardGener"
    }
  }
}
```

### 4. 查看 MCP 服务器输出

在 VSCode 中:
1. 打开输出面板 (View > Output 或 Ctrl+Shift+U)
2. 在下拉菜单中选择 "MCP Server: cardgener"
3. 查看是否有错误信息

你应该看到:
```
2026-02-10 22:23:24,223 - cardgener-mcp - INFO - Initializing CardGener MCP Server v1.0.0
2026-02-10 22:23:24,224 - cardgener-mcp - INFO - Starting cardgener-mcp-server v1.0.0
2026-02-10 22:23:24,235 - mcp.server.lowlevel.server - INFO - Processing request of type ListToolsRequest
2026-02-10 22:23:24,236 - cardgener-mcp - INFO - Returning 12 tools to client
```

### 5. 验证工具列表

现在应该看到以下日志:
```
2026-02-10 22:23:24,236 - cardgener-mcp - INFO - Returning 12 tools to client
```

这表示服务器正在返回 12 个工具。

### 6. 重启 VSCode

1. 完全关闭 VSCode (File > Exit)
2. 重新打开 VSCode
3. 打开 GitHub Copilot Chat
4. 检查工具列表

## 可用工具列表

服务器应该提供以下 12 个工具:

1. **get_card_schema** - 获取卡片模式定义
2. **update_card_schema** - 更新卡片模式
3. **generate_card** - 生成单张卡片
4. **generate_cards_batch** - 批量生成卡片
5. **read_card** - 读取卡片信息
6. **search_cards** - 搜索卡片
7. **delete_card** - 删除卡片
8. **generate_ai_artwork** - 生成 AI 艺术作品
9. **render_cards_to_images** - 渲染卡片为图片
10. **stitch_card_images** - 拼接卡片图片
11. **full_workflow** - 完整工作流

## 故障排查

### 问题 1: 服务器无法启动

检查:
- Python 是否安装并在 PATH 中
- 所有依赖是否安装: `pip install -r requirements.txt`
- 文件路径是否正确(使用绝对路径)

### 问题 2: 服务器启动但无工具

检查:
- MCP 服务器输出中是否有 "Returning X tools to client" 日志
- 是否有 Python 错误(特别是 `NameError: name 'false' is not defined`)
- 已修复:布尔值问题 (true/false -> True/False)

### 问题 3: 权限问题

如果遇到权限错误:
```json
{
  "mcpServers": {
    "cardgener": {
      "command": "cmd",
      "args": ["/c", "python", "mcp_server.py"],
      "cwd": "c:\\Users\\Public\\Documents\\OtherProjects\\CardGener"
    }
  }
}
```

## 测试服务器

运行测试脚本:
```bash
cd c:\Users\Public\Documents\OtherProjects\CardGener
python test_list_tools.py
```

这将验证服务器配置是否正确。

## 更新日志

### 2026-02-10 修复

1. ✅ 添加了 try-except 异常处理到 `list_tools()`
2. ✅ 添加了详细日志输出
3. ✅ 修复了布尔值问题 (true/false -> True/False)
4. ✅ 确保工具列表正确返回

## 支持

如果问题仍然存在:
1. 检查 VSCode 版本是否支持 MCP
2. 检查 GitHub Copilot 扩展是否最新
3. 查看完整的服务器输出日志
4. 尝试重启 VSCode MCP 服务器: Command Palette > "MCP: Restart Server"
