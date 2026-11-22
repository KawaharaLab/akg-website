#!/usr/bin/env python3
"""抽出時に [TABLE] に化けた表を本文に戻す（該当は /archives/3356 の 2 箇所だけ）。
ミラー site/archives/3356/index.html の <table> から手で書き起こした。
"""
p = 'hugo/content/archives/3356.md'
s = open(p, encoding='utf-8').read()
t1 = """国際会議名：33rd ACM User Interface Software and Technology Symposium (UIST)  
論文タイトル：“poimo: Portable and Inflatable Mobility Devices Customizable for Personal Physical Characteristics”  
著者：Ryuma Niiyama\\*, Hiroki Sato\\*, Kazumasa Tsujimura, Koya Narumi, Young ah Seong, Ryosuke Yamamura, Yasuaki Kakehi, Yoshihiro Kawahara (\\* joint first authors)  
DOI番号：https://dx.doi.org/10.1145/3379337.3415894 （2020年10月6日ごろ公開予定）  
YouTube動画：https://youtu.be/HgFTZsKX2k4"""
t2 = """論文タイトル：“Soft yet Strong Inflatable Structures for a Foldable and Portable Mobility”  
著者：Hiroki Sato, Young ah Seong, Ryosuke Yamamura, Hiromasa Hayashi, Katsuhiro Hata, Hisato Ogata, Ryuma Niiyama, and Yoshihiro Kawahara  
DOI番号：https://doi.org/10.1145/3334480.3383147"""
if s.count('[TABLE]') == 2:
    open(p, 'w', encoding='utf-8').write(s.replace('[TABLE]', t1, 1).replace('[TABLE]', t2, 1))
    print('3356: 表 2 つを戻した')
else:
    print('3356: [TABLE] が 2 つではない（%d）。何もしない' % s.count('[TABLE]'))
