#!/usr/bin/env python3
"""A8の広告をページに入れる（なんどでも実行してだいじょうぶ）。
python3 _build/ads.py   ※リポジトリのルートで実行
"""
import os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def ad(mat, host, text):
    return (f'<a href="https://px.a8.net/svt/ejp?a8mat={mat}" rel="nofollow sponsored" target="_blank">{text}</a>'
            f'<img border="0" width="1" height="1" src="https://{host}.a8.net/0.gif?a8mat={mat}" alt="" loading="lazy">')

ADS = {
  'sheer':  ad('4BGDZ7+94NDSI+2UVW+6XP76', 'www12', 'シアーミュージックの公式サイトはこちら'),
  'nayutas':ad('4BGDZ7+8TC5AQ+4GDM+C164Y', 'www14', 'NAYUTAS（ナユタス）ボイトレスクールの公式サイト'),
  'eys':    ad('4BGDZ7+8SQPOY+3H64+65EOI', 'www10', '生ピアノで歌う　ヴォーカル教室'),
  'avalon': ad('4BGDZ7+941Y6Q+4FRO+60OXE', 'www16', '【アバロンミュージックスクール】'),
  'wacca':  ad('4BGDZ7+9A0A8I+5OGK+5YJRM', 'www19', '東京のボイトレならWACCA MUSIC SCHOOL'),
}
PR = '<span class="pr-tag">PR</span>'
START, END = '<!--ads-start-->', '<!--ads-end-->'

def box(title, lead, keys):
    items = ''.join(f'<li>{ADS[k]}</li>' for k in keys)
    return (f'{START}<aside class="ad-box"><p class="ad-box-t">{PR}{title}</p><p class="ad-box-l">{lead}</p>'
            f'<ul>{items}</ul><p class="ad-box-n">広告のリンクです。料金や教室の場所は、公式サイトでたしかめてください。</p></aside>{END}')

def strip(s):
    return re.sub(re.escape(START) + r'.*?' + re.escape(END), '', s, flags=re.S)

def save(p, s):
    open(p, 'w').write(s)

n = 0
# 1) くらべる記事：表のリンクを広告リンクに、各教室の最後に案内
p = 'voitore-kyoshitsu-hikaku/index.html'
s = strip(open(p).read())
swap = {'https://www.sheer.jp/': 'sheer', 'https://nayutas.net/': 'nayutas',
        'https://eys-musicschool.com/': 'eys', 'https://www.avalon-works.com/': 'avalon'}
for url, k in swap.items():
    s = re.sub(r'<a href="' + re.escape(url) + r'"[^>]*>[^<]*</a>', START + ADS[k] + PR + END, s, count=1)
for h, k in [('シアーミュージック', 'sheer'), ('NAYUTAS（ナユタス）', 'nayutas'), ('EYS音楽教室 / EYS-Kids', 'eys'), ('アバロンミュージックスクール', 'avalon')]:
    m = re.search(r'<h2>' + re.escape(h) + r'</h2>', s)
    if not m: continue
    nxt = s.find('<h2>', m.end())
    cta = f'{START}<p class="ad-cta">{PR}{ADS[k]}</p>{END}'
    s = s[:nxt] + cta + s[nxt:]
save(p, s); n += 1

# 2) 都道府県ページ：はじめの説明のあとに案内
for p in glob.glob('kyoshitsu/*/index.html'):
    s = strip(open(p).read())
    keys = ['wacca', 'sheer', 'nayutas', 'avalon'] if '/tokyo/' in p else ['sheer', 'nayutas', 'avalon']
    b = box('全国やオンラインで習える教室', '近くに合う教室が見つからないときは、全国に教室がある大手の教室や、オンラインのレッスンも候補になります。', keys)
    i = s.find('</div>', s.find('class="kuta-intro"'))
    if i < 0: continue
    s = s[:i+6] + b + s[i+6:]
    save(p, s); n += 1

# 3) ボイトレ・おとな・シニアの記事：本文のおわりに案内
for p in glob.glob('*/index.html'):
    s = open(p).read()
    if '<article class="art' not in s or 'voitore-kyoshitsu-hikaku' in p: continue
    tags = re.findall(r'href="/tag/([a-z]+)/"', s[s.find('art-tags'):s.find('art-tags')+600]) if 'art-tags' in s else []
    if not set(tags) & {'voitore', 'otona', 'senior'}: continue
    s = strip(s)
    b = box('ボイトレの無料体験ができる教室', '体験レッスンで先生との相性をたしかめるのが、いちばんの近道です。',
            ['sheer', 'nayutas', 'avalon'])
    i = s.find('<p class="art-tags">')
    s = s[:i] + b + s[i:]
    save(p, s); n += 1
print('pages updated:', n)
