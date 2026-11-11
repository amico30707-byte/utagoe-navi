#!/usr/bin/env python3
"""Build the static site for utagoe-navi.jp into /home/claude/site"""
import json as _json_ncon
NCON=len(_json_ncon.load(open('/home/claude/utagoe-navi/_build/concours/contests-final.json')))
import re, os, json, csv, html, shutil, datetime

ROOT = '/home/claude'
OUT = f'{ROOT}/site'
DOMAIN = 'https://utagoe-navi.jp'
import datetime as _dt, os as _os
TODAY = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=9)).date().isoformat()
LASTMOD = {}
SITE = 'うたごえナビ'

if os.path.exists(OUT):
    for n in os.listdir(OUT):
        if n == '.git':
            continue
        p = os.path.join(OUT, n)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
os.makedirs(OUT, exist_ok=True)

def esc(s):
    return html.escape(s, quote=True)

CATS = {
    'contest': 'コンクール・発表の場', 'lesson': '歌の習い事・教室えらび',
    'practice': '練習・発声のコツ', 'prepare': '本番の準備（動画・衣装・持ち物）',
    'money': 'お礼・費用', 'heart': '心のこと・声かけ'}
TAGS = {'youji': '幼児', 'shogakusei': '小学生', 'chugakusei': '中学生', 'koukousei': '高校生',
        'daigakusei': '大学生', 'otona': 'おとな', 'senior': 'シニア', 'douyou': '童謡',
        'seigaku': '声楽', 'musical': 'ミュージカル', 'gassho': '合唱', 'voitore': 'ボイトレ'}

sitemap = []

CSS = open(f'{ROOT}/site-build/site.css').read()

def page(path, title, desc, body, *, h1_in_body=True, jsonld=None, noindex=False, full_title=None):
    url = DOMAIN + path
    t = full_title or (f'{title}｜{SITE}' if title != SITE else SITE)
    ld = ''
    if jsonld:
        ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + '</script>'
    doc = f'''<!doctype html>
<html lang="ja">
<head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2LQJEDZ04M"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-2LQJEDZ04M');</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(t)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<meta property="og:type" content="{'website' if path == '/' else 'article'}">
<meta property="og:title" content="{esc(t)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:image" content="https://utagoe-navi.jp/assets/ogp.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
{ld}
</head>
<body>
<header class="sh">
<div class="sh-in">
<a class="sh-logo" href="/"><svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><circle cx="15" cy="15" r="14" fill="#B9530F"/><path d="M12 20.5a2.5 2.5 0 1 1-2.5-2.5c.9 0 1.7.4 2.5 1V9l9-2v10.5a2.5 2.5 0 1 1-2.5-2.5c.9 0 1.7.4 2.5 1" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg><span>{SITE}</span></a>
<nav class="sh-nav" aria-label="メインメニュー">
<a href="/kyoshitsu/">教室さがし</a><a href="/concours/">コンクール</a><a href="/grandprix/">グランプリ</a><a href="/articles/">記事</a>
</nav>
</div>
</header>
<main>
{body}
</main>
<footer class="sf">
<div class="sf-in">
<p class="sf-logo">{SITE}</p>
<p class="sf-links"><a href="/kyoshitsu/">歌の教室さがし</a><a href="/concours/">コンクールさがし</a><a href="/grandprix/">こどもの歌声グランプリ</a><a href="/articles/">記事一覧</a><a href="/about/">運営者について</a><a href="/contact/">お問い合わせ・掲載のご相談</a></p>
<p class="sf-pr">本サイトはアフィリエイト広告（PR）をふくみます。</p>
<p class="sf-c">&copy; 2026 株式会社Bright Future Family</p>
</div>
</footer>
</body>
</html>
'''
    d = OUT + path
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.html'), 'w') as f:
        f.write(doc)
    if not noindex:
        sitemap.append(url)

def crumbs(items):
    """items: list of (name, path) ; last has path None"""
    h = '<nav class="bc" aria-label="パンくずリスト"><a href="/">トップ</a>'
    ld = [{"@type": "ListItem", "position": 1, "name": "トップ", "item": DOMAIN + '/'}]
    for i, (n, p) in enumerate(items, start=2):
        if p:
            h += f' <span aria-hidden="true">›</span> <a href="{p}">{esc(n)}</a>'
            ld.append({"@type": "ListItem", "position": i, "name": n, "item": DOMAIN + p})
        else:
            h += f' <span aria-hidden="true">›</span> <span>{esc(n)}</span>'
            ld.append({"@type": "ListItem", "position": i, "name": n})
    h += '</nav>'
    return h, {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld}

