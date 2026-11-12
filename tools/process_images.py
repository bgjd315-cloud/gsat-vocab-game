"""把 img_raw/ 裡 Gemini 畫好的圖處理成遊戲用素材，輸出到 img/。
- map、region_*（場景橫幅）：縮成寬 1600 的 webp，不去背
- 其他：洋紅色 #FF00FF 背景去背 → 去色溢 → 裁掉透明邊 → 最長邊 512 → webp（保留透明）
用法：python -I tools/process_images.py
"""
import os, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, DST = os.path.join(ROOT, "img_raw"), os.path.join(ROOT, "img")
os.makedirs(DST, exist_ok=True)

def chroma(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # 「洋紅程度」：紅藍都高、綠低
    mag = np.minimum(r, b) - g
    alpha = np.clip((140 - mag) / 90, 0, 1)          # mag≥140 全透明，≤50 全不透明
    # 去色溢：半透明邊緣把多出來的紅藍拉回綠的水準
    spill = np.clip(mag, 0, None) * (1 - alpha)
    r, b = r - spill, b - spill
    out = np.dstack([r, g, b, alpha * 255]).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    box = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    return im.crop(box) if box else im

def is_magenta_bg(im):
    """四個角落有兩個以上是洋紅色，才算洋紅底"""
    a = im.convert("RGB"); w, h = a.size
    def mag(p): r, g, b = a.getpixel(p); return min(r, b) - g > 120
    return sum(mag(p) for p in [(3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)]) >= 2

def vignette(im):
    """圓角方形遮罩，邊緣 12% 漸淡成透明"""
    im = im.convert("RGBA"); w, h = im.size
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = np.minimum(x, w - 1 - x) / w; dy = np.minimum(y, h - 1 - y) / h
    edge = np.minimum(dx, dy)
    alpha = np.clip(edge / 0.12, 0, 1) ** 1.5
    a = np.asarray(im).copy(); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8)
    return Image.fromarray(a, "RGBA")

def process_one(path):
    """處理單一原圖，回傳輸出檔名與尺寸"""
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    im = Image.open(path)
    if stem.startswith("gsat_"):   # 學測附圖重繪：白底、不去背，存到 img/gsat/（之後再拼成四格圖）
        im = im.convert("RGB"); im.thumbnail((700, 700), Image.LANCZOS)
        os.makedirs(os.path.join(DST, "gsat", "parts"), exist_ok=True)
        im.save(os.path.join(DST, "gsat", "parts", stem + ".webp"), "WEBP", quality=85)
        return "gsat/parts/" + stem + ".webp", im.size
    if stem.startswith("map") or stem.startswith("region_"):
        im = im.convert("RGB")
        if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        im.save(os.path.join(DST, stem + ".webp"), "WEBP", quality=82)
    else:
        # Gemini 沒畫洋紅底時不去背，改成四邊柔和淡出
        im = chroma(im) if is_magenta_bg(im) else vignette(im)
        im.thumbnail((512, 512), Image.LANCZOS)
        im.save(os.path.join(DST, stem + ".webp"), "WEBP", quality=85)
    return stem + ".webp", im.size

def main():
    names = sorted(f for f in os.listdir(SRC) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
    if not names:
        print("img_raw/ 是空的"); return
    for f in names:
        out, size = process_one(os.path.join(SRC, f))
        print("ok", out, size)

if __name__ == "__main__":
    main()
