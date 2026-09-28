# 검토 로그

## 현재 변경 판정

PASS

## 검토 범위

`src/pages/cp-news`의 신규 파일 8개. 이번 세션에서 다른 경로는 변경하지 않았다.

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 승인된 scope 준수 | PASS | 변경 경로가 모두 `src/pages/cp-news` 아래에 있다 |
| UI·Logic 경계 | PASS | View가 API·검증·캐시·이동을 구현하지 않고 callback으로 위임한다 |
| 타입 검증 | PASS | `npx tsc --noEmit -p tsconfig.app.json`에서 신규 경로 오류 0건 |
| lint | PASS | `npx eslint src/pages/cp-news --ext .ts,.tsx` 출력 없음 |
| 기존 회귀 | PASS | `node --test tests/news-*.test.mjs` 28/28 |
| 번역 키 노출 | PASS | 화면 표기를 페이지 config의 한국어 상수로 정의했다 |
| 서버 집계 보존 | PASS | 목록 집계·순서를 재계산하지 않는다 |
| 실패·빈 결과 구분 | PASS | 조회 실패는 표 대신 오류 영역, 빈 결과는 `Table`의 `NoResults` |
| 미지원 필드 | PASS | 노출 기간·메인 노출·작성자 입력이 없다 |
| 접근성 | PASS | 필터 라벨 연결, 칩 그룹 `ariaLabel`, 오류 문구 `role="alert"` |
| 새 의존성·토큰 | PASS | 추가 없음. 기존 `_cp-admin.css` 토큰만 사용 |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 중 | `src/pages/cp-news/model/cp-news-list.config.ts` | 초안의 상태 배지 색 `gray/green/red`가 `StatusBadgeColor`에 없는 값이었다 | 구현 중 `neutral/positive/warning`으로 교정 완료 |
| 하 | `src/pages/cp-news/ui/cp-news-form-view.tsx` | 상단고정에 `ToggleSwitch`를 쓰면 접근 가능한 이름이 없다 | 구현 중 `ChoiceChipGroup`으로 교체 완료 |

미해결 필수 조치는 없다.

## 반복 문제와 escalation

- `repeat_issue_detected`: 없음
- `escalation_needed`: none

## 결론

현재 변경은 승인된 UI scope 안에서 표현 계층과 controller 계약만 신설했고, 타입·lint·기존 news 회귀 테스트를 통과했다. 다만 화면이 라우트에 연결되지 않아 사용자 접근 경로는 아직 없으며, 기능 동작 PASS는 Logic 통합 후에 판정해야 한다. `npm run build`와 브라우저 확인은 실행하지 않았다.

---

# 2차 검토 — Logic 병합분과 라우트·메뉴 연결

## 현재 변경 판정

PASS

## 검토 범위

- 병합된 Logic 구현(`6f1d322`): `hook/`, `lib/`, 페이지 컴포넌트, controller 테스트
- 이번 UI 변경: `cp-news-form.config.ts`, `cp-news-form-view.tsx`, `routes.tsx`, `_navigation5.ts`

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| controller의 계약 이행 | PASS | `search`·`table`·`error`·`fields`·`delete`·`load` 필드와 callback이 인터페이스와 일치 |
| 검색 쌍 계약 | PASS | `buildNewsListQuery`가 keyword가 있을 때만 `by`와 함께 전송 |
| 서버 집계 보존 | PASS | `totalPages`·`totalElements`·`pinnedItemCount`를 그대로 전달 |
| 늦은 응답 차단 | PASS | `cp-news-form-request.ts`의 generation 카운터로 화면 이탈 후 결과를 무시 |
| 게시 상태 오조작 | PASS(교정 완료) | 상태별 액션 라벨로 "저장"과 "게시 중단"을 분리 |
| 라우트 경로 일치 | PASS | controller가 이동하는 `/cp/news`, `/cp/news/new`, `/cp/news/:newsId/edit`와 등록 라우트가 동일 |
| 기존 진입점 보존 | PASS | `/cp/boards`와 `boards/notices/:noticeId/edit`를 변경하지 않음 |
| 타입·lint·테스트 | PASS | 변경 파일 오류 0건, 46/46 PASS |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 상 | `src/pages/cp-news/ui/cp-news-form-view.tsx` | 게시 중인 공지에서 "임시 저장"이 `status: DRAFT` PATCH를 보내 게시를 내리는데 라벨이 그 결과를 드러내지 않았다 | 상태별 액션 라벨로 교정 완료 |

미해결 필수 조치는 없다.

## 반복 문제와 escalation

- `repeat_issue_detected`: 없음
- `escalation_needed`: none

## 결론

Logic 병합분은 UI 계약을 정확히 이행했고, 라우트·메뉴 연결로 `/cp/news` 접근 경로가 생겼다. 게시 상태 오조작 위험은 View 라벨 교정으로 해소했다. 다만 `npm run build`와 브라우저 확인을 하지 않았으므로 실제 화면 렌더와 서버 연동은 미검증 상태다. 기존 타입 14건·lint 68건은 이번 변경과 무관하게 남아 있다.
