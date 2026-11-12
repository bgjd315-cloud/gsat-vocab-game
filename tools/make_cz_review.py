# 產生學測闖關（綜合測驗、文意選填）中譯解析審查表 review/學測闖關審查.xlsx
# 用法：python -I -X utf8 tools/make_cz_review.py <專案根目錄> [--all]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
cs = json.load(open(f'{G}/src/examples/gsat_cz.json', encoding='utf-8'))
if '--all' not in sys.argv: cs = [c for c in cs if c.get('status') != 'ok']
wb = Workbook()
def head(ws, cols, color):
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor=color)
        c.alignment = Alignment(vertical='center', wrap_text=True)
a = wb.active; a.title = '文章'
head(a, ['id', '學年度', '題型', '題號', '標題', '原文（大考中心，不需審）', '中譯', '審查結果', '修改意見'], '4C94D6')
for c in cs:
    a.append([c['id'], c['y'], '文意選填' if c['kind'] == 'fill' else '綜合測驗', f"{c['first']}–{c['first'] + len(c['qs']) - 1}",
              c.get('title', ''), '\n\n'.join(c['text']), '\n\n'.join(c['zh']), '', ''])
q = wb.create_sheet('解析')
head(q, ['id', '題號', '選項／字庫', '答案', '解析', '審查結果', '修改意見'], '8274DC')
for c in cs:
    for x in c['qs']:
        if c['kind'] == 'fill':
            opts = '　'.join(f"({'ABCDEFGHIJ'[i]}) {w}" for i, w in enumerate(c['bank'])); ans = f"({'ABCDEFGHIJ'[x['a']]}) {c['bank'][x['a']]}"
        else:
            opts = '\n'.join(f"({'ABCD'[i]}) {o}" for i, o in enumerate(x['o'])); ans = f"({'ABCD'[x['a']]}) {x['o'][x['a']]}"
        q.append([c['id'], x['n'], opts, ans, x['ex'], '', ''])
for ws, cols, widths, wrap, vcol in ((a, 'ABCDEFGHI', [9, 7, 9, 8, 18, 70, 50, 10, 26], (5, 6, 7, 9), 'H'),
                                     (q, 'ABCDEFG', [9, 6, 40, 20, 56, 10, 26], (3, 4, 5, 7), 'F')):
    dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'{vcol}2:{vcol}{max(2, ws.max_row)}')
    for col, wd in zip(cols, widths): ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for cell in row: cell.alignment = Alignment(vertical='top', wrap_text=cell.column in wrap)
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in ['學測闖關：97–115 學年度學測英文「綜合測驗」與「文意選填」，一篇一關。',
             '原文、選項與答案是大考中心原題與公布答案（已逐句和原卷核對、答案和官方答案逐題核對），不需審。',
             '請審本站寫的「中譯」「標題」與每題「解析」；空白視同 OK。']:
    n.append([line])
n.column_dimensions['A'].width = 100
out = f'{G}/review/學測闖關審查.xlsx'; wb.save(out); print('ok', out, len(cs), '篇', q.max_row - 1, '題')
