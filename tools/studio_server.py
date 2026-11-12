"""生圖工作台：本機伺服器（只聽 127.0.0.1）
- GET  /tools/studio.html      工作台網頁
- GET  /api/prompts            從「Gemini生圖提示詞.md」解析出的提示詞
- GET  /api/status             哪些圖已經有了
- POST /api/upload?name=xxx    上傳一張圖（任何格式）→ 存成 img_raw/xxx.png → 去背縮圖到 img/xxx.webp
- POST /api/build              重新組合遊戲 index.html
其餘路徑當靜態檔案（遊戲本身）提供。
用法：python -I tools/studio_server.py [port]
"""
import io, json, os, re, subprocess, sys, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from process_images import process_one, SRC, DST  # noqa: E402
from PIL import Image  # noqa: E402

MD = os.path.join(ROOT, "Gemini生圖提示詞.md")

def parse_prompts():
    text = open(MD, encoding="utf-8").read()
    blocks = list(re.finditer(r"```\n(.*?)```", text, re.S))
    style = blocks[0].group(1).strip() if blocks else ""
    items, section, gstyle = [], "", ""
    for k, b in enumerate(blocks[1:], 1):
        before = text[:b.start()]
        sec = re.findall(r"^## (.+)$", before, re.M)
        section = sec[-1].strip() if sec else section
        gap = text[blocks[k - 1].end():b.start()]          # 只看上一個區塊到這個區塊之間的檔名
        m = re.findall(r"\*\*(?:檔名：)?`([a-z0-9_]+)\.png`\*\*(?:（([^）]*)）)?", gap)
        if not m:
            if "考題附圖風格" in gap: gstyle = b.group(1).strip().replace("請回覆「了解」即可，先不要畫圖。", "").strip()
            continue
        name, note = m[-1]
        prompt = b.group(1).strip()
        if name.startswith("gsat_") and gstyle: prompt = gstyle + "\n\n現在請畫：" + prompt   # 考題附圖自帶風格，不必先貼共同風格
        items.append({"name": name, "section": section, "note": note, "prompt": prompt})
    return {"style": style, "items": items}

NAMES = lambda: {i["name"] for i in parse_prompts()["items"]}

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header("Cache-Control", "no-store"); super().end_headers()
    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/prompts": return self._json(parse_prompts())
        if u.path == "/api/status":
            st = {}
            for n in NAMES():
                w = os.path.join(DST, "gsat", "parts", n + ".webp") if n.startswith("gsat_") else os.path.join(DST, n + ".webp")
                raw = os.path.join(SRC, n + ".png")   # 只算已貼上的 Gemini 新圖（img/ 裡的舊小卡圖不算）
                st[n] = int(os.path.getmtime(w)) if os.path.exists(raw) and os.path.exists(w) else 0
            return self._json(st)
        if u.path == "/": self.path = "/tools/studio.html"
        return super().do_GET()
    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/upload":
            name = (parse_qs(u.query).get("name") or [""])[0]
            if name not in NAMES(): return self._json({"ok": False, "err": "未知的檔名"}, 400)
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > 40_000_000: return self._json({"ok": False, "err": "檔案大小不對"}, 400)
            data = self.rfile.read(n)
            try:
                im = Image.open(io.BytesIO(data)); im.load()
            except Exception as e:
                return self._json({"ok": False, "err": "讀不到圖片：" + str(e)}, 400)
            os.makedirs(SRC, exist_ok=True)
            raw = os.path.join(SRC, name + ".png")
            im.save(raw, "PNG")
            out, size = process_one(raw)
            return self._json({"ok": True, "out": "img/" + out, "size": size, "raw": [im.width, im.height], "t": int(time.time())})
        if u.path == "/api/build":
            env = dict(os.environ, NO_COLOR="1", FORCE_COLOR="0")
            r = subprocess.run(["node", os.path.join(ROOT, "build.js")], capture_output=True, text=True, encoding="utf-8", env=env)
            return self._json({"ok": r.returncode == 0, "log": (r.stdout + r.stderr).strip()})
        return self._json({"ok": False}, 404)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8772
    print(f"生圖工作台：http://localhost:{port}/", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
