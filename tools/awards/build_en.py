#!/usr/bin/env python3
"""content/awardsmedia*.md（日本語）から content-en/awardsmedia*.md（英語）を再生成する。

翻訳そのものは JSON に入っている（機械翻訳はしない）：
  items.json      年ページ AWARDS 欄の項目（id, year, sec, ja=元HTML, auto=辞書変換後）
  media.json      年ページ MEDIA 欄の項目（同上）
  en_awards.json  id -> 英訳（<a> は空タグで書き、href は元HTMLから復元する）
  en_media.json   id -> 英訳
  names.json      人名対訳（日本語表記から空白を除いたもの -> 英語表記）
  extra.json      機械抽出に乗らなかった項目の手訳

英訳が無い id は auto（人名・学会名・賞名・日付を辞書で置き換えたもの）で出す。
日本語側に項目を足したら、items.json / media.json にはまだ無いので、
  1. このスクリプトを --extract で走らせて items.json / media.json を作り直し（既存 id は保持）
  2. 新しい id の英訳を en_*.json に書く
  3. 引数なしで走らせて content-en を再生成
使い方:  python3 tools/awards/build_en.py [--extract] [--out DIR]   （hugo/ で実行）
"""
import re, json, glob, os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
JA = re.compile(r'[぀-ヿ一-鿿]')
MON = ["", "Jan.", "Feb.", "Mar.", "Apr.", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]

def load(name):
    with open(os.path.join(HERE, name), encoding='utf-8') as f:
        return json.load(f)

NAMES = load('names.json')
TERMS = [("優秀プレゼンテーション賞","Best Presentation Award"),("優秀論文賞","Best Paper Award"),("優秀卒業論文賞","Best Bachelor's Thesis Award"),
 ("優秀修士論文賞","Best Master's Thesis Award"),("若手研究奨励賞","Young Researcher Encouragement Award"),("若手奨励賞","Young Researcher Encouragement Award"),
 ("ヤングリサーチャー賞","Young Researcher Award"),("ヤングリサーチャ賞","Young Researcher Award"),("学生奨励賞","Student Encouragement Award"),
 ("山下記念研究賞","Yamashita SIG Research Award"),("研究科長賞","Dean's Award"),("専攻長賞","Department Head's Award"),("工学部長賞","Dean of Engineering Award"),
 ("原島学術奨励賞","Harashima Academic Encouragement Award"),("大会奨励賞","Conference Encouragement Award"),("奨励賞","Encouragement Award"),("受賞",""),
 ("卒業論文","Bachelor's thesis"),("修士論文","Master's thesis"),("博士論文","Doctoral thesis"),
 ("工学部電子情報工学科","Department of Information and Communication Engineering, Faculty of Engineering"),
 ("工学部 電子情報工学科","Department of Information and Communication Engineering, Faculty of Engineering"),
 ("情報理工学系研究科電子情報学専攻","Department of Information and Communication Engineering, Graduate School of Information Science and Technology"),
 ("情報理工学系研究科 電子情報学専攻","Department of Information and Communication Engineering, Graduate School of Information Science and Technology"),
 ("情報理工学系研究科","Graduate School of Information Science and Technology"),
 ("工学系研究科電気系工学専攻","Department of Electrical Engineering and Information Systems, Graduate School of Engineering"),
 ("電子情報通信学会","IEICE"),("情報処理学会","IPSJ"),("信学技報","IEICE Tech. Rep."),("情処研報","IPSJ SIG Tech. Rep."),("研究報告","SIG Tech. Rep."),
 ("全国大会","National Convention"),("マルチメディア，分散，協調とモバイル","Multimedia, Distributed, Cooperative, and Mobile"),
 ("マルチメディア、分散、協調とモバイル","Multimedia, Distributed, Cooperative, and Mobile"),("シンポジウム","Symposium"),("年度","FY"),
 ("東京大学","The University of Tokyo"),("東大","UTokyo"),("日本経済新聞","Nihon Keizai Shimbun"),("日経産業新聞","Nikkei Sangyo Shimbun"),("日経","Nikkei"),
 ("朝日新聞","Asahi Shimbun"),("読売新聞","Yomiuri Shimbun"),("毎日新聞","Mainichi Shimbun"),("産経新聞","Sankei Shimbun"),("日刊工業新聞","Nikkan Kogyo Shimbun"),
 ("東京新聞","Tokyo Shimbun"),("東奥日報","To-o Nippo"),("Web東奥","Web To-o"),("テレビ東京","TV Tokyo"),("日本テレビ","Nippon TV"),("フジテレビ","Fuji TV"),
 ("週刊ダイヤモンド","Weekly Diamond")]

