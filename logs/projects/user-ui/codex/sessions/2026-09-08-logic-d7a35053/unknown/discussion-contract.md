# 토론 임시 API 계약

## 상태와 근거

화면정의서 `/Users/okand/Downloads/시민참여v_4.8.pdf` 8~9쪽과 기존 API 경로를 기준으로 구현한 임시 계약이다. 실제 백엔드 명세와 운영 서버 응답으로 확정한 계약이 아니다. 서버 명세가 제공되면 DTO·parser·HTTP 테스트를 함께 대조한다.

## 요청

| 작업 | HTTP·경로 | 데이터 |
| --- | --- | --- |
| 목록 | GET /citizen/discussions | page·size 양의 정수, mine=true/false, optional status·search·sort |
| 상세 | GET /citizen/discussions/{id} | id URL 인코딩 |
| 의견 선택 등록 | POST /citizen/discussions/{id}/participations | choice: AGREE / DISAGREE / NEUTRAL |
| 댓글 조회·등록 | GET·POST /citizen/discussions/{id}/comments | 기존 댓글 페이지 계약·content 본문 |
| 좋아요 | POST /citizen/discussions/{id}/comments/{commentId}/likes | 기존 좋아요 응답 계약 |
| 신고 | POST /citizen/discussions/{id}/reports | 기존 commentId·reason·optional detail 계약 |

## 응답

- 기존 ApiClient가 성공·실패 envelope를 해석하고 성공 데이터만 Zod로 검증한다.
- 목록: items, page, pageSize, itemCount, pageCount.
- 항목: id, type=discussion, status=open/closed, title, summary, createdAt. authorName·commentCount·찬성/반대/중립 count는 optional이다.
- 상세: 항목의 summary 대신 body. period·canParticipate·myDiscussionChoice를 추가한다.
- count와 myDiscussionChoice의 null·누락은 값 없음으로 정규화한다. 잘못된 상태·의견·숫자·날짜를 조용히 대체하지 않는다.
- 참여: id, completed, choice. completed=true에만 완료 상태와 캐시 갱신을 적용한다.
- 댓글 stance는 optional AGREE/DISAGREE/NEUTRAL이며 화면에서는 찬성/반대/중립으로 변환한다.

## 동작

- 진행 중 집계는 UI에 전달하지 않는다. 종료 후에도 세 집계값이 모두 있어야 비율을 계산한다.
- 진행 상태와 canParticipate를 사용하며 표시용 period 문자열에서 시각을 추론하지 않는다.
- 로그인·진행 조건을 만족할 때 의견·댓글을 등록하고, 이미 제출된 의견과 중복 요청을 보호한다.
- 브라우저용 MSW는 토론 전체 하위 경로를 통과시킨다. 명시적으로 만든 테스트 factory는 기존 토론 mock을 제공한다.
