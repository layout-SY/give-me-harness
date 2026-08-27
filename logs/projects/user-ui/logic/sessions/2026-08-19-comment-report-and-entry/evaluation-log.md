# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- 시민참여 route는 인증 guard 없이 공개돼 있어 기능별로 `/me` 성공 여부를 주입해야 한다.
- 댓글·신고 상태는 투표·토론·정책반영 세 화면에서 같은 생명주기를 공유한다.
- 제안 UI의 `background`와 API의 `body`는 명칭이 달라 mapper 경계를 유지해야 한다.

## 목록에 등록할 재사용 가능 자산

- `useCitizenCommentActions`: 세 상세 화면에서 공유하는 기능 내부 재사용 hook으로 유지한다.
- `createCommentHandlers`: 댓글 조회·등록·좋아요·신고의 독립적인 MSW 상태 경계다.
- `useProposalForm`, `toCreateProposalRequest`: 제안 UI 검증과 API payload 변환 경계다.

## 기술 부채

- 실제 backend 댓글 신고 request 계약이 저장소 문서에 없다.
- 인증 상태를 앱 전역에서 표현하는 reactive session store나 route guard가 없다.
- production bundle에 500 kB 초과 chunk 경고가 있다.
- 전체 회귀에는 이번 범위 밖 auth query 이동 1건과 meeting API URL 보안 2건이 실패한다.

## 프로세스 개선 사항

- backend 계약 확정 시 신고 endpoint와 body를 문서화한다.
- 공식 Watcher 실행 환경의 외부 API 크레딧 가용성을 검토 전에 확인한다.

## 권고 사항

현재 범위에서는 전역 인증 구조나 bundle 분할을 새로 만들지 않는다. 인증 구조, 기존 전체 회귀 3건, code splitting은 각각 독립 작업으로 다룬다.
