# コンクールの説明記事に「要項ボックス」を入れ、年れい別・動画OK・月ごとの一覧ページをつくる（くりかえし実行してよい）
# 順番：deadline_page.py のあとに実行
import json, os, re, html, datetime, urllib.parse, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, '_build/concours/contests-final.json'), encoding='utf-8'))
JST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.datetime.now(JST).date()
WD = '月火水木金土日'
esc = lambda s: html.escape(s or '', quote=True)
METHOD = {'venue': '会場で歌う', 'video': '動画で出る（会場に行かない）', 'video-venue': '動画（音源）の予選のあと、会場で本選'}
SITE = 'https://utagoe-navi.jp'
fd = lambda d: f'{d.year}年{d.month}月{d.day}日（{WD[d.weekday()]}）'
dd = lambda s: datetime.date.fromisoformat(s) if s else None

def gcal(name, d, url):
    q = {'action': 'TEMPLATE', 'text': f'しめきり：{name}', 'dates': f'{d:%Y%m%d}/{d + datetime.timedelta(days=1):%Y%m%d}',
         'details': f'くわしくは公式サイトで確認：{url}\nうたごえナビ {SITE}/concours/shimekiri/'}
    return 'https://calendar.google.com/calendar/render?' + urllib.parse.urlencode(q)

CSS = ('<style>.yk{background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:14px 16px;margin:16px 0}.yk h2{font-size:1.05rem;margin:0 0 8px;border:0;padding:0}'
       '.yk dl{display:grid;grid-template-columns:7.5em 1fr;gap:6px 10px;margin:0}.yk dt{color:#7a3a0a;font-weight:700}.yk dd{margin:0}'
       '.yk .yk-a{margin:10px 0 0;display:flex;flex-wrap:wrap;gap:8px}.yk .yk-a a{display:inline-block;background:#fff;border:1px solid #d9c6ad;border-radius:999px;padding:4px 12px;font-size:.9rem;text-decoration:none}'
       '.yk small{color:#5d6482}@media(max-width:480px){.yk dl{grid-template-columns:1fr}.yk dd{margin-bottom:4px}}</style>')

# ---------- 1. 説明記事の要項ボックス ----------
fam = collections.OrderedDict()
for c in D:
    if c.get('id') == 'grandprix': continue
    fam.setdefault(c['family'], []).append(c)
