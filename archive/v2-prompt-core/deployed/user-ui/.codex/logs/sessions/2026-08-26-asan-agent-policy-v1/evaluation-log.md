# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- 동일 정책의 host별 표현은 adapter로 한정했지만 Codex·Claude 역할 문서의 내용 차이는 여전히 크다.
- user-ui와 admin-ui가 중앙 산출물을 Git에서 ignore하면 새 clone에는 bootstrap sync가 필수다.
- Claude UI 전담 계약 때문에 host 선택이 작업 능력의 완전한 상호 교환을 뜻하지 않는다.

## 목록에 등록할 재사용 가능 자산

- source digest와 파일별 SHA-256 manifest
- 세 host 공용 managed-file guard 판정 로직
- OpenCode local plugin runtime smoke test

## 기술 부채

- 프로젝트별 overlay는 V1에서 지원하지 않는다.
- legacy 최초 퇴역은 정적 감사 snapshot에 의존하며 동시 변경 시 사용자 판단이 필요하다.
- adapter에 user-ui baseline 역할·워크플로 파일이 다수 남아 있으므로 후속 단순화 후보가 있다.

## 프로세스 개선 사항

- 중앙 변경은 commit → audit/test → diff → 배포 승인 → sync → check → handoff/restart 순서로 고정한다.
- 커밋 메시지는 영어 type과 한글 요약을 사용한다.

## 권고 사항

- 첫 배포 뒤 두 프로젝트에서 `check`와 consumer governance test를 실행한다.
- overlay는 실제 첫 차이가 생긴 뒤 최소 계약으로 도입한다.
- 중앙 산출물을 Git ignore할지, bootstrap을 CI/setup script에 넣을지 별도 결정한다.
