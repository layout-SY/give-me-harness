# Exploration — i18n 완전 제거

> 작성일: 2026-07-06
> 요청: 전체 문서와 구현에서 i18n 관련 코드/내용을 전부 제거. UI 문자열은 한글 하드코딩, 언어 기능 완전 제거.

## 1. i18n footprint (제거 전)

### src
- `useLanguage` import 16파일 / `mui["key"]` 50개(정적) + 동적 6곳
- 인프라: `shared/lib/hooks/use-language.ts`, `shared/lib/language.store.ts`, `shared/assets/i18n/{ko,ja}.json`(ko 1005키), `shared/assets/icons/language.icon.tsx`, `shared/config/enums/language.enum.ts`, `shared/config/constants.ts`의 `LOCAL_STORAGE_LANGUAGE_KEY`
- 언어 스위처 UI: `widgets/app-header/ui/header.tsx`

### 동적 mui 사용처 (개별 처리 필요)
| 파일 | 형태 |
| --- | --- |
| `widgets/side-navigation/ui/navigation.tsx` | `mui[x.label]` — config가 label 키 보유 |
| `shared/ui/status/status-badge.tsx` | `mui[label]` — label 프롭이 키 |
| `shared/ui/category/category-badge.tsx` | `mui[labelKey] ?? categoryKey` |
| `shared/api/axios-instance.ts` | `mui[\`_api_err_${msg}\`]` |
| `shared/lib/hooks/use-api.tsx` | `mui[\`_api_err_${msg}\`]` |

### .claude 문서 (~25개)
- 전용 문서: `recipe/i18n/`, `reference/custom-hooks/use-language/`
- 언급 문서: policy(validation/documentation/data-fetch-layer/SKILL 인덱스), recipe(data-fetch/SKILL 인덱스), reference(custom-hooks 인덱스·useFetchAdapter·컴포넌트 다수·use-reason-prompt·header·navigation·badges), dependency(fsd-layer-contract·form-validation), backlog(F-01 등)

## 2. 핵심 판단 — `LANGUAGES` enum 보존

`shared/config/enums/language.enum.ts`의 `LANGUAGES`는 **UI i18n이 아니라 도메인 데이터 필드**다:
- `entities/faq`, `entities/news`, `entities/inquiries`의 DTO에 `language: LANGUAGES`(콘텐츠 언어) 존재.
- → UI 번역 시스템만 제거하고 이 enum은 유지(삭제 시 도메인 DTO 파손).

## 3. 대체 정책 (사용자 확정)
- `mui["key"]` → **ko.json의 한글 값 인라인 하드코딩**.
- ja.json·언어전환·language store/enum(UI용)·use-language·language.icon **완전 삭제**.
- 향후 사용자 노출 문자열은 한글 직접 작성이 표준.

## 4. 제약
- git 저장소 존재(안전망). tsc 게이트 = 0 유지 목표.
- 별개 미커밋 편집(`constants.ts`의 `synthoria-admin-*`→`admin-*` 리브랜딩)은 무관하므로 보존.