# ---------------------------------------------------------------- articles
x = open(f'{ROOT}/wp-import/utagoe-navi-articles.xml').read()
raw_items = x.split('<item>')[1:]

STORY_FIRST = ('<p>息子がはじめてコンクールの舞台に立った日のことは、今もよくおぼえています。舞台袖で「あぁ、むりだ、どうしよう」と言っていた息子は、歌いおわってわたしの顔を見た瞬間、だきついて泣きました。</p>'
               '<p>「それでも、まだコンクールに出たい？」と聞くと、「出たい」と言って、ゆずりませんでした。終わってから泣かなくなったのは、5回目の舞台のときです。</p>')
STORY_FIRST_PLACE = ('<p>息子は「1位をとりたい。1位の賞状とトロフィーがほしい」と言って、練習をつづけていました。1位をもらえた日は、涙を流してよろこび、わたしに「1位をとらせてくれてありがとう。がんばらせてくれてありがとう。歌をさせてくれてありがとう」と言ってくれました。</p>'
                     '<p>今、息子は「歌のコンクールは卒業する」と言って、コンクールには出ていません。それでも、コンクールに向けてがんばった日々や、1位をとって表彰された経験は、まちがいなく息子の人生の財産になっていると思います。</p>')
STORY_PARENT = ('<p>はじめての本番の日、舞台袖で「あぁ、むりだ、どうしよう」と言っていた息子は、歌いおわってわたしの顔を見た瞬間、だきついて泣きました。それでも「出たい」と言いつづけ、5回目の舞台で、やっと終わってから泣かなくなりました。</p>'
                '<p>1位をとった日、息子は涙を流してよろこび、「1位をとらせてくれてありがとう。がんばらせてくれてありがとう。歌をさせてくれてありがとう」と言ってくれました。今はコンクールを卒業しましたが、がんばった日々は、まちがいなく息子の人生の財産になっていると思います。</p>')
STORY_STAGE = '<p>息子も、はじめのころは本番のたびに、舞台袖で不安そうにしていました。終わってから泣かなくなったのは、5回目の舞台のときです。人前で歌う経験を1回ずつかさねることが、そのまま力になっていったのだと思います。</p>'

FILL = {
    '息子さんがはじめてコンクールに出たときのエピソードがあれば': STORY_FIRST,
    '息子さんが1位をとって感じたこと、受賞歴について今思うことがあれば': STORY_FIRST_PLACE,
    'ここはわたしのことばで。': STORY_PARENT,
    '息子さんが人前で堂々とできた場面があれば': STORY_STAGE,
    'このサイトでは、ゆくゆく子どもの歌の先生をさがせるページをつくる予定です。': '<p>全国の歌の教室・声楽教室は、こちらからさがせます。<a href="/kyoshitsu/">歌の教室さがし</a></p>',
    '息子さんが出たジュニアクラシックなど': '<p>声楽（クラシック）のコンクールは、コンクールさがしで「声楽」をえらぶと、しめきりの近い順に見られます。<a href="/concours/">コンクールをさがす</a></p>',
}
fill_used = []

def fix_placeholders(body):
    def para(m):
        inner = m.group(1)
        for k, v in FILL.items():
            if k in inner:
                fill_used.append(k)
                return v
        return ''
    body = re.sub(r'<p>【([^】]*)】</p>', para, body)
    body = re.sub(r'【[^】]*】', '', body)  # inline leftovers
    return body

def cdata(tag, s):
    m = re.search(r'<' + tag + r'><!\[CDATA\[(.*?)\]\]></' + tag + '>', s, re.S)
    return m.group(1) if m else ''

def meta(key, s):
    m = re.search(r'<wp:meta_key><!\[CDATA\[' + key + r'\]\]></wp:meta_key><wp:meta_value><!\[CDATA\[(.*?)\]\]>', s, re.S)
    return m.group(1) if m else ''

