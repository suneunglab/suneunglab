const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const res = {};
  for (const [name, w, path] of [['home_360', 360, '/'], ['track_360', 360, '/g1/2029/2026-11-09/'], ['track_1280', 1280, '/g1/2029/2026-11-09/'], ['g3_360', 360, '/g3/2028/2026-11-09/']]) {
    const p = await b.newPage({ viewport: { width: w, height: 800 }, deviceScaleFactor: 2 });
    await p.goto('http://localhost:4321' + path, { waitUntil: 'networkidle' });
    const m = await p.evaluate(() => ({
      overflowX: document.documentElement.scrollWidth - window.innerWidth,
      wideEls: [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.right > window.innerWidth + 1 && !e.closest('.tw,.katex-display,.fig,.tabs'); }).slice(0,5).map(e => e.tagName + '.' + e.className),
      katex: document.querySelectorAll('.katex').length, katexErr: document.querySelectorAll('.katex-error').length,
      svg: document.querySelectorAll('.fig svg').length, probs: document.querySelectorAll('.prob').length, details: document.querySelectorAll('details.ans').length,
      height: document.documentElement.scrollHeight }));
    res[name] = m;
    await p.screenshot({ path: `shots/${name}.png`, fullPage: name === 'home_360' || name === 'track_1280' });
    if (name === 'g3_360') {
      await p.evaluate(() => { const f = document.querySelector('#science .fig'); f.closest('.prob').querySelector('details.ans').open = true; f.scrollIntoView(); window.scrollBy(0, -120); });
      await p.screenshot({ path: 'shots/g3_360_science_svg.png' });
    }
    if (name === 'track_360') {
      await p.evaluate(() => document.querySelector('#math').scrollIntoView());
      await p.screenshot({ path: 'shots/track_360_math.png' });
      await p.evaluate(() => { 1 });
      await p.screenshot({ path: 'shots/track_360_science_svg.png' });
    }
    await p.close();
  }
  const d = await b.newPage({ viewport: { width: 360, height: 800 }, deviceScaleFactor: 2, colorScheme: 'dark' });
  await d.goto('http://localhost:4321/', { waitUntil: 'networkidle' }); await d.screenshot({ path: 'shots/home_360_dark.png' });
  console.log(JSON.stringify(res, null, 1)); await b.close();
})();
