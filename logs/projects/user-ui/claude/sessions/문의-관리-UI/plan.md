# 문의 관리 UI 계획

- 역할: UI (inject `--role ui`)
- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`, branch `sy-main` (기준 HEAD `d676dec`)
- 목표: 기존 문의 API·controller(`src/features/inquiry`)를 `/manage/inquiry` 목록·상세·작성 화면에 연결

## 사용자 확정 사항
1. 시민참여 레이아웃 부품을 `src/shared/ui`로 공용화(b)
2. 상태 문구: `OPEN` → 답변대기, `COMPLETED` → 답변완료
3. 문의 유형: 드롭다운, 표시 문구는 응답 코드 그대로(추후 추가 예정)
4. 재문의: 상세의 「재문의」 → `/manage/inquiry/new?prevInquiryId=:id`, 요청에 `prevInquiryId` 포함
5. 생성 성공 시 목록으로 이동(응답에 id 없음)
6. `/manage/**`는 로그인 필수(`AuthRouteBoundary`)
7. 목록 기본 10건, `?page=` URL 유지, 정렬 UI 없음

## 검증
- 포맷 트리거 → `npm run lint`, `npm run test`, `npm run build`
