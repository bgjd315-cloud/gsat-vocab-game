# 產生構詞卡審查表 review/構詞卡審查.xlsx
# 用法：python -I -X utf8 tools/make_morph_review.py <專案根目錄> [--all]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
cs = json.load(open(f'{G}/src/examples/morph.json', encoding='utf-8'))
if '--all' not in sys.argv: cs = [c for c in cs if c.get('status') != 'ok']
wb = Workbook(); ws = wb.active; ws.title = '構詞卡'
ws.append(['id', '類別', '標題', '公式', '說明', '口訣', '字族拆解', '逐條說明與例句', '拆解步驟', '易混淆比較', '陷阱與常見錯誤', '練習題（含答案、提示、解析）', '審查結果', '修改意見'])
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='8274DC')
    c.alignment = Alignment(vertical='center', wrap_text=True)
for c in cs:
    fam = '\n'.join(f"{f['w']} ＝ {f['parts']}　{f['zh']}" for f in c['family'])
    pts = '\n\n'.join(f"{i+1}. {p['t']}\n" + '\n'.join(f"　• {e['en']}\n　　{e['zh']}" for e in p['ex']) for i, p in enumerate(c['points']))
    qs = '\n\n'.join(f"{i+1}. {q['s']}\n" + '／'.join(f"({'ABCD'[j]}) {o}" for j, o in enumerate(q['o'])) +
                     f"\n答案 ({'ABCD'[q['a']]})　提示：{q['hint']}\n解析：{q['ex']}" for i, q in enumerate(c['qs']))
    ws.append([c['id'], c['group'], c['title'], c['formula'], c['intro'], c['rhyme'], fam, pts, '\n'.join(c['steps']),
               '\n\n'.join(f"{x['a']}\n↔ {x['b']}\n{x['note']}" for x in c['compare']),
               '\n\n'.join(f"✘ {x['wrong']}\n✔ {x['right']}\n{x['why']}" for x in c['mistakes']), qs, '', ''])
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'M2:M{max(2, ws.max_row)}')
for col, wd in zip('ABCDEFGHIJKLMN', [10, 8, 18, 26, 36, 22, 40, 64, 36, 40, 44, 70, 10, 26]):
    ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for cell in row: cell.alignment = Alignment(vertical='top', wrap_text=cell.column >= 3)
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in ['構詞卡 55 張：字首 17、字尾 19、複合字 3、高頻字根 14、策略 2。每張有說明與口訣、字族拆解、逐條說明與例句、拆解步驟、易混淆比較、陷阱與常見錯誤，以及 6 題練習（附提示與解析）。',
             '已另請兩輪檢查：盲測 330 題（修 4 題）、構詞與字源校對（修 23 處，例如 colleague、suspect 的錯誤拆法）。',
             '全部為本站編寫；空白視同 OK。']:
    n.append([line])
n.column_dimensions['A'].width = 110
out = f'{G}/review/構詞卡審查.xlsx'; wb.save(out); print('ok', out, len(cs))
