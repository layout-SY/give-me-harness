# 리뷰 로그

## 리뷰 대상
- `src/pages/cp-survey/ui/` 설문 목록 페이지 패턴 정렬

## 결과
- 보류 (`paused_after_generator`)

## 체크리스트 검토
- SKILL 준수: Refactorer self-check만 수행. Watcher 미실행.
- 재사용 확인: 공용 목록 추상화 훅을 만들지 않고 vote 도메인 전용 패턴을 복제함.
- 검증 확인: 처리 payload는 entity DTO 필드(`status`, `externalUrl`)만 전달. URL 형식은 서버/MSW 스키마에 위임.
- Payload 완결성: 변경된 필드만 optional로 전송.
- 성능 우려: placeholderData 구간 행 클릭/저장 가드 유지.
- 중복 코드 우려: CP 목록 훅 세트가 도메인마다 반복되지만, 기존 vote/proposal/discussion과 동일한 약한 추상화 결정.

## 위반 사항
1. 없음 (Watcher 미실행, 구현자 self-check 기준)

## 필수 수정 사항
1. 없음

## 반복 이슈
- false

## 에스컬레이션
- none

## 비고
- AGENTS.md: Claude Code API 비가용 시 Watcher를 실행하지 않고 `paused_after_generator`로 둔다.
