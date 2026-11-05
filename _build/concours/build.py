import re,json
t=open('template.html').read()
data=json.load(open('contests-final.json'))
open('kodomo-uta-concours.html','w').write(t.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__DATE__','2026年11月'))
# WordPress version (scoped CSS, prefixed ids, IIFE, light only)
style=re.search(r'<style>(.*?)</style>',t,re.S).group(1)
style=re.sub(r'@media \(prefers-color-scheme: dark\)\{:root:not\(\[data-theme="light"\]\)\{.*?\}\}','',style,flags=re.S)
style=re.sub(r':root\[data-theme="dark"\]\{.*?\}','',style,flags=re.S)
style=style.replace(':root{','#kuco{').replace('*{box-sizing:border-box}','#kuco,#kuco *{box-sizing:border-box}')
style=re.sub(r'\nbody\{([^}]*)\}',r'\n#kuco{\1}',style)
def pref(block):
    out=[]
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}',block):
        sels=re.sub(r'/\*.*?\*/','',m.group(1),flags=re.S).strip(); body=m.group(2)
        if not sels: continue
        if sels.startswith('#kuco'): out.append(f'{sels}{{{body}}}'); continue
        out.append(','.join('#kuco '+s.strip() for s in sels.split(','))+'{'+body+'}')
    return '\n'.join(out)
res=[];i=0
for m in re.finditer(r'@media[^{]+\{((?:[^{}]*\{[^{}]*\})*)\s*\}',style):
    res.append(pref(style[i:m.start()])); res.append(m.group(0).split('{',1)[0]+'{'+pref(m.group(1))+'}'); i=m.end()
res.append(pref(style[i:]))
css='\n'.join(res).replace('padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 56px','padding:8px 0 40px').replace('#kuco header h1','#kuco header .kuco-h1')
body=t.split('</style>',1)[1].replace('<div class="wrap">','<div id="kuco"><div class="wrap">',1).replace('\n<script>','\n</div>\n<script>\n(function(){',1)
idx=body.rfind('</script>'); body=body[:idx]+'})();\n'+body[idx:]
body=body.replace('<h1>','<h2 class="kuco-h1">').replace('</h1>','</h2>')
for i_ in ['q','ages','genres','region','methods','status','within','reset','count','sort','list']:
    body=body.replace(f'id="{i_}"',f'id="kuco-{i_}"').replace(f'for="{i_}"',f'for="kuco-{i_}"').replace(f'$("{i_}")',f'$("kuco-{i_}")')
body=body.replace('document.querySelectorAll(".chip")','document.querySelectorAll("#kuco .chip")')
head='<!-- 歌のコンクールさがし：WordPressの「カスタムHTML」ブロックに、このファイルの中身をすべて貼りつけてください -->\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&family=Noto+Sans+JP:wght@400;500;700&display=swap">\n'
open('concours-wordpress.html','w').write(head+'<style>\n'+css+'\n</style>'+body.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__DATE__','2026年11月'))
print(len(data))
