# 포트폴리오 경험 기록

## 문제
- **UX/접근성**: 잘못된 종료일을 입력해도 detail 저장 버튼이 활성처럼 보였고 input에 `aria-invalid`가 없어 오류 상태가 보조 기술에 직접 노출되지 않았다.
- **시각 품질**: 12px 오류 문구 색 `#f31700`은 흰색에서 `4.2566:1`로 WCAG AA `4.5:1`에 미달했다.
- **제약**: shared navigation/token/Dialog/Button과 non-T03 source를 수정할 수 없었다.

## 고민 과정
| 접근법 | 장점 | 단점 | 채택 |
|---|---|---|---|
| shared input/button/token 변경 | 전역 일관성 개선 가능 | 승인 범위 위반, 큰 blast radius | 아니오 |
| 오류 문구만 유지 | 변경 최소 | accessibility state와 action affordance 불일치 지속 | 아니오 |
| 기존 `isClosedAtValid`를 aria와 disabled에 연결하고 로컬 token만 조정 | 단일 source of truth, 범위 준수 | shared 이슈는 별도 deferred 필요 | 예 |

**판단 기준**: 사용자 범위 준수, invalid 상태의 시각·접근성·network behavior 일치, 최소 blast radius.

## 결과

### 결과 1: invalid state 계약 통합
- conditional `aria-invalid`, 기존 `aria-describedby`/`role=alert`, save disabled를 `isClosedAtValid`에 연결했다.
- **도출 이유**: 동일 오류가 보조 기술, 사용자 affordance, 요청 차단에서 서로 다르게 표현되지 않도록 하기 위해서다.

### 결과 2: T03-local 오류 대비 개선
- 오류색을 `#d91500`으로 변경했다.
- **도출 이유**: shared token 변경 금지 조건을 지키며 12px AA 대비를 충족하기 위해서다.

### 결과 3: fresh visual evidence 강화
- updated/invalid input과 활성/비활성 save를 한 프레임에 담은 1440/1024 캡처를 포함해 총 9개 PNG를 생성했다.
- **도출 이유**: 이전 Visual QA blocker가 단순 DOM이 아니라 실제 시각 affordance에 관한 것이었기 때문이다.

## 성과
- 오류 문구 대비: `4.2566:1` → `5.1755:1`.
- invalid detail 요청: POST 0회; corrected rapid save: POST 정확히 1회.
- invalid list 요청: GET 0회; reset 후 corrected flow: GET 1회.
- 9/9 PNG signature·dimensions·hash 확인.
- 독립 Visual QA Pass A/B 모두 PASS, blocking finding 0.
- scoped ESLint, TypeScript build, production build PASS.

## 회고
- 접근성 속성만 추가하거나 버튼만 비활성화했다면 상태 불일치가 남았을 것이다. 하나의 validation source of truth를 aria, affordance, network suppression에 연결한 것이 핵심이었다.
- 상태 증거는 화면 상단 고정 캡처보다 문제의 입력·문구·버튼이 동시에 보이는 scroll 위치가 더 강한 검증 자료가 된다.
- shared 문제를 무리하게 함께 고치지 않고 deferred risk로 명시해 범위와 책임을 분리했다.

[세션 최종 요약](../../sessions/2026-08-21-cp-t03-discussion-api/final-summary.md) · [DoneClaim](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/done-claim.json)
