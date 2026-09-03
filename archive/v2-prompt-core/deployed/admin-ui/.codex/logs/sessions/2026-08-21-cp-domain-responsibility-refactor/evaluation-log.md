# CP 도메인 책임 분리 평가 로그

## 컨텍스트

Discussion 목록은 실제 API query/mutation, 검색 draft, 기간 validation, 선택·처리 상태, Dialog, navigation, JSX가 단일 page에 모여 있었다. 기능을 바꾸지 않고 도메인 내부 경계를 명시하는 것이 이번 섹션의 목적이었다.

## 구조적 결과

1. route page는 controller와 view 결선만 소유한다.
2. server state/query feedback은 data hook에 위치한다.
3. UI draft와 DTO mapping은 search hook에 위치한다.
4. 선택·상태 전이·mutation surface는 process hook에 위치한다.
5. view는 typed controller contract만 소비한다.

## 왜 중요한가

- 실제 API shape 변경은 entity/parser 경계에 머무르고 화면 orchestration 수정 범위를 줄일 수 있다.
- 검색·처리·표현 변경이 서로 다른 파일에 국소화된다.
- Vote·Comment 등 후속 도메인에서 동일한 분리 판단 기준을 재사용할 수 있다.

## 구조적 리스크

1. 도메인별 유사 파일 증가로 단순 라인 수는 늘어난다.
2. controller 반환 shape가 커지면 view 계약이 비대해질 수 있다.
3. 유사 도메인을 너무 일찍 공용화하면 query/payload 차이를 generic으로 숨길 수 있다.

## 개선 옵션

1. Discussion 상세를 form/model/process/view로 분리한다.
2. Vote 목록까지 동일한 도메인 전용 패턴으로 적용한 뒤 공통 불변식을 비교한다.
3. shared shell/table 반응형 문제는 사용자가 보류를 해제한 별도 작업에서 처리한다.

## 권장 백로그

1. Discussion 상세 책임 분리
2. Vote 목록 책임 분리
3. Vote 상세 책임 분리
4. Comment controller 세분화
5. Proposal detail/process 정리

## 다음 단계 제안

- Watcher 비가용 정책을 유지한 채 다음 독립 섹션인 Discussion 상세를 새 Refactorer tranche로 준비한다.

---

## Discussion 상세 평가

### 구조적 결과

1. route page는 controller/view 결선만 소유한다.
2. controller는 route/query/error/retry/navigation을 소유한다.
3. process hook은 종료일 draft/status transition/mutation feedback을 소유한다.
4. model은 date validation과 DTO payload mapping을 소유한다.
5. view는 detail과 typed callback 계약만 소비한다.

### 목록과 다르게 분리한 이유

- 상세에는 검색 query draft나 row selection lifecycle이 없어 data/search hook을 추가하면 단일 사용 추상화만 늘어난다.
- form 상태와 mutation은 저장 가능 조건을 함께 계산하므로 하나의 process hook에 유지하는 편이 응집도가 높다.
- validation/payload는 React 밖에서도 설명 가능한 순수 규칙이므로 model로 분리할 가치가 있다.

### 확인된 효과

- detail API lifecycle 변경은 controller에 국소화된다.
- 종료일 규칙이나 process DTO mapping 변경은 model/process에 국소화된다.
- 화면 구조와 문구 변경은 view에 국소화된다.
- route page는 후속 Discussion 상세 진입 계약을 바꾸지 않는다.

### 잔여 리스크

1. test script 부재로 model 순수 함수의 자동 회귀 테스트는 없다.
2. Watcher 독립 판정과 Closure는 정책상 미진행이다.
3. shared navigation 반응형 결함은 사용자 지정 deferred 범위다.
4. Discussion 목록·상세와 Vote 구조의 공통 불변식은 Vote tranche 후에만 재평가한다.

### 다음 단계 제안

- 시각 QA 독립 판정 후 본 tranche를 `paused_after_generator`로 기록한다.
- 다음 도메인 섹션은 Vote 목록으로 진행한다.

### 독립 판정 결과

- 기능·디자인 시스템 무결성 Oracle: PASS, HIGH confidence
- 시각·CJK 정밀성 Oracle: PASS, HIGH confidence
- 변경 파일 원인의 blocking defect: 0건
- shared navigation 결함은 Discussion 상세 책임 밖이며 사용자 지정 deferred backlog 유지
- 본 tranche 최종 pipeline 상태: `paused_after_generator`

---

## Vote 목록 평가

### 구조적 결과

1. route page는 controller/view 결선만 소유한다.
2. data hook은 query lifecycle, KPI/pagination, placeholder, error/retry를 소유한다.
3. search hook은 draft와 committed query, submit/reset/page 변경을 소유한다.
4. process hook은 row selection, status/disclosure transition, mutation feedback을 소유한다.
5. controller는 세 hook의 reset 순서와 detail navigation을 조합한다.
6. view는 typed contract와 기존 shared/widget primitive만 소비한다.

