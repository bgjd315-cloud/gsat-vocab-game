# 組出 src/words.json（遊戲用的精簡資料）
# 用法：python -I tools/build_data.py <專案根目錄> [--drafts]
import json, re, sys, os

ROOT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else '.'
RAW = os.path.join(ROOT, 'src', 'raw')
data = json.load(open(os.path.join(RAW, 'vocab-3-6.json'), encoding='utf-8'))
freq = json.load(open(os.path.join(RAW, 'gsat_freq.json'), encoding='utf-8'))
sents = json.load(open(os.path.join(RAW, 'exam_sents.json'), encoding='utf-8'))

def variants(word):
    out = []
    for part in word.split('/'):
        m = re.match(r"^([a-zA-Z'\- ]+)\(([a-z]+)\)([a-z]*)$", part.strip())
        if m:
            out += [(m.group(1) + m.group(3)).lower(), (m.group(1) + m.group(2) + m.group(3)).lower()]
        else:
            out.append(re.sub(r'[()]', '', part).strip().lower())
    return out

def cands(t):
    c = [t]
    if t.endswith('ies'): c.append(t[:-3] + 'y')
    if t.endswith('es'): c.append(t[:-2])
    if t.endswith('s'): c.append(t[:-1])
    if t.endswith('ied'): c.append(t[:-3] + 'y')
    if t.endswith('ed'): c += [t[:-2], t[:-1]]
    if t.endswith('ing'): c += [t[:-3], t[:-3] + 'e']
    for s in ('ed', 'ing'):
        if t.endswith(s) and len(t) > len(s) + 2 and t[-len(s) - 1] == t[-len(s) - 2]:
            c.append(t[:-len(s) - 1])
    if t.endswith('er'): c += [t[:-2], t[:-1]]
    if t.endswith('est'): c += [t[:-3], t[:-2]]
    return c

def find_target(sentence, word):
    vs = set(variants(word))
    for tok in re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)?", sentence):
        if any(c in vs for c in cands(tok.lower())):
            return tok
    return None

# 例句（老師審過的檔案，src/examples/l3.json …）
examples = {}
for lv in '3456':
    p = os.path.join(ROOT, 'src', 'examples', f'l{lv}.json')
    if os.path.exists(p):
        for r in json.load(open(p, encoding='utf-8')):
            if r.get('status') in ('ok', 'draft') and r['target'] in r['en']:
                examples[r['id']] = r

# 只出現在題目指示語（which paragraph / the passage）的字，不算學測頻率
# accord 只以 according to 片語出現，也不算，且不用其學測原句
INSTRUCTION_ONLY = {'passage', 'paragraph', 'accord'}
for lv_arr in data['levels'].values():
    for e in lv_arr:
        if e['word'] in INSTRUCTION_ONLY:
            freq[e['id']] = {'years': [], 'count': 0}

