# Exploration — FSD 아키텍처 재설계

> 작성일: 2026-07-03
> 도메인: 전 프로젝트 구조 (횡단)
> 목적: 기술 유형별(type-first) 구조를 엄격한 FSD로 재설계 + 이전 프로젝트 잔재 제거

---

## 1. 초기 상태 요약

### 스택
- React 19 · react-router-dom 7 · zustand · axios · dayjs · jwt-decode
- 별칭 `~/*` → `src/*` (tsconfig.app.json + vite-tsconfig-paths)
- 빌드/검사: `vite` / `tsc -b && vite build` / `eslint .`

### 구조적 성격
- **기술 유형별 분류(type-first)**: `apis/`, `components/`, `hooks/`, `store/`, `enums/`, `utils/`, `exceptions/`, `assets/`
- 한 도메인이 여러 최상위 폴더에 흩어짐 (예: user → apis/services/users + store/user.store + enums/user.enum + components/select-users).
- **앱 셸 미구성**: `App.tsx`는 Vite 기본 템플릿, 라우팅/`pages` 계층 부재. → 이전 프로젝트에서 복사한 **공용 인프라만 얹힌 스캐폴드**.

### 규모 (재설계 전)
- `apis/services/` 20개 도메인, `components/` 30여 개, `enums/` 15개, hooks 5종, store 4종.

---

## 2. 엄격 FSD 관점에서 발견한 핵심 결합 (역방향 의존)

| # | 위치 | 문제 | 심각도 |
|---|------|------|--------|
| 1 | `hooks/use-pub-sub/events.ts` | `PubSubEvents` 타입이 도메인 DTO(users/items/dao/currency)를 직접 import → **shared 훅이 전 도메인을 앎** | 최상 |
| 2 | `apis/index.ts` + `hooks/use-api.tsx` | 전역 registry가 모든 도메인 api를 집계하고 `useApi`가 이를 참조 → **shared가 전 도메인 의존** | 최상 |
| 3 | `enums/*`, `components/*` | 도메인 전용 enum·컴포넌트가 "공용" 폴더에 혼재 | 중 |

### 잠재(이관 후 표면화된) 결합
- `components/table/interface/domain/*TableRows.ts` → 도메인 DTO 참조
- `utils/date.util.ts` → calendar-picker 타입 참조
- `utils/admin-role.util.ts` → admin enum 참조
- `apis/services/{profile,usage}` → 타 도메인 enum 참조 (cross-entity)

---

## 3. 제거 대상 (이전 프로젝트 잔재)

사용자 확정:
- **완전 제거**: `ecommerce`, `videos`, `nft`, `parcel` (+ `dao/nft` 슬라이스)
- **병합**: `item-category` → `items`
- **nft 처리 방침**: 전면 제거하되, 유지 도메인(users·dao)의 nft 참조부는 **삭제 대신 주석 처리**(`[nft-removed]`)

### nft ↔ 유지 도메인 결합 (제거 걸림돌)
- `users.dto.ts`: `NFT_TYPES`, `hasNft`, `nftSummary`, `GetNftUser*` (유저 상세 응답 타입 포함)
- `users.api.ts`: `getNftUsers`, `getUserByUserId`(응답 타입이 nft-prefixed)
- `dao/table-rows`: `DaoQuestRewardAction`(dao/nft 유래)

---

## 4. 문서-코드 불일치
- `reference/custom-hooks` SKILL: 상태관리를 `jotai`로 기술 → 실제 코드는 `zustand`. (정정 필요)

---

## 5. 도구/제약
- **git 미사용** (`.git` 없음). 사용자 결정으로 안전망 없이 진행 → **소단위 이동 + 매 단계 tsc 게이트**로 대체.
- tsc 베이스라인: 선재 에러 18건 (대부분 `erasableSyntaxOnly`의 enum/파라미터-프로퍼티 금지, 미사용 import). → 게이트 기준을 "재설계로 인한 신규 결함 0"으로 설정.
