# 최종 요약

## 제공 사항

- 제안 form의 명시적 `useWatch` controlled subscription.
- 문자 단위 입력 전체 표시·payload 회귀 테스트.
- 생성마다 다른 deterministic proposal ID와 후속 상세·목록 persistence.
- 응답 ID 그대로 상세 route 이동 검증.
- proposal test를 막던 discussion mutation 구문 오류 수정.

## 제외 사항

- production UI markup·CSS·shared UI adapter 변경.
- 브라우저 자동화와 시각 QA.
- 범위 밖 full-suite 실패 수정.

## 검증

| 명령어 | 결과 |
| --- | --- |
| focused Vitest | PASS, 4 files / 24 tests |
| final route Vitest | PASS, 2 tests |
| `npm run lint` | PASS |
| `npm run build` | PASS |
| `npm test` | 173 PASS / 범위 밖 4 FAIL |

## 산출물

- 필수 8종 문서와 `portfolio-log.md`.

## 남은 제한 사항

- 공식 Watcher와 TypeScript LSP 미사용.
- 실제 브라우저 확인은 사용자 후속 확인이 필요하다.
- 기존 bundle chunk 경고 유지.

## 다음 단계

사용자가 실제 브라우저에서 입력 누적과 생성 상세 URL을 확인한다. 증상이 남으면 HeroUI production event 경계를 별도 진단한다.
