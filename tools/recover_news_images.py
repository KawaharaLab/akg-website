"""Recover news thumbnails from the verified site mirror; run from repository root.

Requires Pillow. Rebuilds news_images.json and optimized local WebP assets.
Explicit article thumbnail metadata takes precedence in the template.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,json,unicodedata,hashlib
from PIL import Image,ImageOps
class Images(HTMLParser):
 def __init__(self):super().__init__();self.href='';self.images={}
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a':self.href=d.get('href','')
  if t=='img' and (m:=re.fullmatch(r'/archives/(\d+)/?',self.href)):self.images[m[1]]=d['src']
 def handle_endtag(self,t):
  if t=='a':self.href=''
images={}
for p in sorted(Path('site/archives/category/news').rglob('*.html')):
 parser=Images();parser.feed(p.read_text());images.update(parser.images)
posts=[]
for p in Path('hugo/content/archives').glob('*.md'):
 front=p.read_text().split('---',2)[1]
 if re.search(r'^ *- [\"\']?(?:news|award|press|events|seminar|media)[\"\']?$',front,re.M):posts.append(p.stem)
files={unicodedata.normalize('NFC','/'+str(p.relative_to('hugo/static'))):p for p in Path('hugo/static').rglob('*') if p.is_file()}
out=Path('hugo/static/images/news');out.mkdir(parents=True,exist_ok=True)
data={};missing=[];records=[]
for pid in posts:
 src=images.get(pid,'');path=files.get(unicodedata.normalize('NFC',unquote(urlsplit(src).path)))
 if not path:missing.append([pid,src]);continue
 key=hashlib.sha256(str(path).encode()).hexdigest()[:12]
 dest=out/(key+'.webp')
 with Image.open(path) as im:
  im=ImageOps.exif_transpose(im);im.thumbnail((640,640));im.convert('RGB').save(dest,'WEBP',quality=85)
 data[pid]={'src':'/images/news/'+dest.name}
 records.append({'id':pid,'original':src,'source':str(path),'image':data[pid]['src'],'shared': '/themes/' in src or 'thumbnail-' in src})
Path('hugo/data/news_images.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
Path('inventory/recovered-news-images.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('posts',len(posts),'recovered',len(data),'shared',sum(r['shared'] for r in records),'missing',json.dumps(missing,ensure_ascii=False))
