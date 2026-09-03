---
name: component-navigation
description: synthoria-admin-ui의 Navigation 사용 가이드. 좌측 메뉴/권한/환경 기반 노출 제어가 필요한 레이아웃 요구사항에서 사용.
---

# Navigation Component

## 대상

- `src/components/navigation/navigation.tsx`
- 실 라우팅 데이터 : `_navigation1.tsx`~`_navigation4.tsx`
  - 형태

    ```ts
    export const _navigation4 = [
      {
        icon: settingsIcon,
        label: "관리자 설정",
        path: "/admin-settings",
        sublinks: [
          { label: "관리자 관리", path: "/admin-settings/admins" },
          { label: "감사 로그", path: "/admin-settings/audit" },
          { label: "정책 관리", path: "/admin-settings/policies" },
          { label: "점검 관리", path: "/admin-settings/maintenance" },
        ],
      },
    ];
    ```

    - 네비게이션 영역 상 섹션이 구분되어 `_navigation1 ~ 4`로 분류된다.

## 언제 선택하나

- 전역 사이드 네비게이션 또는 메뉴 섹션 확장이 필요할 때

## 사용 핵심

- 기존 섹션 분할 구조를 따른다. 메뉴 label은 한글 문자열로 직접 작성한다.
- 라우팅 경로/권한 조건은 기존 패턴에 맞게 추가한다.

## 주의

- 네비게이션 변경은 전 페이지 영향이 크므로 최소 변경으로 진행한다.
