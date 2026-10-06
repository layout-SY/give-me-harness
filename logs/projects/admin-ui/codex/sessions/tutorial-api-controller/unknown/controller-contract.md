# 튜토리얼 controller 연결 계약

상태: 구현·Prettier·자동 검증 완료. 튜토리얼 25개·이미지 슬롯 4개 테스트(총 29개), lint·build 통과. Logic 선행으로 UI가 이 계약에 맞춘다.

## 진입점과 데이터

- `src/pages/tutorial/index.ts`에서 `useTutorialListController`, `useTutorialDetailController`, `useTutorialActionsController`, `useTutorialEditorController` 및 공개 타입을 import한다. 기존 앱의 QueryClientProvider 안에서 호출한다.
- 목록은 `items`와 `isEmpty`, `load`를 제공한다. 항목은 `id/title/pageCount/createdAt/updatedAt`이며 서버 배열 순서와 날짜 문자열을 유지한다. 서버의 name은 사용자 확인에 따라 상세 title과 같은 제목으로 매핑한다. 페이지네이션은 없다. 대기·실패를 빈 목록 성공으로 표시하지 않는다.
- 상세는 목록의 `id`를 `useTutorialDetailController(id)`에 전달한다. 미선택은 `null`이다. `item`은 `id/title/images`이고 각 이미지의 `id/imageUrl`을 보존한다. 다른 ID로 전환하면 해당 ID의 Query 캐시를 사용하며 이전 ID 데이터를 임시로 표시하지 않는다.
- `load`에는 `isPending/isFetching/isFailed/errorMessage/onRetry`가 있다. 서버 오류는 기존 공통 reporter가 표시하므로 `isFailed: true`이면서 `errorMessage: null`일 수 있다.

## UI 입력과 동작

- 입력 `TutorialFormInput`: `{ title, images? }`, images는 `null` 또는 `{ imageUrl: string | null }[]`이다. 상세 이미지 배열을 그대로 입력할 수 있지만 응답 이미지 ID는 전송하지 않는다.
- 등록·수정 모두 images 생략/null/배열을 허용한다. 수정에서 생략/null은 기존 이미지 유지, []는 전부 삭제다. 배열은 입력 순서대로 sortOrder를 0부터 부여해 전체 교체한다.
- `onCreate(values)`, `onUpdate(tutorialId, values)`, `onDelete(tutorialId)`, `onUploadImage(file)`를 제공한다. 함수 결과는 `status: success/failed/busy/canceled`로 구분한다. success의 value는 등록·수정·삭제에서 undefined, 업로드에서 URL 문자열이다. 생성 ID를 추측하지 않는다.
- 이미지 업로드는 단독 스토리지 업로드다. 성공 URL을 UI가 해당 편집 이미지의 imageUrl에 넣고 등록/수정으로 저장한다. 파일은 비어 있지 않아야 한다. 명세 밖의 파일 확장자·크기 제한은 추가하지 않는다.
- actions는 마지막 `operation/tutorialId`와 `isPending/isSuccess/isFailed/errorMessage/onReset`을 제공한다. 같은 hook 인스턴스에서 작업이 진행 중이면 다른 변경·업로드는 busy로 반환한다. 요청 중 reset은 무시한다. 편집 입력은 UI가 소유하고 조회 재갱신으로 자동 덮어쓰지 않는다.
- 상세 대상이 바뀌면 UI는 편집 컨테이너의 key를 ID별로 분리해 작업 수명을 종료한다. controller는 unmount 시 진행 중 요청을 취소하고 늦은 결과를 canceled로 반환한다. 별도 인스턴스 사이 요청 잠금은 공유하지 않는다.
- 저수준 actions를 직접 사용할 때 삭제 확인은 UI가 맡는다. editor를 사용하면 확인 상태와 동작을 제공하며, 확인창 표시와 화면 닫기·이동은 UI가 맡는다. 삭제는 서버상 복구 불가능한 실제 삭제다. 수정으로 교체된 이미지의 스토리지 파일은 서버에서 자동 삭제하지 않는다.

## 편집 화면 controller

