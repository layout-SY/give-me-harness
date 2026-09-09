# 평가 로그

## 결론

현재 작업의 Watcher PASS와 `sy-main@25f41f2` 병합 결과를 유지한다. 아래 내용은 병합을 차단하지 않는 장기 권고다.

## 장기 관찰

1. 전역 API 실패 경계가 하나의 정책 축으로 수렴했다.
   - `ApiFailure`가 server·client-contract·transport·canceled를 분류한다.
   - Axios는 정규화하고 `useApi`·TanStack Query가 terminal reporting을 담당한다.
   - app bridge가 shared queue와 기존 Dialog를 결합한다.
2. 인증 수명주기와 비동기 경쟁 방지가 한 기능 모듈에 모였다.
   - `auth-session.ts`가 token presence, commit·clear, revision guard, URL bootstrap을 소유한다.
   - sign-in 401과 refresh 401의 의미를 typed behavior로 분리한다.
3. 기반과 production 화면 통합은 의도적으로 구분됐다.
   - `/sign-in` UI와 보호 route 활성화는 현재 범위의 결함이 아니라 후속 통합 작업이다.

## 재사용 가능 자산 후보

| 후보 | 재사용 가치 | 권고 |
| --- | --- | --- |
| `src/shared/api/error/**` | taxonomy, redaction, terminal claim, 401 정책, FIFO queue | API terminal failure policy로 등록하되 raw error 비전달 계약을 함께 기록한다. |
| `src/features/auth/model/auth-session.ts` | token write·clear·presence·revision·bootstrap 단일 경계 | feature 소유권을 유지하고 사용처 수만으로 shared로 올리지 않는다. |
| `src/app/providers/api-error-dialog-bridge.tsx` | shared 생산자와 UI/auth side effect 분리 | app-level adapter 패턴으로 기록한다. |
| `src/entities/auth/api/**` | injectable transport, signal, Zod parser | 후속 auth endpoint의 도메인 예제로 사용한다. |

## 기술 부채

1. Vite/Rolldown native child의 비결정적 `SIGBUS`
   - 전체 suite의 실패 파일과 통과 여부가 cache·concurrency 조건에 따라 이동했다.
   - 별도 인프라 작업에서 outer launcher, native child lifecycle, Node scheduling을 격리한다.
2. no-excuse helper와 TypeScript 6.0.2 호환성
   - 프로젝트에 없는 `typescript/unstable/*` import를 안정 API 또는 version adapter로 정렬한다.
3. 저장소 전체 lint 기준선
   - 기존 71 errors·5 warnings를 현재 기능 diff와 섞지 않고 별도 부채 작업에서 줄인다.
4. diagnostics allowlist 유지 비용
   - 새 API surface마다 operation·source·path 어휘와 redaction 테스트 갱신 여부를 확인한다.

## 우선순위 권고

- P1: Claude UI handoff 이후 `/sign-in`, 보호 route, `returnTo`를 현재 auth-session·401 계약에 연결한다.
- P1: Vite/Rolldown native child `SIGBUS`를 별도 인프라 작업으로 격리한다.
- P2: no-excuse helper를 TypeScript 6과 정렬한다.
- P2: whole lint 기준선을 소유 경로·규칙별로 분리한다.
- P3: API failure와 auth-session 자산을 재사용 목록에 등록한다.
