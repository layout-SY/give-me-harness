# 탐색

## 결론

production route는 이미 TanStack Query를 사용하지만 `src/pages/citizen-participation/model/presentation.ts`가 API 계약에 없는 필드를 빈 문자열·0으로 만들고 `PolicyDetailRoute`는 stages를 항상 빈 배열로 전달한다. UI 파일을 수정하지 않고 DTO·parser·MSW fixture와 pages mapper를 확장하는 것이 가장 작은 해결책이다.

## 확인한 흐름

`MSW handler → ApiClient → unwrapApiResult → Zod parser → TanStack Query → pages mapper → production UI props`

## 주요 발견

- main, 5개 list, 5개 detail, activity, comment GET endpoint는 모두 존재한다.
- UI의 `DEFAULT_*` 배열/객체는 production route가 props를 전달하므로 현재 직접 사용되지 않는다.
- 실제 route-reachable placeholder는 author, period, comment count, policy stage, survey metadata, proposal detail section, reward notice 등이다.
- `ContentListItemDto`와 `ContentDetailDto`가 해당 표시 필드를 표현하지 못해 mapper가 값을 만들거나 비워 두고 있다.
- comment handler는 모든 content에 같은 댓글을 반환하고 detail `commentCount`와 개수가 일치하지 않는다.
- 기존 `Loading`, `NoResults`, React Query `isLoading`/`isFetching`을 재사용할 수 있어 새 UI abstraction은 필요 없다.

## 재사용 자산

| 자산 | 경로 | 사용 결정 |
| --- | --- | --- |
| typed query hooks | `src/features/citizen-participation/hook/useCitizenParticipationQueries.ts` | 유지·확장 |
| Zod parser | `src/features/citizen-participation/api/http/citizenParticipation.parser.ts` | 응답 boundary로 유지 |
| MSW handlers | `src/features/citizen-participation/mocks/handlers.ts` | endpoint와 query/path parsing 재사용 |
| `Loading`, `NoResults` | `src/shared/ui/` | 기존 UI에서 계속 사용 |
| raw React/Vitest harness | auth hook test 및 citizen MSW tests | 신규 프레임워크 없이 focused test 작성 |

## 제약

- Hephaestus는 production UI 파일을 수정하지 않는다.
- TypeScript LSP는 미설치 상태이므로 `npm run build`로 진단을 대체한다.
- 브라우저 자동화·스크린샷·시각 QA는 프로젝트 규칙에 따라 수행하지 않는다.
- `presentation.ts`는 pure LOC 218로 경고 구간이므로 250 LOC를 넘기지 않도록 기존 placeholder 교체 중심으로 수정한다.
