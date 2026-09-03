# 평가 로그

## 현재 판정과의 경계

Watcher는 이번 상세 DTO와 path만 판정했다.

## 장기 관찰 사항

- 토론·정책·설문 상세는 아직 `ContentDetailDto`다. 스펙이 오면 제안·투표와 같이 분리할 수 있다.
- 목록 `author`는 여전히 필수다. 탈퇴 작가가 목록에도 null이면 별도 계약이 필요하다.
- 화면 `reviewResult`는 서버 필드가 아니라 status 라벨이다.

## 목록에 등록할 재사용 가능 자산

없음. 기존 투표 상세 패턴을 따랐다.

## 기술 부채

MSW 내부 저장은 여전히 `ContentDetailDto`이고 GET 때 `toProposalDetailResponse`로 번역한다.

## 프로세스 개선 사항

없음

## 권고 사항

댓글·신고 path도 `/citizen/{collection}/...`로 맞춰 두었다. 백엔드 컬렉션명이 다르면 그때 수정한다.
