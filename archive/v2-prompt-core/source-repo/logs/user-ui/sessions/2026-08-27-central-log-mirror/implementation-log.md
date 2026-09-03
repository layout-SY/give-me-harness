# 중앙 필수 산출물 로그 미러링 구현 로그

## 승인된 범위

- 각 프로젝트의 필수 산출물을 독립 Git 저장소 `asan-agent-policy`에도 복사해 관리한다.
- user-ui와 admin-ui, Logic과 Claude 채널을 분리한다.
- Codex·Claude Code·OpenCode 종료 수명주기에 자동 수집을 연결한다.
- Git add·commit은 자동화하지 않고 소비자 정책 sync도 별도 승인 전 실행하지 않는다.

## 변경 경로

- 중앙 수집기: `lib/agent_policy/log_mirror.py`
- 중앙 CLI: `lib/agent_policy/cli.py`
- Codex·Claude 렌더러와 청결 판정: `lib/agent_policy/core.py`
- OpenCode plugin: `adapters/opencode/files/.opencode/plugins/agent-policy.js`
- 생성 정책 문서: `policy/common/AGENTS.template.md`, `adapters/claude/CLAUDE.template.md`
- 중앙 운영 문서: `README.md`, `AGENTS.md`, `logs/README.md`
- 검증: `tests/test_log_mirror.py`, `tests/test_rendering.py`, `tests/test_sync.py`

## 작업 구간별 결과

1. 허용 목록의 8개 파일만 직접 세션 디렉터리에서 읽고 프로젝트·채널별 중앙 경로로 쓰는 수집기를 추가했다.
2. byte 비교로 같은 파일을 건너뛰고 `atomic_write`로 변경분만 교체했다. 소스 삭제는 중앙 사본에 전파하지 않는다.
3. 소스 세션·파일 심볼릭 링크와 중앙 대상 심볼릭 링크를 거부하거나 건너뛰도록 경계 검사를 추가했다.
4. `collect-logs --project {all,user-ui,admin-ui} --channel {all,logic,claude}` CLI를 추가했다. 정상 자동 실행은 `--quiet`이며 수집 오류는 종료 코드 1로 보고한다.
5. Codex Stop과 Claude Stop, OpenCode `session.idle`에 각각 `logic`, `claude`, `logic` 수집을 연결했다.
6. 중앙 Git 청결 판정은 `logs/**`만 변경된 경우 통과하고 정책 소스 또는 외부→logs rename은 계속 거부하도록 수정했다.

## 결정 사항

- 활성 세션의 프로젝트 로그를 원본으로, 중앙 로그를 별도 Git 이력용 사본으로 본다.
- 자동 수집이 실패하면 세션을 차단하거나 Git 작업을 시도하지 않고 stderr로 알린 뒤 다음 수명주기에서 재시도한다.
- Logic 채널은 Codex와 OpenCode가 같은 `.codex/logs/sessions/` 원본을 공유한다.

## 명령과 결과

- `python3 -B -m unittest discover -s tests -v`: 30개 PASS.
- `bin/agent-policy audit`: user-ui와 admin-ui 각각 128 managed files PASS.
- `bin/agent-policy diff --project all`: 두 프로젝트 모두 기존 미배포 상태이며 add 10, change 100, legacy 11, manifest missing을 확인했다. sync하지 않았다.
- `bin/agent-policy collect-logs --help`: 새 project·channel·quiet 옵션 표시 PASS.
- `node --check adapters/opencode/files/.opencode/plugins/agent-policy.js`: PASS.
- `python3 -B tests/smoke_opencode_plugin.py`: 설치된 OpenCode 1.18.19의 local plugin과 보호 명령 permission 로드 PASS.
- 최초 중앙 수집: admin-ui Logic 187개, admin-ui Claude 17개, user-ui Logic 332개, user-ui Claude 31개로 총 567개 복사.
- 동일 명령 즉시 재실행: `copied=0`, `unchanged=567`로 멱등성 PASS.

## 인계 참고 사항

- 자동 훅은 중앙 정책을 소비자 프로젝트에 sync한 뒤 새 세션부터 적용된다.
- 현재 소비자 파일은 변경하지 않았고 legacy `harness_core.py` 3종의 SHA-256 불일치도 그대로 남아 있다.
