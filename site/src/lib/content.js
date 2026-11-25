// 학습 콘텐츠 읽기 — DATA_DIR(환경 변수)의 YAML을 읽는다. 없으면 빈 콘텐츠로 빌드(페이지는 '준비 중').
// 게시 확정 콘텐츠는 구축 B-10·B-23에서 저장소 content/ 로 들어온다. 검수 대기·예비분·교과서 텍스트는 비공개 저장소(결정 11) — 이 저장소에 넣지 않는다(지침 5).
import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import katex from 'katex';

export const SUBJECTS = [
  ['korean', '국어'], ['math', '수학'], ['english', '영어'], ['history', '한국사'], ['social', '통합사회'], ['science', '통합과학'],
];
export const BEHAVIOR = {
  korean: { vocab: '어휘·개념', literal: '사실적 이해', inferential: '추론적 이해', critical: '비판적 이해', apply: '적용·창의' },
  math: { calc: '계산', understand: '이해', reason: '추론', solve: '문제 해결' },
  english: { main: '중심 내용', detail: '세부 정보', implied: '함축 의미', context: '맥락 파악', speak: '간접 말하기', write: '간접 쓰기', form: '언어 형식·어휘' },
  history: { knowledge: '역사 지식 이해', chrono: '연대기적 사고', issue: '상황·쟁점 인식', inquiry: '탐구 설계·수행', source: '자료 분석·해석', judge: '역사적 판단' },
  social: { concept: '개념·원리 이해', problem: '문제 파악', design: '탐구 설계', analyze: '자료 분석', conclude: '결론 도출', value: '가치 판단' },
  science: { understand: '이해', apply: '적용', hypothesis: '가설 설정', design: '탐구 설계', collect: '자료 수집', transform: '자료 해석', generalize: '일반화', communicate: '의사소통' },
};

export function loadDay(track, date) {
  const dir = process.env.DATA_DIR;
  const out = {};
  if (!dir) return out;
  for (const [key] of SUBJECTS) {
    const f = path.join(dir, `${track}_${key}.yaml`);
    if (fs.existsSync(f)) out[key] = yaml.load(fs.readFileSync(f, 'utf8'));
  }
  return out;
}

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function inline(s) {
  // $$…$$ · $…$ 를 KaTeX로, 나머지는 이스케이프. [① 표현] 밑줄 표시(F11)도 처리.
  const parts = String(s).split(/(\$\$[\s\S]+?\$\$|\$[^$\n]+?\$)/g);
  return parts.map((p) => {
    if (p.startsWith('$$')) return katex.renderToString(p.slice(2, -2), { displayMode: true, throwOnError: false });
    if (p.startsWith('$') && p.length > 1) return katex.renderToString(p.slice(1, -1), { throwOnError: false });
    return esc(p).replace(/\[([①②③④⑤])\s*([^\]]+)\]/g, '<u><span class="mk">$1</span> $2</u>');
  }).join('');
}

export function rich(s) {
  // 줄 단위: '|'로 시작하는 연속 줄은 표, 빈 줄은 문단 구분.
  if (s == null) return '';
  const lines = String(s).replace(/\r/g, '').split('\n');
  let html = '', table = [], para = [];
  const flushP = () => { if (para.length) { html += `<p>${para.map(inline).join('<br>')}</p>`; para = []; } };
  const flushT = () => {
    if (!table.length) return;
    const rows = table.filter((r) => !/^\|\s*-/.test(r)).map((r) => r.replace(/^\||\|$/g, '').split('|').map((c) => c.trim()));
    html += '<div class="tw"><table>' + rows.map((r, i) => '<tr>' + r.map((c) => (i === 0 ? `<th>${inline(c)}</th>` : `<td>${inline(c)}</td>`)).join('') + '</tr>').join('') + '</table></div>';
    table = [];
  };
  for (const ln of lines) {
    if (/^\s*\|/.test(ln)) { flushP(); table.push(ln.trim()); continue; }
    flushT();
    if (!ln.trim()) { flushP(); continue; }
    para.push(ln);
  }
  flushT(); flushP();
  return html;
}

export const svg = (s) => String(s || '').replace(/<script[\s\S]*?<\/script>/gi, '').replace(/\son\w+="[^"]*"/gi, '');
export const choiceMark = (i) => '①②③④⑤'[i];
export const dots = (d) => '●'.repeat(d) + '○'.repeat(3 - d);

