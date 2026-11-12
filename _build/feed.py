# 新しい記事のRSS（/feed.xml）と、しめきりのRSS（/concours/shimekiri.xml）をつくる（くりかえし実行してよい）
import os, re, json, html, datetime, email.utils
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://utagoe-navi.jp'
JST = datetime.timezone(datetime.timedelta(hours=9))
esc = lambda s: html.escape(s or '', quote=False)
def rfc(d): return email.utils.format_datetime(datetime.datetime.combine(d, datetime.time(9, 0), JST))
items = []
for d in os.listdir(ROOT):
    p = os.path.join(ROOT, d, 'index.html')
    if not os.path.isfile(p): continue
    s = open(p, encoding='utf-8').read()
    if 'class="art-meta"' not in s: continue
    m = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})', s); t = re.search(r'<h1>(.*?)</h1>', s, re.S)
    ds = re.search(r'<meta name="description" content="([^"]*)"', s)
    if not (m and t): continue
    items.append((m.group(1), d, html.unescape(re.sub('<[^>]+>', '', t.group(1))), html.unescape(ds.group(1)) if ds else ''))
items.sort(key=lambda x: (x[0], x[1]), reverse=True)
def rss(title, link, desc, its):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            f'<title>{esc(title)}</title><link>{link}</link><description>{esc(desc)}</description><language>ja</language>'
            f'<atom:link href="{link.rstrip("/")}" rel="self" type="application/rss+xml"/>' + ''.join(its) + '</channel></rss>\n')
its = [f'<item><title>{esc(t)}</title><link>{SITE}/{d}/</link><guid>{SITE}/{d}/</guid><pubDate>{rfc(datetime.date.fromisoformat(dt))}</pubDate><description>{esc(ds)}</description></item>' for dt, d, t, ds in items[:30]]
open(os.path.join(ROOT, 'feed.xml'), 'w', encoding='utf-8').write(rss('うたごえナビ 新しい記事', SITE + '/feed.xml', '歌の教室とコンクールの情報サイト「うたごえナビ」の新しい記事', its))
# しめきり
D = json.load(open(os.path.join(ROOT, '_build/concours/contests-final.json'), encoding='utf-8'))
TODAY = datetime.datetime.now(JST).date()
best = {}
for c in D:
    if c.get('id') == 'grandprix' or not c.get('deadline'): continue
    dd = datetime.date.fromisoformat(c['deadline'])
    if dd < TODAY: continue
    if c['family'] not in best or dd < best[c['family']][0]: best[c['family']] = (dd, c)
up = sorted(best.values(), key=lambda x: x[0])
its = []
for dd, c in up:
    u = SITE + c['guide'] if c.get('guide') else c.get('source', SITE + '/concours/')
    ck = datetime.date.fromisoformat(c.get('checked') or TODAY.isoformat())
    its.append(f'<item><title>{esc(f"{dd.month}/{dd.day} しめきり：" + c["name"])}</title><link>{esc(u)}</link><guid isPermaLink="false">{esc(c["id"])}-{c["deadline"]}</guid>'
               f'<pubDate>{rfc(ck)}</pubDate><description>{esc((c.get("feeText") or "") + " " + (c.get("ageText") or ""))}</description></item>')
open(os.path.join(ROOT, 'concours', 'shimekiri.xml'), 'w', encoding='utf-8').write(rss('うたごえナビ 歌のコンクールのしめきり', SITE + '/concours/shimekiri.xml', 'これからしめきりの歌のコンクール（しめきり順）', its))
# ページに RSS の場所を書く
for rel, href, ttl in (('index.html', '/feed.xml', 'うたごえナビ 新しい記事'), ('articles/index.html', '/feed.xml', 'うたごえナビ 新しい記事'),
                       ('concours/shimekiri/index.html', '/concours/shimekiri.xml', '歌のコンクールのしめきり')):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<link rel="alternate" type="application/rss\+xml"[^>]*>', '', s)
    s = s.replace('</head>', f'<link rel="alternate" type="application/rss+xml" title="{ttl}" href="{href}"></head>', 1)
    open(p, 'w', encoding='utf-8').write(s)
print('feed:', len(items), 'articles,', len(up), 'deadlines')
