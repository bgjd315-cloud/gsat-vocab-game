# 產生詞性變化審查表 review/詞性變化審查.xlsx（每個級別一張工作表）
# 用法：python -I -X utf8 tools/make_fam_review.py <專案根目錄>
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
fam = json.load(open(f'{G}/src/examples/fam.json', encoding='utf-8'))
W = {r[0]: r for r in json.load(open(f'{G}/src/words.json', encoding='utf-8'))}
NAME = {0: '銜接站', 2: '課本補充字', 3: '第三級', 4: '第四級', 5: '第五級', 6: '第六級'}
wb = Workbook(); wb.remove(wb.active)
sheets = {}
for lv in (0, 3, 4, 5, 6, 2):
    ws = wb.create_sheet(NAME[lv]); sheets[lv] = ws
    ws.append(['id', '單字', '詞性', '中文', '詞性變化', '填空句（英）', '答案', '中譯', '審查結果', '修改意見'])
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='4C94D6')
        c.alignment = Alignment(vertical='center', wrap_text=True)
for r in fam:
    w = W.get(r['id'])
    if not w: continue
    q = r.get('q') or {}
    sheets[w[1]].append([r['id'], w[4], w[5], w[6], '\n'.join(f'{a} {p} {z}' for a, p, z in r['fam']),
                         q.get('en', ''), q.get('answer', ''), q.get('zh', ''), '', ''])
for ws in sheets.values():
    dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'I2:I{max(2, ws.max_row)}')
    for col, wd in zip('ABCDEFGHIJ', [9, 16, 9, 16, 34, 48, 14, 30, 10, 30]):
        ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in (4, 5, 6, 8, 10))
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in ['每個字列出常用的詞性變化／衍生字（遊戲會在單字卡、答題回饋和字卡圖鑑顯示），以及一題「填入正確詞性」練習句。',
             '練習句只在學生把這個字練到 3 星以上才會出現：句子挖空，給原形，學生要打出正確的詞性變化（學測混合題、非選常考）。',
             '「詞性變化」欄空白＝這個字沒有常用的相關字；填空句空白＝沒有適合的練習句。',
             '請在「審查結果」選 OK／修改／刪除，修改的寫在「修改意見」；空白視同 OK。審完交回才會上線。']:
    n.append([line])
n.column_dimensions['A'].width = 110
out = f'{G}/review/詞性變化審查.xlsx'; wb.save(out); print('ok', out, {NAME[k]: v.max_row - 1 for k, v in sheets.items()})
