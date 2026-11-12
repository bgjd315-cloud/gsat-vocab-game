// 單字開外掛：離線快取（service worker）。由 build.js 產生根目錄的 sw.js（VER 會換成圖片、音檔的指紋）
// - 網頁本身（index.html）與 audio/index.json：先上網拿最新的，沒網路才用存起來的
// - 圖片、音檔、圖示：用過一次就存起來，之後沒網路也能用（檔案有更新時 VER 會變，舊的自動清掉）
// - iPhone 播音檔會用 Range 請求，存起來的音檔要切成 206 回應才能播
const VER = 'faa9a2a276';
const SHELL = 'shell-v1', MEDIA = 'media-' + VER, FONT = 'font-v1';
const PRE = ['./', 'index.html', 'manifest.json', 'icons/icon-192.png', 'icons/apple-touch-icon.png', 'img/map6.webp', 'img/guide_hello.webp', 'img/guide_think.webp', 'img/guide_cheer.webp'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(PRE)).catch(() => {}).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => ![SHELL, MEDIA, FONT].includes(k)).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

async function networkFirst(req, key) {
  const c = await caches.open(SHELL);
  try {
    const r = await fetch(req, { cache: 'no-store' });
    if (r.ok) c.put(key || req, r.clone());
    return r;
  } catch (e) {
    return (await c.match(key || req, { ignoreSearch: true })) || (await c.match('index.html')) || Response.error();
  }
}
async function rangeFrom(resp, range) {
  const buf = await resp.arrayBuffer(), n = buf.byteLength;
  const m = /bytes=(\d*)-(\d*)/.exec(range) || [];
  let a = m[1] === '' || m[1] === undefined ? NaN : +m[1], b = m[2] === '' || m[2] === undefined ? NaN : +m[2];
  if (isNaN(a)) { a = Math.max(0, n - (isNaN(b) ? n : b)); b = n - 1; } else if (isNaN(b) || b >= n) b = n - 1;
  return new Response(buf.slice(a, b + 1), { status: 206, statusText: 'Partial Content', headers: {
    'Content-Type': resp.headers.get('Content-Type') || 'audio/mpeg', 'Content-Range': `bytes ${a}-${b}/${n}`, 'Content-Length': String(b - a + 1), 'Accept-Ranges': 'bytes' } });
}
async function cacheFirst(req, name) {
  const c = await caches.open(name), url = req.url.split('#')[0];
  const range = req.headers.get('range');
  let hit = await c.match(url, { ignoreSearch: true });
  if (!hit) {
    try {
      const r = await fetch(url);                       // 不帶 Range，整個檔案存起來
      if (r.ok && r.status === 200) { await c.put(url, r.clone()); hit = r; }
      else return range ? fetch(req) : r;
    } catch (e) { return Response.error(); }
  }
  return range ? rangeFrom(hit.clone(), range) : hit;
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const u = new URL(req.url);
  if (u.origin === location.origin) {
    const p = u.pathname;
    if (req.mode === 'navigate' || p.endsWith('/') || p.endsWith('/index.html')) { e.respondWith(networkFirst(req, 'index.html')); return; }
    if (p.endsWith('/audio/index.json') || p.endsWith('/manifest.json')) { e.respondWith(networkFirst(req)); return; }
    if (/\/(img|audio|icons)\//.test(p)) { e.respondWith(cacheFirst(req, MEDIA)); return; }
    return;
  }
  if (u.hostname === 'fonts.googleapis.com' || u.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open(FONT).then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(r => { if (r.ok || r.type === 'opaque') c.put(req, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    }));
  }
});
