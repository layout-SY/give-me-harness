---
name: component-pagination
description: {{PROJECT_NAME}}의 공용 Pagination(src/shared/ui/pagination) 사용 및 수정 가이드. 10개 단위 페이지 묶음과 1-based 페이지 계약을 다룰 때 사용.
---

# Pagination

## 대상

- `src/shared/ui/pagination/pagination.tsx`
- `src/shared/ui/pagination/pagination.css`

## 계약

`@heroui/react`의 `Pagination`을 감싼 래퍼다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `page` | `0` | 현재 페이지. **1-based다** |
| `pageCount` | `0` | 전체 페이지 수 |
| `handler` | 필수 | `(page: number) => void` |

페이지 번호는 `getValues`가 10개 단위 묶음으로 계산한다. 현재 페이지가 속한 10단위 구간만 노출하며 `pageCount`를 넘지 않는다. `page`가 10의 배수면 이전 구간에 속하도록 보정한다.

- 이전 버튼은 `page - 1 <= 0`일 때 비활성이다.
- 다음 버튼은 `page >= pageCount`일 때 비활성이다.
- 현재 페이지 링크는 활성인 동시에 비활성이다. 중복 호출을 막는다.

## 사용 기준

- 페이지는 1부터 센다. 0-based 인덱스를 그대로 넘기지 않는다.
- 페이지 크기와 총 개수 계산은 소비처 책임이다. 이 컴포넌트는 `pageCount`만 받는다.
- 표 목록은 `table`의 데이터 흐름과 함께 사용한다.

## 수정 규칙

- `getValues`의 10단위 묶음 규칙은 화면 전반의 페이징 UX 계약이다. 임의로 바꾸지 않는다.
- 1-based 전제를 0-based로 바꾸지 않는다. 모든 소비처가 함께 깨진다.
- 경계 비활성 조건을 완화하면 범위를 벗어난 페이지 요청이 발생한다.
