# 구현 기록

요청한 동시 호출 규칙을 user-ui에 적용하고 중앙 API 스킬을 실제 패턴에 맞춰 확장했다.

## 변경

- user-ui src/shared/lib/hooks/use-api.tsx: activeRequestCountRef→seqRef. 호출별 currentSeq를 잡아 resolve/catch에서 최신 요청만 반영한다. finally는 mounted && latest일 때만 loading=false. 공개 ExecuteResult, 실패 reporter 옵션, controller Set·unmount abort는 유지했다.
- 같은 폴더 use-api.test.tsx: deferred reject 지원, 두 완료 순서, 오래된 업무 실패/throw 무시, 최신 실패 시 loading 종료를 검증한다. 기존 단일 요청·오류 옵션·취소 검증을 유지했다.
- 중앙 api-authoring: 앱별 기존 factory 명명과 FSD 경계를 허용하고 transport-contracts/query-mutation 참조를 추가했다. data-fetch/data-dto와 admin use-api 설명의 충돌도 정리했다.
- 전역 AGENTS.md: React 18·Jotai 및 이전 프로젝트/버전/빌드 고정을 제거하고 현재 package·lockfile·source를 확인하도록 바꿨다. 기존 승인 절차와 일반 코딩 지침은 보존했다.
- docs: API 조사·개선 보고서, 62행 전수 목록, 활성 세션 6개의 포트폴리오 조사와 JSON 증거를 작성했다.

## 회귀 확인

새 테스트를 먼저 소비자에 적용했다. 기존 useApi는 5 실패/14 통과였다. 소스 변경 후 직접 소비처를 포함한 36개 테스트가 통과했다. 전체 suite는 38 실패/720 통과이므로 전체 통과로 주장하지 않았다.

## 경계

중앙 repo와 두 소비자에 기존 dirty 변경이 있었다. 계획된 중앙 파일은 수정 직전 내용을 백업해 이번 변경과 구분했고, 소비자 두 파일·전역 안내는 checksum을 확인한 정확한 파일만 적용했다. admin API와 다른 세션의 로그는 읽기만 했다. 초기 구현 단계에서는 사용자 승인 아래 외부 경로를 수정했고, commit·merge·다른 세션 종료는 수행하지 않았다. 후속 커밋 요청의 결과는 아래에 기록한다.

## 후속 요청: 작업 단위 커밋

사용자의 “작업 단위 커밋” 요청에 따라 중앙 공통 스킬과 user-ui 구현을 별도 커밋했다.

- 중앙 `main`: `34f2dab` — `refactor: 공통 API 연결 스킬과 요청 수명 규칙 정리` (6개 파일).
- user-ui `sy-main`: `57c88ac` — `fix: useApi 동시 요청을 최신 호출 기준으로 처리` (구현·회귀 테스트 2개 파일).
- 조사 문서·검증 근거·이번 세션 산출물 7종은 별도의 문서 커밋으로 묶는다.

작업 시작 시 보관한 원본과 비교해 api-authoring의 기존 2·6·9번 지침 변경은 스테이징에서 제외했다. 기존 다른 세션의 소스·정책·로그 변경은 보존했다. 전역 `/Users/okand/.codex/AGENTS.md`는 Git 저장소 밖이어서 수정 상태만 유지한다. 구현은 검증 당시 내용과 동일하며 기존 테스트 결과·전체 suite 실패 제한을 유지한다.
