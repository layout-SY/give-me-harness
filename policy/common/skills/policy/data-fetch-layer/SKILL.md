---
name: policy-data-fetch-layer
description: 전송·도메인·서버 상태·controller·UI의 책임과 양방향 연결 계약을 분리한다.
---

# 데이터 요청 계층

1. 전송 모듈은 HTTP 세부 사항과 DTO 경계를 책임진다.
2. 도메인 작업은 요청 의도와 결과 매핑을 책임진다.
3. 기존 query·mutation 또는 도메인 hook은 서버 상태, 캐시와 요청 수명을 책임진다.
4. Logic의 UI 없는 controller는 응답→UI 데이터·상태와 UI 입력·동작→API 요청 계약을 정의하고 기존 hook·mapper를 조합한다.
5. 컴포넌트는 controller가 제공하는 계약으로 렌더링과 사용자 이벤트를 연결한다.

가공하지 않은 요청과 UI 부수 효과를 동일한 컴포넌트 콜백에 두지 않는다.

Logic 선행은 `controller <- UI`, UI 선행은 `controller -> UI`로 선행 계약에 맞춘다. UI 선행에서 controller·DTO와 UI 항목이 일치하지 않으면 사용자 확인을 받는다. 구체적인 책임·판단·기존 패턴은 [controller 계약](../../recipe/api-authoring/references/ui-controller.md)을 따른다.
