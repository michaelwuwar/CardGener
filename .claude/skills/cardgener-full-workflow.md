# CardGener Full Workflow Skill

This skill guides you through using CardGener's MCP server to create a complete set of custom game cards from concept to printable images.

## Prerequisites

- CardGener MCP server configured and running
- Claude Desktop or MCP-compatible client
- Internet connection (for AI image generation)
- Chrome/Chromium browser (for card rendering)

## Workflow Overview

CardGener provides a complete end-to-end workflow for creating custom game cards:

1. **Design Phase**: Define card schema and card content
2. **Generation Phase**: Generate card JSON files
3. **Artwork Phase**: Create AI-generated artwork
4. **Rendering Phase**: Render cards to high-quality images
5. **Assembly Phase**: Stitch cards into printable sheets

## Step-by-Step Guide

### 1. Check Current Card Schema

First, understand the current card schema to see what fields are available:

```
Use the get_card_schema tool to retrieve the current schema
```

This will show you:
- Available card fields (card_name, card_type, rules_text, cost, power, defense, etc.)
- Field types and requirements
- Available card types and class values

### 2. Customize Schema (Optional)

If you need additional fields or card types, update the schema:

**Example: Add a rarity field**
```
Use update_card_schema tool:
- action: "add_field"
- field_name: "rarity"
- field_config: {
    "type": "enum",
    "required": false,
    "description": "Card rarity level",
    "values": ["Common", "Uncommon", "Rare", "Legendary"]
  }
```

**Example: Add new class type**
```
Use update_card_schema tool:
- action: "add_class_value"
- value: "assassin"
```

**Example: Add new card type**
```
Use update_card_schema tool:
- action: "add_card_type"
- value: "Enchantment"
```

### 3. Generate Cards

Now generate your cards. You have two options:

#### Option A: Generate Single Card
```
Use generate_card tool with parameters:
- card_name: "Shadow Strike"
- card_type: "Action - Attack"
- rules_text: "Deal 5 damage to target hero. Go again."
- cost: "2"
- power: "5"
- defense: "3"
- class_type: "ninja"
- artist: "AI Generated"
- year: "2024"
- output_path: "output/cards"
```

#### Option B: Generate Multiple Cards
```
Use generate_cards_batch tool with:
- cards: [array of card objects]
- output_path: "output/cards"
```

Example cards array:
```json
[
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
    "card_name": "Warrior's Shield",
    "card_type": "Action - Defense",
    "rules_text": "Prevent 4 damage.",
    "cost": "1",
    "power": "0",
    "defense": "4",
    "class_type": "warrior"
  }
]
```

#### Option C: Full Automated Workflow (Recommended)
```
Use full_workflow tool with:
- cards: [array of card objects as above]
- output_base_dir: "card_set_output"
- generate_artwork: true
- render_images: true
- stitch_images: true
- tts_format: true
- ai_api: "pollinations"
```

This single tool call will execute all steps automatically!

### 4. Generate AI Artwork (if not using full_workflow)

Generate artwork for your cards using AI:

```
Use generate_ai_artwork tool:
- cards: [
    {
      "card_name": "Shadow Strike",
      "card_type": "Action - Attack",
      "rules_text": "Deal 5 damage. Go again.",
      "class_type": "ninja"
    }
  ]
- output_dir: "generated_art"
- api_type: "pollinations"  // Free service, no API key needed
- width: 1024
- height: 1024
```

**Supported API types:**
- `pollinations`: Free, no API key required (recommended)
- `huggingface`: Requires HF_API_KEY environment variable
- `modelscope`: Requires MODELSCOPE_API_KEY environment variable
- `modelscope_inference`: Requires MODELSCOPE_SDK_TOKEN environment variable

### 5. Render Cards to Images (if not using full_workflow)

Render the JSON cards to final images:

```
Use render_cards_to_images tool:
- json_dir: "output/cards"
- output_dir: "rendered_cards"
- headless: true
- overlay_art_dir: "generated_art"  // If you generated artwork
```

