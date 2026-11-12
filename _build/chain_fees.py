# 大手の歌の教室の「体験・入会金・月謝」くらべページ（/kyoshitsu/ryokin/）をつくる（くりかえし実行してよい）
# データ：_build/kyoshitsu/chain-fees.json（公式サイトでたしかめた内容と、そのURL）
import json, os, re, html, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://utagoe-navi.jp'
D = json.load(open(os.path.join(ROOT, '_build/kyoshitsu/chain-fees.json'), encoding='utf-8'))
esc = lambda s: html.escape(s or '', quote=True)
chk = max(d.get('checked', '') for d in D)
cd = datetime.date.fromisoformat(chk)
cdt = f'{cd.year}年{cd.month}月{cd.day}日'

def cell(f):
    if not f or not f.get('text'):
        return '<span class="rk-na">公式サイトに記載なし</span>'
    u = f.get('url')
    return esc(f['text']) + (f' <a class="rk-src" href="{esc(u)}" target="_blank" rel="noopener nofollow">出典</a>' if u else '')

cards = []
for d in D:
    t = d.get('trial') or {}
    trial = (t.get('price') or '公式サイトに記載なし') + (f'（{t["length"]}）' if t.get('length') else '')
    trial_cell = esc(trial) + (f' <a class="rk-src" href="{esc(t["url"])}" target="_blank" rel="noopener nofollow">出典</a>' if t.get('url') else '')
    note = d.get('notes') or ''
    cards.append(
        f'<section class="rk-c"><h2>{esc(d["chain"])}</h2><dl>'
        f'<dt>体験レッスン</dt><dd>{trial_cell}</dd>'
        f'<dt>入会金</dt><dd>{cell(d.get("admission"))}</dd>'
        f'<dt>月謝・料金</dt><dd>{cell(d.get("monthly"))}</dd>'
        f'<dt>レッスンの形</dt><dd>{esc(d.get("format") or "公式サイトに記載なし")}</dd>'
        f'<dt>オンライン</dt><dd>{esc(d.get("online") or "公式サイトに記載なし")}</dd>'
        + '</dl></section>')

css = ('<style>.rk{max-width:820px;margin:0 auto;padding:0 16px 40px}.rk h1{font-size:1.45rem;margin:12px 0}'
       '.rk-c{background:#fff;border:1px solid #eadfce;border-radius:12px;padding:12px 16px;margin:14px 0}.rk-c h2{font-size:1.1rem;margin:0 0 8px;border-left:5px solid #B9530F;padding-left:10px}'
       '.rk-c dl{display:grid;grid-template-columns:7em 1fr;gap:6px 10px;margin:0;font-size:.95rem}.rk-c dt{color:#7a3a0a;font-weight:700}.rk-c dd{margin:0;overflow-wrap:anywhere}'
       '.rk-src{font-size:.8rem;margin-left:4px}.rk-na{color:#5d6482}.rk-box{background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:12px 14px;margin:12px 0}'
       '@media(max-width:480px){.rk-c dl{grid-template-columns:1fr}.rk-c dd{margin-bottom:6px}}</style>')
intro = (f'<h1>大手の歌の教室 体験・入会金・月謝のまとめ【{cd.year}年{cd.month}月】</h1>'
         f'<p>全国に教室がある歌・ボイトレの教室について、体験レッスン・入会金・月謝・レッスンの形を、各教室の公式サイトでたしかめてまとめました（{cdt}に確認）。ならび順に意味はありません。</p>'
         '<div class="rk-box"><p style="margin:0">料金やキャンペーンは、教室・地域・時期によって変わります。ここにのせたのは、公式サイトに書かれていた内容をそのまま写したものです。'
         '申しこむ前に、かならず各教室の公式サイトや、通いたい校舎でご確認ください。「出典」から、たしかめたページを開けます。</p></div>'
         '<p>金額だけでなく、先生との相性や通いやすさもあわせて見てみましょう。くらべ方は<a href="/voitore-kyoshitsu-hikaku/">大手のボイトレ教室・音楽教室のくらべ方</a>や、'
         '<a href="/checklist/kengaku/">見学・体験レッスン メモ</a>もごらんください。お住まいの近くの教室は<a href="/kyoshitsu/">歌の教室さがし</a>でさがせます。</p>')
