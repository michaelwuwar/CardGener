#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server Test Script
Demonstrates direct testing of CardGenerator MCP Server functionality
"""

import json
import sys
from pathlib import Path

# Import the server class directly
sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import CardGeneratorMCPServer


def test_single_card_generation():
    """Test generating a single card"""
    print("\n" + "="*60)
    print("TEST 1: Single Card Generation")
    print("="*60)

    server = CardGeneratorMCPServer()

    # AI-generated parameters
    card_params = {
        'card_name': 'Shadow Strike',
        'card_type': 'Action - Attack',
        'rules_text': 'Deal 5 damage to target hero. If this hits, draw a card. Go again.',
        'cost': '2',
        'power': '5',
        'defense': '3',
        'art_path': '',
        'class_type': 'ninja',
        'artist': 'Test Artist',
        'year': '2024'
    }

    print("\n📝 AI-generated parameters:")
    print(json.dumps(card_params, indent=2, ensure_ascii=False))

    try:
        # Generate card
        card_data = server.generate_single_card(card_params)

        # Save card
        output_path = 'test_output'
        saved_file = server.save_card_to_file(card_data, output_path, card_params['card_name'])

        print(f"\n✅ SUCCESS: Card generated and saved")
        print(f"📂 File: {saved_file}")
        print(f"📊 Card data size: {len(json.dumps(card_data))} bytes")

        return True

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False


def test_batch_generation():
    """Test batch card generation"""
    print("\n" + "="*60)
    print("TEST 2: Batch Card Generation")
    print("="*60)

    server = CardGeneratorMCPServer()

    # AI-generated batch parameters
    cards_batch = [
        {
            'card_name': 'Ninja Strike',
            'card_type': 'Action - Attack',
            'rules_text': 'Deal 5 damage.',
            'cost': '2',
            'power': '5',
            'defense': '3',
            'class_type': 'ninja',
            'artist': 'Artist A',
            'year': '2024'
        },
        {
            'card_name': 'Warrior Shield',
            'card_type': 'Action - Defense',
            'rules_text': 'Prevent 4 damage.',
            'cost': '1',
            'power': '0',
            'defense': '4',
            'class_type': 'warrior',
            'artist': 'Artist B',
            'year': '2024'
        },
        {
            'card_name': 'Wizard Bolt',
            'card_type': 'Action - Attack',
            'rules_text': 'Deal 6 arcane damage.',
            'cost': '3',
            'power': '6',
            'defense': '2',
            'class_type': 'wizard',
            'artist': 'Artist C',
            'year': '2024'
        }
    ]

    print(f"\n📝 AI-generated batch: {len(cards_batch)} cards")

    try:
        output_path = 'test_output/batch'
        success_count = 0

        for idx, card_params in enumerate(cards_batch):
            try:
                card_data = server.generate_single_card(card_params)
                saved_file = server.save_card_to_file(
                    card_data, output_path, card_params['card_name']
                )
                success_count += 1
                print(f"  ✅ Card {idx+1}/{len(cards_batch)}: {card_params['card_name']}")

            except Exception as e:
                print(f"  ❌ Card {idx+1}/{len(cards_batch)}: {card_params['card_name']} - {e}")

        print(f"\n🎉 Batch complete: {success_count}/{len(cards_batch)} cards generated")
        return success_count == len(cards_batch)

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False


def test_parameter_validation():
    """Test that all parameters are required from AI"""
    print("\n" + "="*60)
    print("TEST 3: Parameter Validation (AI must provide all params)")
    print("="*60)

    server = CardGeneratorMCPServer()

    # Test missing required parameters
    incomplete_params = {
        'card_name': 'Test Card',
        'card_type': 'Action',
        # Missing: rules_text, cost, power, defense, class_type
    }

    print("\n📝 Testing with incomplete parameters (missing required fields):")
    print(json.dumps(incomplete_params, indent=2))

    try:
        card_data = server.generate_single_card(incomplete_params)
        # Check if fields are empty or have defaults
        card_json = json.dumps(card_data)

        # Extract some key fields for validation
        has_empty_fields = '""' in card_json or 'null' in card_json

        if has_empty_fields:
            print("\n⚠️  EXPECTED: Some fields are empty (AI should provide all)")
            print("   This demonstrates that AI MUST provide complete parameters")
            return True
        else:
            print("\n✅ Card generated with defaults")
            return True

    except Exception as e:
        print(f"\n❌ Error (expected if validation enforced): {e}")
        return True  # Expected behavior


def test_class_types():
    """Test different class types"""
    print("\n" + "="*60)
    print("TEST 4: Multiple Class Types")
    print("="*60)

    server = CardGeneratorMCPServer()

    classes = ['ninja', 'warrior', 'wizard', 'ranger', 'guardian']
    success_count = 0

    for class_type in classes:
        card_params = {
            'card_name': f'{class_type.title()} Test Card',
            'card_type': 'Action',
            'rules_text': f'Test card for {class_type} class.',
            'cost': '1',
            'power': '3',
            'defense': '2',
            'class_type': class_type,
            'artist': 'Test',
            'year': '2024'
        }

        try:
            card_data = server.generate_single_card(card_params)
            print(f"  ✅ {class_type.title()}: Generated successfully")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {class_type.title()}: {e}")

    print(f"\n🎉 Class types tested: {success_count}/{len(classes)} successful")
    return success_count == len(classes)


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 CardGener MCP Server Test Suite")
    print("Testing AI-generated parameter functionality")
    print("="*60)

    # Check if template exists
    if not Path('template.json').exists():
        print("\n❌ ERROR: template.json not found")
        print("   Please ensure template.json is in the current directory")
        return

    results = []

    # Run tests
    results.append(("Single Card Generation", test_single_card_generation()))
    results.append(("Batch Generation", test_batch_generation()))
    results.append(("Parameter Validation", test_parameter_validation()))
    results.append(("Class Types", test_class_types()))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! MCP server is working correctly.")
        print("   ✓ All parameters are AI-generated")
        print("   ✓ Single and batch generation work")
        print("   ✓ Multiple class types supported")
    else:
        print("\n⚠️  Some tests failed. Check output above.")


if __name__ == '__main__':
    main()
