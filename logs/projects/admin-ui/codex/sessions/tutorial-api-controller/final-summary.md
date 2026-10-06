# 튜토리얼 controller 추가 작업 결과

UI handoff의 편집 규칙을 controller에 반영하고 검증·커밋했다. 커밋은 `811c8bbc4570572e4167c4aeef5e62ea2ac8e6a6`이며 작업 트리는 clean이다.

- 위치: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`, `feature/tutorial`, HEAD `811c8bbc4570572e4167c4aeef5e62ea2ac8e6a6`.
- 제목: 사용자 결정에 따라 Unicode 코드 포인트로 최대 30자를 계산한다. 길이·상한을 UI에 공개하고 공백·31자 이상이면 저장을 막는다.
- 기본값: 등록만 빈 칸 3개로 시작하며 수정은 저장된 페이지 그대로 표시한다. 제목이 유효하면 빈 칸 및 이미지 0개도 저장할 수 있다.
- 페이지: 편집 가능·20개 미만·빈 칸 없음일 때만 추가한다. 전체 배열 및 직접 업로드 추가 경로에도 제한을 적용한다. 기존 20개 초과 값은 표시하고 한 칸씩 줄일 수 있지만 20개 이하로 줄이기 전에는 저장하지 않는다.
- 변경 파일: editor controller, 공개 controller types, controller 테스트 총 3개. 기존 UI·ImageManager·API DTO·패키지는 보존했다.
- 검증: 공식 Prettier 3개 적용 성공, 관련 테스트 29/29(튜토리얼 25 + 이미지 슬롯 4), 전체 lint·타입 검사·build 및 diff --check 통과.
- 테스트 범위: 30/31 코드 포인트와 이모지, 등록 기본값·수정 원본 유지, 빈 칸·20개 추가 제한, 중복 추가, 직접 업로드 사전 차단, 기존 22→21→20개 삭제 후 저장. 등록 빈 칸 3개 전송은 기존 테스트 기대값을 확정 계약에 맞춰 변경했다.
- 제한: 실제 서버 데이터 변경·DOM mount/unmount·시각 QA·독립 Watcher 판정은 수행하지 않았다. 빌드에는 기존 Vite 플러그인·청크 크기 경고가 있다.
- Git: 기존 Logic `6b96d7b`, UI `2967764` 보존. 이번 3개 변경은 사용자 승인 후 `811c8bb` (`feat(tutorial): 제목 길이 및 페이지 편집 규칙 적용`)로 커밋했다. 보호 작업 `26b0b445ff7bdb80c49f0e2b9a9a7ffd` done, git status clean 확인. push·merge는 수행하지 않았다.
- 다음: UI 2차에서 제목 카운터, 페이지 추가 버튼, 세로 목록·드래그 편집을 공개 계약에 연결한다.

[controller 계약](unknown/controller-contract.md)과 [UI 인계](handoff.md)에 필드와 동작 경계를 기록했다.
