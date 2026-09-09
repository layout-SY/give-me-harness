# 사용자 요청에 따른 중앙 직접 자식 병합

## 실행 근거와 범위

사용자의 “너가 그냥 임의로 merge 해주면 안돼?” 요청에 따라 중앙 관리 세션에서 아래 두 자식→부모 병합을 직접 실행했다. 기존 부모 세션으로 가장하거나 host·role·assignment 환경을 바꾸지 않았다. 일반 inject 정책을 완화한 변경도 아니다.

실행 전 네 worktree의 clean 상태, 직접 부모 계보, 양쪽 V3 계약·HEAD·Git claim, 부모의 미확인 도구 예약과 진행 중인 통합 예약 부재를 확인했다. 정확한 source HEAD를 대상으로 `git merge --ff-only`만 실행했다. 실제 소비자 쓰기는 도구의 권한 승인 후 수행했다.

검토한 [계획 원본](operations/2026-09-09-child-merges.plan.json)의 SHA-256:

```text
0733fb27efc9250fb7be2e99a3fb9d5999843c0a93a541b650bdce4b0c091218
```

[실행 결과 원본](operations/2026-09-09-child-merges.result.json)도 함께 보관한다. 이 기록은 중앙 사용자 위임 작업이며 소비자 세션의 SHA 승인 이력을 대신하거나 성공한 hook 결과를 생성하지 않는다.

## 병합 결과

| 프로젝트 | 자식 → 부모 | 부모 HEAD 변경 | lint | build | 자식 상태 |
| --- | --- | --- | --- | --- | --- |
| user-ui | `task/reservation-mock-logic` → `task/reservation-detail-ui` | `b5b07fab0a0f93cf1b1423d8ee2cc1a7088377ac` → `2184467e3270acd2d49f7652122999fc1e8061f6` | PASS | PASS | CLOSED |
| admin-ui | `task/news-management-logic` → `task/news-management-ui` | `49aa7392882479dcb6fb08eacd73fc432d2af726` → `6f1d322c5e14802a0d7504d9d83890bfda215b92` | FAIL: 68 errors, 5 warnings | PASS | READY_TO_MERGE |

각 부모 worktree에서 `npm run lint`와 `npm run build`를 실제로 실행했다. user-ui는 모두 exit 0이다. admin-ui는 lint exit 1, build exit 0으로 기존 보고와 같은 lint 문제가 남았다. 실패를 검증 완료로 기록하지 않았다.

user-ui 자식에는 `closure_kind: user_delegated_central`, `verification_status: passed`, 위 operator SHA를 연결한 CLOSED 기록을 남겼다. 자식 Git claim만 해제했다. admin-ui 자식은 병합되었지만 검증 미완료이므로 READY_TO_MERGE와 기존 자식 claim을 유지했다. 두 프로젝트의 일회성 중앙 실행 예약은 작업 종료 후 제거했다.

## 보존된 작업 경계

- 부모 `task/reservation-detail-ui`와 `task/news-management-ui`는 모두 ACTIVE이며 원래 UI assignment의 Git claim을 유지한다.
- user-ui 부모 owner: `98fa9835fbc24050a5d9765a1901d1e8`.
- admin-ui 부모 owner: `f14c4487b1bc4431a3ac89583753fad6`.
- user-ui sy-main은 `c79f3d8c74c0536fa2d3afb983fb2e121742f076`, admin-ui sy-main은 `5834f920fcceadbe79491791d5cf8a35ca7e2a98`로 유지했다.
- 네 worktree 모두 사후 clean 상태다. branch·worktree·세션 산출물은 삭제하지 않았고 push는 실행하지 않았다.
- 기존 자식의 결과 미확인 apply_patch 예약은 임의로 성공·취소 처리하지 않았다. user-ui CLOSED는 실행한 병합과 lint·build 결과를 근거로 한다.

## 다음 작업

이번 병합 결과를 사용하기 위해 기존 부모 UI 세션을 새로 열 필요는 없다. 기존 UI 담당자는 실제 Git HEAD와 이 결과를 확인한 뒤 해당 부모 branch에서 작업을 이어갈 수 있다.

admin-ui 자식의 close에는 실패한 lint 처리와 검증 완료가 남아 있다. 과거 source 담당자용 finish 계약은 target HEAD가 이미 변경되었으므로 그대로 다시 실행하지 않는다. 이번 실행을 일반 finish가 수행했다고 가정하여 같은 SHA의 verify·close를 실행하지 않고, 중앙 사용자 위임 실행 기록에 따라 후속 검증·종료를 처리한다.

향후 다른 자식 병합에 새 부모 완료 정책을 사용하려면 새 inject bundle이 필요하다. 이는 이번 중앙 직접 병합 결과와 별도다.

원본 실행 로그는 중앙 `state/operator-merges/0733fb27efc9250fb7be2e99a3fb9d5999843c0a93a541b650bdce4b0c091218/`에 프로젝트별 merge·lint·build 로그로 보존한다.
