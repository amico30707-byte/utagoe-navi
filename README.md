# うたごえナビ（utagoe-navi.jp）

歌の教室とコンクールを、お子様からシニアの方までさがせるサイトです。
GitHub Pages で公開しています。`_build/` はページを作るための元ファイルです。


## コンクール情報の更新
1. `_build/concours/contests-final.json` を直す（しめきり・日程・参加費・checked の日付）
2. `python3 _build/update_contests.py` を実行
3. コミットしてプッシュ（GitHub Pages に自動で反映）

## 広告（A8）
`python3 _build/ads.py` で、くらべる記事・都道府県ページ・ボイトレ／おとな／シニアの記事に「PR」つきの広告をいれます（なんどでも実行可）。リンクをかえるときは ads.py の ADS を直します。

## 教室ページ・市区町村ページ
`python3 _build/kyoshitsu_pages.py` で、教室ごとのページ（公式サイトで確認できた教室）と、教室が3つ以上ある市区町村のページを作ります。データは `_build/kyoshitsu/classrooms.json`。

## サイトを作りなおしたあとの順番
1. `python3 _build/kyoshitsu_pages.py`
2. `python3 _build/ads.py`
3. `python3 _build/update_contests.py`
