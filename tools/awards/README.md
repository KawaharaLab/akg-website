# AWARDS & MEDIA の英訳データ

`hugo/content-en/awardsmedia*.md` はここから生成する。翻訳は JSON に入っており、
`build_en.py` は置き換えとリンク復元だけを行う（機械翻訳はしない）。

    cd hugo && python3 ../tools/awards/build_en.py            # content-en を再生成
    cd hugo && python3 ../tools/awards/build_en.py --extract  # 日本語側に項目を足したあと、items/media.json を更新

| ファイル | 内容 |
|---|---|
| `items.json` | 年ページ AWARDS 欄の項目。`ja` は元 HTML そのもの（置換キーなので変えない）、`auto` は辞書変換の結果 |
| `media.json` | 年ページ MEDIA 欄の項目 |
| `en_awards.json` | id → 英訳。`<a>` は空で書く（href は元から復元） |
| `en_media.json` | id → 英訳 |
| `names.json` | 人名対訳。日本語は空白を除いた形。People ページ・タグ一覧由来が 180 件、手で足した共同研究者が約 50 件 |
| `extra.json` | class なし `<p>` の見出しと、旧一覧ページで突き合わせに失敗した項目の手訳 |

日本語側の項目を直したら、`items.json` / `media.json` の `ja` も同じ文字列に直す
（`--extract` を使うと一致しない項目は新しい id になり、英訳が外れる）。

読みを推定した人名（要確認）: 佐藤峻 Takashi Sato, 坂井珠麗亜 Juria Sakai, 渡邉慎人 Shinto Watanabe,
谷道鼓太朗 Kotaro Tanimichi, 香山楷 Kai Kayama, 趙若彤 Ruotong Zhao。飯田静空 は Seiku Iida で確定（2026-09-05）。
