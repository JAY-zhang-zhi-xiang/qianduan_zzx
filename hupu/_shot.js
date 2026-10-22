// 通用截图：node _shot.js <url> <width> <height> <dsf> <out> [top|bottom|<selector>]
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
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: +dsf, mobile: true });
  await send('Page.navigate', { url });
  await new Promise(r => setTimeout(r, 1500));
  await send('Runtime.evaluate', { expression: 'document.fonts.ready', awaitPromise: true });

  if (mode === 'bottom') {
    await send('Runtime.evaluate', { expression: 'window.scrollTo(0, document.documentElement.scrollHeight)' });
    await new Promise(r => setTimeout(r, 700));
  } else if (mode !== 'top') {
    // 把目标元素滚进视口，再按视口坐标裁切
    await send('Runtime.evaluate', { expression: `(()=>{const e=document.querySelector(${JSON.stringify(mode)});if(e)e.scrollIntoView({block:'center'})})()` });
    await new Promise(r => setTimeout(r, 700));
  }

  let clip;
  if (mode !== 'top' && mode !== 'bottom') {
    const r = await send('Runtime.evaluate', {
      expression: `(()=>{const e=document.querySelector(${JSON.stringify(mode)});if(!e)return null;const b=e.getBoundingClientRect();return JSON.stringify({x:b.left,y:b.top,w:b.width,h:b.height})})()`,
      returnByValue: true
    });
    const v = r.result.result.value;
    if (v) { const b = JSON.parse(v); clip = { x: Math.max(0, b.x - 2), y: Math.max(0, b.y - 2), width: b.w + 4, height: b.h + 4, scale: 1 }; }
    // 只截导航条时，把页面主体隐藏掉，避免裁切边缘带上正文内容
    await send('Runtime.evaluate', { expression: `(()=>{var p=document.querySelector('.zzx-page');if(p)p.style.visibility='hidden';document.body.style.background='#ffffff';})()` });
    await new Promise(r => setTimeout(r, 250));
  }

  const shot = await send('Page.captureScreenshot', clip
    ? { format: 'png', fromSurface: true, captureBeyondViewport: false, clip }
    : { format: 'png', fromSurface: true, captureBeyondViewport: false });
  fs.writeFileSync(out, Buffer.from(shot.result.data, 'base64'));
  console.log('ok ->', out);
  ws.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
