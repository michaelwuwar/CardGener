# CardGener MCP Server - Quick Start

## Overview

CardGener now provides a comprehensive MCP (Model Context Protocol) server with **8 powerful tools** for AI-assisted card generation. Go from concept to printable cards with a single conversation!

## 🚀 New Features

### 1. Dynamic Schema Management
- **`get_card_schema`**: View all available card fields and types
- **`update_card_schema`**: Add custom fields, card types, or class values on the fly

### 2. Complete Workflow Automation
- **`full_workflow`**: ONE tool call for the complete pipeline
  - Generate card JSONs
  - Create AI artwork
  - Render via CardConjurer
  - Stitch into printable sheets

### 3. Individual Tools for Fine Control
- **`generate_card`**: Single card generation
- **`generate_cards_batch`**: Multiple cards at once
- **`generate_ai_artwork`**: AI-generated artwork (FREE, no API key!)
- **`render_cards_to_images`**: Automated CardConjurer rendering
- **`stitch_card_images`**: Create TTS decks or printable sheets

## 🎯 Quick Examples

### Example 1: Complete Card Set (Easiest!)
```
User: "Create 5 ninja attack cards with AI artwork and make them ready for Tabletop Simulator"

AI uses full_workflow with:
- cards: [5 ninja card definitions]
- generate_artwork: true
- render_images: true
- stitch_images: true
- tts_format: true
```

**Result**: Complete TTS-ready deck with AI artwork in one go!

### Example 2: Add Custom Field
```
User: "I want to add a rarity field to my cards with values Common, Rare, and Legendary"

AI uses update_card_schema:
- action: "add_field"
- field_name: "rarity"
- field_config: {type: "enum", values: ["Common", "Rare", "Legendary"]}
```

**Result**: Schema updated, future cards can include rarity!

### Example 3: Generate with Custom Field
```
User: "Create a Legendary ninja card called 'Master Strike'"

AI first checks schema with get_card_schema, then uses generate_card with:
- card_name: "Master Strike"
- rarity: "Legendary"
- [other fields...]
```

## 📦 Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure in Claude Desktop** (or any MCP client):
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

3. **Restart Claude Desktop** and tools will be available!

## 🎨 AI Artwork (Free!)

The `pollinations` API is **completely free** and requires **no API key**. Just enable `generate_artwork: true` in full_workflow or call `generate_ai_artwork` directly.

Other supported APIs:
- `huggingface`: Requires HF_API_KEY
- `modelscope`: Requires MODELSCOPE_API_KEY
- `modelscope_inference`: Requires MODELSCOPE_SDK_TOKEN

You can pass `api_key`, `model`, and `poll_interval` to `generate_ai_artwork` when using paid providers (e.g., ModelScope inference) if the environment variables are not set.

## 📚 Documentation

- **`MCP_IMPROVEMENTS.md`**: Detailed documentation of all improvements
- **`.github/skills/cardgener-full-workflow.md`**: Comprehensive skill guide
- **`MCP_USAGE_GUIDE.md`**: Original MCP usage documentation
- **`mcp_config.json`**: Tool schemas and examples

## 🔧 What Changed?

### Removed
- ❌ `parse_natural_language`: Unnecessary - AI can parse directly

### Added
- ✅ `get_card_schema`: View schema
- ✅ `update_card_schema`: Customize schema
- ✅ `generate_ai_artwork`: AI art generation
- ✅ `render_cards_to_images`: Automated rendering
- ✅ `stitch_card_images`: Create printable sheets
- ✅ `full_workflow`: Complete automation

### Fixed
- ✅ GitHub Actions packaging issues
- ✅ Missing icon handling
- ✅ Artifact upload/download paths

## 🎮 Use Cases

1. **Game Designers**: Rapidly prototype card designs with AI
2. **Tabletop Sim Players**: Create custom decks for online play
3. **Print & Play**: Generate printable card sheets
4. **Rapid Iteration**: Test card mechanics quickly
5. **Custom Cards**: Personalize existing games

## 💡 Pro Tips

1. **Start with full_workflow** for the simplest experience
2. **Check schema first** with `get_card_schema` before generating
3. **Use pollinations** for free, unlimited AI artwork
4. **TTS format** creates perfect 10×7 grids for Tabletop Simulator
5. **Batch generation** is faster than individual cards
6. **Read cards via tools**: use `search_cards` + `read_card` instead of raw file reads to avoid noisy JSON dumps

## 🚨 Requirements

- Python 3.8+
- Chrome/Chromium (for rendering)
- Internet connection (for AI artwork)
- MCP-compatible client (Claude Desktop, etc.)

## 📞 Support

- Issues: https://github.com/michaelwuwar/CardGener/issues
- Documentation: See `MCP_IMPROVEMENTS.md`
- Examples: See `.github/skills/cardgener-full-workflow.md`

---

**Start creating amazing cards with AI today!** 🎴✨
