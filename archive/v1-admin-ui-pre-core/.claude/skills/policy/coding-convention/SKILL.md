---
name: policy-coding-convention
description: synthoria-admin-ui에서 코드를 작성/수정하기 전에 항상 함께 적용해야 하는 횡단 코딩 규약. any 금지, interface/type 선택(policy-type-definition 위임), functional component, 커스텀 훅 분리, early return, JSX 헬퍼 분리, 네이밍/폴더/import 규칙을 지켜야 할 때 사용.
---

# Coding Convention (Policy)

## 언제 이 스킬을 사용하나요?

- 신규 파일/함수/컴포넌트를 작성하기 직전
- 기존 코드를 수정하면서 네이밍/타입/구조 규칙을 재확인해야 할 때
- 리뷰·리팩터 작업 시 공통 기준으로 삼아야 할 때

## 규칙

- `any` 사용 금지 (필요 시 `unknown` 후 좁히기)
- **interface vs type 결정은 [`policy-type-definition`](../type-definition/SKILL.md)를 따른다** — 두 관계 간 계약(props·콜백·hook 반환·경계 DTO)이면 `interface`, 그 외 데이터 형태/유니온/파생이면 `type`.
- React는 **functional component**로만 작성
- 재사용 가능한 로직은 **custom hook으로 분리**
- **early return** 우선, 깊은 중첩 지양
- JSX 내 복잡한 helper 로직은 바깥으로 추출 후 단순 호출만 남김
- 네이밍 / 폴더 구조 / import 순서는 프로젝트 기존 패턴 일관 유지
- 절대 경로(`~/...`) 우선, 동일 파일 내 중복 import 금지

## 금지

- 전역 변수/모듈 최상위 mutable state 추가
- 사용처 없는 유틸/타입 선제 정의
- 기존 배럴/선언 위치 규칙을 깨는 독자 스타일 도입