nbox = 0
for f, items in fam.items():
    g = items[0].get('guide')
    if not g: continue
    p = os.path.join(ROOT, g.strip('/'), 'index.html')
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--yk-->.*?<!--/yk-->', '', s, flags=re.S)
    s = re.sub(r'<script type="application/ld\+json" id="yk-ev">.*?</script>', '', s, flags=re.S)
    up = sorted([c for c in items if c.get('deadline') and dd(c['deadline']) >= TODAY], key=lambda c: c['deadline'])
    c0 = up[0] if up else sorted(items, key=lambda c: c.get('deadline') or '')[-1]
    rows = []
    if up:
        d = dd(c0['deadline'])
        t = fd(d) + (f'<br><small>地区・部門によってちがいます（{len(up)}件）。いちばん近いしめきりです</small>' if len(up) > 1 else '')
    elif c0.get('deadline'):
        t = fd(dd(c0['deadline'])) + '<br><small>このしめきりは過ぎました。次の回は公式サイトでご確認ください</small>'
    else:
        t = '公式サイトでご確認ください'
    rows.append(('しめきり', t))
    if len(items) == 1 and c0.get('eventText'): rows.append(('日程', esc(c0['eventText'])))
    elif c0.get('eventDate'): rows.append(('本番', fd(dd(c0['eventDate'])) + ('<br><small>地区・部門によってちがいます</small>' if len(items) > 1 else '')))
    if c0.get('method'): rows.append(('出かた', esc(METHOD.get(c0['method'], ''))))
    if c0.get('ageText') or c0.get('ages'): rows.append(('出られる人', esc(c0.get('ageText') or '・'.join(c0['ages']))))
    if c0.get('feeText'): rows.append(('参加費', esc(c0['feeText']) + ('<br><small>部門によってちがいます</small>' if len(items) > 1 else '')))
    if c0.get('place') and len(items) == 1: rows.append(('会場', esc(c0['place'])))
    src = c0.get('source', '')
    chk = dd(c0.get('checked'))
    acts = [f'<a href="{esc(src)}" target="_blank" rel="noopener">公式サイトを見る</a>'] if src else []
    if up: acts.append(f'<a href="{esc(gcal(c0["name"], dd(c0["deadline"]), src))}" target="_blank" rel="noopener">しめきりをGoogleカレンダーに入れる</a>')
    acts.append('<a href="/concours/shimekiri/">ほかのしめきりも見る</a>')
    box = ('<!--yk-->' + CSS + '<section class="yk" aria-label="要項のまとめ"><h2>要項のまとめ</h2><dl>' +
           ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows) + '</dl>' +
           f'<p class="yk-a">{"".join(acts)}</p>' +
           (f'<p style="margin:8px 0 0"><small>{chk.year}年{chk.month}月{chk.day}日に公式サイトでたしかめました。変わることがあるので、申しこむ前にかならず公式サイトをご確認ください。</small></p>' if chk else '') +
           '</section><!--/yk-->')
    if '<div class="art-body">' not in s: continue
    s = s.replace('<div class="art-body">', box + '<div class="art-body">', 1)
    # 本番のEventデータ（1件の大会で、本番の日がわかるものだけ）
    if len(items) == 1 and c0.get('eventDate') and dd(c0['eventDate']) >= TODAY:
        loc = ({'@type': 'VirtualLocation', 'url': src} if c0.get('method') == 'video'
               else {'@type': 'Place', 'name': c0.get('place') or c0.get('region') or '日本', 'address': {'@type': 'PostalAddress', 'addressCountry': 'JP', 'addressRegion': c0.get('region', '')}})
        ev = {'@context': 'https://schema.org', '@type': 'Event', 'name': c0['name'] + (f' {c0["subtitle"]}' if c0.get('subtitle') else ''),
              'startDate': c0['eventDate'], 'eventStatus': 'https://schema.org/EventScheduled',
              'eventAttendanceMode': 'https://schema.org/OnlineEventAttendanceMode' if c0.get('method') == 'video' else 'https://schema.org/OfflineEventAttendanceMode',
              'location': loc, 'url': SITE + g, 'description': (c0.get('ageText') or '') + ' ' + (c0.get('feeText') or '')}
        if src: ev['organizer'] = {'@type': 'Organization', 'name': c0['name'], 'url': src}
        s = s.replace('</head>', '<script type="application/ld+json" id="yk-ev">' + json.dumps(ev, ensure_ascii=False) + '</script></head>', 1)
    open(p, 'w', encoding='utf-8').write(s); nbox += 1
print('yoko boxes:', nbox)

# ---------- 2. 一覧ページ（年れい別・動画OK・月ごと） ----------
tpl = open(os.path.join(ROOT, 'concours', 'index.html'), encoding='utf-8').read()
tpl = re.sub(r'<!--sk-link-->.*?<!--/sk-link-->', '', tpl, flags=re.S)
i = tpl.index('<main>'); j = tpl.rindex('</main>')
HEAD, FOOT = tpl[:i], tpl[j:]
FOOT = re.sub(r'<script>\s*\(function\(\)\{\s*const DATA = .*?</script>', '', FOOT, flags=re.S)
LCSS = ('<style>.cl{max-width:820px;margin:0 auto;padding:0 16px 40px}.cl h1{font-size:1.45rem;margin:12px 0}.cl h2{font-size:1.15rem;margin:28px 0 8px;border-left:5px solid #B9530F;padding-left:10px}'
        '.cl-l{list-style:none;padding:0;margin:0}.cl-l li{background:#fff;border:1px solid #eadfce;border-radius:12px;padding:12px 14px;margin:10px 0}'
        '.cl-d{font-weight:700;margin:0;color:#7a3a0a}.cl-t{margin:4px 0;font-size:1.05rem}.cl-i{margin:2px 0;color:#5d6482;font-size:.9rem}'
        '.cl-soon{display:inline-block;margin-left:8px;font-size:.8rem;background:#fbeee4;color:#b4541b;border-radius:8px;padding:1px 8px}'
        '.cl-box{background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:12px 14px;margin:12px 0}.cl-nav a{display:inline-block;margin:4px 6px 4px 0;padding:4px 12px;border:1px solid #d9c6ad;border-radius:999px;background:#fff;text-decoration:none;font-size:.9rem}</style>')
