# 歌のコンクールの参加費まとめ（/concours/sankahi/）をつくる（くりかえし実行してよい）
# データ：_build/concours/contests-final.json（公式サイトでたしかめた参加費）
import json, os, re, html, datetime, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://utagoe-navi.jp'
D = json.load(open(os.path.join(ROOT, '_build/concours/contests-final.json'), encoding='utf-8'))
JST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.datetime.now(JST).date()
esc = lambda s: html.escape(s or '', quote=True)
METHOD = {'venue': '会場', 'video': '動画', 'video-venue': '動画→会場'}
fam = collections.OrderedDict()
for c in D:
    if c.get('id') == 'grandprix': continue
    fam.setdefault(c['family'], []).append(c)
solo, ens = [], []
for f, items in fam.items():
    c = items[0]
    if c.get('feeMin') is None: continue
    lo = min(x['feeMin'] for x in items if x.get('feeMin') is not None)
    hi = max((x.get('feeMax') or x['feeMin']) for x in items if x.get('feeMin') is not None)
    row = dict(c=c, lo=lo, hi=hi, n=len(items))
    (ens if '合唱' in (c.get('genres') or []) else solo).append(row)
solo.sort(key=lambda r: (r['lo'], r['hi'])); ens.sort(key=lambda r: r['c']['name'])
BR = [(0, 0, '無料'), (1, 5000, '1〜5,000円'), (5001, 10000, '5,001〜10,000円'), (10001, 20000, '10,001〜20,000円'), (20001, 10**9, '20,001円以上')]
cnt = collections.Counter()
for r in solo:
    for a, b, lab in BR:
        if a <= r['lo'] <= b: cnt[lab] += 1
yen = lambda v: '無料' if v == 0 else f'{v:,}円'
def tr(r):
    c = r['c']; href = c.get('guide') or c.get('source') or '/concours/'
    rng = yen(r['lo']) if r['lo'] == r['hi'] else f'{yen(r["lo"])}〜{yen(r["hi"])}'
    return (f'<tr><td><a href="{esc(href)}">{esc(c["name"])}</a>' + (f'<br><small>地区・部門 {r["n"]}件</small>' if r['n'] > 1 else '') +
            f'</td><td>{esc(METHOD.get(c.get("method"), ""))}</td><td>{rng}<br><small>{esc(c.get("feeText"))}</small></td></tr>')
css = ('<style>.fp{max-width:880px;margin:0 auto;padding:0 16px 40px}.fp h1{font-size:1.45rem;margin:12px 0}.fp h2{font-size:1.15rem;margin:28px 0 8px;border-left:5px solid #B9530F;padding-left:10px}'
       '.fp-box{background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:12px 14px;margin:12px 0}.fp-t{width:100%;border-collapse:collapse;font-size:.92rem;background:#fff}'
       '.fp-t th,.fp-t td{border:1px solid #eadfce;padding:8px;vertical-align:top;text-align:left}.fp-t th{background:#fbf3e8}.fp-t small{color:#5d6482}.fp-w{overflow-x:auto}'
       '@media(max-width:600px){.fp-t thead{display:none}.fp-t tr{display:block;border:1px solid #eadfce;margin:8px 0}.fp-t td{display:block;border:0;border-bottom:1px dashed #eadfce}}</style>')
