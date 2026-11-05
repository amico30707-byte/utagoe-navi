#!/usr/bin/env python3
"""コンクール情報の更新用。
1) _build/concours/contests-final.json を直す
2) リポジトリのルートで  python3 _build/update_contests.py  を実行
   → /concours/index.html と トップ(index.html)の「しめきりが近いコンクール」が作り直される
"""
import json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, '_build', 'concours')
subprocess.run([sys.executable, 'build.py'], cwd=C, check=True)
frag = open(os.path.join(C, 'concours-wordpress.html')).read()
frag = re.sub(r'<!--.*?-->', '', frag, count=1, flags=re.S).replace('https://utagoe-navi.jp/', '/')
p = os.path.join(ROOT, 'concours', 'index.html')
page = open(p).read()
i = page.index('<main>\n'); j = page.rindex('</main>')
main = page[i+6:j]
k = main.index('</nav></div>') + len('</nav></div>')
page = page[:i+6] + main[:k] + frag + '\n' + page[j:]
open(p, 'w').write(page)
data = json.load(open(os.path.join(C, 'contests-final.json')))
items = [{"n": x["name"], "s": x.get("subtitle", ""), "d": x["deadline"], "m": x["method"], "f": x.get("family", ""),
          "a": "・".join(x["ages"][:3]) + ("など" if len(x["ages"]) > 3 else "")} for x in data if x.get("deadline")]
tp = os.path.join(ROOT, 'index.html')
top = open(tp).read()
m = re.search(r'var D=(\{.*?\});\n', top, re.S)
D = json.loads(m.group(1)); D['c'] = items
top = top[:m.start(1)] + json.dumps(D, ensure_ascii=False) + top[m.end(1):]
open(tp, 'w').write(top)
print('updated', len(data), 'contests;', len(items), 'with deadlines')