### Discussion과 분리한 이유

- Vote와 Discussion은 기간 query와 status/disclosure UI가 유사하지만 status union, ID, DTO, Dialog, disclosure vocabulary가 다르다.
- Vote의 역전 기간 observable은 별도 오류 state가 아니라 DateRangeField native invalid/form 차단이다.
- Vote 목록 payload는 `status`와 `disclosureRule`만 사용하고 상세 전용 `closedAt`을 포함하지 않는다.
- 따라서 구조만 재사용하고 hook/controller 구현은 Vote 도메인에 유지하는 편이 generic parameter와 domain leak를 줄인다.

### 확인된 효과

- Vote page 180줄이 11줄 route entry로 축소됐다.
- query/error 변경은 data, 검색 정책은 search, 처리 DTO·feedback은 process, markup은 view에 국소화된다.
- placeholder stale row, selection reset, mutation guard가 명시적인 계약으로 드러났다.
- API/entity/config/shared/widget/CSS/copy/route 변경 없이 브라우저 observable을 보존했다.

### 잔여 리스크

1. test script 부재로 자동 회귀 테스트가 없다.
2. Watcher 독립 판정과 Closure는 정책상 미진행이다.
3. DateRange placeholder, Table horizontal viewport, shared navigation 반응형 결함은 사용자 지정 deferred 범위다.
4. 세 목록 구조의 공통화 여부는 여전히 query/payload 차이가 커서 보류한다.

### 독립 판정 결과

- 기능·디자인 시스템 무결성 Oracle: PASS, HIGH confidence
- 시각·CJK 정밀성 Oracle: PASS, HIGH confidence
- 변경 파일 원인의 blocking defect: 0건
- 본 tranche 최종 pipeline 상태: `paused_after_generator`

### 다음 단계 제안

- 다음 독립 섹션은 Vote 상세 책임 분리다.

---

## Vote 상세 평가

### 구조적 결과

1. route page는 controller/view 결선과 framework default export만 소유한다.
2. controller는 route param, detail query, error feedback, retry와 navigation을 소유한다.
3. process hook은 detail keyed draft, status transition, mutation lifecycle과 feedback을 소유한다.
4. model은 종료일 validation과 조건부 DTO mapping만 소유한다.
5. view는 typed contract와 기존 shared/widget primitive만 소비한다.

### 목록과 다르게 분리한 이유

- 상세에는 검색 draft, pagination, row selection, placeholder lifecycle이 없다.
- 반대로 detail ID 교체, 종료일 draft와 process mutation의 응집이 핵심이다.
- 따라서 목록의 data/search/process 구조를 복제하지 않고 controller/process/model/view만 사용했다.

### 확인된 효과

- Vote 상세 page 142줄이 11줄 route entry로 축소됐다.
- query/error 변경은 controller, form/mutation 변경은 process, 순수 날짜·payload 규칙은 model, markup은 view에 국소화된다.
- `CpVoteStatus | null` 계약으로 domain status vocabulary가 controller/view 경계에서도 유지된다.
- API/entity/shared/widget/CSS/copy/route 변경 없이 브라우저 observable을 보존했다.

### 잔여 리스크

1. test script 부재로 model 순수 함수 자동 회귀 테스트가 없다.
2. Watcher 독립 판정과 Closure는 정책상 미진행이다.
3. invalid 종료일의 field-level 오류 표현과 375px TimelineList 음절 분리는 기존 deferred UI debt다.
4. generic CP detail 추상화는 소비자별 status·DTO·결과 UI 차이로 보류한다.

### 독립 판정 결과

- 최초 Oracle 타입 finding 반영 후 fresh source/capture로 재판정했다.
- 기능·디자인 시스템 무결성 Oracle: PASS, HIGH confidence
- 시각·CJK 정밀성 Oracle: PASS, HIGH confidence
- 변경 파일 원인의 blocking defect: 0건
- 본 tranche 최종 pipeline 상태: `paused_after_generator`

### 다음 단계 제안

- 다음 독립 섹션은 Comment 목록 controller다.

---

## Comment 목록 평가

### 구조적 결과

1. route page는 controller/view 결선만 소유한다.
2. data hook은 query lifecycle, KPI/pagination, error feedback과 retry를 소유한다.
3. search hook은 source tab과 text draft, trim/query mapping, submit/reset/page 변경을 소유한다.
4. process hook은 row selection, state transition, mutation lifecycle과 feedback을 소유한다.
5. controller는 세 hook의 selection reset 순서와 typed view 계약을 조합한다.
6. view는 기존 shared/widget primitive와 사용자 observable만 보존한다.

