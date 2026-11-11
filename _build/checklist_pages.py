# 印刷できるチェックリスト（/checklist/ ほか）をつくり、関係する記事に入口を入れる（くりかえし実行してよい）
import os, re, html, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://utagoe-navi.jp'
esc = lambda s: html.escape(s or '', quote=True)
L = [
 ('motimono', 'コンクール当日のもちものチェックリスト', 'コンクールや発表会の当日に、わすれものがないかを確認するためのリストです。前の日の夜に、ご家族でいっしょにチェックしてみてください。', [
   ('申しこみ・受付', ['受付票・出場のお知らせ（メールなら画面をすぐ出せるように）', '楽譜（歌う人の分と、伴奏者の分）', '参加費の領収書や、当日はらう参加費（必要な大会だけ）', '会場までの地図・電車の時間', '主催者の連絡先']),
   ('衣装・身じたく', ['衣装（しわにならないようにハンガーやカバーで）', 'くつ（はきなれたもの）', '着がえ用の服', '髪をまとめるゴム・ピン', 'ハンカチ・ティッシュ', '安全ピン・ソーイングセット']),
   ('のど・体', ['水やお茶（ふたつきのもの）', 'のどにやさしいあめ（大会の決まりを確認）', 'かるく食べられるもの', 'マスク', 'はおるもの（会場が寒いことがあります）', 'いつも使っている薬（必要な方だけ）']),
   ('そのほか', ['筆記用具（講評のメモに）', '楽譜を入れるファイル', '小銭・交通系ICカード', '撮影のルールの確認（会場で写真や動画をとってよいか）', '先生や伴奏者へのお礼（用意する場合）'])]),
 ('douga', '歌の動画をとる前のチェックリスト', '動画審査のある大会に出す動画を、とる前・とったあとに確認するためのリストです。要項のきまりがなにより大事なので、かならず先に要項を読みましょう。', [
   ('とる前（要項の確認）', ['動画の長さ・曲の長さのきまり', '体のどこまでうつすか（全身・上半身など）', '編集してよいか（カット・音の加工・字幕）', 'ファイルの形式・大きさ・送り方', '伴奏のきまり（生のピアノ・音源・アカペラ）', 'しめきりの日と時間']),
   ('部屋とスマホ', ['スマホを横向き・縦向きのどちらにするか（要項に合わせる）', 'スマホをスタンドなどで動かないようにする', '通知を切る（機内モードなど）', 'ストレージの空き', 'うしろに個人の情報（名前・住所・写真）がうつらない', 'エアコンや外の音が入らない時間をえらぶ', '顔に光が当たるように、窓や照明の向きを見る']),
   ('とったあと', ['さいごまで止まらずにとれているか', '音がわれていないか（イヤホンで聞く）', '顔と口もとが見えるか', '名前や部門など、たのまれた情報を入れたか', '送る前に、ファイル名と送り先をもう一度見る', '送ったあとの確認メールを保存する'])]),
 ('kengaku', '歌の教室の見学・体験レッスン メモ', '歌の教室を見学したり、体験レッスンを受けたりするときのメモです。いくつかの教室をくらべるときに、同じ点を見ておくと決めやすくなります。', [
   ('教室のこと', ['教室の名前と場所', '家からの行き方・かかる時間', '個人レッスンか、グループか', 'レッスンの曜日と時間帯', '月の回数・1回の長さ', '月謝・入会金・教材費など、かかるお金', 'ふりかえができるか', 'やめるときの決まり']),
   ('レッスンのようす', ['先生の話し方・説明のわかりやすさ', 'お子様（ご本人）が楽しそうか', '声やのどへの気くばり（むりな発声をさせないか）', '歌いたい曲・ジャンルを習えるか', '発表会やコンクールの考え方']),
   ('帰ってから', ['ご本人の感想（またやりたいか）', '気になった点・質問したいこと', 'ほかの教室とくらべてみて'])]),
]
LINKS = {'motimono': [310, 12, 49], 'douga': [9, 70, 437], 'kengaku': [400]}
CSS = ('<style>.ck{max-width:760px;margin:0 auto;padding:0 16px 40px}.ck h1{font-size:1.45rem;margin:12px 0}.ck h2{font-size:1.1rem;margin:22px 0 6px;border-left:5px solid #B9530F;padding-left:10px}'
       '.ck ul{list-style:none;padding:0;margin:0}.ck li{display:flex;gap:10px;align-items:flex-start;padding:8px 4px;border-bottom:1px dashed #e3d6c3}'
       '.ck li input{width:20px;height:20px;margin-top:3px;flex:none}.ck .pb{display:inline-block;margin:8px 0;padding:8px 18px;border-radius:999px;border:1px solid #B9530F;background:#fff;color:#B9530F;font-size:1rem;cursor:pointer}'
       '.ck .memo{border:1px solid #d9c6ad;border-radius:8px;min-height:90px;margin-top:6px}.ck-nav a{display:inline-block;margin:4px 6px 4px 0;padding:4px 12px;border:1px solid #d9c6ad;border-radius:999px;background:#fff;text-decoration:none;font-size:.9rem}'
       '@media print{header,footer,.bc,.pb,.ck-nav,.noprint,.ad,.ads,[class*="ad-"]{display:none!important}.ck{max-width:none;padding:0}.ck li{padding:5px 0}body{background:#fff}}</style>')
