#!/usr/bin/env python3
"""研究記事を四領域（わかる／考える／ふれる／とけこむ）に振り分ける。

判定は記事タイトル・本文と、旧カテゴリの両方を見る。
どれにも当たらないものは archive に送る。
"""
import os, re, sys, json
from collections import Counter

CONTENT = "hugo/content/archives"

# 領域スラッグ -> (判定パターン, 旧カテゴリからの寄与)
DOMAINS = {
    "perceive": (
        r'イベントカメラ|イベントベース|event.based|Gaussian|深度|depth|認識|recognition'
        r'|推定|estimation|レイトレ|ray.tracing|センシング|sensing|センサ|sensor'
        r'|画像|vision|カメラ|camera|音響|acoustic|音声|speech|聴|手話|マイク'
        r'|計測|measurement|位置推定|localization|データマイニング',
        {"sensing", "sensing-and-data-mining"},
    ),
    "think": (
        r'LLM|大規模言語モデル|言語モデル|強化学習|世界モデル|機械学習|machine.learning'
        r'|深層学習|deep.learning|ニューラル|neural|生成モデル|diffusion|拡散モデル'
        r'|フィジカルAI|physical.ai|人工知能|最適化|optimization|予測|prediction'
        r'|AIチップ|推論|inference',
        set(),
    ),
    "act": (
        r'ロボット|robot|グリッパ|gripper|アクチュエータ|actuat|触覚|haptic|力覚'
        r'|エラストマー|elastomer|マニピュレ|manipulat|把持|grasp|柔らか|soft'
        r'|折り紙|origami|折り|folding|切り紙|kirigami|機構|mechanism|駆動',
        {"softrobot"},
    ),
    "dissolve": (
        r'ウェアラブル|wearable|テキスタイル|textile|e-textile|編み|knit|リング|ring'
        r'|NFC|指輪|衣服|garment|装着|body.?net|身体スケール|貼り付け|皮膚|skin'
        r'|印刷|printed|インクジェット|inkjet|回路|circuit|導電|conductive'
        r'|無線給電|wireless.power|給電|環境発電|energy.harvest|極低電力|低消費電力'
        r'|バッテリーレス|battery.free',
        {"digifab", "wpt", "inclusive-wearable"},
    ),
}


def read(p):
    return open(p, encoding="utf-8", errors="surrogateescape").read()


def old_cats(s):
    m = re.search(r'^categories:\n((?:  - .*\n)+)', s, re.M)
    return set(re.findall(r'  - "(.*)"', m.group(1))) if m else set()


def title_of(s):
    m = re.search(r'^title: "(.*)"', s, re.M)
    return m.group(1) if m else ""


def classify(s):
    cats = old_cats(s)
    if "research" not in cats:
        return None  # 研究記事以外は対象外
    hay = title_of(s) + "\n" + s.split("---", 2)[2]
    hits = []
    for slug, (pat, from_cats) in DOMAINS.items():
        score = len(re.findall(pat, hay, re.I))
        if cats & from_cats:
            score += 3  # 旧カテゴリの一致は強い証拠として加点
        if score:
            hits.append((score, slug))
    if not hits:
        return []
    hits.sort(reverse=True)
    top = hits[0][0]
    # 最高スコアの半分以上を取ったものは併記する（領域は交差する）
    return [s for sc, s in hits if sc >= max(2, top * 0.5)]


def main():
    write = "--write" in sys.argv
    stats = Counter()
    combos = Counter()
    archive = []
    for fn in sorted(os.listdir(CONTENT)):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(CONTENT, fn)
        s = read(p)
        doms = classify(s)
        if doms is None:
            continue
        stats["研究記事"] += 1
        if not doms:
            archive.append((fn[:-3], title_of(s)))
            doms_out = []
            stats["archive"] += 1
        else:
            doms_out = doms
            for d in doms:
                stats[d] += 1
            combos[tuple(sorted(doms))] += 1
        if write:
            s = re.sub(r'^domains:\n(?:  - .*\n)+', '', s, flags=re.M)
            block = ""
            if doms_out:
                block = "domains:\n" + "".join(f'  - "{d}"\n' for d in sorted(doms_out))
            else:
                block = 'archived: true\n'
            s = re.sub(r'^(wpId:)', block + r'\1', s, count=1, flags=re.M)
            open(p, "w", encoding="utf-8", errors="surrogateescape").write(s)

    print(f"研究記事 {stats['研究記事']} 件")
    for d in DOMAINS:
        print(f"  {d:10} {stats[d]:4}")
    print(f"  {'archive':10} {stats['archive']:4}")
    print("\n複数領域の組み合わせ上位:")
    for c, n in combos.most_common(8):
        if len(c) > 1:
            print(f"  {' + '.join(c):34} {n}")
    if archive:
        print(f"\narchive 行き {len(archive)} 件の例:")
        for a, t in archive[:8]:
            print(f"  {a:6} {t[:56]}")


if __name__ == "__main__":
    main()