arts = []
for n, it in enumerate(raw_items, start=1):
    title = re.search(r'<title>(.*?)</title>', it, re.S).group(1)
    title = html.unescape(title)
    slug = cdata('wp:post_name', it)
    body = cdata('content:encoded', it)
    cat = re.findall(r'<category domain="category" nicename="([^"]+)"', it)
    tags = re.findall(r'<category domain="post_tag" nicename="([^"]+)"', it)
    desc = meta('meta_description', it)
    pd = (cdata('wp:post_date', it) or '2026-11-04')[:10]
    if pd < '2026-11-04': pd = '2026-11-04'
    body = body.replace(DOMAIN + '/', '/').replace(DOMAIN, '/')
    body = fix_placeholders(body)
    body = re.sub(r'<p>\s*</p>', '', body)
    arts.append(dict(n=n, title=title, slug=slug, body=body, cat=cat[0] if cat else 'contest', tags=tags, desc=desc, date=pd))

for a in arts:
    mp = '/home/claude/wp-import/md/%s.md' % (('%02d' % a['n']) if a['n'] < 10 else a['n'])
    d = a['date']
    if _os.path.exists(mp):
        d = max(d, (_dt.datetime.fromtimestamp(_os.path.getmtime(mp), _dt.timezone.utc) + _dt.timedelta(hours=9)).date().isoformat())
    LASTMOD[f"{DOMAIN}/{a['slug']}/"] = d
assert not any('【' in a['body'] for a in arts), [a['slug'] for a in arts if '【' in a['body']]

AUTHOR = ('<aside class="author"><div class="author-ic" aria-hidden="true">う</div><div><p class="author-n">この記事を書いた人：うみ</p>'
          '<p>息子といっしょに、たくさんの歌のコンクールに出てきた母です。お礼や費用、教室えらびで なやんだ経験をもとに書いています。<a href="/about/">くわしいプロフィール</a></p></div></aside>')
CTA = ('<section class="cta"><h2>つぎの一歩を さがす</h2><div class="cta-g">'
       '<a href="/kyoshitsu/" class="cta-a">歌の教室をさがす<small>全国1,988か所</small></a>'
       '<a href="/concours/" class="cta-b">コンクールをさがす<small>'+str(NCON)+'件</small></a>'
       '<a href="/grandprix/" class="cta-c">こどもの歌声グランプリ<small>動画で出られる</small></a></div></section>')

def _bg(t):
    t = re.sub(r'[。、？！?!・｜「」（）()\s]', '', t)
    return {t[i:i+2] for i in range(len(t) - 1)}
_BG = {a['slug']: _bg(a['title']) for a in arts}
_USED = {}
REL = {}
for a in arts:
    linked = set(re.findall(r'href="/([^/"]+)/"', a['body']))
    sc = []
    for b in arts:
        if b is a or b['slug'] in linked: continue
        A, B = _BG[a['slug']], _BG[b['slug']]
        j = len(A & B) / max(1, len(A | B))
        v = 10 * j + 3 * (b['cat'] == a['cat']) + len(set(a['tags']) & set(b['tags'])) - 0.4 * _USED.get(b['slug'], 0)
        sc.append((v, b['n'], b))
    sc.sort(key=lambda x: (-x[0], x[1]))
    REL[a['slug']] = [b for _, _, b in sc[:4]]
    for b in REL[a['slug']]: _USED[b['slug']] = _USED.get(b['slug'], 0) + 1

def card(a):
    return (f'<a class="ac" href="/{a["slug"]}/"><span class="ac-c">{esc(CATS[a["cat"]])}</span>'
            f'<span class="ac-t">{esc(a["title"])}</span></a>')

for a in arts:
    bc, bld = crumbs([(CATS[a['cat']], f'/category/{a["cat"]}/'), (a['title'], None)])
    rel = REL[a['slug']]
    tagl = ''.join(f'<a href="/tag/{t}/">{esc(TAGS[t])}</a>' for t in a['tags'] if t in TAGS)
    body = (f'<article class="art wrap">{bc}'
            f'<p class="art-cat"><a href="/category/{a["cat"]}/">{esc(CATS[a["cat"]])}</a></p>'
            f'<h1>{esc(a["title"])}</h1>'
            f'<p class="art-meta">更新日：{int(a["date"][:4])}年{int(a["date"][5:7])}月{int(a["date"][8:10])}日 ・ 書いた人：うみ</p>'
            f'<div class="art-body">{a["body"]}</div>'
            f'<p class="art-tags">{tagl}</p>'
            f'{AUTHOR}</article>'
            f'<div class="wrap">{CTA}'
            + (f'<section class="rel"><h2>あわせて読みたい</h2><div class="acl">{"".join(card(b) for b in rel)}</div></section>' if rel else '')
            + '</div>')
    ld = [bld, {"@context": "https://schema.org", "@type": "Article", "headline": a['title'][:110],
                "description": a['desc'], "datePublished": a["date"], "dateModified": a["date"],
                "author": {"@type": "Person", "name": "うみ", "url": DOMAIN + '/about/'},
                "publisher": {"@type": "Organization", "name": "株式会社Bright Future Family"},
                "mainEntityOfPage": f'{DOMAIN}/{a["slug"]}/'}]
    page(f'/{a["slug"]}/', a['title'], a['desc'] or a['title'], body, jsonld=ld)

