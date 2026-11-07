# 都道府県の教室ページに「この地域で歌を習うときの記事」の箱を入れる（くりかえし実行してよい）
# 順番：kyoshitsu_pages.py → ads.py → update_contests.py → region_contests.py → city_articles.py
import os, re, html, csv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = {  # 県のslug: [記事のslug, ...]
 'hokkaido':['sapporo-uta'],'miyagi':['sendai-uta'],'tokyo':['tokyo-uta','tama-uta'],
 'kanagawa':['yokohama-uta','shonan-uta'],'saitama':['saitama-uta'],'aichi':['nagoya-uta','aichi-uta'],
 'osaka':['osaka-uta','osakafu-uta'],'fukuoka':['fukuoka-uta','kitakyushu-uta'],'hyogo':['kobe-uta'],
 'kyoto':['kyoto-uta'],'hiroshima':['hiroshima-uta'],'chiba':['chiba-uta'],'shizuoka':['shizuoka-uta'],
 'niigata':['niigata-uta'],'okayama':['okayama-uta'],'kumamoto':['kumamoto-uta'],'gifu':['gifu-uta'],
 'kagoshima':['kagoshima-uta'],'nagano':['nagano-uta'],
 'yamaguchi':['yamaguchi-uta'],'mie':['mie-uta'],'oita':['oita-uta'],'nara':['nara-uta'],
 'tochigi':['tochigi-uta'],'shiga':['shiga-uta'],'kagawa':['kagawa-uta'],'okinawa':['okinawa-uta'],
 'toyama':['toyama-uta'],'ishikawa':['ishikawa-uta'],'tottori':['tottori-uta'],'ibaraki':['ibaraki-uta'],
 'gunma':['gunma-uta'],'shimane':['shimane-uta'],'nagasaki':['nagasaki-uta'],'yamanashi':['yamanashi-uta'],
}
def title(slug):
    p = os.path.join(ROOT, slug, 'index.html')
    if not os.path.exists(p): return None
    m = re.search(r'<h1[^>]*>(.*?)</h1>', open(p, encoding='utf-8').read(), re.S)
    return re.sub('<[^>]+>', '', m.group(1)).strip() if m else None
n = 0
for pref, slugs in M.items():
    p = os.path.join(ROOT, 'kyoshitsu', pref, 'index.html')
    if not os.path.exists(p): continue
    items = [(s, title(s)) for s in slugs]
    items = [(s, t) for s, t in items if t]
    if not items: continue
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--ca-start-->.*?<!--ca-end-->', '', s, flags=re.S)
    box = '<!--ca-start--><section class="city-box"><h2>この地域で歌を習うときの記事</h2><ul class="kl">%s</ul></section><!--ca-end-->' % ''.join(
        '<li><a href="/%s/">%s</a></li>' % (sl, html.escape(t)) for sl, t in items)
    if '<!--cities-end-->' in s:
        s = s.replace('<!--cities-end-->', '<!--cities-end-->' + box, 1)
    else:
        i = s.rfind('</main>'); s = s[:i] + box + s[i:]
    open(p, 'w', encoding='utf-8').write(s); n += 1
print('city article boxes:', n)
