---
name: recipe-api-authoring
description: FSD 경계에서 typed Axios API, DTO/parser, TanStack Query 및 MSW 계약을 일관되게 조립합니다.
---

# API 작성 레시피

## 적용 조건

새 REST 도메인, 목록/상세 query, mutation 또는 backend 이전용 MSW 계약을 추가할 때 사용합니다. 단일 URL 상수 변경에는 사용하지 않습니다.

## 절차

1. `src/shared/ui/`와 기존 `shared/api`, 동일 feature의 인접 구현을 먼저 확인합니다.
2. endpoint, 인증, 요청/응답 envelope, 오류, pagination, 상태 vocabulary를 확정합니다. 미확정 값은 임의로 채우지 않습니다.
3. 외부 요청/응답 형태는 `*RequestDto`, `*QueryDto`, `*ResponseDto`로 정의하고 UI 모델과 분리합니다.
4. 알 수 없는 응답 값은 parser에서 좁힌 뒤 도메인 모델로 변환합니다.
5. API 파일은 `api/<도메인>/<도메인>.api.ts`에 두고 `<도메인>Api(client)` factory가 `<HTTP메서드><도메인><대상>` 메서드를 반환하게 합니다.
6. 기존 `ApiClient`와 `ApiResult`를 전송 경계로 재사용합니다. 거대한 전역 API 객체나 도메인 spread registry를 만들지 않습니다.
7. TanStack Query 사용 시 실패 `ApiResult`를 typed error로 변환하고, query key에 id·filter·search·sort·page 등 모든 의존값을 포함합니다.
8. mutation 성공 시 영향받는 최소 key만 무효화합니다. 기존 범용 요청 hook인 `useApi`로 신규 query hook을 다시 감싸지 않습니다.
9. MSW handler는 실제 endpoint, envelope, query/path parsing과 동일하게 작성하고 success·empty·error·상태별 fixture를 제공합니다.
10. 요청 DTO mapper는 허용 필드만 명시적으로 옮기며 RHF form value를 그대로 전송하지 않습니다.
11. 실제 Axios 표면을 통해 happy path와 오류 경계를 확인하고 `npm run build`, `npm run lint`를 실행합니다.

## 명명 예시

```typescript
export const proposalApi = (client: ApiClient) => ({
  getProposalList: (query: GetProposalListQueryDto) =>
    client.get<GetProposalListResponseDto>("/proposals", { params: query }),
  getProposalDetail: (proposalId: string) =>
    client.get<GetProposalDetailResponseDto>(`/proposals/${proposalId}`),
  postProposal: (request: PostProposalRequestDto) =>
    client.post<PostProposalResponseDto, PostProposalRequestDto>("/proposals", request),
});
```

## 완료 조건

- DTO와 UI 모델의 경계가 분명합니다.
- API 이름에서 method·domain·대상을 알 수 있습니다.
- query key와 invalidation 범위가 데이터 의존성을 정확히 반영합니다.
- MSW와 실제 backend가 같은 공개 계약을 사용합니다.
- 미확정 계약과 UI 부수 효과가 transport 함수에 숨겨져 있지 않습니다.
