#!/usr/bin/env python3
"""
APIpedia - 個別APIページ自動生成スクリプト
apis.json を読み込み、各APIの詳細ページを docs/api/{id}/index.html に生成する。
"""

import json
import os
import html

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
DATA_FILE = os.path.join(DOCS_DIR, 'data', 'apis.json')
API_DIR = os.path.join(DOCS_DIR, 'api')

def escape(text):
    return html.escape(str(text)) if text else ''

def get_popularity_class(score):
    if score >= 70: return 'high'
    if score >= 45: return 'medium'
    return 'low'

def get_score_gradient(cls):
    if cls == 'high': return 'var(--color-success), #4ade80'
    if cls == 'medium': return 'var(--color-warning), #fbbf24'
    return '#64748b, #94a3b8'

def get_score_color(cls):
    if cls == 'high': return 'var(--color-success)'
    if cls == 'medium': return 'var(--color-warning)'
    return '#94a3b8'

PRICING_LABEL = {'free': '無料', 'freemium': 'フリーミアム', 'paid': '有料'}
AUTH_LABEL = {'apiKey': 'APIキー', 'oauth2': 'OAuth 2.0', 'bearer': 'Bearer Token', 'none': '認証不要'}
REGION_LABEL = {'japan': '日本', 'global': 'グローバル', 'both': '日本 / グローバル'}
DIFFICULTY_LABEL = {'easy': '初級', 'medium': '中級', 'hard': '上級'}

