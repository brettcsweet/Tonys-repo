const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
(async () => {
  const scale = parseFloat(process.argv[2] || '1');
  const out = process.argv[3] || path.join(__dirname, 'preview.png');
  const svg = fs.readFileSync(path.join(__dirname, 'higher_ed_challenges.svg'), 'utf8');
  const [, VW, VH] = svg.match(/viewBox="0 0 (\d+) (\d+)"/).map(Number);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: scale });
  await page.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  await page.screenshot({ path: out, clip: process.argv[4] ? (([x,y,w,h]) => ({x,y,width:w,height:h}))(process.argv[4].split(',').map(Number)) : { x: 0, y: 0, width: VW, height: VH } });
  await browser.close();
  console.log('wrote', out);
})();
