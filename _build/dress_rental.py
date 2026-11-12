# 発表会・コンクール用ドレスのレンタルまとめ（/dress-rental/）をつくる（くりかえし実行してよい）
# データ：_build/data/dress-rental.json（公式サイトでたしかめた内容・出典URL・読者むけの文 show）
import json, os, re, html, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://utagoe-navi.jp'
D = json.load(open(os.path.join(ROOT, '_build/data/dress-rental.json'), encoding='utf-8'))
esc = lambda s: html.escape(s or '', quote=True)
chk = max(d.get('checked', '') for d in D)
cd = datetime.date.fromisoformat(chk)
cdt = f'{cd.year}年{cd.month}月{cd.day}日'

def cell(f):
    f = f or {}
    t = f.get('show') or '公式サイトに記載なし'
    u = f.get('url')
    return esc(t) + (f' <a class="rk-src" href="{esc(u)}" target="_blank" rel="noopener nofollow">出典</a>' if u else '')

cards = {'子ども': [], '大人': []}
for d in D:
    cards.setdefault(d.get('target') or '子ども', []).append(
        f'<section class="rk-c"><h3>{esc(d.get("nameShow") or d["name"])}</h3><dl>'
        f'<dt>料金</dt><dd>{cell(d.get("price"))}</dd>'
        f'<dt>かりる期間</dt><dd>{cell(d.get("period"))}</dd>'
        f'<dt>サイズ</dt><dd>{cell(d.get("sizes"))}</dd>'
        f'<dt>送料</dt><dd>{cell(d.get("shipping"))}</dd>'
        f'<dt>小物・補償など</dt><dd>{cell(d.get("extras"))}</dd>'
        f'<dt>予約</dt><dd>{cell(d.get("reserve"))}</dd></dl></section>')
css = ('<style>.rk{max-width:820px;margin:0 auto;padding:0 16px 40px}.rk h1{font-size:1.45rem;margin:12px 0}.rk>h2{font-size:1.2rem;margin:26px 0 6px}'
       '.rk-c{background:#fff;border:1px solid #eadfce;border-radius:12px;padding:12px 16px;margin:14px 0}.rk-c h3{font-size:1.1rem;margin:0 0 8px;border-left:5px solid #B9530F;padding-left:10px}'
       '.rk-c dl{display:grid;grid-template-columns:7em 1fr;gap:6px 10px;margin:0;font-size:.95rem}.rk-c dt{color:#7a3a0a;font-weight:700}.rk-c dd{margin:0;overflow-wrap:anywhere}'
       '.rk-src{font-size:.8rem;margin-left:4px}.rk-na{color:#5d6482}.rk-box{background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:12px 14px;margin:12px 0}'
       '@media(max-width:480px){.rk-c dl{grid-template-columns:1fr}.rk-c dd{margin-bottom:6px}}</style>')
intro = (f'<h1>発表会・コンクールのドレス レンタルまとめ【{cd.year}年{cd.month}月】子ども・大人</h1>'
         f'<p>歌の発表会やコンクールで着るドレス・スーツを、宅配でかりられるお店をまとめました。料金・かりる期間・サイズ・送料・予約を、各お店の公式サイトでたしかめています（{cdt}に確認）。ならび順に意味はありません。</p>'
         '<div class="rk-box"><p style="margin:0">料金や送料は、商品や時期によって変わります。ここにのせたのは、公式サイトに書かれていた内容をまとめたものです。'
         '申しこむ前に、かならず各お店の公式サイトでご確認ください。「出典」から、たしかめたページを開けます。</p></div>'
         '<p>衣装のえらび方は<a href="/isho/">歌のコンクールの衣装のえらび方</a>、<a href="/happyokai-dress/">発表会・コンクールの服えらび</a>、大人の方は<a href="/seigaku-dress/">声楽のドレスの選び方</a>もごらんください。'
         '当日のもちものは<a href="/checklist/motimono/">もちものチェックリスト</a>で確認できます。</p>')
body = ('<div class="wrap"><nav class="bc" aria-label="パンくずリスト"><a href="/">トップ</a> <span aria-hidden="true">›</span> <span>ドレス レンタルまとめ</span></nav></div>'
        + css + '<div class="rk">' + intro + '<h2>子どものドレス・スーツ</h2>' + ''.join(cards.get('子ども', [])) +
        '<h2>大人のドレス（声楽・演奏会）</h2>' + ''.join(cards.get('大人', [])) +
        '<p style="margin-top:20px">衣装を気にせず、まずはおうちで歌ってみたい方へ。動画で出られる<a href="/grandprix/">こどもの歌声グランプリ</a>もあります。</p></div>')

tpl = open(os.path.join(ROOT, 'concours', 'index.html'), encoding='utf-8').read()
tpl = re.sub(r'<!--(sk-link|cl-nav)-->.*?<!--/\1-->', '', tpl, flags=re.S)
i = tpl.index('<main>'); j = tpl.rindex('</main>')
head, foot = tpl[:i], re.sub(r'<script>\s*\(function\(\)\{\s*const DATA = .*?</script>', '', tpl[j:], flags=re.S)
path = '/dress-rental/'
title = f'発表会・コンクールのドレスレンタルまとめ【{cd.year}年{cd.month}月】子ども・大人｜うたごえナビ'
desc = f'歌の発表会・コンクールで着る子どものドレス・スーツや、大人の声楽ドレスを宅配でかりられるお店{len(D)}社の料金・期間・サイズ・送料を、公式サイトでたしかめてまとめました（{cdt}確認）。'
head = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', head, count=1)
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head, count=1)
head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{SITE}{path}">', head, count=1)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + esc(title), head)
head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>' + SITE + path, head)
head = re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*', r'\g<1>' + esc(desc), head)
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
    {'@type': 'ListItem', 'position': 1, 'name': 'トップ', 'item': SITE + '/'},
    {'@type': 'ListItem', 'position': 2, 'name': 'ドレス レンタルまとめ', 'item': SITE + path}]}
head = head.replace('</head>', f'<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script></head>', 1)
os.makedirs(os.path.join(ROOT, path.strip('/')), exist_ok=True)
open(os.path.join(ROOT, path.strip('/'), 'index.html'), 'w', encoding='utf-8').write(head + '<main>\n' + body + '\n' + foot)

# 入口：教室さがしのトップと、くらべ方の記事
for rel, anchor in (('isho/index.html', 'h2'), ('happyokai-dress/index.html', 'h2'), ('seigaku-dress/index.html', 'h2'), ('happyoukai-hiyou/index.html', 'h2')):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--dr-->.*?<!--/dr-->', '', s, flags=re.S)
    box = f'<!--dr--><p style="background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:10px 14px">発表会・コンクールのドレスを宅配でかりられるお店を、公式サイトでたしかめてまとめました：<a href="{path}">ドレス レンタルまとめ（{cd.year}年{cd.month}月）</a></p><!--/dr-->'
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
print('dress rental page:', len(D))
