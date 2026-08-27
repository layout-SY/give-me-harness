# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- pages 라우트가 `~/features/citizen-participation` barrel에서 훅을 가져오면 typescript-eslint가 반환 타입을 오류 유형으로 본다. 새 라우트는 처음부터 훅 깊은 경로를 쓰는 편이 낫다.

## 목록에 등록할 재사용 가능 자산

없음.

## 기술 부채

- 다른 상세 라우트(`CitizenReadDetailRoutes` 등)가 아직 barrel을 쓰면 같은 오류가 날 수 있다.

## 프로세스 개선 사항

투표 상세 훅을 연결할 때 목록 라우트의 깊은 import를 같이 적용하지 않아 같은 오류가 다시 났다.

## 권고 사항

시민참여 pages 라우트의 훅 import를 barrel에서 제외하는 규칙을 라우트 추가 시 기본으로 둔다.
