# 최종 요약

## 제공 사항

- ProposalStatus: `RECEIVED`, `UNDER_REVIEW`, `ADOPTED`, `REJECTED`
- VoteChoice: `AGREE`, `DISAGREE`
- OpinionStance: `AGREE`, `DISAGREE`, `NEUTRAL`
- 세 집합의 독립 `as const`와 파생 타입
- uppercase API request/response/detail parser와 stateful MSW
- production UI lowercase 값과의 route adapter
- ProposalStatus 표시와 fixture·테스트 migration

## 제외 사항

- 미확정 Vote·Discussion·Policy·Survey lifecycle status
- production UI 직접 수정
- 범위 밖 auth·meeting 실패 수정

## 검증

| 명령어 | 결과 |
| --- | --- |
| focused Vitest | 5 files, 31 tests PASS |
| `npm run lint` | PASS |
| `npm run build` | PASS |
| `npm test` | 162 PASS, 범위 밖 3 FAIL |
| Node 모듈 실행 | 세 uppercase 상수 객체 확인 |

## 남은 제한 사항

- TypeScript LSP는 미설치·설치 거절 상태다.
- no-excuse 전용 스크립트는 Bun 미설치와 Node 실행 제한으로 수행하지 못했다.
- 전체 suite의 기존 auth 1건·meeting 2건 실패가 남아 있다.
- `fixtures.ts` 246 LOC, `presentation.ts` 236 LOC로 다음 확장 전 분리가 필요하다.
