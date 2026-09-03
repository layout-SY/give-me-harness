# i18n ko.json 분석 리포트

- 대상 파일: `src/assets/i18n/ko.json`
- 분석일: 2026-04-20

---

## 1. 중복 값 (같은 문자열을 여러 키가 공유)

### 1-1. 단일 키워드 중복

| 값 | 중복 키 |
|---|---|
| `"저장"` | `_save`, `_dao_pass_count_btn_save`, `_maintenance_action_save` |
| `"검색"` | `_search`, `_maintenance_action_search` |
| `"등록"` | `_create`, `_dao_action_register` |
| `"추가"` | `_dao_action_add`, `_dao_pass_create_btn_add` |
| `"이미지 업로드"` | `_image_upload`, `_dao_pass_create_upload_text` |

### 1-2. confirm / success 메시지 중복

| 값 | 해당 키 |
|---|---|
| `"등록 하시겠습니까?"` | `_msg_create_admin_confirm`, `_msg_error_event_attendance_create_confirm`, `_msg_error_event_roulette_create_confirm`, `_msg_create_faq_confirm`, `_msg_create_item_confirm`, `_msg_create_item_category_confirm`, `_msg_create_news_confirm`, `_msg_create_video_confirm`, `_msg_create_video_playlist_confirm` |
| `"등록 되었습니다."` | `_msg_create_admin_success`, `_msg_error_event_attendance_create_success`, `_msg_error_event_roulette_create_success`, `_msg_create_faq_success`, `_msg_create_item_success`, `_msg_create_item_category_success`, `_msg_create_news_success`, `_msg_create_video_success`, `_msg_create_video_playlist_success` |
| `"정말 삭제 하시겠습니까?"` | `_msg_delete_faq_confirm`, `_msg_delete_item_confirm`, `_msg_delete_news_confirm`, `_msg_delete_news_comment_confirm`, `_msg_delete_video_confirm`, `_msg_delete_video_playlist_confirm` |
| `"삭제 되었습니다."` | `_msg_delete_faq_success`, `_msg_delete_item_success`, `_msg_delete_news_success`, `_msg_delete_news_image_success`, `_msg_delete_news_comment_success`, `_msg_delete_video_success`, `_msg_delete_video_playlist_success` |
| `"저장 하시겠습니까?"` | `_msg_update_admin_confirm`, `_msg_update_faq_confirm`, `_msg_update_item_confirm`, `_msg_update_item_category_confirm`, `_msg_save_video_confirm`, `_msg_save_video_playlist_confirm` |
| `"저장 되었습니다."` | `_msg_update_admin_success`, `_msg_update_faq_success`, `_msg_update_item_success`, `_msg_update_item_category_success`, `_msg_save_video_success`, `_msg_save_video_playlist_success` |
| `"수정 하시겠습니까?"` | `_msg_update_event_info_confirm`, `_msg_update_event_config_text_confirm`, `_msg_update_event_reward_confirm`, `_msg_update_profile_confirm` |
| `"수정 되었습니다."` | `_msg_update_event_info_success`, `_msg_update_event_config_text_success`, `_msg_update_event_reward_success`, `_msg_batch_update_item_success`, `_msg_batch_update_news_success`, `_msg_batch_update_faq_list_success`, `_msg_update_profile_success` |
| `"변경 하시겠습니까?"` | `_msg_dao_pass_count_update_confirm`, `_msg_update_user_status_confirm` |
| `"변경 되었습니다."` | `_msg_update_event_config_image_success`, `_msg_dao_pass_count_update_success`, `_msg_update_user_status_success` |

### 1-3. 버그 (오타)

- `_msg_delete_item_image_success`: `"삭제제 되었습니다."` → `"삭제 되었습니다."` 로 수정 필요

---

## 2. 접두사 누락 / 불일치

### 2-1. `_proposal_*` — `_dao_` 접두사 누락

`_dao_proposal_*` 패턴이 존재함에도 일부 키가 `_proposal_` 단독 사용.

| 현재 키 | 추천 키 |
|---|---|
| `_proposal_id` | `_dao_proposal_id` |
| `_proposal_title` | `_dao_proposal_title` |
| `_proposal_vote_status_percentage` | `_dao_proposal_vote_status_percentage` |
| `_proposal_manage_my_only` | `_dao_proposal_manage_my_only` |
| `_proposal_create_success` | `_msg_dao_proposal_create_success` |
| `_msg_error_proposal_create_missing` | `_msg_error_dao_proposal_create_missing` |
| `_msg_error_proposal_title_missing` | `_msg_error_dao_proposal_title_missing` |
| `_msg_error_proposal_content_missing` | `_msg_error_dao_proposal_content_missing` |
| `_msg_error_proposal_category_missing` | `_msg_error_dao_proposal_category_missing` |
| `_msg_error_proposal_vote_start_missing` | `_msg_error_dao_proposal_vote_start_missing` |
| `_msg_error_proposal_vote_end_missing` | `_msg_error_dao_proposal_vote_end_missing` |
| `_msg_error_proposal_min_vote_pass_level_missing` | `_msg_error_dao_proposal_min_vote_pass_level_missing` |

### 2-2. 인증/비밀번호 관련 — `_auth_` 접두사 누락

`_sign_*`, `_password_*`, `_change_password_*`, `_request_change_password_*`으로 파편화.