def fix_names(t):
    t = re.sub(r'(?<=[぀-ヿ一-鿿])[ 　]+(?=[぀-ヿ一-鿿])', '', t)
    for k in sorted(NAMES, key=len, reverse=True):
        t = t.replace(k, NAMES[k])
    return t

def auto(t):
    t = fix_names(t)
    for k, v in TERMS: t = t.replace(k, v)
    t = re.sub(r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda m: f'{int(m.group(3))} {MON[int(m.group(2))]} {m.group(1)}', t)
    t = re.sub(r'(\d{4})年(\d{1,2})月', lambda m: f'{MON[int(m.group(2))]} {m.group(1)}', t)
    t = t.replace('，', ', ').replace('、', ', ').replace('。', '.').replace('　', ' ').replace('（', ' (').replace('）', ') ').replace('：', ': ')
    return re.sub(r'\s+', ' ', t)

def restore_links(orig, en):
    tags = re.findall(r'<a\b[^>]*>', orig)
    holes = en.count('<a>')
    if holes and len(tags) != holes:
        print('WARN link count mismatch:', orig[:60], file=sys.stderr)
        tags = (tags + ['<a>'] * holes)[:holes]
    for t in tags: en = en.replace('<a>', t, 1)
    return en

def extract():
    """content/ から items.json / media.json を作り直す（既存 id・auto は保持）"""
    old_items = {it['ja']: it for it in load('items.json')}
    old_media = {it['ja']: it for it in load('media.json')}
    items, media = [], []
    for f in sorted(glob.glob('content/awardsmedia-20*.md')):
        y = re.search(r'(\d{4})', f).group(1); s = open(f, encoding='utf-8').read()
        sec = 'awards'
        for m in re.finditer(r'<h2[^>]*>([^<]*)</h2>|<p class="description">(.*?)</p>', s, flags=re.S):
            if m.group(1): sec = 'media' if 'MEDIA' in m.group(1) else 'awards'; continue
            ja = m.group(2).strip()
            it = old_items.get(ja) or {'id': f'{y}-n{len(items)}', 'year': y, 'sec': sec, 'ja': ja, 'auto': auto(ja)}
            items.append(it)
        mm = re.search(r'<h2[^>]*>MEDIA[^<]*</h2>', s)
        if mm:
            after = re.sub(r'<!--.*?-->', '', s[mm.end():], flags=re.S)
            for i, m in enumerate(re.finditer(r'<(div|p) class="(?:description|wp-block-paragraph)">(.*?)</\1>', after, flags=re.S)):
                ja = m.group(2).strip()
                it = old_media.get(ja) or {'id': f'm{y}-n{i}', 'year': y, 'ja': ja, 'auto': auto(ja)}
                media.append(it)
    json.dump(items, open(os.path.join(HERE, 'items.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(media, open(os.path.join(HERE, 'media.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('items', len(items), 'media', len(media))

def build(outdir):
    items, media = load('items.json'), load('media.json')
    ea, em, extra = load('en_awards.json'), load('en_media.json'), load('extra.json')
    missing = [it['id'] for it in items if it['sec'] == 'awards' and it['id'] not in ea and JA.search(it['auto'])]
    missing += [it['id'] for it in media if it['id'] not in em and JA.search(it['auto'])]
    if missing: print('英訳が無く日本語が残る id:', missing, file=sys.stderr)
    def en_for(it, table):
        return restore_links(it['ja'], fix_names(table.get(it['id'], it['auto'])))
    for f in sorted(glob.glob('content/awardsmedia-20*.md')):
        y = re.search(r'(\d{4})', f).group(1); s = open(f, encoding='utf-8').read()
        s = s.replace('bilingual: true\n', '')
        for it in items:
            if it['year'] == y and it['sec'] == 'awards': s = s.replace(it['ja'], en_for(it, ea), 1)
        for it in media:
            if it['year'] == y: s = s.replace(it['ja'], en_for(it, em), 1)
        s = re.sub(r'\s+title="[^"]*[぀-ヿ一-鿿][^"]*"', '', s)
        for a, b in extra['bare_p'].items(): s = s.replace(a, b)
        for a, b in extra['outlets_after_link'].items(): s = s.replace('、' + a, ', ' + b)
        s = re.sub(r'(?<=</a>)、(?=[A-Za-z])', ', ', s)
        s = re.sub(r'(\d{4})年度', r'FY\1', s)
        s = re.sub(r'href="/awardsmedia-(\d{4})/?"', r'href="/en/awardsmedia-\1/"', s)
        s = s.replace('href="/awardsmedia/"', 'href="/en/awardsmedia/"')
        s = re.sub(r'<!--(?:(?!-->).)*?[぀-ヿ一-鿿](?:(?!-->).)*?-->', '', s, flags=re.S)
        open(os.path.join(outdir, os.path.basename(f)), 'w', encoding='utf-8').write(s)
    # 旧一覧ページ /awardsmedia/ : 年ページの項目と題名で突き合わせる
    def key(t):
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'&#\d+;|&[a-z]+;', '', t)
        return re.sub(r'[^぀-ヿ一-鿿A-Za-z0-9]', '', t)
    def title_of(t):
        m = re.search(r'[“”"](.+?)[,，]?\s*[“”"]', re.sub(r'<[^>]*>', '', t))
        return key(m.group(1)) if m else None
    s = open('content/awardsmedia.md', encoding='utf-8').read()
    for li in re.findall(r'<li>(.*?)</li>', s, flags=re.S):
        if not JA.search(li): continue
        k, tt, hit = key(li), title_of(li), None
        for it in items:
            if it['sec'] != 'awards': continue
            ik = key(it['ja'])
            if ik == k or (tt and len(tt) >= 12 and tt in ik): hit = it; break
        en = None
        if hit and hit['id'] in ea: en = restore_links(li, fix_names(ea[hit['id']]))
        else:
            for rule in extra['index_li']:
                if all(c in li for c in rule['contains']): en = restore_links(li, rule['en']); break
        if en: s = s.replace('<li>' + li + '</li>', '<li>' + en + '</li>', 1)
    s = re.sub(r'(\d{4})年度', r'FY\1', s)
    open(os.path.join(outdir, 'awardsmedia.md'), 'w', encoding='utf-8').write(s)
    # 残った日本語を報告（中国語媒体の見出しは除外できないので目視）
    for f in sorted(glob.glob(os.path.join(outdir, 'awardsmedia*.md'))):
        t = re.sub(r'<[^>]*>', ' ', open(f, encoding='utf-8').read())
        left = [x for x in re.findall(r'[^ \n]*[぀-ヿ][^ \n]*', t)]   # かな を含むものだけ（漢字のみは中国語の可能性）
        if left: print(os.path.basename(f), '日本語が残っています:', left[:5], file=sys.stderr)

if __name__ == '__main__':
    if not os.path.isdir('content'): sys.exit('hugo/ で実行してください')
    if '--extract' in sys.argv: extract()
    out = 'content-en'
    if '--out' in sys.argv: out = sys.argv[sys.argv.index('--out') + 1]
    os.makedirs(out, exist_ok=True)
    build(out)
