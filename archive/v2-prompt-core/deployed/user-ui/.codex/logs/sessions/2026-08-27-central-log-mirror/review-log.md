# 중앙 필수 산출물 로그 미러링 검토 로그

## Watcher 판정

PASS

## 검토 범위

- `lib/agent_policy/log_mirror.py`, CLI와 렌더러 연결
- Codex·Claude Code·OpenCode 종료 수명주기
- 중앙 로그 경로 격리, 허용 파일 목록, 심볼릭 링크와 삭제 정책
- 중앙 정책 sync 청결 판정
- 운영 문서와 회귀 테스트

## 점검 항목

- [x] 프로젝트와 채널이 `logs/projects/{project}/{channel}/sessions/`로 분리된다.
- [x] 필수 8개 일반 파일만 byte 단위 그대로 복사한다.
- [x] 같은 내용은 건너뛰고 변경 내용은 원자 교체한다.
- [x] 원본 삭제가 중앙 사본을 지우지 않는다.
- [x] 소스·대상 심볼릭 링크를 통해 허용 경로 밖으로 쓰지 않는다.
- [x] Codex Stop, Claude Stop, OpenCode `session.idle`가 올바른 채널을 호출한다.
- [x] 자동 실행은 Git add·commit 또는 소비자 sync를 호출하지 않는다.
- [x] `logs/**` 외 미커밋 중앙 변경은 계속 정책 sync를 차단한다.
- [x] 기존 렌더링·guard·sync 테스트가 회귀 없이 통과한다.

## 발견 사항

- 차단 발견 사항 없음.
- 정보 | 소비자 정책 미배포 | 새 자동 훅은 아직 user-ui/admin-ui에 반영되지 않았다. 별도 sync 승인 후 적용해야 한다.
- 정보 | legacy 경로 | 두 소비자 프로젝트에서 `.claude/hooks/harness_core.py`, `.codex/hooks/harness_core.py`, `.opencode/plugins/harness_core.py`의 감사 SHA-256 불일치가 계속되어 자동 퇴역할 수 없다.

## 근거

- 중앙 단위 테스트 30개 PASS.
- 두 프로젝트 중앙 audit 각각 128 managed files PASS.
- OpenCode plugin Node 구문 검사와 설치된 OpenCode 1.18.19 local plugin/config smoke PASS.
- 수집기의 허용 목록·멱등 갱신·비삭제·채널 분리 테스트 PASS.
- 기존 필수 산출물 567개 최초 복사 후 동일 명령 재실행에서 567개 전부 unchanged, 신규 복사 0개.