### 선행 목록과 분리한 이유

- Comment는 source tab과 `state` vocabulary를 사용하고 Vote/Discussion의 기간·공개 기준·detail navigation이 없다.
- placeholder 중 stale row 조작 가능 여부도 선행 목록과 달라 이를 generic controller 불변식으로 만들 수 없다.
- 따라서 data/search/process 책임 이름만 재사용하고 구현과 계약은 Comment 도메인에 유지했다.

### 확인된 효과

- 기존 단일 page hook을 8줄 route page와 47~171 pure LOC의 책임 파일로 분해했다.
- query/error 변경은 data, 검색 정책은 search, 상태 DTO·feedback은 process, markup은 view에 국소화된다.
- click·keyboard selection, first-row fallback, trim query, state-only POST와 cache/KPI 동기화를 실제 브라우저에서 보존했다.
- API/entity/config/shared/widget/CSS/copy/route 변경 없이 정상 사용자 observable을 유지했다.

### 잔여 리스크

1. test script 부재로 자동 회귀 테스트가 없다.
2. Watcher 독립 판정과 Closure는 정책상 미진행이다.
3. placeholder stale row guard는 기존 기능 보존 때문에 도입하지 않았다.
4. 768/375 Table clipping·CJK 조각과 navigation 침범은 사용자 지정 deferred 범위다.

### 독립 판정 결과

- 기능·디자인 시스템 Oracle: PASS, MEDIUM confidence
- 반응형·CJK Oracle: PASS, MEDIUM confidence
- Comment tranche 원인의 시각 회귀와 blocking defect: 0건
- 활성 MSW worker 500 주입으로 query retry 2회, Alert·fallback, 사용자 retry 추가 2회와 정상 handler 복구를 브라우저에서 확인했다.
- 변경 전 기준 캡처가 없어 pixel-level 동일성은 증명하지 않았고, 현재 캡처와 알려진 shared debt를 기준으로 판정했다.
- 본 tranche 최종 pipeline 상태: `paused_after_generator`

### 다음 단계 제안

- 다음 독립 섹션은 Proposal detail/process 정리다.

---

## Proposal 상세·process 평가

### 구조적 결과

1. route page는 controller/view 결선과 framework default export만 소유한다.
2. controller는 route param, detail query, 조회 오류 feedback, retry와 navigation을 소유한다.
3. process hook은 detail ID keyed reviewComment draft, 저장 조건, mutation lifecycle과 Dialog를 소유한다.
4. view는 typed controller 계약과 기존 shared/widget primitive만 소비한다.
5. 단일 입력의 trim·비교·payload는 process에 유지해 불필요한 model 파일을 만들지 않았다.

### Discussion·Vote 상세와 다르게 분리한 이유

- Proposal 상세은 status와 department가 읽기 전용이고 reviewComment 하나만 수정한다.
- 날짜 형식·하한 validation이나 status transition이 없어 별도 순수 model의 인지 부하 감소 효과가 없다.
- 따라서 구조적 controller/process/view 경계만 재사용하고 payload·validation은 Proposal-local process에 유지했다.

### 확인된 효과

- 166줄 mixed page를 14 pure LOC route entry와 19~91 pure LOC 책임 파일로 분해했다.
- query/error/navigation 변경은 controller, 처리 의견/mutation 변경은 process, markup 변경은 view에 국소화된다.
- reviewComment-only payload, server validation, response cache/history와 list invalidation을 브라우저에서 보존했다.
- API/entity/shared/widget/CSS/copy/route 변경 없이 정상·오류 observable을 유지했다.

### 잔여 리스크

1. test script 부재로 자동 회귀 테스트가 없다.
2. Watcher 독립 판정과 Closure는 정책상 미진행이다.
3. 768/375 shared TextArea CJK 줄바꿈과 navigation 침범은 사용자가 지정한 후속 shared 단계다.
4. generic CP detail 추상화는 도메인별 editable field·validation·payload 차이로 계속 보류한다.

### 독립 판정 결과

- 기능·디자인 시스템 Oracle: PASS, MEDIUM confidence
- CJK Oracle: 책임 분리 tranche PASS, 전체 화면 REVISE, MEDIUM confidence
- Proposal tranche 원인의 blocking defect: 0건
- 전체 화면 REVISE 원인은 unchanged shared TextArea/navigation 부채이며 사용자 sequencing에 따라 accepted deferred
- 본 tranche 최종 pipeline 상태: `paused_after_generator`

### 다음 단계 제안

- 남은 CP 도메인 책임 분리를 한 섹션씩 계속한다.
- 모든 도메인 책임 분리 후 shared TextArea CJK wrapping, navigation, Table 반응형 부채를 별도 리팩터링한다.
