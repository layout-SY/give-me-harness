# 계획

## 목표

시민참여 production route가 UI 임시 표시값 대신 MSW API 응답의 목록·상세·활동·댓글 데이터를 parser와 presentation mapper를 거쳐 props로 전달하도록 한다.

## 범위

- 시민참여 목록·상세 DTO/parser에 현재 UI가 요구하는 표시 메타데이터 추가
- MSW fixture를 content type별 실제 화면 데이터와 content별 댓글 데이터로 확장
- pages presentation mapper의 `""`, `0`, `[]` placeholder를 parsed 응답 필드로 교체
- 정책 처리 단계와 내 활동 요약/보상 안내를 API 응답에서 route props로 연결
- parser, presentation, MSW handler, route render 경계를 focused test로 검증

## 제외 사항

- `src/features/citizen-participation/ui/**` production UI와 CSS 수정
- 정적 옵션·서비스명·버튼 문구처럼 API 데이터가 아닌 UI copy 이동
- proposal 작성 mutation, comment mutation state, 실제 backend endpoint 변경
- auth, meeting 및 다른 세션 소유 파일 변경

## 작업 구간과 역할

| 구간 | 역할 | 스킬 | 결과 |
| --- | --- | --- | --- |
| 탐색 | Hephaestus + Explore | `skill-index`, `reference-index`, `policy-data-fetch-layer` | 임시값·mock·query·props codemap |
| 계약 | Hephaestus | `recipe-data-dto`, `policy-type-definition`, `recipe-api-authoring` | Zod 기반 typed response contract |
| 구현 | Hephaestus | `programming`, `policy-coding-convention` | UI 외부 기능 로직 연결 |
| 검토 | Watcher 문서 판정 | `policy-review-checklist` | 범위·타입·동작 PASS/FAIL |
| 평가 | Evaluator 문서 기록 | `policy-documentation` | 후속 backend 계약 위험 기록 |

## 구현 순서

1. parser와 presentation 경계에 실패 테스트를 추가한다.
2. DTO schema와 MSW fixture/handler를 확장한다.
3. presentation mapper와 pages route props를 응답 필드로 연결한다.
4. focused test, `npm run build`, `npm run lint`와 실행 표면을 검증한다.
5. 필수 문서 7종을 작성하고 신규 변경을 별도 커밋한다.

## 승인

- 상태: approved
- 근거: 사용자의 `지금 UI에 있는 임시 데이터들을 mock을 사용해서 API 응답에 따라 데이터를 받을 수 있는 구조로 변경해봐.`