yr = f'{TODAY.year}-{TODAY.year + 1}'

def item(c, d):
    left = (d - TODAY).days
    soon = '<span class="cl-soon">もうすぐ</span>' if left <= 14 else ''
    name = c['name'] + (f'（{c["subtitle"]}）' if c.get('subtitle') else '')
    href = c.get('guide') or c.get('source') or '/concours/'
    info = ' ・ '.join(x for x in [METHOD.get(c.get('method'), ''), '・'.join(c.get('ages', [])), c.get('feeText', ''), c.get('region', '')] if x)
    return (f'<li><p class="cl-d">しめきり {fd(d)}{soon}</p><p class="cl-t"><a href="{esc(href)}">{esc(name)}</a></p>'
            f'<p class="cl-i">{esc(info)}</p></li>')

def upcoming(pred):
    # 同じ大会は、いちばん近いしめきりだけ
    best = {}
    for c in D:
        if c.get('id') == 'grandprix' or not c.get('deadline'): continue
        d = dd(c['deadline'])
        if d < TODAY or not pred(c): continue
        if c['family'] not in best or d < best[c['family']][0]: best[c['family']] = (d, c)
    return sorted(best.values(), key=lambda x: x[0])

PAGES = [  # slug, 見出し, 説明, 条件
 ('youji', '幼児（未就学）が出られる歌のコンクール', '3歳〜6歳くらいの、小学校に入る前のお子様が出られる部門がある大会です。', lambda c: '幼児' in c.get('ages', [])),
 ('shogakusei', '小学生が出られる歌のコンクール', '小学生の部門がある大会です。童謡・声楽・合唱・ミュージカルなどをまとめました。', lambda c: '小学生' in c.get('ages', [])),
 ('chugakusei', '中学生が出られる歌のコンクール', '中学生の部門がある大会です。声変わりの時期の方は、部門の分け方も見てえらびましょう。', lambda c: '中学生' in c.get('ages', [])),
 ('koukousei', '高校生が出られる歌のコンクール', '高校生の部門がある大会です。音大の受験をかんがえている方の腕だめしにも。', lambda c: '高校生' in c.get('ages', [])),
 ('otona', '大人（大学生・社会人）が出られる歌のコンクール', '大学生や社会人の方が出られる部門がある大会です。アマチュアの部があるかも見てえらびましょう。', lambda c: 'おとな' in c.get('ages', []) or '大学生' in c.get('ages', [])),
 ('senior', 'シニアの方が出られる歌のコンクール', '年れいの上限がない大会や、シニアの部門がある大会です。', lambda c: 'シニア' in c.get('ages', [])),
 ('gassho', '合唱・アンサンブルで出られるコンクール', '合唱団や少人数のアンサンブルで出られる大会です。県の大会から全国・国際の大会までまとめました。', lambda c: '合唱' in (c.get('genres') or [])),
 ('karaoke', 'カラオケ・歌謡曲で出られる歌の大会', 'カラオケや歌謡曲・演歌で出られる大会です。大人やシニアの方が出られるものもあります。', lambda c: 'カラオケ・歌謡' in (c.get('genres') or [])),
 ('douga', '動画・音源で出られる歌のコンクール', '動画や録音を送って審査を受けられる大会です。会場に行かずに出られるものと、動画の予選のあと会場で本選があるものがあります。', lambda c: c.get('method') in ('video', 'video-venue')),
]
nav = '<p class="cl-nav">' + ''.join(f'<a href="/concours/list/{s}/">{h.replace("が出られる歌のコンクール", "").replace("で出られる歌のコンクール", "")}</a>' for s, h, _, _ in PAGES) + '<a href="/concours/shimekiri/">しめきりカレンダー</a></p>'

