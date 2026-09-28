---
name: recipe-data-dto
description: 타입이 지정된 요청, 응답, 쿼리, 폼-페이로드 DTO 경계를 조립합니다.
---

# 데이터 DTO 레시피

전송 계약을 점검하고, 불변 데이터 형태를 정의하며, 생성/수정/쿼리 DTO를 분리하고, 폼 상태를 명시적으로 매핑한 뒤 필수/선택 의미가 서버 계약과 일치하는지 검증합니다. 전송 타입과 UI 속성의 생명주기가 다르면 서로 분리합니다.

응답 DTO를 작성할 때는 현재 프로젝트의 `src/shared/api/common/`부터 확인하고, 계약이 일치하는 공통 envelope·pagination DTO와 schema를 반드시 import하여 재사용합니다. 도메인별로 같은 구조를 다시 선언하지 않으며, 프로젝트별 자산과 `ApiClient`의 payload 타입 경계는 [공통 응답 DTO 재사용 규칙](../api-authoring/references/transport-contracts.md)을 따릅니다.

외부 응답은 `unknown`에서 parser로 좁히며, TypeScript 응답 타입 지정만으로 검증을 대신하지 않습니다. Query 캐시나 UI 모델로 들어가기 전 한 번 검증하고, 이미 API factory에서 검증한 응답을 hook에서 다시 parse하지 않습니다.

목록 pagination·nullable 상세·mutation의 문자열/boolean/빈 body는 각 endpoint 계약대로 정의합니다. request mapper는 허용 필드만 옮기고, null·undefined·필드 생략과 query 배열 직렬화의 차이를 유지합니다. 자세한 경계는 `api-authoring/references/transport-contracts.md`를 참조합니다.
