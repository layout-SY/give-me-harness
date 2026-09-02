# 구현 로그

## 승인된 범위

제안 작성 controlled input 구독, 생성 ID 발급·상세 이동, 테스트 차단 구문 오류를 수정한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `useCitizenParticipationMutations.ts` | discussion detail/list invalidation을 `Promise.all`로 묶음 | Vite parser와 mutation callback 복구 |
| `CitizenAuxiliaryRoutes.tsx` | `form.watch()` 대신 `useWatch({ control })` 구독과 완전한 기본값 계약 적용 | controlled UI에 최신 form 값 전달 |
| `CitizenProposalWriteRoute.test.tsx` | StrictMode·문자 단위 입력·전체 POST body·응답 ID 이동 검증 | `qweetedf` 전체 표시·제출 고정 |
| `mocks/handlers.ts` | fixture 충돌을 건너뛰는 증가형 `proposal-N` 발급 | 생성마다 실제로 다른 ID 반환·저장 |
| `mocks/handlers.test.ts` | 연속 2회 생성·ID 차이·각 상세·목록 순서 검증 | fixed `proposal-created` 회귀 차단 |

## 결정 사항

- production UI props/callback은 변경하지 않는다.
- HeroUI event adapter는 공식 v3 계약과 route test가 정상이라 유지한다.
- 실제 backend 응답 ID는 route가 그대로 사용하며, mock 환경만 deterministic 생성 ID로 현실화한다.
- random UUID 대신 fixture 충돌을 검사하는 증가형 ID를 사용해 테스트 재현성을 유지한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| 기존 proposal route test | parser 복구 후 2 PASS |
| 동적 ID targeted test | RED: 두 ID 모두 `proposal-created` |
| proposal focused suite | 4 files / 24 tests PASS |
| 최종 route 재검증 | 2 tests PASS |
| `npm run lint` | PASS |
| `npm run build` | PASS, 기존 chunk 경고 |
| `npm test` | 173 PASS / 범위 밖 4 FAIL |

## Watcher 인계

- 공식 Watcher는 Anthropic API 크레딧 부족으로 실행되지 않았다.
- TypeScript LSP는 설치 거절 상태라 lint/build로 대체했다.
