---
name: component-no-results
description: {{PROJECT_NAME}}의 빈 목록 표시(src/shared/ui/no-results) 사용 및 수정 가이드. 조회 결과 없음 상태를 다룰 때 사용.
---

# NoResults

## 대상

- `src/shared/ui/no-results/no-results.tsx`
- `src/shared/ui/no-results/no-result.css`

파일명이 `no-result.css`로 단수다. 디렉터리·컴포넌트 이름과 다르다.

## 계약

`React.HTMLAttributes<HTMLDivElement>`를 받는 단순 표시 컴포넌트다.

- `~/shared/assets/icons/block.icon`과 고정 문구 `"내역이 없습니다."`를 렌더링한다.
- **`children`을 받지만 렌더링하지 않는다.** 문구를 바꿀 수 없다.
- 루트 클래스는 `no-results`다.

## 사용 기준

- `table`이 로딩이 아니고 행이 없을 때 자동으로 이 컴포넌트를 렌더링한다. 표 아래에 중복 배치하지 않는다.
- 표가 아닌 영역의 빈 상태에 직접 사용한다.
- 다른 문구가 필요하면 이 컴포넌트를 쓰지 말고 소비처에서 구성한다. `table`의 `emptyContent`가 그 용도다.

## 수정 규칙

- `children`을 렌더링하도록 바꾸면 기존 호출부의 의도치 않은 내용이 노출될 수 있다. 변경 전 호출부를 전수 확인한다.
- 고정 문구를 다국어 키로 바꾸는 변경은 사용자 승인을 받는다.
- CSS 파일명 `no-result.css`를 정정하려면 import 경로를 함께 고친다.
