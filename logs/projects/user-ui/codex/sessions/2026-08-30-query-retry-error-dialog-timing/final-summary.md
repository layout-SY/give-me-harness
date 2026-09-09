# 최종 요약

## 제공 사항

- 4xx query failure의 불필요한 retry 제거
- 5xx·transport·unknown failure의 기존 1회 retry 보존
- 404 RED→GREEN 회귀 테스트
- 시민참여 메인 route 이탈 시 query 비활성 복원 테스트
- 실제 브라우저에서 404 단일 요청·Dialog와 네트워크 abort 확인

## 제외 사항

- Dialog queue·dedupe 정책 변경
- production UI 변경
- mutation retry 변경
- bundle 분할

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npm run build` | 성공, 기존 대형 청크 경고 |
| `npm run lint` | 통과 |
| `npm run test` | Vitest 454개·governance 20개 통과 |
| targeted Vitest | 17개 통과 |
| Playwright | 404 요청 1회·Dialog 표시, route 이탈 `net::ERR_ABORTED`·Dialog 0개 |

## 산출물

- production retry 정책 1개 파일
- 회귀 테스트 2개 파일
- 현재 디렉터리의 필수 8종 문서

## 남은 제한 사항

- TypeScript LSP는 설치 거절 상태라 실행하지 못했고 `tsc -b`로 대체했다.
- Vite 청크 크기 경고는 기존 상태로 남아 있다.
- `CitizenDataRoutes.test.tsx`는 순수 LOC 238줄의 경고 구간이다.

## 다음 단계

- Watcher 최종 PASS와 Evaluator 기록을 포함한 변경 diff를 바탕으로 commit·merge 승인을 요청한다.
