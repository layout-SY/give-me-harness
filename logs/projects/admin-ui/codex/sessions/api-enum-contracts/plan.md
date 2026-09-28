# 계획

## 목표와 범위

사용자가 제공한 `/Users/okand/Downloads/enums/`의 Java enum과 현재 요청·응답 DTO를 맞춘다. 작업 위치는 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, 브랜치는 `sy-main`, 시작 HEAD는 `c3927095a58bc7814f28348b8ae94e11228a4627`이다.

- 아이템: 기존 `ITEM_GENDERS`, `ITEM_STATUS`, `ITEM_PAYMENT_TYPES`와 공통 DTO 스키마를 재사용한다. gender를 `COMMON/MAN/WOMAN`으로 변경하고 검색·폼·이벤트 검색·채번 타입을 연결한다. 상태·결제 방식도 확정 enum으로 검증한다.
- 이벤트: 기존 설정 스키마를 확장하여 출석 11개·룰렛 8개 키를 도메인별 요청·응답에서 검증한다. 두 화면이 공유하는 설정 hook·payload의 키 타입을 보존한다.
- 점검: 기존 설정 조회·수정 DTO의 configKey를 Java의 8개 키로 제한한다.
- 이미 일치하는 문의·뉴스·시민 제안·이벤트 type·사용자 상태 변경 계약은 검증한다.

## 확정 사항과 제외 사항

- 사용자 지시: “이거까지 전부 반영하면 돼.” 이후 필수 계약 질문의 답변을 모두 받았다. 최초 소스 수정은 승인 미기록으로 차단됐으나, 사용자의 명시적 `진행` 승인 후 구현을 적용했다.
- ItemGender는 앞선 복수형 설명 대신 Java 파일의 `COMMON/MAN/WOMAN`을 사용한다.
- DeviceOs는 해당 DTO 구현 전이므로 이번 작업에서 보류한다.
- 사용자 상세 응답의 `WITHDRAWN` 허용은 유지한다.
- ProposalStatus·VoteChoice는 시민참여 계약에만 적용한다. 기존 `/v1/dao`, `/v1/cp` 계약은 유지한다. 현재 시민 투표 관리자 DTO에는 VoteChoice를 받거나 반환하는 필드가 없다.
- null 허용·필수 여부·채번 숫자 규칙·공통 응답 envelope·페이지 구조는 유지한다.
- 기존 미추적 파일 `PR_sy-main-to-dev.md`를 보존한다. 후속 사용자 요청 `sy-main에 직접 커밋` 및 `명령 실행 승인`에 따라 이번 변경 21개 파일만 stage·commit한다.

## 역할과 재사용 근거

- 역할: inject로 확인된 Logic, 산출물 책임 owner.
- 적용 스킬: task-role-routing, git-branch-strategy, coding-convention, type-definition, data-fetch-layer, implementation-quality, documentation, abstraction-strategy.
- 근거: `src/entities/items/`, `src/entities/event/api/`, `src/widgets/event-admin/lib/event-config.ts`, `src/widgets/event-admin/hook/use-event-configs.ts`, `src/entities/maintenance/api/maintenance.dto.ts`, `src/shared/api/common/response.dto.ts`와 기존 계약·통합 테스트.

## 수행 및 검증

1. 현재 작업 위치에서 기존 상수와 스키마를 확장하고 소비하는 상태·hook 타입을 연결한다.
2. 기존 `node:test`/tsx/Vite 테스트에서 숫자 gender와 미확정 문자열 기대값을 확정 계약으로 교체한다. 허용값·거부값·nullable·출석/룰렛 키 혼용 방지·전송 payload를 검증한다.
3. 중앙 `formatting.py apply`를 실행한 후 관련 테스트, `npm run lint`, `npm run build`를 수행한다. package.json에는 test script가 없어 기존 `node --test` 실행 방식을 사용한다.
4. diff와 실행 결과를 검토하고 final-summary.md에 실제 변경·검증·남은 범위를 기록한다.

## 검증 및 복구 결과

- 소스 14개·테스트 7개 파일 수정 완료, `git diff --check` 통과.
- 자동 포맷을 막던 이전 Codex 세션의 미확인 쓰기 기록은 사용자 `명령 실행 승인` 후 보호 실행기로 해소했다.
- 이전 세션 `01a0c1d7-b319-7873-9cb3-77e5bc2e2467`, 호출 `exec-19a9036c-ece1-4648-b93e-84a93e5e71bd`, 쓰기 기록 `3d8127caf5626ae3840403846c1f1ed82aa208e176a0c116467cf5a369f940ce`.
- 해당 시각 세션 로그에서 macOS 로그 조회가 sandbox 오류와 exit_code 64로 종료된 것을 확인했다. 현재 프로세스 목록에서도 로그 조회·소스 쓰기·포맷 프로세스가 없음을 확인했다.
- 보호 실행기의 write-recovery 작업 `be5cb8babe834eb59eb4c706be658d58`을 한 번 실행해 stage done을 확인했다. 소스·Git 복원·삭제는 수행하지 않았다.
- 21개 수정 파일의 중앙 자동 포맷 성공. 관련 15개 테스트 파일의 139개 테스트, `npm run lint`, `npm run build` 모두 통과했다. 완료 내용은 final-summary.md에 기록한다.

## 직접 커밋 결과

- 인증·메뉴 변경이 반영된 `sy-main` HEAD `c739a91fef5a687123bf4851419224720068830b`에서 재검증했다. 공식 포맷 명령은 추가 변경 없이 성공했고, 기존 15개 테스트 파일에 인증·메뉴 5개 파일을 더한 172개 테스트와 lint·build가 모두 통과했다.
- 보호 실행 작업 `0d2e26e2c75c629b5edc36d316dd0738`은 최초 잠금 파일 권한 오류 및 재승인 요구 후, 사용자 승인과 쓰기 권한을 받아 stage done으로 완료했다.
- 커밋: `e8061323543fcf350e43515f482858da50b6d93b`, 메시지: `fix(api): 요청·응답 DTO에 서버 enum 계약 반영`.
- 커밋은 21개 파일, 351줄 추가·113줄 삭제다. 추적 파일의 남은 변경은 없고, 기존 미추적 `PR_sy-main-to-dev.md`만 남아 있다. merge·push는 수행하지 않았다.
