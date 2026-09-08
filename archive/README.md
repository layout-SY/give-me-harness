# 정책 세대 아카이브

이 디렉터리는 현재 중앙 정책(V3)에 앞선 수작업 세대의 파일을 보존한 기록이다.

## 정본이 아니다

- 렌더, `sync`, `audit`, guard 판정의 대상이 아니다. `bin/agent-policy`는 이 경로를 읽지 않는다.
- 여기 있는 문구, 역할 배정, 호스트 고정 표현은 현재 운영 계약과 충돌한다. 참조하지 않는다.
- 현재 계약의 정본은 `policy/common/`, `policy/guards/`, `adapters/`다.
- 파일 수정, 정리, 재포맷을 하지 않는다. 기록으로서의 가치는 원형 유지에 있다.

## 세대 구분

| 세대 | 내용 | 원본 위치 |
| --- | --- | --- |
| V1 | `admin-ui`에만 존재하던 수작업 세대 | `archive/v1-admin-ui-pre-core/` |
| V3 | 현재 중앙 저장소 | 저장소 루트 (아카이브 아님) |

## V1 판별 근거

`admin-ui`의 정책 파일 중 다음 두 조건을 모두 만족하는 122개를 V1으로 분류했다.

1. 폐기된 자동 배포 헤더 주석이 없다.
2. `user-ui`에 같은 경로가 없거나 내용이 다르다.

특징은 다음과 같다.

- 프로젝트명이 현재와 다른 `synthoria-admin-ui`로 기록되어 있다.
- `.agents/skills/reference/**`와 `.claude/skills/reference/**`가 43쌍 중 7쌍만 일치한다. 손으로 두 번 복제된 흔적이다.
- `user-ui`에는 이 세대가 존재하지 않는다.

`MANIFEST.sha256`은 복사 시점의 무결성 기록이다.

## 제외한 파일

- `admin-ui`의 `.claude/settings.local.json`: 사용자 전역 Git ignore가 `**/.claude/settings.local.json`을 대상으로 하고 있어 아카이브에 포함하지 않았다. 개인 권한 설정이며 정책 세대 판별에 필요하지 않다.
- `__pycache__/**`와 `.DS_Store`: 생성물이다.

폐기된 자동 배포 저장소와 그 소비자 사본 archive는 inject-only 전환 후 현재 트리에서 제거했다.
