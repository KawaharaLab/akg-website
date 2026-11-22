#!/usr/bin/env python3
"""抽出時に YouTube 埋め込みが「# エラーが発生しました。／JavaScript を実行できませんでした。」に
化けた記事（8 件）を、ミラー HTML の <iframe> で復元する。

  python3 tools/fix_embeds.py          # 書き換え
  python3 tools/fix_embeds.py --check  # 対応の確認だけ
"""
import re, sys, glob, os
GARBAGE = re.compile(r'^# エラーが発生しました。\n\nJavaScript を実行できませんでした。\n', re.M)
check = '--check' in sys.argv
for md in sorted(glob.glob('hugo/content/archives/*.md')):
    s = open(md, encoding='utf-8').read()
    n = len(GARBAGE.findall(s))
    if not n: continue
    wp = os.path.basename(md)[:-3]
    html = open(f'site/archives/{wp}/index.html', encoding='utf-8').read()
    iframes = re.findall(r'<iframe[^>]*></iframe>|<iframe[^>]*>', html)
    iframes = [re.sub(r'\s+loading="lazy"', '', f) for f in iframes]
    iframes = [f if f.endswith('</iframe>') else f + '</iframe>' for f in iframes]
    print(f'{wp}: garbage={n} iframes={len(iframes)}', file=sys.stderr)
    if n != len(iframes): print('  数が合わないので飛ばす', file=sys.stderr); continue
    if check: continue
    it = iter(iframes)
    s = GARBAGE.sub(lambda m: '<div class="embed">' + next(it) + '</div>\n', s)
    open(md, 'w', encoding='utf-8').write(s)
