# 검토·검증 결과

useApi의 요청한 동시 호출 동작, 직접 소비처, 타입·lint·build, 중앙 정책 검증은 통과했다. user-ui 전체 테스트에는 해결하지 않은 실패가 있다.

| 검증                                           | 결과                                                     | 해석                                                                               |
| ---------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 변경 전 useApi 회귀                            | 19개 중 5 실패/14 통과                                   | 새 최신 호출 계약과 기존 구현의 차이를 재현                                        |
| 변경 후 useApi + useMeetingEntry + MeetingPage | 3개 파일 36 통과                                         | 두 완료 순서, stale 성공/오류, loading, unmount와 직접 소비처 확인                 |
| user-ui 전체 npm run test                      | 92개 파일 82 통과/10 실패, 758개 테스트 720 통과/38 실패 | MSW endpoint/handler 불일치, UI assertion·시간 초과 등. 변경 전 전체 비교는 미실행 |
| user-ui npm run lint                           | 통과                                                     | 수정 및 현재 소스 정적 규칙 확인                                                   |
| user-ui npm run build                          | 통과                                                     | TypeScript와 Vite 빌드; 500 kB chunk 경고 남음                                     |
| python3 -m unittest discover -s tests -v       | 344개 통과, 1437.327초                                   | 중앙 repo의 현재 변경 전체를 포함한 회귀 suite                                     |
| bin/agent-policy audit                         | central-contract, admin 276/user 206 bundle 파일 통과    | 중앙 계약과 렌더 산출물 검증                                                       |

주요 명령: `npm run test -- src/shared/lib/hooks/use-api.test.tsx src/features/meeting/hook/useMeetingEntry.test.tsx src/features/meeting/ui/MeetingPage.test.tsx --maxWorkers=2`. 중앙 전체 로그는 docs/operations/2026-09-17-api-pattern-unittest.log에 보존한다.

## 리뷰한 위험

- latest 정책은 이전 HTTP를 자동 취소하거나 서버 mutation을 되돌리지 않는다. 모든 결과가 필요한 독립 명령은 인스턴스/조정을 분리해야 한다.
- Query signal 전달, 실패 ApiResult의 throw, parser 검증 위치, mutation 취소/갱신 순서를 스킬에 구분했다. admin의 mixed ExecuteResult 타입 제약도 숨기지 않았다.
- API 전수 도달성은 정적 모듈 수준이며 서버 성공 증거가 아니다. 미연결 레거시를 운영 장애로 단정하지 않았다.
- 최초 세션 조사 후보 7개 중 중앙 프로세스 1개를 제외하고 소비자 6개로 확정했다. 최종 재확인 시 6개 모두 필수 2종은 작성했고 portfolio는 없다.
- skill-creator quick_validate는 현재 Python에 PyYAML이 없어 실행되지 않았다. 중앙 renderer/audit와 별도 frontmatter·참조 검사로 검증했다. 이 의존성 때문에 전체 환경에 임의 패키지를 설치하지 않았다.

실 backend·브라우저 E2E·기존 세션 재시작·다른 세션의 포트폴리오 대필은 수행하지 않았다.
