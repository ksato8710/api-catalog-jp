#!/usr/bin/env python3
"""
APIpedia - apis.json スキーマバリデーション
CI/CDパイプラインでデータの整合性を検証する。
"""

import json
import os
import sys

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'docs', 'data', 'apis.json')

VALID_PRICING = {'free', 'freemium', 'paid'}
VALID_AUTH = {'apiKey', 'oauth2', 'bearer', 'none'}
VALID_REGION = {'japan', 'global', 'both'}
VALID_DIFFICULTY = {'easy', 'medium', 'hard'}

REQUIRED_METADATA_FIELDS = {'version', 'lastUpdated', 'totalApis', 'totalCategories'}
REQUIRED_API_FIELDS = {'id', 'name', 'description', 'url', 'category', 'pricing', 'auth', 'region', 'popularity'}


def validate(data):
    errors = []

    # --- metadata ---
    metadata = data.get('metadata')
    if not metadata:
        errors.append('metadata が存在しません')
        return errors

    for field in REQUIRED_METADATA_FIELDS:
        if field not in metadata:
            errors.append(f'metadata.{field} が不足しています')

    categories = data.get('categories', [])
    apis = data.get('apis', [])
    category_ids = {c['id'] for c in categories}

    # totalApis / totalCategories の整合性
    if metadata.get('totalApis') != len(apis):
        errors.append(
            f'metadata.totalApis ({metadata.get("totalApis")}) が実データ ({len(apis)}) と不一致'
        )
    if metadata.get('totalCategories') != len(categories):
        errors.append(
            f'metadata.totalCategories ({metadata.get("totalCategories")}) が実データ ({len(categories)}) と不一致'
        )

    # --- 重複IDチェック ---
    seen_ids = set()
    for api in apis:
        api_id = api.get('id', '<unknown>')
        if api_id in seen_ids:
            errors.append(f'重複ID: {api_id}')
        seen_ids.add(api_id)

    # --- 各APIバリデーション ---
    for i, api in enumerate(apis):
        api_id = api.get('id', f'<index {i}>')
        prefix = f'apis[{api_id}]'

        # 必須フィールド
        for field in REQUIRED_API_FIELDS:
            if field not in api:
                errors.append(f'{prefix}: 必須フィールド "{field}" が不足')

        # category がカテゴリ一覧に存在するか
        if api.get('category') and api['category'] not in category_ids:
            errors.append(f'{prefix}: category "{api["category"]}" が categories に未定義')

        # pricing
        if api.get('pricing') and api['pricing'] not in VALID_PRICING:
            errors.append(f'{prefix}: pricing "{api["pricing"]}" は不正 (有効値: {VALID_PRICING})')

        # auth
        if api.get('auth') and api['auth'] not in VALID_AUTH:
            errors.append(f'{prefix}: auth "{api["auth"]}" は不正 (有効値: {VALID_AUTH})')

        # region
        if api.get('region') and api['region'] not in VALID_REGION:
            errors.append(f'{prefix}: region "{api["region"]}" は不正 (有効値: {VALID_REGION})')

        # difficulty (任意だが存在する場合はバリデーション)
        if 'difficulty' in api and api['difficulty'] not in VALID_DIFFICULTY:
            errors.append(f'{prefix}: difficulty "{api["difficulty"]}" は不正 (有効値: {VALID_DIFFICULTY})')

        # popularity
        pop = api.get('popularity')
        if pop:
            score = pop.get('score')
            if score is not None:
                if not isinstance(score, (int, float)) or score < 0 or score > 100:
                    errors.append(f'{prefix}: popularity.score ({score}) は 0-100 の範囲で指定')

            sources = pop.get('sources', [])
            if len(sources) < 1:
                errors.append(f'{prefix}: popularity.sources が0件（最低1件のURLが必要）')
            if len(sources) < 2:
                # 警告レベル（エラーにはしないがログに出す）
                print(f'  WARNING: {prefix}: popularity.sources が1件のみ（理想は2件以上）')

            for j, src in enumerate(sources):
                if not src.get('url'):
                    errors.append(f'{prefix}: popularity.sources[{j}] に url がありません')

    return errors


def main():
    print('=== APIpedia Schema Validation ===')
    print(f'Data file: {os.path.abspath(DATA_FILE)}')

    if not os.path.exists(DATA_FILE):
        print(f'ERROR: {DATA_FILE} が見つかりません')
        sys.exit(1)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    errors = validate(data)

    api_count = len(data.get('apis', []))
    cat_count = len(data.get('categories', []))
    print(f'APIs: {api_count}, Categories: {cat_count}')

    if errors:
        print(f'\nERROR: {len(errors)} 件のバリデーションエラー:')
        for err in errors:
            print(f'  - {err}')
        sys.exit(1)

    print('OK: すべてのバリデーションに合格しました')
    sys.exit(0)


if __name__ == '__main__':
    main()
