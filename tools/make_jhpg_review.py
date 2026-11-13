# 國中常用片語＋國中基礎文法卡審查表 → review/國中片語與基礎文法審查.xlsx
# 用法：python -I -X utf8 tools/make_jhpg_review.py <專案根目錄> [片語校對 applied.json] [文法校對 applied.json]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
ph = json.load(open(f'{G}/src/examples/jh_phr.json', encoding='utf-8'))
base = {e['id']: e for e in json.load(open(f'{G}/src/raw/jh_phrases.json', encoding='utf-8'))}
cards = [c for c in json.load(open(f'{G}/src/examples/grammar.json', encoding='utf-8')) if c['id'].startswith('G0-K')]
HEAD = PatternFill('solid', fgColor='8A6A3E')
def header(ws, cols):
    ws.append(cols)
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = HEAD; c.alignment = Alignment(vertical='center', wrap_text=True)
def finish(ws, widths, wrap_from, dv_col=None):
    if dv_col:
        dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'{dv_col}2:{dv_col}{max(2, ws.max_row)}')
    for col, wd in zip('ABCDEFGHIJKLMNOP', widths): ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column >= wrap_from)
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
wb = Workbook(); ws = wb.active; ws.title = '國中片語'
header(ws, ['id', '天', '片語', '中文', '例句', '例句中譯', '片語在例句中', '用法提醒', '學測出現年數', '審查結果', '修改意見'])
for r in ph:
    b = base[r['id']]
    ws.append([r['id'], b['day'], r['phrase'], r['zh'], r['en'], r['exzh'], ' … '.join(r['targets']), r.get('note', ''), b['gsat_years'], '', ''])
finish(ws, [8, 5, 20, 22, 50, 34, 18, 30, 8, 10, 26], 4, 'J')
w2 = wb.create_sheet('基礎文法卡')
header(w2, ['id', '卡', '句型', '公式', '情境導入', '口訣', '逐條說明與例句', '造句步驟', '易混淆比較', '常見錯誤', '練習題（★＝答案）', '審查結果', '修改意見'])
L = 'ABCD'
for c in cards:
    pts = '\n\n'.join(f"{i+1}. {p['t']}\n" + '\n'.join(f"　• {e['en']}\n　　{e['zh']}" for e in p['ex']) for i, p in enumerate(c['points']))
    qs = '\n\n'.join(f"{i+1}. {q['s']}\n" + '\n'.join(f"　{'★' if k == q['a'] else ' '}({L[k]}) {o}" for k, o in enumerate(q['o'])) + f"\n　解析：{q['ex']}\n　提示：{q['hint']}" for i, q in enumerate(c['qs']))
    w2.append([c['id'], '基礎 ' + str(int(c['l'][1:])), c['title'], c['formula'], c['intro'], c['rhyme'], pts, '\n'.join(c['steps']),
               '\n\n'.join(f"✔ {x['a']}\n↔ {x['b']}\n{x['note']}" for x in c['compare']),
               '\n\n'.join(f"✘ {x['wrong']}\n✔ {x['right']}\n{x['why']}" for x in c['mistakes']), qs, '', ''])
finish(w2, [10, 8, 16, 22, 34, 22, 70, 40, 44, 44, 70, 10, 26], 3, 'L')
if len(sys.argv) > 2:
    w3 = wb.create_sheet('校對已修正'); header(w3, ['類別', 'id', '位置', '原本', '改成', '原因'])
    for kind, f in zip(('片語', '文法卡'), sys.argv[2:4]):
        for a in json.load(open(f, encoding='utf-8')):
            w3.append([kind, a['id'], a.get('field') or a.get('path'), json.dumps(a['old'], ensure_ascii=False) if not isinstance(a['old'], str) else a['old'],
                       json.dumps(a['new'], ensure_ascii=False) if not isinstance(a['new'], str) else a['new'], a['why']])
    for col, wd in zip('ABCDEF', [8, 10, 18, 46, 46, 34]): w3.column_dimensions[col].width = wd
    for row in w3.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column >= 4)
n = wb.create_sheet('說明')
for line in [f'國中常用片語 {len(ph)} 個：先列出國中常見片語，扣掉課本片語與本站已有的，學測文章出現過的 135 個全收，再補 15 個最常用的；放在國中基礎站第 69–74 天，每天 25 個。',
             f'國中基礎文法卡 {len(cards)} 張（基礎 1–10），排在原本 16 張「國中文法銜接」前面，給國中文法還不穩的學生先補基礎。',
             '全部為本站編寫，已各做一輪從嚴校對（見「校對已修正」頁）。空白視同 OK；要改請選「修改」並寫意見，不要的選「刪除」。',
             '審完後片語會錄朗讀語音再上線（文法卡不用錄音）。']:
    n.append([line])
n.column_dimensions['A'].width = 120
out = f'{G}/review/國中片語與基礎文法審查.xlsx'; wb.save(out); print('ok', out, len(ph), len(cards))
