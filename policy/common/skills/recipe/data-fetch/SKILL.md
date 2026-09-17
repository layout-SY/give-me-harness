---
name: recipe-data-fetch
description: 전송, 연산, 훅, UI 계층을 사용해 타입이 지정된 데이터 조회 화면을 조립합니다.
---

# 데이터 조회 레시피

1. `src/shared/ui/`와 `reference` 스킬을 검색합니다.
2. 기존 DTO/parser와 전송 factory를 재사용합니다. 새 API가 필요하면 `api-authoring`의 전송 계약을 따릅니다.
3. 서버 조회는 기존 TanStack Query hook/options에 로딩·오류·취소·캐시를 맡깁니다. Query를 `useApi`로 다시 감싸거나 같은 loading state를 중복 관리하지 않습니다. 명령형 요청은 `api-authoring/references/query-mutation.md`의 useApi 계약을 확인합니다.
4. 기존 테이블, 페이지네이션, 폼, 모달 어댑터가 있으면 이를 조합합니다.
5. 새로고침, 빈 상태, 오류, 제출 결과와 mutation 후 영향받는 key의 재검증을 확인합니다. Query signal이 실제 전송까지 전달되는지 점검합니다.
