# 產生翻譯題審查表 review/學測翻譯題審查.xlsx
# 用法：python -I -X utf8 tools/make_tr_review.py <專案根目錄>
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
G = sys.argv[1]
st = json.load(open(f'{G}/src/examples/gsat_tr.json', encoding='utf-8'))
cards = {c['id']: c['title'] for c in json.load(open(f'{G}/src/examples/grammar_v2.json', encoding='utf-8'))}
wb = Workbook(); ws = wb.active; ws.title = '翻譯題'
ws.append(['關卡', '題', '中文題目', '參考答案', '也可以這樣寫', '提示 1：關鍵字', '提示 2：句型骨架', '翻譯策略', '自評要點（分數）', '連結文法卡', '審查結果', '修改意見'])
for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='7A5AE0'); c.alignment = Alignment(vertical='center', wrap_text=True)
for s in st:
    name = f"{s['y']} 學測" if s['kind'] == 'past' else f"{s['id']} {s['title']}"
    for i, it in enumerate(s['items'], 1):
        ws.append([name, i, it['zh'], it['ref'], '\n'.join(it['alt']), '\n'.join(f"{k['zh']} → {k['en']}" for k in it['keys']), it['frame'], it['tip'],
                   '\n'.join(f"{p['t']}（{p['w']}）" for p in it['points']), '\n'.join(cards.get(g, g) for g in it.get('gram', [])), '', ''])
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'K2:K{ws.max_row}')
for col, wd in zip('ABCDEFGHIJKL', [16, 4, 30, 44, 40, 30, 34, 30, 50, 20, 9, 28]): ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(vertical='top', wrap_text=True)
ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in ['學測闖關新增兩個分頁：「翻譯題」＝歷屆學測中譯英 97–115 年，一年一關、兩題，從最新年度開始；「翻譯句型特訓」＝12 個常考句型，一關 5 題，由易到難，連到對應文法卡。',
             '作答流程：學生先自己寫 → 可按「提示 1：關鍵字」「提示 2：句型骨架」→ 看參考答案與其他寫法 → 網站列出他用到幾個關鍵字 → 依「自評要點」勾選，算出 0–4 分。',
             '星等：總分達 50% 一顆星（解鎖下一關）、75% 兩顆、90% 三顆。學生寫的句子會存在自己的裝置。',
             '歷屆題中文照大考原文；參考答案、提示與評分要點為本站編寫（大考中心沒有公布官方答案），頁面會註明。',
             '空白視同 OK；要改請在「審查結果」選修改並寫意見，不要的選刪除。']:
    n.append([line])
n.column_dimensions['A'].width = 130
out = f'{G}/review/學測翻譯題審查.xlsx'; wb.save(out); print('ok', out, sum(len(s['items']) for s in st))
