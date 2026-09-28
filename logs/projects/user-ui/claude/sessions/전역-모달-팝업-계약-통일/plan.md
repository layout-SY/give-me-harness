# 전역 모달 팝업 계약 통일 계획

- 역할: ui (inject role)
- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`, 브랜치 `sy-main`, 기준 HEAD `63eda3b`
- 요청: 도메인마다 따로 만든 모달 UI를 하나로 통일한다. 기준은 meeting-reservation 예약 팝업.

## 조사 결과

전역 모달 계층이 다섯 갈래였다.

| 계층 | 구현 | 사용처 |
| --- | --- | --- |
| `shared/ui/popup` | 네이티브 `<dialog class="custom-popup">` | meeting-reservation 4종, citizen `ReportPopup`, `image-upload` |
| `shared/ui/dialog` | 전역 alert/confirm 싱글턴 + zustand | 앱 전역 |
| `shared/ui/modal` | HeroUI `Modal.Root` | `reason-prompt` 하나 |
| `shared/ui/side-modal` | HeroUI `Drawer` | 없음(데드 코드) |
| `shared/ui/image-modal` | 전체화면 이미지 뷰어 | pub-sub `open-image` |

오버레이를 손으로 만든 곳은 없었다. 갈라진 지점은 공용 컨테이너가 둘(`popup`, `modal`)이고, 같은 목적의 팝업이 도메인마다 별도 내부 스타일(`vo-*`, `cp-*`, 하드코딩 hex)을 만든 것이었다.

## 사용자 확정 사항

1. 단일 진입점은 `shared/ui/popup` 유지. HeroUI `modal`·`side-modal`은 제거.
2. 표준 파트까지 통일. 제목·부제·안내박스·액션 영역을 공용 파트로 승격하고 도메인은 그 계약에 연결.
3. `ReasonPrompt`는 기준 규격으로 변경 허용(폭 800px → 480px, 헤더 X 제거, 공용 Button).
4. 전역 `Dialog`(alert/confirm)와 `image-modal`은 대상에서 제외.
5. 공용 클래스 prefix는 `popup-*`.

## 변경 범위

- 신설: `shared/ui/popup/parts/popup-parts.tsx`, `popup-parts.css`. `vo-*` 값을 그대로 옮긴다.
- meeting-reservation 4종 팝업과 `NoticeBox` 사용처를 표준 파트로 교체.
- citizen `ReportPopup` 헤더·액션·컨테이너 중복 선언 제거.
- `ImageUploadPopup`의 원시 `h1`+`hr` 제거.
- `ReasonPrompt`를 `Popup` 기반으로 이전.
- 삭제: `shared/ui/modal/`, `shared/ui/side-modal/`, `parts/NoticeBox.tsx`.
- 테스트 셀렉터 갱신.

## 검증

`npx eslint .`, `npx vitest run`(영향 범위), `npx tsc -b && npx vite build`.
