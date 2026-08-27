# 구현 로그

## 승인된 범위

생성 POST의 error 유형 할당을 제거하고, barrel 순환 진입점을 줄인다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `api/proposal/createProposal.dto.ts` | 생성 요청/응답 타입·매퍼·Location 파서 | 목록 DTO와 분리된 완료 유형 |
| `api/proposal/proposal.api.ts` | 새 모듈에서 body 복사, Location을 `{ id }`로 변환 | 29–32행 error 할당 없음 |
| `index.ts` | 생성 DTO·`parseCreateProposalResponse` 재export 제거 | barrel이 생성 계약을 다시 묶지 않음 |
| `CitizenMainRoute.tsx` 등 pages | barrel 대신 훅·페이지 깊은 경로 | 순환 진입점 제거 |
| presentation 테스트 | parser 직접 import | 테스트가 barrel을 로드하지 않음 |

## 결정 사항

- `postProposal`이 Location을 `{ id }`로 바꿔 돌려서 mutations가 god parser를 `.then`하지 않는다.
- 투표 `.then(parseVoteResponse)`는 이번 오류 위치가 아니라 그대로 둔다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| ReadLints `proposal.api.ts` | 오류 없음 |
| `npx eslint` 변경 경로 | 성공 |
| `npx vitest run` citizen-participation | 12 files / 71 tests passed |

## Watcher 인계

현재 변경은 타입 해석과 import 경계다. UI 시각 QA는 없다.
