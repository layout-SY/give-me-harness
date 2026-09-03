---
name: hook-use-language
description: synthoria-admin-ui의 legacy useLanguage 가이드. 현재 구현 파일이 없으므로 신규 사용 전 대체 자산과 i18n 구조를 다시 탐색할 때 사용.
---

# useLanguage Hook

## 대상

- 현재 `src/`에 useLanguage 구현 파일이 없다. 신규 사용 전 `src/shared/lib/hooks/`, app provider, locale 자산을 다시 탐색한다.
- 사전 파일: `src/assets/i18n/ja.json`, `src/assets/i18n/ko.json`
- 연관 atom: `languageAtom`, `languageJsonAtom` (`src/atoms/language.atom.ts`)
- 키: `LOCAL_STORAGE_LANGUAGE_KEY`, `LANGUAGES` enum

## 언제 선택하나

- 컴포넌트/모달/위젯에서 사용자 노출 문자열을 출력할 때 (모든 페이지 공통)
- 헤더에서 언어 변경
- 앱 부트스트랩에서 저장된 언어 복원

## 사용 핵심

- 반환값: `{ language, setLanguage, mui, refreshLanguage }`
  - `mui`: 현재 언어 사전 객체 (`mui["_user_id"]` 형태로 접근)
  - `setLanguage(lang)`: 언어 변경 + localStorage 저장 + 폰트 패밀리 갱신
  - `refreshLanguage()`: localStorage에서 언어 읽어와 적용 (기본값 `LANGUAGES.JA`)

## 호출 예시

```ts
const { mui, setLanguage } = useLanguage();

return <span>{mui["_user_id"]}</span>;
```

```ts
// 앱 시작 시
const { refreshLanguage } = useLanguage();
useEffect(() => {
  refreshLanguage();
}, []);
```

## 주의

- 사용자 노출 문자열은 **반드시** `mui[키]`로 가져온다. 하드코딩은 금지.
- 새 키가 필요하면 `ko.json`/`ja.json`에 동시 추가한다 (현재 EN/ZH는 비활성).
- `setLanguage`는 `<html>`의 `font-family`도 함께 바꾼다. 폰트 외 영역에서 언어별 분기를 추가하려면 이 훅을 수정한다 (페이지에서 분기 금지).
- 사전에 없는 키 접근은 `undefined`를 반환한다. 기본값 fallback이 필요하면 `mui["key"] ?? "fallback"`로 작성한다.
- `mui` 객체 자체는 `useMemo` 의존성에 포함시켜야 언어 전환 시 재계산이 일어난다 (예: `useMemo(..., [mui])`).
