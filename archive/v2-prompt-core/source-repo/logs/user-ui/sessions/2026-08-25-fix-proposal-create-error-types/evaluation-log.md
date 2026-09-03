# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- feature barrel이 UI·훅·parser·DTO를 한 번에 재export하면, pages가 페이지 하나만 가져도 생성 API까지 `error` 유형으로 무너진다.
- CLI eslint 파일 단위는 통과하고 IDE `projectService`만 실패하는 패턴이 반복된다.

## 목록에 등록할 재사용 가능 자산

없음.

## 기술 부채

- `index.ts`는 여전히 훅과 parser를 재export한다. 새로 barrel에서 가져오는 파일이 생기면 같은 오류가 돌아온다.
- `useVoteMutation`의 parser `.then`은 같은 그래프에 남아 있다.

## 프로세스 개선 사항

시민참여 pages와 테스트는 처음부터 `hook/`·`api/`·`ui/` 깊은 경로를 쓴다. 생성/목록 DTO를 한 파일에 두지 않는다.

## 권고 사항

barrel을 UI 전용으로 줄이거나, 훅/DTO 재export를 중단한다.