out = []
for lv in ['3', '4', '5', '6']:
    arr = data['levels'][lv]
    # 學測高頻優先的排序：出現年數多→總次數多→原順序
    def key(e):
        f = freq.get(e['id'], {'years': [], 'count': 0})
        return (-len(f['years']), -f['count'], e['index'])
    ranked = sorted(arr, key=key)
    hday = {}
    for i, e in enumerate(ranked):
        hday[e['id']] = min(i // 25 + 1, 40)
    for e in arr:
        f = freq.get(e['id'], {'years': [], 'count': 0})
        ex_exam = None
        for s in ([] if e['word'] in INSTRUCTION_ONLY else sents.get(e['id'], [])):
            t = find_target(s['s'], e['word'])
            if t:
                ex_exam = [s['y'], s['s'], t]
                break
        ex = examples.get(e['id'])
        out.append([
            e['id'], int(lv), e['day'], hday[e['id']], e['word'], e['pos'], e['zh'],
            [int(y) for y in f['years']],
            ex_exam,
            [ex['en'], ex['zh'], ex['target'], 1 if ex.get('status') == 'ok' else 0] if ex else None,
        ])

# ---- 國中學過：三到六級裡屬於國中 2000 字的字，加第 11 欄 1 ----
jhp = os.path.join(RAW, 'jh2000.json')
jhset = set()
if os.path.exists(jhp):
    jj = json.load(open(jhp, encoding='utf-8'))
    jhset = set(jj['jh_basic']) | set(jj['jh_adv'])
for row in out:
    row.append(1 if any(v in jhset for v in variants(row[4])) else 0)

# ---- L0 銜接站（國中→高中）：src/raw/bridge_words.json ＋ src/examples/l0.json（含中文意思） ----
bp = os.path.join(RAW, 'bridge_words.json')
l0p = os.path.join(ROOT, 'src', 'examples', 'l0.json')
if os.path.exists(bp) and os.path.exists(l0p):
    bw = json.load(open(bp, encoding='utf-8'))
    # 正式版只放審過的（ok）；加 --drafts 才連待審一起放（本機預覽用）
    okset = ('ok', 'draft') if '--drafts' in sys.argv else ('ok',)
    l0 = {r['id']: r for r in json.load(open(l0p, encoding='utf-8')) if r.get('status') in okset}
    b_out = []
    for e in bw:
        x = l0.get(e['id'])
        if not x: continue
        ex = [x['en'], x['exzh'], x['target'], 1 if x.get('status') == 'ok' else 0] if x['target'] in x['en'] else None
        b_out.append([e['id'], 0, e['day'], e['day'], e['word'], e['pos'], x['zh'], e['years'], None, ex, 1])
    out = out + b_out   # 一定要接在最後：學生進度用字的位置存檔，插在前面會打亂舊進度
    print('銜接站', len(b_out), '字')

# ---- 課本補充字（課本「要會用的字」裡、網站詞表沒有的字，等級記為 2）：src/raw/tb_extras.json ＋ src/examples/tb.json ----
tp = os.path.join(RAW, 'tb_extras.json')
tep = os.path.join(ROOT, 'src', 'examples', 'tb.json')
if os.path.exists(tp) and os.path.exists(tep):
    okset = ('ok', 'draft') if '--drafts' in sys.argv else ('ok',)
    tx = {r['id']: r for r in json.load(open(tep, encoding='utf-8')) if r.get('status') in okset}
    t_out = []
    for e in json.load(open(tp, encoding='utf-8')):
        x = tx.get(e['id'])
        if not x: continue
        ex = [x['en'], x['exzh'], x['target'], 1 if x.get('status') == 'ok' else 0] if x['target'] in x['en'] else None
        t_out.append([e['id'], 2, 0, 0, x.get('word', e['word']), x.get('pos', e['pos']), x['zh'], [], None, ex, 0])
    out = out + t_out   # 一樣接在最後
    print('課本補充字', len(t_out), '字')

# ---- 片語（課本 Idioms and Phrases，等級記為 1，第 12 欄是朗讀用的說法）：src/raw/tb_phrases.json ＋ src/examples/phr.json ----
pp = os.path.join(RAW, 'tb_phrases.json')
pep = os.path.join(ROOT, 'src', 'examples', 'phr.json')
if os.path.exists(pp) and os.path.exists(pep):
    okset = ('ok', 'draft') if '--drafts' in sys.argv else ('ok',)
    px = {r['id']: r for r in json.load(open(pep, encoding='utf-8')) if r.get('status') in okset}
    p_out = []
    for e in json.load(open(pp, encoding='utf-8')):
        x = px.get(e['id'])
        if not x: continue
        ex = [x['en'], x['exzh'], '|'.join(x['targets']), 1 if x.get('status') == 'ok' else 0]
        p_out.append([e['id'], 1, 0, 0, e['phrase'], 'phr.', x['zh'], [], None, ex, 0, x['say']])
    out = out + p_out   # 一樣接在最後
    print('片語', len(p_out), '個')

# ---- 第七級（進階字彙：wordfreq 詞頻＋實用度選字，大考詞彙表以外）：src/raw/vocab-7.json ＋ src/examples/l7.json，接在最後 ----
p7 = os.path.join(RAW, 'vocab-7.json')
e7 = os.path.join(ROOT, 'src', 'examples', 'l7.json')
if os.path.exists(p7) and os.path.exists(e7):
    okset = ('ok', 'draft') if '--drafts' in sys.argv else ('ok',)
    x7 = {r['id']: r for r in json.load(open(e7, encoding='utf-8')) if r.get('status') in okset}
    gy = {}
    gp = os.path.join(RAW, 'gsat_offlist_years.json')
    if os.path.exists(gp): gy = json.load(open(gp, encoding='utf-8'))
    o7 = []
    for e in json.load(open(p7, encoding='utf-8')):
        x = x7.get(e['id'])
        if not x: continue
        ex = [x['en'], x['exzh'], x['target'], 1 if x.get('status') == 'ok' else 0] if x['target'] in x['en'] else None
        o7.append([e['id'], 7, e['day'], e['hday'], x.get('word', e['word']), x.get('pos', e['pos']), x['zh'], gy.get(e['word'].lower(), []), None, ex, 0])
    out = out + o7   # 一定接在最後，不影響既有進度
    print('第七級', len(o7), '字')

# ---- 多益職場英文主題包（等級 8，TOEIC Service List 1.2 中網站沒有的字）：src/raw/vocab-toeic.json ＋ src/examples/toeic.json，接在最後 ----
pt = os.path.join(RAW, 'vocab-toeic.json')
et = os.path.join(ROOT, 'src', 'examples', 'toeic.json')
if os.path.exists(pt) and os.path.exists(et):
    okset = ('ok', 'draft') if '--drafts' in sys.argv else ('ok',)
    xt = {r['id']: r for r in json.load(open(et, encoding='utf-8')) if r.get('status') in okset}
    o8 = []
    for e in json.load(open(pt, encoding='utf-8')):
        x = xt.get(e['id'])
        if not x: continue
        ex = [x['en'], x['exzh'], x['target'], 1 if x.get('status') == 'ok' else 0] if x['target'] in x['en'] else None
        o8.append([e['id'], 8, e['day'], e['day'], x['word'], x['pos'], x['zh'], [], None, ex, 0])
    out = out + o8   # 一定接在最後
    print('多益主題包', len(o8), '字')

# ---- 國中基礎站（等級 9，國中 2000 字裡網站還沒有的字）：src/raw/jh_words.json ＋ src/examples/jh.json，接在最後 ----
pj = os.path.join(RAW, 'jh_words.json')
ej = os.path.join(ROOT, 'src', 'examples', 'jh.json')
if os.path.exists(pj) and os.path.exists(ej):
    okset = ('ok', 'draft') if '--drafts' in sys.argv else ('ok',)
    xj = {r['id']: r for r in json.load(open(ej, encoding='utf-8')) if r.get('status') in okset}
    o9 = []
    for e in json.load(open(pj, encoding='utf-8')):
        x = xj.get(e['id'])
        if not x: continue
        ex = [x['en'], x['exzh'], x['target'], 1 if x.get('status') == 'ok' else 0] if x['target'] in x['en'] else None
        o9.append([e['id'], 9, e['day'], e['hday'], x.get('word', e['word']), x['pos'], x['zh'], e['years'], None, ex, 0])
    # 國中常用片語：src/raw/jh_phrases.json（JP-xxx，接在國中字之後的天數）；例句放在 src/examples/jh_phr.json
    pp = os.path.join(RAW, 'jh_phrases.json')
    ep = os.path.join(ROOT, 'src', 'examples', 'jh_phr.json')
    if os.path.exists(pp) and os.path.exists(ep):
        xp = {r['id']: r for r in json.load(open(ep, encoding='utf-8')) if r.get('status') in okset}
        for e in json.load(open(pp, encoding='utf-8')):
            x = xp.get(e['id'])
            if not x: continue
            ex = [x['en'], x['exzh'], '|'.join(x['targets']), 1 if x.get('status') == 'ok' else 0]
            o9.append([e['id'], 9, e['day'], e['hday'], e['phrase'], 'phr.', x['zh'], [], None, ex, 0, x['say']])
    out = out + o9   # 一定接在最後
    print('國中基礎站', len(o9), '字')

json.dump(out, open(os.path.join(ROOT, 'src', 'words.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
n_exam = sum(1 for r in out if r[8]); n_ex = sum(1 for r in out if r[9])
print(f'words={len(out)} 真題句={n_exam} 編寫例句={n_ex}')
