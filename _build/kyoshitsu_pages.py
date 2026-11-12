#!/usr/bin/env python3
"""教室ごとのページと、市区町村ごとのページを作る。
リポジトリのルートで  python3 _build/kyoshitsu_pages.py
- データ：_build/kyoshitsu/classrooms.json
- 教室ページ：公式サイトで確認できた教室だけ（listingOnly=false） → /kyoshitsu/<県>/s/<id>/
- 市区町村ページ：教室が3つ以上ある市区町村 → /kyoshitsu/<県>/<市区町村>/
- 都道府県ページの下に「市区町村からさがす」を入れる
- sitemap.xml に追加する
なんどでも実行してだいじょうぶ。
"""
import os, re, json, csv, html, hashlib, collections, shutil, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
DOMAIN = 'https://utagoe-navi.jp'
import datetime as _dt
TODAY = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=9)).date().isoformat()
SITE = 'うたごえナビ'
MIN_CITY = 3

data = json.load(open('_build/kyoshitsu/classrooms.json'))
prefs = list(csv.reader(open('_build/kyoshitsu/pages-list.csv', encoding='utf-8-sig')))[1:]
PSLUG = {r[0]: r[1] for r in prefs}

shell = open('about/index.html').read()
HEAD, rest = shell.split('<main>', 1)
_, FOOT = rest.rsplit('</main>', 1)

esc = lambda s: html.escape(str(s), quote=True)
AGE = [('toddler', '幼児'), ('elem', '小学生'), ('jhs', '中学生'), ('high', '高校生'), ('adult', 'おとな'), ('senior', 'シニア')]
def genre_label(g):
    return 'ボーカル・ボイトレ' if g == 'キッズボーカル' else g
def cid(e):
    return hashlib.sha1((e['prefecture'] + '|' + e['city'] + '|' + e['name']).encode()).hexdigest()[:8]
def city_path(e):
    return f"/kyoshitsu/{PSLUG[e['prefecture']]}/{urllib.parse.quote(e['city'])}/"
def cls_path(e):
    return f"/kyoshitsu/{PSLUG[e['prefecture']]}/s/{cid(e)}/"

