"""Build a single pasteable bound Apps Script and a standalone UI preview."""
from pathlib import Path
import json
root=Path(__file__).resolve().parent
fields=json.loads((root/'schema.json').read_text())
page=(root/'Index.html').read_text().replace('<script>','<script>\nconst PREVIEW_FIELDS='+json.dumps(fields,ensure_ascii=False)+';\n',1)
(root/'preview.html').write_text(page)
code='const FIELDS = '+json.dumps(fields,ensure_ascii=False)+';\nconst APP_HTML = '+json.dumps(page,ensure_ascii=False)+';\n'+(root/'Core.js').read_text()+'\n'+(root/'Server.js').read_text()
(root/'Code.gs').write_text(code)
print('Built Code.gs and preview.html')
