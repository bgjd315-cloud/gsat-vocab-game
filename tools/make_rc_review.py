# 產生學測閱讀測驗闖關審查表 review/學測閱讀測驗審查.xlsx
# 用法：python -I -X utf8 tools/make_rc_review.py <專案根目錄> [盲測結果 json：{"113-R2#39": 1}] [--all]
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G = sys.argv[1]
blind = json.load(open(sys.argv[2], encoding='utf-8')) if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else {}
cs = json.load(open(f'{G}/src/examples/gsat_rc.json', encoding='utf-8'))
if '--all' not in sys.argv: cs = [c for c in cs if c.get('status') != 'ok']
RED = PatternFill('solid', fgColor='FBE3E3')
wb = Workbook()
def head(ws, cols, color):
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor=color)
        c.alignment = Alignment(vertical='center', wrap_text=True)
a = wb.active; a.title = '文章與鷹架'
head(a, ['id', '學年度', '題號', '標題', '類型', '原文（大考中心，不需審）', '圖表說明', '讀前提示', '關鍵字', '段落大意', '中譯', '讀後整理', '審查結果', '修改意見'], '3FAE95')
for c in cs:
    a.append([c['id'], c['y'], f"{c['first']}–{c['first'] + len(c['qs']) - 1}", c.get('title', ''), c.get('genre', ''), '\n\n'.join(c['text']),
              c.get('figure', ''), c.get('pre', ''), '\n'.join(f"{g['w']}：{g['zh']}" for g in c.get('gloss', [])),
              '\n'.join(f'{i+1}. {g}' for i, g in enumerate(c.get('gist', []))), '\n\n'.join(c['zh']), c.get('summary', ''), '', ''])
q = wb.create_sheet('題目解析')
head(q, ['id', '題號', '題型', '題目與選項（原題）', '答案', '提示', '證據句', '解析', '選項分析', '策略', 'AI 盲測', '審查結果', '修改意見'], '8274DC')
for c in cs:
    for x in c['qs']:
        b = blind.get(f"{c['id']}#{x['n']}")
        flag = '' if b is None else ('一致' if b == x['a'] else f"不一致：盲測選 ({'ABCD'[b]})")
        q.append([c['id'], x['n'], x.get('type', ''), x['s'] + '\n' + '\n'.join(f"({'ABCD'[i]}) {o}" for i, o in enumerate(x['o'])),
                  '(' + 'ABCD'[x['a']] + ')', x.get('hint', ''), x.get('ev', ''), x.get('ex', ''), '\n'.join(x.get('why', [])), x.get('strat', ''), flag, '', ''])
        if flag.startswith('不一致'):
            for cell in q[q.max_row]: cell.fill = RED
for ws, cols, widths, wrap, vcol in ((a, 'ABCDEFGHIJKLMN', [9, 7, 8, 16, 14, 64, 30, 30, 26, 34, 50, 34, 10, 26], range(4, 15), 'M'),
                                     (q, 'ABCDEFGHIJKLM', [9, 6, 9, 50, 6, 30, 40, 40, 44, 30, 14, 10, 26], range(3, 14), 'L')):
    dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'{vcol}2:{vcol}{max(2, ws.max_row)}')
    for col, wd in zip(cols, widths): ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for cell in row: cell.alignment = Alignment(vertical='top', wrap_text=cell.column in wrap)
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
n = wb.create_sheet('說明')
for line in ['學測闖關・閱讀測驗：97–115 學年度學測英文閱讀測驗，一篇一關，附四層鷹架。',
             '① 讀前準備（文章類型、讀前提示、關鍵字）② 閱讀中（每段大意，可開關）③ 作答（提示 → 作答後標出證據句、解析、四個選項分析、題型策略）④ 讀後整理＋全文中譯。',
             '原文、題目與答案是大考中心原題與公布答案（已和原卷、官方答案核對），不需審；請審本站寫的鷹架與解析。空白視同 OK。',
             '原題附圖表的篇章，網站無法顯示原圖，改用「圖表說明」文字描述，請特別看一下是否足以作答。']:
    n.append([line])
n.column_dimensions['A'].width = 110
out = f'{G}/review/學測閱讀測驗審查.xlsx'; wb.save(out); print('ok', out, len(cs), '篇', q.max_row - 1, '題')
