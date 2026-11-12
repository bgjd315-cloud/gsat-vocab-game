# 產生 KK 音標審查表 review/KK音標審查.xlsx
# 用法：python -I -X utf8 tools/make_kk_review.py <專案根目錄> [抽查意見 issues.json]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
issues = {x['id']: x for x in json.load(open(sys.argv[2], encoding='utf-8'))} if len(sys.argv) > 2 else {}
W = json.load(open(f'{G}/src/words.json', encoding='utf-8'))
K = json.load(open(f'{G}/src/raw/kk.json', encoding='utf-8'))
MAN = {k.lower() for k in json.load(open(f'{G}/src/raw/kk_manual.json', encoding='utf-8'))}
LV = {0: '銜接', 1: '片語', 2: '課本補充', 3: 'L3', 4: 'L4', 5: 'L5', 6: 'L6', 7: 'L7', 8: '多益'}
HEAD = PatternFill('solid', fgColor='3D5AA8'); YEL = PatternFill('solid', fgColor='FFF2B3'); BLU = PatternFill('solid', fgColor='DCE8FF'); RED = PatternFill('solid', fgColor='FBE3E3')
wb = Workbook()
def sheet(ws, rows):
    ws.append(['id', '級別', '單字', '詞性', 'KK 音標', '說明', '審查結果', '正確音標（要改才填）'])
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = HEAD; c.alignment = Alignment(vertical='center', wrap_text=True)
    for r, note, fill in rows:
        ws.append([r[0], LV[r[1]], r[4], r[5], K[r[0]], note, '', ''])
        if fill:
            for c in ws[ws.max_row]: c.fill = fill
    dv = DataValidation(type='list', formula1='"OK,修改"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'G2:G{max(2, ws.max_row)}')
    for col, wd in zip('ABCDEFGH', [9, 7, 22, 9, 34, 40, 9, 30]): ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=c.column in (5, 6, 8))
    ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
def tag(r):
    word = r[4].lower()
    if r[0] in issues: return f"抽查建議寫成 {issues[r[0]]['fix']}（{issues[r[0]]['why']}）", RED
    if any(x in MAN for x in [word] + word.replace('-', ' ').split()): return '人工補或更正（字典沒收、抽查更正或 KK 習慣不同）', YEL
    if '／' in K[r[0]]: return '名詞／動詞重音不同，兩種都標', BLU
    return '', None
rows = [(r, *tag(r)) for r in W]
sheet(wb.active, [x for x in rows if x[2]]); wb.active.title = '優先看'
sheet(wb.create_sheet('全部'), rows)
n = wb.create_sheet('說明')
for line in [f'全站 {len(W)} 個單字與片語的 KK 音標（美式）。來源：CMU Pronouncing Dictionary（BSD 授權）自動轉換成 KK，再依 KK 字典習慣調整：',
             '　重音符號 ˋ（主重音）、͵（次重音）標在該音節前；單音節字不標；兩音節字不標次重音；字尾輕讀的 y 寫 ɪ（happy [ˋhæpɪ]）；成音節 ḷ ṇ（table [ˋtebḷ]）。',
             '　名詞、動詞重音不同的字兩種都標，例如 protest [ˋprotɛst] n.／[prəˋtɛst] v.；separate 等 -ate 字的形容詞／動詞念法也分開標。',
             '　片語照顯示的字逐字標，單音節字不標重音；sb、sth 保留原樣。字的後面有 (ment)、(s) 或斜線的，音標標第一個寫法。',
             '「優先看」只列需要特別確認的：紅色＝兩輪抽查（隨機 868 字＋所有兩讀字，找到的 46 處已修正）中，兩種寫法都通、我先保留的；黃色＝人工補或更正的；藍色＝名詞／動詞兩讀。',
             '要改的請在「審查結果」選修改，並在最後一欄填正確音標；空白視同 OK。紅色列若要改成建議的寫法，選修改即可（不用再填）。']:
    n.append([line])
n.column_dimensions['A'].width = 130
out = f'{G}/review/KK音標審查.xlsx'; wb.save(out)
print('ok', out, '優先看', sum(1 for x in rows if x[2]))
