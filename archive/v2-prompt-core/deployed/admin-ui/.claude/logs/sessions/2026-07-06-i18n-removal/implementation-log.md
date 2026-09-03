# Implementation Log — i18n 완전 제거

> 작성일: 2026-07-06
> 기법: ko.json 기반 스크립트 치환 + 동적 개별 편집 + 인프라 삭제 + 문서 정리. tsc 게이트 0 유지.

## A. 코드 (src)

### A1. 정적 mui 치환 (스크립트)
- `node`로 ko.json 로드 → `mui["KEY"]`/`mui['KEY']`를 `JSON.stringify(ko[KEY])`(한글)로 치환.
- **50개 전량 치환**, ko.json에 없는 키 0(모두 존재).

### A2. 동적 6곳 개별 처리
- `navigation.tsx`: 렌더 `{mui[x.label]}`·`{mui[y.label]}` → `{x.label}`·`{y.label}`.
- `_navigation1..4.ts`(model): `label: "_key"` → 한글(스크립트, **51개**). 커밋된 주석 1건만 잔존(무해).
- `status-badge.tsx`: `{mui[label]}` → `{label}` (label 프롭이 표시 문자열).
- `category-badge.tsx`: `label ?? mui[labelKey] ?? categoryKey` → `label ?? categoryKey` (labelKey 제거).
- `axios-instance.ts`: `_api_err_*` mui 조회 브랜치 제거 → rawMessage 사용. `useLanguageStore` import 제거.
- `use-api.tsx`: 에러 다이얼로그 `translated ?? message` → `message`. useLanguage import/`mui` dep 제거.

### A3. useLanguage 제거 (일괄 sed)
- `import useLanguage ...` 줄 + `const { mui } = useLanguage();` 줄 삭제, dep 배열 `mui` 제거 — 대상 파일 전체.

### A4. 인프라 삭제
```
rm shared/lib/hooks/use-language.ts
rm shared/lib/language.store.ts
rm -r shared/assets/i18n
rm shared/assets/icons/language.icon.tsx
```
- `header.tsx`: 언어 스위처 `<li>`(무동작 버튼) + `languageIcon` import 제거.
- `constants.ts`: 고아 `LOCAL_STORAGE_LANGUAGE_KEY` 제거.

### A5. 보존
- `shared/config/enums/language.enum.ts`(`LANGUAGES`) — faq/news/inquiries DTO의 콘텐츠 언어 필드. 유지.

### 검증
- `tsc --noEmit`: **0 errors**. eslint import/정의 오류 0.

## B. 문서 (.claude)

### B1. 삭제
- `skills/recipe/i18n/`, `skills/reference/custom-hooks/use-language/`, `skills/reference/components/send-parcel/`(이미 제거된 컴포넌트).

### B2. 정책/계약/인덱스
- `policy-validation`: 에러 메시지 "i18n 키" → **한글 zod message 직접 작성**. frontmatter/규칙 갱신.
- `dependency/2026-07-06-form-validation` 계약: `{mui[error.message]}` → `{error.message}`, "i18n 키 치환" → "zod message에 한글 직접".
- `src/shared/ui/form/index.ts` placeholder 주석 동기화.
- policy 인덱스(validation 설명), recipe 인덱스(recipe-i18n 행 삭제 + 예시 문구), policy-documentation, data-fetch-layer, fsd-layer-contract(useLanguage 제거).
- reference 인덱스·custom-hooks 인덱스: `useLanguage` 행/규칙/링크/체크리스트 항목 제거.

### B3. 예제/레퍼런스
- `recipe/data-fetch`: 예제의 useLanguage/`mui["_msg_*"]` → 한글 직접("삭제하시겠습니까?"/"삭제되었습니다.").
- `use-reason-prompt`·`reason-prompt`: mui 예제 → 한글, i18n 책임 문구 → "라벨은 호출부 책임(한글 직접)", cancelLabel 기본값 "취소".
- `header` ref: 언어전환 서술 제거. `navigation` ref: label 키 예제 → 한글.
- badges/button/text-input/text-area/search-state-bar/no-results, COMMON/PAGE/DOMAIN_COMPONENTS, useFetchAdapter: "mui 키 사용" → "한글 직접 작성".

### B4. backlog
- F-01(moderation i18n 키) **폐기** 처리, use-language 링크 티켓 **해결** 표기, FSD 경로 매핑에서 assets/i18n 제거.

### B5. 보존 판단
- **과거 세션 로그**(2026-07-03 implementation-log 등)의 i18n 언급은 당시 사실 기록이라 이력 보존(히스토리 미조작).
