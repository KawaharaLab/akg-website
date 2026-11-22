#!/usr/bin/env python3
"""日英併記だった旧 HTML ページを日本語版・英語版に分ける（2026-09-05 に一度実行済み）。

再実行が要るのは、元の併記ファイルからやり直すときだけ。元ファイルは
archive/hugo-20260905.tgz の hugo/content/member.md, publications-*.md に入っている。
現在の content/member.md は既に日本語だけなので、そのまま入力にしてはいけない。

  python3 tools/split_bilingual.py member  <併記のmember.md>  content/member.md  content-en/member.md
  python3 tools/split_bilingual.py pubs    <併記のpublications-YYYY.md>  content/  content-en/

member: <h3 class="card-title">日本語名 / 役職<br>English Name / Role</h3> を <br> で分ける。
        Alumni の「日本語名 / English Name」は " / " で分ける。役職 <p class="description"> は下の対訳表。
pubs:   <h2 class="border">国内全国大会 / Domestic General Conferences</h2> を " / " で分け、
        英語側は年ナビを FY 表記・リンクを /en/publications-YYYY/ にする。引用文献は触らない。
"""
import re, sys, os
JA = re.compile(r'[぀-ヿ一-鿿]')
ROLES = {
 "インクルーシブ工学連携研究機構機構長":"Director, RIISE","トロント大学進学":"Went on to the University of Toronto",
 "メルボルン大学進学":"Went on to the University of Melbourne","外国人協力研究員":"Foreign Cooperative Researcher",
 "学士卒業":"Bachelor's graduate","学術支援職員":"Academic Support Staff","学術支援専門職員":"Academic Support Specialist",
 "学術専門職員":"Project Academic Support Specialist","技術補佐員":"Technical Assistant",
 "技術補佐員 / 国際インターンシップ":"Technical Assistant / International Internship","客員研究員":"Visiting Researcher",
 "共同研究員":"Collaborative Researcher","教授":"Professor","研究生":"Research Student","交換留学生":"Exchange Student",
 "工学部国際インターンシップ研修生":"International Internship Trainee, Faculty of Engineering","国際インターンシップ":"International Internship",
 "国際短期プログラム受講生":"Short-term International Program Student","修士卒業":"Master's graduate",
 "他大学編入":"Transferred to another university","大学院国際インターンシップ研修生":"International Internship Trainee, Graduate School",
 "特任研究員":"Project Researcher","特任講師":"Project Lecturer","特任助教":"Project Assistant Professor","特任専門職員":"Project Specialist",
 "特別聴講学生":"Special Auditing Student","博士卒業":"Doctoral graduate","博士単位取得退学":"Completed doctoral coursework","秘書":"Secretary",
}

def split_title(inner):
    m = re.match(r'^(\s*<a [^>]*>)?(.*?)(</a>)?\s*$', inner, flags=re.S)
    pre, core, post = m.group(1) or '', m.group(2), m.group(3) or ''
    parts = re.split(r'<br\s*/?>', core)
    if len(parts) == 2: ja, en = parts[0].strip(), parts[1].strip()
    elif ' / ' in core and JA.search(core.split(' / ')[0]) and not JA.search(core.split(' / ', 1)[1]):
        ja, en = [x.strip() for x in core.split(' / ', 1)]
    else: ja = en = core.strip()
    return pre + ja + post, pre + en + post

def member(src, out_ja, out_en):
    s = open(src, encoding='utf-8').read().replace('bilingual: true\n', '')
    ja = en = s
    for t in re.findall(r'<h3 class="card-title">(.*?)</h3>', s, flags=re.S):
        a, b = split_title(t)
        ja = ja.replace('<h3 class="card-title">' + t + '</h3>', '<h3 class="card-title">' + a + '</h3>', 1)
        en = en.replace('<h3 class="card-title">' + t + '</h3>', '<h3 class="card-title">' + b + '</h3>', 1)
    en = re.sub(r'<p class="description">([^<]*)</p>', lambda m: '<p class="description">' + ROLES.get(m.group(1).strip(), m.group(1)) + '</p>', en)
    en = en.replace('メールアドレスは@以降にakg.t.u-tokyo.ac.jpをお付けください', 'E-mail addresses: append akg.t.u-tokyo.ac.jp after the @.')
    en = re.sub(r'(\d{4})年度', r'FY\1', en)
    unk = sorted(set(d for d in re.findall(r'<p class="description">([^<]*)</p>', en) if JA.search(d)))
    if unk: print('対訳表に無い役職:', unk, file=sys.stderr)
    open(out_ja, 'w', encoding='utf-8').write(ja); open(out_en, 'w', encoding='utf-8').write(en)

def pubs(src, dir_ja, dir_en):
    s = open(src, encoding='utf-8').read().replace('bilingual: true\n', '')
    ja = re.sub(r'(<h2 class="border">)([^<]*?) / ([^<]*?)(</h2>)', r'\1\2\4', s)
    en = re.sub(r'(<h2 class="border">)([^<]*?) / ([^<]*?)(</h2>)', r'\1\3\4', s)
    # Only translate the year navigation; preserve original citation language.
    en = re.sub(r'(<p\b[^>]*class="search__year-list"[^>]*>)(.*?)(</p>)',
                lambda m: m[1] + re.sub(r'(\d{4})年度', r'FY\1', m[2]) + m[3], en, flags=re.S)
    en = re.sub(r'href="/publications-(\d{4})/?"', r'href="/en/publications-\1/"', en)
    b = os.path.basename(src)
    open(os.path.join(dir_ja, b), 'w', encoding='utf-8').write(ja); open(os.path.join(dir_en, b), 'w', encoding='utf-8').write(en)

if __name__ == '__main__':
    if len(sys.argv) < 5 or sys.argv[1] not in ('member', 'pubs'): sys.exit(__doc__)
    (member if sys.argv[1] == 'member' else pubs)(*sys.argv[2:5])