This will:
- Launch CardConjurer in a browser
- Import each JSON file
- Download the rendered card image
- Overlay AI-generated artwork (if provided)

### 6. Stitch Images into Sheets (if not using full_workflow)

Create printable sheets or TTS-compatible decks:

#### For Tabletop Simulator Format
```
Use stitch_card_images tool:
- image_dir: "rendered_cards"
- output_path: "final_output/deck.png"
- tts_mode: true
- preset: "4k"  // Optional: scale output to 4K resolution
```

This creates 10×7 grids with 70 cards per sheet (TTS standard).

#### For Custom Layout
```
Use stitch_card_images tool:
- image_dir: "rendered_cards"
- output_path: "final_output/custom_sheet.png"
- cols: 8
- rows: 4
- preset: "2k"
```

## Complete Example

Here's a complete conversation flow to create a ninja-themed card set:

**User**: "I want to create 5 ninja-themed attack cards for a card game."

**AI Response**:
```
I'll help you create a complete ninja card set! Let me use the full_workflow tool to:
1. Generate 5 ninja attack cards
2. Create AI artwork for each
3. Render them to high-quality images
4. Stitch them into a Tabletop Simulator sheet

[Calls full_workflow tool with 5 ninja card definitions]
```

The full_workflow tool will handle everything and return a complete summary with:
- Generated JSON files location
- Generated artwork location
- Rendered cards location
- Final stitched sheets location

## Best Practices

1. **Start Small**: Test with 1-2 cards before generating large sets
2. **Use Descriptive Names**: Card names help with organizing files
3. **Check Schema First**: Always verify current schema before generating cards
4. **Free AI Services**: Use `pollinations` API for free AI artwork generation
5. **TTS Format**: Use `tts_mode: true` for Tabletop Simulator compatibility
6. **Batch Processing**: Generate multiple cards at once for efficiency
7. **Artwork Prompts**: Let AI auto-generate prompts based on card data for best results

## Troubleshooting

### CardConjurer Rendering Issues
- Ensure Chrome/Chromium is installed
- Try with `headless: false` to see what's happening
- Check that JSON files are valid

### AI Artwork Generation Fails
- Try different API types (pollinations is most reliable)
- Check internet connection
- Reduce batch size (rate limiting)

### Stitching Creates Wrong Layout
- Verify image_dir has the correct images
- Check TTS format requirements (10×7 for TTS)
- Use preset parameter to control output size

## Output Structure

When using `full_workflow`, you'll get this structure:

```
card_workflow_output/
├── card_jsons/          # Generated JSON files
│   ├── Shadow_Strike.json
│   ├── Ninja_Assault.json
│   └── ...
├── generated_art/       # AI-generated artwork
│   ├── Shadow_Strike.png
│   ├── Ninja_Assault.png
│   └── ...
├── rendered_cards/      # Final rendered cards
│   ├── Shadow_Strike.png
│   ├── Ninja_Assault.png
│   └── ...
└── stitched/           # TTS sheets
    ├── deck_sheet_1.png
    └── ...
```

## Advanced Usage

### Custom Templates
```
Use generate_card with custom template:
- template_path: "custom_templates/my_template.json"
- [other card parameters]
```

### Multiple Card Sets
Generate different themed sets by calling the workflow multiple times with different `output_base_dir`:

```
full_workflow with output_base_dir: "ninja_set"
full_workflow with output_base_dir: "warrior_set"
full_workflow with output_base_dir: "wizard_set"
```

### Selective Workflow Steps
Control which steps execute:
```
full_workflow with:
- generate_artwork: false  // Skip artwork generation
- render_images: true      // Still render cards
- stitch_images: true      // Still create sheets
```

## Next Steps

After creating your cards:
1. Import TTS sheets into Tabletop Simulator
2. Print rendered cards for physical gameplay
3. Share card JSONs with others
4. Iterate on card designs by modifying JSONs

## Support

For issues or questions:
- Check the MCP_USAGE_GUIDE.md in the repository
- Review tool schemas with get_card_schema
- Ensure all dependencies are installed (see requirements.txt)
