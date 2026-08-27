# Review Log — FSD 아키텍처 재설계

> 작성일: 2026-07-03
> 게이트: `npx tsc --noEmit -p tsconfig.app.json` (매 단계) + `eslint .` + 레이어 경계 감사

---

## 1. 단계별 tsc 게이트 추이

| 단계 | 총 에러 | cannot-find | 판정 |
|------|--------|-------------|------|
| 베이스라인 | 18 | 0 | 기준 |
| S7 제거 | 17 | 0 | ✅ (send-parcel 에러 소멸) |
| S1 assets/config | 17 | 0 | ✅ |
| S1 lib(utils/exceptions/hooks) | 17 | 0 | ✅ |
| S1 config enum | 17 | 0 | ✅ |
| S1 ui(components) | 24→17 | 4→0 | ✅ (store 상대참조 교정 후) |
| S1 api 인프라 | 17 | 0 | ✅ |
| S3 services→entities | 42→17 | 17→0 | ✅ (registry 경로 갱신 후) |
| S3 enum/store | 17 | 0 | ✅ |
| S5 features/widgets | 19→17 | 2→0 | ✅ (상대참조 절대화 + dead 배럴 삭제) |
| S4 api 싱글턴 | 17 | 0 | ✅ |
| S2 pub-sub 병합 | 17 | 0 | ✅ (선언 병합 정상 인식) |
| shared 순수성 마감 | 17 | 0 | ✅ |
| S6 app 셸 | 16 | 0 | ✅ |

> 최종 16건은 전량 **선재** 이슈: TS1294(`erasableSyntaxOnly` enum/param-property) 10 · TS6133(미사용 import) 4 · TS6196(미사용 type) 2. **재설계 기인 신규 결함 0.**

---

## 2. eslint 교차 검증
- `import/no-unresolved` 류 오류 **0** → 모든 이동/remap의 참조 무결성 확인.
- 잔여 error는 선재 `@typescript-eslint/no-explicit-any`, `no-unused-vars` (콘텐츠 품질 이슈, 재설계 무관).

---

## 3. 레이어 경계 감사 (하위 방향만 허용)

| 검사 | 결과 |
|------|------|
| entities → features/widgets/app/pages | ✅ 0 |
| features → widgets/app/pages | ✅ 0 |
| widgets → app/pages | ✅ 0 |
| shared → entities/features/widgets/app | ✅ 0 (주석 2줄 제외) |

### cross-entity 참조 (type-only, 잔여 2건)
| 참조 | 대상 | 처리 |
|------|------|------|
| `entities/profile/api/profile.dto.ts` | `admin-settings`의 `ADMIN_ROLE_TYPE_CODES` | 후속: shared/config 승격 권장 |
| `entities/usage/api/usage.dto.ts` | `sales`의 `TRANSACTION_*` | 후속: shared/config 승격 권장 |

---

## 4. 결합 해소 검증 (초기 3대 결합)

| 결합 | 이전 | 이후 | 검증 |
|------|------|------|------|
| #1 pub-sub | events가 도메인 DTO import | interface + 선언 병합, shared 무지 | `grep ~/entities src/shared/lib/pub-sub` = 0 |
| #2 api registry | useApi가 전역 registry import | entity별 싱글턴 + useApi 순수 실행기 | `grep ~/apis src` = 0 |
| #3 도메인 혼재 | 공용 폴더에 도메인 enum/컴포넌트 | entities로 분리 | shared 순수성 감사 통과 |

---

## 5. 판정
- **PASS** — 구조 이관 무결(참조 오류 0), shared 도메인-무지 확립, 상위 역참조 0, 3대 결합 해소.
- **조건부 항목**: cross-entity 2건·라우터 배선·nft 주석·tsconfig 정책은 후속(`final-summary.md` / `src/ARCHITECTURE.md`).
