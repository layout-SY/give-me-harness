# 검토 로그

## Watcher 판정

PASS

## 검토 범위

브라우저 MSW 시작이 `VITE_API_BASE_URL_STATUS=dev`에만 의존하는지, 기존 `VITE_ENABLE_MSW`/DEV 기본 켜짐이 제거됐는지.

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 목표 충족 | PASS | `startMocks.ts`가 `dev`가 아니면 즉시 return한다. |
| 승인 근거 | PASS | 사용자 지시 `추가해줘` 이후 구현했다. |
| 불러온 스킬 | PASS | coding-convention, type-definition, documentation을 적용했다. |
| `src/shared/ui/` 재사용 | PASS | UI 변경이 없다. |
| 타입 안전성 | PASS | `npm run build`의 `tsc -b`가 통과했다. |
| 요청 데이터 완전성 | PASS | 해당 없음. HTTP 요청 DTO가 아니다. |
| 중복/추상화 | PASS | 기존 `startMocks` 한 곳만 바꿨다. |
| 검증 | PASS | startMocks 테스트 4건, `npm run build`, `npm run lint` 성공. |
| 문서화 | PASS | 세션 산출물 8종을 이 디렉터리에 작성한다. |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 없음 | - | `dev`가 아닌데 worker가 시작되거나 `VITE_ENABLE_MSW`가 남아 있는 결함은 확인되지 않았다. | 없음 |

## 결론

현재 작업 범위에서 모의 서버 스위치를 `VITE_API_BASE_URL_STATUS`로 교체했다.
