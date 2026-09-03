---
name: domain-component-dao-pass-dropdown
description: DAO Pass 관리 도메인 전용 PassDropdown 사용 가이드. 리워드/타입 전환 드롭다운 요구사항에서 사용.
---

# DAO PassDropdown

## 대상
- `src/pages/dao/pass-management/components/passDropdown.tsx`

## 언제 선택하나
- PASS 관리 화면에서 문자열 값 기반 타입 선택이 필요할 때

## 사용 핵심
- `value`, `items`, `onChange`, `disabled`를 연결한다.
- 제네릭 `<T extends string>` 계약을 유지한다.

## 주의
- 일반 `Dropdown`과 계약이 다르므로 혼용 시 호출부 타입을 명확히 구분한다.
