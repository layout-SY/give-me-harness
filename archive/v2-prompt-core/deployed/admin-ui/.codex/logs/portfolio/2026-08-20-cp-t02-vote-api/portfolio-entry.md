# 포트폴리오 경험 기록

## 작업 개요
Vote 목록·상세·처리 수직 slice의 closure를 evidence 기반 문서로 정리했다. 작업 유형은 documentation-only다.

## 문제 상황
- 출처: 구조적 위험과 승인 계획. fixture 기반 화면을 API/query/cache 경계로 전환한 결과를 정확히 닫아야 했다.
- 실제 backend 호환성·auth는 범위 밖이며 측정하지 않았다.

## 요구사항 및 의사결정
| 접근법 | 장점 | 선택 |
|---|---|---|
| 기존 evidence만 구조적으로 요약 | 추적성·무결성 유지 | 채택 |
| 새 QA나 제품 수정 수행 | 추가 정보 가능 | 미채택: 범위 위반 |

## 사용 기술과 목적
| 기술/패턴 | 목적 |
|---|---|
| `ApiResult<unknown>` → unwrap → Zod | transport 경계의 검증 사실 기록 |
| TanStack Query cache update/invalidation | POST 후 list/detail 일관성 기록 |
| stateful MSW | local provisional operation 근거 |

## 적용 내용
2 routes, 3 provisional operations, 2 save controls와 source→render 흐름을 기록했다. 목록·상세 저장은 pending guard로 exactly-one POST이며 후속 GET으로 확인됐다.

## 결과 및 성과
- 16/16 hash match, pure LOC 최대 159, 정상 console/unhandled 0을 evidence-linked로 기록했다.
- 400/404/500/malformed-success와 cleanup을 분리 기록했다.
- attempt 1 billing `not-run`은 코드 실패로 해석하지 않았다.

## 잔여 리스크
provisional backend contract, auth/permission, LSP unavailable, 기존 build chunk warning. 장기 Evaluator는 deferred다. reusable-assets update는 N/A다.

## 회고
문서 closure에서는 측정된 local/mock 결과와 측정하지 않은 backend compatibility를 분리하는 것이 핵심이다.

[세션 최종 요약](../../sessions/2026-08-20-cp-t02-vote-api/final-summary.md) · [Watcher](../../../../.omo/evidence/cp-admin-api-remediation/t02/watcher/attempt-2/adversarial-verify.json)