body = (f'<div class="wrap"><nav class="bc" aria-label="パンくずリスト"><a href="/">トップ</a> <span aria-hidden="true">›</span> <a href="/kyoshitsu/">歌の教室さがし</a> <span aria-hidden="true">›</span> <span>大手の歌の教室 料金まとめ</span></nav></div>'
        + css + '<div class="rk">' + intro + ''.join(cards) +
        '<p style="margin-top:20px">教室に通う前に、まずは歌ってみたい方へ。会場に行かずに動画で出られる<a href="/grandprix/">こどもの歌声グランプリ</a>もあります。</p></div>')

tpl = open(os.path.join(ROOT, 'concours', 'index.html'), encoding='utf-8').read()
tpl = re.sub(r'<!--(sk-link|cl-nav)-->.*?<!--/\1-->', '', tpl, flags=re.S)
i = tpl.index('<main>'); j = tpl.rindex('</main>')
head, foot = tpl[:i], re.sub(r'<script>\s*\(function\(\)\{\s*const DATA = .*?</script>', '', tpl[j:], flags=re.S)
path = '/kyoshitsu/ryokin/'
title = f'大手の歌の教室・ボイトレの料金まとめ【{cd.year}年{cd.month}月】体験・入会金・月謝｜うたごえナビ'
desc = f'シアーミュージック・NAYUTAS・島村楽器・EYSなど、全国の歌の教室・ボイトレ教室{len(D)}社の体験レッスン・入会金・月謝を、公式サイトでたしかめてまとめました（{cdt}確認）。'
head = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', head, count=1)
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head, count=1)
head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{SITE}{path}">', head, count=1)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + esc(title), head)
head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>' + SITE + path, head)
head = re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*', r'\g<1>' + esc(desc), head)
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
    {'@type': 'ListItem', 'position': 1, 'name': 'トップ', 'item': SITE + '/'},
    {'@type': 'ListItem', 'position': 2, 'name': '歌の教室さがし', 'item': SITE + '/kyoshitsu/'},
    {'@type': 'ListItem', 'position': 3, 'name': '大手の歌の教室 料金まとめ', 'item': SITE + path}]}
head = head.replace('</head>', f'<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script></head>', 1)
os.makedirs(os.path.join(ROOT, path.strip('/')), exist_ok=True)
open(os.path.join(ROOT, path.strip('/'), 'index.html'), 'w', encoding='utf-8').write(head + '<main>\n' + body + '\n' + foot)

# 入口：教室さがしのトップと、くらべ方の記事
for rel, anchor in (('kyoshitsu/index.html', None), ('voitore-kyoshitsu-hikaku/index.html', 'h2'), ('gessha/index.html', 'h2'), ('kyoshitsu-hikaku-hyou/index.html', 'h2')):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--rk-->.*?<!--/rk-->', '', s, flags=re.S)
    box = f'<!--rk--><p style="background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:10px 14px">大手の歌の教室の体験・入会金・月謝を、公式サイトでたしかめて1ページにまとめました：<a href="{path}">大手の歌の教室 料金まとめ（{cd.year}年{cd.month}月）</a></p><!--/rk-->'
    if anchor:
        k = s.find('<h2', s.find('<div class="art-body">'))
        if k < 0: continue
        s = s[:k] + box + s[k:]
    else:
        k = s.rfind('</main>'); s = s[:k] + '<div class="wrap">' + box + '</div>' + s[k:]
    open(p, 'w', encoding='utf-8').write(s)
sp = os.path.join(ROOT, 'sitemap.xml'); sm = open(sp, encoding='utf-8').read()
sm = re.sub(r'<url><loc>' + re.escape(SITE + path) + r'</loc>.*?</url>\n?', '', sm)
sm = sm.replace('</urlset>', f'<url><loc>{SITE}{path}</loc><lastmod>{chk}</lastmod></url>\n</urlset>')
open(sp, 'w', encoding='utf-8').write(sm)
print('ryokin page:', len(D), 'chains')

