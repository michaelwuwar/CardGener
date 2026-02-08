#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CardGener MCP Server
Provides Model Context Protocol (MCP) integration for AI-powered card generation.
All operation parameters are designed to be generated and passed by AI.
"""

import json
import sys
import os
import time
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
        self.card_schema = None  # Dynamic card schema
        self.schema_path = "card_schema.json"

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

    def load_card_schema(self) -> Dict[str, Any]:
        """Load or create card schema definition"""
        try:
            if Path(self.schema_path).exists():
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load schema: {e}", file=sys.stderr)

        # Return default schema
        return {
            "fields": {
                "card_name": {"type": "text", "required": True, "description": "Card title/name"},
                "card_type": {"type": "text", "required": True, "description": "Card type (e.g., 'Action - Attack')"},
                "rules_text": {"type": "text", "required": True, "description": "Card rules and effect text"},
                "cost": {"type": "text", "required": True, "description": "Resource cost"},
                "power": {"type": "text", "required": True, "description": "Attack/power value"},
                "defense": {"type": "text", "required": True, "description": "Defense value"},
                "art_path": {"type": "image", "required": False, "description": "Path or URL to card artwork"},
                "class_type": {"type": "enum", "required": True, "description": "Character class",
                              "values": ["ninja", "warrior", "wizard", "ranger", "guardian", "brute", "mechanologist", "runeblade", "merchant", "illusionist"]},
                "artist": {"type": "text", "required": False, "description": "Artist name", "default": "Unknown Artist"},
                "year": {"type": "text", "required": False, "description": "Copyright year", "default": "2024"}
            },
            "card_types": ["Action - Attack", "Action - Defense", "Hero", "Equipment", "Weapon", "Instant"],
            "version": "1.0"
        }

    def save_card_schema(self, schema: Dict[str, Any]) -> bool:
        """Save card schema to file"""
        try:
            with open(self.schema_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Failed to save schema: {e}", file=sys.stderr)
            return False

    def setup_handlers(self):
        """Setup MCP tool handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools - all require AI-generated parameters"""
            return [
                Tool(
                    name="get_card_schema",
                    description=(
                        "Get the current card schema definition including all fields, types, and their properties. "
                        "Use this to understand what fields are available for card generation and their requirements."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="update_card_schema",
                    description=(
                        "Update the card schema to add new fields, modify field types, or add new card types. "
                        "AI can use this to customize the card system based on user requirements. "
                        "For example: add a new field 'rarity', add new class types, or modify existing field properties."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Action to perform: 'add_field', 'modify_field', 'remove_field', 'add_card_type', 'add_class_value'",
                                "enum": ["add_field", "modify_field", "remove_field", "add_card_type", "add_class_value"]
                            },
                            "field_name": {
                                "type": "string",
                                "description": "Name of the field (for field operations)"
                            },
                            "field_config": {
                                "type": "object",
                                "description": "Field configuration (for add_field/modify_field)",
                                "properties": {
                                    "type": {"type": "string", "description": "Field type: text, image, enum"},
                                    "required": {"type": "boolean"},
                                    "description": {"type": "string"},
                                    "default": {"type": "string"},
                                    "values": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "value": {
                                "type": "string",
                                "description": "Value to add (for add_card_type or add_class_value)"
                            }
                        },
                        "required": ["action"]
                    }
                ),
                Tool(
                    name="generate_card",
                    description=(
                        "Generate a single CardConjurer JSON card file. "
                        "AI must provide ALL card parameters based on current schema. "
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
                    name="generate_ai_artwork",
                    description=(
                        "Generate AI artwork for cards using free API services. "
                        "AI provides prompts or card data, and this tool generates artwork images. "
                        "Supports multiple AI image generation services (pollinations, huggingface, modelscope)."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cards": {
                                "type": "array",
                                "description": "Array of card data to generate artwork for",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "card_name": {"type": "string"},
                                        "prompt": {"type": "string", "description": "Custom image prompt (optional, auto-generated if not provided)"},
                                        "card_type": {"type": "string"},
                                        "rules_text": {"type": "string"},
                                        "class_type": {"type": "string"}
                                    }
                                }
                            },
                            "output_dir": {
                                "type": "string",
                                "description": "Directory to save generated images",
                                "default": "generated_art"
                            },
                            "api_type": {
                                "type": "string",
                                "description": "AI service to use",
                                "enum": ["pollinations", "huggingface", "modelscope", "modelscope_inference"],
                                "default": "pollinations"
                            },
                            "width": {
                                "type": "integer",
                                "description": "Image width",
                                "default": 1024
                            },
                            "height": {
                                "type": "integer",
                                "description": "Image height",
                                "default": 1024
                            }
                        },
                        "required": ["cards"]
                    }
                ),
                Tool(
                    name="render_cards_to_images",
                    description=(
                        "Render card JSON files to PNG images using CardConjurer automation. "
                        "Takes JSON files and produces final card images ready for printing or use. "
                        "Optionally can overlay AI-generated artwork onto the cards."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "json_dir": {
                                "type": "string",
                                "description": "Directory containing card JSON files"
                            },
                            "output_dir": {
                                "type": "string",
                                "description": "Directory to save rendered card images",
                                "default": "rendered_cards"
                            },
                            "headless": {
                                "type": "boolean",
                                "description": "Run browser in headless mode",
                                "default": true
                            },
                            "overlay_art_dir": {
                                "type": "string",
                                "description": "Optional directory with AI-generated art to overlay onto cards"
                            }
                        },
                        "required": ["json_dir"]
                    }
                ),
                Tool(
                    name="stitch_card_images",
                    description=(
                        "Stitch multiple card images into a grid/sheet suitable for Tabletop Simulator or printing. "
                        "Creates organized layouts of cards in N×M grids. "
                        "Supports presets like '4k', '2k', '1080p' for output scaling."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_dir": {
                                "type": "string",
                                "description": "Directory containing card images to stitch"
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Output file path for stitched image",
                                "default": "stitched_cards.png"
                            },
                            "cols": {
                                "type": "integer",
                                "description": "Number of columns",
                                "default": 10
                            },
                            "rows": {
                                "type": "integer",
                                "description": "Number of rows (optional, auto-calculated if not provided)"
                            },
                            "cards_per_sheet": {
                                "type": "integer",
                                "description": "Cards per sheet for TTS format (default 70 for 10×7)",
                                "default": 70
                            },
                            "preset": {
                                "type": "string",
                                "description": "Output resolution preset",
                                "enum": ["4k", "2k", "1080p", "720p"]
                            },
                            "tts_mode": {
                                "type": "boolean",
                                "description": "Create Tabletop Simulator format (10×7 grid, 70 cards per sheet)",
                                "default": false
                            }
                        },
                        "required": ["image_dir"]
                    }
                ),
                Tool(
                    name="full_workflow",
                    description=(
                        "Execute the complete card generation workflow: generate cards, create AI artwork, "
                        "render to images, and stitch into printable sheets. This is the all-in-one tool "
                        "for creating complete card sets from AI-generated data. Returns summary of all operations."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cards": {
                                "type": "array",
                                "description": "Array of card definitions",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "card_name": {"type": "string"},
                                        "card_type": {"type": "string"},
                                        "rules_text": {"type": "string"},
                                        "cost": {"type": "string"},
                                        "power": {"type": "string"},
                                        "defense": {"type": "string"},
                                        "class_type": {"type": "string"},
                                        "artist": {"type": "string"},
                                        "year": {"type": "string"}
                                    }
                                }
                            },
                            "output_base_dir": {
                                "type": "string",
                                "description": "Base directory for all outputs",
                                "default": "card_workflow_output"
                            },
                            "generate_artwork": {
                                "type": "boolean",
                                "description": "Whether to generate AI artwork",
                                "default": true
                            },
                            "render_images": {
                                "type": "boolean",
                                "description": "Whether to render card images",
                                "default": true
                            },
                            "stitch_images": {
                                "type": "boolean",
                                "description": "Whether to stitch into sheets",
                                "default": true
                            },
                            "tts_format": {
                                "type": "boolean",
                                "description": "Use Tabletop Simulator format for stitching",
                                "default": true
                            },
                            "ai_api": {
                                "type": "string",
                                "description": "AI service for artwork",
                                "enum": ["pollinations", "huggingface", "modelscope"],
                                "default": "pollinations"
                            }
                        },
                        "required": ["cards"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls - all parameters come from AI"""

            if name == "get_card_schema":
                try:
                    schema = self.load_card_schema()
                    result = {
                        "status": "success",
                        "message": "✅ Card schema retrieved",
                        "schema": schema
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
                            "message": f"❌ Failed to get schema: {str(e)}"
                        }, indent=2)
                    )]

            elif name == "update_card_schema":
                try:
                    schema = self.load_card_schema()
                    action = arguments.get('action')

                    if action == "add_field":
                        field_name = arguments.get('field_name')
                        field_config = arguments.get('field_config', {})
                        if not field_name:
                            raise ValueError("field_name is required for add_field")
                        schema['fields'][field_name] = field_config
                        message = f"✅ Added field: {field_name}"

                    elif action == "modify_field":
                        field_name = arguments.get('field_name')
                        field_config = arguments.get('field_config', {})
                        if not field_name or field_name not in schema['fields']:
                            raise ValueError(f"Field {field_name} not found")
                        schema['fields'][field_name].update(field_config)
                        message = f"✅ Modified field: {field_name}"

                    elif action == "remove_field":
                        field_name = arguments.get('field_name')
                        if not field_name or field_name not in schema['fields']:
                            raise ValueError(f"Field {field_name} not found")
                        del schema['fields'][field_name]
                        message = f"✅ Removed field: {field_name}"

                    elif action == "add_card_type":
                        value = arguments.get('value')
                        if not value:
                            raise ValueError("value is required for add_card_type")
                        if 'card_types' not in schema:
                            schema['card_types'] = []
                        if value not in schema['card_types']:
                            schema['card_types'].append(value)
                        message = f"✅ Added card type: {value}"

                    elif action == "add_class_value":
                        value = arguments.get('value')
                        if not value:
                            raise ValueError("value is required for add_class_value")
                        if 'class_type' in schema['fields'] and 'values' in schema['fields']['class_type']:
                            if value not in schema['fields']['class_type']['values']:
                                schema['fields']['class_type']['values'].append(value)
                        message = f"✅ Added class value: {value}"

                    else:
                        raise ValueError(f"Unknown action: {action}")

                    self.save_card_schema(schema)

                    result = {
                        "status": "success",
                        "message": message,
                        "updated_schema": schema
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
                            "message": f"❌ Failed to update schema: {str(e)}"
                        }, indent=2)
                    )]

            elif name == "generate_card":
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

            elif name == "generate_ai_artwork":
                try:
                    from ai_image_generator import AIImageGenerator

                    cards_data = arguments.get('cards', [])
                    output_dir = arguments.get('output_dir', 'generated_art')
                    api_type = arguments.get('api_type', 'pollinations')
                    width = arguments.get('width', 1024)
                    height = arguments.get('height', 1024)

                    if not cards_data:
                        raise ValueError("No cards provided")

                    generator = AIImageGenerator(api_type=api_type)
                    results = []

                    os.makedirs(output_dir, exist_ok=True)

                    for idx, card_data in enumerate(cards_data):
                        card_name = card_data.get('card_name', f'card_{idx}')
                        prompt = card_data.get('prompt')

                        if not prompt:
                            # Auto-generate prompt from card data
                            prompt = generator.generate_card_art_prompt(card_data)

                        safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
                        safe_name = safe_name.replace(' ', '_')
                        output_path = os.path.join(output_dir, f"{safe_name}.png")

                        print(f"🎨 Generating art for: {card_name}", file=sys.stderr)
                        success = generator.generate_and_save(prompt, output_path, width, height)

                        results.append({
                            "card_name": card_name,
                            "status": "success" if success else "failed",
                            "output_path": output_path if success else None,
                            "prompt": prompt
                        })

                        if idx < len(cards_data) - 1:
                            time.sleep(2)  # Rate limiting

                    success_count = sum(1 for r in results if r['status'] == 'success')

                    summary = {
                        "status": "completed",
                        "message": f"🎨 Generated {success_count}/{len(cards_data)} artworks",
                        "output_dir": output_dir,
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
                            "message": f"❌ AI artwork generation failed: {str(e)}"
                        }, indent=2)
                    )]

            elif name == "render_cards_to_images":
                try:
                    from cardconjurer_automation import CardConjurerAutomation

                    json_dir = arguments.get('json_dir')
                    output_dir = arguments.get('output_dir', 'rendered_cards')
                    headless = arguments.get('headless', True)
                    overlay_art_dir = arguments.get('overlay_art_dir')

                    if not json_dir:
                        raise ValueError("json_dir is required")

                    json_files = list(Path(json_dir).glob("*.json"))
                    if not json_files:
                        raise ValueError(f"No JSON files found in {json_dir}")

                    automation = CardConjurerAutomation(headless=headless, download_dir=output_dir)
                    success_count = automation.batch_import_and_download([str(f) for f in json_files])

                    # Overlay art if provided
                    overlay_count = 0
                    if overlay_art_dir and Path(overlay_art_dir).exists():
                        overlay_count = automation.overlay_generated_art(
                            overlay_art_dir,
                            source_dir=output_dir,
                            json_dir=json_dir,
                            inplace=True
                        )

                    result = {
                        "status": "success",
                        "message": f"✅ Rendered {success_count}/{len(json_files)} cards",
                        "rendered_count": success_count,
                        "overlay_count": overlay_count,
                        "output_dir": output_dir
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
                            "message": f"❌ Card rendering failed: {str(e)}"
                        }, indent=2)
                    )]

            elif name == "stitch_card_images":
                try:
                    from image_stitcher import ImageStitcher

                    image_dir = arguments.get('image_dir')
                    output_path = arguments.get('output_path', 'stitched_cards.png')
                    cols = arguments.get('cols', 10)
                    rows = arguments.get('rows')
                    cards_per_sheet = arguments.get('cards_per_sheet', 70)
                    preset = arguments.get('preset')
                    tts_mode = arguments.get('tts_mode', False)

                    if not image_dir:
                        raise ValueError("image_dir is required")

                    stitcher = ImageStitcher()

                    if tts_mode:
                        # TTS format: 10x7, 70 cards per sheet
                        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
                        image_paths = [
                            str(p) for p in Path(image_dir).iterdir()
                            if p.suffix.lower() in image_extensions
                        ]
                        image_paths.sort()

                        output_dir = Path(output_path).parent / 'tts_decks'
                        sheets = stitcher.create_tabletop_simulator_deck(
                            image_paths,
                            str(output_dir),
                            cards_per_sheet=70,
                            cols=10,
                            preset=preset
                        )

                        result = {
                            "status": "success",
                            "message": f"✅ Created {len(sheets)} TTS sheets",
                            "sheets": sheets,
                            "output_dir": str(output_dir)
                        }
                    else:
                        # Regular stitching
                        success = stitcher.auto_stitch(
                            image_dir,
                            output_path,
                            max_cols=cols,
                            cards_per_sheet=cards_per_sheet,
                            preset=preset
                        )

                        result = {
                            "status": "success" if success else "failed",
                            "message": f"✅ Stitched cards to {output_path}" if success else "❌ Stitching failed",
                            "output_path": output_path
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
                            "message": f"❌ Image stitching failed: {str(e)}"
                        }, indent=2)
                    )]

            elif name == "full_workflow":
                try:
                    import time

                    cards_data = arguments.get('cards', [])
                    output_base_dir = arguments.get('output_base_dir', 'card_workflow_output')
                    generate_artwork = arguments.get('generate_artwork', True)
                    render_images = arguments.get('render_images', True)
                    stitch_images = arguments.get('stitch_images', True)
                    tts_format = arguments.get('tts_format', True)
                    ai_api = arguments.get('ai_api', 'pollinations')

                    if not cards_data:
                        raise ValueError("No cards provided")

                    workflow_results = {
                        "status": "in_progress",
                        "steps": []
                    }

                    # Step 1: Generate card JSONs
                    print("📝 Step 1: Generating card JSONs...", file=sys.stderr)
                    json_dir = os.path.join(output_base_dir, "card_jsons")
                    os.makedirs(json_dir, exist_ok=True)

                    json_results = []
                    for card_params in cards_data:
                        try:
                            card_data = self.generate_single_card(card_params)
                            saved_path = self.save_card_to_file(
                                card_data, json_dir, card_params['card_name']
                            )
                            json_results.append({"card": card_params['card_name'], "path": saved_path, "status": "success"})
                        except Exception as e:
                            json_results.append({"card": card_params.get('card_name', 'unknown'), "error": str(e), "status": "failed"})

                    workflow_results["steps"].append({
                        "step": "generate_jsons",
                        "status": "completed",
                        "results": json_results
                    })

                    # Step 2: Generate AI artwork (optional)
                    art_dir = None
                    if generate_artwork:
                        print("🎨 Step 2: Generating AI artwork...", file=sys.stderr)
                        from ai_image_generator import AIImageGenerator

                        art_dir = os.path.join(output_base_dir, "generated_art")
                        os.makedirs(art_dir, exist_ok=True)

                        generator = AIImageGenerator(api_type=ai_api)
                        art_results = []

                        for idx, card_data in enumerate(cards_data):
                            card_name = card_data.get('card_name', f'card_{idx}')
                            prompt = generator.generate_card_art_prompt(card_data)
                            safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
                            output_path = os.path.join(art_dir, f"{safe_name}.png")

                            success = generator.generate_and_save(prompt, output_path, 1024, 1024)
                            art_results.append({
                                "card": card_name,
                                "status": "success" if success else "failed",
                                "path": output_path if success else None
                            })

                            if idx < len(cards_data) - 1:
                                time.sleep(2)

                        workflow_results["steps"].append({
                            "step": "generate_artwork",
                            "status": "completed",
                            "results": art_results
                        })

                    # Step 3: Render cards to images (optional)
                    rendered_dir = None
                    if render_images:
                        print("🖼️ Step 3: Rendering cards to images...", file=sys.stderr)
                        from cardconjurer_automation import CardConjurerAutomation

                        rendered_dir = os.path.join(output_base_dir, "rendered_cards")
                        json_files = list(Path(json_dir).glob("*.json"))

                        automation = CardConjurerAutomation(headless=True, download_dir=rendered_dir)
                        render_count = automation.batch_import_and_download([str(f) for f in json_files])

                        # Overlay art if generated
                        overlay_count = 0
                        if art_dir:
                            overlay_count = automation.overlay_generated_art(
                                art_dir,
                                source_dir=rendered_dir,
                                json_dir=json_dir,
                                inplace=True
                            )

                        workflow_results["steps"].append({
                            "step": "render_cards",
                            "status": "completed",
                            "rendered_count": render_count,
                            "overlay_count": overlay_count
                        })

                    # Step 4: Stitch images (optional)
                    if stitch_images and rendered_dir:
                        print("📐 Step 4: Stitching images...", file=sys.stderr)
                        from image_stitcher import ImageStitcher

                        stitcher = ImageStitcher()
                        stitch_output = os.path.join(output_base_dir, "stitched")

                        if tts_format:
                            image_extensions = {'.png', '.jpg', '.jpeg'}
                            image_paths = [
                                str(p) for p in Path(rendered_dir).iterdir()
                                if p.suffix.lower() in image_extensions
                            ]
                            image_paths.sort()

                            sheets = stitcher.create_tabletop_simulator_deck(
                                image_paths,
                                stitch_output,
                                cards_per_sheet=70,
                                cols=10
                            )

                            workflow_results["steps"].append({
                                "step": "stitch_images",
                                "status": "completed",
                                "tts_sheets": sheets
                            })
                        else:
                            output_file = os.path.join(stitch_output, "stitched_cards.png")
                            success = stitcher.auto_stitch(
                                rendered_dir,
                                output_file,
                                max_cols=10
                            )

                            workflow_results["steps"].append({
                                "step": "stitch_images",
                                "status": "completed" if success else "failed",
                                "output": output_file if success else None
                            })

                    workflow_results["status"] = "completed"
                    workflow_results["message"] = f"✅ Full workflow completed! Generated {len(cards_data)} cards"
                    workflow_results["output_base_dir"] = output_base_dir

                    return [TextContent(
                        type="text",
                        text=json.dumps(workflow_results, indent=2, ensure_ascii=False)
                    )]

                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": f"❌ Full workflow failed: {str(e)}"
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
