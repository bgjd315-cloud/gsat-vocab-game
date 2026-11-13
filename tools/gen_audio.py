# 用 Google Cloud Text-to-Speech 產生單字與例句的美式發音 MP3
# 金鑰放在 .secrets/google_tts_key.txt（已排除在 git 之外，不會上傳）
# 用法：
#   python -I -X utf8 tools/gen_audio.py . --dry        只計算字元數與檔案數，不呼叫 API
#   python -I -X utf8 tools/gen_audio.py . --words      產生單字（audio/w/<id>.mp3）
#   python -I -X utf8 tools/gen_audio.py . --sentences  產生編寫例句（audio/s/<id>.mp3）
#   python -I -X utf8 tools/gen_audio.py . --forms      產生詞性變化相關字（audio/f/<slug>.mp3）
#   python -I -X utf8 tools/gen_audio.py . --passages   產生文章逐段朗讀（audio/p/<id>_<段>.mp3）
#   python -I -X utf8 tools/gen_audio.py . --gsat       產生學測闖關文章朗讀（同樣放 audio/p/）
#   加 --limit 20 只做前 20 個（試聽用）；加 --force 連已存在的檔案也重錄（改語速時用）
# 已經存在的檔案會跳過；最後更新 audio/index.json 給網站讀取。
import json, os, re, sys, base64, time, urllib.request, urllib.error

ROOT = sys.argv[1]
args = sys.argv[2:]
DRY = '--dry' in args
FORCE = '--force' in args
LIMIT = int(args[args.index('--limit') + 1]) if '--limit' in args else None
VOICE_WORD = {'languageCode': 'en-US', 'name': 'en-US-Neural2-F'}   # 美式女聲
VOICE_SENT = {'languageCode': 'en-US', 'name': 'en-US-Neural2-F'}
CFG_WORD = {'audioEncoding': 'MP3', 'speakingRate': 0.9, 'sampleRateHertz': 24000}
CFG_SENT = {'audioEncoding': 'MP3', 'speakingRate': 0.82, 'sampleRateHertz': 24000}   # 約每分鐘 138 字，接近空中英語教室等學習節目的語速（原 0.95 約 166 字）

words = json.load(open(os.path.join(ROOT, 'src', 'words.json'), encoding='utf-8'))

def say_form(word):
    p = word.split('/')[0].strip()
    m = re.match(r"^([a-zA-Z'\- ]+)\(([a-z]+)\)([a-z]*)$", p)
    return (m.group(1) + m.group(3)) if m else re.sub(r'[()]', '', p)

jobs = []
if '--words' in args or DRY:
    jobs += [('w', r[0], (r[11] if len(r) > 11 else say_form(r[4])), VOICE_WORD, CFG_WORD) for r in words]
if '--sentences' in args or DRY:
    jobs += [('s', r[0], r[9][0], VOICE_SENT, CFG_SENT) for r in words if r[9]]
# 詞性變化的相關字（audio/f/<slug>.mp3）：只做網站單字表裡沒有錄音的形式
FORMS = {}
if '--forms' in args or DRY:
    have = set((r[11] if len(r) > 11 else say_form(r[4])).lower() for r in words)
    fp = os.path.join(ROOT, 'src', 'examples', 'fam.json')
    if os.path.exists(fp):
        for r in json.load(open(fp, encoding='utf-8')):
            for f in r['fam']:
                txt = f[0].strip(); low = txt.lower()
                if low in have: continue
                slug = re.sub(r'[^a-z0-9]+', '_', low).strip('_')
                if slug and slug not in FORMS: FORMS[slug] = low
    jobs += [('f', k, v, VOICE_WORD, CFG_WORD) for k, v in FORMS.items()]
# 學測翻譯題參考答案（audio/f/tr_<關卡>_<題>.mp3，網站用文字查錄音）
if '--trans' in args or DRY:
    tp = os.path.join(ROOT, 'src', 'examples', 'gsat_tr.json')
    if os.path.exists(tp):
        for s in json.load(open(tp, encoding='utf-8')):
            if s.get('status') != 'ok': continue
            for i, it in enumerate(s['items']):
                slug = re.sub(r'[^a-z0-9]+', '_', f"tr_{s['id']}_{i}".lower())
                FORMS[slug] = it['ref'].lower()
                jobs.append(('f', slug, it['ref'], VOICE_SENT, CFG_SENT))
# 文章逐段朗讀（audio/p/<文章id>_<段落序號>.mp3）：冒險日誌與課本延伸閱讀
PASS = {}
if '--passages' in args or DRY:
    import glob as _g
    CFG_PASS = {'audioEncoding': 'MP3', 'speakingRate': 0.82, 'sampleRateHertz': 22050}   # 約每分鐘 138 字（原 0.92 約 154 字）
    for fp in sorted(_g.glob(os.path.join(ROOT, 'src', 'reading', '*.json'))):
        for r in json.load(open(fp, encoding='utf-8')):
            if r.get('status') != 'ok': continue
            paras = [re.sub(r"\[\[([^|\]]+)\|[^\]]+\]\]", r"\1", x) for x in r['paragraphs']]
            paras = [re.sub(r"^--- (.+) ---$", r"\1.", x, flags=re.M) for x in paras]   # 多益雙篇分隔線念成「E-mail 2.」
            PASS[r['id']] = len(paras)
            jobs += [('p', f"{r['id']}_{i}", x, VOICE_SENT, CFG_PASS) for i, x in enumerate(paras)]
