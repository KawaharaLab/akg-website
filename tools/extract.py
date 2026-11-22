#!/usr/bin/env python3
"""静的ミラー site/ から Hugo 用コンテンツを抽出する。

投稿記事は Markdown に変換し、構造の重い固定ページ（Publications /
Awards & Media / MEMBER）は HTML のまま保持する。既存 URL は完全に維持する。
"""
import os, re, sys, json, html, subprocess, datetime

SRC = "site"
DST = "hugo"

# --- 抽出 ---------------------------------------------------------------

def read(path):
    return open(path, encoding="utf-8", errors="surrogateescape").read()

def entry_content(s):
    m = re.search(r'<div class="entry-content">(.*?)</div><!-- \.entry-content', s, re.S)
    return m.group(1).strip() if m else ""

def title(s):
    m = re.search(r'<article[^>]*>\s*<h1[^>]*>(.*?)</h1>', s, re.S)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<title>(.*?)</title>', s, re.S)
    if m:
        return html.unescape(m.group(1)).split("–")[0].strip()
    return ""

def post_date(s):
    m = re.search(r'<p class="date[^"]*">\s*(\d{4})年(\d{2})月(\d{2})日', s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None

def categories(s):
    m = re.search(r'<article[^>]*class="([^"]*)"', s)
    if not m:
        return []
    return sorted({c[len("category-"):] for c in m.group(1).split()
                   if c.startswith("category-")})

def tags(s):
    return sorted({html.unescape(t) for t in
                   re.findall(r'href="/archives/tag/([^"/]+)/?"', s)})

# --- Markdown 変換 ------------------------------------------------------

def to_markdown(fragment):
    r = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
        input=fragment, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout.strip()

# --- front matter -------------------------------------------------------

def yaml_str(v):
    return '"' + str(v).replace('\\', '\\\\').replace('"', '\\"') + '"'

def front_matter(d):
    out = ["---"]
    for k, v in d.items():
        if v is None or v == [] or v == "":
            continue
        if isinstance(v, list):
            out.append(f"{k}:")
            out += [f"  - {yaml_str(x)}" for x in v]
        elif isinstance(v, bool):
            out.append(f"{k}: {'true' if v else 'false'}")
        else:
            out.append(f"{k}: {yaml_str(v)}")
    out.append("---")
    return "\n".join(out)

def write(path, fm, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(fm + "\n\n" + body + "\n")

# --- 実行 ---------------------------------------------------------------

def main():
    stats = {"posts": 0, "pages_md": 0, "pages_html": 0, "md_fail": [], "empty": []}

    # 1) 投稿記事 /archives/NNNN
    for name in sorted(os.listdir(f"{SRC}/archives")):
        d = f"{SRC}/archives/{name}"
        if not (name.isdigit() and os.path.isfile(f"{d}/index.html")):
            continue
        s = read(f"{d}/index.html")
        body_html = entry_content(s)
        md = to_markdown(body_html) if body_html else ""
        if body_html and md is None:
            stats["md_fail"].append(name)
            md, fmt = body_html, "html"
        else:
            fmt = "md"
        if not body_html:
            stats["empty"].append(f"archives/{name}")
        fm = front_matter({
            "title": title(s),
            "date": post_date(s),
            "categories": categories(s),
            "tags": tags(s),
            "wpId": int(name),
            "contentFormat": fmt,
        })
        write(f"{DST}/content/archives/{name}.md", fm, md)
        stats["posts"] += 1

    # 2) 固定ページ（URL をそのまま維持）
    HTML_KEEP = re.compile(r'^(publications-\d{4}|awardsmedia(-\d{4})?|member)$')
    for name in sorted(os.listdir(SRC)):
        d = f"{SRC}/{name}"
        if not os.path.isdir(d) or name in ("archives", "wordpress"):
            continue
        f = f"{d}/index.html"
        if not os.path.isfile(f):
            continue
        s = read(f)
        body_html = entry_content(s)
        if not body_html:
            stats["empty"].append(name)
        keep_html = bool(HTML_KEEP.match(name))
        if keep_html:
            body, fmt = body_html, "html"
            stats["pages_html"] += 1
        else:
            md = to_markdown(body_html) if body_html else ""
            if body_html and md is None:
                stats["md_fail"].append(name)
                body, fmt = body_html, "html"
            else:
                body, fmt = md, "md"
            stats["pages_md"] += 1
        fm = front_matter({
            "title": title(s),
            "type": "page",
            "contentFormat": fmt,
        })
        write(f"{DST}/content/{name}.md", fm, body)

    # 3) トップページ
    s = read(f"{SRC}/index.html")
    write(f"{DST}/content/_index.md",
          front_matter({"title": "KAWAHARA LABORATORY"}), "")

    print(json.dumps(stats, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
