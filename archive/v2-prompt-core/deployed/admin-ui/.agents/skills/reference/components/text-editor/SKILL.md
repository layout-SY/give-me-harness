---
name: component-text-editor
description: synthoria-admin-ui의 공용 TextEditor 사용 가이드. HTML/리치 텍스트 작성 요구사항(뉴스/FAQ/DAO 본문)에서 사용.
---

# Text Editor Component

## 대상

- 현재 `src/`에 TextEditor 구현 파일이 없다. 이 문서는 legacy reference이며 신규 사용 전 실제 대체 자산을 다시 탐색한다.

## 언제 선택하나

- 단순 textarea가 아닌 포맷팅/HTML 콘텐츠 입력이 필요한 경우

## 사용 핵심

- 초기값/변경 핸들러를 controlled 방식으로 연결한다.
- 길이 제한이 있으면 상위에서 명시적으로 검사한다.

## 주의

- 에디터 내부 스타일만으로 부족하면 페이지 컨테이너 스타일로 보강한다.

## 수정(리팩토링) 주의

- React-Quill 라이브러리가 사용되었기 때문에 수정(or 리팩토링) 진행 시 참고한다.
