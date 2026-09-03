# user-ui 기준 정책 감사

## 기준

- 저장소: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- 최초 기준 commit: `9edd378560c3c3b7f258984698202498f5c31831`
- 2026-08-31 사용자의 명시적 승인으로 `user-ui` 소비자에 배포된 공통 정책 형태를 현재 중앙 구조에 일회성 역이관했다.
- 다른 중앙 저장소는 직접 읽거나 복사하지 않았고, 소비자 파일의 배포 안내 헤더는 중앙 원본에 포함하지 않았다.
- 프로젝트 전용 컴포넌트·hook 카탈로그는 모든 소비자에 존재하는 공통 자산으로 단정하지 않는다. 후속 사용자 승인으로 기존 항목은 실제 경로와 사용처가 확인될 때만 적용하는 조건부 예시로 보존한다.

## 교정한 불일치

1. 외부 지시의 `synthoria-admin-ui`, React 18, Vite 6, TypeScript 5.8, Jotai, Router 6 정보는 실제 두 package와 일치하지 않아 제외했다. 실제 저장소는 React 19, Vite 8, TypeScript 6, Zustand, Router 7 계열이다.
2. 공용 custom hook reference의 user-ui 파일 경로와 미팅 RTC 생명주기는 실제 대상에서 확인될 때만 적용하도록 조건을 추가하고, 대상 독립적 검색 규칙을 함께 유지했다.
3. 2026-08-31 일회성 역이관에서는 세션 산출물 정본을 `.codex/logs/sessions`로 통합했다. 이 과거 결정을 2026-09-03 호스트 독립 실행 계약이 대체하며 신규 원본은 `.codex`, `.claude`, `.opencode`별 `logs/sessions`로 분리한다.
4. Agora SDK는 두 프로젝트 모두 의존하므로 user-ui 전용 정책으로 분류하지 않았다.
5. 최신 소비자 정책의 한국어 산출물, 승인 기반 브랜치 계보, 호스트별 산출물 정본과 `.agent-policy/common` 공통 계약을 중앙 renderer와 guard에 맞게 이관했다.
6. 기존 harness 파일은 새 중앙 guard와 중복되므로 원본으로 편입하지 않고, 양 소비자에서 다시 확인한 SHA-256만 legacy 감사 스냅샷에 갱신했다.
7. 소비자 `AGENTS.md`에서는 중앙 시스템 프롬프트 저장소를 가리키는 절을 제거하고, 관리 경로 판정과 차단은 manifest 및 `managed_policy_guard.py`가 담당하도록 분리했다.
8. 기존 UI·Logic·오케스트레이션·파이프라인 책임은 유지하되 특정 호스트에 고정하지 않고 공통 `task-role-routing` 계약으로 이동했다.

## 현재 역할 결정

- host 선택은 실행 환경을 선택할 뿐 UI, Logic 또는 오케스트레이션 역할을 자동 배정하지 않는다.
- 사용자 요청과 최신 handoff를 근거로 역할·scope·Git 통합 담당자를 제안하고 사용자 확인 후 수행한다.
- 전체 작업 책임과 부분 역할 인계의 산출물 차이는 host나 branch 고정 속성이 아니라 세션별 `owner|contributor` assignment로 기록한다.
- 프로젝트별 overlay는 후속 기능으로 남겼다.
