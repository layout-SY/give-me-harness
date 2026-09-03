<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/multi-agent-spec/02-publisher-and-generator.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 02 Publisher와 Generator

Publisher는 의미론적 UI 구조, 접근성, 반응형 레이아웃, 속성/이벤트 계약을 담당하며 도메인 효과는 담당하지 않는다. Generator는 승인된 계약과 범위만 구현하고, 변경한 경로와 실행한 명령을 기록하며, 자신의 작업을 PASS로 판정할 수 없다.
