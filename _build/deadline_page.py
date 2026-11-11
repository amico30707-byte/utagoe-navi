# しめきりカレンダー（/concours/shimekiri/）と、カレンダー用ファイル（/concours/shimekiri.ics）をつくる
# 順番：update_contests.py のあとに実行（くりかえし実行してよい）
import json, os, re, html, datetime, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, '_build/concours/contests-final.json'), encoding='utf-8'))
JST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.datetime.now(JST).date()
WD = '月火水木金土日'
esc = lambda s: html.escape(s or '', quote=True)
METHOD = {'venue': '会場で歌う', 'video': '動画で出る', 'video-venue': '動画のあと会場へ'}

# 大会ごとにまとめる（同じ大会の地区・部門は、いちばん近いしめきりを代表にする）
fam = {}
for c in D:
    dl = c.get('deadline')
    if not dl or c.get('id') == 'grandprix': continue
    d = datetime.date.fromisoformat(dl)
    if d < TODAY: continue
    f = fam.setdefault(c['family'], {'items': [], 'first': None})
    f['items'].append((d, c))
for f in fam.values():
    f['items'].sort(key=lambda x: x[0])
    f['first'] = f['items'][0]
groups = sorted(fam.values(), key=lambda f: f['first'][0])

def gcal(name, d, url):
    q = {'action': 'TEMPLATE', 'text': f'しめきり：{name}', 'dates': f'{d:%Y%m%d}/{d + datetime.timedelta(days=1):%Y%m%d}',
         'details': f'くわしくは公式サイトで確認：{url}\nうたごえナビ https://utagoe-navi.jp/concours/'}
    return 'https://calendar.google.com/calendar/render?' + urllib.parse.urlencode(q)

rows = []; cur = None; ics = []
for f in groups:
    d, c = f['first']
    ym = f'{d.year}年{d.month}月'
    if ym != cur:
        if cur: rows.append('</ul></section>')
        rows.append(f'<section class="sk-m"><h2>{ym}にしめきり</h2><ul class="sk-l">')
        cur = ym
    name = c['name'] + (f'（{c["subtitle"]}）' if c.get('subtitle') and len(f['items']) == 1 else '')
    href = c.get('guide') or c.get('source') or '/concours/'
    more = f'<span class="sk-n">地区・部門によって日程がちがいます（{len(f["items"])}件）</span>' if len(f['items']) > 1 else ''
    ages = '・'.join(c.get('ages', [])[:4])
    left = (d - TODAY).days
    soon = '<span class="sk-soon">もうすぐ</span>' if left <= 14 else ''
    rows.append(
        f'<li><p class="sk-d">{d.month}月{d.day}日（{WD[d.weekday()]}）{soon}</p>'
        f'<p class="sk-t"><a href="{esc(href)}">{esc(name)}</a></p>'
        f'<p class="sk-i">{esc(METHOD.get(c.get("method"), ""))}{" ・ " + esc(ages) if ages else ""}{" ・ " + esc(c.get("feeText", "")) if c.get("feeText") else ""}</p>'
        f'{more}<p class="sk-a"><a href="{esc(gcal(c["name"], d, c.get("source", "")))}" target="_blank" rel="noopener">Googleカレンダーに入れる</a></p></li>')
    for dd, cc in f['items']:
        uid = f'{cc["id"]}@utagoe-navi.jp'
        summ = cc['name'] + (f'（{cc["subtitle"]}）' if cc.get('subtitle') else '')
        ics.append('BEGIN:VEVENT\r\nUID:%s\r\nDTSTAMP:%sT000000Z\r\nDTSTART;VALUE=DATE:%s\r\nDTEND;VALUE=DATE:%s\r\nSUMMARY:%s\r\nDESCRIPTION:%s\r\nURL:%s\r\nEND:VEVENT\r\n' % (
            uid, f'{TODAY:%Y%m%d}', f'{dd:%Y%m%d}', f'{dd + datetime.timedelta(days=1):%Y%m%d}',
            ('しめきり：' + summ).replace(',', '\\,').replace(';', '\\;'),
            ('くわしくは公式サイトでご確認ください ' + cc.get('source', '')).replace(',', '\\,').replace(';', '\\;'),
            cc.get('source', 'https://utagoe-navi.jp/concours/')))
if cur: rows.append('</ul></section>')

css = ('<style>.sk{max-width:760px;margin:0 auto;padding:0 16px 40px}.sk h1{font-size:1.5rem;margin:12px 0}'
       '.sk-m h2{font-size:1.15rem;margin:28px 0 8px;border-left:5px solid #B9530F;padding-left:10px}'
       '.sk-l{list-style:none;padding:0;margin:0}.sk-l li{background:#fff;border:1px solid #eadfce;border-radius:12px;padding:12px 14px;margin:10px 0}'
       '.sk-d{font-weight:700;margin:0;color:#7a3a0a}.sk-soon{display:inline-block;margin-left:8px;font-size:.8rem;background:#fbeee4;color:#b4541b;border-radius:8px;padding:1px 8px}'
       '.sk-t{margin:4px 0;font-size:1.05rem}.sk-i,.sk-n{margin:2px 0;color:#5d6482;font-size:.9rem;display:block}.sk-a{margin:6px 0 0;font-size:.9rem}'
       '.sk-box{background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:12px 14px;margin:12px 0}</style>')
