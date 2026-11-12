#!/bin/bash
# 使い方: repub.sh "commit message" N N N ...  (md を直したあと、XML 更新→ビルド→公開)
set -e
MSG="$1"; shift
W=/tmp/claude-0/-home-claude/c7b1aa7e-094d-5d48-a807-2cdf8450c9b8/scratchpad/wxr
cd /home/claude
python3 $W/refresh.py "$@" | tail -c 200
python3 site-build/build.py > /dev/null
(cd utagoe-navi && git stash -q; git pull -q --rebase origin main; git stash pop -q 2>/dev/null || true)
cp -r site/. utagoe-navi/
cd utagoe-navi
for s in kyoshitsu_pages ads update_contests region_contests city_articles deadline_page contest_pages checklist_pages chain_fees; do python3 _build/$s.py > /dev/null; done
git add -A
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Kso9MsKBEHUWi5vqvBhJmm"
git push -q origin main
echo pushed $(git rev-parse --short HEAD) remote $(git ls-remote origin main | cut -c1-7)
