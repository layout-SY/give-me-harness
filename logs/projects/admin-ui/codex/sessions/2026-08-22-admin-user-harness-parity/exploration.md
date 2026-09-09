# Admin/User 하네스 동일화 탐색

## 결론

- feature, production UI, CSS 작업은 전면 중단한다.
- admin-ui의 marker 기반 허용형 Hook을 user-ui의 session identity 기반 default-deny Hook으로 교체해야 한다.
- user-ui 구조를 그대로 가져오는 것만으로는 승인 후 CSS, 브라우저·시각 QA, Watcher 실행을 막지 못한다.
- 이번 사용자 지시는 Python `PreToolUse` hard deny와 회귀 테스트로 추가 강제해야 한다.

## 비교 결과

| 영역 | user-ui | admin-ui | 조치 |
| --- | --- | --- | --- |
| 승인 | 정규화된 전체 프롬프트 exact match | 이벤트 전체 substring match | user-ui 방식 이식 |
| 상태 | session/task/transcript identity 바인딩 JSON | 저장소 공용 marker 파일 | user-ui v2 상태 이식 |
| 변경 경로 | canonicalize, symlink·repository escape 차단 | 문자열 기반 probable path | user-ui 방식 이식 |
| 미분류 도구 | 필수 조건 전 default-deny | 대부분 허용 | user-ui 방식 이식 |
| Hook 무결성 | entry + common SHA-256 검증 | 직접 Python 실행 | user-ui bootstrap 이식 |
| Stop | 바인딩 session과 8개 산출물 검증 | active slug와 분리 portfolio 검증 | user-ui 구조로 통일 |
| Python 테스트 | 22개 governance 회귀 테스트 | portfolio 중심 11개 테스트 | user-ui suite 이식 후 admin 금지 규칙 추가 |
| QA 제한 | AGENTS.md prose 중심 | 명시적 제한 없음 | Python hard deny 추가 |

## 사용자 지시를 실행 규칙으로 변환

1. Hephaestus의 production UI·CSS mutation을 승인 여부와 무관하게 차단한다.
2. Playwright, browser automation, screenshot·image capture, visual QA 도구를 승인 여부와 무관하게 차단한다.
3. Watcher 및 별도 review agent 실행을 승인 여부와 무관하게 차단한다.
4. QA 근거는 repository 테스트 코드와 test command 결과만 허용한다.
5. build·lint는 정적 검증으로 실행할 수 있지만 QA 통과 근거로 대체하지 않는다.
6. 위 제한은 prompt 요약이나 context compaction과 무관하게 Python 코드와 테스트에 남긴다.

## 재사용 대상

- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/AGENTS.md`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/.codex/hooks.json`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/.codex/hooks/*.py`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/.codex/harness/`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/.codex/agents/`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/.codex/multi-agent-spec*`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/.codex/workflows/`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/.codex/templates/`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/.harness/roles/orchestration.md`

## 보존 대상

- admin 도메인 전용 `.agents/skills/**`
- admin 도메인 전용 `.codex/memory/reusable-assets.md`
- 기존 session·portfolio 이력
- application source와 CSS

## 현재 상태

- `hold_for_approval`
- 하네스 production 파일은 아직 수정하지 않았다.
- 브라우저, Watcher, 이미지 캡처 QA는 실행하지 않았다.
