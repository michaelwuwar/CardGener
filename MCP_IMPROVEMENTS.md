# CardGener MCP Service Improvements

This document describes the improvements made to the CardGener MCP (Model Context Protocol) service.

## Summary of Changes

### 1. Removed Unnecessary Tools
- **Removed `parse_natural_language` tool**: This tool provided no real value since AI models can already parse natural language directly and extract structured parameters. The tool was essentially a placeholder that returned suggestions for the AI to do the parsing itself.

### 2. Added Dynamic Schema Management

#### `get_card_schema` Tool
- Retrieves the current card schema definition
- Shows all available fields, their types, requirements, and default values
- Displays available card types and class values
- No parameters required

**Example Usage:**
```json
{
  "tool": "get_card_schema"
}
```

**Returns:**
```json
{
  "status": "success",
  "schema": {
    "fields": {
      "card_name": {"type": "text", "required": true, ...},
      "class_type": {"type": "enum", "values": ["ninja", "warrior", ...], ...}
    },
    "card_types": ["Action - Attack", "Action - Defense", ...],
    "version": "1.0"
  }
}
```

#### `update_card_schema` Tool
- Dynamically add, modify, or remove card fields
- Add new card types or class values
- Persists changes to `card_schema.json`

**Supported Actions:**
- `add_field`: Add a new field to card schema
- `modify_field`: Update existing field properties
- `remove_field`: Remove a field from schema
- `add_card_type`: Add a new card type option
- `add_class_value`: Add a new class type value

**Example: Add Rarity Field**
```json
{
  "tool": "update_card_schema",
  "action": "add_field",
  "field_name": "rarity",
  "field_config": {
    "type": "enum",
    "required": false,
    "description": "Card rarity level",
    "values": ["Common", "Uncommon", "Rare", "Legendary"]
  }
}
```

### 3. Added AI Artwork Generation

#### `generate_ai_artwork` Tool
- Generates AI artwork for cards using free APIs
- Supports multiple AI services (pollinations, huggingface, modelscope)
- Auto-generates prompts based on card data
- Allows custom prompts for each card

**Features:**
- **Free Service**: Default `pollinations` API requires no API key
- **Auto-prompt Generation**: Creates contextual prompts from card data
- **Batch Processing**: Generate artwork for multiple cards at once
- **Rate Limiting**: Built-in delays to respect API limits

**Example:**
```json
{
  "tool": "generate_ai_artwork",
  "cards": [
    {
      "card_name": "Shadow Strike",
      "card_type": "Action - Attack",
      "class_type": "ninja",
      "rules_text": "Deal 5 damage. Go again."
    }
  ],
  "output_dir": "generated_art",
  "api_type": "pollinations",
  "width": 1024,
  "height": 1024
}
```

### 4. Added Card Rendering Automation

#### `render_cards_to_images` Tool
- Automates CardConjurer web interface to render cards
- Imports JSON files and downloads rendered images
- Optionally overlays AI-generated artwork
- Supports headless browser mode

**Features:**
- **Automated Browser Control**: Uses Selenium to control CardConjurer
- **Artwork Overlay**: Automatically overlays AI-generated art onto rendered cards
- **Batch Processing**: Process multiple cards in one run
- **Bounds-Aware Overlay**: Uses JSON bounds data for precise artwork placement

**Example:**
```json
{
  "tool": "render_cards_to_images",
  "json_dir": "output/cards",
  "output_dir": "rendered_cards",
  "headless": true,
  "overlay_art_dir": "generated_art"
}
```

### 5. Added Image Stitching

#### `stitch_card_images` Tool
- Combines multiple card images into printable sheets
- Supports Tabletop Simulator (TTS) format
- Configurable grid layouts and resolutions
- Output scaling presets (4K, 2K, 1080p, 720p)

**Features:**
- **TTS Mode**: Creates 10×7 grids with 70 cards per sheet (TTS standard)
- **Custom Layouts**: Specify any N×M grid configuration
- **Resolution Presets**: Easy output scaling for different uses
- **Auto-pagination**: Splits large sets into multiple sheets

**Example (TTS Format):**
```json
{
  "tool": "stitch_card_images",
  "image_dir": "rendered_cards",
  "output_path": "final_deck.png",
  "tts_mode": true,
  "preset": "4k"
}
```

### 6. Added Complete Workflow Automation

#### `full_workflow` Tool
- **All-in-one tool** for complete card generation pipeline
- Executes all steps: JSON generation → AI artwork → rendering → stitching
- Configurable steps: enable/disable any phase
- Returns comprehensive progress summary

**Workflow Steps:**
1. **Generate Card JSONs**: Creates CardConjurer-compatible JSON files
2. **Generate AI Artwork** (optional): Creates artwork for each card
3. **Render Cards** (optional): Produces final card images via CardConjurer
4. **Overlay Artwork** (optional): Applies AI art to rendered cards
5. **Stitch Images** (optional): Creates printable sheets/TTS decks

**Example:**
```json
{
  "tool": "full_workflow",
  "cards": [
    {
      "card_name": "Shadow Strike",
      "card_type": "Action - Attack",
      "rules_text": "Deal 5 damage. Go again.",
      "cost": "2",
      "power": "5",
      "defense": "3",
      "class_type": "ninja"
    },
    {
      "card_name": "Ninja Assault",
      "card_type": "Action - Attack",
      "rules_text": "Deal 3 damage. Draw a card.",
      "cost": "1",
      "power": "3",
      "defense": "2",
      "class_type": "ninja"
    }
  ],
  "output_base_dir": "ninja_card_set",
  "generate_artwork": true,
  "render_images": true,
  "stitch_images": true,
  "tts_format": true,
  "ai_api": "pollinations"
}
```

