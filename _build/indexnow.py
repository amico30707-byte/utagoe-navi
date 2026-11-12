# IndexNow（Bing など）に、きょう更新したページを知らせる。GitHub Actions から実行
import re, json, os, sys, datetime, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = '3b8d85f836631b2b73002adf6fa6c666'
JST = datetime.timezone(datetime.timedelta(hours=9))
days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
since = (datetime.datetime.now(JST).date() - datetime.timedelta(days=days - 1)).isoformat()
sm = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
urls = [u for u, d in re.findall(r'<loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?', sm) if not d or d[:10] >= since]
urls = urls[:10000]
print('urls:', len(urls))
if not urls: sys.exit(0)
body = json.dumps({'host': 'utagoe-navi.jp', 'key': KEY, 'keyLocation': f'https://utagoe-navi.jp/{KEY}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    print('status:', urllib.request.urlopen(req, timeout=30).status)
except Exception as e:
    print('error:', e)
