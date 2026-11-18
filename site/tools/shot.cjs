// 화면 점검 캡처 — Playwright(Chromium). 360px·1280px × 라이트·다크, 메뉴 펼침, 가로 넘침·KaTeX 오류 측정.
// 사용: (site 폴더) npx astro build → dist를 http://localhost:4321 로 띄운 뒤 node tools/shot.cjs → tools/shots/*.png (저장소 제외)
// 2026-11-11 시안 v0.1 작성, 2026-11-17 B-05에서 다크·메뉴·1280 확대, 2026-11-18 B-06에서 트랙(T1)·코호트(T2)·오늘 페이지 추가
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const OUT = path.join(__dirname, 'shots');
fs.mkdirSync(OUT, { recursive: true });
const BASE = process.env.BASE || 'http://localhost:4321';
const TODAY = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);   // KST
const PAGES = [['home', '/'], ['g1', '/g1/2029/2026-11-09/'], ['g3', '/g3/2028/2026-11-09/'],
  ['t1_g1', '/g1/'], ['t1_g3', '/g3/'], ['t2_g2', '/g2/2028/'], ['today_g1', `/g1/2029/${TODAY}/`]];
const SHOT = new Set(['home', 't1_g1', 't1_g3', 't2_g2', 'today_g1']);   // 전체 화면을 남길 페이지

(async () => {
  const b = await chromium.launch();
  const res = {};
  for (const scheme of ['light', 'dark']) {
    for (const w of [360, 1280]) {
      for (const [name, url] of PAGES) {
        const p = await b.newPage({ viewport: { width: w, height: 800 }, deviceScaleFactor: 1, colorScheme: scheme });
        await p.goto(BASE + url, { waitUntil: 'networkidle' });
        const key = `${name}_${w}_${scheme}`;
        res[key] = await p.evaluate(() => ({
          overflowX: document.documentElement.scrollWidth - window.innerWidth,
          wide: [...document.querySelectorAll('body *')].filter((e) => { const r = e.getBoundingClientRect(); return r.right > window.innerWidth + 1 && !e.closest('.tw,.katex-display,.fig,.tabs'); }).slice(0, 3).map((e) => e.tagName + '.' + e.className),
          katex: document.querySelectorAll('.katex').length,
          katexErr: document.querySelectorAll('.katex-error').length,
          menuItems: document.querySelectorAll('.menu-wide > a, .menu-wide > details').length,
          tracks: [...document.querySelectorAll('.dd-panel a')].map((a) => a.textContent),
          footerLinks: document.querySelectorAll('.foot nav a').length,
        }));
        if (SHOT.has(name)) await p.screenshot({ path: path.join(OUT, `${key}.png`), fullPage: name === 'home' });
        if (name === 'home' && w === 360) {
          await p.click('.menu-narrow > summary');
          await p.screenshot({ path: path.join(OUT, `${key}_menu.png`) });
        }
        if (name === 'home' && w === 1280) {
          await p.click('.dd > summary');
          await p.screenshot({ path: path.join(OUT, `${key}_tracks.png`), clip: { x: 0, y: 0, width: 1280, height: 320 } });
        }
        if (name === 'g3' && w === 360) {
          await p.evaluate(() => { const f = document.querySelector('#science .fig'); if (f) { f.scrollIntoView(); window.scrollBy(0, -140); } });
          await p.screenshot({ path: path.join(OUT, `${key}_svg.png`) });
        }
        if (name === 'g1' && w === 1280) await p.screenshot({ path: path.join(OUT, `${key}.png`) });
        await p.close();
      }
    }
  }
  // 본문 바로가기(키보드 Tab 첫 칸)
  const k = await b.newPage({ viewport: { width: 360, height: 800 } });
  await k.goto(BASE + '/', { waitUntil: 'networkidle' });
  await k.keyboard.press('Tab');
  res.skipLink = await k.evaluate(() => document.activeElement.className + ':' + document.activeElement.getBoundingClientRect().top);
  await k.screenshot({ path: path.join(OUT, 'skip_link.png'), clip: { x: 0, y: 0, width: 360, height: 120 } });
  console.log(JSON.stringify(res, null, 1));
  await b.close();
})();
