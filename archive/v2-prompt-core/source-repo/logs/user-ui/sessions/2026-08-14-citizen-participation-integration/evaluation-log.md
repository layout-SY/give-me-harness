# 시민참여 production UI 장기 평가

## 결론

현재 integration layer는 generic API DTO와 richer production UI 계약 사이의 차이를 격리한다. Backend DTO가 확장되면 presenter만 교체할 수 있다.

## 후속 계약

- Proposal create용 category field/value vocabulary.
- Comment report endpoint 또는 request의 target comment id.
- Survey question schema와 participation URL.
- Author, 기간, D-Day, 정책 처리 단계의 backend fields.
- Vote/discussion `scheduled` 전용 UI state.
