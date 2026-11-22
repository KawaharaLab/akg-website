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
