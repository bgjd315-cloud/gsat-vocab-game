# 產生文法卡審查表 review/文法卡審查.xlsx（「卡片」與「練習題」兩張工作表）
# 用法：python -I -X utf8 tools/make_gram_review.py <專案根目錄> [--all]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
cs = json.load(open(f'{G}/src/examples/grammar.json', encoding='utf-8'))
if '--all' not in sys.argv: cs = [c for c in cs if c.get('status') != 'ok']
where = lambda c: f"國中銜接 {int(c['l'][1:])}" if c['b'] == 0 else f"第{c['b']}冊 {c['l']}"
wb = Workbook()
def head(ws, cols, color):
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor=color)
        c.alignment = Alignment(vertical='center', wrap_text=True)
a = wb.active; a.title = '卡片'
head(a, ['id', '出處', '句型名稱', '公式', '說明', '例句', '易錯提醒', '審查結果', '修改意見'], 'E0913A')
for c in cs:
    a.append([c['id'], where(c), c['title'], c['formula'], '\n'.join(f'{i+1}. {p}' for i, p in enumerate(c['points'])),
              '\n'.join(f"{e['en']}\n　{e['zh']}" for e in c['examples']), c['tip'], '', ''])
q = wb.create_sheet('練習題')
head(q, ['id', '題號', '句型名稱', '題型', '題目', '(A)', '(B)', '(C)', '(D)', '答案', '解析', '審查結果', '修改意見'], '4C94D6')
for c in cs:
    for i, x in enumerate(c['qs']):
        q.append([c['id'], i + 1, c['title'], '選出正確形式' if x['type'] == 'mc' else '選出正確句子', x['s'], *x['o'], 'ABCD'[x['a']], x['ex'], '', ''])
for ws, cols, widths, wrap, vcol in ((a, 'ABCDEFGHI', [11, 12, 16, 22, 46, 50, 34, 10, 26], (5, 6, 7, 9), 'H'),
                                     (q, 'ABCDEFGHIJKLM', [11, 5, 14, 10, 42, 22, 22, 22, 22, 6, 42, 10, 26], (5, 6, 7, 8, 9, 11, 13), 'L')):
    dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'{vcol}2:{vcol}{max(2, ws.max_row)}')
    for col, wd in zip(cols, widths): ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for cell in row: cell.alignment = Alignment(vertical='top', wrap_text=cell.column in wrap)
    ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in ['課本文法卡：國中文法銜接站＋第 1–5 冊各課句型。每張卡有說明、3 個例句、易錯提醒，以及 6 題練習（4 題選出正確形式、2 題選出正確句子），答完有解析。',
             '各課句型主題依課本決定；說明、例句、練習題與解析全部是本站自己寫的，沒有抄課本。',
             '「卡片」和「練習題」兩張表各自選 OK／修改／刪除，修改的寫在「修改意見」；空白視同 OK。']:
    n.append([line])
n.column_dimensions['A'].width = 110
out = f'{G}/review/文法卡審查.xlsx'; wb.save(out); print('ok', out, len(cs), '張卡', q.max_row - 1, '題')
