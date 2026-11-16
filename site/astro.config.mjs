// 수능랩 사이트 — 정적 출력, 결정 6(Astro)·7(Cloudflare Pages). 2026-11-17 초기화(계획서 52행, 백로그 B-04): 11/11 시안(Paul 승인 11/12)에서 출발
import { defineConfig } from 'astro/config';
export default defineConfig({ output: 'static', site: 'https://suneunglab.com', build: { format: 'directory' } });
