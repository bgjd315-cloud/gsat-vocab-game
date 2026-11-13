# 國中基礎站：國中 2000 字裡網站還沒有的字 → src/raw/jh_words.json
# 依學測（閱讀測驗、綜合測驗、文意選填、詞彙題）出現的年份數排「學測高頻」順序；另有字母順序
# 用法：python -I -X utf8 tools/make_jh.py
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
RAW = os.path.join(ROOT, 'src', 'raw')
def J(p): return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
jj = J('src/raw/jh2000.json')
W = J('src/words.json')
site = set()
for r in W:
    if r[1] == 9: continue   # 國中基礎站本身的字不算「網站已有」
    for part in r[4].lower().split('/'):
        site.add(re.sub(r'[()]', '', part).strip()); site.add(re.sub(r'\([^)]*\)', '', part).strip())
def cands(t):
    c = [t]
    if t.endswith('ies'): c.append(t[:-3] + 'y')
    if t.endswith('es'): c.append(t[:-2])
    if t.endswith('s'): c.append(t[:-1])
    if t.endswith('ied'): c.append(t[:-3] + 'y')
    if t.endswith('ed'): c += [t[:-2], t[:-1]]
    if t.endswith('ing'): c += [t[:-3], t[:-3] + 'e']
    for s in ('ed', 'ing'):
        if t.endswith(s) and len(t) > len(s) + 2 and t[-len(s) - 1] == t[-len(s) - 2]: c.append(t[:-len(s) - 1])
    if t.endswith('er'): c += [t[:-2], t[:-1]]
    if t.endswith('est'): c += [t[:-3], t[:-2]]
    return c
# 學測文本（年份）
texts = []
for c in J('src/examples/gsat_rc.json'): texts.append((c['y'], ' '.join(c['text'])))
for c in J('src/examples/gsat_cz.json'): texts.append((c['y'], ' '.join(c['text'])))
for q in J('src/raw/gsat_vocab_q.json'): texts.append((q['y'], q['s'] + ' ' + ' '.join(q['o'])))
years, count = {}, {}
for y, t in texts:
    toks = re.findall(r"[a-z]+", t.lower())
    seen = set()
    for tok in toks:
        for c in cands(tok): seen.add(c)
        count_key = tok
    for w in seen: years.setdefault(w, set()).add(y)
    for tok in toks:
        for c in set(cands(tok)): count[c] = count.get(c, 0) + 1
# 太基礎、不值得當單字學的：冠詞、be 動詞變化、斷字殘片
SKIP = {'a', 'an', 'the', 'is', 'are', 'am', 'was', 'were', 'been', 's', 'be', 'does', 'done', 'had', 'has',
        'dad', 'daddy', 'mom', 'mommy', 'good-bye', 'bye'}   # 變化形與暱稱併在 have／do／father／mother／goodbye 的說明裡
out = []
for lst in ('jh_basic', 'jh_adv'):
    for w in jj[lst]:
        lw = w.lower().strip()
        if lw in site or lw in SKIP: continue
        key = lw if ' ' not in lw else None
        ys = sorted(years.get(lw, set())) if key else []
        out.append({'word': w, 'list': 'basic' if lst == 'jh_basic' else 'adv', 'years': ys, 'count': count.get(lw, 0) if key else 0})
# 去重（同一字在兩表）
seen = set(); uniq = []
for e in out:
    if e['word'].lower() in seen: continue
    seen.add(e['word'].lower()); uniq.append(e)
uniq.sort(key=lambda e: e['word'].lower())
# 已有編號的字沿用原編號與天數（進度、語音都靠編號），新字接在最後
pj = os.path.join(RAW, 'jh_words.json')
prev = {e['word'].lower(): e for e in json.load(open(pj, encoding='utf-8'))} if os.path.exists(pj) else {}
n = len(prev)
for e in uniq:
    p = prev.get(e['word'].lower())
    if p: e['id'], e['day'], e['word'] = p['id'], p['day'], p['word']
new = [e for e in uniq if 'id' not in e]
for e in new:
    n += 1; e['id'] = f'J-{n:04d}'; e['day'] = (n - 1) // 25 + 1
uniq.sort(key=lambda e: e['id'])
for i, e in enumerate(sorted(uniq, key=lambda e: (-len(e['years']), -e['count'], e['word'].lower()))): e['hday'] = i // 25 + 1
json.dump(uniq, open(os.path.join(RAW, 'jh_words.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('words', len(uniq), 'days', max(e['day'] for e in uniq), 'basic', sum(e['list'] == 'basic' for e in uniq), 'with gsat years', sum(bool(e['years']) for e in uniq))
