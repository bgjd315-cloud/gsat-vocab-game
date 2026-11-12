# 產生片語例句審查表 review/課本片語例句審查.xlsx
# 用法：python -I -X utf8 tools/make_phr_review.py <專案根目錄>
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
ex = json.load(open(f'{G}/src/examples/phr.json', encoding='utf-8'))
first = {e['id']: e['first'] for e in json.load(open(f'{G}/src/raw/tb_phrases.json', encoding='utf-8'))}
wb = Workbook(); ws = wb.active; ws.title = '課本片語'
ws.append(['id', '出處', '片語', '朗讀說法', '中文', '編寫例句（英）', '例句中譯', '挖空部分', '審查結果', '修改後中文', '修改後英文', '修改後中譯', '備註'])
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='2F9FB0')
    c.alignment = Alignment(vertical='center', wrap_text=True)
for r in ex:
    f = first.get(r['id'], '')
    ws.append([r['id'], f'第{f[1]}冊 {f[2:]}' if f else '', r['phrase'], r['say'], r['zh'], r['en'], r['exzh'], ' … '.join(r['targets']), '', '', '', '', ''])
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'I2:I{ws.max_row}')
for col, wd in zip('ABCDEFGHIJKLM', [9, 11, 20, 20, 20, 50, 32, 18, 10, 18, 42, 28, 16]):
    ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in (5, 6, 7, 10, 11, 12))
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in [f'課本片語 {len(ex)} 個：第 1–5 冊各課「Idioms and Phrases」。',
             '中文和例句都是本站自己寫的，沒有抄課本。「朗讀說法」是發音時念的樣子（把 … 換成 someone／something）。',
             '「挖空部分」是句子挖空題要挖掉的字，分開的片語會挖成兩格（例：take … seriously）。',
             '片語只考選擇題（選中文、選片語、句子挖空選片語），不考拼字。',
             '請在「審查結果」選 OK／修改／刪除；空白視同 OK。審完交回才會上線。']:
    n.append([line])
n.column_dimensions['A'].width = 100
out = f'{G}/review/課本片語例句審查.xlsx'; wb.save(out); print('ok', out, ws.max_row - 1)
