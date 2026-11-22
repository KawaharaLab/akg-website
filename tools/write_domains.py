#!/usr/bin/env python3
"""領域ページの本文を書き出す。各領域は WHY と APPROACH の二つに答える。"""
import io, os

DOMAINS = [
 dict(slug="perceive", verb="わかる", verbEn="Perceive", field="知覚", fieldEn="Perception",
      weight=10,
      topics="イベントカメラ / 非同期処理 / 3D 再構成 / 深度推定 / 音響センシング / 聴覚支援 / 手話認識",
      summary="見るとは、すべてを受けとることではなく、変わったところに応じること。",
      image="/wordpress/wp-content/uploads/2025/08/18_Takaki.png",
      caption="asEars — 骨伝導スピーカを耳介に当て、片耳難聴者の聞こえを助ける装置",
      why=[
        "見ることは、世界のすべてを受けとることではありません。変わったところにだけ応じることです。",
        "ところが標準的なカメラは、何も起きていない場面でも毎秒おなじ枚数の画像をつくり続けます。"
        "撮ってから捨てる、という手順を踏んでいる。遍在させたい知能にとって、これは払えない代償です。",
      ],
      approach=[
        "イベントカメラを核に置きます。変化のあった画素だけが発火するこの視覚は、"
        "電力をほとんど使わないことと、速いものを捉えられることが、同じ一つの性質から出てきます。"
        "倹約と俊敏が同じ根を持つ——私たちがこの素子を選ぶ理由はそこにあります。",
        "理解を助ける相手が機械か人かは、問いのかたちを変えません。"
        "二人の声が重なるとき、どちらかを選んで聞くこと。"
        "手の動きの、どこからどこまでが一つの語であるかを決めること。"
        "わかるとは、いつも取捨のことです。",
      ]),

 dict(slug="think", verb="考える", verbEn="Think", field="知能", fieldEn="Intelligence",
      weight=20,
      topics="世界モデル / 大規模言語モデル / 強化学習 / フィジカルAIチップ / 省電力アーキテクチャ",
      summary="考える能力と、考えないでいられる仕組みを、同時に設計する。",
      image="/wordpress/wp-content/uploads/2025/07/12_tsumura.png",
      caption="力のデータを言語モデルに読ませ、押すか、持ち上げてから押すかを選ばせる",
      why=[
        "賢さは、いつも高くつきます。大きなモデルは大きな電力を要求し、それを払える場所にしか置けません。",
        "知能をあらゆる場所に置こうとするなら、賢くすることと燃費をよくすることを、"
        "別々の課題として順番に解いていては間に合いません。同時に設計するしかない。",
      ],
      approach=[
        "考える能力と、考えないでいられる仕組みを、同時につくります。"
        "反射で足りる場面は反射で返す。世界モデルには、変化のあった瞬間だけを渡す。",
        "いつ考え、いつ考えずに済ませるか。この配分は計算量の問題に見えて、"
        "知能がどんなかたちをしているのかという問いそのものです。",
        "四つのうち最も新しく、2026 年に動きはじめた領域です。",
      ]),

 dict(slug="act", verb="はたらきかける", verbEn="Act", field="アクチュエーションとロボット",
      fieldEn="Robotics & Haptics", weight=30,
      topics="力触覚 / グリッパ / 柔らかい機構 / エラストマーセンサ / 触覚の言語化",
      summary="触れた瞬間、こちらも触れられている。距離をゼロにしてはじめて分かること。",
      image="/wordpress/wp-content/uploads/2024/03/enomoto.jpg",
      caption="永久磁石エラストマ膜のジャミンググリッパが、崩れやすいパンを潰さずに掴む",
      why=[
        "目は距離を保ったまま働きますが、手は対象と同じ場所へ行かなければ、何も知ることができません。"
        "触れることは、いつも相互的です。触れた瞬間、こちらも触れられている。",
        "実世界で働く機械は、この危うさを避けて通れません。"
        "見えているだけでは、掴めたかどうかは分からないからです。",
      ],
      approach=[
        "接触そのものから情報を取り出します。"
        "いま何に触れているかを、力の手ごたえから読みとる。"
        "掴めたかどうかを、グリッパの内側で鳴る音から聞きわける。",
        "そのうえで、手ざわりを言葉につなごうとしています。"
        "「ざらざら」「つるつる」は曖昧な語に見えて、人が長いあいだ使ってきた確かな記述です。"
        "感覚を数値にすることであり、同時に、言葉のほうを測り直すことでもあります。",
      ]),

 dict(slug="dissolve", verb="とけこむ", verbEn="Dissolve", field="身体とウェアラブル",
      fieldEn="Embodiment & Wearables", weight=40,
      topics="極低電力設計 / e-textile / 身体スケール NFC / 機械編み / 印刷回路 / 無線給電",
      summary="気づかれないことが、この領域における完成のかたち。",
      image="/wordpress/wp-content/uploads/2025/07/1_takahashi.jpg",
      caption="身体に沿わせた e-textile が、電池を持たないセンサに電力とデータを同時に運ぶ",
      why=[
        "よくできた道具は、使っているあいだ意識されません。眼鏡も、靴も、そうです。",
        "知能を遍在させるという構想は、それを載せるかたちがなければ一行も実装されません。"
        "そしてそのかたちは、気づかれないところまで小さくなければ、遍在できません。",
      ],
      approach=[
        "電池を替えなくてよい極低電力のリング。糸の段階から機能を編み込んだ布。"
        "身体そのものを通り道にする近接無線。"
        "小さく、薄くしようとしているのは寸法だけではなく、装置が人に要求する注意の量です。",
        "印刷による回路づくりも、無線給電も、そこへ向かうための道具でした。"
        "研究室が長く積み上げてきた技術が、ここで一つの目的に束ねられます。",
      ]),
]

def yaml_block(key, paras):
    out = [f"{key}:"]
    for p in paras:
        out.append(f"  - >-")
        out.append(f"    {p}")
    return "\n".join(out)

for d in DOMAINS:
    path = f"hugo/content/research/{d['slug']}/_index.md"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fm = f"""---
title: "{d['verb']}"
verb: "{d['verb']}"
verbEn: "{d['verbEn']}"
field: "{d['field']}"
fieldEn: "{d['fieldEn']}"
type: "domain"
weight: {d['weight']}
topics: "{d['topics']}"
summary: "{d['summary']}"
image: "{d['image']}"
imageCaption: "{d['caption']}"
{yaml_block('why', d['why'])}
{yaml_block('approach', d['approach'])}
---
"""
    open(path, "w", encoding="utf-8").write(fm)
    print("wrote", path)