- `useTutorialEditorController(mode, tutorialId)`를 사용한다. mode는 create/edit이고 등록 ID는 null이다. 페이지는 mode와 ID를 React key에 포함해 편집 수명을 분리한다.
- `fields`는 title, `(string | null)[]` images, 준비·변경 여부, 제목·페이지 오류 및 입력 callback을 제공한다. 제목은 공백만 입력할 수 없고 Unicode 코드 포인트 기준 30자 이하여야 한다. `titleLength`는 `Array.from(title).length`, `titleMaxLength`는 30이다. 일반 이모지 😀는 1자지만 결합 문자·ZWJ는 각각 센다. 공백도 길이에 포함하며 입력을 자르거나 정규화하지 않는다.
- 등록 모드만 `[null, null, null]`로 시작한다. 수정 모드는 저장된 페이지 그대로 표시한다. 빈 칸은 페이지 수에 포함되며, 빈 칸 3개 그대로 저장하면 imageUrl:null 3개를 전송한다. 모든 칸을 지운 []도 제목이 유효하면 저장할 수 있다.
- `maxImages`는 20이며 `canAddImage`는 편집 가능·20개 미만·빈 칸 없음 조건을 모두 만족할 때 true다. 요청 중·삭제 확인 중에는 false다. `onAddEmpty`는 이 조건에서 끝에 빈 칸 하나만 추가한다. 같은 렌더에서 중복 호출해도 추가한 빈 칸 때문에 두 번째 추가는 무시한다.
- `onImagesChange`는 20개를 넘는 배열을 거부하고 빈 칸이 있는 상태에서 개수를 늘리는 입력도 거부한다. 단, 서버에 이미 20개를 넘는 값이 있으면 한 칸씩 줄일 수 있도록 개수가 감소하는 입력은 20개 초과여도 허용한다. 동일 개수의 교체는 20개 이하일 때 허용한다.
- 서버의 기존 초과 페이지는 자르지 않고 모두 표시한다. `imagesError`에 20개 이하로 줄이라는 메시지를 제공하고 `save.errorMessage`에도 반영한다. title을 바꿔도 20개를 넘으면 canSave:false이며 onSave는 요청 없이 failed를 반환한다. 삭제로 20개 이하가 되면 오류가 해제된다. `onRemoveImage`·`onMoveImage`는 기존 동작을 유지한다.
- 첫 변경 때 서버 데이터를 draft로 복사하고 후속 재조회가 draft를 덮어쓰지 않는다. 저장은 현재 슬롯 전체를 배열로 전달한다. 저수준 actions의 images 생략/null 계약은 그대로 유지한다.
- `fields.onAddImage(file)`은 추가 조건을 업로드 전에 검사하고 성공 URL을 끝에 추가한다. 빈 칸이 있거나 이미 20개이면 업로드하지 않는다. `fields.uploadApi(FormData)`는 ImageManager용으로 URL을 반환하고 슬롯 반영은 해당 UI의 onChange가 맡는다. 두 경로 중 UI 흐름에 맞는 하나를 사용한다.
- uploadApi는 FormData에서 file만 추출하며 type 등 다른 필드는 보내지 않는다. 실패 시 원래 오류로 reject한다. 다른 작업이 진행 중이거나 편집할 수 없는 상태이면 AbortError로 reject한다.
- `save`는 canSave/isSaving/isSuccess/errorMessage/onSave를 제공한다. `delete`는 isAvailable/isOpen/isDeleting/isSuccess/errorMessage와 onRequest/onCancel/onConfirm을 제공한다. 확인 상태 없이 onConfirm을 호출해도 삭제하지 않는다.
- `preview`의 url/onOpen(index)/onClose로 미리보기 상태를 제어한다. 빈 슬롯의 URL은 null이다. `isNotFound`로 404 또는 TUTORIAL_NOT_FOUND를 구분한다. 요청 ID와 응답 ID가 다르면 편집·저장을 차단한다.
- 저장·삭제·업로드 중 변경 동작은 직렬화한다. 생성 성공 응답에는 ID가 없으므로 상세 이동 ID를 추측하지 않는다. 경로·화면 이동은 후속 UI 계약에서 결정한다.

## 캐시와 오류

- 생성 성공: 목록 무효화. 수정 성공: 목록과 해당 상세 무효화. 삭제 성공: 해당 상세 요청 취소·캐시 제거 및 목록 무효화. 업로드 성공은 튜토리얼 캐시를 변경하지 않는다.
- Query/mutation은 실패 ApiResult를 기존 unwrap으로 throw하고 parser를 거쳐 성공 payload를 검증한다. 잘못된 body나 업무/HTTP/전송 실패를 성공으로 처리하지 않는다.
- 응답 DTO는 전 필드 필수이며 imageUrl만 nullable이다. JSON 정수 ID는 안전한 정수 표현 범위를 검사한다. 별도 envelope DTO를 중복 작성하지 않으며 기존 ApiClient가 공통 envelope를 처리한다.

## 검증 계획과 제한

- `tests/tutorial-contract.test.mjs`: 필수·nullable·배열 응답·입력·빈 파일 검증.
- `tests/tutorial-controller.test.mjs`: 실제 Axios/MSW를 통과하는 6개 API, 인증·multipart·순서 매핑·캐시·오류·취소·controller SSR 상태 및 중복 요청.
- SSR 테스트는 실제 DOM mount/unmount를 실행하지 않는다. unmount cleanup은 코드 검토 범위이며 브라우저 자동화는 수행하지 않는다.
- 후속 변경 3개 파일에 공식 formatter apply 성공. `node --test tests/tutorial-contract.test.mjs tests/tutorial-controller.test.mjs tests/image-manager-slots.test.mjs` 29/29 및 전체 lint·build 통과. 30/31 코드 포인트, 등록 3칸·수정 유지, 빈 칸과 20개 추가 제한, 기존 초과 값의 단계적 삭제 후 저장을 검증했다. 실제 서버 호출 검증이나 독립 Watcher 판정으로 확대해 해석하지 않는다.
- 최대 길이·페이지 수는 편집 controller 규칙이다. 기존 API DTO·저수준 actions의 Swagger 계약은 변경하지 않았다. UI는 제목 카운터·페이지 추가 버튼·최대 개수 prop에 공개 fields를 사용해야 한다. 현재 1차 UI의 카운터·버튼 연결은 다음 UI 단계다.
