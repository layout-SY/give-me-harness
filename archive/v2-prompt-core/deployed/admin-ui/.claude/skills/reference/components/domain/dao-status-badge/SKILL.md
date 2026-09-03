---
name: domain-component-dao-status-badge
description: DAO 도메인 공용 StatusBadge 사용 가이드. 제안/토론/심사 상태 배지 표시에 사용.
---

# DAO StatusBadge

## 대상
- `src/pages/dao/components/status/status-badge.tsx`

## 언제 선택하나
- DAO 상태값(`ACTIVE`, `PENDING_REVIEW`, `REJECTED` 등)을 배지로 통일 표기할 때

## 사용 핵심
- `status`, `label`, `variant`를 전달한다.
- label은 표시할 한글 문자열을 직접 전달한다.

## 주의
- 상태 컬러 매핑(`resolveDefaultColor`) 변경은 여러 DAO 화면에 동시에 반영된다.
