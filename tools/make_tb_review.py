# 產生課本補充字例句審查表 review/課本補充字例句審查.xlsx
# 用法：python -I -X utf8 tools/make_tb_review.py <專案根目錄>
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
ex = json.load(open(f'{G}/src/examples/tb.json', encoding='utf-8'))
first = {e['id']: e['first'] for e in json.load(open(f'{G}/src/raw/tb_extras.json', encoding='utf-8'))}
wb = Workbook(); ws = wb.active; ws.title = '課本補充字'
ws.append(['id', '首次出現', '單字', '詞性', '中文', '編寫例句（英）', '例句中譯', '挖空字', '審查結果', '修改後中文', '修改後英文', '修改後中譯', '備註'])
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='C0647A')
    c.alignment = Alignment(vertical='center', wrap_text=True)
for r in ex:
    f = first.get(r['id'], '')
    ws.append([r['id'], f'第{f[1]}冊 {f[2:]}' if f else '', r['word'], r['pos'], r['zh'], r['en'], r['exzh'], r['target'], '', '', '', '', ''])
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'I2:I{ws.max_row}')
for col, wd in zip('ABCDEFGHIJKLM', [9, 11, 16, 8, 18, 50, 32, 13, 10, 18, 42, 28, 16]):
    ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in (5, 6, 7, 10, 11, 12))
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in [f'課本補充字 {len(ex)} 個：第 1–5 冊各課「Words for Production」中，網站詞表（銜接站＋三到六級）沒有的字。',
             '多半是二級字（國中後段到高一常見字）和衍生字（如 accidentally、embarrassed）。',
             '中文和例句都是本站自己寫的，沒有抄課本；請在「審查結果」選 OK／修改／刪除，修改的寫在後面三欄。',
             '空白視同 OK。審完交回，這些字才會出現在正式網站的課本進度裡。']:
    n.append([line])
n.column_dimensions['A'].width = 100
out = f'{G}/review/課本補充字例句審查.xlsx'; wb.save(out); print('ok', out, ws.max_row - 1)
