---
name: require-documentation
enabled: true
event: stop
pattern: .*
action: warn
---

작업 결과를 자기 세션의 `.claude/logs/sessions/{날짜}-{작업명}/`에 기록한다.
owner는 `plan.md`와 `final-summary.md`, 부분 기여자 또는 인계 시에는 `handoff.md`를 사용한다. 세부 탐색·구현·리뷰·평가 기록은 필요에 따라 선택한다.
문서 누락으로 대화 종료, Git 변경 또는 다음 작업 시작을 차단하지 않는다.
