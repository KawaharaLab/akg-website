#!/usr/bin/env python3
"""研究記事に、対応する発表（論文）を紐づける。

業績ページから引用を抽出し、記事タイトル（和文・英文）と突き合わせる。
誤対応は無いほうがましなので、閾値は高めにとる。
"""
import os, re, sys, html, json, difflib
from collections import defaultdict

CONTENT = "hugo/content"
ARCH = f"{CONTENT}/archives"

def norm(s):
    """比較用に正規化する。記号と空白を落とし、全角英数を半角に。"""
    s = html.unescape(s)
    s = s.translate(str.maketrans(
        "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
        "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))
    s = s.lower()
    s = re.sub(r'[\s　]+', '', s)
    s = re.sub(r'[-–—_,，.。:：;；/／\'"“”‘’「」『』（）()\[\]【】~〜!！?？*+&＆]', '', s)
    return s


def load_pubs():
    """業績ページから {year, section, url, citation, title} を集める。"""
    pubs = []
    for fn in sorted(os.listdir(CONTENT)):
        m = re.fullmatch(r'publications-(\d{4})\.md', fn)
        if not m:
            continue
        year = int(m.group(1))
        s = open(f"{CONTENT}/{fn}", encoding="utf-8", errors="surrogateescape").read()
        section = ""
        # 見出しと項目を出現順にたどる
        for tok in re.finditer(
                r'<h2[^>]*>(?P<h>.*?)</h2>'
                r'|<p class="description">(?P<p>.*?)</p>', s, re.S):
            if tok.group('h') is not None:
                section = re.sub(r'<[^>]+>', '', html.unescape(tok.group('h'))).strip()
                continue
            body = tok.group('p')
            url = ""
            a = re.search(r'href\s*=\s*"([^"]+)"', body)
            if a:
                url = html.unescape(a.group(1)).strip()
            cite = re.sub(r'<[^>]+>', '', html.unescape(body))
            cite = re.sub(r'\s+', ' ', cite).strip()
            if len(cite) < 30:
                continue
            # 引用中の論文題目を取り出す
            title = ""
            q = re.search(r'[“”"]\s*(.+?)\s*[,，]?\s*[“”"]', cite)
            if q:
                title = q.group(1)
            pubs.append(dict(year=year, section=section, url=url,
                             citation=cite, title=title))
    return pubs


def main():
    write = "--write" in sys.argv
    pubs = load_pubs()
    print(f"業績 {len(pubs)} 件を抽出（題目を取れたもの {sum(1 for p in pubs if p['title'])} 件）")

    # 同じ URL を指す業績の数を数えておく
    url_owners = defaultdict(int)
    for p in pubs:
        if p["url"]:
            url_owners[p["url"].rstrip('/')] += 1

    # 題目の正規化インデックス
    index = []
    for p in pubs:
        if p["title"]:
            index.append((norm(p["title"]), p))

    matched = 0
    total = 0
    signal = defaultdict(int)
    per_article = {}
    for fn in sorted(os.listdir(ARCH)):
        if not fn.endswith(".md"):
            continue
        s = open(f"{ARCH}/{fn}", encoding="utf-8", errors="surrogateescape").read()
        if not re.search(r'^  - "research"', s, re.M):
            continue
        total += 1
        body = s.split("---", 2)[2] if s.count("---") >= 2 else ""

        # 信号 1: 本文中の DOI / URL。業績側の URL と直接照合できるので最も確実。
        urls = {u.rstrip('.,)）') for u in re.findall(r'https?://[^\s")\]、]+', body)}

        # 信号 2: 本文中の引用符つき題目。【参考文献】欄に多いが、欄外にもある。
        quoted = [q.strip(' 　,，.。') for q in
                  re.findall(r'[“”"]([^“”"]{15,200})[”“"]', body)]

        # 信号 3: 記事タイトル（和文・英文）
        titles = []
        for key in ("titleEn", "title"):
            m = re.search(rf'^{key}: "(.*)"$', s, re.M)
            if m and m.group(1).strip():
                titles.append(m.group(1))

        hits = []
        # --- 信号 1 ---
        # 学会のプログラムページなど、複数の業績が共有する URL は特定に使えない。
        # その URL がただ一件の業績を指すときだけ採用する。
        seen_urls = {u.rstrip('/') for u in urls}
        for p in pubs:
            if not p["url"]:
                continue
            key = p["url"].rstrip('/')
            if key in seen_urls and url_owners[key] == 1:
                hits.append((1.0, p, "url"))
        # --- 信号 2・3 ---
        for src, cands in (("ref", quoted), ("title", titles)):
            for c in cands:
                nc = norm(c)
                if len(nc) < 12:
                    continue
                for ntitle, p in index:
                    if not ntitle:
                        continue
                    if nc == ntitle:
                        hits.append((1.0, p, src)); continue
                    # 包含は、短いほうが長いほうの 6 割以上を占めるときだけ認める。
                    # そうしないと「無線電力伝送」のような短い題目が長い記事名に当たる。
                    if nc in ntitle or ntitle in nc:
                        lo, hi = sorted((len(nc), len(ntitle)))
                        if lo >= 20 and lo / hi >= 0.6:
                            hits.append((0.97, p, src)); continue
                    r = difflib.SequenceMatcher(None, nc, ntitle).ratio()
                    if r >= 0.88:
                        hits.append((r, p, src))
        for _, _, src in hits:
            signal[src] += 1
        if not hits:
            continue
        # 重複排除して新しい順
        seen = set(); best = []
        for r, p, src in sorted(hits, key=lambda x: (-x[0], -x[1]["year"])):
            k = (p["title"], p["year"])
            if k in seen:
                continue
            seen.add(k); best.append(p)
        per_article[fn[:-3]] = best[:6]
        matched += 1

    print(f"研究記事 {total} 件中 {matched} 件に対応する発表が見つかった")
    print("  信号別のヒット数:", dict(signal))
    cnt = defaultdict(int)
    for v in per_article.values():
        cnt[len(v)] += 1
    print("  紐づいた本数:", dict(sorted(cnt.items())))

    if write:
        for pid, plist in per_article.items():
            p = f"{ARCH}/{pid}.md"
            s = open(p, encoding="utf-8", errors="surrogateescape").read()
            s = re.sub(r'^pubs:\n(?:  - .*\n(?:    .*\n)*)+', '', s, flags=re.M)
            block = "pubs:\n"
            for x in plist:
                cite = x["citation"].replace('"', "'")
                block += (f'  - citation: "{cite}"\n'
                          f'    year: {x["year"]}\n'
                          f'    section: "{x["section"]}"\n')
                if x["url"]:
                    block += f'    url: "{x["url"]}"\n'
            s = re.sub(r'^(wpId:)', block + r'\1', s, count=1, flags=re.M)
            open(p, "w", encoding="utf-8", errors="surrogateescape").write(s)
        print("front matter に書き込んだ")
    else:
        for pid, plist in list(per_article.items())[:5]:
            print(f"\n  {pid}:")
            for x in plist:
                print(f"    [{x['year']}] {x['citation'][:96]}")


if __name__ == "__main__":
    main()
