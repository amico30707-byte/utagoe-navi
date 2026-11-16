# 教室・コンクールのページに「掲載のご案内（無料）」の箱を入れる（くりかえし実行してよい）
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = {'kyoshitsu': '<!--lc--><section class="city-box"><h2>教室の先生・合唱団の方へ</h2><p>うたごえナビにのっていない教室・合唱団を募集しています。現在の掲載は無料です。<a href="/contact/">掲載の申しこみはこちら</a>（教室の名前・場所・ジャンル・対象の年代・ホームページを書いてお送りください）。</p></section><!--/lc-->',
       'concours': '<!--lc--><div class="wrap"><p style="background:#fff8ef;border:1px solid #eadfce;border-radius:12px;padding:10px 14px">コンクールの主催者の方へ：のせてほしい大会や、内容の直しがあれば<a href="/contact/">こちら</a>からご連絡ください。現在の掲載は無料です。</p></div><!--/lc-->'}
n = 0
for dp, dn, fn in os.walk(os.path.join(ROOT, 'kyoshitsu')):
    if 'index.html' not in fn or os.sep + 's' + os.sep in dp + os.sep: continue
    p = os.path.join(dp, 'index.html'); s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--lc-->.*?<!--/lc-->', '', s, flags=re.S)
    k = s.rfind('</main>'); s = s[:k] + BOX['kyoshitsu'] + s[k:]
    open(p, 'w', encoding='utf-8').write(s); n += 1
p = os.path.join(ROOT, 'concours', 'index.html'); s = open(p, encoding='utf-8').read()
s = re.sub(r'<!--lc-->.*?<!--/lc-->', '', s, flags=re.S)
k = s.rfind('</main>'); s = s[:k] + BOX['concours'] + s[k:]
open(p, 'w', encoding='utf-8').write(s)
print('listing cta:', n + 1)
