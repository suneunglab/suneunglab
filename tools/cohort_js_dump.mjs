// tools/test_cohort_parity.py가 부르는 도우미 — site/src/lib/calendar.js(JS) 결과를 날짜별 JSON으로 낸다. 2026-11-22 B-11.
// 사용: node tools/cohort_js_dump.mjs 2027-03-01 2027-11-19 …
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import * as cal from '../site/src/lib/calendar.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(path.join(here, '..', 'site', 'package.json'));
const yaml = require('js-yaml');
const norm = (v) => (v instanceof Date ? v.toISOString().slice(0, 10) : v);
const read = (n) => yaml.load(fs.readFileSync(path.join(here, '..', 'data', `${n}.yaml`), 'utf8'))
  .map((r) => Object.fromEntries(Object.entries(r).map(([k, v]) => [k, norm(v)])));
const exams = read('exam_years');
const cohorts = read('cohorts');
const first = Math.min(...cohorts.map((c) => c.id));

const out = process.argv.slice(2).map((date) => ({
  date,
  slots: cal.slotsOf(date, first, exams),
  generate: cal.generationCohorts(date, first, exams, cohorts),
  band: cal.bandCohorts(date, first, exams),
}));
process.stdout.write(JSON.stringify(out));
