# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다. 장기적인 문서·하네스 개선 사항만 기록한다.

## 장기 관찰 사항

- project별 prompt 복제는 정책 drift와 비교 비용을 만든다.
- host별 session store가 다른 만큼 공통 evidence schema와 host adapter가 함께 필요하다.
- token 총량만으로 낭비를 판단하면 정상 작업까지 잘못 귀속할 수 있으므로 chronology와 사용자 피드백을 함께 보존해야 한다.

## 목록에 등록할 재사용 가능 자산

- AI 세션·하네스 사고용 `portfolio-log.template.md` 필드
- OpenCode compaction 지시 유실 작성 예시
- session 사용량의 인과 해석 제한 문구

## 기술 부채

- user-ui OpenCode·Claude host adapter는 production UI·CSS, browser, screenshot, Watcher를 직접 hard deny하지 않는다.
- 중앙 공통 하네스와 project profile compiler는 아직 구현되지 않았다.

## 프로세스 개선 사항

- 하네스 사고 조사 시 session ID, 사용자 prompt, compaction chronology, tool/file 실행, 사용량을 하나의 evidence table로 수집한다.
- 하네스 변경 릴리스는 각 host conformance test와 project별 version pin으로 검증한다.

## 권고 사항

현재 문서 스키마를 중앙 하네스의 공통 invariant로 승격하고 프로젝트별 템플릿은 생성 산출물로 관리한다.
