---
name: recipe-index
description: synthoria-admin-ui의 recipe(조립 가이드) 카테고리 인덱스이자 신규 도메인/플로우 recipe를 만들 때의 생성 기준. 이미 있는 recipe로 해결되는지 판단하거나, 새 recipe를 만들지(혹은 기존 recipe·reference 보강으로 끝낼지) 결정해야 할 때 사용.
---

# Recipe (synthoria-admin-ui)

> Recipe = "여러 reference 조각을 어떤 순서로 조립하는가"를 처방하는 문서.
> Reference가 "조각의 계약"이라면 Recipe는 "그 조각들을 묶는 레시피"다.

## 언제 이 스킬을 사용하나요?

- 새 화면/모달/플로우를 만들기 전, **이미 있는 recipe로 해결 가능한지** 먼저 확인
- 기존에 없는 도메인/플로우를 발견했을 때, **새 recipe를 만들지 vs 기존 문서 보강으로 끝낼지** 판단
- recipe 작성 시 표준 구조/필수 섹션을 따르기 위함

---

## 1) 현재 recipe 카탈로그

| Recipe | 위치 | 다루는 플로우 |
| --- | --- | --- |
| `recipe-data-fetch` | [data-fetch/SKILL.md](data-fetch/SKILL.md) | 목록 fetch + 모달 fetch + 이미지 업로드 fetch 조립 |
| `recipe-data-dto` | [data-dto/SKILL.md](data-dto/SKILL.md) | 도메인 DTO 설계, 폼↔payload 매핑 |

새 작업이 위 카탈로그 어디에도 안 잡히면 **신규 recipe 후보**다. 단, 아래 생성 기준을 먼저 통과해야 한다.

---

## 2) 신규 recipe 생성 기준 (필수 통과)

다음 **모든 항목**이 참일 때만 새 recipe를 만든다.

### 2-1. 조립 복잡도 기준

- 작업이 **3개 이상의 reference 조각**(컴포넌트/훅/이벤트/DTO/유틸 등)을 함께 다룬다
- 각 조각의 reference 문서만 읽어서는 **올바른 순서/조건을 도출할 수 없다**
- 즉, "어느 조각을 언제 어떻게 끼우는가"가 **암묵지**로 남아있다

### 2-2. 재사용성 기준

- **2개 이상의 도메인** 또는 **2개 이상의 다른 페이지 그룹**에서 같은 조립 패턴이 등장한다
- 한 도메인에서만 등장하는 1회성 흐름은 **recipe 후보가 아니다** (해당 도메인의 코드/주석으로 충분)

### 2-3. 의사결정 분기 존재

- 조립 도중 **선택 분기**(예: 통합 모달 vs 분리 모달, useFetchAdapter vs 수동 테이블, popup vs side-modal)가 있고, 잘못 선택 시 일관성·유지보수성에 영향을 준다
- 분기를 처방으로 명문화할 가치가 있다

### 2-4. 정책으로 충분하지 않음

- `policy/*` 횡단 규칙(예: validation, coding-convention)으로는 흐름까지 처방할 수 없다
- "무엇을 지킬 것인가"(policy)와 "어떻게 조립할 것인가"(recipe)가 명확히 다르다

> **위 4가지 중 하나라도 미충족 → 신규 recipe 만들지 않는다.** 대안:
> - reference 보강 (해당 조각 SKILL.md에 패턴 추가)
> - policy 보강 (횡단 규칙으로 충분한 경우)
> - 도메인 코드의 README/주석으로 처리 (1회성/도메인 한정)

---

## 3) 도메인 종속 vs 횡단 recipe 구분

### 3-1. 횡단 recipe (현재 카탈로그가 모두 이에 해당)

- 여러 도메인이 공통으로 따르는 조립 패턴
- 위치: `recipe/<flow-name>/SKILL.md` (예: `recipe/data-fetch`)
- 네이밍: `recipe-<flow-name>`

### 3-2. 도메인 종속 recipe

- **하나의 도메인 안에서 여러 reference 조각을 조립**해야 하지만, 다른 도메인에는 그대로 적용되지 않음
- 예: DAO 제안 작성/심사 흐름, 대시보드 위젯 조립, 활동맵 마커/타일 좌표 결합
- 위치: `recipe/domain/<domain-name>/SKILL.md`
- 네이밍: `recipe-domain-<domain-name>`
- 도메인 종속 reference(컴포넌트/훅)도 같은 도메인 폴더 하위에 둘 수 있다 (예: `recipe/domain/dao/proposal-image-upload/SKILL.md`)

### 3-3. 도메인 recipe 승격/강등 신호

- **승격(reference → recipe)**: 같은 도메인 안에서 동일 조립 패턴이 3회 이상 반복 등장
- **강등(recipe → reference 보강)**: 그 recipe가 다루는 플로우가 1개 페이지로 줄어듦

---

## 4) Recipe 표준 구조 (필수 섹션)

신규 recipe SKILL.md는 다음 섹션을 반드시 포함한다.

```markdown
---
name: recipe-<flow-name>  또는  recipe-domain-<domain>-<flow>
description: "<언제 이 recipe를 부르는가>" 중심으로 작성. 끝에 "(reference: A, B, C)" 표기.
---

# <Recipe 제목>

## 언제 이 스킬을 사용하나요?
- 트리거 시나리오 3~5개

## 선행 reference 확인 체크리스트     ← 필수
- [ ] reference/<...>/SKILL.md — 무엇을 알아야 하는지
- [ ] policy/<...>/SKILL.md — 적용되는 횡단 정책

## 0) 작업 시작 전 필수 확인          ← 필수
1. 재사용 가능성 확인
2. 패턴 분기 결정 (어떤 분기를 고를지)
3. 의존 데이터/이벤트/DTO 확인

## 1)~N) 단계별 조립 절차              ← 필수
- 조각의 호출 순서, 각 단계의 입출력, 분기 조건

## N+1) 구현 시 주의사항               ← 필수
- 흔한 함정, 누락 패턴

## N+2) 빠른 템플릿                    ← 권장
- 복붙 가능한 최소 구현 예시
```

---

## 5) 안티패턴

- **Recipe가 reference 내용을 통째로 복제**한다 (drift 발생) → 링크로 위임만 한다
- **Recipe에 정책 규칙을 다시 쓴다** (예: "any 금지", "한글 문자열 직접 작성") → policy로 위임
- **1회성 페이지의 구현 절차를 recipe로 만든다** → 코드/주석으로 충분
- **Recipe 하나가 여러 무관한 플로우를 모은 잡탕** → 플로우 단위로 분리
- **선행 reference 확인 체크리스트 누락** → 항상 포함

---

## 6) 신규 recipe 작성 절차

1. 위 **2장 4가지 기준**을 통과하는지 자체 점검
2. 횡단 vs 도메인 종속 결정 → 위치/네이밍 확정
3. 같은 카테고리의 기존 recipe(특히 `recipe-data-fetch`)를 한 번 정독해 톤·구조 일치
4. 위 **4장 표준 구조**대로 SKILL.md 작성
5. 본문에서 reference·policy를 **링크로만** 위임 (내용 복제 금지)
6. 카탈로그(본 인덱스 1장 표)에 새 항목 추가
