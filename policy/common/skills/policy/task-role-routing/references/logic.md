# Logic 역할

Logic 역할은 화면 표현 밖의 기능 동작과 데이터 흐름을 담당한다.

## 책임

- API transport, 요청·응답 DTO, parser, validator와 오류 변환
- hook, util, lib, store, atom 또는 상태 머신과 도메인 상태 전이
- 데이터 조회·가공·캐시·영속성 및 업무 규칙
- 확인된 scope 안의 `App.tsx`, `main.tsx`, feature barrel, 패키지·빌드 설정과 기능 통합
- UI 역할이 제공한 최신 props/callback 계약을 다시 읽고 기능을 연결하는 작업
- 변경 동작을 입증하는 타입 검사, lint, build와 필요한 기존 테스트

## 경계

- UI 파일에 API 호출, 영속성, 파싱, 업무 검증, 재사용 hook/util 또는 도메인 상태 전이를 숨기지 않는다.
- 별도 UI 역할이 활성화돼 있으면 그 역할이 소유한 파일을 덮어쓰거나 선행 통합하지 않는다. 최신 handoff와 사용자 확인 후 연결한다.
- 사용자가 기능 확인용 임시 UI를 명시적으로 요청하면 production UI와 분리된 경로에 최소 시맨틱 마크업과 필요한 레이아웃만 만들 수 있다.
- 시각적 완성도, 디자인 시스템 확장 또는 공용 UI 추상화가 필요하면 UI 역할을 추가 제안한다.
