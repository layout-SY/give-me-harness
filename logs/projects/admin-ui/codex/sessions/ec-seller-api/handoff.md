# EC 판매자 Logic 인계

- requested_roles: Logic
- confirmed_roles: Logic (inject)
- completed_roles: Logic 구현·검증
- next_role: UI(보류 기능 재개 시 제안) / 실제 명세 연결은 Logic

## 현재 상태와 근거

사용자는 기존 EC UI에 API·MSW 연결을 요청하고 임시 계약 설계를 위임했다. v1을 제외하고 추가 UI는 보류했으며 2026-10-02 구현 진행을 승인했다. 기존 View props를 기준으로 `controller -> UI` 방향으로 구현했다.

프로젝트 `asan-metaverse-admin-ui`, branch `feature/ec-seller-ui`, HEAD `b6fc92d2eed80a4920cc4681bda7f44a3565a8f5`, 실제 worktree·다음 작업 위치는 `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/ec-seller-ui`다. UI 인계 기록상 직접 부모는 `sy-main`이며 이번 작업에서 관계 등록·병합은 하지 않았다.

모든 API 연결은 미커밋 상태다. staged 변경은 없다. 기존 추적 page 9개·shell·MSW registry·app 시작/감시·mock 정책 테스트를 수정했고, `entities/ec-seller`·`features/ec-seller`·각 page hook/lib·EC MSW 3파일·EC 테스트를 추가했다. `.env.local`은 로컬 환경 설정으로 보존해야 한다. 기존 UI commit과 다른 worktree의 작업을 변경하지 않았다.

## 재개 작업

같은 branch·worktree에서 순차로 작업한다. 소스 수정 전 최신 HEAD·dirty와 아래 계약을 확인한다. 사용자 Git 승인은 아직 없으므로 commit·merge는 별도 승인 대상이다.

| 보류 대상 | 연결 위치·계약 | 필요한 작업 |
| --- | --- | --- |
| 상품 이미지 추가 | `pages/ec-product`, `onImageAdd` | 업로드 선택 UI·파일 전달 계약 확정 후 이미지 API 연결 |
| 상품 옵션 편집 | `onOptionsEdit`, `values.options` | 편집 UI·추가/삭제/재고 입력 callback 확정 |
| 주문 수령인 수정 | `pages/ec-order`, `onRecipientEdit` | 편집 UI·저장 DTO/mutation 추가 |
| 배송 추적 | `onTrackShipment` | 조회 URL/화면·외부 서비스 계약 확정 |
| 전체 문의 이력 | `pages/ec-inquiry`, `onHistoryOpen` | 기존 최근 3건 외 전체 화면·조회 계약 |
| 약관·개인정보·도움말 | `pages/ec-seller-apply` callback | 실제 콘텐츠·경로 제공 후 연결 |
| 카테고리 상세 | `pages/ec-settlement`, `onCategoryDetailOpen` | 상세 화면·조회 계약 |
| 대시보드·차트 | 기존 UI 보류 | 사용자 재개 요청 후 별도 UI 구현 |

보류 callback은 `features/ec-seller/model/ec-display.ts`의 `ecDeferred`다. 새 UI를 현재 Logic 역할에서 임의로 추가하지 않았다. 역할 재개 시 실제 필요 범위를 확인한다.

## 실행·검증

이 worktree에서 `npm run dev` 실행. `.env.local`의 `VITE_ENVIRONMENT=dev`가 MSW를 활성화한다. 인증 흐름은 기존 계약을 사용한다. MSW 상태는 새로고침 시 초기화된다.

공통 formatter → lint·build → 관련 Node 테스트 42개 통과. 브라우저 시각 QA·실제 서버·독립 Watcher는 미실행. [최종 요약](final-summary.md), [임시 API 계약](unknown/api-contract.md)에 검증 명령과 제한을 기록했다.

새로운 서버 명세 연결에는 task-role-routing·git-branch-strategy·api-authoring·data-fetch-layer·validation 스킬을 사용하고 DTO와 기존 View 차이를 확인한다. UI 추가는 올바른 UI 역할 세션에서 자산 선정과 연결 계약을 계획한다.

## 후속 커밋 요청 상태

커밋 작업 `a7b4b736e8d6fba16887c902d70d124b` 완료. 사용자 재승인 후 종료된 문서 패치의 미확인 기록을 별도 승인된 복구 절차로 해소하고, 기존 승인으로 stage·commit을 실행했다. 현재 HEAD는 `bbb337d` (`feat(ec): 판매자 API와 MSW 연결`)이며 `git status --short` 출력이 없다. 위 본문의 미커밋 상태는 이 기록으로 갱신한다. 병합·push는 수행하지 않았으며 병합 승인은 여전히 없다. [최종 요약](final-summary.md)에 실패·복구·완료 이력을 기록했다.
