# 產生 App 圖示（加到手機主畫面用）：icons/icon-512.png、icon-192.png、apple-touch-icon.png（180）、maskable-512.png
# 用法：python -I tools/make_icons.py
# 若 img_raw/app_icon.png 存在（自己畫的圖示，正方形），就用它；否則用文字版圖示。
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'icons'); os.makedirs(OUT, exist_ok=True)
S = 1024

def grad(size, c1, c2):
    im = Image.new('RGB', (size, size)); px = im.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size - 2)
            px[x, y] = tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
    return im

def text_icon(safe):
    """safe：內容縮在中間的比例（maskable 圖示要留邊）"""
    im = grad(S, (124, 92, 240), (61, 110, 214))
    d = ImageDraw.Draw(im)
    # 柔和光暈
    glow = Image.new('L', (S, S), 0); ImageDraw.Draw(glow).ellipse([S * .18, S * .12, S * .82, S * .76], fill=110)
    im = Image.composite(Image.new('RGB', (S, S), (255, 255, 255)), im, glow.filter(ImageFilter.GaussianBlur(120)).point(lambda v: v // 3))
    d = ImageDraw.Draw(im)
    k = safe
    cx = S / 2
    f1 = ImageFont.truetype('C:/Windows/Fonts/msjhbd.ttc', int(330 * k))
    f2 = ImageFont.truetype('C:/Windows/Fonts/seguibl.ttf', int(150 * k))
    # 「單字」
    t = '單字'; w = d.textlength(t, font=f1)
    y1 = S / 2 - 250 * k
    d.text((cx - w / 2 + 8, y1 + 10), t, font=f1, fill=(40, 30, 110))          # 陰影
    d.text((cx - w / 2, y1), t, font=f1, fill=(255, 255, 255))
    # 「BOOST」
    t2 = 'BOOST'; w2 = d.textlength(t2, font=f2)
    y2 = S / 2 + 110 * k
    d.text((cx - w2 / 2 + 6, y2 + 8), t2, font=f2, fill=(40, 30, 110))
    d.text((cx - w2 / 2, y2), t2, font=f2, fill=(255, 214, 74))
    # 閃電
    bx, by, sc = cx + 345 * k, S / 2 - 410 * k, 1.0 * k
    bolt = [(0, 0), (-70, 130), (-10, 130), (-50, 250), (80, 90), (15, 90), (60, 0)]
    pts = [(bx + x * sc, by + y * sc) for x, y in bolt]
    d.polygon([(x + 6, y + 8) for x, y in pts], fill=(40, 30, 110))
    d.polygon(pts, fill=(255, 214, 74))
    return im

src = os.path.join(ROOT, 'img_raw', 'app_icon.png')
if os.path.exists(src):
    base = Image.open(src).convert('RGB'); w, h = base.size; m = min(w, h)
    base = base.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m)).resize((S, S), Image.LANCZOS)
    mask = Image.new('RGB', (S, S), base.getpixel((5, 5))); mask.paste(base.resize((int(S * .8),) * 2, Image.LANCZOS), (int(S * .1),) * 2)
else:
    base, mask = text_icon(1.0), text_icon(0.78)
base.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, 'icon-512.png'), optimize=True)
base.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, 'icon-192.png'), optimize=True)
base.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, 'apple-touch-icon.png'), optimize=True)
mask.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, 'maskable-512.png'), optimize=True)
print('ok', 'custom' if os.path.exists(src) else 'text')
