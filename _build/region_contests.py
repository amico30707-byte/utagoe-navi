# 都道府県の教室ページに「この地方のコンクール」の箱を入れる（くりかえし実行してよい）
# 順番：kyoshitsu_pages.py → ads.py → update_contests.py → region_contests.py
import json, re, os, html, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, '_build/concours/contests-final.json'), encoding='utf-8'))
TODAY = datetime.date.today().isoformat()
P = {  # slug: (県名, 地方のよび名)
 'hokkaido':('北海道',['北海道']),'aomori':('青森',['東北']),'iwate':('岩手',['東北']),'miyagi':('宮城',['東北']),'akita':('秋田',['東北']),
 'yamagata':('山形',['東北']),'fukushima':('福島',['東北']),'ibaraki':('茨城',['関東']),'tochigi':('栃木',['関東']),'gunma':('群馬',['関東']),
 'saitama':('埼玉',['関東']),'chiba':('千葉',['関東']),'tokyo':('東京',['関東']),'kanagawa':('神奈川',['関東']),'niigata':('新潟',['中部']),
 'toyama':('富山',['中部']),'ishikawa':('石川',['中部']),'fukui':('福井',['中部']),'yamanashi':('山梨',['中部','関東']),'nagano':('長野',['中部']),
 'gifu':('岐阜',['東海','中部']),'shizuoka':('静岡',['東海','中部']),'aichi':('愛知',['東海','中部']),'mie':('三重',['東海','近畿','関西']),
 'shiga':('滋賀',['近畿','関西']),'kyoto':('京都',['近畿','関西']),'osaka':('大阪',['近畿','関西']),'hyogo':('兵庫',['近畿','関西']),
 'nara':('奈良',['近畿','関西']),'wakayama':('和歌山',['近畿','関西']),'tottori':('鳥取',['中国・四国']),'shimane':('島根',['中国・四国']),
 'okayama':('岡山',['中国・四国']),'hiroshima':('広島',['中国・四国']),'yamaguchi':('山口',['中国・四国']),'tokushima':('徳島',['中国・四国']),
 'kagawa':('香川',['中国・四国']),'ehime':('愛媛',['中国・四国']),'kochi':('高知',['中国・四国']),'fukuoka':('福岡',['九州・沖縄']),
 'saga':('佐賀',['九州・沖縄']),'nagasaki':('長崎',['九州・沖縄']),'kumamoto':('熊本',['九州・沖縄']),'oita':('大分',['九州・沖縄']),
 'miyazaki':('宮崎',['九州・沖縄']),'kagoshima':('鹿児島',['九州・沖縄']),'okinawa':('沖縄',['九州・沖縄'])}

def esc(s): return html.escape(s or '', quote=True)

def item(c):
    href = c.get('guide') or '/concours/'
    dl = c.get('deadline') or ''
    meta = []
    meta.append({'venue':'会場','video':'動画','video-venue':'動画→会場'}.get(c.get('method'),''))
    if c.get('ages'): meta.append('・'.join(c['ages'][:3]) + ('など' if len(c['ages'])>3 else ''))
    if dl: meta.append('しめきり ' + dl[5:].replace('-','/'))
    name = c['name'] + ('（%s）' % c['subtitle'] if c.get('subtitle') else '')
    return '<li><a href="%s">%s</a><br><span class="kc-m">%s</span></li>' % (esc(href), esc(name), esc(' ・ '.join(m for m in meta if m)))

n = 0
for slug, (ken, regs) in P.items():
    p = os.path.join(ROOT, 'kyoshitsu', slug, 'index.html')
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<!--rc-start-->.*?<!--rc-end-->', '', s, flags=re.S)
    live = [c for c in D if c['id'] != 'grandprix' and (not c.get('deadline') or c['deadline'] >= TODAY)]
    local = [c for c in live if ken in (c.get('place') or '')]
    near = [c for c in live if c not in local and c.get('region') in regs]
    seen = set(); pick = []
    for c in sorted(local, key=lambda c: c.get('deadline') or '9') + sorted(near, key=lambda c: c.get('deadline') or '9'):
        if c['family'] in seen: continue
        seen.add(c['family']); pick.append(c)
        if len(pick) >= 6: break
    video = [c for c in live if c.get('method') == 'video' and c['family'] not in seen]
    vpick = []
    for c in sorted(video, key=lambda c: c.get('deadline') or '9'):
        if c['family'] in seen: continue
        seen.add(c['family']); vpick.append(c)
        if len(vpick) >= 3: break
    if not pick and not vpick: continue
    box = '<!--rc-start--><section class="city-box"><h2>%sの近くで出られる歌のコンクール</h2>' % esc(ken + ('都' if ken=='東京' else '府' if ken in ('大阪','京都') else '' if ken=='北海道' else '県'))
    if pick: box += '<ul class="kl">%s</ul>' % ''.join(item(c) for c in pick)
    if vpick: box += '<p class="kt-n">家から動画で出られるコンクール</p><ul class="kl">%s</ul>' % ''.join(item(c) for c in vpick)
    box += '<p><a href="/concours/">コンクールをもっと見る</a> ／ <a href="/grandprix/">動画で出られる「こどもの歌声グランプリ」</a></p><p class="kt-n">日程や参加費は、かならず各コンクールの公式サイトでご確認ください。</p></section><!--rc-end-->'
    if '<!--cities-end-->' in s:
        s = s.replace('<!--cities-end-->', '<!--cities-end-->' + box, 1)
    else:
        i = s.rfind('</main>'); s = s[:i] + box + s[i:]
    open(p, 'w', encoding='utf-8').write(s); n += 1
print('region boxes:', n)
