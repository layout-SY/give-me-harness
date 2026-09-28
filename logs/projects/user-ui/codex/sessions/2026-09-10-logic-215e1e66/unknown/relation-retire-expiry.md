# 관계 기록 보정 승인 후 실행 예약 만료 재발

## 후속 결과

사용자가 삭제 재개와 동일 명령 실행을 다시 승인한 뒤 작업 367e1a7a는 exit 0·done으로 성공했다. 예약 후속 branch는 graph에서 deleted=true로 정합화됐다. 현재 남은 작업은 최종 resume 정리 88ff206fd2364580ba99ef13468bd6f6의 승인과 실행이다. 아래는 당시 예약 만료의 진단 이력이며 현재 관계 보정은 완료됐다.

## 결론

사용자가 작업 `367e1a7a09c74ea3a71d33b42cb237b8`을 명시적으로 승인했고 PreToolUse도 일치하는 실행 예약을 생성했다. 실제 실행 진입은 예약 생성 후 123.536235초로, 보호 실행기의 120초 유효기간을 초과했다. 따라서 관계 보정은 수행되지 않았으며 승인 누락이나 Git 변경 충돌이 원인이 아니다. 같은 원인으로 재승인·재시도를 반복하지 않는다.

## 실행과 읽기 전용 증거

- 실행: 바인딩된 git_operations.py의 `execute 367e1a7a09c74ea3a71d33b42cb237b8`, python3 -I, 프로젝트 root workdir, require_escalated.
- 실제 프로세스 결과: exit 2, `Git 작업: 이 작업의 사용자 승인과 도구 실행 예약이 필요합니다.`
- operation은 stage prepared, authorized=null이다. 실제 관계 수정 전에 실패했다.
- grant fingerprint와 operation fingerprint: `b8fb2eeb88a081aa95b7584185df9469213909477b4156800eb8ed58961c2fd4`로 동일하다.
- grant host codex, assignment 215e1e66acfb48adad6983a207398c98, cwd는 현재 프로젝트 root로 모두 일치한다.
- grant created_at: 1789046893.9376; 파일 mtime: 1789046893.9378984.
- 최초 생성된 operation-367e1a7a09c74ea3a71d33b42cb237b8.lock의 mtime: 1789047017.473835.
- lock mtime - grant created_at: 123.53623509407043초. 예약 검사보다 먼저 operation lock을 생성한다.
- 현재 bundle git_operations.py:500은 `state.read(grant_path, max_age=120)`을 사용하고 501–502행에서 관측된 오류를 발생시킨다.
- 예약 생성과 실제 프로세스 사이에 호스트 권한 대기 구간이 있었으나 지연 세부 구성을 측정하지 않아 특정 구간이 전부 원인이라고 단정하지 않는다.
- 이전 a2299069 작업에서도 130.597192초 지연으로 같은 오류가 발생했다. 상세는 approval-expiry.md에 있다. 이후 개별 작업은 성공했지만 이번에 재발했다.

## 보존된 실제 상태

- sy-main: badf615ec74a435e9710774a51253a081e6db26d, tracked clean. resume 병합과 lint·build 통과 완료.
- 기존 task/citizen-discussion-api 브랜치: 삭제 완료.
- task/citizen-discussion-api-resume 브랜치: 32e2265e3581a2bc0590ff01f935ebc1e61423a0, 아직 존재.
- 두 시민 토론 worktree: 기존 커밋에 detached 상태로 남아 있으며 파일·로그 보존.
- graph revision 8. 외부에서 삭제된 task/reservation-detail-followup은 graph에 deleted=false로 남아 있음.
- 이번 실패로 refs·관계 기록·앱 소스에 변경이 생기지 않았다. grant·승인·lock·정책 파일을 직접 수정하거나 삭제하지 않았다.

## 필요한 후속 조치

현재 user-ui Logic 세션에서는 읽기 전용 정책 snapshot과 중앙 정책 저장소를 수정할 수 없다. 별도 중앙 정책 프로젝트 세션에서 호스트 권한 대기와 실행 예약 유효기간의 정합성, 승인됐지만 미실행된 작업의 재예약 경로를 보정해야 한다. 재현 회귀 테스트는 정상 승인과 승인 후 120초 초과 지연, 실제 미실행 확인, 동일 작업 중복 실행 방지를 검증해야 한다.

정책 보정 적용은 새 inject 세션에서 이 handoff를 읽고 시작한다. user-ui의 실제 관계·refs를 다시 확인하고 필요하면 정식 relation retire로 예약 후속 브랜치 기록을 보정한다. 이어서 최신 resume review --cleanup·보고·complete를 준비하고 source_worktree=null을 확인해 워크트리를 보존한 채 남은 로컬 브랜치만 삭제한다. 이전 완료·삭제 작업을 재실행하지 않는다.
