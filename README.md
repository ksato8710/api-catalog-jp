# APIPedia (`api-catalog-jp`)

日本語で API を探して比較できる、静的サイト構成の API カタログです。  
公開物は `docs/` 配下に生成されます。

## ディレクトリ

- `docs/`: 公開サイト本体（`index.html`、`api/*`、`guides/*`、`data/*`）
- `scripts/`: データ検証・ページ生成・データマージ用スクリプト
- `.github/workflows/`: CI/CD（検証、GitHub Pages デプロイ）

## 必要環境

- Python 3.11 以上

## ローカル実行

```bash
# 1) データ整合性チェック
python3 scripts/validate-schema.py

# 2) API詳細ページ・sitemap・robots を再生成
python3 scripts/generate-pages.py

# 3) ローカル確認
python3 -m http.server 8000 --directory docs
```

ブラウザで `http://localhost:8000` を開いて確認します。

## APIデータ追加フロー

```bash
# 例: 新規JSONをマージ
python3 scripts/merge-apis.py data-batch1.json

# 検証と生成
python3 scripts/validate-schema.py
python3 scripts/generate-pages.py
```

上記実行後、`docs/data/apis.json` と `docs/api/*` の差分をコミットします。

## GitHub Actions

- `/.github/workflows/ci.yml`
  - `push` / `pull_request` で JSON 構文チェック、スキーマ検証、生成物差分チェックを実行
- `/.github/workflows/deploy.yml`
  - `main` への push 時に GitHub Pages へデプロイ

