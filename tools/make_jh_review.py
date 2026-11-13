# 產生國中基礎站審查表 review/國中基礎站審查.xlsx
# 用法：python -I -X utf8 tools/make_jh_review.py <專案根目錄> [校對修正 applied.json]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
base = {e['id']: e for e in json.load(open(f'{G}/src/raw/jh_words.json', encoding='utf-8'))}
ex = json.load(open(f'{G}/src/examples/jh.json', encoding='utf-8'))
kk = json.load(open(f'{G}/src/raw/kk.json', encoding='utf-8'))
HEAD = PatternFill('solid', fgColor='8A6A3E')
def header(ws, cols):
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = HEAD; c.alignment = Alignment(vertical='center', wrap_text=True)
wb = Workbook(); ws = wb.active; ws.title = '國中基礎站'
header(ws, ['id', '天', '單字', 'KK', '詞性', '中文', '例句', '例句中譯', '用法提醒', '學測出現年數', '審查結果', '修改意見'])
for r in ex:
    b = base[r['id']]
    ws.append([r['id'], b['day'], r['word'], kk.get(r['id'], ''), r['pos'], r['zh'], r['en'], r['exzh'], r.get('note', ''), len(b['years']), '', ''])
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'K2:K{ws.max_row}')
for col, wd in zip('ABCDEFGHIJKL', [8, 5, 14, 16, 8, 22, 50, 34, 26, 8, 10, 26]):
    ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in (6, 7, 8, 9, 12))
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
if len(sys.argv) > 2:
    A = json.load(open(sys.argv[2], encoding='utf-8'))
    w2 = wb.create_sheet('校對已修正')
    header(w2, ['id', '單字', '欄位', '原本', '改成', '原因'])
    F = {'pos': '詞性', 'zh': '中文', 'en': '例句', 'exzh': '例句中譯', 'target': '目標字', 'note': '用法提醒'}
    W = {r['id']: r['word'] for r in ex}
    for f in A: w2.append([f['id'], W.get(f['id'], ''), F.get(f['field'], f['field']), f['old'], f['new'], f['why']])
    for col, wd in zip('ABCDEF', [8, 14, 10, 44, 44, 34]): w2.column_dimensions[col].width = wd
    for row in w2.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column >= 4)
    w2.freeze_panes = 'A2'
n = wb.create_sheet('說明')
for line in [f'國中基礎站：十二年國教課綱〈國民中小學英語 2000 基本字彙〉裡、本站其他級別都沒有的字，共 {len(ex)} 個，每天 25 字、{max(b["day"] for b in base.values())} 天。',
             '給基礎較弱的高中生先補國中字；分級小測國中字答對率低於 70% 的學生，會建議從這一站開始。',
             '中文意思、例句、中譯、用法提醒全部為本站編寫，已先做過一輪從嚴校對（修正內容見「校對已修正」頁）。',
             '審查方式：空白視同 OK；要改請在「審查結果」選「修改」並在「修改意見」寫怎麼改；不要的字選「刪除」。',
             '這一級不出拼字題。審完後會錄製單字與例句的朗讀語音再上線。']:
    n.append([line])
n.column_dimensions['A'].width = 120
out = f'{G}/review/國中基礎站審查.xlsx'; wb.save(out); print('ok', out, len(ex))
