# 使い方: python3 /home/claude/simcheck.py 700 [702 ...]
# 指定した記事と、ほかの全記事との本文の重なり（8文字単位のジャッカード）を表示する
import glob,os,re,sys
def load(n):
    s=open(f'/home/claude/wp-import/md/{n}.md' if n>9 else f'/home/claude/wp-import/md/{n:02d}.md',encoding='utf-8').read()
    s=re.sub(r'こどもの歌声グランプリは.*?リンク】','',s,flags=re.S)
    s=s.replace('わたしは息子といっしょに、たくさんのコンクールに出てきました','')
    s=re.sub(r'教室の内容や募集は変わることがあるので[^。]*。','',s)
    t=re.sub(r'\s|【[^】]*】|https?://\S+','',s)
    return {t[i:i+8] for i in range(len(t)-7)}
ALL={}
for f in glob.glob('/home/claude/wp-import/md/*.md'):
    n=int(os.path.basename(f)[:-3]); ALL[n]=None
for a in map(int,sys.argv[1:]):
    A=load(a); res=[]
    for n in ALL:
        if n==a: continue
        if ALL[n] is None: ALL[n]=load(n)
        B=ALL[n]; j=len(A&B)/max(1,len(A|B)); res.append((round(j,3),n))
    res.sort(reverse=True); print(a,'top:',res[:5])
