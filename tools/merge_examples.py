# 合併子任務寫好的例句 → src/examples/l<級>.json，並做用字難度檢查
# 用法：python -I tools/merge_examples.py <專案根目錄> <級別> <l?_out_0*.json 所在資料夾>
import json, sys, os, re, glob, collections

G, LV, SRC = sys.argv[1], sys.argv[2], sys.argv[3]
rows = []
for f in sorted(glob.glob(os.path.join(SRC, f'l{LV}_out_0*.json'))):
    rows += json.load(open(f, encoding='utf-8'))
data = json.load(open(os.path.join(G, 'src/raw/vocab-3-6.json'), encoding='utf-8'))
ids = [e['id'] for e in data['levels'][LV]]
assert [r['id'] for r in rows] == ids, 'id 順序或數量不符'

def forms_of(word):
    out = set()
    for p in word.split('/'):
        m = re.match(r"^([a-zA-Z'\- ]+)\(([a-z]+)\)([a-z]*)$", p.strip())
        out |= {(m.group(1) + m.group(3)).lower(), (m.group(1) + m.group(2) + m.group(3)).lower()} if m else {re.sub(r'[()]', '', p).strip().lower()}
    return out

l12 = set(json.load(open(os.path.join(G, 'src/raw/l12.json'))))
lower = set(l12)               # 比目標級別低的字（含 1–2 級）
for lv in range(3, int(LV)):
    for e in data['levels'][str(lv)]:
        lower |= forms_of(e['word'])
same = set()
for e in data['levels'][LV]:
    same |= forms_of(e['word'])
FUNC = set("""i me my mine you your yours he him his she her hers it its we us our ours they them their theirs myself yourself himself herself itself ourselves themselves
is am are was were been being has had does did done going went gone got gotten made said saw seen took taken came gave given knew known thought told found left felt kept
brought bought began begun ran sat stood wrote written ate eaten drank fell fallen grew grown heard held lost meant met paid put read sent set shut slept spent spoke spoken
swam threw thrown understood won wore worn broke broken chose chosen drove driven flew flown forgot forgotten hid hidden hung led lent lit rode risen rose sang sung sank
shook shot showed shown sold stuck struck taught tore torn woke woken caught fought built blew became stole cannot anymore everyone someone anyone
one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen twenty thirty forty fifty hundred would could should might
mom dad grandma grandpa children men women people feet teeth mice birthday o'clock""".split())

def ok(t, allowed):
    c = [t]
    for suf, rep in (('ies', 'y'), ('es', ''), ('s', ''), ('ied', 'y'), ('ed', ''), ('ed', 'e'), ('d', ''), ('ing', ''), ('ing', 'e'),
                     ('er', ''), ('er', 'e'), ('est', ''), ('est', 'e'), ('ly', ''), ('ily', 'y'), ('ier', 'y'), ('iest', 'y'), ('ness', ''), ('ful', '')):
        if t.endswith(suf): c.append(t[:-len(suf)] + rep)
    if len(t) > 5 and t.endswith('ing') and t[-4] == t[-5]: c.append(t[:-4])
    if len(t) > 4 and t.endswith('ed') and t[-3] == t[-4]: c.append(t[:-3])
    if len(t) > 4 and (t.endswith('er') or t.endswith('est')) and t[-3 if t.endswith('er') else -4] == t[-4 if t.endswith('er') else -5]:
        c.append(t[:-3] if t.endswith('er') else t[:-4])
    return any(x in allowed for x in c)

out = []; nflag = 0; cnt = collections.Counter()
for r in rows:
    raw = re.findall(r"[A-Za-z']+", r['en'].replace(r['target'], ' '))
    above, samelv = [], []
    for k, t in enumerate(raw):
        t = re.sub(r"^can't$", 'can', t, flags=re.I)
        t = re.sub(r"^won't$", 'will', t, flags=re.I)
        t = re.sub(r"'s$|s'$|'ll$|n't$|'re$|'ve$|'d$|'m$", '', t)
        if len(t) < 2: continue
        if t[:1].isupper() and not ok(t.lower(), lower | same) and t.lower() not in FUNC: continue  # 人名地名
        tl = t.lower()
        if tl in FUNC or ok(tl, lower): continue
        (samelv if ok(tl, same) else above).append(tl)
    note = ''
    if above: note = f'超出1–{int(LV)-1}級：' + ', '.join(above); nflag += 1; cnt.update(above)
    elif samelv: note = f'含其他{LV}級字：' + ', '.join(samelv)
    out.append({**r, 'status': 'draft', 'note': note})
json.dump(out, open(os.path.join(G, f'src/examples/l{LV}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('rows', len(out), 'flag', nflag)
print(cnt.most_common(30))
