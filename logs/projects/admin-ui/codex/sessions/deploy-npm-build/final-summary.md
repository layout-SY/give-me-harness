# 최종 요약

## 제공 사항

`sy-main`의 배포 설정을 npm으로 전환하고 `c392709` (`fix(ci): Docker 빌드를 npm으로 전환`)으로 커밋했다. `Dockerfile`, `.dockerignore`, `docs/deploy-onprem.md` 세 파일만 포함했다. 초기 샌드박스 실패 이후 현재 HEAD 기준으로 보호 실행을 준비하고 사용자 승인과 권한 확장을 거쳐 완료했다. push는 수행하지 않았으며 사용자가 진행한다.

## 변경 이유

사용자가 제공한 CI 로그에서 `COPY package.json yarn.lock ./`가 `yarn.lock: not found`로 실패했다. 앱은 npm으로 전환됐지만 배포 설정에는 Yarn 설치·빌드 명령과 npm lockfile 제외 규칙이 남아 있었다.

## 변경 및 재사용한 자산

- `Dockerfile`: 기존 멀티스테이지를 유지하면서 `package-lock.json`을 복사하고 npm 10.9.3 및 `npm ci --include=dev`를 사용한다. 캐시는 `/root/.npm`으로 전환하고 기존 `lint`·`build` 스크립트를 npm으로 실행한다.
- `.dockerignore`: `package-lock.json` 제외와 오래된 주석을 삭제한다.
- `docs/deploy-onprem.md`: npm 버전·설치·lockfile 갱신 설명을 실제 설정과 맞춘다.
- `package.json`, `package-lock.json`, `.github/workflows/deploy.yml`, `docker/entrypoint.sh`는 기존 계약을 재사용하고 수정하지 않았다.
- 소스와 기존 테스트에 있던 다른 작업의 미커밋 변경은 수정·stage하지 않았다.

## 검증

검증 당시 위치는 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, 브랜치는 `sy-main`, HEAD는 `e9292a5351fe7f087b1f29f1c5245f027f3d1115`였다. 결과는 다른 작업의 미커밋 앱 변경이 포함된 현재 작업 트리 기준이다.

| 명령어 | 결과 |
| --- | --- |
| 중앙 `formatting.py apply` | 종료 코드 0. 대상 코드 파일 없음(`formatted: []`). |
| `npm ci --dry-run --include=dev --ignore-scripts --offline --no-audit --no-fund --cache node_modules/.cache/npm-ci-validation --json` | 종료 코드 0. lockfile 정합성 확인. 실제 의존성 재설치는 수행하지 않음. |
| `npm run lint` | 종료 코드 0. |
| `VITE_API_BASE_URL=__RUNTIME_VITE_API_BASE_URL__ VITE_ENVIRONMENT= npm run build` | 종료 코드 0. TypeScript·Vite 빌드 성공. 기존 경로 플러그인 안내와 청크 크기 경고 있음. |
| `rg -l '__RUNTIME_VITE_API_BASE_URL__' dist/assets` | 생성된 `index-CO6reWl9.js`에서 런타임 치환용 자리표시자 확인. |
| `rg -n -i yarn Dockerfile .dockerignore docs .github docker` | 일치 없음(종료 코드 1). |
| `git diff --check -- Dockerfile .dockerignore docs/deploy-onprem.md` | 종료 코드 0. |
| `docker version` | 클라이언트 있음. Docker 소켓 부재로 엔진 연결 실패. 이미지 빌드 미실행. |

`package.json`에 `test` 스크립트는 없다. 애플리케이션 동작 변경이나 새로운 테스트 프레임워크·구현 문자열 검사 테스트를 추가하지 않았다.

## 산출물

- `.codex/logs/sessions/deploy-npm-build/plan.md`
- `.codex/logs/sessions/deploy-npm-build/final-summary.md`

## 알려진 제한과 다음 단계

- Docker 엔진이 실행되지 않아 Linux 이미지의 실제 설치·번들 생성·기동 검증은 수행하지 못했다. 사용자의 push 및 `dev` 반영 후 CI 확인이 필요하다.
- 사용자가 “명령 실행 승인”으로 승인한 작업은 `git add -- Dockerfile .dockerignore docs/deploy-onprem.md && git commit -m "fix(ci): Docker 빌드를 npm으로 전환"`이다. 기존 다른 작업의 변경과 세션 기록은 commit 대상에 포함하지 않는다.
- 보호 실행 작업 ID: `8f0a455c92ae2a5755bb2b18758c843a`. 첫 실행은 중앙 `branch-relations/v1/locks/operation-8f0a455c92ae2a5755bb2b18758c843a.lock` 생성에서 `Operation not permitted`로 종료 코드 2를 반환했다.
- 같은 작업을 `require_escalated`로 재시도했지만 PreToolUse가 다시 “명령 실행 승인으로 답하세요”로 차단했다. 이미 승인된 작업이므로 동일 승인을 다시 요구하거나 보호 실행기를 우회하지 않았다.
- 실패 후 `show` 결과는 `stage: prepared`다. `git diff --cached --name-only`는 비어 있고 HEAD는 여전히 `e9292a5351fe7f087b1f29f1c5245f027f3d1115`다. stage·commit·push 모두 실행되지 않았고 세 파일의 수정은 작업 트리에 남아 있다.
- 이후 다른 작업의 페이지네이션 변경이 `2803c51`로 커밋됐다. 세 배포 파일의 diff와 비어 있는 index를 재확인해 현재 HEAD 기준 작업 `b41b45cba61c6210310cf7559ce12756`을 준비했다.
- 사용자의 재승인 후 보호 실행을 처음부터 `require_escalated`로 호출해 중앙 잠금 기록과 stage·commit을 완료했다. 중앙 정책 파일은 수정하지 않았다.
- 이전 구현 시도는 정책 훅의 승인·탐색 준비 부족으로 차단됐고, 사용자의 “작업 진행” 승인과 추가 탐색 후 파일 수정이 성공했다.

## Git 반영 결과

- 브랜치: `sy-main`.
- 커밋: `c392709` — `fix(ci): Docker 빌드를 npm으로 전환`.
- 범위: 세 파일, 16줄 추가·19줄 삭제.
- 보호 실행 결과: `stage: done`, 종료 코드 0.
- 사후 확인: `git show --stat --oneline HEAD`에서 세 파일만 포함됨을 확인했다. index는 비었으며 기존 미추적 `PR_sy-main-to-dev.md`만 남아 있다.
- push·원격 변경은 하지 않았다. 사용자의 push 및 `dev` 통합 후 Docker CI 검증이 남아 있다.