def page(path, title, h1, desc, intro, lis, crumbs, extra=''):
    head = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', HEAD, count=1)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head, count=1)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{SITE}{path}">', head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + esc(title), head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>' + SITE + path, head)
    head = re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*', r'\g<1>' + esc(desc), head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
    il = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': h1, 'itemListElement': [
        {'@type': 'ListItem', 'position': k + 1, 'name': c['name'] + (f' {c["subtitle"]}' if c.get('subtitle') else ''), 'url': (SITE + c['guide']) if c.get('guide') else c.get('source', SITE + '/concours/')}
        for k, (d, c) in enumerate(lis)]}
    bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': k + 1, 'name': n, 'item': SITE + u} for k, (n, u) in enumerate(crumbs)]}
    head = head.replace('</head>', ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (il, bc)) + '</head>', 1)
    bch = ' <span aria-hidden="true">›</span> '.join([f'<a href="{u}">{n}</a>' for n, u in crumbs[:-1]] + [f'<span>{crumbs[-1][0]}</span>'])
    body = (f'<div class="wrap"><nav class="bc" aria-label="パンくずリスト">{bch}</nav></div>' + LCSS + '<div class="cl">' +
            f'<h1>{esc(h1)}</h1>{intro}' +
            (f'<ul class="cl-l">{"".join(item(c, d) for d, c in lis)}</ul>' if lis else '<p>いまは、これからしめきりの大会がありません。<a href="/concours/">コンクールさがし</a>でほかの条件もごらんください。</p>') +
            extra + '<h2>ほかの一覧</h2>' + nav +
            '<p style="margin-top:20px">会場に行かず、動画だけで出られる<a href="/grandprix/">こどもの歌声グランプリ</a>もあります。幼児からシニア（65歳以上）までの8部門です。</p></div>')
    os.makedirs(os.path.join(ROOT, path.strip('/')), exist_ok=True)
    open(os.path.join(ROOT, path.strip('/'), 'index.html'), 'w', encoding='utf-8').write(head + '<main>\n' + body + '\n' + FOOT)
    return path

made = []
note = ('<div class="cl-box"><p style="margin:0">しめきりの近い順です（{d}時点）。同じ大会で地区や部門がいくつかあるときは、いちばん近いしめきりをのせています。'
        'しめきり・参加費は変わることがあるので、申しこむ前にかならず公式サイトをご確認ください。</p></div>').format(d=f'{TODAY.year}年{TODAY.month}月{TODAY.day}日')
for slug, h, intro, pred in PAGES:
    lis = upcoming(pred)
    h1 = f'{h}一覧【{yr}年】'
    made.append(page(f'/concours/list/{slug}/', f'{h1}｜しめきり順｜うたごえナビ', h1,
                     f'{h}を、しめきりの近い順にまとめました（{len(lis)}大会）。部門・出かた・参加費・地域がひと目でわかります。', f'<p>{intro}</p>' + note, lis,
                     [('トップ', '/'), ('コンクールさがし', '/concours/'), (h1, f'/concours/list/{slug}/')]))
# 月ごと
months = collections.OrderedDict()
for d, c in upcoming(lambda c: True):
    months.setdefault((d.year, d.month), []).append((d, c))
