#!/bin/sh
# 記事の日英分割と翻訳の流し込みを、スナップショットからやり直す。
# tools/split_articles.py は日英併記の元ファイルにしか使えない（分割後の日本語ファイルを入力にすると
# 全部「翻訳待ち」になる）ので、必ずこの手順で通す。プロジェクトルートで実行する。
set -e
SNAP=archive/hugo-content-archives-20260905.tgz   # fix_embeds.py 適用後、分割前の content/archives
rm -rf hugo/content/archives hugo/content-en/archives
tar xzf "$SNAP"
python3 tools/fix_tables.py
python3 tools/split_articles.py --write > /dev/null
python3 tools/apply_translations.py
echo "done: $(ls hugo/content/archives | wc -l) ja, $(ls hugo/content-en/archives | wc -l) en"