**Output Structure:**
```
ninja_card_set/
├── card_jsons/          # Generated JSON files
│   ├── Shadow_Strike.json
│   └── Ninja_Assault.json
├── generated_art/       # AI-generated artwork
│   ├── Shadow_Strike.png
│   └── Ninja_Assault.png
├── rendered_cards/      # Final rendered cards with artwork
│   ├── Shadow_Strike.png
│   └── Ninja_Assault.png
└── stitched/           # TTS sheets
    └── deck_sheet_1.png
```

## Benefits of These Improvements

### 1. Flexibility
- **Dynamic Schema**: Users can customize card structure without modifying code
- **Configurable Workflow**: Enable/disable any step in the pipeline
- **Multiple AI Services**: Choose from several free AI image generation APIs

### 2. Automation
- **End-to-End Workflow**: Single tool call generates complete, printable card sets
- **Reduced Manual Work**: No need to manually upload to CardConjurer or stitch images
- **Batch Processing**: Handle dozens or hundreds of cards efficiently

### 3. Quality
- **AI-Generated Artwork**: Professional-looking card art without hiring artists
- **Precise Overlay**: Uses JSON bounds data for accurate artwork placement
- **High-Resolution Output**: 4K support for printing

### 4. Accessibility
- **No API Keys Required**: Default pollinations service is completely free
- **MCP Integration**: Works seamlessly with Claude Desktop and other MCP clients
- **Comprehensive Documentation**: Skills and examples guide users through the workflow

## GitHub Actions Improvements

### Fixed Packaging Issues

**Problems Addressed:**
1. **Missing Icon Handling**: Added fallback for missing icon.ico file
2. **Artifact Path Issues**: Fixed artifact upload/download paths
3. **Cross-Platform Compatibility**: Added shell directives for Windows compatibility
4. **Release File Matching**: Added `fail_on_unmatched_files: false` for flexibility

**Key Changes:**
- Create placeholder icon if missing (using PIL)
- Use `dist/*` pattern to capture all build outputs
- Add directory listing for debugging
- Use artifact subdirectories for better organization
- Support recursive artifact downloading in releases

## Usage Recommendations

### For Simple Card Generation
```python
# Just generate card JSONs
generate_card(...)
```

### For Complete Automation
```python
# One call does everything
full_workflow(
    cards=[...],
    generate_artwork=True,
    render_images=True,
    stitch_images=True,
    tts_format=True
)
```

### For Custom Workflows
```python
# Mix and match tools as needed
1. get_card_schema()
2. update_card_schema(action="add_field", ...)
3. generate_cards_batch(cards=[...])
4. generate_ai_artwork(cards=[...])
5. render_cards_to_images(json_dir="...", overlay_art_dir="...")
6. stitch_card_images(image_dir="...", tts_mode=True)
```

## Skill Documentation

Comprehensive skill documentation has been added to guide AI assistants through the full workflow:
- `.github/skills/cardgener-full-workflow.md`
- `.agent/skills/cardgener-full-workflow.md`
- `.claude/skills/cardgener-full-workflow.md`

These files provide:
- Step-by-step workflow guides
- Complete examples for each tool
- Best practices and troubleshooting
- Output structure documentation

## Testing Notes

While comprehensive automated testing would require a full MCP environment with browser automation, the following manual testing is recommended:

1. **Schema Management**: Test get/update schema operations
2. **Card Generation**: Verify JSON output format
3. **AI Artwork**: Test with pollinations API (free, no key needed)
4. **Rendering**: Requires Chrome/Chromium and CardConjurer access
5. **Stitching**: Test with sample images
6. **Full Workflow**: End-to-end test with small card set (2-3 cards)

## Migration Guide

### For Existing Users

**No Breaking Changes**: All existing tools (`generate_card`, `generate_cards_batch`) continue to work as before.

**New Capabilities**: Simply start using the new tools:
- Check your schema: `get_card_schema`
- Customize fields: `update_card_schema`
- Full automation: `full_workflow`

### Removing parse_natural_language

If you were using `parse_natural_language`, simply stop calling it. AI models can parse natural language directly and call `generate_card` with the extracted parameters. This is actually more efficient and accurate than the previous approach.

**Before:**
```json
{
  "tool": "parse_natural_language",
  "description": "Create a ninja card that costs 2..."
}
// Then AI would have to parse the result and call generate_card
```

**After (Better):**
```json
// AI directly extracts parameters and calls generate_card
{
  "tool": "generate_card",
  "card_name": "Ninja Strike",
  "cost": "2",
  ...
}
```

## Future Enhancements

Potential areas for future improvement:
1. **Real-time Progress Updates**: Stream progress for long-running operations
2. **Parallel Processing**: Render multiple cards simultaneously
3. **Template Management**: Tools to manage custom CardConjurer templates
4. **Export Formats**: Support for additional output formats (PDF, printable sheets)
5. **Advanced AI Services**: Integration with paid services for higher quality
6. **Card Database**: Store and retrieve previously generated cards

## Conclusion

These improvements transform CardGener from a simple card JSON generator into a complete, AI-powered card production system. Users can now go from card ideas to printable, professional-quality cards with a single tool call, all while maintaining flexibility for custom workflows.
