# 產生例句審查表 review/第<級>級例句審查.xlsx
# 用法：python -I tools/make_review.py <專案根目錄> <級別>
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G, LV = sys.argv[1], sys.argv[2]
ZH = {'0': '國中銜接站', '3': '三', '4': '四', '5': '五', '6': '六'}[LV]
ex = json.load(open(f'{G}/src/examples/l{LV}.json', encoding='utf-8'))
words = {r[0]: r for r in json.load(open(f'{G}/src/words.json', encoding='utf-8'))}
wb = Workbook(); ws = wb.active; ws.title = '銜接站例句審查' if LV == '0' else f'第{ZH}級例句審查'
ws.append(['id', 'Day', '單字', '詞性', '中文（參考）', '學測出現年數', '編寫例句（英）', '例句中譯', '挖空字', '自動檢查',
           '審查結果', '修改後英文', '修改後中譯', '備註', '學測原句（參考，不需審）'])
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='7A5AE0')
    c.alignment = Alignment(vertical='center', wrap_text=True)
yellow = PatternFill('solid', fgColor='FFF2B3')
for r in ex:
    w = words[r['id']]
    exam = f"{w[8][0]}學年度：{w[8][1]}" if w[8] else ''
    ws.append([r['id'], w[2], w[4], w[5], w[6], len(w[7]), r['en'], r['zh'], r['target'], r['note'], '', '', '', '', exam])
    if r['note'].startswith('超出'): ws.cell(ws.max_row, 10).fill = yellow
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'K2:K{ws.max_row}')
for col, wd in zip('ABCDEFGHIJKLMNO', [9, 6, 16, 10, 18, 8, 50, 32, 12, 22, 10, 42, 28, 16, 60]):
    ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in (7, 8, 10, 12, 13, 15))
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
lo = int(LV) - 1
for line in [f'第{ZH}級編寫例句 {len(ex)} 句，請在「審查結果」欄選 OK／修改／刪除。',
             '選「修改」時，把改好的句子填在「修改後英文」「修改後中譯」，挖空字若有變也請在備註寫明。',
             f'「自動檢查」標黃色＝句中有字超出第 1–{lo} 級（常是人名、衍生字、不規則變化，可能誤判）；「含其他{ZH}級字」只是提醒。',
             '原則：句中除了目標字，只用比它低的級別；情境以高中生（尤其女生）的校園、社團、朋友、家庭、飲食、旅行為主。',
             '敏感字已用中性情境，請特別看一下是否適合學生。',
             '學測原句欄是大考中心試題原文，只供參考，遊戲會另外標示來源，不需審。',
             '審完存檔交回，匯入後標「編寫例句」的字才會正式上線。']:
    n.append([line])
n.column_dimensions['A'].width = 100
out = f'{G}/review/' + ('國中銜接站例句審查.xlsx' if LV == '0' else f'第{ZH}級例句審查.xlsx'); wb.save(out); print('ok', out, ws.max_row - 1)
