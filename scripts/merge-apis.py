#!/usr/bin/env python3
"""
APIpedia - APIデータマージスクリプト
新APIデータ（JSON配列）をapis.jsonにマージする。
重複IDはスキップし、新カテゴリがあれば自動追加する。
"""

import json
import os
import sys
import re

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
DATA_FILE = os.path.join(DOCS_DIR, 'data', 'apis.json')

CATEGORY_DEFINITIONS = {
    "cms": {"id": "cms", "name": "CMS・コンテンツ管理", "icon": "📝"},
    "crm": {"id": "crm", "name": "CRM・顧客管理", "icon": "👥"},
    "nocode": {"id": "nocode", "name": "ノーコード・自動化", "icon": "⚡"},
    "iot": {"id": "iot", "name": "IoT・ハードウェア", "icon": "📡"},
    "travel": {"id": "travel", "name": "旅行・交通", "icon": "✈️"},
    "food": {"id": "food", "name": "食・グルメ", "icon": "🍽️"},
    "logistics": {"id": "logistics", "name": "物流・配送", "icon": "📦"},
    "realestate": {"id": "realestate", "name": "不動産", "icon": "🏠"},
    "education": {"id": "education", "name": "教育・学習", "icon": "📚"},
    "blockchain": {"id": "blockchain", "name": "ブロックチェーン・Web3", "icon": "⛓️"},
    "communication": {"id": "communication", "name": "コミュニケーション", "icon": "📹"},
    "security": {"id": "security", "name": "セキュリティ", "icon": "🛡️"},
}

def extract_json_from_file(filepath):
    """ファイルからJSON配列を抽出する（```json ブロック対応）"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Try direct JSON parse first
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json blocks
    matches = re.findall(r'```json\s*\n([\s\S]*?)\n```', content)
    for match in matches:
        try:
            data = json.loads(match)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            continue

    # Try extracting any JSON array
    matches = re.findall(r'\[\s*\{[\s\S]*?\}\s*\]', content)
    for match in matches:
        try:
            data = json.loads(match)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            continue

    return []

def merge_apis(new_apis_files):
    """新APIデータをapis.jsonにマージ"""
    # Load existing data
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    existing_ids = {api['id'] for api in data['apis']}
    existing_cat_ids = {cat['id'] for cat in data['categories']}

    added = 0
    skipped = 0
    new_categories = 0

    for filepath in new_apis_files:
        new_apis = extract_json_from_file(filepath)
        print(f"  {os.path.basename(filepath)}: {len(new_apis)} APIs found")

        for api in new_apis:
            if not api.get('id'):
                continue

            if api['id'] in existing_ids:
                skipped += 1
                continue

            # Add new category if needed
            cat_id = api.get('category', '')
            if cat_id and cat_id not in existing_cat_ids:
                if cat_id in CATEGORY_DEFINITIONS:
                    data['categories'].append(CATEGORY_DEFINITIONS[cat_id])
                    existing_cat_ids.add(cat_id)
                    new_categories += 1
                    print(f"    + New category: {cat_id}")
                else:
                    print(f"    ! Unknown category: {cat_id}")

            data['apis'].append(api)
            existing_ids.add(api['id'])
            added += 1

    # Update metadata
    data['metadata']['totalApis'] = len(data['apis'])
    data['metadata']['totalCategories'] = len(data['categories'])
    data['metadata']['version'] = '3.0.0'

    # Save
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nResult: +{added} APIs added, {skipped} skipped (duplicates)")
    print(f"New categories: {new_categories}")
    print(f"Total: {len(data['apis'])} APIs, {len(data['categories'])} categories")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python merge-apis.py <file1.json> [file2.json ...]")
        sys.exit(1)

    merge_apis(sys.argv[1:])