# article list / category / tag pages
def listing(path, h1, lead, items, crumb):
    bc, bld = crumbs(crumb)
    body = f'<div class="wrap">{bc}<h1 class="ph">{esc(h1)}</h1><p class="lead">{lead}</p><div class="acl">{"".join(card(b) for b in items[::-1])}</div>{CTA}</div>'
    page(path, h1, f'{h1}の記事一覧です。{SITE}では、歌の習い事・コンクール・練習のことを、やさしくまとめています。', body, jsonld=[bld])

cat_nav = '<p class="chips">' + ''.join(f'<a href="/category/{k}/">{esc(v)}</a>' for k, v in CATS.items()) + '</p>'
bc, bld = crumbs([('記事一覧', None)])
page('/articles/', '記事一覧', f'{SITE}の記事一覧です。歌の習い事、コンクール、練習、お礼や費用のことまで、{len(arts)}本の記事をのせています。',
     f'<div class="wrap">{bc}<h1 class="ph">記事一覧</h1>{cat_nav}<h2 class="ut-h" style="font-size:20px;color:#1F3A5F">あたらしい記事</h2><div class="acl">{"".join(card(b) for b in arts[::-1][:8])}</div><h2 class="ut-h" style="font-size:20px;color:#1F3A5F">すべての記事（あたらしい順）</h2><div class="acl">{"".join(card(b) for b in arts[::-1])}</div>{CTA}</div>', jsonld=[bld])
for k, v in CATS.items():
    listing(f'/category/{k}/', v, f'「{esc(v)}」の記事をまとめています。', [a for a in arts if a['cat'] == k], [('記事一覧', '/articles/'), (v, None)])
for k, v in TAGS.items():
    its = [a for a in arts if k in a['tags']]
    if its:
        listing(f'/tag/{k}/', f'{v}の歌の記事', f'{esc(v)}の方に向けた記事をまとめています。', its, [('記事一覧', '/articles/'), (f'{v}の歌の記事', None)])

# ---------------------------------------------------------------- tools
def wrapfrag(src):
    s = open(src).read()
    s = re.sub(r'<!--.*?-->', '', s, count=1, flags=re.S)
    return s.replace(DOMAIN + '/', '/')

bc, bld = crumbs([('歌の教室さがし', None)])
page('/kyoshitsu/', '歌の教室さがし｜全国の歌・ボイトレ・声楽教室と合唱団',
     '全国の歌の教室・ボイトレ教室・声楽教室・ミュージカル教室・合唱団を1,988件のせています。都道府県、年代（子ども・中高生・おとな・シニア）、ジャンル、オンラインの有無でさがせます。',
     f'<div class="wrap">{bc}</div>' + wrapfrag(f'{ROOT}/directory/kyoshitsu-wordpress.html'), jsonld=[bld],
     full_title='歌の教室さがし｜全国の歌・ボイトレ・声楽教室と合唱団｜うたごえナビ')

prefs = list(csv.reader(open(f'{ROOT}/directory/pref-pages/pages-list.csv', encoding='utf-8-sig')))[1:]
for name, slug, _u, title, desc, cnt in prefs:
    bc, bld = crumbs([('歌の教室さがし', '/kyoshitsu/'), (name, None)])
    frag = wrapfrag(f'{ROOT}/directory/pref-pages/{slug}.html')
    page(f'/kyoshitsu/{slug}/', title, desc, f'<div class="wrap">{bc}</div>' + frag, jsonld=[bld], full_title=f'{title}｜{SITE}')