// 수능 시험일·D-day는 calendar.js(examOf·dday)와 components/DDay.astro로 옮김(2026-11-22 B-11)
export { dday } from './calendar.js'; // 2026-11-22 B-11: 계산은 calendar.js 한 곳
export const weekday = (iso) => '일월화수목금토'[new Date(iso + 'T00:00:00Z').getUTCDay()];

// ── B-13(2026-11-24, 계획서 62행 앞당김): 게시 콘텐츠 실데이터 경로 ─────────────────────
// 위치: 저장소 content/lessons/{코호트}/{YYYY}/{MM}/{YYYY-MM-DD}.md (04 데이터모델 10-1절, 스키마 B-10).
// 게시 조건: status '게시' + example 아님(견본은 content/schema/examples/에만 있고 여기서 읽지 않는다).
// 실데이터가 없는 날은 DATA_DIR(로컬 시안 확인용 yaml)로, 그것도 없으면 빈 값('준비 중').
const LESSON_ROOT = path.resolve(process.cwd(), '..', 'content', 'lessons');

function readFront(file) {
  const t = fs.readFileSync(file, 'utf8').replace(/\r/g, '');
  const m = t.match(/^---\n([\s\S]*?)\n---/);
  return m ? yaml.load(m[1]) : null;
}
const published = (doc) => doc && doc.status === '게시' && !doc.example;
// YAML의 날짜(2026-11-23)는 js-yaml이 Date(UTC 자정)로 읽는다 → 'YYYY-MM-DD' 문자열로 통일
export const isoOf = (v) => (v instanceof Date ? v.toISOString().slice(0, 10) : String(v).slice(0, 10));

// 코호트의 게시 학습 파일 전체(날짜 오름차순) — 아카이브·최근 7일·전날/다음날에 쓴다
const _cache = new Map();
export function listLessons(cohort) {
  const key = String(cohort);
  if (_cache.has(key)) return _cache.get(key);
  const dir = path.join(LESSON_ROOT, key);
  const out = [];
  if (fs.existsSync(dir)) {
    for (const y of fs.readdirSync(dir).sort()) for (const m of fs.readdirSync(path.join(dir, y)).sort()) {
      const md = path.join(dir, y, m);
      if (!fs.statSync(md).isDirectory()) continue;
      for (const f of fs.readdirSync(md).filter((x) => /^\d{4}-\d{2}-\d{2}\.md$/.test(x)).sort()) {
        const doc = readFront(path.join(md, f));
        if (published(doc) && String(doc.cohort) === key && isoOf(doc.date) === f.slice(0, 10)) out.push({ ...doc, date: isoOf(doc.date), _dir: md });
      }
    }
  }
  _cache.set(key, out);
  return out;
}

// 그날 코호트 학습 → { korean: {concept, problems, passage}, … } (DATA_DIR 시안과 같은 모양)
export function loadLesson(cohort, track, date) {
  const doc = listLessons(cohort).find((d) => isoOf(d.date) === date);
  if (doc) return { source: 'content', doc, day: Object.fromEntries(doc.subjects.map((s) => [s.subject, s])) };
  const day = loadDay(track, date);
  return { source: Object.keys(day).length ? 'data_dir' : 'none', doc: null, day };
}

// 그림(63행 점검, 2026-11-25): 게시 파일의 figures는 'fig/이름.svg'(학습 파일 옆 fig 폴더) → 파일을 읽어 넣는다.
//   시안 yaml(DATA_DIR)은 SVG 글을 바로 담으므로 그대로. 그림에 <title>이 없으면 빌드를 멈춘다(대체 텍스트 필수, 06 SVG 규칙).
export function figureHtml(f, dir) {
  let t = String(f || '');
  if (/^fig\/[a-z0-9-]+\.svg$/.test(t)) {
    const p = path.join(dir || '', t);
    if (!dir || !fs.existsSync(p)) throw new Error(`그림 파일 없음: ${p}`);
    t = fs.readFileSync(p, 'utf8');
    if (!/<title>[^<]+<\/title>/.test(t)) throw new Error(`그림에 <title>(대체 텍스트) 없음: ${p}`);
  }
  t = svg(t);
  return /<svg[^>]*\srole=/.test(t) ? t : t.replace(/<svg\b/, '<svg role="img"');
}

// D6(1주차 점검): 성취기준 코드 중복 제거, 순서 유지
export const uniq = (a) => [...new Set((a || []).map((x) => String(x).trim()).filter(Boolean))];

// 행동 영역 라벨(아카이브 필터)
export const behaviorLabel = (subject, code) => BEHAVIOR[subject]?.[code] ?? code;
