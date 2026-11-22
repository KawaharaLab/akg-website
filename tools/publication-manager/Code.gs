const FIELDS = [["id", "論文ID"], ["title", "題名"], ["authors", "著者（掲載順）"], ["venue", "採録先"], ["type", "業績種別", ["未分類", "論文誌", "国際会議", "国内会議・研究会", "解説", "講演", "その他"]], ["format", "発表形式", ["未確認", "論文", "口頭", "ポスター", "デモ", "その他"]], ["peer_review", "査読", ["未確認", "有", "無"]], ["publication_month", "発行年月"], ["expected_month", "刊行予定年月"], ["volume", "巻"], ["issue", "号"], ["pages", "ページ"], ["article_number", "記事番号"], ["doi", "DOI"], ["url", "論文ページURL"], ["language", "言語", ["未確認", "ja", "en", "その他"]], ["publication_status", "刊行状態", ["未確認", "投稿中", "採録済み", "刊行予定", "オンライン公開済み", "正式刊行済み", "発表済み"]], ["visibility", "サイト掲載", ["非公開", "公開"]], ["review_status", "確認状態", ["未確認", "暫定確認済み", "確認済み"]], ["owner_email", "確認担当メール"], ["last_checked", "最終確認日"], ["next_check", "次回確認日"], ["project_ids", "関連研究ID"], ["funding_ids", "助成課題ID"], ["acknowledgement", "謝辞原文"], ["notes", "内部メモ"], ["legacy_citation", "旧巻号ページ原文"], ["legacy_date", "旧年月原文"], ["legacy_type", "旧種別"], ["source_row", "旧シート行"], ["created_at", "登録日時"], ["updated_at", "更新日時"], ["revision", "改訂番号"], ["source_url", "補完情報の出典"], ["metadata_checked_at", "補完取得日時"], ["location", "開催地"], ["awards", "受賞等"], ["group_scope", "グループ業績の対象", ["未確認", "対象", "対象外（別グループ）", "対象外（重複）"]]];
const APP_HTML = "<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><style>\n:root{font:14px/1.6 system-ui,sans-serif;color:#252525;background:#f6f5f2}*{box-sizing:border-box}body{margin:0}header{padding:20px 26px;background:white;border-bottom:1px solid #ddd;display:flex;justify-content:space-between;align-items:center}h1{font-size:22px;margin:0}h2{font-size:16px}main{padding:20px 26px;max-width:1100px;margin:auto}button,input,select,textarea{font:inherit}button{border:1px solid #bbb;border-radius:5px;background:white;padding:8px 14px;cursor:pointer}button.primary{background:#a81b36;color:white;border-color:#a81b36}button:disabled{opacity:.5;cursor:wait}.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.row input{flex:1;min-width:200px}input,select,textarea{border:1px solid #bbb;border-radius:4px;padding:8px;width:100%;background:white}textarea{min-height:76px;resize:vertical}label{display:block}label span{display:block;color:#555;font-size:12px;margin:0 0 4px}section{background:white;padding:18px;border:1px solid #ddd;border-radius:7px;margin-bottom:16px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.wide{grid-column:1/-1}small,.muted{color:#666}#status{white-space:pre-line;padding:12px 0}#status.error{color:#a01731}#searchResults button,#due button{display:block;width:100%;text-align:left;margin:6px 0}.pill{font-size:12px;background:#eee;padding:3px 8px;border-radius:20px}details{margin:16px 0}summary{cursor:pointer;font-weight:600}.diff{display:grid;grid-template-columns:28px 110px 1fr 1fr;gap:8px;padding:12px 0;border-bottom:1px solid #eee;overflow-wrap:anywhere}.diff input{width:auto}.diff .label{font-weight:600}.actions{position:sticky;bottom:0;background:#fff;padding:14px 0;border-top:1px solid #ddd}.check{display:flex;align-items:center;gap:8px}.check input{width:auto}#legacy{white-space:pre-wrap;overflow-wrap:anywhere}#previewNotice{padding:12px;background:#fff4d8}a{color:#8c1730}#conflicts{white-space:pre-line}#due{max-height:260px;overflow:auto}@media(max-width:650px){.grid{grid-template-columns:1fr}.diff{grid-template-columns:24px 1fr}.diff .old,.diff .new{grid-column:2}main{padding:14px}header{padding:14px}.row input{min-width:140px}}\n</style></head><body><div id=\"previewNotice\" hidden>画面確認用です。シートへの保存・外部取得は接続されていません。実際の入力は新シートのメニューから開きます。</div><header><div><small>AKG · Publications</small><h1>業績を登録・確認する</h1></div><button id=\"newBtn\">新規登録</button></header><main>\n<section><div class=\"row\"><input id=\"search\" aria-label=\"既存論文を検索\" placeholder=\"題名・DOI・論文IDで既存の登録を探す\"><button id=\"searchBtn\">検索</button></div><div id=\"searchResults\"></div><details><summary>確認期限が来ている業績 <span id=\"dueCount\" class=\"pill\">—</span></summary><p class=\"muted\">確認担当と次回確認日を見直せます。メールやSlackへの自動送信はありません。</p><div id=\"due\"></div></details></section>\n<details><summary>川原先生の業績から登録漏れ候補を探す</summary><section><div class=\"row\"><input id=\"discoveryYear\" type=\"number\" min=\"1900\" max=\"2099\" value=\"2026\" aria-label=\"検索する年\"><button id=\"discoverBtn\" type=\"button\">外部の業績を確認</button></div><p class=\"muted\">他の先生だけの業績は漏れと判定しません。川原先生の氏名一致も本人・掲載対象の確認が必要です。</p><div id=\"discoveryResults\"></div></section></details><div id=\"status\" role=\"status\" aria-live=\"polite\">読み込み中…</div><form id=\"editor\"><section><div class=\"row\"><h2 id=\"recordLabel\">新規登録</h2><span id=\"recordId\" class=\"pill\"></span></div><div class=\"row\"><input id=\"lookup\" placeholder=\"DOI または論文のWebページURL\" aria-label=\"書誌情報の取得元\"><button type=\"button\" id=\"lookupBtn\">書誌情報を取得</button></div><p class=\"muted\">取得した候補を確認し、使いたい項目だけ選べます。未確定の項目は空欄のまま保存できます。</p><div id=\"candidate\" hidden><p id=\"source\"></p><div id=\"diffs\"></div><button id=\"applyBtn\" type=\"button\">選択した候補を入力欄に反映</button><p class=\"muted\">入力欄への反映後、下の「保存」で台帳に記録します。</p></div></section>\n<section><h2>書誌情報</h2><div id=\"bibliography\" class=\"grid\"></div></section>\n<section><h2>掲載と確認</h2><p class=\"muted\">刊行の段階、書誌の確認、このグループの業績かどうかを別々に管理します。</p><div id=\"workflow\" class=\"grid\"></div><div class=\"row\" style=\"margin-top:12px\"><button id=\"laterBtn\" type=\"button\">次の確認を30日後にする</button><label class=\"check\"><input id=\"markChecked\" type=\"checkbox\">今回、内容を確認した</label></div></section>\n<details><summary>研究・助成・補足情報</summary><section><div id=\"extra\" class=\"grid\"></div><p id=\"catalogHelp\" class=\"muted\"></p></section></details>\n<details id=\"legacyDetails\" hidden><summary>移行元の情報</summary><section id=\"legacy\"></section></details>\n<div id=\"conflicts\"></div><label id=\"duplicateBox\" class=\"check\" hidden><input id=\"confirmDuplicates\" type=\"checkbox\">候補を確認し、別の発表として登録する必要がある</label>\n<div class=\"actions row\"><button type=\"submit\" class=\"primary\" id=\"saveBtn\">保存</button><span class=\"muted\">現在のサイトへの自動反映は未接続です。</span></div></form></main><script>\nconst PREVIEW_FIELDS=[[\"id\", \"論文ID\"], [\"title\", \"題名\"], [\"authors\", \"著者（掲載順）\"], [\"venue\", \"採録先\"], [\"type\", \"業績種別\", [\"未分類\", \"論文誌\", \"国際会議\", \"国内会議・研究会\", \"解説\", \"講演\", \"その他\"]], [\"format\", \"発表形式\", [\"未確認\", \"論文\", \"口頭\", \"ポスター\", \"デモ\", \"その他\"]], [\"peer_review\", \"査読\", [\"未確認\", \"有\", \"無\"]], [\"publication_month\", \"発行年月\"], [\"expected_month\", \"刊行予定年月\"], [\"volume\", \"巻\"], [\"issue\", \"号\"], [\"pages\", \"ページ\"], [\"article_number\", \"記事番号\"], [\"doi\", \"DOI\"], [\"url\", \"論文ページURL\"], [\"language\", \"言語\", [\"未確認\", \"ja\", \"en\", \"その他\"]], [\"publication_status\", \"刊行状態\", [\"未確認\", \"投稿中\", \"採録済み\", \"刊行予定\", \"オンライン公開済み\", \"正式刊行済み\", \"発表済み\"]], [\"visibility\", \"サイト掲載\", [\"非公開\", \"公開\"]], [\"review_status\", \"確認状態\", [\"未確認\", \"暫定確認済み\", \"確認済み\"]], [\"owner_email\", \"確認担当メール\"], [\"last_checked\", \"最終確認日\"], [\"next_check\", \"次回確認日\"], [\"project_ids\", \"関連研究ID\"], [\"funding_ids\", \"助成課題ID\"], [\"acknowledgement\", \"謝辞原文\"], [\"notes\", \"内部メモ\"], [\"legacy_citation\", \"旧巻号ページ原文\"], [\"legacy_date\", \"旧年月原文\"], [\"legacy_type\", \"旧種別\"], [\"source_row\", \"旧シート行\"], [\"created_at\", \"登録日時\"], [\"updated_at\", \"更新日時\"], [\"revision\", \"改訂番号\"], [\"source_url\", \"補完情報の出典\"], [\"metadata_checked_at\", \"補完取得日時\"], [\"location\", \"開催地\"], [\"awards\", \"受賞等\"], [\"group_scope\", \"グループ業績の対象\", [\"未確認\", \"対象\", \"対象外（別グループ）\", \"対象外（重複）\"]]];\n\nlet schema=[],bootstrap=null,current={},metadata=null,busy=false,dirty=false;\nconst $=id=>document.getElementById(id),preview=!(window.google&&google.script&&google.script.run);\nfunction message(s,error=false){$('status').textContent=s;$('status').className=error?'error':'';}\nfunction setBusy(v){busy=v;document.querySelectorAll('button').forEach(b=>b.disabled=v);}\nfunction call(name,...args){return new Promise((resolve,reject)=>{if(preview)return reject(Error('画面確認用ではこの操作は接続されていません。'));google.script.run.withSuccessHandler(resolve).withFailureHandler(reject)[name](...args);});}\nfunction safeLink(url){try{const u=new URL(url);return /^https?:$/.test(u.protocol)?u.href:null;}catch{return null;}}\nfunction renderFields(){const bib=['title','authors','venue','type','format','peer_review','publication_month','expected_month','volume','issue','pages','article_number','doi','url','language'];const flow=['publication_status','visibility','review_status','group_scope','owner_email','last_checked','next_check'];const extra=['project_ids','funding_ids','acknowledgement','notes','location','awards'];\n for(const [k,label,options] of schema){const group=bib.includes(k)?'bibliography':flow.includes(k)?'workflow':extra.includes(k)?'extra':null;if(!group)continue;const wrap=document.createElement('label'),span=document.createElement('span');span.textContent=label;wrap.append(span);let input;if(options){input=document.createElement('select');for(const o of options){const opt=document.createElement('option');opt.value=o;opt.textContent=o;input.append(opt);}}else{input=document.createElement(['authors','title','acknowledgement','notes'].includes(k)?'textarea':'input');if(input.tagName==='INPUT')input.type=k.includes('month')?'month':['last_checked','next_check'].includes(k)?'date':k==='owner_email'?'email':'text';}input.id='f_'+k;input.name=k;if(k==='last_checked')input.readOnly=true;if(k==='title')input.required=true;if(['title','authors','venue','url','notes','acknowledgement'].includes(k))wrap.className='wide';wrap.append(input);$(group).append(wrap);}}\nfunction blank(){const r={};for(const [k,,opts] of schema)r[k]=opts?opts[0]:'';return r;}\nfunction showRecord(r){current=r;for(const [k] of schema){const input=$('f_'+k);if(input)input.value=r[k]||'';}$('recordLabel').textContent=r.id?'登録内容を編集':'新規登録';$('recordId').textContent=r.id||'未保存';$('lookup').value=r.doi||r.url||'';$('candidate').hidden=true;$('duplicateBox').hidden=true;$('confirmDuplicates').checked=false;$('markChecked').checked=false;$('conflicts').textContent='';$('legacyDetails').hidden=!r.source_row;$('legacy').textContent='元シート '+(r.source_row||'')+'行\\n旧年月：'+(r.legacy_date||'')+'\\n旧種別：'+(r.legacy_type||'')+'\\n旧巻号ページ：'+(r.legacy_citation||'');metadata=null;dirty=false;}\nasync function loadRecord(id){if(dirty&&!confirm('保存していない変更があります。読み込み直しますか？'))return;setBusy(true);try{showRecord(await call('getRecord',id));message('読み込みました。');}catch(e){message(e.message,true);}finally{setBusy(false);}}\nfunction renderLists(){const q=$('search').value.toLowerCase();$('searchResults').replaceChildren();if(q){const found=bootstrap.records.filter(r=>[r.title,r.doi,r.id].join(' ').toLowerCase().includes(q));for(const r of found.slice(0,30)){const b=document.createElement('button');b.type='button';b.textContent=r.id+' · '+r.title;b.onclick=()=>loadRecord(r.id);$('searchResults').append(b);}if(!found.length)$('searchResults').textContent='該当する登録はありません。';if(found.length>30)$('searchResults').append('先頭30件を表示しています。検索語を追加してください。');}\n const due=bootstrap.records.filter(r=>r.next_check&&r.next_check<=bootstrap.today);$('dueCount').textContent=due.length+'件';$('due').replaceChildren();for(const r of due){const b=document.createElement('button');b.type='button';b.textContent=r.next_check+' · '+(r.owner_email||'担当未設定')+' · '+r.title;b.onclick=()=>loadRecord(r.id);$('due').append(b);}}\n$('discoverBtn').onclick=async()=>{setBusy(true);try{const result=await call('findKawaharaCandidates',$('discoveryYear').value);$('discoveryResults').replaceChildren();const p=document.createElement('p');p.textContent=result.notice+' 取得 '+result.scanned+'件 / 氏名一致 '+result.matched+'件 / 未一致候補 '+result.candidates.length+'件。';$('discoveryResults').append(p);for(const r of result.candidates){const wrap=document.createElement('p'),b=document.createElement('button');b.type='button';b.textContent=r.title+' — 書誌を確認';b.onclick=()=>{if(dirty&&!confirm('未保存の入力を破棄して候補を確認しますか？'))return;showRecord(blank());$('lookup').value=r.doi||r.url;$('lookupBtn').click();};wrap.append(b);$('discoveryResults').append(wrap);}message('候補を確認できます。台帳にはまだ登録していません。');}catch(e){message(e.message,true);}finally{setBusy(false);}};\n$('searchBtn').onclick=renderLists;$('search').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();renderLists();}});\n$('newBtn').onclick=()=>{if(!dirty||confirm('保存していない変更を破棄しますか？')){showRecord(blank());message('新しい業績を入力してください。');}};\n$('editor').addEventListener('input',event=>{dirty=true;if(event.target.id!=='confirmDuplicates')$('confirmDuplicates').checked=false;});\n$('lookupBtn').onclick=async()=>{setBusy(true);message('書誌情報を取得しています…');try{metadata=await call('lookupMetadata',$('lookup').value);$('source').replaceChildren();const a=document.createElement('a');const url=safeLink(metadata.source);a.textContent=metadata.provider;if(url){a.href=url;a.target='_blank';a.rel='noopener noreferrer';}$('source').append('取得元：',a,' · '+metadata.fetched_at);$('diffs').replaceChildren();for(const [k,label] of schema){const input=$('f_'+k),value=metadata.values[k];if(!input||!value||input.value===value)continue;const row=document.createElement('div');row.className='diff';const check=document.createElement('input');check.type='checkbox';check.dataset.key=k;check.checked=!input.value;check.setAttribute('aria-label',label+'を採用');const name=document.createElement('span');name.className='label';name.textContent=label;const old=document.createElement('span');old.className='old';old.textContent='現在：'+(input.value||'未入力');const proposed=document.createElement('span');proposed.className='new';proposed.textContent='候補：'+value;row.append(check,name,old,proposed);$('diffs').append(row);}$('candidate').hidden=false;message(metadata.notice||'変更する項目を選んでください。題名・著者・DOIが同じ論文を指すか確認してください。');}catch(e){message(e.message,true);}finally{setBusy(false);}};\n$('applyBtn').onclick=()=>{let count=0;for(const box of $('diffs').querySelectorAll('input:checked')){$('f_'+box.dataset.key).value=metadata.values[box.dataset.key];count++;}if(count){current.source_url=metadata.source;current.metadata_checked_at=metadata.fetched_at;dirty=true;$('confirmDuplicates').checked=false;}message(count+'項目を入力欄に反映しました。保存すると台帳に記録します。');};\n$('laterBtn').onclick=()=>{const d=new Date(bootstrap.today+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+30);$('f_next_check').value=d.toISOString().slice(0,10);dirty=true;};\n$('editor').onsubmit=async e=>{e.preventDefault();if(busy)return;const values={};for(const [k] of schema){const input=$('f_'+k);if(input)values[k]=input.value;}values.source_url=current.source_url||'';values.metadata_checked_at=current.metadata_checked_at||'';setBusy(true);try{const result=await call('saveRecord',{id:current.id||'',version:current._version||'',values,markChecked:$('markChecked').checked,confirmDuplicates:$('confirmDuplicates').checked});if(!result.saved){$('conflicts').textContent=[...(result.errors||[]),...(result.warnings||[])].join('\\n');$('duplicateBox').hidden=!(result.warnings||[]).length;message('保存していません。指摘を確認してください。',true);}else{showRecord(await call('getRecord',result.id));bootstrap=await call('getBootstrap');renderLists();message('保存しました。'+(result.warnings.length?'\\n'+result.warnings.join('\\n'):''));}}catch(err){message(err.message,true);}finally{setBusy(false);}};\nwindow.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});\nasync function init(){try{if(preview){$('previewNotice').hidden=false;bootstrap={fields:PREVIEW_FIELDS,today:new Date().toISOString().slice(0,10),records:[],projects:[],funding:[]};}else bootstrap=await call('getBootstrap');schema=bootstrap.fields;renderFields();showRecord(blank());renderLists();$('catalogHelp').textContent='登録済みの研究ID：'+(bootstrap.projects.map(r=>r[0]+' '+r[1]).join(' / ')||'なし')+'。助成課題ID：'+(bootstrap.funding.map(r=>r[0]+' '+r[3]).join(' / ')||'なし')+'。複数IDはセミコロン区切り。';message(preview?'画面確認用：入力欄と選択肢を確認できます。':'新規登録、または検索から既存の業績を選んでください。');}catch(e){message(e.message,true);}}\ninit();\n</script></body></html>\n";
/* Pure bibliography parsing and validation. Shared by Apps Script and tests. */
function cleanText(value) {
  return String(value == null ? '' : value).replace(/<[^>]*>/g, '').replace(/&#(x[0-9a-f]+|\d+);/gi, function (_, n) {
    var cp = n[0].toLowerCase() === 'x' ? parseInt(n.slice(1), 16) : Number(n);
    return cp > 0 && cp <= 0x10ffff ? String.fromCodePoint(cp) : '';
  }).replace(/&(amp|quot|apos|lt|gt|nbsp);/g, function (_, n) { return {amp:'&',quot:'"',apos:"'",lt:'<',gt:'>',nbsp:' '}[n]; }).trim();
}
function normalizeDoi(value) {
  var s = String(value || '').trim().replace(/^doi\s*:\s*/i, '').replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '');
  try { s = decodeURIComponent(s); } catch (_) {}
  return /^10\.\d{4,9}\/[^\s<>"?#]+$/i.test(s) ? s : '';
}
function normalizeTitle(s) { return cleanText(s).normalize('NFKC').toLowerCase().replace(/[\s\p{P}\p{S}]/gu, ''); }
function validMonth(s) { return /^(19|20)\d{2}-(0[1-9]|1[0-2])$/.test(s); }
function validDay(s) { return /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(Date.parse(s)) && new Date(s).toISOString().slice(0,10) === s; }
function nextCheckDate(record, today) {
  if (record.review_status === '確認済み' && /^(正式刊行済み|発表済み)$/.test(record.publication_status)) return '';
  if (validMonth(record.expected_month)) {
    var next = new Date(record.expected_month + '-01T00:00:00Z'); next.setUTCMonth(next.getUTCMonth() + 1);
    if (next.toISOString().slice(0,10) > today) return next.toISOString().slice(0,10);
  }
  var d = new Date(today + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate()+60); return d.toISOString().slice(0,10);
}
function monthFromParts(p) {
  if (!p || !p[0] || !p[0][1]) return '';
  var s = String(p[0][0]) + '-' + String(p[0][1]).padStart(2,'0'); return validMonth(s) ? s : '';
}
function fromCrossref(m) {
  var first = function(v) { return cleanText(Array.isArray(v) ? v[0] : v); };
  var r = {title:first(m.title)+(first(m.subtitle)?': '+first(m.subtitle):''), authors:(m.author||[]).map(function(a){return cleanText(a.name || [a.given,a.family].filter(Boolean).join(' '));}).join('; '),
    venue:first(m['container-title']), doi:normalizeDoi(m.DOI), url:m.URL || '', volume:first(m.volume), issue:first(m.issue), pages:first(m.page), article_number:first(m['article-number'])};
  r.publication_month = monthFromParts((m['published-print'] || m['published-online'] || m.issued || {})['date-parts']);
  if (m.type === 'journal-article') r.type='論文誌';
  // Crossref proceedings-article does not establish international/domestic or oral/poster.
  if (['ja','en'].includes(m.language)) r.language=m.language;
  return r;
}
function fromDataCite(m) {
  return {title:cleanText((m.titles||[])[0] && m.titles[0].title),authors:(m.creators||[]).map(function(a){return cleanText(a.name || [a.givenName,a.familyName].filter(Boolean).join(' '));}).join('; '),doi:normalizeDoi(m.doi),url:m.url||''};
}
function fromHtml(html) {
  var tags = {}, re=/<meta\b[^>]*>/gi, tag;
  while ((tag=re.exec(html))) {
    var attrs={}, ar=/([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g, a;
    while((a=ar.exec(tag[0]))) attrs[a[1].toLowerCase()]=cleanText(a[2]===undefined?(a[3]===undefined?a[4]:a[3]):a[2]);
    var key=(attrs.name||attrs.property||'').toLowerCase();
    if(key && attrs.content) (tags[key]||(tags[key]=[])).push(attrs.content);
  }
  var pick=function(keys){for(var i=0;i<keys.length;i++)if(tags[keys[i]])return tags[keys[i]][0];return '';};
  var d=pick(['citation_publication_date','citation_date','dc.date']); var match=d.match(/^(\d{4})[-/](\d{1,2})(?:[-/]|$)/);
  var r={title:pick(['citation_title','dc.title','dcterms.title']),authors:(tags.citation_author||tags['dc.creator']||[]).join('; '),venue:pick(['citation_journal_title','citation_conference_title']),doi:normalizeDoi(pick(['citation_doi','dc.identifier.doi','dc.identifier'])),volume:pick(['citation_volume']),issue:pick(['citation_issue'])};
  if(match)r.publication_month=match[1]+'-'+match[2].padStart(2,'0');
  var p=pick(['citation_firstpage']),q=pick(['citation_lastpage']);r.pages=p+(q&&q!==p?'-'+q:'');
  return r;
}
function validateRecord(record, records, schema) {
  var errors=[],warnings=[];
  if(!record.title.trim())errors.push('題名を入力してください。');
  schema.forEach(function(f){if(f[2] && !f[2].includes(record[f[0]]))errors.push(f[1]+'の選択が不正です。');});
  ['publication_month','expected_month'].forEach(function(k){if(record[k]&&!validMonth(record[k]))errors.push(k+'は YYYY-MM または空欄にしてください。');});
  ['last_checked','next_check'].forEach(function(k){if(record[k]&&!validDay(record[k]))errors.push(k+'は有効な YYYY-MM-DD にしてください。');});
  if(record.doi&&!normalizeDoi(record.doi))errors.push('DOIの形式を確認してください。');
  if(record.url&&!/^https?:\/\/[^\s]+$/i.test(record.url))errors.push('論文ページURLは http(s):// から入力してください。');
  if(record.owner_email&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(record.owner_email))errors.push('確認担当メールの形式を確認してください。');
  if(record.visibility==='公開'){
    if(record.group_scope!=='対象')errors.push('このグループの業績として対象を選んでください。');
    if(!record.authors||!record.venue||record.type==='未分類')errors.push('公開には著者・採録先・業績種別が必要です。');
    if(record.review_status==='未確認'||['未確認','投稿中'].includes(record.publication_status))errors.push('公開前に確認状態と刊行状態を指定してください。');
    if(record.review_status==='暫定確認済み'&&!record.owner_email)errors.push('暫定公開には確認担当メールが必要です。');
  }
  records.forEach(function(other){
    if(other.id===record.id)return;
    var sameDoi=record.doi&&other.doi&&normalizeDoi(record.doi).toLowerCase()===normalizeDoi(other.doi).toLowerCase();
    if(sameDoi||normalizeTitle(record.title)===normalizeTitle(other.title))warnings.push('重複候補 '+other.id+'：'+other.title+'（'+(sameDoi?'同じDOI':'同じ題名')+'）');
  });
  return {errors:errors,warnings:warnings};
}

/* Spreadsheet-bound Apps Script. Never deployed as a public web app. */
function onOpen() { SpreadsheetApp.getUi().createMenu('Publication管理').addItem('入力・編集画面を開く','openManager').addToUi(); }
function openManager() { SpreadsheetApp.getUi().showModalDialog(HtmlService.createHtmlOutput(APP_HTML).setWidth(1100).setHeight(800),'Publication管理'); }
function book_() { return SpreadsheetApp.getActiveSpreadsheet(); }
function table_() { var s=book_().getSheetByName('Publications'); if(!s)throw Error('Publicationsシートがありません。'); var heads=s.getRange(1,1,1,FIELDS.length).getDisplayValues()[0]; if(JSON.stringify(heads)!==JSON.stringify(FIELDS.map(function(f){return f[1];})))throw Error('列構成が変わっています。見出しを確認してください。');return s; }
function today_() {return Utilities.formatDate(new Date(),'Asia/Tokyo','yyyy-MM-dd');}
function stamp_() {return new Date().toISOString();}
function fingerprint_(values) {return Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,JSON.stringify(values)));}
function toRecord_(row) {var r={};FIELDS.forEach(function(f,i){r[f[0]]=String(row[i]||'');});r._version=fingerprint_(row);return r;}
function records_() {var s=table_();return s.getLastRow()<2?[]:s.getRange(2,1,s.getLastRow()-1,FIELDS.length).getDisplayValues().filter(function(r){return r[0];}).map(toRecord_);}
function catalog_(name) {var s=book_().getSheetByName(name);return s&&s.getLastRow()>1?s.getRange(2,1,s.getLastRow()-1,s.getLastColumn()).getDisplayValues().filter(function(r){return r[0];}):[];}
function getBootstrap() {return {fields:FIELDS,today:today_(),records:records_().map(function(r){return {id:r.id,title:r.title,doi:r.doi,next_check:r.next_check,owner_email:r.owner_email,review_status:r.review_status,publication_status:r.publication_status};}),projects:catalog_('研究'),funding:catalog_('助成課題')};}
function getRecord(id) {var r=records_().find(function(r){return r.id===id;});if(!r)throw Error('論文が見つかりません。');return r;}
function emptyRecord_() {var r={};FIELDS.forEach(function(f){r[f[0]]=f[2]?f[2][0]:'';});return r;}
function safeCell_(v) {v=String(v||'');return /^[=+@-]/.test(v)?"'"+v:v;}
function saveRecord(payload) {
  var lock=LockService.getDocumentLock();lock.waitLock(10000);
  try {
    var all=records_(),old=payload.id?all.find(function(r){return r.id===payload.id;}):null;
    if(payload.id&&!old)throw Error('対象が削除されています。再読み込みしてください。');
    if(old&&old._version!==payload.version)throw Error('別の編集が保存されています。再読み込みして変更を確認してください。');
    var record=old?Object.assign({},old):emptyRecord_();
    var protectedKeys=['id','created_at','updated_at','revision','source_row','legacy_date','legacy_type','legacy_citation','last_checked'];
    FIELDS.forEach(function(f){if(!protectedKeys.includes(f[0])&&Object.prototype.hasOwnProperty.call(payload.values||{},f[0]))record[f[0]]=String(payload.values[f[0]]||'').trim();});
    record.doi=normalizeDoi(record.doi)||record.doi;
    var check=validateRecord(record,all,FIELDS);
    var changedBibliography=old&&['title','authors','venue','doi','publication_month','volume','issue','pages','article_number'].some(function(k){return record[k]!==old[k];});
    if(record.review_status!=='未確認'&&!payload.markChecked&&(!old||record.review_status!==old.review_status||changedBibliography))check.errors.push('確認状態を確定・維持するには「今回、内容を確認した」にチェックしてください。');
    ['project_ids','funding_ids'].forEach(function(k){var ids=catalog_(k==='project_ids'?'研究':'助成課題').map(function(r){return r[0];});record[k].split(/[;,\n]/).map(function(v){return v.trim();}).filter(Boolean).forEach(function(v){if(!ids.includes(v))check.errors.push('未登録のID: '+v);});});
    if(check.errors.length)return {saved:false,errors:check.errors,warnings:check.warnings};
    if(check.warnings.length&&!payload.confirmDuplicates)return {saved:false,errors:[],warnings:check.warnings};
    if(!record.next_check)record.next_check=nextCheckDate(record,today_());
    if(payload.markChecked)record.last_checked=today_();
    if(!old){record.id='PUB-'+Utilities.getUuid();record.created_at=stamp_();}
    record.updated_at=stamp_();record.revision=String(Number(old?old.revision:0)+1);
    var sheet=table_(),ids=sheet.getRange(1,1,sheet.getLastRow(),1).getDisplayValues().map(function(r){return r[0];});
    var row=old?ids.indexOf(record.id)+1:sheet.getLastRow()+1;
    if(row>sheet.getMaxRows())sheet.insertRowsAfter(sheet.getMaxRows(),100);
    sheet.getRange(row,1,1,FIELDS.length).setValues([FIELDS.map(function(f){return safeCell_(record[f[0]]);})]);
    SpreadsheetApp.flush();
    var changes=FIELDS.filter(function(f){return (old?old[f[0]]:'')!==record[f[0]];}).map(function(f){return {field:f[0],before:old?old[f[0]]:'',after:record[f[0]]};});
    var result={saved:true,id:record.id,warnings:check.warnings};
    try {book_().getSheetByName('変更履歴').appendRow([stamp_(),record.id,Session.getActiveUser().getEmail()||'不明',old?'更新':'新規登録',record.revision,JSON.stringify(changes)]);} catch(e){result.warnings.push('保存済みですが変更履歴への記録に失敗しました。管理者に連絡してください。');}
    return result;
  } finally {lock.releaseLock();}
}
// Fetch only public HTTPS hosts; redirects are validated individually. No login cookies or sheet data sent.
function safeUrl_(input) {
 var m=String(input).match(/^https:\/\/([a-z0-9.-]+)(?::443)?(\/[^\s]*)?$/i);
 if(!m)throw Error('取得には公開HTTPSページのURLを指定してください。');
 var h=m[1].toLowerCase();
 if(!h.includes('.')||/^\d+(\.\d+){3}$/.test(h)||/(^|\.)(localhost|local|internal|invalid|test)$/.test(h)||h.endsWith('.local')||h.endsWith('.internal'))throw Error('このURLは取得できません。');
 return {url:input,host:h};
}
function fetchPublic_(url) {
 for(var i=0;i<5;i++){
   safeUrl_(url);
   var response=UrlFetchApp.fetch(url,{followRedirects:false,muteHttpExceptions:true,headers:{Accept:'application/json, text/html;q=0.9','User-Agent':'AKG-Publication-Manager/1.0'}}),code=response.getResponseCode();
   if([301,302,303,307,308].includes(code)){
     var headers=response.getAllHeaders(),key=Object.keys(headers).find(function(k){return k.toLowerCase()==='location';}),loc=key?String(headers[key]):'';
     if(loc.startsWith('/')){var host=url.match(/^https:\/\/[^/]+/)[0];loc=loc.startsWith('//')?'https:'+loc:host+loc;}
     if(!loc)throw Error('転送先を取得できません。');url=loc;continue;
   }
   if(code<200||code>=300)throw Error('取得先が HTTP '+code+' を返しました。DOIでの取得または手入力を試してください。');
   var text=response.getContentText();if(text.length>2000000)throw Error('ページが大きすぎます。DOIを入力してください。');
   return {text:text,url:url};
 }
 throw Error('転送回数が多いため取得を中止しました。');
}
function lookupDoi_(doi) {
 var endpoint='https://api.crossref.org/works/'+encodeURIComponent(doi);
 try {var m=JSON.parse(fetchPublic_(endpoint).text).message;return {values:fromCrossref(m),source:endpoint,provider:'Crossref'};}
 catch(e){
   var fallback='https://api.datacite.org/dois/'+encodeURIComponent(doi);
   try{return {values:fromDataCite(JSON.parse(fetchPublic_(fallback).text).data.attributes),source:fallback,provider:'DataCite'};}
   catch(_){throw Error('DOIの書誌情報を取得できませんでした。DOIの登録待ち・取得先の制限・一時的な接続障害の可能性があります。手入力で保存できます。');}
 }
}
function lookupMetadata(input) {
 input=String(input||'').trim();if(input.length>2048)throw Error('入力が長すぎます。');
 var d=normalizeDoi(input),result;
 if(d) result=lookupDoi_(d);
 else {
   var match=input.match(/^https:\/\/[^/]+\/doi\/(?:abs\/|full\/|pdf\/|epdf\/)?(10\.\d{4,9}\/[^?#]+)/i);
   if(match&&normalizeDoi(match[1]))result=lookupDoi_(normalizeDoi(match[1]));
   else {
    var page=fetchPublic_(input),values=fromHtml(page.text);values.url=page.url;
    if(!values.title&&!values.doi&&!values.authors)throw Error('このページから論文用メタデータを取得できません。DOIを入力するか手入力してください。');
    result={values:values,source:page.url,provider:'Webページの論文メタデータ'};
    if(values.doi){try {var enriched=lookupDoi_(values.doi);Object.keys(enriched.values).forEach(function(k){if(enriched.values[k])values[k]=enriched.values[k];});result.source=enriched.source;result.provider+=' + '+enriched.provider;}catch(e){result.notice=e.message;}}
   }
 }
 result.fetched_at=stamp_();return result;
}
function findKawaharaCandidates(year) {
 year=String(year);if(!/^(19|20)\d{2}$/.test(year))throw Error('検索する年を入力してください。');
 var url='https://api.crossref.org/works?query.author=Yoshihiro%20Kawahara&filter=from-pub-date:'+year+'-01-01,until-pub-date:'+year+'-12-31&rows=100';
 var message=JSON.parse(fetchPublic_(url).text).message,all=records_();
 var matches=(message.items||[]).filter(function(m){return (m.author||[]).some(function(a){return /^kawahara$/i.test(a.family||'')&&/^yoshihiro$/i.test(a.given||'');});});
 var candidates=matches.map(fromCrossref).filter(function(r){return !all.some(function(p){return (r.doi&&p.doi&&normalizeDoi(r.doi).toLowerCase()===normalizeDoi(p.doi).toLowerCase())||normalizeTitle(r.title)===normalizeTitle(p.title);});});
 return {source:url,year:year,scanned:(message.items||[]).length,matched:matches.length,candidates:candidates,notice:'Crossrefの関連度順・先頭100件以内から、著者名がYoshihiro Kawaharaと一致する候補を抽出しています。同姓同名・別版・掲載対象を確認してください。国内大会、DOI未登録、著者名がイニシャルのみの業績などは拾えません。網羅的な登録漏れ判定ではありません。'};
}
