# 이력서·포트폴리오 기록

## 사례 1 — 시민 투표 목록 API 계약 분리와 status 어휘 정리

- 작업 유형: 프로젝트 구현
- 관련 도메인/서비스: 시민참여 vote list
- 문제 출처: 사용자 요구, 기획 변경

### 문제 상황

- 사용자가 제시한 요구·문제·변경 이유: 백엔드 투표 목록 응답이 `{ items: [{ id, title, summary, status, startsAt, endsAt, commentCount, agreeCount, disagreeCount, createdAt }], total, page, size }`로 확정됐다. 요청은 `page`/`size`를 항상 보내고, `status`는 `IN_PROGRESS`|`CLOSED` 배열(생략 시 둘 다, 둘 다면 OR), `sort`는 `property,(asc|desc)` 배열이다. 그 외 status는 400이므로 클라이언트가 보내면 안 된다.
- 테스트·런타임에서 관찰한 오류: Axios 기본 배열 params가 `status[]`로 나가 `URLSearchParams.getAll("status")`가 비었다. `exactOptionalPropertyTypes`에서 `author: string | undefined`를 optional prop에 넣으면 tsc가 실패했다. 진행 중 fixture에서 찬반 수를 빼자 상세 테스트가 `agreeCount: 72`를 기대해 실패했다.
- 필요한 기술·구조·패턴이 없을 때 발생할 문제: 공용 `ContentListQueryDto`에 `scheduled`/`open`을 남기면 확정 status와 어긋나 파싱이 실패하고, 유효하지 않은 status를 보내면 400이 난다. 진행 중 `agreeCount`를 숫자로 가정하면 확정 `null` 응답을 거절한다.

### 세션·하네스 사고 근거

해당 없음

- 플랫폼·프로젝트 또는 cwd: Cursor, asan-metaverse-user-ui
- main session ID와 관련 child session 범위: `05e51fb4-da33-4830-9865-1201ca868135`. child session 측정 근거 없음
- 사용자 핵심 지시 원문과 시각: 2026-08-25 16:36에 투표 목록 SUCCESS JSON을 제시했고, 구현 전 계획 확인 후 16:46에 `작업 진행`으로 승인했다.
- 재지적·중단 지시와 시각: 없음
- compaction 전후 `Objective`·제한·`Next Move` 변화: 구현 도중 compaction이 있었고, 목표는 투표 목록 계약 구현과 세션 산출물 작성으로 유지됐다.
- 지시와 어긋난 파일 수정·도구·검토·캡처·재작업: `VoteListPage` 마크업은 수정하지 않았다. `CitizenListRoutes.tsx`에 훅 연결만 했다. 이미지 캡처 QA는 하지 않았다.
- message·transcript entry·input token·cache read·child session 측정값: 측정 근거 없음
- 측정 출처와 인과 해석의 한계: 전체 세션 token을 이 작업 소비량으로 단정하지 않는다.
- 비용·품질·협업 영향에 관한 사용자 피드백: 없음
- 방지책과 남은 host·Hook 제한: 배열 query는 `URLSearchParams.append`로 반복 키를 만들고, 새 query key 팩토리 대신 기존 `lists()`에 객체를 붙였다.

### 고민과 선택

- 사용자 제안: 확정 목록 JSON과 `page`/`size` 필수, optional `status`/`sort`. 유효하지 않은 status는 보내지 않는다.
- 에이전트 제안: 투표 목록만 전용 DTO로 분리하고 `VOTE_STATUS`를 토론 status와 분리한다. 첫 화면은 `page`/`size`만 보낸다. 내 활동과 상세 envelope는 이번 범위에서 유지한다.
- 검토한 대안: (1) 공용 content list DTO에 투표 필드만 추가 (2) 투표 목록 전용 DTO를 사용처까지 관통 (3) `UPCOMING`/`CANCELLED`를 클라이언트 enum에 미리 넣기
- 최종 선택: (2). status 어휘는 투표만 `IN_PROGRESS`/`CLOSED`.
- 선택 이유와 제외한 방식의 이유: 확정 JSON이 proposal list와 같이 `{ items, total, page, size }`이고 아이템 필드가 공용 content list와 다르다. 미허용 status를 enum에 넣으면 클라이언트가 400을 유발할 수 있다. 사용자는 계획에 `작업 진행`으로 승인했다.

