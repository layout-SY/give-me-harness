# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다. 아래 항목은 모두 현재 작업을 차단하지 않는 장기 권고다.

## 장기 관찰 사항

- `package.json`의 `packageManager`가 npm 계약의 단일 기준점이 됐다.
- `.nvmrc`, `.node-version`, `volta.json`, `.tool-versions`, `engines.node`는 확인되지 않아 Node 버전 계약은 별도로 남아 있다.
- README는 Vite 템플릿 안내 중심이라 npm 단일화 정책을 설명하지 않는다.

## 목록에 등록할 재사용 가능 자산

- dependency 변경 체크리스트 후보:
  1. `packageManager` 값 확인
  2. 허용 lockfile이 하나인지 확인
  3. `npm ci` 실행
  4. `npm run build` 실행
  5. `package.json`·`package-lock.json` 동반 검토

## 기술 부채

- 지원 Node.js 버전 계약 부재
- npm 단일화 정책 문서 부재
- 비승인 lockfile 재도입을 차단하는 자동화 부재
- `npm audit`가 보고한 6 high severity vulnerabilities
- 저장소 전역 lint 기준선 73 errors·5 warnings

## 프로세스 개선 사항

- CI 설치 명령을 `npm ci`로 고정하고 비승인 lockfile을 검사한다.
- README 또는 기여 가이드에 npm·Node 버전과 dependency 변경 규칙을 명시한다.
- 보안 dependency 업데이트와 lint 기준선 정리는 각각 별도 작업으로 추적한다.

## 권고 사항

1. npm 단일화 계약을 README 또는 기여 문서에 기록한다.
2. 팀 지원 Node.js 버전을 결정한 뒤 저장소 관례에 맞는 버전 파일 또는 `engines.node`로 명시한다.
3. CI 도입 시 `npm ci`와 비승인 lockfile 탐지를 필수화한다.
4. `npm audit fix`는 breaking change를 검토하는 별도 보안 작업으로 수행한다.

- Evaluator 세션: `ses_f9f2a2ecefferHxzcwPnTYXkit`
