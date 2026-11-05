# うたごえナビ（utagoe-navi.jp）

歌の教室とコンクールを、お子様からシニアの方までさがせるサイトです。
GitHub Pages で公開しています。`_build/` はページを作るための元ファイルです。


## コンクール情報の更新
1. `_build/concours/contests-final.json` を直す（しめきり・日程・参加費・checked の日付）
2. `python3 _build/update_contests.py` を実行
3. コミットしてプッシュ（GitHub Pages に自動で反映）
