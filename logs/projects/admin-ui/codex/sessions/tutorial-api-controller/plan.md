# 튜토리얼 API와 controller 구현

## 승인된 범위와 계약

- 역할: logic, owner. 사용자 최초 요청과 신규 작성·필드·순서·응답 계약 답변의 `작업 진행` 승인으로 구현한다. 추가 답변으로 등록도 `images: null`을 허용한다.
- 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main`, 조사 HEAD `bc579b39278387f9b2e5b6f5bcce4a274249308c`. 작업 시작 시 미커밋 변경 없음. Git 변경은 요청하지 않았으며 수행하지 않는다.
- 목표: Swagger 튜토리얼 관리 6개 API를 UI 없는 controller까지 구현하고 양방향 계약을 검증한다. Logic 선행 `controller <- UI`이며 화면·라우트 구현은 포함하지 않는다.
- 근거: `https://admin-api.oasis.shovvel.com:8443/v3/api-docs`의 `/admin/tutorials`, `/admin/tutorials/{tutorialId}`, `/admin/tutorials/images`.
- GET 목록은 페이지 없는 배열이며 `id/name/pageCount/createdAt/updatedAt`, 상세는 `id/title/images` 및 이미지 `id/imageUrl`을 모두 필수로 받는다. `imageUrl`만 nullable이다.
- POST/PATCH title 필수, images 생략·null·배열 허용. 각 전송 이미지의 imageUrl과 sortOrder 필수, imageUrl 값만 nullable. UI 배열 입력은 입력 순서를 보존하며 sortOrder를 0부터 부여한다. PATCH 생략/null은 이미지 유지, []는 전체 삭제다.
- 업로드는 비어 있지 않은 file을 multipart로 전달하고 URL 문자열을 받는다. 업로드만으로 튜토리얼에 연결되지 않는다. 등록·수정·삭제 성공 payload는 null이고 공통 mapper의 undefined 정규화를 수용한다.
- ID는 목록/상세 응답의 튜토리얼 ID를 UI가 상세·수정·삭제 동작에 전달한다. 이미지 응답 ID는 저장 payload에 넣지 않는다. 등록 성공에는 생성 ID가 없다.

## 조사와 재사용

- `src/shared/api/common/response.dto.ts`, `api-client.ts`, `common/api-result/*`: envelope는 기존 client가 처리한다. 목록이 배열이므로 pagination DTO는 사용하지 않는다.
- `src/entities/maintenance/{api,model,hook}`, `src/entities/items/api/item-category.api.ts`: factory, unknown parser 경계, Query options·mutation 및 cache invalidation 구조를 사용한다.
- `src/entities/video/api/video.api.ts`: FormData file 전송 및 Axios multipart 처리 패턴을 사용한다.
- `src/pages/maintenance/{hook,model,lib}`, `src/pages/cp-news/ui/cp-news-form-page.tsx`: UI 없는 controller·공개 타입·mapper와 실제 UI 사용 구조를 확인했다. 도메인별 상태이므로 기존 controller를 가져다 쓰지 않고 사용자 승인에 따라 신규 작성한다.
- `src/shared/ui` 조사 완료. 이번 범위에는 UI 작성이 없다. 기존 튜토리얼 구현은 src 조사에서 확인하지 못했다.
- 공통 에러 reporter는 서버 오류 표시를 담당한다. controller는 실패 여부와 입력/전송/응답 형식 오류를 제공하며 같은 서버 오류의 중복 메시지 표시는 만들지 않는다.
- 스킬: task-role-routing/git-branch-strategy로 범위·승인 확인, api-authoring/data-fetch-layer로 전송·Query·controller 분리, coding-convention/type-definition/validation으로 타입·순수 mapper·입력 검증, implementation-quality/documentation으로 포맷·검증·산출물 기록.

## 수행 항목

1. 현재 worktree의 `src/entities/tutorials`에 DTO/schema, parser, 6개 API factory, Query key/options·mutation/hooks와 public API를 신규 작성한다.
2. `src/pages/tutorial`에 목록·상세·동작 controller와 공개 타입·mapper를 작성한다. 서버 상태는 Query에 두고 중복 요청·unmount 취소·명시적 결과 반환을 제공한다.
3. `tests/tutorial-*.test.mjs`에서 기존 node:test·tsx/Vite·MSW로 필드·null·순서·전송·캐시·controller·취소 경계를 확인한다. 테스트 외 런타임 mock과 실제 데이터 변경은 수행하지 않는다.
4. 중앙 `formatting.py apply` 후 `node --test tests/tutorial-*.test.mjs`, `npm run lint`, `npm run build`를 실행한다. package.json에 test script는 없어 기존 Node 테스트 방식으로 실행한다.
5. 같은 세션의 final-summary와 UI 인계용 계약 문서에 결과·검증·제한을 기록한다.

