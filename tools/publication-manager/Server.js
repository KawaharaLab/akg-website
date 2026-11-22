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
