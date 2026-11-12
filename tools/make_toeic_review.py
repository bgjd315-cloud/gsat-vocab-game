# 產生多益職場英文主題包審查表 review/多益職場英文審查.xlsx
# 用法：python -I -X utf8 tools/make_toeic_review.py <專案根目錄> [dropped.json]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
base = {e['id']: e for e in json.load(open(f'{G}/src/raw/vocab-toeic.json', encoding='utf-8'))}
ex = json.load(open(f'{G}/src/examples/toeic.json', encoding='utf-8'))
HEAD = PatternFill('solid', fgColor='C2741F')
def header(ws, cols):
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = HEAD; c.alignment = Alignment(vertical='center', wrap_text=True)
wb = Workbook(); ws = wb.active; ws.title = '職場新字'
header(ws, ['id', '情境', '單字', '詞性', '中文', '例句', '例句中譯', '用法提醒', '多益頻率排名', '審查結果', '修改意見'])
for r in ex:
    ws.append([r['id'], r['group'], r['word'], r['pos'], r['zh'], r['en'], r['exzh'], r.get('note', ''), base[r['id']]['rank'], '', ''])
    if base[r['id']].get('extra'):
        for c in ws[ws.max_row]: c.fill = PatternFill('solid', fgColor='FFF2B3')
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'J2:J{ws.max_row}')
for col, wd in zip('ABCDEFGHIJK', [9, 14, 16, 8, 22, 54, 34, 26, 8, 10, 26]):
    ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in (5, 6, 7, 8, 11))
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
if len(sys.argv) > 2:
    dr = json.load(open(sys.argv[2], encoding='utf-8'))
    w2 = wb.create_sheet('未收的字')
    header(w2, ['單字', '多益頻率排名', '不收的理由', '要收嗎（填「收」）'])
    for r in dr: w2.append([r['word'], r['rank'], r['why_drop'], ''])
    for col, wd in zip('ABCD', [18, 10, 40, 16]): w2.column_dimensions[col].width = wd
    w2.freeze_panes = 'A2'
n = wb.create_sheet('說明')
for line in [f'多益職場英文主題包：TOEIC Service List 1.2（Browne & Culligan，CC BY-SA 4.0）中、本站各級（含第七級與詞性變化）都沒有的字，收 {len(ex)} 個，依六個職場情境分組。',
             '中文意思與例句全部為本站編寫。「職場新字」空白視同 OK；要改請在「審查結果」選修改並寫意見，不要的選刪除。',
             '黃色列＝原本判定不收、後來決定全部收的 98 個字（片段已改成完整的字，如 headquarters、pants、job seeker）。',
             '另外：本站既有字中有 765 個也在多益常見字表裡，會標「多益常見」，可在字卡圖鑑篩選，或在多益頁一次複習。']:
    n.append([line])
n.column_dimensions['A'].width = 120
out = f'{G}/review/多益職場英文審查.xlsx'; wb.save(out); print('ok', out, len(ex))
