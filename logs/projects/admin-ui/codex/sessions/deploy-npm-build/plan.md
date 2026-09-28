# 계획

## 목표

`sy-main → dev` 병합 후 Docker가 삭제된 `yarn.lock`을 복사하다 실패하는 문제를 해결한다. 배포 설정을 현재 프로젝트의 npm 계약에 맞춰 `sy-main` 작업 트리에 반영한다. push는 사용자가 수행한다.

## 작업 유형과 범위

- 유형: 배포 설정 오류 수정 및 관련 문서 갱신.
- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main`, 시작 HEAD `e9292a5`.
- `Dockerfile`: `package-lock.json` 복사, npm 10.9.3 설치, `/root/.npm` 캐시, `npm ci --include=dev`, `npm run lint`, `npm run build` 사용.
- `.dockerignore`: npm lockfile 제외 규칙과 오래된 설명 제거.
- `docs/deploy-onprem.md`: npm 설치·lockfile 관리 안내로 갱신.

## 제약 조건과 재사용 근거

- 기존 `package.json`의 `packageManager: npm@10.9.3`, `build`, `lint` 스크립트를 재사용한다.
- `.github/workflows/deploy.yml`의 Docker stage 호출, 환경변수 주입과 배포 순서를 유지한다.
- `docker/entrypoint.sh`와 `src/shared/api/axios-instance.ts`의 `VITE_API_BASE_URL` 연결 및 자리표시자 계약을 확인했다.
- 기존 API·DTO·hook·화면·테스트 미커밋 변경과 `PR_sy-main-to-dev.md`는 이번 수정에 포함하지 않는다.
- 실행 중인 Docker 엔진이 없어 전체 컨테이너 빌드는 현재 검증할 수 없다.
- 다른 작업자가 사용할 수 있는 `node_modules`를 재설치하지 않고 `npm ci --dry-run`으로 lockfile 정합성을 검사한다.

## 스킬 및 역할

- 역할: 세션에서 확인된 Logic. 패키지·빌드 설정 수정 책임 범위.
- 적용 스킬: `policy-task-role-routing`, `policy-git-branch-strategy`, `skill-index`, `policy-coding-convention`, `policy-implementation-quality`, `policy-documentation`.
- 산출물 책임: owner.
- Git 변경: 별도 승인이 필요한 stage·commit은 검증 후 세 파일만 대상으로 제시한다. push는 수행하지 않는다.

## 검증

1. 프로젝트 루트에서 npm 설치 dry-run으로 `package.json`과 `package-lock.json`의 정합성을 확인한다.
2. 공통 포맷 트리거를 실행하고 대상 변경 diff를 확인한다.
3. `npm run lint`와 CI 자리표시자를 주입한 `npm run build`로 린트·타입·번들 생성을 확인한다.
4. 생성 번들에서 `__RUNTIME_VITE_API_BASE_URL__` 유지 여부와 배포 파일에 Yarn 참조가 남았는지 확인한다.
5. `git diff --check`와 최종 diff로 범위·공백 오류를 확인한다.

## 승인

- 상태: 승인됨.
- 사용자 요청: “yarn 관련 내용 npm으로 변경하고, sy-main 브랜치 반영해줘. push는 내가 할게.”
- 구현 승인: 세 파일의 변경 계획 보고 후 “작업 진행”.
- 이후 사용자가 “명령 실행 승인”으로 세 파일의 stage·commit 작업을 별도 승인했다. 초기 보호 실행 ID `8f0a455c92ae2a5755bb2b18758c843a`는 샌드박스 오류로 실행되지 않았다. HEAD 변경 후 현재 상태 기준 ID `b41b45cba61c6210310cf7559ce12756`을 재승인받아 권한 확장 실행으로 `c392709` 커밋을 완료했다. 상세 결과는 `final-summary.md`에 기록했다.
