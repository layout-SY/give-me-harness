# 탐색 기록

## 대상 경로
- `src/features/meeting/`
- `src/shared/ui/`
- `src/shared/api/`
- `package.json` 및 lockfile
- Git 이력과 현재 worktree

## 발견한 기존 재사용 자산
- 발견 항목: Button, IconButton, TextInput, TextArea, Loading, Axios API client
- 재사용 제안: 실제 라우터 통합 전에 회의 폼/제어 UI와 API 호출을 기존 공용 계약에 맞춘다.
- 근거: 현재 회의 초안은 native form control과 `fetch`를 사용해 대상 프로젝트 방식과 차이가 있다.

## 재사용이 어려운 자산
- 자산: Agora client와 media track
- 부적합 사유: mutable SDK 객체이므로 전역 store보다 회의 Hook의 ref 소유가 생명주기 정리에 적합하다.

## 신규 자산 필요성
- 필요 항목: `src/features/meeting/**`
- 필요 이유: 회의 API parsing, RTC 연결, 로컬 미디어, 원격 참가자 상태는 기존 공용 UI에서 제공하지 않는 도메인 기능이다.

## 커밋 경계 근거
- 오늘 생성된 회의 feature, SDK 의존성, handoff 문서를 이번 범위로 묶었다.
- 7월 6~9일 수정된 Architecture, Dropdown, form/validation placeholder는 회의 코드에서 참조하지 않아 제외했다.
