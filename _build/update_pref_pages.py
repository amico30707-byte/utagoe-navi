# directory/build.py のあとに実行：都道府県ページ（pref-pages/*.html）のデータと件数を classrooms.json に合わせる
import json, re, csv, os
D = os.path.dirname(os.path.abspath(__file__))
out = json.load(open(f'{D}/classrooms.json'))
rows = list(csv.reader(open(f'{D}/pref-pages/pages-list.csv', encoding='utf-8-sig')))
hdr, body = rows[0], rows[1:]
for r in body:
    pref, slug = r[0], r[1]
    L = [x for x in out if x['prefecture'] == pref]
    old, n = int(r[5]), len(L)
    p = f'{D}/pref-pages/{slug}.html'; s = open(p).read()
    m = re.search(r'const DATA = (\[.*?\]);\n', s, re.S)
    s = s[:m.start(1)] + json.dumps(L, ensure_ascii=False) + s[m.end(1):]
    if n != old:
        s = s.replace(f'{old}件', f'{n}件')
        r[3] = r[3].replace(f'{old}件', f'{n}件'); r[4] = r[4].replace(f'{old}件', f'{n}件'); r[5] = str(n)
        print(pref, old, '->', n)
    open(p, 'w').write(s)
w = csv.writer(open(f'{D}/pref-pages/pages-list.csv', 'w', encoding='utf-8-sig', newline='')); w.writerow(hdr); w.writerows(body)
