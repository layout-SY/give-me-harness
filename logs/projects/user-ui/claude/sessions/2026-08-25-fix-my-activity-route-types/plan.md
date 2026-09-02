# 계획

## 목표

`CitizenAuxiliaryRoutes.tsx`의 `@typescript-eslint/no-unsafe-assignment` (`Unsafe assignment of an error typed value`)를 제거하고, 같은 원인으로 깨진 제안 목록 라우트의 타입 오류도 함께 해소한다.

## 범위

- 제안 목록/내 활동 훅 반환 타입을 오류 유형이 되지 않게 고정
- pages 라우트가 feature barrel을 거쳐 훅 타입을 잃지 않도록 import 경로 정리
- 표시 매퍼가 UI 페이지 모듈과 순환하지 않도록 분리

## 제외 사항

- activity API 응답 스키마 재설계
- 제안 목록 UI 마크업·동작 변경
- `src/shared/ui/` 변경

## 제약 조건

- 사용자 지시 `Fix it`을 구현 승인으로 본다
- Hephaestus는 hook/DTO/parser, Claude Code 소유 UI는 타입 오류 해소에 필요한 import·지역 변수만 수정
- 이미지 캡처·별도 리뷰 에이전트 없이 `tsc`/`eslint`/`vitest`로 검증

## 선택한 스킬

- `.agents/skills/policy/harness/SKILL.md`
- `.agents/skills/policy/coding-convention/SKILL.md`
- `.agents/skills/policy/type-definition/SKILL.md`
- `.agents/skills/policy/documentation/SKILL.md`
- `.agents/skills/policy/portfolio/SKILL.md`
- `.agents/skills/policy/review-checklist/SKILL.md`

## 역할 담당

- Hephaestus: DTO·query key·훅·presentation import 경계
- 라우트 UI 파일: 오류 유형을 만드는 barrel import와 지역 매핑만 수정

## 작업 구간

1. 훅/`useQuery` 제네릭과 제안 DTO를 명시 타입으로 고정
2. pages → feature barrel 순환을 깊은 경로 import로 끊기
3. `toActivityItemFromProposalList`를 별도 모듈로 분리
4. lint/build/테스트 후 세션 문서 작성

## 검증

- 대상 파일 ReadLints
- `npx vitest run src/features/citizen-participation src/pages/citizen-participation`
- `npm run lint`
- `npm run build`

## 위험 요소

- IDE projectService와 CLI eslint가 어긋나면 CLI만 통과하고 편집기 오류가 남을 수 있다
- barrel 재export를 유지하면 같은 순환이 다른 라우트에서 재발할 수 있다

## 승인 상태

사용자 원문 `Fix it, verify, and then give a concise explanation`으로 구현을 진행했다.