tpl = open(os.path.join(ROOT, 'concours', 'index.html'), encoding='utf-8').read()
i = tpl.index('<main>'); j = tpl.rindex('</main>')
HEAD = tpl[:i]; FOOT = re.sub(r'<script>\s*\(function\(\)\{\s*const DATA = .*?</script>', '', tpl[j:], flags=re.S)
nav = '<p class="ck-nav">' + ''.join(f'<a href="/checklist/{s}/">{t}</a>' for s, t, _, _ in L) + '</p>'
def write(path, title, desc, body, crumbs):
    head = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', HEAD, count=1)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head, count=1)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{SITE}{path}">', head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + esc(title), head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>' + SITE + path, head)
    head = re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*', r'\g<1>' + esc(desc), head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
    bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': k + 1, 'name': n, 'item': SITE + u} for k, (n, u) in enumerate(crumbs)]}
    head = head.replace('</head>', f'<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script></head>', 1)
    bch = ' <span aria-hidden="true">›</span> '.join([f'<a href="{u}">{n}</a>' for n, u in crumbs[:-1]] + [f'<span>{crumbs[-1][0]}</span>'])
    out = head + '<main>\n' + f'<div class="wrap"><nav class="bc" aria-label="パンくずリスト">{bch}</nav></div>' + CSS + '<div class="ck">' + body + '</div>\n' + FOOT
    os.makedirs(os.path.join(ROOT, path.strip('/')), exist_ok=True)
    open(os.path.join(ROOT, path.strip('/'), 'index.html'), 'w', encoding='utf-8').write(out)
made = []
for s, t, intro, secs in L:
    b = f'<h1>{esc(t)}</h1><p>{esc(intro)}</p><button class="pb" type="button" onclick="window.print()">このページを印刷する</button><p class="noprint" style="font-size:.9rem;color:#5d6482">画面でもチェックを入れられます（ページをとじると消えます）。</p>'
    for h, items in secs:
        b += f'<h2>{esc(h)}</h2><ul>' + ''.join(f'<li><input type="checkbox" aria-label="{esc(x)}"><span>{esc(x)}</span></li>' for x in items) + '</ul>'
    b += '<h2>メモ</h2><div class="memo"></div>'
    b += '<div class="noprint"><h2>ほかのチェックリスト</h2>' + nav + '<p>動画だけで出られる<a href="/grandprix/">こどもの歌声グランプリ</a>もあります。</p></div>'
    write(f'/checklist/{s}/', f'{t}（印刷できます）｜うたごえナビ', intro[:110], b, [('トップ', '/'), ('チェックリスト', '/checklist/'), (t, f'/checklist/{s}/')])
    made.append(f'/checklist/{s}/')
hub = '<h1>印刷できるチェックリスト</h1><p>歌のコンクールや教室えらびのときに使える、チェックリストをまとめました。印刷しても、スマホの画面で使ってもかまいません。</p><ul>' + \
      ''.join(f'<li style="display:block"><a href="/checklist/{s}/">{esc(t)}</a><br><small>{esc(intro)}</small></li>' for s, t, intro, _ in L) + '</ul>'
write('/checklist/', '歌のコンクール・教室えらびのチェックリスト（印刷できます）｜うたごえナビ', 'コンクール当日のもちもの、動画をとる前の確認、教室の見学メモ。印刷して使えるチェックリストです。', hub, [('トップ', '/'), ('チェックリスト', '/checklist/')])
made.append('/checklist/')
# 関係する記事に入口
import csv
idx = os.path.join(os.path.dirname(ROOT), 'wp-import', 'articles-index.csv')
n = 0
if os.path.exists(idx):
    rows = list(csv.reader(open(idx, encoding='utf-8')))
    hdr = rows[0]; si = hdr.index('slug') if 'slug' in hdr else None
    if si is not None:
        num2slug = {r[0]: r[si] for r in rows[1:]}
        for s, t, _, _ in L:
            for a in LINKS[s]:
                sl = num2slug.get(str(a))
                p = sl and os.path.join(ROOT, sl, 'index.html')
                if not p or not os.path.exists(p): continue
                h = open(p, encoding='utf-8').read()
                h = re.sub(r'<!--ck-->.*?<!--/ck-->', '', h, flags=re.S)
                box = f'<!--ck--><p style="background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:10px 14px">印刷して使える<a href="/checklist/{s}/">{esc(t)}</a>もあります。</p><!--/ck-->'
                k = h.find('<div class="art-body">')
                if k < 0: continue
                k = h.find('<h2', k)
                if k < 0: continue
                h = h[:k] + box + h[k:]
                open(p, 'w', encoding='utf-8').write(h); n += 1
sp = os.path.join(ROOT, 'sitemap.xml'); sm = open(sp, encoding='utf-8').read()
sm = re.sub(r'<url><loc>' + re.escape(SITE) + r'/checklist/(?:[a-z]+/)?</loc>.*?</url>\n?', '', sm)
sm = sm.replace('</urlset>', ''.join(f'<url><loc>{SITE}{u}</loc></url>\n' for u in made) + '</urlset>')
open(sp, 'w', encoding='utf-8').write(sm)
print('checklist pages:', len(made), 'article links:', n)
