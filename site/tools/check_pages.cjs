// B-07 페이지 점검(2026-11-19) — Playwright(Chromium). 360·1280px × 라이트·다크:
//  ① 가로 넘침 ② 실제 화면 글자 대비(계산된 글자색 vs 실제 바탕색, 4.5:1 미만 목록) ③ 메뉴 7·바닥글 7 개수 ④ 화면 캡처(SHOT).
//  ⑤ dist 전체 HTML의 내부 링크가 dist에 있는지(깨진 링크 목록).
// 사용: (site 폴더) npx astro build → dist를 http://localhost:4321 로 띄운 뒤 node tools/check_pages.cjs → tools/shots/b07_*.png (저장소 제외)
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const OUT = path.join(__dirname, 'shots');
fs.mkdirSync(OUT, { recursive: true });
const BASE = process.env.BASE || 'http://localhost:4321';
const DIST = path.join(__dirname, '..', 'dist');
const PAGES = [['system', '/system/'], ['changes', '/system/changes/'], ['links', '/system/links/'], ['notices', '/notices/'],
  ['subscribe', '/subscribe/'], ['concepts', '/concepts/'], ['about', '/about/'], ['how', '/about/how-it-works/'],
  ['license', '/about/license/'], ['corrections', '/about/corrections/'], ['report', '/about/report/'], ['bot', '/about/bot/'],
  ['privacy', '/privacy/'], ['contact', '/contact/'], ['search', '/search/'], ['404', '/404.html']];
const SHOT = new Set(['system', 'links', 'notices', 'subscribe', 'how', 'privacy']);

// ⑤ 깨진 내부 링크(정적 검사)
function brokenLinks() {
  const files = [];
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).forEach((e) => { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else if (p.endsWith('.html')) files.push(p); });
  walk(DIST);
  const exists = (u) => { const p = path.join(DIST, decodeURI(u.split('#')[0].split('?')[0])); return fs.existsSync(p) && (fs.statSync(p).isFile() || fs.existsSync(path.join(p, 'index.html'))); };
  const bad = {};
  for (const f of files) {
    const html = fs.readFileSync(f, 'utf8');
    for (const m of html.matchAll(/href="(\/[^"]*)"/g)) if (!m[1].startsWith('//') && !exists(m[1])) (bad[m[1]] ??= new Set()).add('/' + path.relative(DIST, f).replace(/index\.html$/, ''));
  }
  return { pages: files.length, broken: Object.fromEntries(Object.entries(bad).map(([k, v]) => [k, [...v].slice(0, 3)])) };
}

(async () => {
  const b = await chromium.launch();
  const res = {};
  for (const scheme of ['light', 'dark']) {
    for (const w of [360, 1280]) {
      for (const [name, url] of PAGES) {
        const p = await b.newPage({ viewport: { width: w, height: 800 }, deviceScaleFactor: 1, colorScheme: scheme });
        await p.goto(BASE + url, { waitUntil: 'networkidle' });
        res[`${name}_${w}_${scheme}`] = await p.evaluate(() => {
          const rgb = (s) => (s.match(/[\d.]+/g) || []).map(Number);
          const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
          const lum = ([r, g, bb]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(bb);
          const bgOf = (el) => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c.length === 3 || (c.length === 4 && c[3] > 0.5)) return c.slice(0, 3); } return [255, 255, 255]; };
          const low = [];
          let n = 0;
          document.querySelectorAll('body *').forEach((el) => {
            const own = [...el.childNodes].some((t) => t.nodeType === 3 && t.textContent.trim());
            const r = el.getBoundingClientRect();
            if (!own || r.width === 0 || getComputedStyle(el).visibility === 'hidden' || el.closest('.skip,.logo,[hidden]')) return;
            n += 1;
            const fg = rgb(getComputedStyle(el).color).slice(0, 3); const bg = bgOf(el);
            const [x, y] = [lum(fg), lum(bg)].sort((a, c) => c - a);
            const ratio = (x + 0.05) / (y + 0.05);
            if (ratio < 4.5) low.push(`${el.tagName}.${el.className}:${ratio.toFixed(2)}`);
          });
          return {
            overflowX: document.documentElement.scrollWidth - window.innerWidth,
            textEls: n, lowContrast: [...new Set(low)].slice(0, 5),
            menu: document.querySelectorAll('.menu-wide > a, .menu-wide > details').length,
            footer: document.querySelectorAll('.foot nav a').length,
            robots: document.querySelector('meta[name=robots]')?.content ?? '',
          };
        });
        if (SHOT.has(name)) await p.screenshot({ path: path.join(OUT, `b07_${name}_${w}_${scheme}.png`), fullPage: true });
        await p.close();
      }
    }
  }
  // 공지 필터 동작(1280·라이트): 분류 '모의평가·학평'만 → 보이는 행 수
  const q = await b.newPage({ viewport: { width: 1280, height: 800 } });
  await q.goto(BASE + '/notices/', { waitUntil: 'networkidle' });
  const total = await q.locator('#notices li:not([hidden])').count();
  await q.selectOption('select[data-f="cat"]', 'mock');
  const mock = await q.locator('#notices li:not([hidden])').count();
  await q.fill('input[data-f="q"]', '없는제목xyz');
  const none = await q.locator('#notices li:not([hidden])').count();
  res.filter = { total, mock, none, emptyMsg: await q.isVisible('#nf-empty') };
  await b.close();
  const vals = Object.entries(res).filter(([k]) => k !== 'filter');
  const summary = {
    screens: vals.length,
    overflow: vals.filter(([, v]) => v.overflowX > 0).map(([k]) => k),
    lowContrast: vals.filter(([, v]) => v.lowContrast.length).map(([k, v]) => [k, v.lowContrast]),
    menuFooterBad: vals.filter(([, v]) => v.menu !== 7 && v.menu !== 0 || v.footer !== 7).map(([k, v]) => [k, v.menu, v.footer]),
    noindexPages: [...new Set(vals.filter(([, v]) => v.robots).map(([k]) => k.split('_')[0]))],
    filter: res.filter,
    links: brokenLinks(),
  };
  console.log(JSON.stringify(summary, null, 1));
})();