dist = ''.join(f'<li>{lab}：{cnt[lab]}大会</li>' for _, _, lab in BR)
body = (f'<div class="wrap"><nav class="bc" aria-label="パンくずリスト"><a href="/">トップ</a> <span aria-hidden="true">›</span> <a href="/concours/">コンクールさがし</a> <span aria-hidden="true">›</span> <span>参加費のまとめ</span></nav></div>'
        + css + '<div class="fp">' +
        f'<h1>歌のコンクールの参加費はいくら？ {len(solo) + len(ens)}大会の参加費まとめ【{TODAY.year}-{TODAY.year + 1}年】</h1>'
        f'<p>うたごえナビにのせている歌のコンクールのうち、公式サイトで参加費をたしかめられた{len(solo) + len(ens)}大会の参加費を、ひとつのページにまとめました（{TODAY.year}年{TODAY.month}月{TODAY.day}日時点）。</p>'
        '<div class="fp-box"><p style="margin:0">参加費は、部門・年れい・地区・予選か本選かによって変わります。表の金額は、公式サイトに書かれていたもっとも安い金額と高い金額です（伴奏料・会員の割引などはふくまないことがあります）。'
        '申しこむ前に、かならず各コンクールの公式サイトでご確認ください。</p></div>'
        f'<h2>ひとりで歌う大会の参加費（安い順）</h2><p>ひとりで出る大会（一部はグループの部門もあり）の、もっとも安い参加費で分けると、次のようになりました。</p><ul>{dist}</ul>'
        '<p>予選と本選で別に参加費がかかる大会もあります。表の下の小さい字に、公式の書き方をそのままのせています。</p>'
        '<div class="fp-w"><table class="fp-t"><thead><tr><th>大会</th><th>出かた</th><th>参加費</th></tr></thead><tbody>' + ''.join(tr(r) for r in solo) + '</tbody></table></div>'
        '<h2>合唱・アンサンブルの大会の参加費</h2><p>合唱やアンサンブルの大会は、「1団体いくら」「1人いくら」など、数え方が大会ごとにちがうので、公式の書き方をそのままのせています。</p>'
        '<div class="fp-w"><table class="fp-t"><thead><tr><th>大会</th><th>出かた</th><th>参加費</th></tr></thead><tbody>' + ''.join(tr(r) for r in ens) + '</tbody></table></div>'
        '<h2>参加費のほかにかかるお金</h2><p>参加費のほかに、伴奏者へのお礼、衣装、会場までの交通費などがかかることがあります。くわしくは<a href="/happyoukai-hiyou/">歌の発表会にかかる費用の種類</a>や、<a href="/dress-rental/">ドレス レンタルまとめ</a>もごらんください。</p>'
        '<p style="margin-top:20px">しめきりの近い順に見るときは<a href="/concours/shimekiri/">しめきりカレンダー</a>へ。動画で出られる<a href="/grandprix/">こどもの歌声グランプリ</a>もあります。</p></div>')
tpl = open(os.path.join(ROOT, 'concours', 'index.html'), encoding='utf-8').read()
tpl = re.sub(r'<!--(sk-link|cl-nav)-->.*?<!--/\1-->', '', tpl, flags=re.S)
i = tpl.index('<main>'); j = tpl.rindex('</main>')
head, foot = tpl[:i], re.sub(r'<script>\s*\(function\(\)\{\s*const DATA = .*?</script>', '', tpl[j:], flags=re.S)
path = '/concours/sankahi/'
title = f'歌のコンクールの参加費まとめ【{TODAY.year}-{TODAY.year + 1}年】{len(solo) + len(ens)}大会｜うたごえナビ'
desc = f'歌のコンクール{len(solo) + len(ens)}大会の参加費を、公式サイトでたしかめてまとめました。ひとりで歌う大会は安い順、合唱・アンサンブルの大会は公式の書き方のまま。子どもからシニアまで。'
head = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', head, count=1)
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head, count=1)
head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{SITE}{path}">', head, count=1)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + esc(title), head)
head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>' + SITE + path, head)
head = re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*', r'\g<1>' + esc(desc), head)
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
    {'@type': 'ListItem', 'position': 1, 'name': 'トップ', 'item': SITE + '/'},
    {'@type': 'ListItem', 'position': 2, 'name': 'コンクールさがし', 'item': SITE + '/concours/'},
    {'@type': 'ListItem', 'position': 3, 'name': '参加費のまとめ', 'item': SITE + path}]}
head = head.replace('</head>', f'<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script></head>', 1)
os.makedirs(os.path.join(ROOT, path.strip('/')), exist_ok=True)
open(os.path.join(ROOT, path.strip('/'), 'index.html'), 'w', encoding='utf-8').write(head + '<main>\n' + body + '\n' + foot)
# 入口
for rel in ('concours/index.html', 'happyoukai-hiyou/index.html', 'seigaku-hiyou/index.html'):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--fp-->.*?<!--/fp-->', '', s, flags=re.S)
    box = f'<!--fp--><p style="background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:10px 14px">歌のコンクールの参加費を、{len(solo) + len(ens)}大会ぶん1ページにまとめました：<a href="{path}">参加費のまとめ</a></p><!--/fp-->'
    if rel == 'concours/index.html':
        if '<!--/sk-link-->' in s: s = s.replace('<!--/sk-link-->', '<!--/sk-link--><div class="wrap">' + box + '</div>', 1)
    else:
        k = s.find('<h2', s.find('<div class="art-body">'))
        if k > 0: s = s[:k] + box + s[k:]
    open(p, 'w', encoding='utf-8').write(s)
sp = os.path.join(ROOT, 'sitemap.xml'); sm = open(sp, encoding='utf-8').read()
sm = re.sub(r'<url><loc>' + re.escape(SITE + path) + r'</loc>.*?</url>\n?', '', sm)
sm = sm.replace('</urlset>', f'<url><loc>{SITE}{path}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n</urlset>')
open(sp, 'w', encoding='utf-8').write(sm)
print('fee page:', len(solo), 'solo,', len(ens), 'ensemble')
