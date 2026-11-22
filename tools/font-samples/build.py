#!/usr/bin/env python3
from pathlib import Path
import urllib.request,urllib.parse,re,base64,json
fonts=['Schibsted Grotesk','Zen Kaku Gothic New','Inter','Noto Sans JP','IBM Plex Sans','IBM Plex Sans JP','Source Serif 4','Noto Serif JP']
text='''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !?.,:;/'&+-—–()[]「」、。：／・。→
研究メンバー研究業績ニュース社会連携私たちについて材料から知能まで現実世界で使える技術をつくる日常生活に計算を組み込むことが研究の根底にありますセンサ回路AI一緒設計し環境試す独自専門持寄り新仕仕組究。わか考はたらきけとこ低電力な指輪型マウス高橋亮川原圭博省情報入力身体編電子布服年月著者掲載先最新'''
template=Path('tools/font-samples/template.html').read_text()
sample=template.split('<div class="stage">',1)[1].split('</template>',1)[0]
text=''.join(sorted(set(text+re.sub(r'<[^>]+>','',sample))))
css=[]
for family in fonts:
 query=urllib.parse.urlencode({'family':family+':wght@400;500;700','text':text,'display':'swap'})
 req=urllib.request.Request('https://fonts.googleapis.com/css2?'+query,headers={'User-Agent':'Mozilla/5.0'})
 style=urllib.request.urlopen(req,timeout=40).read().decode()
 urls=set(re.findall(r'url\((https://[^)]+)\)',style))
 for url in urls:
  blob=urllib.request.urlopen(url,timeout=40).read();encoded=base64.b64encode(blob).decode();style=style.replace(url,'data:font/woff2;base64,'+encoded)
 css.append(style);print(family,len(urls),'font files',flush=True)
template=Path('tools/font-samples/template.html').read_text()
output=template.replace('__FONTS__','\n'.join(css))
licenses=Path('docs/font-sample-licenses.json').read_text()
output=output.replace('</html>','<script type="application/json" id="font-licenses">'+licenses.replace('<','\\u003c')+'</script></html>')
Path('docs/font-samples.html').write_text(output)
