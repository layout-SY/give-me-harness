# 구현 로그

## 승인된 범위

편집기에 보이는 `Unsafe assignment of an error typed value`를 타입 경계 수정으로 제거한다. API·화면 동작은 유지한다.

## 변경 경로

| 경로 | 변경 | 이유 |
| --- | --- | --- |
| `src/features/citizen-participation/api/proposal/proposal.dto.ts` | 목록 item/response DTO를 수동 `type`으로 고정 | `z.infer`가 훅 반환을 오류 유형으로 오염시키지 않게 |
| `src/features/citizen-participation/model/queryKeys.ts` | `proposalList` 제거, `list("proposal", query)` 사용 | 훅에서 해결되지 않던 `proposalList` 호출 제거 |
| `src/features/citizen-participation/hook/useCitizenParticipationQueries.ts` | `useQuery<GetProposalListResponseDto, Error, GetProposalListResponseDto, QueryKey>` | queryKey 튜플 추론을 끊고 data 타입을 명시 |
| `src/pages/citizen-participation/model/useCitizenRouteState.ts` | feature barrel 대신 깊은 경로 import | 라우트 → barrel → 훅 순환 제거 |
| `src/pages/citizen-participation/model/presentation.ts` | barrel/MyActivityPage 타입 import 제거, activity 매퍼 re-export | 페이지 모듈과의 순환 완화 |
| `src/pages/citizen-participation/model/proposalActivityPresentation.ts` | `toActivityItemFromProposalList` 분리 | AuxiliaryRoutes가 대형 presentation 그래프 없이 매퍼를 쓰게 |
| `src/pages/citizen-participation/ui/CitizenAuxiliaryRoutes.tsx` | 명시 query DTO, 매핑을 JSX 밖으로 | 훅 인자·items 배열의 문맥 타입 충돌 제거 |
| `src/pages/citizen-participation/ui/CitizenListRoutes.tsx` | 훅/페이지 깊은 import, pageCount 직접 계산 | barrel 재export로 훅이 오류 유형이 되지 않게 |
| `src/features/citizen-participation/model/citizenParticipation.test.ts` | `list("proposal", query)` 기대값으로 수정 | 제거한 `proposalList` 키에 맞춤 |

## 작업 구간별 결과

1. 훅 파일 ReadLints는 `proposalList` 호출을 없애고 `QueryKey` 제네릭을 넣은 뒤 통과했다
2. ListRoutes의 훅 오류는 barrel import를 끊은 뒤에 사라졌다
3. AuxiliaryRoutes의 훅 할당 오류는 query를 `GetProposalListQueryDto`로 좁힌 뒤에 사라졌다
4. 남은 `.map(toActivityItemFromProposalList)` 오류는 매퍼를 `proposalActivityPresentation.ts`로 옮긴 뒤에 사라졌다

## 결정 사항

- `proposalList` 전용 query key factory는 유지하지 않는다. `list(CONTENT_TYPES.PROPOSAL, query)`가 같은 튜플을 만든다
- 상태 라벨 `"접수"` 등은 activity 매퍼 파일에 최소 복사한다. presentation 전체를 끌어오면 순환이 다시 생긴다

## 명령어 및 결과

- `npx tsc -p tsconfig.app.json --noEmit` → exit 0
- `npx vitest run src/features/citizen-participation src/pages/citizen-participation` → 12 files / 56 tests passed
- `npx vitest run src/pages/citizen-participation/model/presentation.test.ts src/features/citizen-participation` → 7 files / 38 tests passed
- `npm run lint` → exit 0
- `npm run build` → `tsc -b && vite build` exit 0, client build 6.04s

## 인계 참고 사항

다른 citizen-participation 라우트(`CitizenMainRoute`, detail routes)는 아직 feature barrel을 사용한다. 같은 오류 유형이 나면 깊은 경로 import를 우선한다.
