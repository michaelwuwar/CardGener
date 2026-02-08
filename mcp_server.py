#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器 - 卡牌生成器
允许AI工具通过自然语言快速生成大量卡牌
符合Model Context Protocol (MCP)标准
"""

import json
import os
from typing import Dict, Any, List, Optional
import sys

# 导入卡牌生成器
from card_generator import CardGenerator


class CardGeneratorMCPServer:
    """MCP服务器实现"""

    def __init__(self, template_path: str = "template.json"):
        """初始化MCP服务器"""
        self.generator = CardGenerator(template_path)
        self.version = "1.0.0"
        self.capabilities = {
            "tools": [
                {
                    "name": "generate_card",
                    "description": "Generate a single card from parameters",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "card_name": {"type": "string", "description": "Card name"},
                            "card_type": {"type": "string", "description": "Card type (e.g., Action - Attack)"},
                            "rules_text": {"type": "string", "description": "Rules text"},
                            "cost": {"type": "string", "description": "Cost value"},
                            "power": {"type": "string", "description": "Power value"},
                            "defense": {"type": "string", "description": "Defense value"},
                            "art_path": {"type": "string", "description": "Art path or URL"},
                            "class_type": {"type": "string", "description": "Class type (ninja, warrior, etc.)"},
                            "artist": {"type": "string", "description": "Artist name"},
                            "year": {"type": "string", "description": "Year"}
                        },
                        "required": ["card_name", "card_type", "rules_text"]
                    }
                },
                {
                    "name": "generate_cards_batch",
                    "description": "Generate multiple cards from a list of card data",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "cards": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "card_name": {"type": "string"},
                                        "card_type": {"type": "string"},
                                        "rules_text": {"type": "string"},
                                        "cost": {"type": "string"},
                                        "power": {"type": "string"},
                                        "defense": {"type": "string"},
                                        "art_path": {"type": "string"},
                                        "class_type": {"type": "string"},
                                        "artist": {"type": "string"},
                                        "year": {"type": "string"}
                                    }
                                }
                            },
                            "output_dir": {"type": "string", "description": "Output directory path"}
                        },
                        "required": ["cards"]
                    }
                },
                {
                    "name": "parse_natural_language",
                    "description": "Parse natural language description into card data",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "Natural language card description"}
                        },
                        "required": ["description"]
                    }
                }
            ]
        }

    def parse_natural_language_to_card(self, description: str) -> Dict[str, Any]:
        """
        解析自然语言描述为卡牌数据
        这是一个简化版本，实际应用中可以集成更强大的NLP

        Args:
            description: 自然语言描述

        Returns:
            卡牌数据字典
        """
        # 简单的关键词提取（实际应用中可以使用NLP库）
        card_data = {
            "card_name": "",
            "card_type": "Action - Attack",
            "rules_text": "",
            "cost": "1",
            "power": "3",
            "defense": "2",
            "art_path": "",
            "class_type": "ninja",
            "artist": "AI Generated",
            "year": "2024"
        }

        # 提取卡牌名称（假设第一行或引号中的内容是名称）
        lines = description.split('\n')
        if lines:
            first_line = lines[0].strip()
            if first_line:
                # 移除常见的前缀
                for prefix in ["卡牌名称:", "Card name:", "Name:"]:
                    if first_line.startswith(prefix):
                        first_line = first_line[len(prefix):].strip()
                card_data["card_name"] = first_line

        # 提取其他信息
        description_lower = description.lower()

        # 识别类型
        if "attack" in description_lower:
            card_data["card_type"] = "Action - Attack"
        elif "defense" in description_lower:
            card_data["card_type"] = "Defense Reaction"
        elif "instant" in description_lower:
            card_data["card_type"] = "Instant"

        # 识别职业
        for class_name in ["ninja", "warrior", "wizard", "ranger", "guardian"]:
            if class_name in description_lower:
                card_data["class_type"] = class_name
                break

        # 提取数值
        import re
        cost_match = re.search(r'cost[:\s]+(\d+)', description_lower)
        if cost_match:
            card_data["cost"] = cost_match.group(1)

        power_match = re.search(r'(?:power|attack)[:\s]+(\d+)', description_lower)
        if power_match:
            card_data["power"] = power_match.group(1)

        defense_match = re.search(r'defense[:\s]+(\d+)', description_lower)
        if defense_match:
            card_data["defense"] = defense_match.group(1)

        # 使用描述作为规则文本
        card_data["rules_text"] = description

        return card_data

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理工具调用

        Args:
            tool_name: 工具名称
            arguments: 参数字典

        Returns:
            结果字典
        """
        try:
            if tool_name == "generate_card":
                # 生成单张卡牌
                import pandas as pd
                row = pd.Series(arguments)
                card_data = self.generator.generate_card(row)

                # 保存到文件
                output_dir = arguments.get("output_dir", "output")
                os.makedirs(output_dir, exist_ok=True)

                card_name = arguments.get("card_name", "card")
                safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')

                output_file = os.path.join(output_dir, f"{safe_name}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(card_data, f, indent=4, ensure_ascii=False)

                return {
                    "success": True,
                    "message": f"Card generated: {output_file}",
                    "output_file": output_file
                }

            elif tool_name == "generate_cards_batch":
                # 批量生成卡牌
                cards = arguments.get("cards", [])
                output_dir = arguments.get("output_dir", "output")
                os.makedirs(output_dir, exist_ok=True)

                output_files = []
                for card in cards:
                    import pandas as pd
                    row = pd.Series(card)
                    card_data = self.generator.generate_card(row)

                    card_name = card.get("card_name", "card")
                    safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_name = safe_name.replace(' ', '_')

                    output_file = os.path.join(output_dir, f"{safe_name}.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(card_data, f, indent=4, ensure_ascii=False)

                    output_files.append(output_file)

                return {
                    "success": True,
                    "message": f"Generated {len(output_files)} cards",
                    "output_files": output_files
                }

            elif tool_name == "parse_natural_language":
                # 解析自然语言
                description = arguments.get("description", "")
                card_data = self.parse_natural_language_to_card(description)

                return {
                    "success": True,
                    "message": "Parsed natural language to card data",
                    "card_data": card_data
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理MCP请求

        Args:
            request: MCP请求字典

        Returns:
            MCP响应字典
        """
        method = request.get("method")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "card-generator-mcp",
                        "version": self.version
                    },
                    "capabilities": self.capabilities
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": self.capabilities["tools"]
                }
            }

        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            result = self.handle_tool_call(tool_name, arguments)

            # 返回两种表示：
            # 1) 结构化的 tool_result（便于 GitHub Copilot / 其它客户端直接解析）
            # 2) 原始文本字符串（向后兼容现有实现）
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool": tool_name,
                            "data": result
                        },
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False)
                        }
                    ]
                }
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    def run_stdio(self):
        """运行STDIO模式的MCP服务器"""
        print("CardGenerator MCP Server starting in STDIO mode...", file=sys.stderr)

        while True:
            try:
                # 读取请求
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)

                # 处理请求
                response = self.handle_mcp_request(request)

                # 发送响应
                print(json.dumps(response))
                sys.stdout.flush()

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='CardGenerator MCP Server')
    parser.add_argument('-t', '--template', default='template.json', help='模板文件路径')
    parser.add_argument('--test', action='store_true', help='运行测试模式')

    args = parser.parse_args()

    server = CardGeneratorMCPServer(args.template)

    if args.test:
        # 测试模式
        print("Running in test mode...")

        # 测试解析自然语言
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "parse_natural_language",
                "arguments": {
                    "description": "Create a ninja card called Shadow Strike that costs 2 and deals 5 damage with 3 defense"
                }
            }
        }

        response = server.handle_mcp_request(test_request)
        print(json.dumps(response, indent=2, ensure_ascii=False))

    else:
        # STDIO模式
        server.run_stdio()


if __name__ == '__main__':
    main()
