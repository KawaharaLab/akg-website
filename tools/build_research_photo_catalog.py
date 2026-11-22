#!/usr/bin/env python3
"""Refresh the admin photo catalog from existing research pages; run at repository root. Does not change slide selection."""
from pathlib import Path
import re,json,yaml
catalog=[]
assets=json.loads(Path('admin/config/home-photo-assets.json').read_text())
for p in Path('hugo/content/archives').glob('*.md'):
 _,h,b=p.read_text().split('---',2);m=yaml.safe_load(h)
 if 'research' not in m.get('categories',[]):continue
 en=Path('hugo/content-en/archives',p.name);me=yaml.safe_load(en.read_text().split('---',2)[1])
 images=list(dict.fromkeys(re.findall(r'!\[[^\]]*\]\(([^ )]+)',b)))
 images=[x for x in images if x.startswith('/') and Path('hugo/static'+x).is_file()]
 generated=[a['image'] for a in assets if a['researchId']==p.stem and Path('hugo/static'+a['image']).is_file()]
 images=list(dict.fromkeys(images+generated))
 if images:catalog.append({'id':p.stem,'title':m['title'],'titleEn':me['title'],'date':str(m['date']),'url':'/archives/'+p.stem+'/','images':images,'generatedImages':generated})
catalog.sort(key=lambda x:x['date'],reverse=True)
Path('admin/config/research-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
print(len(catalog), "research entries written")
