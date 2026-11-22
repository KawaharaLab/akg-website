#!/usr/bin/env python3
"""実質的に同じプロジェクトの研究記事をひとつにまとめる。

URL は全部残す（外部リンクを切らないため）。
一覧に出るのは最新の一件だけにし、古い記事からは最新へ導線を張る。

同一プロジェクトの判定:
  - タイトルが酷似している（0.8 以上）、または
  - その 2 記事だけが引用している論文を共有している
    （広く引用される論文は背景文献なので使えない）
  かつ、話題が近い（タイトル類似 0.25 以上）
"""
import os, re, sys, difflib
from collections import defaultdict

ARCH = "hugo/content/archives"


def load():
    arts = {}
    for fn in sorted(os.listdir(ARCH)):
        if not fn.endswith(".md"):
            continue
        s = open(f"{ARCH}/{fn}", encoding="utf-8", errors="surrogateescape").read()
        if not re.search(r'^  - "research"', s, re.M):
            continue
        g = lambda k: (re.search(rf'^{k}: "(.*)"$', s, re.M) or [None, ""])[1] \
            if re.search(rf'^{k}: "(.*)"$', s, re.M) else ""
        arts[fn[:-3]] = dict(
            title=g("title"), titleEn=g("titleEn"), date=g("date"),
            cites=set(re.findall(r'^  - citation: "(.*)"', s, re.M)))
    return arts


def norm(s):
    return re.sub(r'[\s　\-–—:：,，.。()（）&#;0-9]', '', s.lower())


def tsim(a, b, arts):
    best = 0
    for k in ("title", "titleEn"):
        x, y = arts[a][k], arts[b][k]
        if len(x) >= 8 and len(y) >= 8:
            best = max(best, difflib.SequenceMatcher(None, norm(x), norm(y)).ratio())
    return best


def main():
    write = "--write" in sys.argv
    arts = load()

    owners = defaultdict(set)
    for pid, a in arts.items():
        for c in a["cites"]:
            owners[c].add(pid)

    adj = defaultdict(set)
    ids = sorted(arts)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            t = tsim(a, b, arts)
            exclusive = [c for c in arts[a]["cites"] & arts[b]["cites"]
                         if len(owners[c]) == 2]
            same = t >= 0.8 or (exclusive and t >= 0.25)
            if same:
                adj[a].add(b); adj[b].add(a)

    # 連結成分をプロジェクトにする
    seen, projects = set(), []
    for pid in ids:
        if pid in seen or pid not in adj:
            continue
        stack, comp = [pid], set()
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x); seen.add(x)
            stack += list(adj[x] - comp)
        projects.append(sorted(comp, key=lambda i: arts[i]["date"], reverse=True))

    print(f"研究記事 {len(arts)} 件 → 同一プロジェクト {len(projects)} 群 "
          f"({sum(len(p) for p in projects)} 記事)")
    for comp in projects:
        head = comp[0]
        print(f"\n  代表 {head}  {arts[head]['date']}  {arts[head]['title'][:50]}")
        for pid in comp[1:]:
            print(f"    以前 {pid}  {arts[pid]['date']}  {arts[pid]['title'][:50]}")

    if not write:
        return

    for comp in projects:
        head = comp[0]
        slug = f"p{head}"
        for pid in comp:
            p = f"{ARCH}/{pid}.md"
            s = open(p, encoding="utf-8", errors="surrogateescape").read()
            s = re.sub(r'^project.*\n', '', s, flags=re.M)
            block = f'project: "{slug}"\n'
            block += f'projectRole: "{"primary" if pid == head else "earlier"}"\n'
            s = re.sub(r'^(wpId:)', block + r'\1', s, count=1, flags=re.M)
            open(p, "w", encoding="utf-8", errors="surrogateescape").write(s)
    print(f"\n{sum(len(p) for p in projects)} 記事に project を書き込んだ")


if __name__ == "__main__":
    main()
