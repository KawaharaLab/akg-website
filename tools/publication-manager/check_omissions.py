"""Read-only candidate extraction; never auto-add or remove a publication."""
import json,re,unicodedata,argparse
from difflib import SequenceMatcher
from pathlib import Path

def norm(s): return re.sub(r'[^\w]','',unicodedata.normalize('NFKC',s).casefold())
def kawahara(s): return bool(re.search(r'川原\s*圭博|(?:Y\.?\s*|Yoshihiro\s+)Kawahara',s,re.I))
def check(source,catalog):
 chunks=json.load(open(source))
 def rows(tab):return [(c['start']+i,[str(v or '') for v in r]) for c in chunks if c['tab']==tab for i,r in enumerate(c.get('values') or [])]
 main=[(n,r) for n,r in rows('シート1') if n>1 and len(r)>7 and r[7]]
 titles={norm(r[7]):n for n,r in main};results=[]
 for tab,start,t,a in [('memo_論文',2,11,12),('詳細確認_会議（2021年度）',3,5,4),('memo_会議',6,5,6)]:
  for n,r in rows(tab):
   if n<start or len(r)<=max(t,a) or not kawahara(r[a]) or not r[t] or norm(r[t]) in titles:continue
   score,key=max((SequenceMatcher(None,norm(r[t]),k).ratio(),k) for k in titles)
   results.append(['補助表',f'{tab} 行{n}',r[t],r[a],str(titles[key]),f'題名類似度 {score:.3f}。表記違い・別発表・掲載対象を確認。','未確認',''])
 for r in json.load(open(catalog))['records']:
  citation=r['citation'];titlematch=re.search(r'[“”"「](.+?)[“”"」]',citation)
  # Only the author segment counts; names in titles or acknowledgements do not establish authorship.
  authorpart=citation[:titlematch.start()] if titlematch else ''
  if not kawahara(authorpart):continue
  title=titlematch[1];key=norm(title)
  if len(key)<12 or key in titles:continue
  nc=norm(citation)
  if any(len(k)>15 and k in nc for k in titles):continue
  score,nearest=max((SequenceMatcher(None,key,k).ratio(),k) for k in titles)
  source=next((s for s in r['sources'] if s.get('kind')=='publications'),r['sources'][0])
  results.append(['既存サイト台帳',r['id']+' '+source.get('path',''),title,authorpart,str(titles[nearest]),f'題名類似度 {score:.3f}。未登録確定ではない。既存サイトの書誌自体の誤りも確認。','未確認',(r.get('urls') or [''])[0]])
 return results
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('catalog');p.add_argument('output');a=p.parse_args();r=check(a.source,a.catalog);Path(a.output).write_text(json.dumps(r,ensure_ascii=False));print(f'{len(r)} candidates; Kawahara-authored records only, no automatic inclusion.')
