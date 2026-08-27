# 시민참여 production UI 통합 계획

## 결론

Claude Code의 `UI_COMPLETE` handoff를 기준으로 production UI 파일은 수정하지 않고, non-UI integration controller·presenter·feature barrel·중앙 route에서 기존 TanStack Query/API 기능을 연결한다.

## 구간

1. 13개 화면과 popup props 계약을 최신 소스와 대조한다.
2. route와 DTO→UI presenter를 테스트 우선으로 고정한다.
3. URL query state와 service navigation을 구현한다.
4. main, 목록, 상세, 참여, 내 활동 controller를 구현한다.
5. backend 계약이 없는 mutation은 가짜 payload 없이 제한한다.
6. 테스트, build, lint로 검증한다.