def generate_page(api, categories, all_apis=None):
    cat = next((c for c in categories if c['id'] == api['category']), None)
    pop = api.get('popularity', {})
    score = pop.get('score', 0)
    pop_cls = get_popularity_class(score)
    gradient = get_score_gradient(pop_cls)
    score_color = get_score_color(pop_cls)

    name = escape(api['name'])
    name_ja = escape(api.get('nameJa', api['name']))
    desc = escape(api['description'])
    cat_name = escape(cat['name']) if cat else ''
    cat_icon = cat.get('icon', '') if cat else ''
    pricing = PRICING_LABEL.get(api.get('pricing', ''), '')
    auth = AUTH_LABEL.get(api.get('auth', ''), '')
    region = REGION_LABEL.get(api.get('region', ''), '')
    difficulty = DIFFICULTY_LABEL.get(api.get('difficulty', ''), '')
    rate_limit = escape(api.get('rateLimit', 'ドキュメント参照'))
    pricing_detail = escape(api.get('pricingDetail', '-'))
    response_fmt = ', '.join(api.get('responseFormat', []))
    sdks = ', '.join(api.get('sdks', []))
    use_cases = api.get('useCases', [])
    tags = api.get('tags', [])

    # JSON-LD structured data
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": api['name'],
        "description": api['description'],
        "url": api.get('url', ''),
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Web API",
        "offers": {
            "@type": "Offer",
            "price": "0" if api.get('pricing') == 'free' else "",
            "priceCurrency": "JPY",
            "description": api.get('pricingDetail', '')
        }
    }, ensure_ascii=False)

    # BreadcrumbList JSON-LD
    breadcrumb_jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://apipedia.dev/"},
            {"@type": "ListItem", "position": 2, "name": "カタログ", "item": "https://apipedia.dev/#catalog"},
            {"@type": "ListItem", "position": 3, "name": api['name'], "item": f"https://apipedia.dev/api/{api['id']}/"}
        ]
    }, ensure_ascii=False)

    # Affiliate link handling
    affiliate = api.get('affiliate', {})
    if affiliate.get('enabled'):
        official_url = escape(affiliate.get('url', api.get('url', '#')))
        official_rel = 'sponsored noopener'
        official_label = escape(affiliate.get('label', '公式サイトへ'))
        affiliate_disclosure = '<p class="affiliate-disclosure">※ アフィリエイトリンクを含みます</p>'
    else:
        official_url = escape(api.get('url', '#'))
        official_rel = 'noopener'
        official_label = '公式サイト'
        affiliate_disclosure = ''

    # Related APIs (same category, excluding self, sorted by popularity, top 5)
    related_html = ''
    if all_apis and cat:
        related = [a for a in all_apis if a['category'] == api['category'] and a['id'] != api['id']]
        related.sort(key=lambda a: (a.get('popularity', {}).get('score', 0)), reverse=True)
        related = related[:5]
        if related:
            items = ''.join(
                f'<a href="../{escape(a["id"])}/" class="related-api-card">'
                f'<div class="related-api-name">{escape(a["name"])}</div>'
                f'<div class="related-api-desc">{escape(a["description"][:60])}{"..." if len(a["description"]) > 60 else ""}</div>'
                f'<div class="related-api-meta">'
                f'<span class="pill pill--{a.get("pricing", "")}">{PRICING_LABEL.get(a.get("pricing", ""), "")}</span>'
                f'{"<span class=score-mini score-mini--" + get_popularity_class(a.get("popularity", {}).get("score", 0)) + ">" + str(a["popularity"]["score"]) + "点</span>" if a.get("popularity", {}).get("score") else ""}'
                f'</div>'
                f'</a>'
                for a in related
            )
            related_html = f'<div class="section-block"><h2 class="section-heading">関連API（{cat_icon} {cat_name}）</h2><div class="related-apis-grid">{items}</div></div>'

    # Build metrics HTML
    metrics_html = ''
    metric_items = []
    if pop.get('monthlyUsers'):
        metric_items.append(f'<div class="metric-card"><div class="metric-label">利用者数</div><div class="metric-value">{escape(pop["monthlyUsers"])}</div></div>')
    if pop.get('monthlyApiCalls'):
        metric_items.append(f'<div class="metric-card"><div class="metric-label">APIコール数</div><div class="metric-value">{escape(pop["monthlyApiCalls"])}</div></div>')
    if pop.get('marketShare'):
        metric_items.append(f'<div class="metric-card"><div class="metric-label">市場ポジション</div><div class="metric-value">{escape(pop["marketShare"])}</div></div>')
    if pop.get('npmDownloads'):
        metric_items.append(f'<div class="metric-card"><div class="metric-label">npm ダウンロード</div><div class="metric-value">{escape(pop["npmDownloads"])}</div></div>')
    if pop.get('githubStars'):
        metric_items.append(f'<div class="metric-card"><div class="metric-label">GitHub Stars</div><div class="metric-value">{escape(pop["githubStars"])}</div></div>')
    if metric_items:
        metrics_html = f'<div class="section-block"><h2 class="section-heading">利用実績・指標</h2><div class="metrics-grid">{"".join(metric_items)}</div></div>'

    # Adopters
    adopters_html = ''
    if pop.get('adopters'):
        chips = ''.join(f'<span class="adopter-chip">{escape(a)}</span>' for a in pop['adopters'])
        adopters_html = f'<div class="section-block"><h2 class="section-heading">主な利用企業・サービス</h2><div class="adopters-wrap">{chips}</div></div>'

    # Sources
    sources_html = ''
    if pop.get('sources'):
        items = ''.join(f'<li><a href="{escape(s["url"])}" target="_blank" rel="noopener" class="source-link">{escape(s["label"])}</a></li>' for s in pop['sources'])
        sources_html = f'<div class="section-block"><h2 class="section-heading">根拠・参照元</h2><ul class="sources-list">{items}</ul></div>'

    # Use cases
    usecases_html = ''
    if use_cases:
        items = ''.join(f'<span class="usecase-tag">{escape(u)}</span>' for u in use_cases)
        usecases_html = f'<div class="section-block"><h2 class="section-heading">ユースケース</h2><div class="usecases-wrap">{items}</div></div>'

    # Tags
    tags_html = ''
    if tags:
        items = ''.join(f'<span class="tag">{escape(t)}</span>' for t in tags)
        tags_html = f'<div class="tags-wrap">{items}</div>'

    return f'''<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
<script>
(function(){{var t=localStorage.getItem('apipedia_theme')||'light';document.documentElement.setAttribute('data-theme',t);}})();
</script>
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} - APIpedia | 日本語APIカタログ</title>
<meta name="description" content="{desc}">
<!-- OGP -->
<meta property="og:type" content="article">
<meta property="og:title" content="{name} — APIpedia | 日本語APIカタログ">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://apipedia.dev/api/{api["id"]}/">
<meta property="og:site_name" content="APIPedia">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{name} — APIpedia">
<meta name="twitter:description" content="{desc}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://apipedia.dev/api/{api["id"]}/">
<script type="application/ld+json">{jsonld}</script>
<script type="application/ld+json">{breadcrumb_jsonld}</script>
<link rel="stylesheet" href="../../assets/style.css">
<style>
  .api-detail {{ max-width: 800px; margin: 0 auto; padding: calc(var(--header-height) + 40px) 24px 80px; }}
  .breadcrumb {{ font-size: 0.82rem; color: var(--text-muted); margin-bottom: 24px; }}
  .breadcrumb a {{ color: var(--text-secondary); }}
  .breadcrumb a:hover {{ color: var(--color-primary); }}
  .api-hero {{ margin-bottom: 32px; }}
  .api-hero h1 {{ font-size: 2rem; font-weight: 800; margin-bottom: 6px; }}
  .api-hero .subtitle {{ font-size: 0.95rem; color: var(--text-muted); margin-bottom: 16px; }}
  .badge-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }}
  .badge {{ display: inline-flex; align-items: center; padding: 4px 14px; font-size: 0.78rem; font-weight: 600; border-radius: var(--radius-pill); }}
  .badge--pricing {{ color: var(--color-primary); background: var(--color-primary-light); }}
  .badge--region {{ color: var(--color-accent); background: var(--color-accent-light); }}
  .badge--category {{ color: var(--color-secondary); background: var(--color-secondary-light); }}
  .badge--difficulty {{ color: var(--text-secondary); background: rgba(255,255,255,0.06); }}
  .badge--featured {{ color: var(--color-warning); background: var(--color-warning-light); }}
  .api-desc {{ font-size: 1rem; color: var(--text-secondary); line-height: 1.8; margin-bottom: 32px; }}
  .score-hero {{ display: flex; align-items: center; gap: 24px; padding: 24px; background: linear-gradient(135deg, rgba(59,130,246,0.06), rgba(139,92,246,0.06)); border: 1px solid var(--border-color); border-radius: var(--radius); margin-bottom: 32px; }}
  .score-number {{ font-size: 3.5rem; font-weight: 800; line-height: 1; }}
  .score-detail {{ flex: 1; }}
  .score-label {{ font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px; }}
  .score-bar-outer {{ width: 100%; height: 10px; background: rgba(255,255,255,0.08); border-radius: 5px; overflow: hidden; }}
  .score-bar-fill {{ height: 100%; border-radius: 5px; }}
  .score-reason {{ font-size: 0.88rem; color: var(--text-secondary); margin-top: 10px; line-height: 1.7; }}
  .section-block {{ margin-bottom: 32px; }}
  .section-heading {{ font-size: 1.05rem; font-weight: 700; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--border-color); display: flex; align-items: center; gap: 8px; }}
  .detail-text {{ font-size: 0.9rem; color: var(--text-secondary); line-height: 1.8; padding: 16px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 10px; }}
  .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }}
  .metric-card {{ padding: 16px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 10px; }}
  .metric-label {{ font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
  .metric-value {{ font-size: 0.9rem; font-weight: 600; color: var(--text-primary); }}
  .adopters-wrap {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .adopter-chip {{ padding: 6px 14px; font-size: 0.82rem; font-weight: 500; color: var(--text-secondary); background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-pill); }}
  .sources-list {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
  .source-link {{ display: block; padding: 12px 16px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 10px; color: var(--color-primary); font-size: 0.85rem; font-weight: 500; transition: all var(--transition); }}
  .source-link:hover {{ border-color: var(--color-primary); background: var(--color-primary-light); }}
  .spec-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .spec-item {{ padding: 14px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 10px; }}
  .spec-item .label {{ font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 4px; }}
  .spec-item .value {{ font-size: 0.88rem; font-weight: 600; color: var(--text-primary); }}
  .spec-item--full {{ grid-column: 1 / -1; }}
  .usecases-wrap, .tags-wrap {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .usecase-tag {{ padding: 6px 14px; font-size: 0.82rem; color: var(--color-accent); background: var(--color-accent-light); border-radius: var(--radius-pill); }}
  .related-apis-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }}
  .related-api-card {{ display: block; padding: 16px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 10px; text-decoration: none; transition: all 0.2s; }}
  .related-api-card:hover {{ border-color: var(--color-primary); transform: translateY(-2px); }}
  .related-api-name {{ font-size: 0.9rem; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }}
  .related-api-desc {{ font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 8px; }}
  .related-api-meta {{ display: flex; align-items: center; gap: 8px; }}
  .pill {{ display: inline-block; padding: 2px 8px; font-size: 0.7rem; font-weight: 600; border-radius: 20px; }}
  .pill--free {{ color: var(--color-success); background: var(--color-success-light); }}
  .pill--freemium {{ color: var(--color-primary); background: var(--color-primary-light); }}
  .pill--paid {{ color: var(--color-warning); background: var(--color-warning-light); }}
  .score-mini {{ font-size: 0.75rem; font-weight: 700; }}
  .score-mini--high {{ color: var(--color-success); }}
  .score-mini--medium {{ color: var(--color-warning); }}
  .score-mini--low {{ color: #94a3b8; }}
  .action-buttons {{ display: flex; gap: 12px; margin-top: 40px; }}
  .action-buttons .btn {{ flex: 1; padding: 14px 24px; font-size: 0.95rem; text-align: center; }}
  @media (max-width: 768px) {{
    .api-hero h1 {{ font-size: 1.5rem; }}
    .score-hero {{ flex-direction: column; align-items: flex-start; gap: 16px; }}
    .score-number {{ font-size: 2.5rem; }}
    .spec-grid {{ grid-template-columns: 1fr; }}
    .action-buttons {{ flex-direction: column; }}
  }}
</style>
</head>
<body>

<header class="site-header">
  <div class="container">
    <a href="../../index.html" class="site-header__logo"><span>APIpedia</span></a>
    <nav class="site-header__nav">
      <a href="../../index.html#ranking" class="nav-link">ランキング</a>
      <a href="../../index.html#catalog" class="nav-link">カタログ</a>
      <a href="../../compare.html" class="nav-link">比較表</a>
      <a href="../../guides/" class="nav-link">ガイド</a>
      <a href="../../lean-canvas.html" class="nav-link">コンセプト</a>
    </nav>
  </div>
</header>

<main class="api-detail">
  <div class="breadcrumb">
    <a href="../../index.html">APIpedia</a> &rsaquo;
    <a href="../../index.html#catalog">カタログ</a> &rsaquo;
    {name}
  </div>

  <div class="api-hero">
    <h1>{name}</h1>
    {f'<div class="subtitle">{name_ja}</div>' if name_ja != name else ''}
    <div class="badge-row">
      <span class="badge badge--pricing">{pricing}</span>
      <span class="badge badge--region">{region}</span>
      {f'<span class="badge badge--category">{cat_icon} {cat_name}</span>' if cat else ''}
      <span class="badge badge--difficulty">{difficulty}</span>
      {'<span class="badge badge--featured">&#x2B50; 注目</span>' if api.get('featured') else ''}
    </div>
  </div>

  <p class="api-desc">{desc}</p>

  {f"""<div class="score-hero">
    <div class="score-number" style="color:{score_color};">{score}</div>
    <div class="score-detail">
      <div class="score-label">人気スコア（100点満点）</div>
      <div class="score-bar-outer"><div class="score-bar-fill" style="width:{score}%;background:linear-gradient(90deg,{gradient});"></div></div>
      {f'<div class="score-reason">{escape(pop.get("reason", ""))}</div>' if pop.get('reason') else ''}
    </div>
  </div>""" if score else ''}

  {f'<div class="section-block"><h2 class="section-heading">詳細分析</h2><div class="detail-text">{escape(pop.get("detail", ""))}</div></div>' if pop.get('detail') else ''}

  {metrics_html}
  {adopters_html}
  {sources_html}

  <div class="section-block">
    <h2 class="section-heading">API仕様</h2>
    <div class="spec-grid">
      <div class="spec-item"><div class="label">認証方式</div><div class="value">{auth}</div></div>
      <div class="spec-item"><div class="label">レスポンス形式</div><div class="value">{response_fmt}</div></div>
      <div class="spec-item"><div class="label">レート制限</div><div class="value">{rate_limit}</div></div>
      <div class="spec-item"><div class="label">料金</div><div class="value">{pricing_detail}</div></div>
      {f'<div class="spec-item spec-item--full"><div class="label">SDK</div><div class="value">{sdks}</div></div>' if sdks else ''}
    </div>
  </div>

  {usecases_html}

  {f'<div class="section-block"><h2 class="section-heading">タグ</h2>{tags_html}</div>' if tags else ''}

  {related_html}

  <div class="action-buttons">
    <a href="{escape(api.get('docsUrl') or api.get('url', '#'))}" target="_blank" rel="noopener" class="btn btn--primary">ドキュメントを見る</a>
    <a href="{official_url}" target="_blank" rel="{official_rel}" class="btn btn--ghost">{official_label}</a>
  </div>
  {affiliate_disclosure}
</main>

<footer class="site-footer">
  <div class="container">
    <div class="site-footer__inner">
      <div>
        <div class="site-footer__brand">APIpedia</div>
        <div class="site-footer__text">日本語APIカタログ</div>
      </div>
      <div class="site-footer__links">
        <a href="../../index.html">トップ</a>
        <a href="../../compare.html">比較表</a>
        <a href="../../guides/">ガイド</a>
        <a href="../../lean-canvas.html">コンセプト</a>
      </div>
    </div>
    <div class="site-footer__copyright">&copy; 2026 APIpedia. All rights reserved.</div>
  </div>
</footer>

</body>
</html>'''