### 적용

- 변경 경로: `constants.ts`, `vote.dto.ts`, `vote.api.ts`, parser, `useVoteListQuery`, presentation 매퍼, `CitizenListRoutes.tsx`, 상세 제출 가드, MSW handlers/fixtures, barrel, 관련 테스트
- 구현·수정·리팩터링 내용: `toVoteListParams`가 `page`/`size`를 set하고 `status`/`sort`만 append한다. 목록 화면은 `myActivityOnly`이면 기존 activity query, 아니면 `useVoteListQuery({ page, size })`다. 진행 중 아이템은 찬반 비율 없이, 종료 아이템은 `agreeCount`/`disagreeCount`로 비율을 계산한다.
- 핵심 동작: 확정 envelope와 숫자 id 목록을 파싱하고, 클라이언트가 `UPCOMING`/`CANCELLED`를 보내지 않으며, 반복 `status` 키로 OR 필터를 표현한다.

### 사용 기술과 구체적 목적

| 기술·구조·패턴 | 해결하려는 구체적 문제 | 적용 위치와 방식 |
| --- | --- | --- |
| Zod response schema + handwritten DTO | 확정되지 않은 목록 필드와 `z.infer` 추론 붕괴를 UI로 흘리지 않기 | `getVoteListResponseSchema` / `GetVoteListItemDto` |
| `URLSearchParams.append` | Axios `status[]`가 서버 repeated key와 어긋남 | `vote.api.ts` `toVoteListParams` |
| 전용 Query DTO | 공용 content list query에 투표 전용 배열 필터를 섞지 않기 | `GetVoteListQueryDto`, 라우트는 `{ page, size }`만 전달 |
| TanStack Query `enabled` | 같은 화면에서 list/activity를 조건부 훅 호출로 깨지 않기 | `useVoteListQuery`, `useMyActivityQuery("vote")` |
| MSW SUCCESS envelope | 로컬이 옛 `{ success: true }`만 재현하면 실서버와 어긋남 | vote list handler만 `{ code: "SUCCESS", data }` |

### 결과

- 적용 전: 투표 목록이 공용 content list 계약과 `scheduled`/`open`/`closed`를 썼다.
- 적용 후: 목록은 확정 응답 DTO와 `IN_PROGRESS`/`CLOSED`를 쓰고, 첫 화면은 `page`/`size`만 보낸다. 진행 중 찬반 수는 `null`이다.
- 검증 결과: 관련 vitest 12 files / 61 passed, `npm run lint` 성공, `npm run build` 성공.
- 사용자 후속 피드백: 없음
- 추가 요청 및 남은 제한: 투표 내 활동 응답·상세 envelope·status/sort UI는 미확정. 목록 size는 클라이언트 10.
- 직접 측정하지 못한 수치: 측정 근거 없음

```mermaid
flowchart LR
  Before[공용 content list와 open/closed] --> Change[전용 vote list DTO와 VOTE_STATUS]
  Change --> After[page/size 목록 요청과 반복 status 키]
```

### 이력서·포트폴리오 문구

- 이력서 bullet: 시민 투표 목록을 확정 백엔드 계약(`items`/`total`/`page`/`size`, `IN_PROGRESS`/`CLOSED`)으로 분리하고, 배열 query를 repeated key로 보내 미허용 status와 Axios `status[]` 직렬화가 400·필터 누락을 만들지 않게 했다.
- 포트폴리오 서술: 공용 목록 DTO에 투표 필드를 얹으면 확정 status·nullable 찬반 수와 어긋나고, 배열 params 기본 직렬화는 서버 OR 필터와 맞지 않는다. 전용 DTO와 `URLSearchParams`를 적용한 뒤 관련 테스트 61건과 빌드·린트가 통과했다.
