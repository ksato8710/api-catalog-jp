# API Catalog JP (APIPedia)

**日本語で API を探して比較できる静的 API カタログサイト**

[![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-222?logo=github)](https://api-catalog-jp.craftgarden.studio)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/ksato8710/api-catalog-jp/actions)

> **Live**: [api-catalog-jp.craftgarden.studio](https://api-catalog-jp.craftgarden.studio)

![API Catalog JP Screenshot](screenshot.png)

---

## 概要

日本語で利用できる API の情報は各社のドキュメントや英語のリソースに散在しており、日本語で横断的に検索・比較できる場所がありません。API Catalog JP は、日本語で API を探し、機能・料金・制限を比較できる**静的カタログサイト**を提供します。JSON データから静的 HTML を自動生成し、GitHub Pages でホスティングする軽量アーキテクチャです。

- **日本語 API 検索** -- カテゴリ・キーワードで API を横断検索
- **API 比較機能** -- 複数 API の機能・料金・制限を並べて比較
- **静的サイト生成** -- JSON データから HTML ページを自動生成、高速表示
- **スキーマ検証** -- JSON Schema によるデータ整合性チェック
- **バッチデータインポート** -- `data-batch*.json` で新規 API データを一括追加
- **CI/CD 完備** -- push ごとにバリデーション、main マージで自動デプロイ
- **ガイド記事** -- API 活用ガイドの掲載

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| Language | Python 3.11+ |
| Frontend | Static HTML / CSS / JavaScript |
| Hosting | GitHub Pages |
| CI/CD | GitHub Actions |
| Data Format | JSON (Schema-validated) |
| SEO | sitemap.xml / robots.txt 自動生成 |

## セットアップ

### 前提条件

- Python 3.11+
- Git

### インストール

```bash
git clone https://github.com/ksato8710/api-catalog-jp.git
cd api-catalog-jp
# pip install は不要（Python 標準ライブラリのみ使用）
```

追加パッケージのインストールは不要です。

### 環境変数

特に必要ありません。GitHub Pages のデプロイは GitHub Actions が自動で行います。

### 起動（dev サーバー）

```bash
# 1. データ整合性チェック
python3 scripts/validate-schema.py

# 2. API 詳細ページ・sitemap・robots を生成
python3 scripts/generate-pages.py

# 3. ローカル dev サーバー起動
python3 -m http.server 8000 --directory docs
```

ブラウザで [http://localhost:8000](http://localhost:8000) を開いて確認。

## アーキテクチャ

### データフロー

```
data-batch*.json  -->  merge-apis.py  -->  docs/data/apis.json
                                                │
                                      validate-schema.py（検証）
                                                │
                                      generate-pages.py（生成）
                                                │
                                                ▼
                                      docs/（公開サイト）
                                                │
                                      GitHub Actions（CI/CD）
                                                │
                                                ▼
                                          GitHub Pages
```

### ディレクトリ構成

```
api-catalog-jp/
├── docs/                           # 公開サイト本体（GitHub Pages）
│   ├── index.html                  #   トップページ（検索 + カテゴリ一覧）
│   ├── api/                        #   API 個別ページ（自動生成）
│   │   ├── openai.html
│   │   ├── stripe-jp.html
│   │   └── ...
│   ├── guides/                     #   API 活用ガイド
│   │   └── *.html
│   ├── data/
│   │   └── apis.json               #   マスターデータ（生成元）
│   ├── sitemap.xml                 #   サイトマップ（自動生成）
│   └── robots.txt                  #   robots.txt（自動生成）
├── scripts/
│   ├── validate-schema.py          #   JSON Schema バリデーション
│   ├── generate-pages.py           #   API ページ + sitemap 生成
│   └── merge-apis.py               #   バッチデータのマージ
├── data-batch1.json                #   API データソース（バッチ 1）
├── data-batch2.json                #   API データソース（バッチ 2）
├── .github/
│   └── workflows/
│       ├── ci.yml                  #   CI（構文チェック + スキーマ検証 + 差分チェック）
│       └── deploy.yml              #   GitHub Pages 自動デプロイ
└── README.md
```

### 主要ファイル

| ファイル | 役割 |
|---------|------|
| `docs/index.html` | トップページ -- API 検索とカテゴリ一覧 |
| `docs/data/apis.json` | 全 API のマスターデータ |
| `scripts/validate-schema.py` | JSON Schema によるデータ整合性チェック |
| `scripts/generate-pages.py` | `apis.json` から API 詳細ページ・sitemap・robots を生成 |
| `scripts/merge-apis.py` | 新規バッチデータを `apis.json` にマージ |
| `.github/workflows/ci.yml` | CI -- JSON 構文チェック、スキーマ検証、生成物差分チェック |
| `.github/workflows/deploy.yml` | `main` push 時に GitHub Pages へ自動デプロイ |

## コマンド一覧

| コマンド | 説明 |
|---------|------|
| `python3 scripts/validate-schema.py` | JSON データのスキーマ検証 |
| `python3 scripts/generate-pages.py` | API ページ・sitemap・robots 生成 |
| `python3 scripts/merge-apis.py data-batch1.json` | 新規データをマージ |
| `python3 -m http.server 8000 --directory docs` | ローカルプレビューサーバー起動 |

### API データ追加フロー

```bash
# 1. 新規 JSON をマージ
python3 scripts/merge-apis.py data-batch2.json

# 2. 検証
python3 scripts/validate-schema.py

# 3. ページ再生成
python3 scripts/generate-pages.py

# 4. 差分をコミット
git add docs/
git commit -m "feat: add new API entries"
git push origin main
# -> deploy.yml が GitHub Pages に自動デプロイ
```

## デプロイ

GitHub Pages で自動デプロイ。`main` ブランチへの push で `deploy.yml` が実行されます。

- **本番 URL**: https://api-catalog-jp.craftgarden.studio
- **ホスティング**: GitHub Pages

### CI パイプライン (ci.yml)

| ステップ | 内容 |
|---------|------|
| JSON 構文チェック | `data-batch*.json` と `docs/data/apis.json` の構文検証 |
| スキーマ検証 | `validate-schema.py` による整合性チェック |
| 生成物差分チェック | `generate-pages.py` 実行後の差分がないことを確認 |

## テスト

GitHub Actions による CI パイプラインで、以下のテストを自動実行しています。

```bash
# ローカルでの検証
python3 scripts/validate-schema.py
python3 scripts/generate-pages.py
```

## 関連プロジェクト

[craftgarden.studio](https://craftgarden.studio) エコシステムの一部として、他プロジェクトと連携しています。

| プロジェクト | 説明 |
|-------------|------|
| [product-hub](https://github.com/ksato8710/product-hub) | プロダクトエコシステム管理ダッシュボード |
| [conf-hub](https://github.com/ksato8710/conf-hub) | 技術カンファレンス集約サービス |
| [ai-solo-craft](https://github.com/ksato8710/ai-solo-craft) | AI ソロビルダー向けニュースキュレーション |

## 開発ガイド

API データの追加は `data-batch*.json` 形式で PR を送ってください。Issue や Pull Request は歓迎です。

## 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-02 | 初期リリース -- スキーマ検証、ページ生成、CI/CD パイプライン構築 |

## ロードマップ

- [ ] API 比較ページの強化（料金計算シミュレーター）
- [ ] カテゴリ別ランキング
- [ ] API 変更検知（定期クロール -> 差分通知）
- [ ] ユーザー投稿による API 情報の追加・更新
- [ ] 英語版サイトの生成
- [ ] API ステータス監視ダッシュボード

## ライセンス

MIT
