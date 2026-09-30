---
name: recipe-data-fetch
description: 기존 API·Query와 UI 없는 controller 계약을 사용해 데이터 조회 화면을 조립합니다.
---

# 데이터 조회 레시피

1. `src/shared/ui/`와 `reference` 스킬을 검색합니다.
2. 기존 DTO/parser와 전송 factory를 재사용합니다. 새 API가 필요하면 `api-authoring`의 전송 계약을 따릅니다.
3. 서버 조회는 기존 TanStack Query hook/options에 로딩·오류·취소·캐시를 맡깁니다. Query를 `useApi`로 다시 감싸거나 같은 loading state를 중복 관리하지 않습니다. 명령형 요청은 `api-authoring/references/query-mutation.md`의 useApi 계약을 확인합니다.
4. [controller 계약](../api-authoring/references/ui-controller.md)에 따라 기존 controller를 재사용·확장하거나 구현합니다. Logic 선행이면 UI가 controller에 맞추고, UI 선행이면 controller가 UI 계약에 맞춥니다. UI 선행에서 UI 항목과 controller·DTO가 불일치하면 사용자에게 질문하고 답변 전 해당 연결을 보류합니다.
5. 기존 테이블, 페이지네이션, 폼, 모달 어댑터를 controller의 데이터·상태·callback 계약으로 조합합니다.
6. 새로고침, 빈 상태, 오류, 제출 결과, 양방향 매핑과 mutation 후 영향받는 key의 재검증을 확인합니다. Query signal이 실제 전송까지 전달되는지 점검합니다.
