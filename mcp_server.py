#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CardGener MCP Server
Provides Model Context Protocol (MCP) integration for AI-powered card generation.
All operation parameters are designed to be generated and passed by AI.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
except ImportError:
    print("❌ MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


class CardGeneratorMCPServer:
    """MCP Server for CardGener - All parameters are AI-generated"""

    def __init__(self):
        self.server = Server("cardgener-mcp-server")
        self.template = None
        self.template_path = "template.json"

        # Setup tool handlers
        self.setup_handlers()

    def load_template(self, template_path: Optional[str] = None) -> Dict[str, Any]:
        """Load JSON template for card generation"""
        path = template_path or self.template_path
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load template from {path}: {e}")

    def update_field(self, data: Dict[str, Any], field_type: str,
                    field_name: str, value: str) -> bool:
        """Recursively update a field in the card data structure"""
        if data.get('type') == field_type and data.get('name') == field_name:
            if field_type == 'text':
                data['text'] = value
            elif field_type == 'image':
                data['src'] = value
            return True

        if 'children' in data:
            for child in data['children']:
                if self.update_field(child, field_type, field_name, value):
                    return True
        return False

    def update_class_frame(self, data: Dict[str, Any], class_type: str) -> bool:
        """Update the class frame image in card data"""
        if data.get('type') == 'image' and 'Class' in data.get('name', ''):
            class_lower = class_type.lower()
            data['src'] = f"fab/frame/classes/{class_lower}.png"
            data['thumb'] = f"fab/frame/classes/thumb-{class_lower}.png"
            data['name'] = f"{class_type.title()} Class"
            return True

        if 'children' in data:
            for child in data['children']:
                if self.update_class_frame(child, class_type):
                    return True
        return False

    def generate_single_card(self, card_params: Dict[str, Any],
                           template_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a single card from AI-provided parameters

        Args:
            card_params: Dictionary with card field values (all AI-generated)
                - card_name: Card title
                - card_type: Card type (e.g., "Action - Attack")
                - rules_text: Card rules/effect text
                - cost: Resource cost
                - power: Attack/left stat value
                - defense: Defense/right stat value
                - art_path: Path or URL to card art
                - class_type: Class/profession (e.g., "ninja", "warrior")
                - artist: Artist name (optional)
                - year: Copyright year (optional)
            template_override: Optional custom template path

        Returns:
            Complete card JSON data
        """
        # Load template
        template = self.load_template(template_override)

        # Deep copy template
        card = json.loads(json.dumps(template))

        # Update text fields from AI parameters
        self.update_field(card['data'], 'text', 'Title',
                         card_params.get('card_name', ''))
        self.update_field(card['data'], 'text', 'Type',
                         card_params.get('card_type', ''))
        self.update_field(card['data'], 'text', 'Rules',
                         card_params.get('rules_text', ''))
        self.update_field(card['data'], 'text', 'Cost',
                         str(card_params.get('cost', '')))
        self.update_field(card['data'], 'text', 'Left Stat',
                         str(card_params.get('power', '')))
        self.update_field(card['data'], 'text', 'Right Stat',
                         str(card_params.get('defense', '')))

        # Update collector info
        artist = card_params.get('artist', 'Unknown Artist')
        year = card_params.get('year', '2024')
        collector_info = f"{artist} © {year} Legend Story Studios"
        self.update_field(card['data'], 'text', 'Collector Info', collector_info)

        # Update art image if provided
        art_path = card_params.get('art_path', '')
        if art_path:
            self.update_field(card['data'], 'image', 'Art', art_path)

        # Update class frame
        class_type = card_params.get('class_type', 'ninja')
        if class_type:
            self.update_class_frame(card['data'], class_type)

        return card

    def save_card_to_file(self, card_data: Dict[str, Any],
                         output_path: str, card_name: str) -> str:
        """Save card JSON to file"""
        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')

        # Save file
        output_file = output_dir / f"{safe_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(card_data, f, indent=4, ensure_ascii=False)

        return str(output_file)

    def setup_handlers(self):
        """Setup MCP tool handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools - all require AI-generated parameters"""
            return [
                Tool(
                    name="generate_card",
                    description=(
                        "Generate a single CardConjurer JSON card file. "
                        "AI must provide ALL card parameters including: "
                        "card_name, card_type, rules_text, cost, power, defense, "
                        "art_path, class_type, artist, and year. "
                        "Returns the generated card data and file path."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "card_name": {
                                "type": "string",
                                "description": "Card title/name (AI-generated)"
                            },
                            "card_type": {
                                "type": "string",
                                "description": "Card type, e.g., 'Action - Attack' (AI-generated)"
                            },
                            "rules_text": {
                                "type": "string",
                                "description": "Card rules and effect text (AI-generated)"
                            },
                            "cost": {
                                "type": "string",
                                "description": "Resource cost value (AI-generated)"
                            },
                            "power": {
                                "type": "string",
                                "description": "Attack/power value (left stat) (AI-generated)"
                            },
                            "defense": {
                                "type": "string",
                                "description": "Defense value (right stat) (AI-generated)"
                            },
                            "art_path": {
                                "type": "string",
                                "description": "Path or URL to card artwork (AI-generated)"
                            },
                            "class_type": {
                                "type": "string",
                                "description": "Class/profession: ninja, warrior, wizard, etc. (AI-generated)",
                                "default": "ninja"
                            },
                            "artist": {
                                "type": "string",
                                "description": "Artist name for credits (AI-generated)",
                                "default": "Unknown Artist"
                            },
                            "year": {
                                "type": "string",
                                "description": "Copyright year (AI-generated)",
                                "default": "2024"
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Output directory path (AI-generated)",
                                "default": "output"
                            },
                            "template_path": {
                                "type": "string",
                                "description": "Optional custom template JSON path (AI-generated)"
                            }
                        },
                        "required": [
                            "card_name", "card_type", "rules_text",
                            "cost", "power", "defense", "class_type"
                        ]
                    }
                ),
                Tool(
                    name="generate_cards_batch",
                    description=(
                        "Generate multiple cards in batch from AI-provided card definitions. "
                        "AI must provide a list of card parameter dictionaries, each containing "
                        "all required fields. Returns summary of generated cards."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cards": {
                                "type": "array",
                                "description": "Array of card parameter objects (all AI-generated)",
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
                                    },
                                    "required": [
                                        "card_name", "card_type", "rules_text",
                                        "cost", "power", "defense", "class_type"
                                    ]
                                }
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Output directory for all cards (AI-generated)",
                                "default": "output"
                            },
                            "template_path": {
                                "type": "string",
                                "description": "Optional custom template path (AI-generated)"
                            }
                        },
                        "required": ["cards"]
                    }
                ),
                Tool(
                    name="parse_natural_language",
                    description=(
                        "Parse natural language card description and extract structured parameters. "
                        "AI provides free-form text description, and this tool extracts card fields. "
                        "Use this when AI has a text description that needs to be structured."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Natural language card description (AI-generated)"
                            },
                            "context": {
                                "type": "object",
                                "description": "Additional context hints (AI-generated)",
                                "properties": {
                                    "game_type": {"type": "string"},
                                    "card_set": {"type": "string"},
                                    "rarity": {"type": "string"}
                                }
                            }
                        },
                        "required": ["description"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls - all parameters come from AI"""

            if name == "generate_card":
                try:
                    # Extract AI-provided parameters
                    card_params = {
                        'card_name': arguments.get('card_name'),
                        'card_type': arguments.get('card_type'),
                        'rules_text': arguments.get('rules_text'),
                        'cost': arguments.get('cost'),
                        'power': arguments.get('power'),
                        'defense': arguments.get('defense'),
                        'art_path': arguments.get('art_path', ''),
                        'class_type': arguments.get('class_type', 'ninja'),
                        'artist': arguments.get('artist', 'Unknown Artist'),
                        'year': arguments.get('year', '2024')
                    }

                    output_path = arguments.get('output_path', 'output')
                    template_path = arguments.get('template_path')

                    # Generate card
                    card_data = self.generate_single_card(card_params, template_path)

                    # Save to file
                    saved_path = self.save_card_to_file(
                        card_data, output_path, card_params['card_name']
                    )

                    result = {
                        "status": "success",
                        "message": f"✅ Card '{card_params['card_name']}' generated successfully",
                        "file_path": saved_path,
                        "card_data": card_data
                    }

                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2, ensure_ascii=False)
                    )]

                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": f"❌ Failed to generate card: {str(e)}"
                        }, indent=2)
                    )]

            elif name == "generate_cards_batch":
                try:
                    cards_list = arguments.get('cards', [])
                    output_path = arguments.get('output_path', 'output')
                    template_path = arguments.get('template_path')

                    if not cards_list:
                        raise ValueError("No cards provided in batch")

                    results = []
                    success_count = 0

                    for idx, card_params in enumerate(cards_list):
                        try:
                            # Generate card
                            card_data = self.generate_single_card(card_params, template_path)

                            # Save to file
                            saved_path = self.save_card_to_file(
                                card_data, output_path, card_params['card_name']
                            )

                            results.append({
                                "index": idx,
                                "card_name": card_params['card_name'],
                                "status": "success",
                                "file_path": saved_path
                            })
                            success_count += 1

                        except Exception as e:
                            results.append({
                                "index": idx,
                                "card_name": card_params.get('card_name', f'card_{idx}'),
                                "status": "error",
                                "error": str(e)
                            })

                    summary = {
                        "status": "completed",
                        "total_cards": len(cards_list),
                        "successful": success_count,
                        "failed": len(cards_list) - success_count,
                        "message": f"🎉 Generated {success_count}/{len(cards_list)} cards successfully",
                        "results": results
                    }

                    return [TextContent(
                        type="text",
                        text=json.dumps(summary, indent=2, ensure_ascii=False)
                    )]

                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": f"❌ Batch generation failed: {str(e)}"
                        }, indent=2)
                    )]

            elif name == "parse_natural_language":
                try:
                    description = arguments.get('description', '')
                    context = arguments.get('context', {})

                    if not description:
                        raise ValueError("No description provided")

                    # This is a placeholder for NLP parsing
                    # In a real implementation, this would use NLP to extract fields
                    result = {
                        "status": "success",
                        "message": "Natural language parsing requires AI implementation",
                        "input": {
                            "description": description,
                            "context": context
                        },
                        "suggestion": (
                            "AI should analyze the description and extract: "
                            "card_name, card_type, rules_text, cost, power, defense, "
                            "class_type, and other fields, then call generate_card with those parameters."
                        )
                    }

                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2, ensure_ascii=False)
                    )]

                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": f"❌ Parse failed: {str(e)}"
                        }, indent=2)
                    )]

            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Unknown tool: {name}"
                    }, indent=2)
                )]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    print("🚀 Starting CardGener MCP Server...", file=sys.stderr)
    print("📝 All operation parameters are AI-generated", file=sys.stderr)

    try:
        server = CardGeneratorMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n⚠️ Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
