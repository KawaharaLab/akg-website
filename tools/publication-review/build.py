#!/usr/bin/env python3
"""Build an offline questionnaire from original Japanese publication pages."""
from pathlib import Path
from html.parser import HTMLParser
import ast,hashlib,json,re
# Reuse the read-only parser definition, without executing the preview build.
source=ast.parse(Path('tools/build_publication_preview.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.ClassDef)],type_ignores=[]),'<citation-parser>','exec'))
rows=[]
for p in sorted(Path('hugo/content').glob('publications-*.md'),reverse=True):
 match=re.fullmatch(r'publications-(\d{4})',p.stem)
 if not match:continue
 year=int(match[1]);parser=Citations();parser.feed(p.read_text().split('---',2)[2])
 for ordinal,r in enumerate(parser.records,1):
  citation=r['citation'].strip();m=re.search(r'[“”"](.+?)[“”"]',citation,re.S);section=r['section']
  group='論文誌' if '論文誌' in section else '国際会議' if any(x in section for x in ['国際','ポスター','デモ']) else '国内会議・研究会' if any(x in section for x in ['国内','研究会']) else 'その他'
  key=f'{year}|{section}|{citation}|{ordinal}'
  rows.append(dict(id='p-'+hashlib.sha256(key.encode()).hexdigest()[:16],number=len(rows)+1,year=year,title=m[1].strip(' ，,') if m else citation,citation=citation,section=section,proposedGroup=group,links=r['links'],source=f'https://www.akg.t.u-tokyo.ac.jp/{p.stem}/'+('#'+r['id'] if r['id'] else ''),issues=[]))
# Candidate overlaps only: identical normalized title or DOI, never auto-merge.
indexes={}
for r in rows:
 keys={'title:'+re.sub(r'[^\w]','',r['title']).casefold()}
 for link in r['links']:
  m=re.search(r'10\.\d{4,9}/[^\s?#]+',link,re.I)
  if m:keys.add('doi:'+m[0].rstrip('/').casefold())
 for key in keys:indexes.setdefault(key,[]).append(r['id'])
for r in rows:
 related=set()
 for key,ids in indexes.items():
  if r['id'] in ids and len(ids)>1:related.update(ids)
 related.discard(r['id']);r['related']=sorted(related)
 if related:r['issues'].append('同題名・同DOI候補')
 if not r['links']:r['issues'].append('リンクなし')
 if re.search(r'to appear|in press',r['citation'],re.I):r['issues'].append('刊行状況の確認')
 if any(x in r['section'] for x in ['国際研究会','ポスター','デモ']):r['issues'].append('掲載枠・原稿種別の確認')
 if r['proposedGroup']=='その他':r['issues'].append('分類の確認')
template=Path('tools/publication-review/template.html').read_text()
Path('docs/publication-review.html').write_text(template.replace('__DATA__',json.dumps(rows,ensure_ascii=False).replace('<','\\u003c')))
Path('inventory/references/review-source.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(len(rows),'entries;',len(set(r['year'] for r in rows)),'years;',sum(bool(r['issues']) for r in rows),'with review flags')
