#!/usr/bin/env python3
"""旧サイトで日英併記だった記事本文を、日本語版（content/）と英語版（content-en/）に分ける。

  python3 tools/split_articles.py            # 判定と統計だけ表示（何も書かない）
  python3 tools/split_articles.py --write    # content/ を日本語だけに書き換え、content-en/ に英語版を書く

判定は行単位。かなを 3 文字以上含むか、CJK 文字の割合が 3 割以上か、行頭が CJK 文字なら日本語行、それ以外は英語行
（英語の論文題や URL を含む日本語文を英語行にしないため）。WordPress の共有ボタン残骸
（[Tweet] / [シェア]）と連続する罫線は両方から落とす。
画像、空行、英字の著者名列、「関連論文/Related Publications」等のラベルに続くブロック
（引用・リンク・連絡先）は両方に残す。ラベル自体は「/」の前後で分ける。

記事の種別:
  split      日本語段落と英語段落の両方がある → 分ける
  en-only    日本語の地の文がほぼ無い（英語の講演告知など） → 日本語版はそのまま、英語版は本文コピー
  translate  英語の地の文が無い、または断片的 → 手で翻訳する（このスクリプトは触らない）

front matter に pubs: があり、本文の「関連論文」ブロックの件数がそれ以下なら、本文側のブロックは
落とす（テンプレートが front matter から同じ一覧を出すため二重になる）。
英語版の title は titleEn があればそれに置き換える。無いものは一覧に出すので inventory/title_fixes.json に書く
（旧サイトで日英の題が連結されていたものは title も同じファイルで直す）。
"""
import re, sys, glob, os, json

ARCH = 'hugo/content/archives'
ARCH_EN = 'hugo/content-en/archives'
CJK = re.compile(r'[぀-ヿ一-鿿々〆ヵヶ]')
KANA = re.compile(r'[぀-ヿ]')
SHARE = re.compile(r'^\s*\[(Tweet|シェア)\]\(https?://(twitter\.com/share|www\.facebook\.com/sharer)[^)]*\)\s*$')
HR = re.compile(r'^-{3,}\s*$')
LABEL = re.compile(r'^\s*([^/\[]{1,30}?)\s*[/／]\s*([A-Za-z][A-Za-z .\'\-]{1,50}?)\s*$')
IMG = re.compile(r'^\s*!\[')
LINKONLY = re.compile(r'^\s*\[!?\[[^\]]*\](\([^)]*\))?\]\([^)]*\)\s*$|^\s*<?(https?://\S+|[\w.+-]+@[\w.-]+)>?\s*$')
HTMLTAG = re.compile(r'^\s*<')

def cjk_ratio(s):
    chars = [c for c in s if not c.isspace()]
    return (sum(1 for c in chars if CJK.match(c)) / len(chars)) if chars else 0.0

def is_authors(s):
    t = s.strip()
    if not t or CJK.search(t) or t.endswith('.') or len(t) > 300: return False
    words = [w for w in re.split(r'[,\s]+', t) if w]
    if len(words) < 2: return False
    cap = sum(1 for w in words if w[0].isupper() or w in ('and', 'de', 'van', 'von')) / len(words)
    return cap >= 0.85 and ',' in t

def classify(lines):
    """各行に ('ja'|'en'|'both'|'label', ja_text, en_text) を付ける。"""
    out = []; in_block = False
    for l in lines:
        st = l.strip()
        if not st:
            out.append(('both', l, l)); in_block = False; continue
        m = LABEL.match(l)
        if m and CJK.search(m.group(1)) and not CJK.search(m.group(2)):
            trail = l[len(l.rstrip()):]
            out.append(('label', m.group(1) + trail, m.group(2) + trail, l)); in_block = True; continue
        if in_block or IMG.match(l) or HTMLTAG.match(l) or LINKONLY.match(l) or is_authors(l):
            out.append(('both', l, l)); continue
        head = re.sub(r'^[#>*_\s\-]+', '', st)[:1]        # 見出し記号・強調を除いた最初の 1 文字
        ja = len(KANA.findall(st)) >= 3 or cjk_ratio(st) >= 0.3 or bool(CJK.match(head)) or head in '【（「『〜～'
        out.append(('ja' if ja else 'en', l, l))
    return out

def prose_len(rows, kind):
    return sum(len(r[1].strip()) for r in rows if r[0] == kind and not LINKONLY.match(r[1]))

def squeeze(lines):
    res = []
    for l in lines:
        if not l.strip() and res and not res[-1].strip(): continue
        if HR.match(l) and any(HR.match(x) for x in res[-2:]): continue
        res.append(l)
    while res and not res[0].strip(): res.pop(0)
    while res and not res[-1].strip(): res.pop()
    return res

