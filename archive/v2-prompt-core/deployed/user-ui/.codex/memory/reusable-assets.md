# 재사용 가능 자산

## 공용 UI

| 그룹 | 자산 | 계약 출처 |
| --- | --- | --- |
| 입력/액션 | button, icon-button, text-input, text-area, dropdown, toggle-switch | `.agents/skills/reference/components/COMMON_COMPONENTS.md` |
| 목록 | table, pagination, search-state-bar, no-results, loading | `.agents/skills/reference/components/COMMON_COMPONENTS.md` |
| 오버레이 | dialog, modal, side-modal, popup, reason-prompt | `.agents/skills/reference/components/COMMON_COMPONENTS.md` |
| 미디어 | image-modal, image-upload, fade-in | `.agents/skills/reference/components/COMMON_COMPONENTS.md` |
| 표현 | author, category, status | `.agents/skills/reference/components/COMMON_COMPONENTS.md` |
| 폼 기반 | form | `.agents/skills/reference/components/COMMON_COMPONENTS.md` |
| 날짜 | date-range-picker | `.agents/skills/reference/components/COMMON_COMPONENTS.md` |

위 7개 분류는 `src/shared/ui/`의 현재 24개 그룹을 모두 포함한다.

## 훅과 유틸리티

| 자산 | 경로 | 책임 |
| --- | --- | --- |
| `useApi` | `src/shared/lib/hooks/use-api.tsx` | 비동기 실행, 로딩, 오래된 결과 방지, 오류 표시 |
| `useFetchAdapter` | `src/shared/ui/table/hooks/useFetchAdapter.ts` | 페이지네이션 `Table` 데이터 조회 바인딩 |
| 발행-구독 | `src/shared/lib/pub-sub/` | 타입이 지정된 컴포넌트 간 이벤트 |
| 날짜 유틸리티 | `src/shared/lib/utils/date.util.ts` | 현지 시간대 날짜와 기간 표시값 정규화 |
| 토큰 유틸리티 | `src/shared/lib/utils/token.util.ts` | JWT 만료 정보 해석과 활성 상태 판정 |
| 성능 유틸리티 | `src/shared/lib/utils/performance.util.ts` | `debounce`와 `throttle` 실행 제어 |
| 색상 유틸리티 | `src/shared/lib/utils/selectColor.ts` | 숫자 식별자 기반의 안정적인 테마/아바타 색상 선택 |
| 애니메이션 완료 유틸리티 | `src/shared/lib/utils/complete-after-animation.ts` | 애니메이션 종료·취소·미실행 시 완료 콜백과 정리 보장 |
| 이미지 출처 보안 정책 | `src/shared/lib/security/imageOriginPolicy.ts` | 현재/API/명시 허용 출처의 안전한 이미지 URL만 승인 |
| 공용 유효성 검사 진입점 | `src/shared/lib/validation/index.ts` | 도메인 중립 검증기의 공개 경계이며 현재 예약 상태 |
| API 클라이언트/결과 | `src/shared/api/api-client.ts`, `src/shared/api/axios-instance.ts`, `src/shared/api/common/api-result.ts`, `src/shared/api/common/api-result/` | Axios 요청 경계와 정규화된 `ApiResult` |
| API 값 검사기 | `src/shared/api/common/util/type-validator.ts` | 알 수 없는 API 값을 레코드·숫자·불리언·문자열로 안전하게 좁힘 |

`src/features/meeting/`은 공용 프리미티브가 아니라 기능 내부에서 재사용하는 단위다. API 파싱, Agora 수명 주기, 참여자/미디어 훅과 반응형 UI를 담당한다.

## 반복 반려 패턴

아직 등록된 패턴이 없다.

## 아키텍처 결정과 기술 부채

- HeroUI와 React Aria는 계속 `src/shared/ui` 어댑터 뒤에 격리한다.
- Meeting은 현재 애플리케이션 루트이며, 라이브 세션에는 `VITE_API_BASE_URL`과 서버에서 발급한 Agora 자격 증명이 필요하다.
- meeting 스타일시트는 기능 내부에 유지하며, `DESIGN.md`에서 수용된 분리 부채로 추적한다.
