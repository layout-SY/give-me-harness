# Plan — FSD 아키텍처 재설계

> 작성일: 2026-07-03

---

## 추구한 방향성 (설계 원칙)

1. **엄격 FSD 레이어링**: `app → pages → widgets → features → entities → shared` 단방향 의존.
2. **shared 도메인-무지**: shared는 어떤 도메인 타입/enum도 알지 않는다. (결합 #1·#2·잠재결합 해소가 최우선)
3. **슬라이스 격리**: 같은 레이어 슬라이스 간 직접 import 금지, public API(`index.ts`)로만.
4. **잔재 제거와 이관 분리**: 죽은 도메인을 먼저 제거해 이관 표면을 축소.
5. **비가역 이동의 안전화**: git 없이 진행하므로 소단위 이동 + 매 단계 `tsc --noEmit` 게이트.

---

## 사용자 결정 사항 (질의 응답)

| 주제 | 결정 |
|------|------|
| 제거 범위 | ecommerce·videos·nft·parcel 제거, item-category→items 병합, 나머지 유지 |
| nft ↔ users/dao | nft 전면 제거하되 유지 도메인 참조부는 **주석 처리** |
| dao 분해 깊이 | (초기) 주요 하위 개별 entity → (구현 중 근거로 조정) **단일 entity 유지** |
| dao 공유 코어 | entities/dao 코어 + @x cross-import (→ 단일 entity 결정으로 불요화) |
| api 결합(#2) | **entity별 api 싱글턴** (규약 변경, 가장 FSD-순수) |
| git 안전망 | 미사용, 그대로 진행 |

---

## 목표 레이어 구조

```
app        진입·router(가드)·providers·styles·(조립 지점)
pages      라우트 단위 화면 (신규)
widgets    app-header · side-navigation
features   auth · select-users · image-manager · calendar-picker
entities   <domain>/{api, model, ui}
shared     api · lib(hooks·utils·exceptions·pub-sub) · ui · config · assets
```

---

## 실행 섹션 (순차, 각 섹션 tsc 게이트)

| # | 섹션 | 핵심 |
|---|------|------|
| S7 | 잔재 제거 | 4개 도메인 삭제 + nft 주석 처리 + item-category 병합 준비 |
| S0 | 골격 | 6개 레이어 + `src/ARCHITECTURE.md` 계약 |
| S1 | shared 확립 | api인프라·hooks·utils·exceptions·범용 UI·공통 enum·assets |
| S2 | pub-sub 제네릭화 | 결합 #1 해소 (선언 병합) |
| S3 | entities 이관 | services→entities, enum·store 재배치, item-category 병합, dao 판단 |
| S4 | api 레지스트리 | 결합 #2 해소 (entity별 싱글턴) |
| S5 | features/widgets | 유스케이스·위젯·가드 승격 |
| S6 | app 셸 | 진입 파일 app 이관 |
| S8 | 검증·문서화 | 경계 감사 + 산출물 |

> 실제 실행 순서: S7 → S0 → S1 → S3 → S5 → S4 → S2 → (shared 순수성 마감) → S6 → S8.
> (이관 표면 축소를 위해 제거 우선, 결합 해소는 물리 이관 후 수행.)

---

## 게이트 정책
- 각 파일 이동 직후 `npx tsc --noEmit -p tsconfig.app.json` 실행.
- 합격 기준: `cannot find module` = 0, 총 에러 수 ≤ 베이스라인(18).
- 최종: eslint import-resolution 오류 0 + 레이어 경계 감사 통과.
