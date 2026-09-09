# 평가 로그

## 현재 판정과의 경계

여기서는 문서 자체의 PASS 판정을 다시 평가하지 않고 장기적인 하네스 개선 방향만 기록한다.

## 장기 관찰 사항

- 사용자 금지 지시는 project context 또는 executable policy로 외부화하지 않으면 compaction에서 약화될 수 있다.
- UI·기능 병렬 세션은 역할 이름보다 경로 ownership과 conflict protocol이 중요하다.
- 화면별 browser·capture·Oracle fan-out은 짧은 기간에 child session과 cache read를 크게 증가시켰다.

## 목록에 등록할 재사용 가능 자산

- session identity 기반 Python governance pattern
- host adapter별 공통 deny policy 설계
- Hephaestus/Claude production path ownership contract

## 기술 부채

- user-ui `.codex` 정책과 OpenCode tool boundary가 직접 연결되지 않았다.
- user-ui post-approval UI/browser/Watcher hard deny가 없다.
- admin-ui 하네스가 Git에서 제외돼 있다.

## 프로세스 개선 사항

- 금지 지시를 transient todo가 아니라 system-injected project contract에 기록한다.
- compaction 직후 active goal보다 최신 사용자 prohibition을 먼저 재검증한다.
- QA fan-out과 child session 수에 task별 budget을 둔다.

## 권고 사항

admin-ui 동일화 시 단순 파일 복사보다 공통 Python policy core와 Codex·Claude·OpenCode adapter를 분리하고, 각 host에서 같은 deny regression test를 실행한다.
