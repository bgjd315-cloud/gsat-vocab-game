// 組出 index.html：把 src/words.json 與 src/reading/*.json 內嵌進 src/app.html
// 用法：python -I tools/build_data.py . && node build.js   （本機預覽待審短文：node build.js --drafts）
const fs = require('fs');
const path = require('path');
const tpl = fs.readFileSync(path.join(__dirname, 'src', 'app.html'), 'utf8');
const data = fs.readFileSync(path.join(__dirname, 'src', 'words.json'), 'utf8');
if (!tpl.includes('/*__DATA__*/[]')) throw new Error('app.html 找不到資料佔位符');
// 閱讀短文：正式版只放審過的（status ok）；加 --drafts 參數時連待審的一起放（本機預覽用）
const withDrafts = process.argv.includes('--drafts');
const rdir = path.join(__dirname, 'src', 'reading');
let reading = [];
if (fs.existsSync(rdir)) {
  for (const f of fs.readdirSync(rdir).filter(f => /^(l\d|tb).*\.json$/.test(f)).sort()) {
    reading = reading.concat(JSON.parse(fs.readFileSync(path.join(rdir, f), 'utf8')).filter(r => withDrafts ? !['deleted', 'retired'].includes(r.status) : r.status === 'ok'));
  }
}
const esc = s => s.replace(/<\/script/gi, '<\\/script');
let out = tpl.replace('/*__DATA__*/[]', () => esc(data));
out = out.replace('/*__READ__*/[]', () => esc(JSON.stringify(reading)));
// 分級小測用的國中字（含中文）
const jhp = path.join(__dirname, 'src', 'raw', 'jh_pool.json');
const jhpool = fs.existsSync(jhp) ? fs.readFileSync(jhp, 'utf8') : '[]';
out = out.replace('/*__JH__*/[]', () => esc(jhpool));
// 課本進度：各課單字（只放網站有的字的 id，app 端再過濾）
const tbp = path.join(__dirname, 'src', 'raw', 'textbook_lt.json');
const tb = fs.existsSync(tbp) ? fs.readFileSync(tbp, 'utf8') : 'null';
if (!out.includes('/*__TB__*/null')) throw new Error('app.html 找不到課本佔位符');
out = out.replace('/*__TB__*/null', () => esc(tb));
// 課本文法卡：src/examples/grammar.json（正式版只放 ok）
const grp = path.join(__dirname, 'src', 'examples', 'grammar.json');
let gr = fs.existsSync(grp) ? JSON.parse(fs.readFileSync(grp, 'utf8')).filter(c => withDrafts ? c.status !== 'deleted' : c.status === 'ok') : [];
// 擴充版文法卡 grammar_v2.json：預覽一律用新版；正式版只有新版審過（ok）才替換
const gr2p = path.join(__dirname, 'src', 'examples', 'grammar_v2.json');
if (fs.existsSync(gr2p)) {
  const v2 = {}; for (const c of JSON.parse(fs.readFileSync(gr2p, 'utf8'))) if (withDrafts ? c.status !== 'deleted' : c.status === 'ok') v2[c.id] = c;
  gr = gr.map(c => v2[c.id] || c);
}
// 構詞卡 src/examples/morph.json（b=9，與文法卡共用版面；正式版只放 ok）
const mop = path.join(__dirname, 'src', 'examples', 'morph.json');
if (fs.existsSync(mop)) gr = gr.concat(JSON.parse(fs.readFileSync(mop, 'utf8')).filter(c => withDrafts ? c.status !== 'deleted' : c.status === 'ok'));
if (!out.includes('/*__GR__*/[]')) throw new Error('app.html 找不到文法卡佔位符');
out = out.replace('/*__GR__*/[]', () => esc(JSON.stringify(gr)));
// 學測闖關（綜合測驗、文意選填）：src/examples/gsat_cz.json（原題＋官方答案＋本站中譯解析；正式版只放 ok）
const czp = path.join(__dirname, 'src', 'examples', 'gsat_cz.json');
const cz = fs.existsSync(czp) ? JSON.parse(fs.readFileSync(czp, 'utf8')).filter(c => withDrafts ? c.status !== 'deleted' : c.status === 'ok') : [];
if (!out.includes('/*__CZ__*/[]')) throw new Error('app.html 找不到學測闖關佔位符');
out = out.replace('/*__CZ__*/[]', () => esc(JSON.stringify(cz)));
// 學測闖關・翻譯題（歷屆＋句型特訓）：src/examples/gsat_tr.json（正式版只放 ok）
const trp = path.join(__dirname, 'src', 'examples', 'gsat_tr.json');
const trd = fs.existsSync(trp) ? JSON.parse(fs.readFileSync(trp, 'utf8')).filter(c => withDrafts ? c.status !== 'deleted' : c.status === 'ok') : [];
if (!out.includes('/*__TR__*/[]')) throw new Error('app.html 找不到翻譯題佔位符');
out = out.replace('/*__TR__*/[]', () => esc(JSON.stringify(trd)));
// 學測闖關・閱讀測驗：src/examples/gsat_rc.json（原題＋官方答案＋本站鷹架與解析；正式版只放 ok）
const rcp = path.join(__dirname, 'src', 'examples', 'gsat_rc.json');
const rc = fs.existsSync(rcp) ? JSON.parse(fs.readFileSync(rcp, 'utf8')).filter(c => withDrafts ? c.status !== 'deleted' : c.status === 'ok') : [];
if (!out.includes('/*__RC__*/[]')) throw new Error('app.html 找不到閱讀測驗佔位符');
out = out.replace('/*__RC__*/[]', () => esc(JSON.stringify(rc)));
// 歷屆學測詞彙題：src/raw/gsat_vocab_q.json（大考中心原題與答案）＋ src/examples/gsat_q.json（本站中譯與解析，正式版只放 ok）
const gqp = path.join(__dirname, 'src', 'raw', 'gsat_vocab_q.json');
let gq = fs.existsSync(gqp) ? JSON.parse(fs.readFileSync(gqp, 'utf8')) : [];
const gxp = path.join(__dirname, 'src', 'examples', 'gsat_q.json');
if (fs.existsSync(gxp)) {
  const gx = {}; for (const r of JSON.parse(fs.readFileSync(gxp, 'utf8'))) if (withDrafts ? r.status !== 'deleted' : r.status === 'ok') gx[r.y + '-' + r.n] = r;
  gq = gq.map(q => { const x = gx[q.y + '-' + q.n]; return x ? Object.assign({}, q, { zh: x.zh, oz: x.oz, ex: x.ex }, x.why ? { hint: x.hint, why: x.why, col: x.col, fam: x.fam, strat: x.strat } : {}) : q; });
}
if (!out.includes('/*__GQ__*/[]')) throw new Error('app.html 找不到學測題佔位符');
out = out.replace('/*__GQ__*/[]', () => esc(JSON.stringify(gq)));
// 詞性變化：src/examples/fam.json（正式版只放 status ok）
const famp = path.join(__dirname, 'src', 'examples', 'fam.json');
const fam = {};
if (fs.existsSync(famp)) for (const r of JSON.parse(fs.readFileSync(famp, 'utf8'))) {
  if (withDrafts ? r.status === 'deleted' : r.status !== 'ok') continue;
  if (r.fam.length || r.q) fam[r.id] = [r.fam, r.q];
}
if (!out.includes('/*__FAM__*/{}')) throw new Error('app.html 找不到詞性佔位符');
out = out.replace('/*__FAM__*/{}', () => esc(JSON.stringify(fam)));
// 進度改用單字編號存：改版前的固定順序（只能增加，不能改）
const oip = path.join(__dirname, 'src', 'raw', 'legacy_index.json');
if (!out.includes('/*__OLDIDX__*/[]')) throw new Error('app.html 找不到舊順序佔位符');
out = out.replace('/*__OLDIDX__*/[]', () => fs.readFileSync(oip, 'utf8').trim());
// KK 音標
const kkp = path.join(__dirname, 'src', 'raw', 'kk.json');
if (!out.includes('/*__KK__*/{}')) throw new Error('app.html 找不到音標佔位符');
out = out.replace('/*__KK__*/{}', () => esc(fs.existsSync(kkp) ? JSON.stringify(JSON.parse(fs.readFileSync(kkp, 'utf8'))) : '{}'));
// 多益主題包：既有字的「多益常見」標籤＋新字分組
const ttp = path.join(__dirname, 'src', 'raw', 'toeic_tags.json');
const tt = { ids: [], groups: {} };
if (fs.existsSync(ttp)) tt.ids = JSON.parse(fs.readFileSync(ttp, 'utf8')).ids;
const tep = path.join(__dirname, 'src', 'examples', 'toeic.json');
if (fs.existsSync(tep)) for (const r of JSON.parse(fs.readFileSync(tep, 'utf8'))) if (withDrafts ? r.status !== 'deleted' : r.status === 'ok') tt.groups[r.id] = r.group;
if (!out.includes('/*__TT__*/null')) throw new Error('app.html 找不到多益佔位符');
out = out.replace('/*__TT__*/null', () => esc(JSON.stringify(tt)));
fs.writeFileSync(path.join(__dirname, 'index.html'), out);
console.log('index.html', (out.length / 1024).toFixed(0) + ' KB', '閱讀篇數', reading.length);

// 離線快取 sw.js：VER＝圖片、音檔、圖示的檔名＋大小指紋，檔案有變（例如重錄音檔）手機上的舊快取就會自動換新
const swSrc = path.join(__dirname, 'src', 'sw.js');
if (fs.existsSync(swSrc)) {
  const crypto = require('crypto'), h = crypto.createHash('sha1');
  const walk = d => { if (!fs.existsSync(d)) return; for (const f of fs.readdirSync(d, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : 1)) {
    const p = path.join(d, f.name); if (f.isDirectory()) walk(p); else h.update(path.relative(__dirname, p) + ':' + fs.statSync(p).size + '\n'); } };
  ['img', 'audio', 'icons'].forEach(d => walk(path.join(__dirname, d)));
  const ver = h.digest('hex').slice(0, 10);
  fs.writeFileSync(path.join(__dirname, 'sw.js'), fs.readFileSync(swSrc, 'utf8').replace("/*__VER__*/'dev'", `'${ver}'`));
  console.log('sw.js', ver);
}
