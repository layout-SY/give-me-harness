# 검토 로그

## Watcher 판정

PASS

## 검토 범위

`/Users/okand/SynologyDrive/asan-agent-policy`의 중앙 원본, renderer, CLI, host adapter, guard, tests와 소비자 dry-run을 검토했다. 실제 소비자 배포는 검토 범위 밖이다.

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 승인 범위 | PASS | 사용자 `이대로 진행`; 중앙 구현과 dry-run까지만 수행 |
| baseline 분리 | PASS | `policy/baseline-user-ui-head.json`, commit 고정 |
| 재사용/추상화 | PASS | 프로젝트 고유 reference 목록 제외, 공통 검색 계약 유지 |
| Codex hook | PASS | 공식 PreToolUse deny shape, integrity hash test 통과 |
| Claude hook | PASS | SessionStart/PreToolUse JSON 계약과 exit 2 차단 test 통과 |
| OpenCode plugin | PASS | 설치된 OpenCode 1.18.19에서 실제 local plugin load PASS |
| drift/manifest | PASS | 중앙 source change와 소비자 mutation 탐지 test 통과 |
| 안전 삭제 | PASS | 이전 manifest hash 불일치와 legacy hash 불일치 시 거부 |
| managed edit 차단 | PASS | Add/Update/Delete/Move, file_path/filePath, shell write test 통과 |
| 애플리케이션 편집 허용 | PASS | `src/App.tsx` 편집 이벤트 허용 test 통과 |
| 문서화 | PASS | 필수 8종 문서 작성 |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 주의 | 두 프로젝트의 legacy `harness_core.py` 3개씩 | 최초 감사 뒤 SHA-256 변경 | 폐기 승인 또는 변경 보존 결정 전 sync 금지 |
| 주의 | user-ui Git index | 별도 작업에서 AI 정책 129개 staged deletion 및 ignore 정책 변경 관찰 | 사용자의 의도 확인; 되돌리지 않음 |
| 정보 | consumer Claude adapter | baseline의 UI 전담 역할 유지 | host 역할 완전 동등화가 필요하면 후속 정책 변경 |

## 결론

중앙 프로젝트와 dry-run은 PASS다. target deployment는 별도 승인과 legacy 동시 변경 해결이 필요하며, 이 보류는 중앙 구현의 FAIL이 아니다.