# 教室ごとのページ（チェーン）に、体験と料金の行を足す
KEYS = {'NAYUTAS': 'NAYUTAS', 'USボーカル教室': 'USボーカル教室', 'シアーミュージック': 'シアーミュージック', '島村楽器': '島村楽器',
        'InspiartZ': 'InspiartZ', 'EYS': 'EYS', 'アバロンミュージックスクール': 'アバロン', '椿音楽教室': '椿音楽教室', 'ヤマハ': 'ヤマハ',
        'avex': 'avex', 'リズムセブン': 'リズムセブン', 'パピーミュージックスクール': 'パピー', 'アミーズボーカルスクール': 'アミーズ', 'カワイ音楽教室': 'カワイ', '劇団ひまわり': '劇団ひまわり'}
def find(name):
    for k, v in KEYS.items():
        if name.startswith(k):
            for d in D:
                if d['chain'].startswith(v) or v in d['chain']: return d
nrow = 0
kroot = os.path.join(ROOT, 'kyoshitsu')
for dp, dn, fn in os.walk(kroot):
    if 'index.html' not in fn or os.sep + 's' + os.sep not in dp + os.sep: continue
    p = os.path.join(dp, 'index.html'); s = open(p, encoding='utf-8').read()
    m = re.search(r'<h1>(.*?)</h1>', s)
    if not m: continue
    s2 = re.sub(r'<tr class="rk-row">.*?</tr>', '', s, flags=re.S)
    d = find(html.unescape(m.group(1)))
    if d:
        t = d.get('trial') or {}
        rows = f'<tr class="rk-row"><th>体験レッスン</th><td>{esc(d.get("trialShort") or "公式サイトでご確認ください")}</td></tr>'
        rows += f'<tr class="rk-row"><th>料金のめやす</th><td><a href="{path}">大手の歌の教室 料金まとめ</a>でくらべられます<br><small>（{cdt}に公式サイトで確認。校舎・地域で変わることがあります）</small></td></tr>'
        s2 = s2.replace('<tr><th>公式サイト</th>', rows + '<tr><th>公式サイト</th>', 1)
        nrow += 1
    if s2 != s: open(p, 'w', encoding='utf-8').write(s2)
print('chain rows:', nrow)

# 都道府県の教室ページに「この県にある大手の教室（体験・料金）」
import csv
PS = {r[0]: r[1] for r in list(csv.reader(open(os.path.join(ROOT, '_build/kyoshitsu/pages-list.csv'), encoding='utf-8-sig')))[1:]}
CL = json.load(open(os.path.join(ROOT, '_build/kyoshitsu/classrooms.json'), encoding='utf-8'))
npref = 0
for pref, slug in PS.items():
    p = os.path.join(ROOT, 'kyoshitsu', slug, 'index.html')
    if not os.path.exists(p): continue
    seen = []
    for x in CL:
        if x.get('prefecture') != pref: continue
        d = find(x['name'])
        if d and d not in seen: seen.append(d)
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--ck-chain-->.*?<!--/ck-chain-->', '', s, flags=re.S)
    if seen:
        li = ''.join(f'<li>{esc(d["chain"].split("（")[0])}：体験 {esc(d.get("trialShort") or "公式サイトでご確認ください")}</li>' for d in seen)
        box = (f'<!--ck-chain--><section class="city-box"><h2>{esc(pref)}にある大手の歌の教室（体験レッスン）</h2><ul class="kl" style="line-height:1.7">{li}</ul>'
               f'<p>入会金・月謝は<a href="{path}">大手の歌の教室 料金まとめ</a>でくらべられます（{cdt}に公式サイトで確認）。</p></section><!--/ck-chain-->')
        if '<!--cities-end-->' in s: s = s.replace('<!--cities-end-->', '<!--cities-end-->' + box, 1)
        else:
            k = s.rfind('</main>'); s = s[:k] + box + s[k:]
        npref += 1
    open(p, 'w', encoding='utf-8').write(s)
print('pref chain boxes:', npref)
