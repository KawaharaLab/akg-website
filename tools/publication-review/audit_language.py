from pathlib import Path
from html.parser import HTMLParser
import ast,tarfile,json,re,unicodedata
source=ast.parse(Path('tools/build_publication_preview.py').read_text());exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.ClassDef)],type_ignores=[]),'<parser>','exec'))
def parse(s):
 p=Citations();p.feed(s.split('---',2)[-1]);return [r['citation'].strip() for r in p.records]
def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFC',s)).strip()
form=json.loads(Path('inventory/references/review-source.json').read_text());report={'years':[],'differences':[]};allold=[];allja=[]
with tarfile.open('archive/hugo-20260905.tgz') as tar:
 for p in sorted(Path('hugo/content').glob('publications-*.md')):
  year=int(p.stem[-4:]);ja=parse(p.read_text());en=parse(Path('hugo/content-en',p.name).read_text());matches=[m for m in tar.getmembers() if m.name.endswith('/content/'+p.name)];old=parse(tar.extractfile(matches[0]).read().decode()) if matches else []
  review=[r['citation'] for r in form if r['year']==year]
  item={'year':year,'old':len(old),'ja':len(ja),'en':len(en),'form':len(review),'japanese_citations':sum(bool(re.search('[ぁ-んァ-ン一-龯]',s)) for s in ja),'form_exact':ja==review,'old_normalized_equal':list(map(norm,old))==list(map(norm,ja)),'en_normalized_equal':list(map(norm,en))==list(map(norm,ja))};report['years'].append(item)
  for label,other in [('old',old),('en',en),('form',review)]:
   for i,(a,b) in enumerate(zip(ja,other)):
    if norm(a)!=norm(b):report['differences'].append({'year':year,'item':i+1,'compare':label,'ja':a,'other':b})
  allold+=old;allja+=ja
report['totals']={'citations':len(allja),'japanese':sum(bool(re.search('[ぁ-んァ-ン一-龯]',s)) for s in allja),'old':len(allold),'differences':len(report['differences'])}
Path('inventory/references/language-preservation-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
