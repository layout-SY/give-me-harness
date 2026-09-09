# 평가 로그

## 현재 판정과의 경계

현재 구현 판정을 반복하지 않고 장기 운영 영향을 기록한다.

## 장기 관찰 사항

- 포트폴리오 품질은 구조 검사만으로 완전히 보장할 수 없으며 사실성은 대화·실행 근거 검토가 필요하다.
- 사례 단위 구조는 한 작업에서 여러 문제를 분리해 재사용하기에 적합하다.
- `.claude` 보호 경로 추가로 Claude Code 하네스 변경도 동일 governance를 받는다.

## 목록에 등록할 재사용 가능 자산

- `.codex/templates/portfolio-log.template.md`
- `portfolio_issues` 사례 구조 검사

## 기술 부채

- 자연어 내용의 사실성은 자동 판별하지 않는다.
- 과거 세션에는 `portfolio-log.md`가 없을 수 있다.

## 프로세스 개선 사항

- 향후 필요하면 사례 메타데이터를 YAML frontmatter 또는 machine-readable schema로 확장한다.

## 권고 사항

현재는 Markdown 구조와 검증 근거 중심으로 운영하고, 과거 세션 소급은 별도 승인 작업으로 다룬다.
