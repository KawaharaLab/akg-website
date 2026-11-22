#!/usr/bin/env python3
"""Build the 2026 layout trial from unchanged legacy citations. No external inference."""
from html.parser import HTMLParser
from pathlib import Path
import json,re,yaml,calendar
from urllib.parse import unquote

class Citations(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.section='';self.heading=False;self.active=None;self.records=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='h2':self.heading=True;self.section=''
  if tag=='p' and 'description' in a.get('class','').split():self.active={'section':self.section,'id':a.get('id',''),'citation':'','links':[]}
  if tag=='a' and self.active is not None:
   url=a.get('href','').strip()
   if url.startswith(('https://','http://')) and url not in self.active['links']:self.active['links'].append(url)
 def handle_data(self,data):
  if self.heading:self.section+=data
  if self.active is not None:self.active['citation']+=data
 def handle_endtag(self,tag):
  if tag=='h2':self.heading=False
  if tag=='p' and self.active is not None:self.records.append(self.active);self.active=None

months={m:i for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],1)}
def link_key(url):
 url=unquote(url).strip().rstrip('/')
 doi=re.search(r'10\.\d{4,9}/[^\s?#]+',url,re.I)
 return doi.group().lower() if doi else url
research_links={}
for path in Path('hugo/content/archives').glob('*.md'):
 meta=yaml.safe_load(path.read_text().split('---',2)[1])
 if 'research' not in meta.get('categories',[]):continue
 for pub in meta.get('pubs',[]) or []:
  if pub.get('url'):research_links.setdefault(link_key(pub['url']),set()).add('/archives/'+path.stem+'/')
data={}
for lang,folder in [('ja','content'),('en','content-en')]:
 rows=[]
 for source in sorted(Path(f'hugo/{folder}').glob('publications-*.md')):
  fiscalYear=int(source.stem[-4:])
  parser=Citations();parser.feed(source.read_text().split('---',2)[2])
  for i,r in enumerate(parser.records):
   c=r['citation'].strip();r['citation']=c;r['id']=r['id'] or f'publication-{fiscalYear}-{i+1}'
   section=r['section'].lower()
   r['group']='journal' if ('論文誌' in section or 'journal' in section) else 'international' if any(x in section for x in ['国際','international','ポスター','poster','デモ','demo']) else 'domestic' if any(x in section for x in ['研究会','国内','domestic','workshop']) else 'other'
   m=re.search(r'[“”"](.+?)[“”"]',c,re.S)
   r.update(title=m.group(1).strip(' ，,' ) if m else c,authors=c[:m.start()].strip(' ，,') if m else '',venue='')
   if m:
    tail=c[m.end():].strip(' ，,');r['venue']=re.split(r'[,，]\s*(?:[Vv]ol\.?|\d+\s*[（(]|\d+巻|[Pp][Pp]?\.|Article|To appear|in press|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',tail,maxsplit=1)[0]
   r['format']='Extended Abstract' if 'extended abstracts' in c.lower() else ''
   r['presentation']='demo' if ('デモ' in section or 'demo' in section) else 'poster' if ('ポスター' in section or 'poster' in section) else ''
   r['review']='unknown';r['track']='workshop' if ('国際研究会' in section or 'international workshops' in section) else '';r['status']='forthcoming' if re.search(r'to appear|in press',c,re.I) else ''
   dates=re.findall(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+((?:19|20)\d{2})',c,re.I)
   r['researchLinks']=sorted({dest for url in r['links'] for dest in research_links.get(link_key(url),set())})
   r['month']=months.get(dates[-1][0].title(),0) if dates else 0;r['sourceOrder']=i
   r['year']=int(dates[-1][1]) if dates else fiscalYear;r['fiscalYear']=fiscalYear
   r['dateStart']=f"{r['year']}-{r['month']:02d}-01" if r['month'] else ''
   r['dateEnd']=f"{r['year']}-{r['month']:02d}-{calendar.monthrange(r['year'],r['month'])[1]}" if r['month'] else ''
   rows.append(r)
 data[lang]=sorted(rows,key=lambda r:(-r['year'],-r['month'],r['sourceOrder']))
 print(lang,len(rows),'records;',sum(not r['authors'] for r in rows),'unparsed')
Path('hugo/data/publication_preview.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
