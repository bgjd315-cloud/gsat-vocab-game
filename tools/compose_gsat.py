# 把生圖工作台畫好的學測附圖（img/gsat/parts/gsat_*.webp）拼成題目用的圖 img/gsat/{年}-{題}.webp
# 四選一的圖拼成 2×2 四格並標 (A)(B)(C)(D)；單張圖直接放大存檔。缺圖的題目會保留原本的圖。
# 用法：python -I -X utf8 tools/compose_gsat.py <專案根目錄>
import os, sys, re
from PIL import Image, ImageDraw, ImageFont

G = sys.argv[1]
P = os.path.join(G, 'img', 'gsat', 'parts'); OUT = os.path.join(G, 'img', 'gsat')
def font(sz):
    for f in ('C:/Windows/Fonts/times.ttf', 'C:/Windows/Fonts/arial.ttf'):
        try: return ImageFont.truetype(f, sz)
        except OSError: pass
    return ImageFont.load_default()
names = sorted(f[:-5] for f in os.listdir(P) if f.endswith('.webp')) if os.path.isdir(P) else []
groups = {}
for n in names:
    m = re.match(r'gsat_(\d+)_(\d+)(?:_([a-d]))?$', n)
    if m: groups.setdefault((m.group(1), m.group(2)), {})[m.group(3) or ''] = n
for (y, q), parts in sorted(groups.items()):
    if '' in parts:   # 單張
        im = Image.open(os.path.join(P, parts[''] + '.webp')).convert('RGB'); im.thumbnail((520, 520))
        im.save(os.path.join(OUT, f'{y}-{q}.webp'), quality=85); print(y, q, '單張'); continue
    if set(parts) != set('abcd'): print(y, q, '缺', sorted(set('abcd') - set(parts)), '→ 保留原圖'); continue
    cell, pad, lab = 460, 14, 40
    G2 = Image.new('RGB', (cell * 2 + pad * 3, (cell + lab) * 2 + pad * 3), 'white'); d = ImageDraw.Draw(G2); f = font(32)
    for k, ch in enumerate('abcd'):
        im = Image.open(os.path.join(P, parts[ch] + '.webp')).convert('RGB'); im.thumbnail((cell, cell))
        x = pad + (k % 2) * (cell + pad); y0 = pad + (k // 2) * (cell + lab + pad)
        d.rectangle((x - 2, y0 - 2, x + cell + 2, y0 + lab + cell + 2), outline=(0, 0, 0), width=2)
        d.text((x + 8, y0 + 4), f'({ch.upper()})', font=f, fill='black')
        G2.paste(im, (x + (cell - im.width) // 2, y0 + lab + (cell - im.height) // 2))
    G2.save(os.path.join(OUT, f'{y}-{q}.webp'), quality=85); print(y, q, '四格')
