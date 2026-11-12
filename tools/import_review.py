# 把老師審完的 review/第?級例句審查.xlsx 匯回 src/examples/l?.json
# OK → status ok；修改 → 換成修改後英文／中譯，status ok；刪除 → 拿掉例句；空白 → 維持 draft
# 用法：python -I tools/import_review.py <專案根目錄> <級別> [xlsx 路徑]
import json, sys, re, os
from openpyxl import load_workbook

G, LV = sys.argv[1], sys.argv[2]
ZH = {'3': '三', '4': '四', '5': '五', '6': '六'}[LV]
xlsx = sys.argv[3] if len(sys.argv) > 3 else f'{G}/review/第{ZH}級例句審查.xlsx'
jpath = f'{G}/src/examples/l{LV}.json'
ex = {r['id']: r for r in json.load(open(jpath, encoding='utf-8'))}
words = {r[0]: r for r in json.load(open(f'{G}/src/words.json', encoding='utf-8'))}

def variants(word):
    out = []
    for p in word.split('/'):
        m = re.match(r"^([a-zA-Z'\- ]+)\(([a-z]+)\)([a-z]*)$", p.strip())
        out += [(m.group(1) + m.group(3)).lower(), (m.group(1) + m.group(2) + m.group(3)).lower()] if m else [re.sub(r'[()]', '', p).strip().lower()]
    return out

def guess_target(en, word, old):
    if old and old in en: return old
    vs = variants(word)
    for tok in re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)?", en):
        t = tok.lower()
        if any(t == v or t.startswith(v[:max(3, len(v) - 2)]) for v in vs): return tok
    return None

ws = load_workbook(xlsx).active
hdr = [c.value for c in ws[1]]
col = {h: i for i, h in enumerate(hdr)}
stat = {'OK': 0, '修改': 0, '刪除': 0, '未審': 0}; problems = []
for row in ws.iter_rows(min_row=2, values_only=True):
    rid = row[col['id']]
    if rid not in ex: continue
    r = ex[rid]; res = (row[col['審查結果']] or '').strip()
    if res == 'OK':
        r['status'] = 'ok'; stat['OK'] += 1
    elif res == '修改':
        en = (row[col['修改後英文']] or '').strip() or r['en']
        zh = (row[col['修改後中譯']] or '').strip() or r['zh']
        t = guess_target(en, words[rid][4], r['target'])
        if not t:
            problems.append(f'{rid} 找不到挖空字，保留原句待確認'); continue
        r.update(en=en, zh=zh, target=t, status='ok'); stat['修改'] += 1
    elif res == '刪除':
        r['status'] = 'deleted'; stat['刪除'] += 1
    else:
        stat['未審'] += 1
json.dump(list(ex.values()), open(jpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(stat)
for p in problems: print('！', p)
