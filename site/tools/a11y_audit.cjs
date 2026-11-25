// 렌더·모바일·접근성 자동 점검(계획서 63행 Claude 몫, 2026-11-25). Playwright(Chromium).
// dist의 모든 HTML 페이지 × 폭 320(200% 확대 리플로 기준)·360·768·1280 × 라이트·다크:
//  ① 가로 넘침 ② KaTeX 오류(.katex-error) ③ SVG 대체 텍스트(title·aria-label·aria-labelledby, 꾸밈은 aria-hidden)
//  ④ img alt ⑤ 글자 대비 4.5:1(큰 글자 18.66px 굵게·24px은 3:1) ⑥ 글자 크기 12px 미만
//     (로고 글자는 WCAG 1.4.3 예외 — 제외)
//  ⑦ 제목 순서(h1 1개, 단계 건너뛰기) ⑧ html lang=ko ⑨ 키보드 초점 표시(Tab 12회, outline 또는 box-shadow)
// 사용: (site) npx astro build → npx astro preview --port 4321 → node tools/a11y_audit.cjs > 결과.json
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const BASE = process.env.BASE || 'http://localhost:4321';
const DIST = path.join(__dirname, '..', 'dist');
const pages = [];
(function walk(d) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else if (e.name.endsWith('.html')) pages.push('/' + path.relative(DIST, p).replace(/\\/g, '/').replace(/index\.html$/, '')); } })(DIST);
pages.sort();

(async () => {
  const b = await chromium.launch();
  const issues = []; let loads = 0;
  const add = (page, w, s, kind, detail) => issues.push({ page, w, s, kind, detail });
  for (const s of ['light', 'dark']) for (const w of [320, 360, 768, 1280]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 }, colorScheme: s });
    const p = await ctx.newPage();
    for (const u of pages) {
      await p.goto(BASE + u, { waitUntil: 'networkidle' }); loads++;
      const r = await p.evaluate(({ full }) => {
        const out = {};
        out.overflow = document.documentElement.scrollWidth > innerWidth + 1;
        if (!full) return out;
        out.katex = document.querySelectorAll('.katex-error').length;
        out.svg = [...document.querySelectorAll('svg')].filter((v) => !v.closest('[aria-hidden="true"]') && v.getAttribute('aria-hidden') !== 'true'
          && !v.querySelector(':scope > title') && !v.getAttribute('aria-label') && !v.getAttribute('aria-labelledby')).map((v) => (v.closest('[class]')?.className || 'svg') + '').slice(0, 5);
        out.img = [...document.querySelectorAll('img')].filter((i) => !i.hasAttribute('alt')).map((i) => i.src).slice(0, 5);
        out.lang = document.documentElement.lang;
        const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter((h) => h.offsetParent !== null || h.closest('details')).map((h) => +h.tagName[1]);
        out.h1 = hs.filter((x) => x === 1).length;
        out.skip = hs.some((x, i) => i > 0 && x > hs[i - 1] + 1) ? hs.join('') : '';
        const rgb = (t) => (t.match(/[\d.]+/g) || []).map(Number);
        const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
        const lum = ([r, g, bb]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(bb);
        const bgOf = (el) => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c.length === 3 || (c.length === 4 && c[3] > 0.5)) return c.slice(0, 3); } return [255, 255, 255]; };
        const low = [], small = [];
        document.querySelectorAll('body *').forEach((el) => {
          const own = [...el.childNodes].some((t) => t.nodeType === 3 && t.textContent.trim());
          const cs = getComputedStyle(el); const rc = el.getBoundingClientRect();
          if (!own || rc.width === 0 || cs.visibility === 'hidden' || el.closest('[hidden],.katex,svg,.print-answers,.logo,.sr-only')) return;
          const fs = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700;
          if (fs < 12) small.push(`${el.tagName}.${el.className}:${fs}px`);
          const [x, y] = [lum(rgb(cs.color).slice(0, 3)), lum(bgOf(el))].sort((a, c) => c - a);
          const ratio = (x + 0.05) / (y + 0.05); const need = fs >= 24 || (bold && fs >= 18.66) ? 3 : 4.5;
          if (ratio < need) low.push(`${el.tagName}.${el.className}:${ratio.toFixed(2)}`);
        });
        out.low = [...new Set(low)].slice(0, 5); out.small = [...new Set(small)].slice(0, 5);
        return out;
      }, { full: w === 360 || w === 1280 });
      if (r.overflow) add(u, w, s, '가로 넘침', '');
      if (r.katex) add(u, w, s, 'KaTeX 오류', r.katex);
      if (r.svg?.length) add(u, w, s, 'SVG 대체 텍스트 없음', r.svg.join(', '));
      if (r.img?.length) add(u, w, s, 'img alt 없음', r.img.join(', '));
      if (r.lang !== undefined && r.lang !== 'ko') add(u, w, s, 'lang', r.lang);
      if (r.h1 !== undefined && r.h1 !== 1) add(u, w, s, 'h1 개수', r.h1);
      if (r.skip) add(u, w, s, '제목 단계 건너뜀', r.skip);
      if (r.low?.length) add(u, w, s, '대비 미달', r.low.join(', '));
      if (r.small?.length) add(u, w, s, '12px 미만 글자', r.small.join(', '));
      if (w === 1280 && s === 'light') {
        const f = [];
        await p.focus('body');
        for (let i = 0; i < 12; i++) {
          await p.keyboard.press('Tab');
          const v = await p.evaluate(() => { const a = document.activeElement; if (!a || a === document.body) return null; const cs = getComputedStyle(a); return { t: a.tagName + (a.className ? '.' + a.className : ''), ok: (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none' }; });
          if (v && !v.ok) f.push(v.t);
        }
        if (f.length) add(u, w, s, '초점 표시 없음', [...new Set(f)].join(', '));
      }
    }
    await ctx.close();
  }
  await b.close();
  const byKind = {}; for (const i of issues) (byKind[i.kind] ??= new Set()).add(i.page);
  console.log(JSON.stringify({ pages: pages.length, loads, issues: issues.length, byKind: Object.fromEntries(Object.entries(byKind).map(([k, v]) => [k, [...v]])), detail: issues }, null, 1));
})();
