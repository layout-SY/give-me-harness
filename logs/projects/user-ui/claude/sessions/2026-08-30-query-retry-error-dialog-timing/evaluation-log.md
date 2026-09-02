# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher의 최종 PASS를 다시 평가하지 않는다. 현재 구현 결함이 아니라 장기 유지보수 관점만 기록한다.

## 장기 관찰 사항

- `src/app/providers/queryClient.ts`가 전역 retry 정책의 단일 진입점이므로 새로운 상태별 예외는 개별 query가 아니라 이 경계와 표 기반 테스트에서 함께 갱신하는 것이 적합하다.
- `CitizenDataRoutes.test.tsx`의 observer 수와 `fetchStatus` 검증은 화면 텍스트보다 query 생명주기를 직접 보호한다.

## 목록에 등록할 재사용 가능 자산

- 등록할 공용 재사용 자산은 없다.
- 지연 요청 구성은 현재 시민참여 메인 route와 query key에 밀접하므로, 같은 검증이 다른 route에서 반복되기 전에는 범용 helper로 추출하지 않는다.

## 기술 부채

- `CitizenDataRoutes.test.tsx`는 순수 LOC 238줄로 경고 구간에 진입했다. 다음 lifecycle 테스트 추가 시 파일 분리를 재평가한다.
- Vite production bundle의 500 kB 초과 청크 경고는 이번 변경이 만든 결함이라는 근거가 없으므로 별도 성능 작업에서 측정 목표를 정한 뒤 다룬다.
- TypeScript LSP 미사용은 사용자 거절에 따른 도구 가용성 제한이며 제품 결함이 아니다.

## 프로세스 개선 사항

- retry 변경 시 `unknown`, `transport`, `5xx`, `4xx`, `client-contract`, `canceled`별 시도 횟수와 terminal 보고 시점을 표 테스트에서 유지한다.
- 브라우저 API interception은 이탈 대상 route의 후속 API까지 격리해야 CORS 잡음 없이 콘솔을 판독할 수 있다.

## 권고 사항

- 다음 retry 정책 변경은 `queryClient.test.ts`의 경계 표를 먼저 확장한다.
- 다음 시민참여 route lifecycle 테스트 추가 시 `CitizenDataRoutes.test.tsx`의 238 LOC를 재평가한다.
- 현재 근거만으로는 추가 추상화, 즉시 리팩터링 또는 PASS 변경이 필요하지 않다.
