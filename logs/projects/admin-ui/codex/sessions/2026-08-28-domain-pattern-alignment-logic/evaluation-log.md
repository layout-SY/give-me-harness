# 평가 로그

## 현재 판정과의 경계

- 여기서는 Watcher PASS를 다시 평가하지 않는다.
- Evaluator 세션 `ses_fb9a4f29dffeZpFqq53Dt5jOMu`는 현재 차단 요인이 없다고 판정했다.
- 아래 항목은 현재 branch 결함이 아니라 장기 아키텍처·프로세스 권고다.

## 장기 관찰 사항

- 공용 날짜 schema는 discussion/vote가 동일 의미와 변경 압력을 공유해 현재 추상화 근거가 충분하다.
- 입력 strictness와 응답 forward compatibility를 분리한 구조가 유지보수 경계를 명확히 한다.
- board 응답 parser를 API 계층에 모으면서 hook이 상태 조율에 집중하게 됐다.

## 목록에 등록할 재사용 가능 자산

- 후보: `src/shared/lib/validation/index.ts`의 `isoCalendarDateSchema`.
- 후보: `src/entities/cp-board/api/cp-board.parser.ts`의 공개 응답 parser 패턴.
- 이번 branch에서는 `.codex/memory/reusable-assets.md`를 변경하지 않는다. 다른 도메인 사용처가 실제로 추가될 때 등록을 검토한다.

## 기술 부채

- CP DTO 회귀 테스트가 명시적 schema 목록을 사용하므로 신규 DTO가 자동 편입되지 않는다.
- bulk-hide parser는 검증하지만 React Query cache update/invalidation callback 자체를 실행하는 자동 테스트는 없다.
- repository full lint에 기존 오류 73건과 경고 5건이 있고 `package.json`에 표준 `test` script가 없다.

## 프로세스 개선 사항

- P1: CP query/process 입력 schema 계약을 parameterized matrix로 관리한다.
- P1: 별도 package/config 작업에서 실제 Vite 모듈 테스트의 표준 진입점을 만든다.
- P2: bulk-hide mutation의 detail cache update와 list invalidation을 QueryClient 수준에서 고정한다.
- P3: 공용 validation 항목이 늘어날 때만 파일 분리를 검토한다. 현재 3줄 모듈에는 추가 추상화가 필요 없다.

## 권고 사항

- 현재 commit·merge를 차단하지 않는다.
- P1~P3는 사용자 승인과 별도 브랜치에서 처리한다.
- UI Todo 5~7는 사용자 최신 지시에 따라 Claude Code를 사용하지 않고 별도 GPT Sol 브랜치 승인 후 진행한다.
