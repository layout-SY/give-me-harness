# 탐색

## 요청

- 로컬 변경을 작업 단위로 commit하던 중 npm 프로젝트에 `yarn.lock`이 필요한지 확인하고 npm 단일화 방향으로 진행한다.

## 대상 관련 사실

- `package.json`의 개발·빌드 명령은 npm scripts로 정의되어 있다.
- `package-lock.json`과 `yarn.lock`이 모두 Git tracked 상태였다.
- tracked CI·Docker 설정에서 Yarn 실행 경로는 확인되지 않았다.
- 문서와 세션 검증 기록은 `npm install`, `npm run build`, `npm run lint`를 사용한다.
- Git 이력에서는 과거 dependency 변경 시 두 lockfile을 병행한 사례가 있어, 삭제는 명시적 package manager 정책 변경으로 처리했다.
- 실행 환경은 Node `v22.20.0`, npm `10.9.3`이다.

## 불러온 스킬

- `policy-git-branch-strategy`
- `git-master`
- `policy-documentation`
- `policy-portfolio`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공용 UI 전체 | 사용하지 않음 | package manager 설정만 변경하며 UI 요구사항이 없다. |

## 제약 조건 및 미확인 사항

- `npm audit`가 보고하는 취약점 수정은 dependency graph 변경이므로 현재 범위에서 제외한다.
- npm 외 package manager를 요구하는 외부 배포 시스템은 저장소 tracked 설정에서 확인되지 않았다.

## 결론

- `packageManager: "npm@10.9.3"`을 명시하고 `yarn.lock`을 제거하는 것이 현재 저장소의 실행·검증 방식과 일치한다.
- `package-lock.json`은 npm으로 재검증하며 실제 dependency 버전은 변경하지 않는다.
