const { chromium } = require('playwright-core');
const fs = require('fs'); const path = require('path');
(async () => {
  const svg = fs.readFileSync(path.join(__dirname, 'higher_ed_challenges.svg'), 'utf8');
  const [, VW, VH] = svg.match(/viewBox="0 0 (\d+) (\d+)"/).map(Number);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: VW, height: VH } });
  await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await page.evaluate(() => document.fonts.ready);
  const res = await page.evaluate(() => {
    const out = { texts: [], fontOk: document.fonts.check("700 20px Lato") };
    document.querySelectorAll('svg text').forEach(t => {
      const r = t.getBoundingClientRect();
      out.texts.push({ s: t.textContent, x0: r.left, y0: r.top, x1: r.right, y1: r.bottom, size: parseFloat(t.getAttribute('font-size')) });
    });
    const img = document.querySelector('svg image').getBoundingClientRect();
    out.logo = { x0: img.left, y0: img.top, x1: img.right, y1: img.bottom };
    return out;
  });
  const T = res.texts, W = VW, H = VH, M = 20;
  console.log('Lato loaded:', res.fontOk, '| text elements:', T.length);
  let issues = 0;
  T.forEach(t => {
    if (t.x0 < M || t.y0 < M || t.x1 > W - M || t.y1 > H - M) { issues++; console.log('EDGE', JSON.stringify(t.s), t.x0|0, t.y0|0, t.x1|0, t.y1|0); }
  });
  for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) {
    const a = T[i], b = T[j];
    const ox = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), oy = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
    if (ox > 2 && oy > 2) { issues++; console.log('OVERLAP', JSON.stringify(a.s), 'x', JSON.stringify(b.s), `${ox|0}x${oy|0}`); }
  }
  console.log('logo box', JSON.stringify(res.logo));
  console.log('issues:', issues);
  await browser.close();
})();
