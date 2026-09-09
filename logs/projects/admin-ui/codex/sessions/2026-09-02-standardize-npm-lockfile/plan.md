# 계획

## 목표

- 저장소의 package manager 계약을 npm으로 단일화한다.
- `package.json`에 실행 환경과 일치하는 `packageManager`를 명시하고 중복 lockfile인 `yarn.lock`을 제거한다.

## 범위

- `package.json`
- `package-lock.json` 정합성 확인
- `yarn.lock` 삭제
- `.codex/logs/sessions/2026-09-02-standardize-npm-lockfile/` 필수 산출물

## 제외 사항

- dependency 버전 변경
- `npm audit fix`
- 애플리케이션 소스 및 UI 변경
- 원격 push

## 제약 조건

- `sy-main@78a5a42101d77bc84bd456c19ea14778b09b5e64`에서 승인된 `task/standardize-npm-lockfile` 브랜치만 사용한다.
- 사용자 요청에 따라 npm을 단일 package manager로 선택한다.
- 브라우저·스크린샷·시각 QA는 수행하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 브랜치 계약 | Hephaestus | `policy-git-branch-strategy`, `git-master` | 승인 범위와 계보 고정 |
| 구현·검증 | Hephaestus | `policy-documentation` | npm 단일화와 실행 근거 확보 |
| 경력 추합 | Hephaestus | `policy-portfolio` | 검증된 포트폴리오 기록 |

## 검증

- `npm_config_dry_run=true npm_config_ignore_scripts=true npm ci`
- `npm run build`
- `npm run lint`
- `npm pkg get packageManager`
- `git diff --check`

## 위험 요소 및 결정 사항

- 두 lockfile을 병행하면 npm과 Yarn의 해석 결과가 달라질 수 있으므로 `package-lock.json`만 유지한다.
- 현재 npm 버전 `10.9.3`을 `packageManager`에 고정한다.
- `npm audit`의 기존 취약점은 dependency 변경이 필요한 별도 작업으로 분리한다.

## 승인

- 구현 승인: 사용자의 `진행해`
- 브랜치 승인: 사용자의 `생성`
- 상태: approved