## 진행 기록

- 후속 커밋 완료: 사용자 `명령 실행 승인` 후 보호 작업 `26b0b445ff7bdb80c49f0e2b9a9a7ffd`로 변경 3개를 커밋했다. commit `811c8bbc4570572e4167c4aeef5e62ea2ac8e6a6`, 메시지 `feat(tutorial): 제목 길이 및 페이지 편집 규칙 적용`. feature/tutorial clean 확인, push·merge 미실행.
- 2026-10-02 후속 완료: editor controller·공개 타입·테스트 3개 수정. 확정된 코드 포인트 30자·등록 빈 칸 3개·최대 20개·빈 칸 추가 금지·초과 데이터 감소 후 저장을 구현했다. 공식 Prettier 성공, 튜토리얼/이미지 슬롯 테스트 29/29, lint·build·diff --check 통과. 최신 HEAD는 UI 1차 `2967764e611adccf2db3723006db19a991eafe5a`, 후속 변경은 미커밋이다. controller 계약과 UI 2차 handoff를 갱신했다.

- 2026-10-02 UI handoff 후속 보완: 사용자 추가 작업 진행 요청과 두 미정 항목 답변으로 계약 확정. 실제 작업 위치는 tutorial worktree, feature/tutorial, HEAD `2967764`, dirty 없음이다. UI 커밋을 보존하고 기존 editor controller·공개 타입·controller 테스트만 확장한다.
- 후속 계약: 제목 최대 30자를 Unicode 코드 포인트로 계산하고 titleLength/titleMaxLength를 공개한다. 등록만 [null, null, null]로 시작한다. 페이지 최대 20개, 빈 칸이 없고 편집 가능할 때만 추가한다. 기존 20개 초과 서버 값은 표시하되 20개 이하로 줄여야 저장 가능하다. onImagesChange도 개수 증가를 검증하며 초과 데이터의 단계적 감소는 허용해 기존 UI 삭제 경로를 유지한다. 업로드로 직접 끝에 추가하는 onAddImage에도 같은 추가 조건을 적용하고 기존 칸 교체용 uploadApi는 유지한다.
- 후속 공개 계약: fields.titleLength/titleMaxLength/maxImages/canAddImage/imagesError를 제공하고 초과 페이지 오류는 save.errorMessage에도 반영한다. API DTO에 명세 밖의 최대 길이·개수 제한을 추가하지 않는다. UI가 새 카운터·버튼 계약을 사용하는 것은 다음 UI 단계다.
- 적용 스킬과 근거: api-authoring/ui-controller의 기존 controller 확장, coding-convention/type-definition/validation의 타입·순수 검증 규칙. 확인한 재사용 대상은 useTutorialEditorController, tutorial-controller.types, 기존 API DTO·mapper, tutorial-editor-view 및 ImageManager useImageSlots다. 신규 추상화·외부 패키지는 필요 없다.
- 후속 검증 계획: 기존 SSR/MSW 테스트로 30/31 코드 포인트(이모지 포함), 등록 3칸·수정 원본 유지, 빈 칸·20개 추가 차단, 배열 입력·직접 업로드 경로, 기존 초과 데이터의 단계적 삭제 후 저장을 검증한다. 공식 Prettier 후 관련 테스트 및 lint·build를 실행한다. 후속 변경 commit·merge 승인은 아직 없다.
- 2026-10-02 이동 사본 정리 완료: primary의 미추적 튜토리얼 소스·테스트 18개가 이동 당시 원본과 같고 최신 tutorial에 보존됨을 재확인했다. 사용자 제거 요청 및 `진행` 승인 후 18개를 삭제했다. sy-main과 feature/tutorial 모두 clean, tutorial HEAD `6b96d7b7f824805dd39c4f2dbd17a0955a0f6d77` 유지 확인. primary의 세션 문서는 이력으로 보존했다.
- 커밋 완료: 사용자 `명령 실행 승인` 후 보호 작업 `f31b1fb97e1b01f9824356e0eade5fe7`로 tutorial 소스·테스트 19개를 커밋했다. commit `6b96d7b7f824805dd39c4f2dbd17a0955a0f6d77`, 메시지 `feat: 튜토리얼 API 및 controller 구현`. worktree clean 확인, push·merge 미실행. primary의 이전 사본은 이번 Git 작업에 포함하지 않았다.
- 최신 검증 결과: 공식 formatter check·apply 성공(19개 파일), 튜토리얼 테스트 19/19 통과, 전체 lint·build exit 0. 포맷 차단은 현재 실행에서 재현되지 않았다. prepared 복구 operation은 재실행하지 않았다.
- 이동 정리 확인: primary의 원본 소스·테스트 18개와 자기 문서 2개가 이동 당시 원본과 완전히 일치했다. 삭제 요청은 해당 위치의 사용자 구현 승인 부족으로 실행 전 차단돼, 구체적인 원본 정리 확인을 요청했다.

