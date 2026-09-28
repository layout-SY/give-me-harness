# 승인된 기준 브랜치 등록의 실행 예약 만료

## 후속 결과

사용자가 동일 작업을 다시 승인한 뒤 a2299069 등록 실행이 exit 0·stage done으로 성공했다. sy-main 기준 노드가 등록됐으며 만료 오류는 재발하지 않았다. 아래 내용은 최초 실패의 진단 이력이다.

## 결론

사용자의 `명령 실행 승인`은 정상 반영됐다. 사전 검사에서 생성한 실행 예약과 실제 프로세스 시작 사이에 120초 제한을 초과하여 등록이 수행되지 않았다. 승인 누락이나 source·target 변경이 원인이 아니다.

## 실행과 실제 상태

- 작업 ID: `a2299069dade4faea3811aa15972e7c5`.
- 실행 명령: 현재 bundle의 `git_operations.py execute a2299069dade4faea3811aa15972e7c5`, `python3 -I`, workdir는 `/Users/okand/SynologyDrive/asan-metaverse-user-ui`, require_escalated.
- 사용자 승인 뒤 해당 명령을 한 번 실행했다. 결과: exit 2, `Git 작업: 이 작업의 사용자 승인과 도구 실행 예약이 필요합니다.`.
- `show` 결과 stage는 `prepared`; graph는 version 1·revision 0·nodes {}다.
- 실제 HEAD는 sy-main `c79f3d8c74c0536fa2d3afb983fb2e121742f076`, resume `32e2265e3581a2bc0590ff01f935ebc1e61423a0`, 이전 브랜치 `d12dfe508e136c2fccefb84128c58a48c4ad4ea2`로 유지됐다.

## 읽기 전용 근거

- grant의 fingerprint는 prepared operation과 일치한다.
- host는 `codex`, assignment는 현재 `215e1e66acfb48adad6983a207398c98`로 일치한다.
- grant `created_at`: `1789043111.8319292`.
- grant 파일 mtime: `1789043111.832239`.
- 이번 실행에서 처음 생성한 `operation-a2299069dade4faea3811aa15972e7c5.lock` mtime: `1789043242.4294312`.
- 실행 lock 생성과 grant 파일 기록 차이: `130.59719228744507`초. actual execute 검사는 이 lock 이후다.
- 현재 snapshot `git_operations.py:500`은 `state.read(grant_path, max_age=120)`으로 예약을 읽는다. 501~502행에서 유효한 예약이 없으면 관측한 오류를 발생시킨다.
- `runtime_state.py:57`부터 `created_at`과 현재 시간의 차이가 max_age를 넘으면 빈 dict를 반환한다.
- `approval_policy.py:460`부터 일치하는 사용자 승인을 확인한 즉시 승인 기록을 unlink한다.
- `shared_git.py:275`부터 사용자 승인 확인 뒤 grant를 생성한다. host 실행 권한 요청은 이 사전 검사와 실제 프로세스 실행 사이에 있었다. 전체 지연의 세부 구성까지 별도 측정하지 않았으므로 특정 대기 시간 비중을 단정하지 않는다.

## 조치와 재개

예약 파일·승인 파일·정책 소스를 직접 수정하지 않았다. 원인 확인 후 같은 execute를 정식 도구로 요청하여 새 승인 대기를 생성했다. 이 호출은 PreToolUse가 `명령 실행 승인`을 요구하며 실제 프로세스 실행 전에 거부했다. 현재 대기 작업은 동일한 sy-main 기준 브랜치 등록이다.

재승인 뒤 같은 오류가 재발하면 추가 재시도 없이 중앙 정책 담당 세션에 위 근거를 넘긴다. 개선 후보는 호스트 권한 대기와 예약 유효기간의 정합성 및 미실행 승인 복구이며, 현재 Logic 작업에서는 정책을 수정하지 않는다.
