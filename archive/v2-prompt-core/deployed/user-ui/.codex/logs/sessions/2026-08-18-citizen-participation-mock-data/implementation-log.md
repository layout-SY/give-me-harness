# 구현 로그

## 승인된 범위

결론: 시민참여 production UI의 route-reachable 임시값을 typed MSW API 응답으로 대체했다. feature production UI 마크업과 CSS는 변경하지 않았다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/app/mocks/startMocks.ts` | 개발 환경 MSW 기본 활성화, 명시적 false/production opt-in 지원 | 별도 env 설정 없이 개발 UI가 mock API를 사용함 |
| `api/common/content.dto.ts` | 목록·상세 표시 메타데이터와 정책 stage Zod schema 추가 | mock 응답이 parser에서 제거되지 않음 |
| `api/me/me.dto.ts`, `me.api.ts` | 활동 요약·보상 응답 계약 추가 | 활동 UI metadata가 API 경계를 통과함 |
| `citizenParticipation.parser.ts`, query hook | 활동 전용 parser 연결 | 외부 응답을 typed 활동 응답으로 변환함 |
| `mocks/fixtures.ts`, `handlers.ts` | type별 표시 데이터, 정책 단계, 활동 요약, content별 댓글 추가 | UI 임시 fixture가 HTTP mock 응답으로 이동함 |
| `pages/.../presentation.ts` | author, period, stage, detail section, survey metadata를 응답에서 mapping | 빈 문자열·0 placeholder 대신 parsed 값 사용 |
| `CitizenReadDetailRoutes.tsx`, `CitizenAuxiliaryRoutes.tsx` | 정책 stages와 활동 summary/reward props 연결 | route가 API 응답을 UI props로 전달함 |

## 결정 사항

- 버튼·필터·서비스명처럼 고정 vocabulary인 정적 UI copy는 API 데이터로 이동하지 않았다.
- UI의 기존 optional prop 계약은 유지하고 production route가 항상 응답 기반 값을 전달하도록 했다.
- comment fixture는 content ID별로 분리하고 detail `commentCount`와 실제 목록 수를 맞췄다.
- backend 미확정 필드는 기존 generic content response의 optional metadata로 추가해 현재 API와 호환성을 유지했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| focused Vitest | 9 files, 29 tests 통과 |
| route DOM + 실제 MSW handlers | 정책 metadata/stages와 활동 summary/reward 렌더 통과 |
| `npm run build` | 통과; 기존 chunk size 경고만 존재 |
| `npm run lint` | 통과 |
| 레이어 상향 import 검사 | 통과 |
| 금지 TypeScript 패턴 검사 | 통과 |
| LOC 검사 | 모든 변경 파일 250 pure LOC 이하; presentation 230 LOC 경고 구간 |
| `npm test` | 145/148 통과; 범위 밖 auth 1건·meeting 2건 실패 |
| governance Python test | 19/20 통과; 범위 밖 `.gitignore`의 `AGENTS.md` 항목 1건 실패 |

## Watcher 인계

DTO/parser → MSW handler → query → pages mapper → route props 경로와 개발 MSW 기본 활성화 계약을 검토한다. `DESIGN.md`, `src/shared/api/common/dto.ts`, `.opencode/settings.json`, `docs/external-browser-deep-link-auth.md`는 다른 세션 변경으로 제외한다.
