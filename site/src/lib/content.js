// 학습 콘텐츠 읽기 — DATA_DIR(환경 변수)의 YAML을 읽는다. 없으면 빈 콘텐츠로 빌드(페이지는 '준비 중').
// 게시 확정 콘텐츠는 구축 B-10·B-23에서 저장소 content/ 로 들어온다. 검수 대기·예비분·교과서 텍스트는 비공개 저장소(결정 11) — 이 저장소에 넣지 않는다(지침 5).
import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import katex from 'katex';
import { EXAM_YEAR_ROWS } from './data.js';

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

// 수능 시험일(04 데이터모델 ExamYear — 확정 표시 필수, R11). 2026-11-20 B-09: data/exam_years.yaml에서 읽는다(트랙 제공·확정만).
export const EXAMS = EXAM_YEAR_ROWS.filter((e) => e.track_provided && e.status === '확정').map((e) => ({ year: e.year, date: e.exam_date, status: e.status }));
export function dday(from, to) {
  const d = Math.round((Date.parse(to) - Date.parse(from)) / 86400000);
  return d === 0 ? 'D-day' : d > 0 ? `D-${d}` : `D+${-d}`;
}
export const weekday = (iso) => '일월화수목금토'[new Date(iso + 'T00:00:00Z').getUTCDay()];
