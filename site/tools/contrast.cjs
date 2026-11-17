// 글자 대비 점검 — theme.css의 라이트·다크 색 토큰으로 WCAG 2 대비를 계산한다. 4.5:1 미만이 있으면 종료 코드 1.
// 사용: node tools/contrast.cjs   (2026-11-17 B-05)
const fs = require('fs');
const path = require('path');
const css = fs.readFileSync(path.join(__dirname, '..', 'src', 'styles', 'theme.css'), 'utf8');

function tokens(block) {
  const out = {};
  for (const m of block.matchAll(/--([\w-]+):\s*(#[0-9a-fA-F]{6})/g)) out[m[1]] = m[2];
  return out;
}
const light = tokens(css.match(/:root\s*{([\s\S]*?)}/)[1]);
const dark = { ...light, ...tokens(css.match(/prefers-color-scheme:\s*dark\)\s*{\s*:root\s*{([\s\S]*?)}/)[1]) };

const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const lum = (h) => { const n = parseInt(h.slice(1), 16); return 0.2126 * lin(n >> 16) + 0.7152 * lin((n >> 8) & 255) + 0.0722 * lin(n & 255); };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

// [글자, 바탕] — 실제로 함께 쓰는 짝
const PAIRS = [
  ['ink', 'bg'], ['ink', 'card'], ['ink', 'soft'],
  ['muted', 'bg'], ['muted', 'card'], ['muted', 'soft'],
  ['link', 'bg'], ['link', 'card'], ['link', 'soft'],
  ['accent', 'soft'], ['accent', 'bg'],
  ['ok', 'card'], ['ok', 'bg'],
  ['btn-fg', 'btn-bg'], ['notice-fg', 'notice-bg'],
];
let bad = 0;
for (const [name, t] of [['라이트', light], ['다크', dark]]) {
  const rows = PAIRS.map(([f, b]) => { const r = ratio(t[f], t[b]); if (r < 4.5) bad += 1; return `${f}/${b} ${r.toFixed(2)}${r < 4.5 ? ' ✗' : ''}`; });
  console.log(`${name}: ${rows.join(' · ')}`);
  console.log(`${name} 초점 테두리(비텍스트 3:1): ${ratio(t.focus, t.bg).toFixed(2)}`);
}
console.log(bad ? `미달 ${bad}건` : '모두 4.5:1 이상');
process.exit(bad ? 1 : 0);
