# Final Summary — i18n 완전 제거

> 작성일: 2026-07-06
> 상세: `exploration.md` · `implementation-log.md`

## What Changed
- 프로젝트에서 **i18n(다국어) 시스템 완전 제거**, 사용자 노출 문자열을 **한글 하드코딩**으로 전환.
- 코드: 정적 `mui["key"]` 50개 + navigation label 51개 → 한글, 동적 mui 6곳 개별 처리, `useLanguage` 전면 제거, i18n 인프라(use-language/language.store/i18n json/language.icon/언어 스위처/language 상수) 삭제.
- 문서: i18n 전용 문서 삭제, 정책·계약·인덱스·레퍼런스·backlog에서 i18n 규칙/예제 → "한글 직접 작성"으로 갱신.

## Why It Changed
- 사용자 요청: i18n 관련 코드/문서 전부 제거. 단일 한국어 운영.

## Impacted Areas
- src: ~20파일(치환/삭제) + 인프라 5개 삭제.
- .claude: 전용 문서 2개 삭제 + ~20개 문서 갱신 + backlog 정리.

## Remaining Risks
- **`LANGUAGES` enum 유지**: UI i18n이 아닌 도메인 콘텐츠 언어 필드(faq/news/inquiries DTO)라 의도적으로 보존. 이후 이 필드를 다룰 때 "UI i18n 아님"을 유의.
- **과거 세션 로그의 i18n 언급 보존**: 이력 기록이라 미수정(현재 상태와 혼동 주의).
- **constants.ts 리브랜딩**(`admin-*`)은 별개 미커밋 편집이라 이번 범위 아님.

## Verification
- `tsc --noEmit`: **0 errors**. eslint import/정의 오류 0.
- src 잔여 `mui`/`useLanguage`/`assets/i18n` 참조 0(LANGUAGES 도메인 enum 제외).
- living 문서 잔여 i18n 키/`mui[` 0("i18n 제거됨" 상태 노트만 잔존).

## Follow-up
- 향후 사용자 노출 문자열은 한글 직접 작성이 표준(정책·레퍼런스 반영 완료).
- constants.ts 리브랜딩은 calendar-picker와 별개 커밋으로 분리 권장(이전 세션 후속과 동일).