bc, bld = crumbs([('コンクールさがし', None)])
page('/concours/', '歌のコンクールさがし｜子どもからシニアまで',
     '歌のコンクールを'+str(NCON)+'件のせています。年代、ジャンル（童謡・声楽・ミュージカル・合唱など）、地域、会場か動画か、しめきりでさがせます。',
     f'<div class="wrap">{bc}</div>' + wrapfrag(f'{ROOT}/concours/concours-wordpress.html'), jsonld=[bld],
     full_title='歌のコンクールさがし｜子どもからシニアまで｜うたごえナビ')

# ---------------------------------------------------------------- top
top = open(f'{ROOT}/top/template.html').read()
d = json.load(open(f'{ROOT}/top/data.json'))
top = top.replace('__DATA__', json.dumps(d, ensure_ascii=False)).replace('__NCLS__', '1,988').replace('__NCON__', str(NCON)).replace('__NEW__', '\n'.join(f'<a href="/{a["slug"]}/">{esc(a["title"])}</a>' for a in arts[::-1][:5]))
top = top.replace('<h1 class="ut-h">', '<h1 class="ut-h">', 1)
page('/', SITE, '全国の歌の教室・ボイトレ教室・合唱団と、歌のコンクールを、お子様からシニアの方までさがせるサイトです。動画で出られる「こどもの歌声グランプリ」も開いています。',
     top, jsonld=[{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": DOMAIN + '/',
}], full_title='うたごえナビ｜歌の教室とコンクールが、ぜんぶさがせる')

# ---------------------------------------------------------------- static pages
for fn, path, title, desc in [
    ('grandprix.html', '/grandprix/', 'こどもの歌声グランプリ 募集要項', '動画で出られる歌のコンクール「こどもの歌声グランプリ」の募集要項です。幼児からシニアまで8部門、ジャンル自由。出た方全員に講評とデジタル賞状をお届けします。'),
    ('about.html', '/about/', '運営者について', 'うたごえナビの運営者「うみ」と、運営会社 株式会社Bright Future Family のご紹介です。'),
    ('contact.html', '/contact/', 'お問い合わせ・掲載のご相談', 'うたごえナビへのお問い合わせ、教室の掲載・情報の修正、協賛のご相談はこちらから。'),
    ('privacy.html', '/privacy/', 'プライバシーポリシー', 'うたごえナビのプライバシーポリシーです。'),
]:
    bc, bld = crumbs([(title, None)])
    body = f'<div class="wrap">{bc}<div class="art">' + open(f'{ROOT}/site-build/{fn}').read() + '</div></div>'
    page(path, title, desc, body, jsonld=[bld])

# 404
with open(f'{OUT}/404.html', 'w') as f:
    f.write(f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ページが見つかりません｜{SITE}</title><meta name="robots" content="noindex"><link rel="stylesheet" href="/assets/site.css"></head><body><main class="wrap" style="padding:60px 16px"><h1 class="ph">ページが見つかりません</h1><p>おさがしのページは、うごいたか、なくなったかもしれません。</p><p><a href="/">トップページへ</a> ／ <a href="/kyoshitsu/">歌の教室さがし</a> ／ <a href="/concours/">コンクールさがし</a></p></main></body></html>''')

os.makedirs(f'{OUT}/assets', exist_ok=True)
with open(f'{OUT}/assets/site.css', 'w') as f:
    f.write(CSS)
with open(f'{OUT}/favicon.svg', 'w') as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30"><circle cx="15" cy="15" r="14" fill="#B9530F"/><path d="M12 20.5a2.5 2.5 0 1 1-2.5-2.5c.9 0 1.7.4 2.5 1V9l9-2v10.5a2.5 2.5 0 1 1-2.5-2.5c.9 0 1.7.4 2.5 1" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')
with open(f'{OUT}/CNAME', 'w') as f:
    f.write('utagoe-navi.jp\n')
open(f'{OUT}/.nojekyll', 'w').close()
with open(f'{OUT}/robots.txt', 'w') as f:
    f.write(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
with open(f'{OUT}/sitemap.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in sitemap:
        f.write(f'<url><loc>{u}</loc><lastmod>{LASTMOD.get(u, TODAY)}</lastmod></url>\n')
    f.write('</urlset>\n')

print('articles', len(arts), 'pages', len(sitemap), 'fills used', fill_used)
