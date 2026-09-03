# 이력서·포트폴리오 기록

## 사례 1 — npm 단일 package manager 계약 수립

- 작업 유형: 품질 개선
- 관련 도메인/서비스: 프런트엔드 개발·빌드 인프라
- 문제 출처: 사용자 요구

### 문제 상황

- 사용자가 제시한 요구·문제·변경 이유: `package-lock.json`을 사용하는 npm 프로젝트에서 `yarn.lock`이 필요한지 확인하고, npm 단일화 방향으로 진행하도록 요청했다.
- 테스트·런타임에서 관찰한 오류: `npm install --package-lock-only`은 정상 완료됐고, npm 출력에서 6 high severity vulnerabilities가 별도 부채로 관찰됐다. 저장소 전체 lint는 기존 73 errors·5 warnings로 실패했다.
- 필요한 기술·구조·패턴이 없을 때 발생할 문제: npm과 Yarn lockfile을 병행하면 dependency 변경 시 서로 다른 해석 결과가 저장소에 공존하고, 신규 참여자가 사용할 package manager를 판단하기 어렵다.

### 고민과 선택

- 사용자 제안: npm 프로젝트이므로 `yarn.lock`이 불필요하지 않은지 확인한다.
- 에이전트 제안: tracked CI·문서·Git 이력을 확인하고 npm 단일화 시 `yarn.lock`을 제거하며 `packageManager`를 명시한다.
- 검토한 대안: 두 lockfile 유지, `yarn.lock`만 삭제, npm 버전 계약과 함께 삭제.
- 최종 선택: `packageManager: "npm@10.9.3"`을 추가하고 `yarn.lock`을 삭제하되 `package-lock.json`은 그대로 유지한다.
- 선택 이유와 제외한 방식의 이유: 실행·검증 경로가 npm으로 통일되어 있으며, 버전 계약 없는 단순 삭제보다 npm 버전을 함께 명시하는 방식이 저장소 의도를 더 분명히 한다. 두 lockfile 유지는 불일치 위험 때문에 제외했다.

### 적용

- 변경 경로: `package.json`, `yarn.lock`
- 구현·수정·리팩터링 내용: npm 버전 계약을 추가하고 Yarn lockfile 2,619줄을 제거했다.
- 핵심 동작: npm이 `package-lock.json`만으로 clean install 계획을 구성하고 `packageManager`를 `npm@10.9.3`으로 노출한다.

### 사용 기술과 구체적 목적

| 기술·구조·패턴 | 해결하려는 구체적 문제 | 적용 위치와 방식 |
| --- | --- | --- |
| `packageManager` | package manager와 버전 선택의 모호성 | `package.json`에 `npm@10.9.3` 명시 |
| npm lockfile v3 | dependency graph 재현 | 변경 없는 `package-lock.json` 유지·검증 |
| `npm ci` dry-run | clean install 계약 검증 | lockfile 추가 변경·Yarn lockfile 재생성 여부 확인 |
| atomic Git 변경 | package manager 정책을 기능 변경과 분리 | 독립 브랜치와 단일 목적 commit 계획 |

### 결과

- 적용 전: `package-lock.json`과 `yarn.lock`이 함께 tracked되어 package manager 계약이 중복됐다.
- 적용 후: npm `10.9.3` 계약과 `package-lock.json` 하나만 남도록 변경 준비를 완료했다.
- 검증 결과: package-lock-only 설치 PASS, npm ci dry-run PASS, production build PASS, Watcher PASS. 전체 lint는 변경 밖 기존 73 errors·5 warnings로 실패했다.
- 사용자 후속 피드백: npm 단일화 계획과 브랜치 생성을 승인했다.
- 추가 요청 및 남은 제한: README·Node 버전 계약·CI lockfile 방어선과 dependency 취약점은 별도 후속 작업이다.

```mermaid
flowchart LR
  Before[package-lock.json + yarn.lock] --> Decision[npm@10.9.3 계약 명시]
  Decision --> After[package-lock.json 단일 lockfile]
```

### 이력서·포트폴리오 문구

- 이력서 bullet: npm·Yarn 이중 lockfile 구조를 분석해 `packageManager` 계약과 npm clean-install 검증을 도입하고, dependency graph 변경 없이 npm 단일 lockfile로 표준화했다.
- 포트폴리오 서술: npm 중심 실행 환경에 두 lockfile이 공존해 dependency 재현 계약이 모호한 문제를 발견했다. tracked 설정과 Git 이력을 검토해 단순 삭제와 버전 계약 병행 방식을 비교했고, `npm@10.9.3` 명시와 `yarn.lock` 제거를 선택했다. `package-lock.json`의 동일성을 보존한 채 npm ci dry-run과 production build, 독립 Watcher PASS로 결과를 검증했다.
