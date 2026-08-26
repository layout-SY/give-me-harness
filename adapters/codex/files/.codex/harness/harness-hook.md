# Harness 훅 계약

훅은 명시적인 승인, 관련 `SKILL.md` 확인, `src/shared/ui/` 또는 재사용 가능 자산 탐색이라는 세 가지 마커를 추적한다. 필요한 마커가 없으면 PreToolUse가 애플리케이션 변경과 미분류 local/MCP 도구를 기본 거부한다. 애플리케이션 변경을 감지할 수 있으면 Stop이 작업 산출물을 확인한다. 훅 명령은 현재 작업 디렉터리의 Git 최상위 경로를 기준으로 SHA-256 검증된 스크립트를 실행하며, 루트 결정·bootstrap·무결성 실패는 종료 코드 2로 차단한다.

별도의 중앙 정책 guard는 `.agent-policy/manifest.json`에 기록된 파일의 소비자 프로젝트 내 수정을 거부하고, SessionStart에서 중앙 소스 및 로컬 파일 drift를 안내한다.