def page(path, title, desc, body, crumbs, full_title=None):
    t = full_title or f'{title}｜{SITE}'
    url = DOMAIN + path
    h = HEAD
    h = re.sub(r'<title>.*?</title>', f'<title>{esc(t)}</title>', h, count=1)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', h, count=1)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h, count=1)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(t)}">', h, count=1)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', h, count=1)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', h, count=1)
    items = [{"@type": "ListItem", "position": 1, "name": "トップ", "item": DOMAIN + '/'}]
    bc = '<nav class="bc" aria-label="パンくずリスト"><a href="/">トップ</a>'
    for i, (n, p) in enumerate(crumbs, start=2):
        if p:
            bc += f' <span aria-hidden="true">›</span> <a href="{p}">{esc(n)}</a>'
            items.append({"@type": "ListItem", "position": i, "name": n, "item": DOMAIN + p})
        else:
            bc += f' <span aria-hidden="true">›</span> <span>{esc(n)}</span>'
            items.append({"@type": "ListItem", "position": i, "name": n})
    bc += '</nav>'
    ld = json.dumps([{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}], ensure_ascii=False)
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + ld.replace('\\', '\\\\') + '</script>', h, count=1, flags=re.S)
    out = h + '<main>\n<div class="wrap">' + bc + body + '</div>\n</main>' + FOOT
    d = '.' + urllib.parse.unquote(path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(out)
    return url

# 前に作ったページを消して作りなおす
for pref, slug in PSLUG.items():
    base = f'kyoshitsu/{slug}'
    if not os.path.isdir(base): continue
    for n in os.listdir(base):
        p = os.path.join(base, n)
        if os.path.isdir(p):
            shutil.rmtree(p)

bycity = collections.defaultdict(list)
for e in data:
    if e['city']:
        bycity[(e['prefecture'], e['city'])].append(e)
city_ok = {k for k, v in bycity.items() if len(v) >= MIN_CITY}

def facts(e):
    ages = [lab for k, lab in AGE if k in e['ageTags']]
    rows = [('種類', esc(e['type'])),
            ('ジャンル', esc('・'.join(genre_label(g) for g in e['genres']) or '公式サイトで確認')),
            ('対象', esc(e['ages']) + (f"<br><small>（{esc('・'.join(ages))}）</small>" if ages else '')),
            ('場所', esc(e['prefecture'] + e['city']))]
    if e.get('senior'):
        sc = e.get('seniorCourse') or ''
        rows.append(('シニアの方', esc('歓迎' if e['senior'] == '歓迎' else '受けられる') + (f'（{esc(sc)}）' if sc else '')))
    on = e['online']
    rows.append(('オンライン', esc(on if on != '不明' else '公式サイトで確認')))
    if e['url']:
        rows.append(('公式サイト', f'<a href="{esc(e["url"])}" target="_blank" rel="noopener">{esc(e["url"])}</a>'))
    return '<table class="kt">' + ''.join(f'<tr><th>{a}</th><td>{b}</td></tr>' for a, b in rows) + '</table>'

def related(e):
    g = set(e['genres'])
    L = []
    if '声楽' in g: L.append(('/seigaku-kyoshitsu/', '子どもの声楽教室のえらび方'))
    if g & {'ボーカル', 'ボイトレ', 'キッズボーカル', 'ボーカル・ボイトレ'}: L.append(('/voitore-kyoshitsu-hikaku/', '大手のボイトレ教室・音楽教室のくらべ'))
    if '合唱' in g: L.append(('/gasshoudan/', '子どもの合唱団に入るには') if 'elem' in e['ageTags'] else ('/otona-gasshodan/', '大人から合唱団に入るには'))
    if 'ミュージカル' in g: L.append(('/kids-musical/', 'キッズミュージカルスクールのえらび方'))
    if e.get('senior'): L.append(('/senior-uta-kyoshitsu/', 'シニアの歌の教室えらび'))
    L.append(('/taiken-lesson/', '歌の体験レッスンで見るべき5つのこと'))
    seen = set(); L2 = []
    for u, t in L:
        if u not in seen and os.path.isdir('.' + u):
            seen.add(u); L2.append((u, t))
    return '<ul>' + ''.join(f'<li><a href="{u}">{esc(t)}</a></li>' for u, t in L2[:4]) + '</ul>'

def card(e, link_self=True):
    ages = '・'.join(lab for k, lab in AGE if k in e['ageTags'])
    g = '・'.join(genre_label(x) for x in e['genres'])
    if not e['listingOnly'] and link_self:
        name = f'<a href="{cls_path(e)}">{esc(e["name"])}</a>'
    elif e['url']:
        name = f'<a href="{esc(e["url"])}" target="_blank" rel="noopener nofollow">{esc(e["name"])}</a>'
    else:
        name = esc(e['name'])
    extra = []
    if e['online'] in ('あり',) or e['online'].startswith('あり'): extra.append('オンラインあり')
    if e.get('senior') == '歓迎': extra.append('シニア歓迎')
    if e['listingOnly']: extra.append('紹介サイトの情報')
    tags = ''.join(f'<span class="kc-t">{esc(x)}</span>' for x in extra)
    return (f'<li class="kc"><p class="kc-n">{name}</p><p class="kc-m">{esc(e["type"])}｜{esc(g)}｜{esc(ages or e["ages"])}</p>'
            f'{"<p>" + tags + "</p>" if tags else ""}</li>')

urls = []
# 教室ページ
for e in data:
    if e['listingOnly'] or not e['city']:
        continue
    pref, city = e['prefecture'], e['city']
    ps = PSLUG[pref]
    others = [o for o in bycity[(pref, city)] if o is not e]
    crumbs = [('歌の教室さがし', '/kyoshitsu/'), (pref, f'/kyoshitsu/{ps}/')]
    if (pref, city) in city_ok:
        crumbs.append((city, city_path(e)))
    crumbs.append((e['name'], None))
    g = '・'.join(genre_label(x) for x in e['genres'])
    title = f"{e['name']}（{pref}{city}）"
    desc = f"{pref}{city}の{e['type']}「{e['name']}」。ジャンル：{g}。対象：{e['ages']}。公式サイトでたしかめた情報をのせています（2026年11月時点）。"[:150]
    body = (f'<article class="art"><p class="art-cat"><a href="/kyoshitsu/{ps}/">{esc(pref)}の歌の教室</a></p>'
            f'<h1>{esc(e["name"])}</h1><p class="art-meta">{esc(pref + city)} ・ {esc(e["type"])}</p>'
            f'{facts(e)}'
            + (f'<p class="note">メモ：{esc(e["note"])}</p>' if e['note'] else '') +
            '<p class="kt-n">この情報は、2026年11月の時点で公式サイトなどでたしかめた内容です。レッスンの内容や料金はかわることがあります。申しこむ前に、かならず公式サイトをご確認ください。まちがいを見つけたときは、<a href="/contact/">お問い合わせ</a>からお知らせください。</p>'
            '<h2>教室をえらぶときに読みたい記事</h2>' + related(e))
    if others:
        body += f'<h2>{esc(city)}のほかの歌の教室</h2><ul class="kl">' + ''.join(card(o) for o in others[:12]) + '</ul>'
        if (pref, city) in city_ok:
            body += f'<p><a href="{city_path(e)}">{esc(city)}の歌の教室をすべて見る</a></p>'
    body += f'<p><a href="/kyoshitsu/{ps}/">{esc(pref)}の歌の教室をさがす</a> ／ <a href="/kyoshitsu/">全国の歌の教室さがし</a></p></article>'
    urls.append(page(cls_path(e), title, desc, body, crumbs, full_title=f"{title}｜歌の教室｜{SITE}"))

# 市区町村ページ
links_by_pref = collections.defaultdict(list)
for (pref, city), L in sorted(bycity.items(), key=lambda kv: (-len(kv[1]), kv[0][1])):
    if (pref, city) not in city_ok:
        continue
    ps = PSLUG[pref]
    n = len(L)
    gc = collections.Counter(genre_label(g) for e in L for g in e['genres'])
    kids = sum(1 for e in L if set(e['ageTags']) & {'toddler', 'elem', 'jhs'})
    adult = sum(1 for e in L if 'adult' in e['ageTags'])
    senior = sum(1 for e in L if 'senior' in e['ageTags'])
    online = sum(1 for e in L if e['online'].startswith('あり'))
    gtxt = '、'.join(f'{k}{v}件' for k, v in gc.most_common(5))
    title = (f'{pref}で県内に複数ある歌の教室・ボイトレ教室・合唱団{n}件' if city == '県内に複数' else f'{city}の歌の教室・ボイトレ教室・合唱団{n}件')
    desc = f'{pref}{city}の歌の教室・ボイトレ教室・声楽教室・合唱団を{n}件まとめました。子ども・おとな・シニアが受けられる教室、オンラインの有無がわかります（2026年11月時点）。'
    L2 = sorted(L, key=lambda e: (e['listingOnly'], e['name']))
    body = (f'<article class="art"><h1>{esc(title)}</h1>'
            f'<p>{esc(pref + city)}で歌をならえる教室や合唱団を{n}件のせています（2026年11月時点）。{esc(gtxt)}です。'
            f'子どもが受けられる教室は{kids}件、おとなが受けられる教室は{adult}件、シニアが受けられる教室は{senior}件わかっています。'
            + (f'オンラインレッスンがある教室は{online}件です。' if online else '') + '</p>'
            '<p class="kt-n">「紹介サイトの情報」とある教室は、教室の紹介サイトでたしかめたものです。くわしいことは、それぞれの公式サイトでご確認ください。</p>'
            '<ul class="kl">' + ''.join(card(e) for e in L2) + '</ul>'
            '<h2>教室をえらぶときに読みたい記事</h2><ul>'
            '<li><a href="/taiken-lesson/">歌の体験レッスンで見るべき5つのこと</a></li>'
            '<li><a href="/sensei-erabikata/">はじめての歌の先生えらび</a></li>'
            '<li><a href="/otona-voitore-hajimeru/">30代・40代・50代から歌を習いたい方へ</a></li>'
            '<li><a href="/senior-uta-kyoshitsu/">シニアの歌の教室えらび</a></li></ul>'
            f'<p><a href="/kyoshitsu/{ps}/">{esc(pref)}の歌の教室をさがす</a> ／ <a href="/kyoshitsu/">全国の歌の教室さがし</a></p></article>')
    path = city_path(L[0])
    urls.append(page(path, title, desc, body, [('歌の教室さがし', '/kyoshitsu/'), (pref, f'/kyoshitsu/{ps}/'), (city, None)],
                     full_title=f'{title}｜子どもから大人・シニアまで｜{SITE}'))
    links_by_pref[pref].append((city, n, path))

# 都道府県ページに「市区町村からさがす」
S, E = '<!--cities-start-->', '<!--cities-end-->'
for pref, ps in PSLUG.items():
    p = f'kyoshitsu/{ps}/index.html'
    if not os.path.exists(p): continue
    s = open(p).read()
    s = re.sub(re.escape(S) + '.*?' + re.escape(E), '', s, flags=re.S)
    L = links_by_pref.get(pref)
    if L:
        box = (S + '<section class="city-box"><h2>市区町村からさがす</h2><ul>' +
               ''.join(f'<li><a href="{u}">{esc(c)}（{n}）</a></li>' for c, n, u in sorted(L, key=lambda x: -x[1])) +
               '</ul></section>' + E)
        i = s.rfind('</main>')
        s = s[:i] + '<div class="wrap">' + box + '</div>' + s[i:]
    open(p, 'w').write(s)

# sitemap
sm = open('sitemap.xml').read()
sm = re.sub(r'<url><loc>https://utagoe-navi\.jp/kyoshitsu/[a-z]+/(?:s/[0-9a-f]+|%[^<]+)/</loc>.*?</url>\n', '', sm)
add = ''.join(f'<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls)
sm = sm.replace('</urlset>', add + '</urlset>')
open('sitemap.xml', 'w').write(sm)
print('classroom pages:', sum(1 for u in urls if '/s/' in u), 'city pages:', sum(1 for u in urls if '/s/' not in u))
