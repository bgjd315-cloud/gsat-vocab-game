# 產生第七級（進階字彙，2026-11 改版）審查表 review/第七級改版審查.xlsx
# 用法：python -I -X utf8 tools/make_l7v2_review.py <專案根目錄> [被拿掉的敏感字 json]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
v = json.load(open(f'{G}/src/raw/vocab-7.json', encoding='utf-8'))
ex = {r['id']: r for r in json.load(open(f'{G}/src/examples/l7.json', encoding='utf-8'))}
kk = json.load(open(f'{G}/src/raw/kk.json', encoding='utf-8'))
HEAD = PatternFill('solid', fgColor='3D5AA8'); GRN = PatternFill('solid', fgColor='E3F4EA')
def header(ws, cols):
    ws.append(cols)
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = HEAD; c.alignment = Alignment(vertical='center', wrap_text=True)
def fmt(ws, widths, wrap):
    for col, wd in zip('ABCDEFGHIJKLMN', widths): ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in wrap)
    ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
wb = Workbook(); ws = wb.active; ws.title = '新第七級全部'
header(ws, ['id', 'Day', '單字', '詞性', 'KK', '中文', '例句', '例句中譯', '用法提醒', '來源', '審查結果', '修改意見'])
for e in v:
    r = ex[e['id']]; old = r['status'] == 'ok'
    ws.append([e['id'], e['day'], r['word'], r['pos'], kk.get(e['id'], ''), r['zh'], r['en'], r['exzh'], r.get('note', ''), '原第七級（已審）' if old else '新字（待審）', '', ''])
    if old:
        for c in ws[ws.max_row]: c.fill = GRN
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'K2:K{ws.max_row}')
fmt(ws, [9, 5, 16, 8, 18, 22, 54, 34, 24, 14, 9, 26], (6, 7, 8, 9, 12))
w2 = wb.create_sheet('移除的舊字')
header(w2, ['id', '單字', '詞性', '中文', '說明'])
for i, r in ex.items():
    if r['status'] == 'retired': w2.append([i, r['word'], r['pos'], r['zh'], '原第七級（英檢字表），新字表沒有選到，不再顯示；學生原本的進度保留在紀錄裡'])
for col, wd in zip('ABCDE', [9, 18, 8, 26, 60]): w2.column_dimensions[col].width = wd
if len(sys.argv) > 2:
    w3 = wb.create_sheet('拿掉的敏感字')
    header(w3, ['單字', '類別', '要加回嗎（填「加回」）'])
    for x in json.load(open(sys.argv[2], encoding='utf-8')): w3.append([x['w'], x['cat'], ''])
    for col, wd in zip('ABC', [18, 16, 20]): w3.column_dimensions[col].width = wd
n = wb.create_sheet('說明')
nn = sum(1 for e in v if ex[e['id']]['status'] != 'ok')
for line in [f'第七級改版：原本選自英檢中高級字表（未取得授權），改用開放授權的 wordfreq 詞頻（CC BY-SA 4.0）選出大考詞彙表以外的常用字，再依「對高中閱讀的實用度」挑選排序。共 {len(v)} 字、46 天。',
             f'綠色列＝原第七級就有、已審過的字（沿用原本的中文、例句、音檔），共 {len(v) - nn} 字，可略過；白色列＝新字 {nn} 個，中文與例句為本站新編寫，已校對一輪（修正 122 處）。',
             '「移除的舊字」：原第七級沒選進新字表的字，網站不再顯示；學過的學生紀錄仍保留，之後若再加回會接續原進度。',
             '「拿掉的敏感字」：依上次刪字標準（戰爭武器、政治意識形態、性與生殖、犯罪司法、宗教教義、歧視標籤、排泄血腥）先拿掉的字；想留的填「加回」，我再補內容。',
             '空白視同 OK；要改請在「審查結果」選修改並寫意見，不要的選刪除。']:
    n.append([line])
n.column_dimensions['A'].width = 130
out = f'{G}/review/第七級改版審查.xlsx'; wb.save(out); print('ok', out, len(v), nn)
