# 產生歷屆學測詞彙題中譯解析審查表 review/學測詞彙題解析審查.xlsx
# 用法：python -I -X utf8 tools/make_gq_review.py <專案根目錄> [--all]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
qs = {(q['y'], q['n']): q for q in json.load(open(f'{G}/src/raw/gsat_vocab_q.json', encoding='utf-8'))}
ex = json.load(open(f'{G}/src/examples/gsat_q.json', encoding='utf-8'))
if '--all' not in sys.argv: ex = [r for r in ex if r.get('status') != 'ok']   # 預設只列待審的
wb = Workbook(); ws = wb.active; ws.title = '學測詞彙題'
ws.append(['學年度', '題號', '題目', '(A)', '(B)', '(C)', '(D)', '答案', '中譯', '提示', '詳細解析', '選項分析', '常見搭配／詞性變化／策略', '審查結果', '修改意見'])
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='8274DC')
    c.alignment = Alignment(vertical='center', wrap_text=True)
for r in ex:
    q = qs[(r['y'], r['n'])]
    ws.append([r['y'], r['n'], q['s'], *q['o'], 'ABCD'[q['a']], r['zh'], r.get('hint', ''), r['ex'],
               '\n'.join(r['why']) if r.get('why') else '\n'.join(f'({"ABCD"[i]}) {q["o"][i]}：{z}' for i, z in enumerate(r['oz'])),
               '\n'.join(x for x in (r.get('col', ''), r.get('fam', ''), r.get('strat', '')) if x), '', ''])
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'N2:N{ws.max_row}')
for col, wd in zip('ABCDEFGHIJKLMNO', [7, 5, 46, 12, 12, 12, 12, 6, 36, 30, 44, 46, 40, 10, 26]):
    ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in (3, 9, 10, 11, 12, 13, 15))
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in ['題目、選項與答案是大考中心歷屆學測英文詞彙題原題與公布答案。',
             '中譯、提示、詳細解析、選項分析、常見搭配／詞性變化／策略是本站編寫，請審這幾欄；空白視同 OK。',
             '學生答完每題會看到中譯、四個選項的意思與解析，選項是網站單字時可以點開字卡。']:
    n.append([line])
n.column_dimensions['A'].width = 100
out = f'{G}/review/學測詞彙題解析審查.xlsx'; wb.save(out); print('ok', out, ws.max_row - 1)