intro = (f'<h1>歌のコンクール しめきりカレンダー</h1>'
         f'<p>これからしめきりがくる歌のコンクールを、しめきりの近い順にならべました（{TODAY.year}年{TODAY.month}月{TODAY.day}日時点）。同じ大会で地区や部門がいくつかあるときは、いちばん近いしめきりをのせています。</p>'
         '<div class="sk-box"><p style="margin:0">「Googleカレンダーに入れる」をおすと、しめきりの日を自分のカレンダーに入れられます。'
         'ぜんぶまとめてカレンダーに入れたいときは、<a href="/concours/shimekiri.ics">カレンダー用ファイル（.ics）</a>をつかってください。</p></div>'
         '<p>しめきりや参加費は変わることがあります。お申し込みの前に、かならず各コンクールの公式サイトでご確認ください。条件をしぼってさがすときは<a href="/concours/">コンクールさがし</a>へ。</p>')
body = '<div class="wrap"><nav class="bc" aria-label="パンくずリスト"><a href="/">トップ</a> <span aria-hidden="true">›</span> <a href="/concours/">コンクールさがし</a> <span aria-hidden="true">›</span> <span>しめきりカレンダー</span></nav></div>' + css + '<div class="sk">' + intro + ''.join(rows) + \
       '<p style="margin-top:28px"><a href="/grandprix/">動画で出られる「こどもの歌声グランプリ」</a>もあります。</p></div>'

tpl = open(os.path.join(ROOT, 'concours', 'index.html'), encoding='utf-8').read()
i = tpl.index('<main>'); j = tpl.rindex('</main>')
head = tpl[:i]
title = '歌のコンクール しめきりカレンダー｜子どもからシニアまで｜うたごえナビ'
desc = f'これからしめきりの歌のコンクールを、しめきりの近い順にまとめました。Googleカレンダーに入れるボタンつき。童謡・声楽・合唱・ミュージカルなど{len(groups)}大会。'
head = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', head, count=1)
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head, count=1)
head = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://utagoe-navi.jp/concours/shimekiri/">', head, count=1)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + esc(title), head)
head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>https://utagoe-navi.jp/concours/shimekiri/', head)
head = re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*', r'\g<1>' + esc(desc), head)
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
out = head + '<main>\n' + body + '\n' + tpl[j:]
out = re.sub(r'<script>\s*\(function\(\)\{\s*const DATA = .*?</script>', '', out, flags=re.S)
os.makedirs(os.path.join(ROOT, 'concours', 'shimekiri'), exist_ok=True)
open(os.path.join(ROOT, 'concours', 'shimekiri', 'index.html'), 'w', encoding='utf-8').write(out)
open(os.path.join(ROOT, 'concours', 'shimekiri.ics'), 'w', encoding='utf-8', newline='').write(
    'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//utagoe-navi.jp//shimekiri//JA\r\nX-WR-CALNAME:歌のコンクール しめきり（うたごえナビ）\r\nCALSCALE:GREGORIAN\r\n' + ''.join(ics) + 'END:VCALENDAR\r\n')

# コンクールさがしのページに、カレンダーへの入口を入れる
p = os.path.join(ROOT, 'concours', 'index.html')
s = open(p, encoding='utf-8').read()
s = re.sub(r'<!--sk-link-->.*?<!--/sk-link-->', '', s, flags=re.S)
link = '<!--sk-link--><div class="wrap" style="margin:8px auto"><p style="background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:10px 14px;margin:0">しめきりの近い順に見たいときは <a href="/concours/shimekiri/">しめきりカレンダー</a>（Googleカレンダーに入れられます）</p></div><!--/sk-link-->'
s = s.replace('</nav></div>', '</nav></div>' + link, 1)
open(p, 'w', encoding='utf-8').write(s)

# サイトマップ
sp = os.path.join(ROOT, 'sitemap.xml')
sm = open(sp, encoding='utf-8').read()
u = 'https://utagoe-navi.jp/concours/shimekiri/'
sm = re.sub(r'<url><loc>' + re.escape(u) + r'</loc>.*?</url>\n?', '', sm)
sm = sm.replace('</urlset>', f'<url><loc>{u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n</urlset>')
open(sp, 'w', encoding='utf-8').write(sm)
print('shimekiri:', len(groups), 'contests,', len(ics), 'calendar events')