mnav = '<p class="cl-nav">' + ''.join(f'<a href="/concours/shimekiri/{y}-{m:02d}/">{y}年{m}月</a>' for y, m in months) + '</p>'
for (y, m), lis in months.items():
    h1 = f'{y}年{m}月しめきりの歌のコンクール'
    made.append(page(f'/concours/shimekiri/{y}-{m:02d}/', f'{h1}（{len(lis)}大会）｜うたごえナビ', h1,
                     f'{y}年{m}月にしめきりがくる歌のコンクールを、日にち順にまとめました（{len(lis)}大会）。子どもからシニアまで、童謡・声楽・合唱など。',
                     f'<p>{y}年{m}月に申しこみのしめきりがくる歌のコンクールです。</p>' + note, lis,
                     [('トップ', '/'), ('コンクールさがし', '/concours/'), ('しめきりカレンダー', '/concours/shimekiri/'), (h1, f'/concours/shimekiri/{y}-{m:02d}/')],
                     extra='<h2>月ごとに見る</h2>' + mnav))
# 古い月のページはけす
import shutil
for n in os.listdir(os.path.join(ROOT, 'concours', 'shimekiri')):
    if re.fullmatch(r'\d{4}-\d{2}', n) and f'/concours/shimekiri/{n}/' not in made:
        shutil.rmtree(os.path.join(ROOT, 'concours', 'shimekiri', n))

# 入口：しめきりカレンダーとコンクールさがしに、一覧へのリンク
for rel, after in (('concours/shimekiri/index.html', '<h1>歌のコンクール しめきりカレンダー</h1>'), ('concours/index.html', '<!--/sk-link-->')):
    p = os.path.join(ROOT, rel); s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--cl-nav-->.*?<!--/cl-nav-->', '', s, flags=re.S)
    box = ('<!--cl-nav--><div class="wrap" style="margin:8px auto">' + LCSS.replace('.cl{', '.clx{') +
           '<p style="margin:0 0 4px">一覧で見る：</p>' + nav + ('<p style="margin:8px 0 4px">月ごとに見る：</p>' + mnav if 'shimekiri' in rel else '') + '</div><!--/cl-nav-->')
    if after in s: s = s.replace(after, after + box, 1)
    open(p, 'w', encoding='utf-8').write(s)