# 學測闖關文章逐段朗讀（閱讀測驗原文；綜合測驗／文意選填填入答案後的全文）
if '--gsat' in args or DRY:
    CFG_PASS = {'audioEncoding': 'MP3', 'speakingRate': 0.82, 'sampleRateHertz': 22050}   # 約每分鐘 138 字（原 0.92 約 154 字）
    for fn, kind in (('gsat_rc.json', 'rc'), ('gsat_cz.json', 'cz')):
        fp = os.path.join(ROOT, 'src', 'examples', fn)
        if not os.path.exists(fp): continue
        for c in json.load(open(fp, encoding='utf-8')):
            if c.get('status') != 'ok': continue
            ans = {q['n']: (c['bank'][q['a']] if c.get('kind') == 'fill' else q['o'][q['a']]) for q in c['qs']} if kind == 'cz' else {}
            paras = [re.sub(r"\{\{(\d+)\}\}", lambda m: ans.get(int(m.group(1)), ''), x) for x in c['text']]
            PASS[c['id']] = len(paras)
            jobs += [('p', f"{c['id']}_{i}", x, VOICE_SENT, CFG_PASS) for i, x in enumerate(paras)]
if LIMIT: jobs = jobs[:LIMIT]

chars = sum(len(j[2]) for j in jobs)
print(f'工作 {len(jobs)} 個，約 {chars:,} 字元（Neural2 每月免費額度約 100 萬字元）')
if DRY: sys.exit(0)

keyf = os.path.join(ROOT, '.secrets', 'google_tts_key.txt')
if not os.path.exists(keyf):
    sys.exit('找不到金鑰檔 .secrets/google_tts_key.txt')
KEY = open(keyf, encoding='utf-8').read().strip()
URL = 'https://texttospeech.googleapis.com/v1/text:synthesize?key=' + KEY

done = skipped = failed = 0
for kind, wid, text, voice, cfg in jobs:
    out = os.path.join(ROOT, 'audio', kind, wid + '.mp3')
    if os.path.exists(out) and not FORCE: skipped += 1; continue
    os.makedirs(os.path.dirname(out), exist_ok=True)
    body = json.dumps({'input': {'text': text}, 'voice': voice, 'audioConfig': cfg}).encode('utf-8')
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL, data=body, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                audio = json.load(resp)['audioContent']
            open(out, 'wb').write(base64.b64decode(audio)); done += 1
            if kind == 'p':   # 文章朗讀轉成單聲道 32 kbps，檔案約小一半，語音品質不受影響
                import subprocess, shutil
                if shutil.which('ffmpeg'):
                    tmp = out + '.tmp.mp3'
                    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-ac', '1', '-ar', '22050', '-b:a', '32k', tmp], check=True)
                    os.replace(tmp, out)
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode('utf-8', 'replace')[:300]
            if e.code in (429, 500, 503): time.sleep(2 * (attempt + 1)); continue
            print('失敗', wid, e.code, msg); failed += 1; break
        except Exception as e:
            time.sleep(2); print('重試', wid, e)
    if done and done % 200 == 0: print('已完成', done)

# 網站讀的清單：有哪些 id 已有音檔
idx = {k: sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, 'audio', k))) for k in ('w', 's') if os.path.isdir(os.path.join(ROOT, 'audio', k))}
# 相關字：slug → 文字（網站用文字查錄音）
old = json.load(open(os.path.join(ROOT, 'audio', 'index.json'))).get('f', {}) if os.path.exists(os.path.join(ROOT, 'audio', 'index.json')) else {}
old.update(FORMS)
pd = os.path.join(ROOT, 'audio', 'p')
if os.path.isdir(pd):   # 只列出每一段都錄好的文章：{文章id: 段數}
    have = set(f[:-4] for f in os.listdir(pd))
    allp = dict(json.load(open(os.path.join(ROOT, 'audio', 'index.json'))).get('p', {})) if os.path.exists(os.path.join(ROOT, 'audio', 'index.json')) else {}
    allp.update(PASS)
    idx['p'] = {k: n for k, n in allp.items() if all(f'{k}_{i}' in have for i in range(n))}
fd = os.path.join(ROOT, 'audio', 'f')
if os.path.isdir(fd): idx['f'] = {k: v for k, v in old.items() if os.path.exists(os.path.join(fd, k + '.mp3'))}
json.dump(idx, open(os.path.join(ROOT, 'audio', 'index.json'), 'w'), separators=(',', ':'))
print(f'新產生 {done}、已存在跳過 {skipped}、失敗 {failed}')
