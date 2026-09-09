# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- mutations가 `citizenParticipation.parser`를 `.then`하면, parser가 모든 DTO를 끌어와 훅 반환/콜백이 `error` 유형이 된다.
- 토론은 이미 feature DTO 스키마를 직접 parse한다. 투표만 parser를 거쳐 같은 오류가 남았다.

## 목록에 등록할 재사용 가능 자산

없음.

## 기술 부채

- `index.ts`는 여전히 `parseVoteResponse`를 재export한다. 훅이 다시 parser를 `.then`하면 오류가 돌아온다.

## 프로세스 개선 사항

mutation 응답 파싱은 god parser가 아니라 해당 feature API/DTO에서 한다.

## 권고 사항

새 mutation은 `citizenParticipation.parser`를 `.then`하지 않는다.
