# user-ui 기준 정책 감사

## 기준

- 저장소: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- commit: `9edd378560c3c3b7f258984698202498f5c31831`
- 현재 작업 트리의 기존 중앙화 산출물은 가져오지 않았다.

## 교정한 불일치

1. 외부 지시의 `synthoria-admin-ui`, React 18, Vite 6, TypeScript 5.8, Jotai, Router 6 정보는 실제 두 package와 일치하지 않아 제외했다. 실제 저장소는 React 19, Vite 8, TypeScript 6, Zustand, Router 7 계열이다.
2. 공용 custom hook reference가 user-ui 파일 경로와 미팅 RTC 생명주기를 단정해 대상 독립적 검색 규칙으로 바꿨다.
3. 공통 산출물은 `.codex/logs`에 쓰도록 하면서 Claude가 그 경로를 읽기 전용으로 취급하던 충돌을 `.claude/logs/sessions` host 치환으로 해결했다.
4. Agora SDK는 두 프로젝트 모두 의존하므로 user-ui 전용 정책으로 분류하지 않았다.

## 의도적으로 유지한 제약

- consumer의 Claude Code는 user-ui 기준대로 production UI 전담 역할을 유지한다.
- 따라서 V1의 host 선택은 같은 정책 버전을 선택한다는 뜻이지, 세 host의 작업 역할이 완전히 동일하다는 뜻은 아니다.
- 프로젝트별 overlay는 후속 기능으로 남겼다.