def drop_body_pubs(rows, fm):
    """front matter の pubs 件数 >= 本文の関連論文ブロック件数なら本文ブロックを落とす。"""
    n_fm = len(re.findall(r'^  - citation:', fm, re.M))
    if not n_fm: return rows, None
    i = next((i for i, r in enumerate(rows) if r[0] == 'label' and r[1].startswith('関連論文')), None)
    if i is None: return rows, None
    j = i + 1
    while j < len(rows) and rows[j][1].strip(): j += 1
    n_body = j - i - 1
    if n_body > n_fm: return rows, f'本文の関連論文 {n_body} 件 > front matter {n_fm} 件（残した）'
    return rows[:i] + rows[j:], None

FIXES = json.load(open('inventory/title_fixes.json')) if os.path.exists('inventory/title_fixes.json') else {}

def yaml_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

def fix_titles(wp, fm):
    """inventory/title_fixes.json の title / titleEn を front matter に反映する。"""
    f = FIXES.get(wp)
    if not f: return fm
    if f.get('title'): fm = re.sub(r'^title: .*$', 'title: ' + yaml_str(f['title']), fm, count=1, flags=re.M)
    if f.get('titleEn'):
        fm = re.sub(r'^titleEn: .*\n', '', fm, flags=re.M)
        fm = re.sub(r'^(title: .*\n)', r'\1' + 'titleEn: ' + yaml_str(f['titleEn']) + '\n', fm, count=1, flags=re.M)
    return fm

def process(path):
    s = open(path, encoding='utf-8').read()
    _, fm, body = s.split('---\n', 2)
    fm = fix_titles(os.path.basename(path)[:-3], fm)
    lines = [l for l in body.split('\n') if not SHARE.match(l)]
    rows = classify(lines)
    ja_p, en_p = prose_len(rows, 'ja'), prose_len(rows, 'en')
    en_sent = sum(1 for r in rows if r[0] == 'en' and len(r[1].strip()) >= 100 and ('. ' in r[1] or r[1].rstrip().endswith('.')))
    if ja_p == 0: kind = 'en-only'                                   # 訳すものが無い（画像だけの記事も含む）
    elif en_p >= 100 and ja_p <= max(60, 0.1 * en_p): kind = 'en-only'  # 英語記事に日本語の断片（会議室名など）
    elif en_sent and en_p >= 250 and en_p / ja_p >= 0.35: kind = 'split'  # 英語の地の文（100 字以上の文）がある
    else: kind = 'translate'
    rows, note = drop_body_pubs(rows, fm)
    if kind != 'split':                       # 英語だけ / 翻訳待ち：日本語版の本文は触らない（ラベルも元のまま）
        ja = [r[-1] for r in rows]; en = [r[-1] for r in rows]
    else:
        ja = [r[1] for r in rows if r[0] in ('ja', 'both', 'label')]
        en = [r[2] for r in rows if r[0] in ('en', 'both', 'label')]
    ja = '\n'.join(squeeze(ja)) + '\n'; en = '\n'.join(squeeze(en)) + '\n'
    # 講演告知の会場リンクも英語側の Access に向ける。
    en = re.sub(r'\]\(/access/?\)', '](/en/access/)', en)
    m = re.search(r'^titleEn: (".*")$', fm, re.M)
    fm_en = re.sub(r'^title: .*$', 'title: ' + m.group(1), fm, count=1, flags=re.M) if m else fm
    return dict(kind=kind, ja_p=ja_p, en_p=en_p, note=note, has_title_en=bool(m),
                fm=fm, fm_en=fm_en, ja=ja, en=en, orig=body)

if __name__ == '__main__':
    write = '--write' in sys.argv
    stats = {}; queue = []
    os.makedirs(ARCH_EN, exist_ok=True)
    for path in sorted(glob.glob(f'{ARCH}/*.md'), key=lambda p: int(os.path.basename(p)[:-3])):
        wp = os.path.basename(path)[:-3]
        r = process(path)
        stats.setdefault(r['kind'], []).append(wp)
        flag = ''
        if r['kind'] == 'split' and r['en_p'] / r['ja_p'] < 0.6: flag = ' [要確認: 比率低]'
        if r['note']: flag += ' [' + r['note'] + ']'
        if r['kind'] != 'translate' and not r['has_title_en']: flag += ' [titleEn なし]'
        if r['kind'] != 'translate' or r['note']:
            print(f"{wp}\t{r['kind']}\tja={r['ja_p']}\ten={r['en_p']}{flag}")
        if r['kind'] == 'translate': queue.append(wp)
        if write:
            ja_doc = '---\n' + r['fm'] + '---\n' + r['ja']
            if ja_doc != open(path, encoding='utf-8').read():
                open(path, 'w', encoding='utf-8').write(ja_doc)
            if r['kind'] != 'translate':
                open(f'{ARCH_EN}/{wp}.md', 'w', encoding='utf-8').write('---\n' + r['fm_en'] + '---\n' + r['en'])
    print({k: len(v) for k, v in stats.items()}, file=sys.stderr)
    json.dump(queue, open('inventory/translate_queue.json', 'w'))
    print('翻訳待ち一覧: inventory/translate_queue.json', file=sys.stderr)