# サイトマップ
sp = os.path.join(ROOT, 'sitemap.xml'); sm = open(sp, encoding='utf-8').read()
sm = re.sub(r'<url><loc>' + re.escape(SITE) + r'/concours/(?:list/[a-z]+|shimekiri/\d{4}-\d{2})/</loc>.*?</url>\n?', '', sm)
sm = sm.replace('</urlset>', ''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n' for u in made) + '</urlset>')
open(sp, 'w', encoding='utf-8').write(sm)
print('list pages:', len(made))

# ---------- 3. コンクールの記事に「しめきりが近いコンクール」 ----------
soon = upcoming(lambda c: True)
ns = 0
for d0 in os.listdir(ROOT):
    p = os.path.join(ROOT, d0, 'index.html')
    if not os.path.isfile(p): continue
    s = open(p, encoding='utf-8').read()
    if 'href="/category/contest/">コンクール・発表の場</a></p>' not in s or '<section class="cta">' not in s: continue
    s = re.sub(r'<!--sn-->.*?<!--/sn-->', '', s, flags=re.S)
    pick = [(d, c) for d, c in soon if c.get('guide') != f'/{d0}/'][:3]
    if not pick: continue
    li = ''.join(f'<li><a href="{esc(c.get("guide") or c.get("source") or "/concours/")}">{esc(c["name"])}</a><br><small>しめきり {d.month}月{d.day}日（{WD[d.weekday()]}） ・ {esc(METHOD.get(c.get("method"), ""))}</small></li>' for d, c in pick)
    box = ('<!--sn--><div class="wrap"><section style="background:#fff;border:1px solid #eadfce;border-radius:12px;padding:12px 16px;margin:16px 0">'
           '<h2 style="font-size:1.05rem;margin:0 0 6px">しめきりが近いコンクール</h2><ul style="margin:0;padding-left:1.2em;line-height:1.7">' + li + '</ul>'
           '<p style="margin:8px 0 0"><a href="/concours/shimekiri/">しめきりカレンダーを見る</a></p></section></div><!--/sn-->')
    s = s.replace('<div class="wrap"><section class="cta">', box + '<div class="wrap"><section class="cta">', 1)
    open(p, 'w', encoding='utf-8').write(s); ns += 1
print('soon boxes:', ns)

# ---------- 4. まとめ記事に、しめきり順の一覧への入口 ----------
LM = {'contest-list': ['youji', 'shogakusei', 'chugakusei'], 'online-contest': ['douga'], 'online-contest-yosa': ['douga'],
      'utagoe-contest-otona': ['otona'], 'otona-seigaku-contest': ['otona'], 'senior-contest': ['senior'], 'senior-contest-matome': ['senior'],
      'koukousei-uta-contest': ['koukousei'], 'chukousei-contest-matome': ['chugakusei', 'koukousei'],
      'seigaku-contest-matome': ['shogakusei', 'chugakusei', 'koukousei', 'otona', 'senior']}
PT = {s: h for s, h, _, _ in PAGES}
nl = 0
for slug, ls in LM.items():
    p = os.path.join(ROOT, slug, 'index.html')
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--ln-->.*?<!--/ln-->', '', s, flags=re.S)
    k = s.find('<h2', s.find('<div class="art-body">'))
    if k < 0: continue
    box = ('<!--ln--><p style="background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:10px 14px">これからしめきりの大会を、しめきりの近い順に見るときは：' +
           '、'.join(f'<a href="/concours/list/{x}/">{PT[x]}一覧</a>' for x in ls) + '</p><!--/ln-->')
    s = s[:k] + box + s[k:]
    open(p, 'w', encoding='utf-8').write(s); nl += 1
print('list links:', nl)

# ---------- 5. 地域・ジャンルのまとめ記事に「いまのしめきり（自動更新）」 ----------
RM = {'kanto-contest-matome': lambda c: c.get('region') == '関東',
      'kansai-contest-matome': lambda c: c.get('region') == '関西',
      'chubu-contest-matome': lambda c: c.get('region') in ('中部', '東海'),
      'kyushu-contest-matome': lambda c: c.get('region') == '九州・沖縄',
      'tohoku-hokkaido-contest-matome': lambda c: c.get('region') in ('東北', '北海道'),
      'chugoku-shikoku-contest-matome': lambda c: c.get('region') == '中国・四国',
      'musical-contest-matome': lambda c: 'ミュージカル' in (c.get('genres') or []),
      'doyo-contest-matome': lambda c: '童謡' in (c.get('genres') or []),
      'seigaku-contest-matome': lambda c: '声楽' in (c.get('genres') or []),
      'contest-schedule': lambda c: True}
nr = 0
for slug, pred in RM.items():
    p = os.path.join(ROOT, slug, 'index.html')
    if not os.path.exists(p): continue
    lis = upcoming(pred)[:8]
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--now-->.*?<!--/now-->', '', s, flags=re.S)
    if lis:
        li = ''.join(f'<li><a href="{esc(c.get("guide") or c.get("source") or "/concours/")}">{esc(c["name"])}{("（" + esc(c["subtitle"]) + "）") if c.get("subtitle") and len(c["subtitle"]) < 30 else ""}</a> ・ しめきり {d.month}月{d.day}日 ・ {esc(METHOD.get(c.get("method"), ""))}</li>' for d, c in lis)
        box = (f'<!--now--><section style="background:#fff;border:1px solid #eadfce;border-radius:12px;padding:12px 16px;margin:16px 0">'
               f'<h2 style="font-size:1.05rem;margin:0 0 6px;border:0;padding:0">いま申しこめる大会（{TODAY.month}月{TODAY.day}日時点・しめきり順）</h2>'
               f'<ul style="margin:0;padding-left:1.2em;line-height:1.7">{li}</ul>'
               '<p style="margin:8px 0 0;font-size:.9rem">この一覧は毎日自動で新しくなります。<a href="/concours/shimekiri/">しめきりカレンダー</a>もごらんください。</p></section><!--/now-->')
        k = s.find('<h2', s.find('<div class="art-body">'))
        if k > 0: s = s[:k] + box + s[k:]; nr += 1
    open(p, 'w', encoding='utf-8').write(s)
print('now boxes:', nr)
