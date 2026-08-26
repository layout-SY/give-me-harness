# 05 파이프라인과 상태

상태 전이는 `EXPLORE -> PLAN -> AWAIT_APPROVAL -> IMPLEMENT -> WATCHER_REVIEW -> EVALUATE -> DOCUMENT -> COMPLETE` 순서다. FAIL이면 범위에 따라 IMPLEMENT 또는 PLAN으로 돌아간다. 차단된 작업은 누락된 입력을 보고하며 승인을 추측하지 않는다.
