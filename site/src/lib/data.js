// 설정 데이터 읽기 — 저장소 루트 data/*.yaml(04 데이터모델 v1.0 10-1절: exam_years·cohorts·exam_systems, + grade_cuts·assessment·exam_day).
// 2026-11-20 B-09. 빌드는 site/ 에서 실행되므로(Cloudflare Pages 루트 디렉터리 = site) 기본 위치는 ../data. SETTINGS_DIR 로 바꿀 수 있다.
// YAML 날짜(2027-11-18)는 js-yaml이 Date로 읽으므로 'YYYY-MM-DD' 문자열로 되돌린다(시간대 차이로 하루 밀리지 않게 UTC 기준).
import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const DIR = process.env.SETTINGS_DIR || path.resolve(process.cwd(), '..', 'data');

const norm = (v) => {
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  if (Array.isArray(v)) return v.map(norm);
  if (v && typeof v === 'object') return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, norm(x)]));
  return v;
};

function read(name) {
  const file = path.join(DIR, `${name}.yaml`);
  if (!fs.existsSync(file)) throw new Error(`설정 파일이 없습니다: ${file} (data/ 폴더를 확인하세요)`);
  return norm(yaml.load(fs.readFileSync(file, 'utf8')));
}

export const EXAM_YEAR_ROWS = read('exam_years');
export const COHORT_ROWS = read('cohorts');
export const EXAM_SYSTEM_ROWS = read('exam_systems');
export const GRADE_CUTS = read('grade_cuts');
export const ASSESSMENT = read('assessment');   // S5 영역별 평가 요소(B-12)
export const EXAM_DAY = read('exam_day');       // S7 시험 당일 안내(B-12)
export const SCHEDULES = read('schedules');     // T6 시험 캘린더(B-13)
export const STANDARDS = read('standards');     // 성취기준 코드 → 슬러그(B-13, tools/gen_standards.py가 만듦)

// 최소 검사 — 형식이 어긋나면 빌드를 멈춘다(08 스키마 검증 취지)
for (const e of EXAM_YEAR_ROWS) {
  if (!['확정', '예상'].includes(e.status)) throw new Error(`exam_years ${e.year}: status는 확정/예상만`);
  if (e.status === '확정' && !(e.source && e.result_date)) throw new Error(`exam_years ${e.year}: 확정이면 source·result_date 필수`);
}
for (const a of ASSESSMENT.areas) {
  if (!(a.area && a.behavior?.length && a.content?.length)) throw new Error(`assessment ${a.id}: area·content·behavior 필수`);
}
for (const k of ['before', 'day', 'allowed', 'banned', 'penalties', 'sources']) {
  if (!EXAM_DAY[k]?.length) throw new Error(`exam_day: ${k} 비어 있음`);
}
for (const [c, list] of Object.entries(SCHEDULES.cohorts)) for (const e of list) {
  if (!['확정', '추정'].includes(e.status)) throw new Error(`schedules ${c}: status는 확정/추정 — ${e.title}`);
  if (e.status === '확정' && !(e.src && SCHEDULES.sources[e.src])) throw new Error(`schedules ${c}: 확정인데 근거 없음 — ${e.title}`);
}
if (STANDARDS.count !== STANDARDS.standards.length) throw new Error('standards: count 불일치');
export const SLUG_OF = Object.fromEntries(STANDARDS.standards.map((s) => [s.code, s.slug]));
