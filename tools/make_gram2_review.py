# 產生擴充版文法卡審查表 review/文法卡擴充審查.xlsx
# 用法：python -I -X utf8 tools/make_gram2_review.py <專案根目錄> [--all]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
cs = json.load(open(f'{G}/src/examples/grammar_v2.json', encoding='utf-8'))
if '--all' not in sys.argv: cs = [c for c in cs if c.get('status') != 'ok']
where = lambda c: f"國中銜接 {int(c['l'][1:])}" if c['b'] == 0 else f"第{c['b']}冊 {c['l']}"
wb = Workbook(); ws = wb.active; ws.title = '文法卡擴充'
ws.append(['id', '出處', '句型', '公式', '情境導入', '口訣', '逐條說明與例句', '造句步驟', '易混淆比較', '常見錯誤', '練習題提示', '審查結果', '修改意見'])
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='E0913A')
    c.alignment = Alignment(vertical='center', wrap_text=True)
for c in cs:
    pts = '\n\n'.join(f"{i+1}. {p['t']}\n" + '\n'.join(f"　• {e['en']}\n　　{e['zh']}" for e in p['ex']) for i, p in enumerate(c['points']))
    ws.append([c['id'], where(c), c['title'], c['formula'], c['intro'], c['rhyme'], pts,
               '\n'.join(c['steps']), '\n\n'.join(f"✔ {x['a']}\n↔ {x['b']}\n{x['note']}" for x in c['compare']),
               '\n\n'.join(f"✘ {x['wrong']}\n✔ {x['right']}\n{x['why']}" for x in c['mistakes']),
               '\n'.join(f"{i+1}. {q['hint']}" for i, q in enumerate(c['qs'])), '', ''])
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'L2:L{max(2, ws.max_row)}')
for col, wd in zip('ABCDEFGHIJKLM', [11, 11, 14, 20, 34, 22, 70, 40, 46, 46, 40, 10, 26]):
    ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for cell in row: cell.alignment = Alignment(vertical='top', wrap_text=cell.column >= 3)
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in ['文法卡擴充版：每張卡加上 ① 什麼時候用（情境導入＋口訣）② 逐條說明，每一點都有自己的例句 ③ 造句步驟 ④ 易混淆比較 ⑤ 常見錯誤（錯→對＋原因），練習題每題加「給我提示」。',
             '原本的 6 題練習與解析不變（已上線審過）；例句與錯誤句已另外請文法校對過一輪。',
             '全部為本站編寫；空白視同 OK。審完前網站上仍是原本的卡片。']:
    n.append([line])
n.column_dimensions['A'].width = 110
out = f'{G}/review/文法卡擴充審查.xlsx'; wb.save(out); print('ok', out, len(cs))
