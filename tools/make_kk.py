# 產生全站 KK 音標：src/raw/kk.json {單字 id: "KK"}
# 來源：CMU Pronouncing Dictionary（cmudict.dict，BSD 授權，美式發音，ARPAbet 標記）轉成台灣通用的 KK 音標；
# 字典沒收、或需要更正的字寫在 src/raw/kk_manual.json {"小寫單字": "KK（不含括號）"}。
# 用法：python -I -X utf8 tools/make_kk.py <專案根目錄> <cmudict.dict 路徑>
import json, re, sys, os, collections
G, CMU = sys.argv[1], sys.argv[2]
V = {'AA': 'ɑ', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔ', 'AW': 'aʊ', 'AY': 'aɪ', 'EH': 'ɛ', 'ER': 'ɝ', 'EY': 'e', 'IH': 'ɪ', 'IY': 'i', 'OW': 'o', 'OY': 'ɔɪ', 'UH': 'ʊ', 'UW': 'u'}
C = {'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð', 'F': 'f', 'G': 'g', 'HH': 'h', 'JH': 'dʒ', 'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'ʃ', 'T': 't', 'TH': 'θ', 'V': 'v', 'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'}
# 英語可以出現在音節開頭的子音組合（決定重音符號放哪裡）
ON = set(x.split('+') and tuple(x.split('+')) for x in
         'P+L B+L K+L G+L F+L S+L P+R B+R T+R D+R K+R G+R F+R TH+R SH+R S+W T+W D+W K+W G+W TH+W '
         'S+P S+T S+K S+M S+N S+P+L S+P+R S+T+R S+K+R S+K+W S+K+L '
         'P+Y B+Y K+Y G+Y M+Y F+Y V+Y HH+Y S+P+Y S+K+Y'.split())
PRI, SEC = 'ˋ', '͵'
def load_cmu():
    d = collections.defaultdict(list)
    for line in open(CMU, encoding='utf-8'):
        line = line.split('#')[0].strip()
        if not line: continue
        w, *ph = line.split()
        d[re.sub(r'\(\d+\)$', '', w)].append(ph)
    return d
BASIC = None
def real(w):
    global BASIC
    if BASIC is None:
        BASIC = set(json.load(open(os.path.join(G, 'src', 'raw', 'l12.json'), encoding='utf-8')))
        for r in json.load(open(os.path.join(G, 'src', 'words.json'), encoding='utf-8')):
            for x in re.split(r'[/ ]', re.sub(r'\(.*?\)', '', r[4])): BASIC.add(x.lower())
        BASIC = {x.lower() for x in BASIC} | {'up', 'un', 'in'}
    if w in BASIC: return True
    if w.endswith('s') and len(w) > 4 and w[:-1] in BASIC: return True
    if w.endswith('ing') and len(w) > 5 and (w[:-3] in BASIC or w[:-3] + 'e' in BASIC): return True
    return False
ND = lambda seq: [re.sub(r'\d', '', x) for x in seq]
def boundary(ph, spell):
    """複合字（lightweight、homeowner、uprising、thereafter）：找出兩個字的分界，重音符號放在分界上"""
    if not spell.isalpha(): return None
    for k in range(2, len(spell) - 2):
        w1, w2 = spell[:k], spell[k:]
        if not (len(w1) >= 3 or w1 in ('up', 'un', 'in')) or w1 not in CMUD or w2 not in CMUD: continue
        if not (real(w1) and real(w2)): continue   # 兩半都要是字表裡的真字（避免 engine＋ering）
        for p1 in CMUD[w1]:
            if ND(ph[:len(p1)]) == ND(p1) and any(ND(ph[len(p1):]) == ND(p2) for p2 in CMUD[w2]): return len(p1)
    return None
def kk(ph, spell='', pos=''):
    ph = list(ph); B = boundary(ph, spell)
    ones = [i for i, p in enumerate(ph) if p.endswith('1')]
    if len(ones) > 1:   # 兩個主重音（engineering、lightweight）：複合名詞／形容詞留第一個，其他留最後一個
        keep = ones[0] if B is not None and sum(p[-1].isdigit() for p in ph[B:]) <= 2 and re.search(r'(^|/)(n|adj)\.', pos) and 'v.' not in pos else ones[-1]
        ph = [p[:-1] + '2' if p.endswith('1') and i != keep else p for i, p in enumerate(ph)]
    vv = [i for i, p in enumerate(ph) if p[-1].isdigit()]
    if len(vv) > 2 and ph[vv[-1]] == 'IY2': ph[vv[-1]] = 'IY0'
    ph = ['ER0' if p == 'ER2' and i + 1 < len(ph) and ph[i + 1][-1].isdigit() else p for i, p in enumerate(ph)]   # liberation：er 後接母音 → ə＋r
    if re.search(r'ates?$', spell) and re.fullmatch(r'v\.', pos.strip()):   # 動詞 -ate 念 [et]：illuminate [ɪˋlumə͵net]
        vv2 = [i for i, p in enumerate(ph) if p[-1].isdigit()]
        if len(vv2) > 2 and ph[vv2[-1]] in ('AH0', 'IH0'): ph[vv2[-1]] = 'EY2'
    ph = ['IY0' if p == 'IY2' and i + 1 < len(ph) and ph[i + 1] == 'AH0' else p for i, p in enumerate(ph)]   # librarian [laɪˋbrɛrɪən]   # 字尾 -ty、-ly 不標次重音：liberty、instinctively
    ph2, nb = [], B   # 非重讀的 ER 後面接母音時，KK 寫成 ə＋r（r 歸下一音節），如 interesting、itinerary
    for i, p in enumerate(ph):
        if p == 'ER0' and i + 1 < len(ph) and ph[i + 1][-1].isdigit() and i + 1 != B:
            ph2 += ['AH0', 'R']
            if B is not None and i < B: nb += 1
        elif p == 'AH0' and i + 2 < len(ph) and ph[i + 1] == 'W' and ph[i + 2][-1].isdigit() and 'u' in spell:   # actual、graduate：KK 寫 ʊ
            ph2.append('UH0'); ph[i + 1] = 'SKIPW'
            if B is not None and i + 1 < B: nb -= 1
        elif p == 'SKIPW': continue
        else: ph2.append(p)
    ph = ph2; B = nb
    vi = [i for i, p in enumerate(ph) if p[-1].isdigit()]
    out = []
    for i, p in enumerate(ph):
        if p[-1].isdigit():
            b, s = p[:-1], p[-1]
            if b == 'AH' and s == '0':
                nxt = ph[i + 1] if i + 1 < len(ph) else None
                after = ph[i + 2] if i + 2 < len(ph) else None
                prev = ph[i - 1] if i else None
                end_ok = after is None or not after[-1].isdigit()
                if nxt == 'L' and prev in C and end_ok and prev not in ('L', 'R'): out.append('ḷ'); continue
                if nxt == 'N' and prev in ('T', 'D', 'S', 'Z') and end_ok: out.append('ṇ'); continue
                t = 'ə'
                if i == vi[0] and i <= 2 and re.match(r'(re|de|be|pre|e)[^aeiou]', spell): t = 'ɪ'
                if i == 0 and re.match(r'u[np]', spell): t = 'ʌ'   # un-、up- 字首 KK 寫 ʌ：unload、update
                # 字尾 -id、-ness、-less、-et、-ice、-ace、-ate（非動詞）KK 習慣寫 ɪ：vivid、market、practice、private
                if i == vi[-1] and len(vi) > 1 and (re.search(r'(id|ness|less|et|ice|ace)s?$', spell) or (re.search(r'ates?$', spell) and pos and 'v.' not in pos)): t = 'ɪ'
            elif b == 'ER': t = 'ɝ' if s != '0' else 'ɚ'
            elif b == 'IY' and s == '0': t = 'ɪ'
            else: t = V[b]
            out.append(t)
        else:
            if out and out[-1] in ('ḷ', 'ṇ') and p in ('L', 'N'): continue
            out.append(C[p])
    # 被 ḷ/ṇ 吃掉的 L、N 已略過；以下放重音符號
    if len(vi) < 2: return ''.join(out)
    marks = {}
    for k, i in enumerate(vi):
        s = ph[i][-1]
        if s not in '12': continue
        if k == 0: at = 0
        else:
            j = vi[k - 1] + 1; cl = ph[j:i]; best = len(cl)  # noqa
            for n in range(len(cl), 0, -1):
                t = tuple(cl[len(cl) - n:])
                if n == 1 and t[0] != 'NG' or t in ON: best = len(cl) - n; break
            at = j + best
            if B is not None and vi[k - 1] < B <= i: at = B   # 複合字照字的分界
        if s == '2' and len(vi) == 2: continue
        if s == '2' and k + 1 < len(vi) and ph[vi[k + 1]].endswith('1'): continue   # 緊接主重音前的音節不標次重音：imaginary、invariably
        if s == '2' and ph[i] == 'IY2' and k + 1 < len(vi) and ph[vi[k + 1]] == 'AH0': continue   # librarian、vegetarian   # 兩音節字不標次重音（KK 字典習慣：protest [ˋprotɛst]）
        marks[at] = PRI if s == '1' else SEC
    # out 與 ph 一一對應（除了被吃掉的子音），重新對位
    res, oi = [], 0
    for i, p in enumerate(ph):
        if i in marks: res.append(marks[i])
        if p in ('L', 'N') and i > 0 and ph[i - 1] == 'AH0' and res and res[-1] in ('ḷ', 'ṇ'): continue
        res.append(out[oi]); oi += 1
    return ''.join(res)
def first_stress(ph):
    v = [p for p in ph if p[-1].isdigit()]
    return next((k for k, p in enumerate(v) if p[-1] == '1'), 0)
def say_text(r):
    if len(r) > 11 and r[11]: return r[11]
    p = r[4].split('/')[0].strip()
    m = re.match(r"^([a-zA-Z'\- ]+)\(([a-z]+)\)([a-z]*)$", p)
    return (m.group(1) + m.group(3)) if m else re.sub(r'[()]', '', p)
CMUD = load_cmu()
MAN = {}
mp = os.path.join(G, 'src', 'raw', 'kk_manual.json')
if os.path.exists(mp): MAN = {k.lower(): v for k, v in json.load(open(mp, encoding='utf-8')).items()}
def norm(w): return w.lower().replace('’', "'").replace('é', 'e').replace('è', 'e').strip()
def one(word, pos=''):
    """單一個字（可含連字號）→ KK；回傳 (kk, 是否找到)"""
    lw = norm(word)
    if word.lower() in MAN: return MAN[word.lower()], True
    if lw in MAN: return MAN[lw], True
    if '-' in lw and lw not in CMUD:
        parts = [one(x) for x in lw.split('-') if x]
        return '-'.join(p[0] for p in parts), all(p[1] for p in parts)
    vs = CMUD.get(lw)
    if not vs: return word, False
    if len(vs) > 1:
        m = re.search(r'\b(n|adj)\.', pos)
        if lw.endswith('ate') and 'v.' in pos and m:   # separate、estimate：形容詞／名詞念 -ət，動詞念 -et
            nv = [v for v in vs if v[-2] in ('AH0', 'IH0')]; vv = [v for v in vs if v[-2].startswith('EY')]
            if nv and vv: return f'{kk(nv[0], lw, m.group(0))}] {m.group(0)}／[{kk(vv[0], lw, "v.")}] v.', True
        fs = sorted(set(first_stress(v) for v in vs))
        isv = 'v.' in pos; isn = bool(re.search(r'\b(n|adj)\.', pos))
        if len(fs) > 1 and (isv or isn):
            early = min(vs, key=first_stress); late = max(vs, key=first_stress)
            if isv and isn: return f'{kk(early, lw, "n.")}] n.／[{kk(late, lw, "v.")}] v.', True   # 名詞重音在前、動詞在後
            return kk(late if isv else early, lw, pos), True
    return kk(vs[0], lw, pos), True
W = json.load(open(os.path.join(G, 'src', 'words.json'), encoding='utf-8'))
out, miss = {}, collections.Counter()
for r in W:
    text = say_text(r)
    if r[1] == 1: text = re.sub(r'\.\.\.|…', ' ', r[4])  # 片語：照顯示的字逐字標
    if text.lower() in MAN: s = '[' + MAN[text.lower()] + ']'; out[r[0]] = s[:-1] if re.search(r'\] \S+\.\]$', s) else s; continue
    toks = re.findall(r"[A-Za-zÀ-ÿ'’\-]+|\(|\)", text)
    pieces, ok = [], True
    for t in toks:
        if t in '()': pieces.append(t); continue
        k, f = one(t, re.sub(r'\(.*?\)', '', r[5]) if len(toks) == 1 else '')
        if not f: ok = False; miss[t.lower()] += 1
        pieces.append(k)
    if ok:
        s = '[' + re.sub(r'\( ', '(', re.sub(r' \)', ')', ' '.join(pieces))) + ']'
        out[r[0]] = s[:-1] if re.search(r'\] \S+\.\]$', s) else s   # 名詞／動詞兩讀：[..] n.／[..] v.
json.dump(out, open(os.path.join(G, 'src', 'raw', 'kk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(sorted(miss), open(os.path.join(G, 'src', 'raw', 'kk_missing.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('有音標', len(out), '/', len(W), '；字典沒收的字', len(miss))
