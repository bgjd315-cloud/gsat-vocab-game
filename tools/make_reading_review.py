# 產生閱讀短文審查表 review/第?級閱讀短文審查.xlsx
# 用法：python -I tools/make_reading_review.py <專案根目錄> <src/reading 檔名> [盲測結果 json]
import json, sys, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

G, FN = sys.argv[1], sys.argv[2]
blind = json.load(open(sys.argv[3], encoding='utf-8')) if len(sys.argv) > 3 else {}
rs = [r for r in json.load(open(f'{G}/src/reading/{FN}', encoding='utf-8')) if r.get('status') not in ('retired', 'deleted')]
words = {r[0]: r for r in json.load(open(f'{G}/src/words.json', encoding='utf-8'))}
lv = rs[0]['level']; ZH = {0: '銜接站', 2: '課本延伸', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '多益'}[lv]
plain = lambda t: re.sub(r'\[\[([^|\]]+)\|[^\]]+\]\]', r'\1', t)
HDR = PatternFill('solid', fgColor='7A5AE0'); RED = PatternFill('solid', fgColor='FBE3E3')
wrap = Alignment(vertical='top', wrap_text=True)

wb = Workbook()
ws = wb.active; ws.title = '短文'
ws.append(['id', 'Day', '類型', '標題', '主題', '字數', '英文全文', '中譯', '註釋', '本日單字', '複習單字', '審查結果', '修改意見'])
for r in rs:
    text = '\n\n'.join(plain(p) for p in r['paragraphs'])
    ws.append([r['id'], r['day'], '長文' if r['kind'] == 'long' else '多益' if r['kind'] == 'toeic' else '短文', r['title'], r.get('topic', ''),
               len(re.findall(r"[A-Za-z']+", text)), text, '\n\n'.join(r.get('zh', [])),
               '；'.join(f"{g['word']} {g['zh']}" for g in r.get('glosses', [])),
               ', '.join(words[i][4] for i in r.get('targets', []) if i in words),
               ', '.join(words[i][4] for i in r.get('review', []) if i in words), '', ''])
for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = HDR
for col, wd in zip('ABCDEFGHIJKLM', [9, 5, 6, 22, 12, 6, 70, 50, 16, 30, 18, 10, 30]): ws.column_dimensions[col].width = wd
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = wrap
dv = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'L2:L{ws.max_row}')
ws.freeze_panes = 'E2'

wq = wb.create_sheet('題目')
wq.append(['id', '題號', '題型', '題幹', '(A)', '(B)', '(C)', '(D)', '答案', '解析', '依據句', 'AI 盲測', '審查結果', '修改意見'])
for r in rs:
    qs = [(q, q.get('type', '')) for q in r['questions']] + [(q, '單字・' + (words[q['word']][4] if q.get('word') in words else '')) for q in r.get('vocab', [])]
    for k, (q, ty) in enumerate(qs, 1):
        b = blind.get(f"{r['id']}#{k}")
        flag = '' if b is None else ('一致' if b == q['answer'] else f"不一致：盲測選 ({'ABCD'[b]})")
        wq.append([r['id'], k, ty, q['stem'], *q['options'], '(' + 'ABCD'[q['answer']] + ')', q.get('explain', ''), q.get('evidence', ''), flag, '', ''])
        if flag.startswith('不一致'):
            for c in wq[wq.max_row]: c.fill = RED
for c in wq[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = HDR
for col, wd in zip('ABCDEFGHIJKLMN', [9, 5, 10, 40, 22, 22, 22, 22, 6, 44, 40, 14, 10, 30]): wq.column_dimensions[col].width = wd
for row in wq.iter_rows(min_row=2):
    for c in row: c.alignment = wrap
dv2 = DataValidation(type='list', formula1='"OK,修改,刪除"', allow_blank=True); wq.add_data_validation(dv2); dv2.add(f'M2:M{wq.max_row}')
wq.freeze_panes = 'E2'

n = wb.create_sheet('說明')
for line in [(f'多益職場短文（多益閱讀 Part 7 題型：書信、公告、廣告、雙篇），共 {len(rs)} 篇；Day＝情境組別 1 辦公室與文書、2 會議與溝通、3 出差・旅遊・飯店、4 購物・客服・行銷、5 人事・求職・財務、6 生活與設施。' if lv == 8 else f'國中銜接站閱讀短文，共 {len(rs)} 篇。' if lv == 0 else f'課本延伸閱讀（第 1–5 冊每課一篇，同主題原創、用該課單字與片語），共 {len(rs)} 篇。' if lv == 2 else f'第{ZH}級閱讀短文，共 {len(rs)} 篇。')+'「短文」與「題目」兩張工作表各自選 OK／修改／刪除，修改的請在「修改意見」寫明。',
             '短文原則：本日單字 10–15 個、複習單字 3–5 個；其他字只用比目標級別低的字；表外字最多 3 個並附中文註釋。',
             '題目：4 題學測題型（細節、字義或指涉、主旨或推論）＋2 題單字題（把當天的字換情境再用一次）。',
             '「AI 盲測」欄：另一個 AI 只看文章與題目作答，和答案一致才算通過；標紅色的是不一致，請特別看。',
             '全部為原創內容，故事情節為虛構。']:
    n.append([line])
n.column_dimensions['A'].width = 110
out = f'{G}/review/' + ('多益職場短文審查.xlsx' if lv == 8 else '國中銜接站閱讀短文審查.xlsx' if lv == 0 else '課本延伸閱讀審查.xlsx' if lv == 2 else f'第{ZH}級閱讀短文審查.xlsx'); wb.save(out); print('ok', out)