def generate_sitemap(apis):
    base_url = 'https://apipedia.dev'
    urls = [
        f'  <url><loc>{base_url}/</loc><priority>1.0</priority><changefreq>weekly</changefreq></url>',
        f'  <url><loc>{base_url}/compare.html</loc><priority>0.8</priority><changefreq>weekly</changefreq></url>',
        f'  <url><loc>{base_url}/lean-canvas.html</loc><priority>0.5</priority><changefreq>monthly</changefreq></url>',
        f'  <url><loc>{base_url}/strategy.html</loc><priority>0.5</priority><changefreq>monthly</changefreq></url>',
        f'  <url><loc>{base_url}/guides/</loc><priority>0.8</priority><changefreq>weekly</changefreq></url>',
        f'  <url><loc>{base_url}/guides/payment-api-comparison.html</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>',
        f'  <url><loc>{base_url}/guides/auth-api-comparison.html</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>',
        f'  <url><loc>{base_url}/guides/ai-api-comparison.html</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>',
        f'  <url><loc>{base_url}/guides/notification-api-comparison.html</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>',
        f'  <url><loc>{base_url}/guides/maps-api-comparison.html</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>',
    ]
    for api in apis:
        urls.append(f'  <url><loc>{base_url}/api/{api["id"]}/</loc><priority>0.7</priority><changefreq>weekly</changefreq></url>')

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
{chr(10).join(urls)}
</urlset>'''


def generate_robots():
    return '''User-agent: *
Allow: /
Sitemap: https://apipedia.dev/sitemap.xml
'''


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    apis = data['apis']
    categories = data['categories']

    generated = 0
    for api in apis:
        api_dir = os.path.join(API_DIR, api['id'])
        os.makedirs(api_dir, exist_ok=True)
        page_html = generate_page(api, categories, all_apis=apis)
        page_path = os.path.join(api_dir, 'index.html')
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(page_html)
        generated += 1

    # Generate sitemap.xml
    sitemap_path = os.path.join(DOCS_DIR, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(generate_sitemap(apis))

    # Generate robots.txt
    robots_path = os.path.join(DOCS_DIR, 'robots.txt')
    with open(robots_path, 'w', encoding='utf-8') as f:
        f.write(generate_robots())

    print(f'Generated {generated} API pages')
    print(f'Generated sitemap.xml ({len(apis)} API URLs)')
    print(f'Generated robots.txt')


if __name__ == '__main__':
    main()
