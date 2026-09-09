# 평가 기록 (Evaluator)

현재 변경의 통과 여부는 `review-log.md` 가 판정한다. 여기에는 이번 범위 밖의 장기 개선 항목만 남긴다.

## 1. 라우트 보호 미적용 (우선순위: 높음)

`private-route.tsx` 와 `role-based-route.tsx` 가 구현되어 있으나 `routes.tsx` 에서 사용되지 않는다.
로그인 화면이 생긴 지금이 `/cp` 라우트에 `PrivateRoute` 를 연결하기 좋은 시점이다.
연결 시 개발 편의(로그인 없이 화면 확인)와 충돌하므로, mock 환경에서의 우회 방식을 함께 결정해야 한다.

## 2. 로그인 후 원래 목적지 복원 없음 (우선순위: 중간)

현재는 성공 시 항상 `/cp/dashboard` 로 이동한다.
`PrivateRoute` 를 연결하게 되면 `<Navigate to="/sign-in" state={{ from: location }} />` 로 목적지를 넘기고
로그인 후 그 경로로 돌아가는 흐름이 필요하다. 두 변경은 같은 작업으로 묶는 편이 낫다.

## 3. `shared/ui/text-input` 의 초기 렌더 타입 (우선순위: 중간)

`_isShow` 초기값 `true` + `useEffect` 로 `false` 전환 구조라 비밀번호 입력이 첫 프레임에 `type="text"` 로 렌더된다.
값이 비어 있어 실제 노출은 없지만, `useState(!enableShow)` 로 초기화하면 effect 자체가 불필요해지고
현재 lint 가 지적 중인 `react-hooks/set-state-in-effect` 도 해소된다. 공용 컴포넌트라 별도 scope 승인이 필요하다.

## 4. 폼 검증 공용 어댑터 부재 (우선순위: 낮음)

`shared/ui/form/index.ts` 는 react-hook-form 기반 `FormField` 계약만 주석으로 남은 placeholder 다.
로그인처럼 필드가 2개인 화면은 controlled state 로 충분하지만, 필드가 늘어나는 폼이 추가되기 전에
패키지 설치와 어댑터 구현 여부를 결정해야 화면마다 검증 방식이 갈라지지 않는다.

## 5. 저장소 전체 lint 부채 (우선순위: 낮음)

`npm run lint` 가 68 error / 5 warning 상태다. 이번 변경과 무관하지만 누적되면
"신규 경로만 깨끗한지" 를 매번 수동으로 걸러내야 해서 검증 신뢰도가 떨어진다. 별도 정리 작업 권장.
