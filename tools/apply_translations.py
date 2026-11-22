#!/usr/bin/env python3
"""手で翻訳した記事本文（inventory/archives-en/*.txt）を hugo/content-en/archives/ に流し込む。

  python3 tools/apply_translations.py          # 書き込み
  python3 tools/apply_translations.py --check  # 対応の確認だけ

翻訳ファイルの形式:
  ##### <wpId>
  TITLE: <英語題>
  <本文（Markdown）。段落内の改行はそのまま強制改行になる>

front matter は日本語版（hugo/content/archives/<wpId>.md）を複製し、title を英語題に、titleEn を追加する。
日本語版にも titleEn を書き戻す（英語版が無いページの一覧表示に使うため）。
対象は inventory/translate_queue.json（tools/split_articles.py が書く「翻訳待ち」一覧）。
一覧にあって翻訳が無いもの、翻訳があって一覧に無いものは報告する。
"""
import re, sys, glob, os, json

ARCH = 'hugo/content/archives'
ARCH_EN = 'hugo/content-en/archives'
SRC = 'inventory/archives-en'

def parse():
    items = {}
    for path in sorted(glob.glob(f'{SRC}/*.txt')):
        cur = None
        for line in open(path, encoding='utf-8').read().split('\n'):
            m = re.match(r'^##### (\d+)\s*$', line)
            if m:
                cur = m.group(1); items[cur] = {'title': None, 'body': []}; continue
            if cur is None: continue
            if items[cur]['title'] is None and line.startswith('TITLE: '):
                items[cur]['title'] = line[7:].strip(); continue
            items[cur]['body'].append(line)
    return items

def hardbreaks(lines):
    """段落内の連続行に強制改行（末尾 2 スペース）を付ける。見出し・箇条書き・罫線・HTML・表は除く。"""
    out = []
    for i, l in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        plain = l.strip()
        if plain and nxt.strip() and not re.match(r'^(#|- |\d+\.\s|-{3,}|<|\|)', plain) and not re.match(r'^(#|- |\d+\.\s|-{3,}|<|\|)', nxt.strip()):
            l = l.rstrip() + '  '
        out.append(l)
    while out and not out[0].strip(): out.pop(0)
    while out and not out[-1].strip(): out.pop()
    return out

def yaml_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

if __name__ == '__main__':
    check = '--check' in sys.argv
    items = parse()
    queue = json.load(open('inventory/translate_queue.json'))
    missing = [w for w in queue if w not in items]
    extra = [w for w in items if w not in queue]
    if missing: print('翻訳が無い:', missing, file=sys.stderr)
    if extra: print('翻訳待ち一覧に無い（書き込みはする）:', extra, file=sys.stderr)
    bad = [w for w, it in items.items() if not it['title'] or not any(l.strip() for l in it['body'])]
    if bad: sys.exit(f'題または本文が空: {bad}')
    os.makedirs(ARCH_EN, exist_ok=True)
    n = 0
    for w, it in items.items():
        src = f'{ARCH}/{w}.md'
        if not os.path.exists(src): print('日本語版が無い:', w, file=sys.stderr); continue
        s = open(src, encoding='utf-8').read()
        _, fm, body = s.split('---\n', 2)
        fm_en = re.sub(r'^title: .*$', 'title: ' + yaml_str(it['title']), fm, count=1, flags=re.M)
        if re.search(r'^titleEn: ', fm_en, re.M):
            fm_en = re.sub(r'^titleEn: .*$', 'titleEn: ' + yaml_str(it['title']), fm_en, count=1, flags=re.M)
        else:
            fm_en = re.sub(r'^(title: .*\n)', r'\1' + 'titleEn: ' + yaml_str(it['title']) + '\n', fm_en, count=1, flags=re.M)
        fm_ja = re.sub(r'^titleEn: .*\n', '', fm, flags=re.M)
        fm_ja = re.sub(r'^(title: .*\n)', r'\1' + 'titleEn: ' + yaml_str(it['title']) + '\n', fm_ja, count=1, flags=re.M)
        if check: continue
        open(f'{ARCH_EN}/{w}.md', 'w', encoding='utf-8').write('---\n' + fm_en + '---\n' + '\n'.join(hardbreaks(it['body'])) + '\n')
        if fm_ja != fm: open(src, 'w', encoding='utf-8').write('---\n' + fm_ja + '---\n' + body)
        n += 1
    print(f'{len(items)} 件を読み、{n} 件を書いた', file=sys.stderr)