- 최신 상태: tutorial worktree에 소스·테스트 18개 전달 후 편집 controller를 추가해 총 19개 파일을 작성했다. 목록 name/title의 동일 의미와 편집 controller·FormData adapter 보완은 사용자 확인을 받았다. 기본 checkout의 이전 사본 삭제는 해당 위치의 구현 승인 검사에 차단되어 보존 중이다.
- 의존성: tutorial worktree에서 `npm ci --offline --no-audit --no-fund` 성공. 포맷·테스트·lint·build는 미완료다.
- 현재 차단: 중복 대상 오류로 종료된 apply_patch 호출 `exec-c86ba388-fe06-407c-8c94-6031492f7a0f`의 쓰기 예약 `0973a25795b4d169eec78f84a91a9a9891139622cacd484051510ecfa6d4641d`가 남았다. 후속 정상 수정으로 대상 5개 파일 구현은 완료됐다. 공식 write-recovery 작업 `20473861be1147babe771ca53d99d5fc`를 준비하고 사용자 `명령 실행 승인`을 받았다.
- 복구 실행 결과: 도구 workdir를 tutorial로 지정한 execute는 `승인 대상의 실제 실행 위치와 다릅니다`로 실행 전 차단됐다. literal cd로 같은 위치를 지정한 호출도 `python -I로 직접 실행하세요`로 차단됐다. 복구는 아직 실행되지 않았다. 같은 실패를 반복하거나 중앙 상태를 직접 수정하지 않는다. tutorial을 launcher의 실제 cwd로 재개하여 동일 승인 작업을 확인해야 한다.
- 작업 위치 변경 승인: 사용자가 UI 제공 공간으로 이동하고 없으면 신규 생성을 요청했다. UI handoff의 `feature/tutorial`·`tutorial`은 제안이며 실제 공간이 없었고, `명령 실행 승인` 후 보호 작업 `57f7f17dbf284ab88cc3e19ce8e35d67`로 생성 완료했다.
- 새 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`, branch `feature/tutorial`, HEAD `987616b724273b63b1d8c7037679402ad26f7c87`, 직접 부모 `sy-main`. 기존 HEAD 이후 변경은 usage 도메인과 관련 테스트에 한정되어 튜토리얼 재사용 경로와 겹치지 않는다.
- 새 위치에서 정책·공통 응답/client·maintenance controller·ImageManager 계약 재탐색 완료. 자기 plan과 controller 계약 문서 전달 완료. 소스·테스트 18개 전달은 새 worktree의 `사용자 구현 승인` 검사에 차단됐으며 원본은 primary checkout에 보존돼 있다. 아직 파일 이동 완료로 보고하지 않는다.
- UI handoff 추가 확인: primary checkout의 `.claude/logs/sessions/튜토리얼-관리-UI/handoff.md`. Logic 선행, 목록/상세 분리, 순서 변경과 빈 자리 추가, ImageManager 확장이 UI 범위라는 결정이 있다. 현재 API·기본 controller는 원래 요청 계약을 구현했으며, handoff가 제안한 제목·슬롯 편집 상태/callback과 FormData 업로드 adapter는 아직 추가하지 않았다. 목록 name과 상세 title의 의미 일치 여부는 handoff에도 미확정으로 남아 있어 사용자 확인 대상이다.
- 요청 명확성: clear. 최초 4개 질문 및 등록 images null 추가 질문까지 사용자 답변 완료.
- 구현 승인: 완료. 재사용 기반 신규 도메인 작성 승인 완료.
- 도구 실행 결과: 사용자 대화상 승인은 확인되지만, 계획 작성 후 최초 source apply_patch가 PreToolUse에서 `사용자 구현 승인` 미충족으로 차단됐다. 소스 쓰기는 실행되지 않았다. 현재 계획에 대한 하네스 승인 재확인이 필요하며 동일 변경을 반복하거나 우회하지 않는다. 테스트·lint·build는 구현 전이므로 아직 실행하지 않았다.
- 후속 사용자 `진행` 승인 및 현 worktree 재사용 자산 재확인 후 source 쓰기 성공. entities 10개·pages 6개·테스트 2개 파일 작성 완료. UI 연결 계약은 `unknown/controller-contract.md`에 기록했다.
- 포맷 차단: 같은 worktree의 Claude 세션 `c4cc0ffa-4df7-4879-960f-951115025535`, call `toolu_01Wv68MEYQpgaB82ggzkfjif`, write ID `140e0aaae8c35f46c372f7bbbe6035fbe82baaea3d2251c5f8c110c00d9ca46b`가 결과 미확인으로 남아 있다. 사용자에게 해당 작업의 실행/종료 여부를 질문했다. 기록을 임의 삭제하거나 포맷/검증 gate를 우회하지 않는다.
