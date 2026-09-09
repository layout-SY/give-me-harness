# 탐색 결과

## 결론

토론 전용 DTO·parser와 상태 흐름을 보완하고 기존 UI 계약에 연결한다. 사용자 요청에 따라 최신 sy-main에서 새 워크트리를 생성했다. 기존 discussion 작업에만 존재하는 커밋이나 시민참여 소스 차이는 없었다.

## 현재 확인한 사실

- 기존 9월 7일 handoff·plan·exploration·implementation-log를 읽었다. 구형 훅으로 첫 source patch가 차단돼 구현은 없었다.
- PDF 8~9쪽을 pdftotext로 다시 읽었다. 내 활동, 목록·상세, 진행 중 결과 비공개, 종료 후 집계, 진행 기간 내 의견 등록, 미저장 복귀 확인이 요구된다.
- discussion API는 공용 Content DTO를 사용하고 목록·상세 parser도 공용이다. 참여 요청은 `/participations`에 choice를 전송한다.
- detail route는 mutation variables의 id만 일치하면 서버에 저장된 개인 선택을 무시한다. 완료 여부도 응답의 completed 값을 고려하지 않는다.
- comment DTO와 toCommentItem에서 stance를 보존하지 않는다. 공용 댓글 hook의 작성 조건은 로그인뿐이어서 토론 종료 상태가 반영되지 않는다.
- 브라우저는 testing.ts의 citizenParticipationHandlers를 등록하며 collection wildcard가 토론 목록·상세·댓글·신고까지 처리한다.
- 기존 토론 UI는 제어형 props/callback, 완료 표시, 등록 비활성, 댓글 notice를 제공한다. UI 파일 수정 없이 기능을 연결할 수 있다.

## 재사용 자산

| 후보 | 결정 | 이유 |
| --- | --- | --- |
| shared/api ApiClient·ApiResult·mapApiResult | 재사용 | 기존 응답 envelope와 오류 경계 보존 |
| vote API·parser 패턴 | 참고 | 인접 typed API와 요청 취소·인증 구성 |
| TanStack Query·queryKeys | 재사용 | 필터·페이지별 캐시와 최소 무효화 |
| useCitizenCommentActions | 필요한 입력 계약만 확장 | 토론 등록 가능 조건을 UI와 실제 제출에 함께 적용 |
| shared/ui/dialog useDialog | 재사용 | 미저장 입력 확인과 의견 제출 안내 |
| DiscussionListPage·DiscussionDetailPage | 재사용 | 기존 시각 계약과 callback 활용 |

## 적용 스킬과 준비 상태

중앙 snapshot의 필수 역할·브랜치 스킬, Logic·handoff·pipeline 문서, coding-convention, type-definition, data-fetch-layer, implementation-quality, validation, documentation, recipe/api-authoring, skill-index를 읽었다. 신규 워크트리에서 실제 API·UI·route·상태·테스트를 다시 확인했다.

현재 assignment는 새 브랜치·워크트리에 귀속됐고, harness 상태의 implementation_approved·skill_confirmed·exploration_completed가 모두 true임을 읽기 전용으로 확인했다. 상태 파일은 수정하지 않았다.

## 검증 대기

이전 세션의 525개 중 6개 실패 기록은 참고만 하며, 현재 워크트리에서 기준 테스트를 새로 실행한다. 실제 백엔드 명세와 실제 서버 응답은 제공되지 않았다.
