// node shot.js <url> <w> <h> <dsf> <out> [top|bottom|<selector>]
const http = require('http');
const fs = require('fs');
const PORT = process.env.CDP_PORT || 9225;
const get = u => new Promise((res, rej) => http.get(u, s => { let d = ''; s.on('data', c => d += c); s.on('end', () => res(JSON.parse(d))); }).on('error', rej));

(async () => {
  const [url, w, h, dsf, out, mode = 'top'] = process.argv.slice(2);
  const tabs = await get(`http://127.0.0.1:${PORT}/json`);
  const page = tabs.find(t => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: +dsf, mobile: true });
  await send('Page.navigate', { url });
  await new Promise(r => setTimeout(r, 1600));
  await send('Runtime.evaluate', { expression: 'document.fonts.ready', awaitPromise: true });
  if (mode === 'bottom') {
    await send('Runtime.evaluate', { expression: 'window.scrollTo(0, document.documentElement.scrollHeight)' });
    await new Promise(r => setTimeout(r, 600));
  }
  const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  fs.writeFileSync(out, Buffer.from(shot.result.data, 'base64'));
  console.log('ok ->', out);
  ws.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
