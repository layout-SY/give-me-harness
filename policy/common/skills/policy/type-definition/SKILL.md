---
name: policy-type-definition
description: 속성, 콜백, 훅 및 DTO에 대한 TypeScript 계약 경계와 데이터 형태 규약을 정의한다.
---

# 타입 정의

속성, 콜백, 훅 반환값, DTO와 로컬 상태를 포함한 TypeScript 정의에는 `type` alias를 우선한다. 라이브러리 확장이나 declaration merging처럼 `interface`가 필요한 경우 이유를 명시한다. 계약을 명시적으로 유지하고 `any`를 도입하지 않는다. 사용자 지정 규칙과 실제 프로젝트 지침을 우선한다.
