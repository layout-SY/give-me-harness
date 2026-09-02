# 이력서·포트폴리오 기록

## 사례 1 — 로컬 개발 서버 포트 고정

- 작업 유형: 프로젝트 설정
- 관련 도메인/서비스: Vite 개발 서버
- 문제 출처: 사용자 요구

### 문제 상황

- 사용자가 제시한 요구·문제·변경 이유: 로컬 `npm run dev`를 2000 포트로 실행하게 `package.json`을 바꾸라고 했다.
- 테스트·런타임에서 관찰한 오류: 없음
- 필요한 기술·구조·패턴이 없을 때 발생할 문제: `vite.config.ts` 기본값이 2426이라 `npm run dev`만 실행하면 2000이 아니다.

### 세션·하네스 사고 근거

해당 없음

- 플랫폼·프로젝트 또는 cwd: Cursor, asan-metaverse-user-ui
- main session ID와 관련 child session 범위: 측정 근거 없음
- 사용자 핵심 지시 원문과 시각: 2026-08-27에 로컬 `npm run dev`를 2000 포트로 실행되게 `package.json`을 변경하라고 했다.
- 재지적·중단 지시와 시각: 없음
- compaction 전후 `Objective`·제한·`Next Move` 변화: 해당 없음
- 지시와 어긋난 파일 수정·도구·검토·캡처·재작업: 없음
- message·transcript entry·input token·cache read·child session 측정값: 측정 근거 없음
- 측정 출처와 인과 해석의 한계: 해당 없음
- 비용·품질·협업 영향에 관한 사용자 피드백: 없음
- 방지책과 남은 host·Hook 제한: `vite.config.ts`는 사용자가 지정하지 않아 변경하지 않았다.

### 고민과 선택

- 사용자 제안: `package.json`을 바꿔 `npm run dev`가 2000 포트로 실행되게 한다.
- 에이전트 제안: `dev` 스크립트에 `vite --port 2000`을 넣는다. CLI가 설정 파일 포트보다 우선한다.
- 검토한 대안: (1) `package.json`만 변경 (2) `vite.config.ts`의 `server.port`도 2000으로 변경
- 최종 선택: (1)
- 선택 이유와 제외한 방식의 이유: 사용자가 `@package.json`만 지정했다.

### 적용

- 변경 경로: `package.json`
- 구현·수정·리팩터링 내용: `"dev": "vite --port 2000"`
- 핵심 동작: `npm run dev`가 2000 포트를 사용한다.

### 사용 기술과 구체적 목적

| 기술·구조·패턴 | 해결하려는 구체적 문제 | 적용 위치와 방식 |
| --- | --- | --- |
| Vite `--port` | 설정 파일 기본 포트 2426으로 뜨는 것 | `package.json` scripts.dev |

### 결과

- 적용 전: `npm run dev`는 `vite`만 실행해 설정 기본 포트(2426 또는 `VITE_PORT`)를 썼다.
- 적용 후: `vite --port 2000`으로 실행한다.
- 검증 결과: `package.json` 스크립트 값을 확인했다. 개발 서버는 상시 실행하지 않았다.
- 사용자 후속 피드백: 없음
- 추가 요청 및 남은 제한: `vite.config.ts` 기본 포트는 2426이다.
- 직접 측정하지 못한 수치: 측정 근거 없음

### 이력서·포트폴리오 문구

- 이력서 bullet: 로컬 Vite 개발 서버가 2000 포트에서 뜨도록 `npm run dev`에 `--port`를 고정했다.
- 포트폴리오 서술: 설정 파일 기본 포트와 로컬 실행 포트가 달랐다. 사용자가 `package.json`만 지정해 CLI `--port 2000`으로 `npm run dev`를 맞췄다.