| 현재 키 | 추천 키 |
|---|---|
| `_sign_in` | `_auth_sign_in` |
| `_sign_out` | `_auth_sign_out` |
| `_sign_up` | `_auth_sign_up` |
| `_request_change_password` | `_auth_request_change_password` |
| `_request_change_password_inst_a` | `_auth_request_change_password_inst_a` |
| `_request_change_password_inst_b` | `_auth_request_change_password_inst_b` |
| `_change_password` | `_auth_change_password` |
| `_change_password_inst` | `_auth_change_password_inst` |
| `_change_password_complete` | `_auth_change_password_complete` |
| `_password_placeholder` | `_auth_password_placeholder` |
| `_password_confirm_placeholder` | `_auth_password_confirm_placeholder` |
| `_password_instruction_a` | `_auth_password_instruction_a` |
| `_password_instruction_b` | `_auth_password_instruction_b` |
| `_password_checklist_a` | `_auth_password_checklist_a` |
| `_password_checklist_b` | `_auth_password_checklist_b` |
| `_password_checklist_c` | `_auth_password_checklist_c` |
| `_password_checklist_d` | `_auth_password_checklist_d` |
| `_msg_request_change_password_success` | `_msg_auth_request_change_password_success` |
| `_msg_error_change_password_link_expired` | `_msg_error_auth_change_password_link_expired` |
| `_msg_error_change_password_link_invalid` | `_msg_error_auth_change_password_link_invalid` |
| `_msg_error_password_missing` | `_msg_error_auth_password_missing` |
| `_msg_error_password_confirm_missing` | `_msg_error_auth_password_confirm_missing` |
| `_msg_error_signin_input_missing` | `_msg_error_auth_signin_input_missing` |
| `_msg_error_signin_input_invalid` | `_msg_error_auth_signin_input_invalid` |
| `_msg_error_signin_input_invalid_attempt` | `_msg_error_auth_signin_input_invalid_attempt` |
| `_msg_error_signin_input_invalid_locked` | `_msg_error_auth_signin_input_invalid_locked` |
| `_msg_signin_confirm_send_password_reset_email` | `_msg_auth_signin_confirm_send_password_reset_email` |
| `_msg_signin_send_password_reset_email_success` | `_msg_auth_signin_send_password_reset_email_success` |
| `_msg_error_password_confirm_not_match` | `_msg_error_auth_password_confirm_not_match` |

### 2-3. 화폐 단위 / 액션 — `_currency_` 접두사 누락

| 현재 키 | 추천 키 |
|---|---|
| `_soria` | `_currency_soria` |
| `_soria_plus` | `_currency_soria_plus` |
| `_point` | `_currency_point` |
| `_sgd` | `_currency_sgd` |
| `_usd` | `_currency_usd` |
| `_deduct` | `_currency_action_deduct` |
| `_recharge` | `_currency_action_recharge` |
| `_redeem` | `_currency_action_redeem` |
| `_reward` | `_currency_action_reward` |

### 2-4. 우편(parcel) — 동사 혼입 및 패턴 불일치

`_send_parcel_*` 방식은 다른 도메인 패턴(`_item_*`, `_news_*` 등)과 불일치.

| 현재 키 | 추천 키 |
|---|---|
| `_send_parcel` | `_parcel_send` |
| `_send_parcel_to` | `_parcel_to` |
| `_send_parcel_title` | `_parcel_title` |
| `_send_parcel_content` | `_parcel_content` |
| `_send_parcel_attach_items` | `_parcel_attach_items` |
| `_msg_error_send_parcel_users_missing` | `_msg_error_parcel_users_missing` |
| `_msg_error_send_parcel_title_missing` | `_msg_error_parcel_title_missing` |
| `_msg_error_send_parcel_content_missing` | `_msg_error_parcel_content_missing` |
| `_msg_error_send_parcel_items_missing` | `_msg_error_parcel_items_missing` |
| `_msg_send_parcel_confirm` | `_msg_parcel_send_confirm` |
| `_msg_send_parcel_success` | `_msg_parcel_send_success` |

### 2-5. 필터/검색 유틸리티 — `_filter_` 패턴 불일치

`_filter_*` 패턴이 존재하나 일부 관련 키가 누락.

| 현재 키 | 추천 키 |
|---|---|
| `_toggle_filters` | `_filter_toggle` |
| `_reset_filters` | `_filter_reset` |
| `_search_keyword` | `_filter_search_keyword` |
| `_query_count` | `_filter_query_count` |
| `_start_at` | `_filter_start_at` |
| `_end_at` | `_filter_end_at` |

### 2-6. 기타 — 도메인 불명확 / 너무 범용

| 현재 키 | 문제 | 추천 키 |
|---|---|---|
| `_manage` | 너무 범용 | `_action_manage` |
| `_manage_detail` | 너무 범용 | `_action_manage_detail` |
| `_new_item_badge` | `_item_` 접두사 누락 | `_item_new_badge` |
| `_image_upload` | 도메인 접두사 필요 | `_upload_image` |
| `_select_users` | popup/action 성격 | `_popup_select_users` |
| `_select_items` | popup/action 성격 | `_popup_select_items` |

---

## 3. 도메인 내 네이밍 혼용

### 3-1. `_dao_discuss_*` vs `_dao_discussion_*`

같은 토론 게시판 도메인에서 두 패턴이 혼재.

- `_dao_discuss_posts_*`, `_dao_discuss_post_id` → `_dao_discussion_*`으로 통일 권장

---

## 4. 정리 방향 제안

| 항목 | 방향 |
|---|---|
| confirm/success 중복 | `_msg_generic_create_confirm` 등 공통 키로 통합 후 도메인별 키 제거 |
| 단일 키워드 중복 | 도메인별 키 제거, 공통 키(`_save`, `_search` 등) 재사용 |
| 접두사 누락 키 | 키 rename + 전체 사용처 일괄 변경 |
| `_dao_discuss_*` 혼용 | `_dao_discussion_*` 단일 패턴으로 통일 |
| 오타 수정 | `_msg_delete_item_image_success` 값 교정 |
