# 페이지 목록 응답 통일

## 결론과 승인

사용자가 2026-09-21 `작업 진행`으로 구현 계획을 승인했다. Logic 역할로 기존 공통 `PageResponseDto`와 `createPageResponseSchema`를 재사용해 페이지 목록을 `items/total/page/size`로 통일한다.

## 확정 계약

- 서버 응답 자체가 공통 구조를 사용한다. 네 필드는 필수·null 불가이며 page와 size는 양의 정수다.
- 페이지네이션 없는 배열 응답과 항목별 상세 필드의 기존 계약은 유지한다.
- 부가 집계 필드는 선택·nullable로 유지한다.
- 공지도 공통 구조를 사용한다. total에는 고정 공지를 포함하며 size는 일반 항목 수다. 고정 3개와 size 10이면 13개를 표시한다. 고정 항목은 각 페이지에 추가되므로 일반 페이지 수는 고정 항목을 제외해 계산한다.

## 작업 위치와 보존

- 프로젝트·workdir: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- branch: `sy-main`, 시작 HEAD: `2b9ca35bd20fb9b071d18655e859576fc9a02e49`
- 기존 untracked `PR_sy-main-to-dev.md`는 보존한다.
- Git 변경 작업은 요청·승인되지 않았다.

## 수행 순서

1. `src/shared/api/common/`의 공통 DTO를 재사용하고 이벤트·공지·영상의 목록 계약과 controller를 맞춘다.
2. CP·DAO·가상오피스와 기존 페이지 목록의 응답·화면 연결·mock을 동일 계약으로 변경한다. endpoint와 비페이지 응답은 유지한다.
3. 기존 node:test 계약·controller·MSW 테스트를 갱신하고 필수 필드, 부가 집계 누락/null, 공지 고정 항목과 페이지 경계를 검증한다.
4. 중앙 `formatting.py apply`를 실제 workdir에서 실행한 다음 lint, 테스트, build를 실행한다.

## 적용 스킬과 근거

task-role-routing, git-branch-strategy, coding-convention, type-definition, data-fetch-layer, abstraction-strategy, implementation-quality, documentation, recipe-data-dto 및 transport-contracts를 확인했다. 공통 DTO와 이벤트·공지·CP 목록 parser·hook, Table 및 mock-table의 실제 사용처를 조사했다.

## 완료 기준

페이지 응답에 기존 totalElements/totalPages 또는 content/count/pagination 계약을 남기지 않고 공통 타입을 사용한다. 일반 배열과 UI 내부의 페이지 표시용 pageCount는 유지 가능하다. 공지 13개 표시와 정확한 마지막 페이지, optional/nullable 집계에서 조회가 유지되는 것을 테스트로 확인한다.

## 완료 결과

전체 구현·포맷·검증을 완료했다. 47개 테스트 파일의 338개 테스트와 lint, build가 통과했다. 작업 중 외부에서 sy-main HEAD가 `e9292a5351fe7f087b1f29f1c5245f027f3d1115`로 변경되었으며, 시작 HEAD 이후 차이는 Docker·CI·배포 문서뿐으로 이번 소스·테스트 변경과 겹치지 않는다. 해당 변경과 기존 PR 문서를 보존했다. 이 세션에서는 Git 변경 명령을 실행하지 않았다.
