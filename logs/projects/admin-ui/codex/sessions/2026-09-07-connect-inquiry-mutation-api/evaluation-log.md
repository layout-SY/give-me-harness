# 평가 로그

## 현재 판정과의 경계

현재 변경의 PASS/FAIL은 review-log.md에 기록했다. 여기서는 장기 관찰과 후속 선택지를 기록한다.

## 장기 관찰 사항

문의처럼 응답이 상세 객체가 아닌 mutation은 서버 데이터 재조회가 필요하다. 상세 DTO를 반환하는 기존 CP mutation의 setQueryData 방식을 그대로 적용하면 문자열이 상세를 덮어쓸 수 있어 이번 작업에서는 도메인에 맞는 후처리를 사용했다.

## 이 문제가 중요한 이유

답변 삭제 후 null과 오래된 조회 응답을 처리하지 않으면 존재하지 않는 답변을 표시하거나 parser 오류가 생길 수 있다. 이번 테스트는 이 경계를 실제 QueryClient와 Axios/MSW로 확인한다.

## 재사용 가능 자산

공용 ApiClient의 PUT은 기존 get/post/patch/delete와 같은 계약이다. 문의 mutation options는 문의 도메인 안에서만 캐시 후처리를 공유한다.

## 기술 부채

전체 lint에 71 오류·5 경고가 남아 있다. 기존 NoResults의 unused children 오류도 여기에 포함된다. 이를 방치하면 저장소 전체 lint를 완료 게이트로 사용하기 어렵지만, 동시에 정리하면 관련 없는 API·UI 파일까지 수정 범위가 커진다.

## 추상화·아키텍처·의존성 방향

UI → 문의 hook/options → 문의 API → 공용 전송 순서를 유지했다. 공용 CRUD framework를 추가하지 않아 도메인마다 다른 mutation 응답·캐시 의미를 유지한다.

## 프로세스 개선 사항

실제 서버의 오류 응답, 중복 답변 정책, 자동 문의 상태 전이, content 길이 제한을 문서화하면 mock과 서버의 차이를 줄일 수 있다. 현재는 제공된 정상 응답과 null 계약만 확정된 것으로 다룬다.

## 권고 사항

UI 통합 시 같은 문의에 대한 mutation 버튼들을 pending 동안 비활성화하고, 편집 draft가 이전 inquiryId의 결과로 초기화되지 않도록 대상 ID와 성공 시점을 확인한다. 이를 생략하면 중복 제출·다른 문의의 입력 손실 위험이 남으며, 적용 비용은 UI의 pending·ID 확인 로직이다.

## 개선 선택지와 권장 backlog

우선 UI 연결과 실제 backend 계약 검증을 완료한다. 이후 기존 lint를 별도 scope로 개선한다. 공용 mutation abstraction은 다른 도메인에서도 같은 의미와 생명주기가 확인될 때 검토한다.

## 다음 제안 단계

ui 역할에서 handoff.md를 기준으로 문의 목록·상세·답변 편집 및 NoResults 표시를 연결한다.
