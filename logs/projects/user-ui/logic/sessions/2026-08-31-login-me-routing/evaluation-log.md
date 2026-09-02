# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

- 현재 source diff는 9개 파일, 142 insertions, 38 deletions이며 production UI 변경은 없다.
- 직전 Watcher는 source blocker를 발견하지 않았고 필수 문서 미완료만 전체 FAIL 사유로 판정했다.
- 아래 내용은 현재 구현의 결함 판정이 아니라 장기 유지보수 관점의 관찰과 권고다.

## 장기 관찰 사항

1. `AuthRouteBoundary`가 보호 경로 진입에서도 `serverErrorQueue`의 `reauthenticate` 이벤트를 사용하면서 전역 재인증 흐름은 API 401과 라우팅 경계를 함께 조정하는 애플리케이션 자산이 됐다.
2. 복귀 위치 보안 책임은 `ApiErrorDialogBridge`와 `createAuthReturnState()`에 유지됐다. 보호 경계는 경로를 이벤트에 넣지 않고, bridge가 확인 시점 위치를 정제한다.
3. 최초 비인증은 콘텐츠를 차단하고 사용 중 만료는 활성 Dialog 동안 콘텐츠를 유지하도록 의도적으로 구분했으며 두 분기 모두 회귀 테스트로 고정했다.
4. current-user의 `/me` 변경은 `getMe()`에만 적용하고 `/citizen/me/activity`를 유지해 API 변경 범위를 리소스 단위로 제한했다.
5. 관련·전체 테스트와 브라우저 pathname 검증 범위는 충분하지만 실제 인증된 backend 성공 payload는 자격 증명과 CORS 제약으로 확인하지 못했다.

## 목록에 등록할 재사용 가능 자산

- `.codex/memory/reusable-assets.md`에는 공용 `dialog`가 이미 등록돼 있지만 재인증 큐·브리지·복귀 위치 정제 계약은 별도 자산으로 등록돼 있지 않다.
- 후속 문서 작업에서 다음 두 자산을 등록하는 것을 권고한다.
  1. `src/shared/api/error/server-error-queue.ts` → `src/app/providers/ApiErrorDialogBridge.tsx` → `src/shared/ui/dialog/`의 재인증 안내·이동 파이프라인.
  2. `src/features/auth/model/authReturnLocation.ts`의 인증 복귀 위치 정제기.
- `AuthRouteBoundary` 자체는 라우팅 구성 요소이므로 독립 공용 자산보다 위 파이프라인의 소비 사례로 기록하는 편이 적절하다.
- 현재 승인 범위에 `.codex/memory`가 포함되지 않으므로 이번 작업에서는 목록을 수정하지 않는다. 이 누락은 현재 구현의 blocker가 아니다.

## 기술 부채

- `AuthRouteBoundary.tsx`는 bit snapshot, 만료 timer, queue subscription, mount-time state와 생명주기 ref를 함께 조정한다. 현재 테스트가 분기를 보호하므로 인증 상태 종류가 실제로 증가할 때만 명명된 상태 모델 추출을 검토한다.
- MSW의 `"*/me"` matcher는 향후 다른 `/me` 리소스가 생기면 넓을 수 있다. 현재 adapter 테스트가 정확한 pathname을 보호하므로 충돌이 실제 발생할 때 origin 기반 matcher로 좁힌다.
- 실제 인증된 `/me` 성공 payload는 미검증이다. backend 통합 환경과 안전한 단기 테스트 계정이 제공되면 status와 parser 호환성을 확인한다.
- build의 500 kB 초과 chunk 경고는 이번 변경에서 새로 발생했다는 근거가 없다. 별도 성능 작업에서 bundle 분석 후 다룬다.

## 프로세스 개선 사항

- source 품질과 무관한 문서 완료 순서 때문에 최초 Watcher가 FAIL했다. 최종 Watcher 호출 전 `evaluation-log.md`와 `final-summary.md` 완료 여부를 체크리스트에 포함한다.
- TypeScript LSP 미설치와 Markdown LSP 미구성으로 diagnostics를 실행하지 못했다. 별도 승인된 환경 설정 작업에서 LSP 구성을 검토한다.
- 브라우저 QA에서 이전 인증 저장값과 같은 문서 navigation이 초기 관찰을 왜곡했다. 인증 QA 절차에 storage 초기화, 새 문서 또는 실제 reload, `performance.timeOrigin` 확인을 포함한다.

## 권고 사항

1. P1: 본 세션의 필수 문서를 완성하고 동일 Watcher 세션에 최종 판정을 요청한다.
2. P2: 별도 승인 후 재인증 안내·이동 파이프라인과 `createAuthReturnState()`를 재사용 자산 목록에 등록한다.
3. P2: backend 통합 환경이 제공되면 인증된 `GET /me` 성공 payload를 검증한다.
4. P3: 인증 상태가 실제로 증가할 때만 `AuthRouteBoundary` snapshot 모델 추출을 검토한다.
5. P3: mock endpoint 충돌이 발생할 때 `"*/me"` matcher를 좁힌다.
6. P3: 별도 환경 작업으로 TypeScript LSP와 인증 브라우저 QA 초기화 절차를 표준화한다.

현재 구현 결함은 이 장기 평가에서 추가로 발견되지 않았다.
