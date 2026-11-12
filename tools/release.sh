#!/usr/bin/env bash
# 上線：用「正式版」組建（只放老師審過的內容）→ commit → push → 再把本機恢復成含待審內容的預覽版
# 用法：bash tools/release.sh "commit 訊息"
set -e
cd "$(dirname "$0")/.."
MSG="${1:-更新}"
python -I -X utf8 tools/build_data.py .
node build.js
git add -A
git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q
git log --oneline -1
# 恢復本機預覽（含待審）
python -I -X utf8 tools/build_data.py . --drafts >/dev/null
node build.js --drafts >/dev/null
echo "已上線；本機已恢復成預覽版（含待審內容，勿直接 commit）"
