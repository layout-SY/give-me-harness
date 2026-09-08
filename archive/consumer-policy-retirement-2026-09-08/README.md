# 소비자 정책 사본 퇴역 기록

- 확인일: 2026-09-08
- 목적: inject-only 전환 전에 소비자 저장소의 정책·프롬프트·훅 사본을 byte 단위로 대조한 결과를 기록한다.
- 실행 사용 금지: 이 디렉터리는 렌더, bundle 생성, audit 판정과 host 실행의 입력이 아니다.

## 삭제 전 대조 결과

폐기 전 별도 보존본과 소비자 파일을 직접 대조했다. `logs/**`와 실행 dependency는 삭제 후보에서 제외했다.

- user-ui primary: 정책 출처 138개 모두 SHA-256 동일
- admin-ui primary: 정책 출처 256개 모두 SHA-256 동일
- user-ui `task/citizen-discussion-api` worktree: 정책 출처 24개 중 23개가 동일

## 별도 fingerprint

`task/citizen-discussion-api`의 `AGENTS.md`는 다른 배포본이어서 별도로 SHA-256을 확인한 뒤 함께 퇴역했다. 원문 사본은 중앙 저장소에 남기지 않는다.

- 원본 당시 경로: `/Users/okand/SynologyDrive/asan-metaverse-user-ui-worktrees/citizen-discussion-api/AGENTS.md`
- SHA-256: `eb790e3aa5f8baeb2f21569b573ca15cf4f11846d9e1489aa08068e36157784a`
- 원본 branch/HEAD: `task/citizen-discussion-api` / `d12dfe508e136c2fccefb84128c58a48c4ad4ea2`

삭제 대상은 대조 당시 실제 bytes가 확인된 파일로 제한했다. 세션 로그, `.claude/settings.local.json`, `.opencode` dependency와 애플리케이션 source는 정책 사본 삭제와 구분한다.

## 적용 및 검증 결과

- 중앙 저장소의 폐기된 자동 배포 archive와 관련 세션 원문을 제거했다.
- user-ui 유지보수 branch `task/retire-consumer-policy-copies`에서 추적 중인 정책 사본 24개를 삭제했다.
- user-ui·admin-ui primary와 두 user-ui worktree에서 정책·프롬프트·훅 소스 및 컴파일 캐시를 다시 검사한 결과는 0건이다.
- Codex·Claude·OpenCode가 동일 유지보수 worktree에서 소비자 로컬 설정 없이 중앙 inject bundle로 시작 준비되는 것을 확인했다.
- 중앙 회귀 테스트 119개가 통과했다.
- `bin/agent-policy audit`는 central contract와 admin-ui를 PASS로 판정하고, 아직 유지보수 commit을 받지 않은 user-ui primary의 `package.json`·`README.md` 참조 2건을 정확히 검출했다.
