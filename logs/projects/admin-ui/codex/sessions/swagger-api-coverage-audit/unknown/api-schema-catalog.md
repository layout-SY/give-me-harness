# DTO schema 전체 사전

원본의 **196개 components.schemas**를 필드 누락 없이 수록했다. [API별 연결](./api-contracts.md)에서 DTO 이름을 선택해 이 문서를 참조한다. DTO 이름은 서버 명세의 이름이며 현재 TypeScript 타입 이름과 일치한다는 뜻은 아니다.

`required`가 없으면 해당 객체의 필수 목록이 명세에 기재되지 않은 것이다. `nullable` 미기재와 생략 가능성은 구분한다. 빈 schema `{}`는 어떤 값인지 구체화하지 않은 것으로, `null`, `string`, `{}` 중 하나로 확정하면 안 된다. 사용자 확정 예외(시민제안 `reviewResult` null/누락 허용)는 [T01](./api-work-items.md#t01)에 별도로 기록했다.

## 색인

- [AccountResponse](#schema-accountresponse)
- [AdjustUserPointRequest](#schema-adjustuserpointrequest)
- [AdminApiResponseTokenResponse](#schema-adminapiresponsetokenresponse)
- [AdminUserResponse](#schema-adminuserresponse)
- [ApiResponse](#schema-apiresponse)
- [ApiResponseAdminUserResponse](#schema-apiresponseadminuserresponse)
- [ApiResponseBoolean](#schema-apiresponseboolean)
- [ApiResponseCreateItemResponse](#schema-apiresponsecreateitemresponse)
- [ApiResponseCreateRoleResponse](#schema-apiresponsecreateroleresponse)
- [ApiResponseDailyDashboardResponse](#schema-apiresponsedailydashboardresponse)
- [ApiResponseEventAttendanceResponse](#schema-apiresponseeventattendanceresponse)
- [ApiResponseEventRouletteResponse](#schema-apiresponseeventrouletteresponse)
- [ApiResponseExternalDashboardResponse](#schema-apiresponseexternaldashboardresponse)
- [ApiResponseGetItemDetailResponse](#schema-apiresponsegetitemdetailresponse)
- [ApiResponseGetPlaylistResponse](#schema-apiresponsegetplaylistresponse)
- [ApiResponseInquiryDetailResponse](#schema-apiresponseinquirydetailresponse)
- [ApiResponseListEventAttendanceItemResponse](#schema-apiresponselisteventattendanceitemresponse)
- [ApiResponseListEventRouletteItemResponse](#schema-apiresponselisteventrouletteitemresponse)
- [ApiResponseListGetItemCategoryResponse](#schema-apiresponselistgetitemcategoryresponse)
- [ApiResponseListMaintenanceResponse](#schema-apiresponselistmaintenanceresponse)
- [ApiResponseListManagedMenuResponse](#schema-apiresponselistmanagedmenuresponse)
- [ApiResponseListMenuGroupResponse](#schema-apiresponselistmenugroupresponse)
- [ApiResponseListPermissionCategoryResponse](#schema-apiresponselistpermissioncategoryresponse)
- [ApiResponseListRoleSummaryResponse](#schema-apiresponselistrolesummaryresponse)
- [ApiResponseLong](#schema-apiresponselong)
- [ApiResponseMaintenanceResponse](#schema-apiresponsemaintenanceresponse)
- [ApiResponseMapStringString](#schema-apiresponsemapstringstring)
- [ApiResponseMeResponse](#schema-apiresponsemeresponse)
- [ApiResponseMonthlyDashboardResponse](#schema-apiresponsemonthlydashboardresponse)
- [ApiResponseObject](#schema-apiresponseobject)
- [ApiResponsePageResponseAccountResponse](#schema-apiresponsepageresponseaccountresponse)
- [ApiResponsePageResponseEventAttendanceSummaryResponse](#schema-apiresponsepageresponseeventattendancesummaryresponse)
- [ApiResponsePageResponseEventRouletteSummaryResponse](#schema-apiresponsepageresponseeventroulettesummaryresponse)
- [ApiResponsePageResponseGetAdminAllAuditLogResponse](#schema-apiresponsepageresponsegetadminallauditlogresponse)
- [ApiResponsePageResponseGetInquiryTypeResponse](#schema-apiresponsepageresponsegetinquirytyperesponse)
- [ApiResponsePageResponseGetItemSummaryResponse](#schema-apiresponsepageresponsegetitemsummaryresponse)
- [ApiResponsePageResponseGetPlaylistSummaryResponse](#schema-apiresponsepageresponsegetplaylistsummaryresponse)
- [ApiResponsePageResponseGetVideoListResponse](#schema-apiresponsepageresponsegetvideolistresponse)
- [ApiResponsePageResponseInquirySummaryResponse](#schema-apiresponsepageresponseinquirysummaryresponse)
- [ApiResponsePageResponseItemHistoryResponse](#schema-apiresponsepageresponseitemhistoryresponse)
- [ApiResponsePageResponseParcelHistoryResponse](#schema-apiresponsepageresponseparcelhistoryresponse)
- [ApiResponsePageResponsePointHistoryResponse](#schema-apiresponsepageresponsepointhistoryresponse)
- [ApiResponsePageResponseProposalSummaryResponse](#schema-apiresponsepageresponseproposalsummaryresponse)
- [ApiResponsePageResponseUserWithdrawLogResponse](#schema-apiresponsepageresponseuserwithdrawlogresponse)
- [ApiResponsePageResponseVoteSummaryResponse](#schema-apiresponsepageresponsevotesummaryresponse)
- [ApiResponseProposalResponse](#schema-apiresponseproposalresponse)
- [ApiResponseProposalStatusCountResponse](#schema-apiresponseproposalstatuscountresponse)
- [ApiResponseRoleDetailResponse](#schema-apiresponseroledetailresponse)
- [ApiResponseUpdateItemResponse](#schema-apiresponseupdateitemresponse)
- [ApiResponseUploadEventAttendanceConfigImageResponse](#schema-apiresponseuploadeventattendanceconfigimageresponse)
- [ApiResponseUploadEventRouletteConfigImageResponse](#schema-apiresponseuploadeventrouletteconfigimageresponse)
- [ApiResponseUploadItemImageResponse](#schema-apiresponseuploaditemimageresponse)
- [ApiResponseVoid](#schema-apiresponsevoid)
- [ApiResponseVoteDetailResponse](#schema-apiresponsevotedetailresponse)
- [ApiResponseVoteStatusCountResponse](#schema-apiresponsevotestatuscountresponse)
- [ApiResponseWeeklyDashboardResponse](#schema-apiresponseweeklydashboardresponse)
- [AttendanceConfigItem](#schema-attendanceconfigitem)
- [BatchUpdateNewsListRequest](#schema-batchupdatenewslistrequest)
- [CitizenProposalResponse](#schema-citizenproposalresponse)
- [CitizenProposalStatusCountResponse](#schema-citizenproposalstatuscountresponse)
- [CitizenProposalSummaryResponse](#schema-citizenproposalsummaryresponse)
- [CitizenVoteDetailResponse](#schema-citizenvotedetailresponse)
- [CitizenVoteStatusCountResponse](#schema-citizenvotestatuscountresponse)
- [CitizenVoteSummaryResponse](#schema-citizenvotesummaryresponse)
- [CreateEventAttendanceRequest](#schema-createeventattendancerequest)
- [CreateEventRouletteRequest](#schema-createeventrouletterequest)
- [CreateInquiryTypeRequest](#schema-createinquirytyperequest)
- [CreateItemCategoryRequest](#schema-createitemcategoryrequest)
- [CreateItemRequest](#schema-createitemrequest)
- [CreateItemResponse](#schema-createitemresponse)
- [CreateNewsRequest](#schema-createnewsrequest)
- [CreatePlaylistRequest](#schema-createplaylistrequest)
- [CreateRoleRequest](#schema-createrolerequest)
- [CreateRoleResponse](#schema-createroleresponse)
- [CreateVideoRequest](#schema-createvideorequest)
- [DailyDashboardResponse](#schema-dailydashboardresponse)
- [EventAttendanceConfigResponse](#schema-eventattendanceconfigresponse)
- [EventAttendanceItemDto](#schema-eventattendanceitemdto)
- [EventAttendanceItemResponse](#schema-eventattendanceitemresponse)
- [EventAttendanceResponse](#schema-eventattendanceresponse)
- [EventAttendanceSummaryResponse](#schema-eventattendancesummaryresponse)
- [EventRouletteConfigResponse](#schema-eventrouletteconfigresponse)
- [EventRouletteItemDto](#schema-eventrouletteitemdto)
- [EventRouletteItemResponse](#schema-eventrouletteitemresponse)
- [EventRouletteResponse](#schema-eventrouletteresponse)
- [EventRouletteSummaryResponse](#schema-eventroulettesummaryresponse)
- [ExternalDashboardResponse](#schema-externaldashboardresponse)
- [ExternalInquiryStatsResponse](#schema-externalinquirystatsresponse)
- [ExternalItemStatsResponse](#schema-externalitemstatsresponse)
- [ExternalOsStatsResponse](#schema-externalosstatsresponse)
- [ExternalUserStatsResponse](#schema-externaluserstatsresponse)
- [GetAccountListRequest](#schema-getaccountlistrequest)
- [GetAdminAllAuditLogResponse](#schema-getadminallauditlogresponse)
- [GetEventAttendanceListRequest](#schema-geteventattendancelistrequest)
- [GetEventRouletteListRequest](#schema-geteventroulettelistrequest)
- [GetInquiryTypeResponse](#schema-getinquirytyperesponse)
- [GetItemCategoryResponse](#schema-getitemcategoryresponse)
- [GetItemDetailResponse](#schema-getitemdetailresponse)
- [GetItemHistoryListRequest](#schema-getitemhistorylistrequest)
- [GetItemLatestIdRequest](#schema-getitemlatestidrequest)
- [GetItemSummaryResponse](#schema-getitemsummaryresponse)
- [GetItemsRequest](#schema-getitemsrequest)
- [GetMaintenanceItemRequest](#schema-getmaintenanceitemrequest)
- [GetPlaylistResponse](#schema-getplaylistresponse)
- [GetPlaylistSummaryResponse](#schema-getplaylistsummaryresponse)
- [GetPointHistoryListRequest](#schema-getpointhistorylistrequest)
- [GetVideoListResponse](#schema-getvideolistresponse)
- [GrantUserAuthorityRequest](#schema-grantuserauthorityrequest)
- [InquiryAnswerRequest](#schema-inquiryanswerrequest)
- [InquiryCommentResponse](#schema-inquirycommentresponse)
- [InquiryDetailResponse](#schema-inquirydetailresponse)
- [InquirySummaryResponse](#schema-inquirysummaryresponse)
- [Item](#schema-item)
- [ItemHistoryResponse](#schema-itemhistoryresponse)
- [ItemSalesRankResponse](#schema-itemsalesrankresponse)
- [LoginRequest](#schema-loginrequest)
- [MaintenanceConfigItem](#schema-maintenanceconfigitem)
- [MaintenanceResponse](#schema-maintenanceresponse)
- [ManagedMenuResponse](#schema-managedmenuresponse)
- [MeResponse](#schema-meresponse)
- [MenuGroupResponse](#schema-menugroupresponse)
- [MenuItemResponse](#schema-menuitemresponse)
- [MonthlyDashboardResponse](#schema-monthlydashboardresponse)
- [NewsApiResponseCommentList](#schema-newsapiresponsecommentlist)
- [NewsApiResponseDetail](#schema-newsapiresponsedetail)
- [NewsApiResponseList](#schema-newsapiresponselist)
- [NewsApiResponseVoid](#schema-newsapiresponsevoid)
- [NewsCommentResponse](#schema-newscommentresponse)
- [NewsDetailResponse](#schema-newsdetailresponse)
- [NewsListResponse](#schema-newslistresponse)
- [NewsSummaryResponse](#schema-newssummaryresponse)
- [OsCountResponse](#schema-oscountresponse)
- [PageResponseAccountResponse](#schema-pageresponseaccountresponse)
- [PageResponseCitizenProposalSummaryResponse](#schema-pageresponsecitizenproposalsummaryresponse)
- [PageResponseCitizenVoteSummaryResponse](#schema-pageresponsecitizenvotesummaryresponse)
- [PageResponseEventAttendanceSummaryResponse](#schema-pageresponseeventattendancesummaryresponse)
- [PageResponseEventRouletteSummaryResponse](#schema-pageresponseeventroulettesummaryresponse)
- [PageResponseGetAdminAllAuditLogResponse](#schema-pageresponsegetadminallauditlogresponse)
- [PageResponseGetInquiryTypeResponse](#schema-pageresponsegetinquirytyperesponse)
- [PageResponseGetItemSummaryResponse](#schema-pageresponsegetitemsummaryresponse)
- [PageResponseGetPlaylistSummaryResponse](#schema-pageresponsegetplaylistsummaryresponse)
- [PageResponseGetVideoListResponse](#schema-pageresponsegetvideolistresponse)
- [PageResponseInquirySummaryResponse](#schema-pageresponseinquirysummaryresponse)
- [PageResponseItemHistoryResponse](#schema-pageresponseitemhistoryresponse)
- [PageResponseNewsCommentResponse](#schema-pageresponsenewscommentresponse)
- [PageResponseParcelHistoryResponse](#schema-pageresponseparcelhistoryresponse)
- [PageResponsePointHistoryResponse](#schema-pageresponsepointhistoryresponse)
- [PageResponseUserWithdrawLogResponse](#schema-pageresponseuserwithdrawlogresponse)
- [Pageable](#schema-pageable)
- [ParcelHistoryResponse](#schema-parcelhistoryresponse)
- [PatchEventAttendanceConfigRequest](#schema-patcheventattendanceconfigrequest)
- [PatchEventAttendanceRequest](#schema-patcheventattendancerequest)
- [PatchEventRouletteConfigRequest](#schema-patcheventrouletteconfigrequest)
- [PatchEventRouletteRequest](#schema-patcheventrouletterequest)
- [PeriodInquiryStatsResponse](#schema-periodinquirystatsresponse)
- [PeriodItemSalesRankResponse](#schema-perioditemsalesrankresponse)
- [PeriodItemStatsResponse](#schema-perioditemstatsresponse)
- [PeriodUserStatsResponse](#schema-perioduserstatsresponse)
- [PermissionCategoryResponse](#schema-permissioncategoryresponse)
- [PermissionResponse](#schema-permissionresponse)
- [PlaylistVideoResponse](#schema-playlistvideoresponse)
- [PointHistoryResponse](#schema-pointhistoryresponse)
- [RoleDetailResponse](#schema-roledetailresponse)
- [RoleSummary](#schema-rolesummary)
- [RoleSummaryResponse](#schema-rolesummaryresponse)
- [RouletteConfigItem](#schema-rouletteconfigitem)
- [SendParcelRequest](#schema-sendparcelrequest)
- [SetMaintenanceTimeRequest](#schema-setmaintenancetimerequest)
- [SetMaintenanceVersionRequest](#schema-setmaintenanceversionrequest)
- [TokenResponse](#schema-tokenresponse)
- [UpdateAccountRolesRequest](#schema-updateaccountrolesrequest)
- [UpdateCitizenProposalReviewResultRequest](#schema-updatecitizenproposalreviewresultrequest)
- [UpdateCitizenProposalStatusRequest](#schema-updatecitizenproposalstatusrequest)
- [UpdateEventAttendanceItemsRequest](#schema-updateeventattendanceitemsrequest)
- [UpdateEventRouletteItemsRequest](#schema-updateeventrouletteitemsrequest)
- [UpdateInquiryStatusRequest](#schema-updateinquirystatusrequest)
- [UpdateInquiryTypeRequest](#schema-updateinquirytyperequest)
- [UpdateItemCategoryRequest](#schema-updateitemcategoryrequest)
- [UpdateItemRequest](#schema-updateitemrequest)
- [UpdateItemResponse](#schema-updateitemresponse)
- [UpdateItemsListStatusRequest](#schema-updateitemsliststatusrequest)
- [UpdateMaintenanceItemRequest](#schema-updatemaintenanceitemrequest)
- [UpdateMenuOrderRequest](#schema-updatemenuorderrequest)
- [UpdateMenuRequest](#schema-updatemenurequest)
- [UpdateNewsRequest](#schema-updatenewsrequest)
- [UpdatePlaylistRequest](#schema-updateplaylistrequest)
- [UpdateRolePermissionsRequest](#schema-updaterolepermissionsrequest)
- [UpdateRoleRequest](#schema-updaterolerequest)
- [UpdateUserStatusRequest](#schema-updateuserstatusrequest)
- [UpdateVideoRequest](#schema-updatevideorequest)
- [UploadEventAttendanceConfigImageResponse](#schema-uploadeventattendanceconfigimageresponse)
- [UploadEventRouletteConfigImageResponse](#schema-uploadeventrouletteconfigimageresponse)
- [UploadItemImageResponse](#schema-uploaditemimageresponse)
- [UserStatusCountResponse](#schema-userstatuscountresponse)
- [UserWithdrawLogResponse](#schema-userwithdrawlogresponse)
- [WeeklyDashboardResponse](#schema-weeklydashboardresponse)

<a id="schema-accountresponse"></a>

## AccountResponse

참조 DTO: [RoleSummary](./api-schema-catalog.md#schema-rolesummary).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "loginId": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "department": {
      "type": "string"
    },
    "roles": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/RoleSummary"
      }
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-adjustuserpointrequest"></a>

## AdjustUserPointRequest

필수 필드: `amount`, `direction`.

```json
{
  "type": "object",
  "properties": {
    "amount": {
      "type": "integer",
      "format": "int32",
      "minimum": 0
    },
    "direction": {
      "type": "string",
      "enum": [
        "RECHARGE",
        "DEDUCT"
      ]
    },
    "reason": {
      "type": "string",
      "maxLength": 510,
      "minLength": 0
    }
  },
  "required": [
    "amount",
    "direction"
  ]
}
```

<a id="schema-adminapiresponsetokenresponse"></a>

## AdminApiResponseTokenResponse

참조 DTO: [TokenResponse](./api-schema-catalog.md#schema-tokenresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/TokenResponse"
    }
  }
}
```

<a id="schema-adminuserresponse"></a>

## AdminUserResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "publicId": {
      "type": "string",
      "format": "uuid"
    },
    "nickname": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": [
        "ACTIVE",
        "SUSPENDED",
        "WITHDRAWN"
      ]
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "updatedAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-apiresponse"></a>

## ApiResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {}
  }
}
```

<a id="schema-apiresponseadminuserresponse"></a>

## ApiResponseAdminUserResponse

참조 DTO: [AdminUserResponse](./api-schema-catalog.md#schema-adminuserresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/AdminUserResponse"
    }
  }
}
```

<a id="schema-apiresponseboolean"></a>

## ApiResponseBoolean

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "boolean"
    }
  }
}
```

<a id="schema-apiresponsecreateitemresponse"></a>

## ApiResponseCreateItemResponse

참조 DTO: [CreateItemResponse](./api-schema-catalog.md#schema-createitemresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/CreateItemResponse"
    }
  }
}
```

<a id="schema-apiresponsecreateroleresponse"></a>

## ApiResponseCreateRoleResponse

참조 DTO: [CreateRoleResponse](./api-schema-catalog.md#schema-createroleresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/CreateRoleResponse"
    }
  }
}
```

<a id="schema-apiresponsedailydashboardresponse"></a>

## ApiResponseDailyDashboardResponse

참조 DTO: [DailyDashboardResponse](./api-schema-catalog.md#schema-dailydashboardresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/DailyDashboardResponse"
    }
  }
}
```

<a id="schema-apiresponseeventattendanceresponse"></a>

## ApiResponseEventAttendanceResponse

참조 DTO: [EventAttendanceResponse](./api-schema-catalog.md#schema-eventattendanceresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/EventAttendanceResponse"
    }
  }
}
```

<a id="schema-apiresponseeventrouletteresponse"></a>

## ApiResponseEventRouletteResponse

참조 DTO: [EventRouletteResponse](./api-schema-catalog.md#schema-eventrouletteresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/EventRouletteResponse"
    }
  }
}
```

<a id="schema-apiresponseexternaldashboardresponse"></a>

## ApiResponseExternalDashboardResponse

참조 DTO: [ExternalDashboardResponse](./api-schema-catalog.md#schema-externaldashboardresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/ExternalDashboardResponse"
    }
  }
}
```

<a id="schema-apiresponsegetitemdetailresponse"></a>

## ApiResponseGetItemDetailResponse

참조 DTO: [GetItemDetailResponse](./api-schema-catalog.md#schema-getitemdetailresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/GetItemDetailResponse"
    }
  }
}
```

<a id="schema-apiresponsegetplaylistresponse"></a>

## ApiResponseGetPlaylistResponse

참조 DTO: [GetPlaylistResponse](./api-schema-catalog.md#schema-getplaylistresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/GetPlaylistResponse"
    }
  }
}
```

<a id="schema-apiresponseinquirydetailresponse"></a>

## ApiResponseInquiryDetailResponse

참조 DTO: [InquiryDetailResponse](./api-schema-catalog.md#schema-inquirydetailresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/InquiryDetailResponse"
    }
  }
}
```

<a id="schema-apiresponselisteventattendanceitemresponse"></a>

## ApiResponseListEventAttendanceItemResponse

참조 DTO: [EventAttendanceItemResponse](./api-schema-catalog.md#schema-eventattendanceitemresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventAttendanceItemResponse"
      }
    }
  }
}
```

<a id="schema-apiresponselisteventrouletteitemresponse"></a>

## ApiResponseListEventRouletteItemResponse

참조 DTO: [EventRouletteItemResponse](./api-schema-catalog.md#schema-eventrouletteitemresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventRouletteItemResponse"
      }
    }
  }
}
```

<a id="schema-apiresponselistgetitemcategoryresponse"></a>

## ApiResponseListGetItemCategoryResponse

참조 DTO: [GetItemCategoryResponse](./api-schema-catalog.md#schema-getitemcategoryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/GetItemCategoryResponse"
      }
    }
  }
}
```

<a id="schema-apiresponselistmaintenanceresponse"></a>

## ApiResponseListMaintenanceResponse

참조 DTO: [MaintenanceResponse](./api-schema-catalog.md#schema-maintenanceresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/MaintenanceResponse"
      }
    }
  }
}
```

<a id="schema-apiresponselistmanagedmenuresponse"></a>

## ApiResponseListManagedMenuResponse

참조 DTO: [ManagedMenuResponse](./api-schema-catalog.md#schema-managedmenuresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/ManagedMenuResponse"
      }
    }
  }
}
```

<a id="schema-apiresponselistmenugroupresponse"></a>

## ApiResponseListMenuGroupResponse

참조 DTO: [MenuGroupResponse](./api-schema-catalog.md#schema-menugroupresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/MenuGroupResponse"
      }
    }
  }
}
```

<a id="schema-apiresponselistpermissioncategoryresponse"></a>

## ApiResponseListPermissionCategoryResponse

참조 DTO: [PermissionCategoryResponse](./api-schema-catalog.md#schema-permissioncategoryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/PermissionCategoryResponse"
      }
    }
  }
}
```

<a id="schema-apiresponselistrolesummaryresponse"></a>

## ApiResponseListRoleSummaryResponse

참조 DTO: [RoleSummaryResponse](./api-schema-catalog.md#schema-rolesummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/RoleSummaryResponse"
      }
    }
  }
}
```

<a id="schema-apiresponselong"></a>

## ApiResponseLong

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-apiresponsemaintenanceresponse"></a>

## ApiResponseMaintenanceResponse

참조 DTO: [MaintenanceResponse](./api-schema-catalog.md#schema-maintenanceresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/MaintenanceResponse"
    }
  }
}
```

<a id="schema-apiresponsemapstringstring"></a>

## ApiResponseMapStringString

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    }
  }
}
```

<a id="schema-apiresponsemeresponse"></a>

## ApiResponseMeResponse

참조 DTO: [MeResponse](./api-schema-catalog.md#schema-meresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/MeResponse"
    }
  }
}
```

<a id="schema-apiresponsemonthlydashboardresponse"></a>

## ApiResponseMonthlyDashboardResponse

참조 DTO: [MonthlyDashboardResponse](./api-schema-catalog.md#schema-monthlydashboardresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/MonthlyDashboardResponse"
    }
  }
}
```

<a id="schema-apiresponseobject"></a>

## ApiResponseObject

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {}
  }
}
```

<a id="schema-apiresponsepageresponseaccountresponse"></a>

## ApiResponsePageResponseAccountResponse

참조 DTO: [PageResponseAccountResponse](./api-schema-catalog.md#schema-pageresponseaccountresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseAccountResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponseeventattendancesummaryresponse"></a>

## ApiResponsePageResponseEventAttendanceSummaryResponse

참조 DTO: [PageResponseEventAttendanceSummaryResponse](./api-schema-catalog.md#schema-pageresponseeventattendancesummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseEventAttendanceSummaryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponseeventroulettesummaryresponse"></a>

## ApiResponsePageResponseEventRouletteSummaryResponse

참조 DTO: [PageResponseEventRouletteSummaryResponse](./api-schema-catalog.md#schema-pageresponseeventroulettesummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseEventRouletteSummaryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponsegetadminallauditlogresponse"></a>

## ApiResponsePageResponseGetAdminAllAuditLogResponse

참조 DTO: [PageResponseGetAdminAllAuditLogResponse](./api-schema-catalog.md#schema-pageresponsegetadminallauditlogresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseGetAdminAllAuditLogResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponsegetinquirytyperesponse"></a>

## ApiResponsePageResponseGetInquiryTypeResponse

참조 DTO: [PageResponseGetInquiryTypeResponse](./api-schema-catalog.md#schema-pageresponsegetinquirytyperesponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseGetInquiryTypeResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponsegetitemsummaryresponse"></a>

## ApiResponsePageResponseGetItemSummaryResponse

참조 DTO: [PageResponseGetItemSummaryResponse](./api-schema-catalog.md#schema-pageresponsegetitemsummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseGetItemSummaryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponsegetplaylistsummaryresponse"></a>

## ApiResponsePageResponseGetPlaylistSummaryResponse

참조 DTO: [PageResponseGetPlaylistSummaryResponse](./api-schema-catalog.md#schema-pageresponsegetplaylistsummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseGetPlaylistSummaryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponsegetvideolistresponse"></a>

## ApiResponsePageResponseGetVideoListResponse

참조 DTO: [PageResponseGetVideoListResponse](./api-schema-catalog.md#schema-pageresponsegetvideolistresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseGetVideoListResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponseinquirysummaryresponse"></a>

## ApiResponsePageResponseInquirySummaryResponse

참조 DTO: [PageResponseInquirySummaryResponse](./api-schema-catalog.md#schema-pageresponseinquirysummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseInquirySummaryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponseitemhistoryresponse"></a>

## ApiResponsePageResponseItemHistoryResponse

참조 DTO: [PageResponseItemHistoryResponse](./api-schema-catalog.md#schema-pageresponseitemhistoryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseItemHistoryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponseparcelhistoryresponse"></a>

## ApiResponsePageResponseParcelHistoryResponse

참조 DTO: [PageResponseParcelHistoryResponse](./api-schema-catalog.md#schema-pageresponseparcelhistoryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseParcelHistoryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponsepointhistoryresponse"></a>

## ApiResponsePageResponsePointHistoryResponse

참조 DTO: [PageResponsePointHistoryResponse](./api-schema-catalog.md#schema-pageresponsepointhistoryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponsePointHistoryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponseproposalsummaryresponse"></a>

## ApiResponsePageResponseProposalSummaryResponse

참조 DTO: [PageResponseCitizenProposalSummaryResponse](./api-schema-catalog.md#schema-pageresponsecitizenproposalsummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseCitizenProposalSummaryResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponseuserwithdrawlogresponse"></a>

## ApiResponsePageResponseUserWithdrawLogResponse

참조 DTO: [PageResponseUserWithdrawLogResponse](./api-schema-catalog.md#schema-pageresponseuserwithdrawlogresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseUserWithdrawLogResponse"
    }
  }
}
```

<a id="schema-apiresponsepageresponsevotesummaryresponse"></a>

## ApiResponsePageResponseVoteSummaryResponse

참조 DTO: [PageResponseCitizenVoteSummaryResponse](./api-schema-catalog.md#schema-pageresponsecitizenvotesummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseCitizenVoteSummaryResponse"
    }
  }
}
```

<a id="schema-apiresponseproposalresponse"></a>

## ApiResponseProposalResponse

참조 DTO: [CitizenProposalResponse](./api-schema-catalog.md#schema-citizenproposalresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/CitizenProposalResponse"
    }
  }
}
```

<a id="schema-apiresponseproposalstatuscountresponse"></a>

## ApiResponseProposalStatusCountResponse

참조 DTO: [CitizenProposalStatusCountResponse](./api-schema-catalog.md#schema-citizenproposalstatuscountresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/CitizenProposalStatusCountResponse"
    }
  }
}
```

<a id="schema-apiresponseroledetailresponse"></a>

## ApiResponseRoleDetailResponse

참조 DTO: [RoleDetailResponse](./api-schema-catalog.md#schema-roledetailresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/RoleDetailResponse"
    }
  }
}
```

<a id="schema-apiresponseupdateitemresponse"></a>

## ApiResponseUpdateItemResponse

참조 DTO: [UpdateItemResponse](./api-schema-catalog.md#schema-updateitemresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/UpdateItemResponse"
    }
  }
}
```

<a id="schema-apiresponseuploadeventattendanceconfigimageresponse"></a>

## ApiResponseUploadEventAttendanceConfigImageResponse

참조 DTO: [UploadEventAttendanceConfigImageResponse](./api-schema-catalog.md#schema-uploadeventattendanceconfigimageresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/UploadEventAttendanceConfigImageResponse"
    }
  }
}
```

<a id="schema-apiresponseuploadeventrouletteconfigimageresponse"></a>

## ApiResponseUploadEventRouletteConfigImageResponse

참조 DTO: [UploadEventRouletteConfigImageResponse](./api-schema-catalog.md#schema-uploadeventrouletteconfigimageresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/UploadEventRouletteConfigImageResponse"
    }
  }
}
```

<a id="schema-apiresponseuploaditemimageresponse"></a>

## ApiResponseUploadItemImageResponse

참조 DTO: [UploadItemImageResponse](./api-schema-catalog.md#schema-uploaditemimageresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/UploadItemImageResponse"
    }
  }
}
```

<a id="schema-apiresponsevoid"></a>

## ApiResponseVoid

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {}
  }
}
```

<a id="schema-apiresponsevotedetailresponse"></a>

## ApiResponseVoteDetailResponse

참조 DTO: [CitizenVoteDetailResponse](./api-schema-catalog.md#schema-citizenvotedetailresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/CitizenVoteDetailResponse"
    }
  }
}
```

<a id="schema-apiresponsevotestatuscountresponse"></a>

## ApiResponseVoteStatusCountResponse

참조 DTO: [CitizenVoteStatusCountResponse](./api-schema-catalog.md#schema-citizenvotestatuscountresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/CitizenVoteStatusCountResponse"
    }
  }
}
```

<a id="schema-apiresponseweeklydashboardresponse"></a>

## ApiResponseWeeklyDashboardResponse

참조 DTO: [WeeklyDashboardResponse](./api-schema-catalog.md#schema-weeklydashboardresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/WeeklyDashboardResponse"
    }
  }
}
```

<a id="schema-attendanceconfigitem"></a>

## AttendanceConfigItem

필수 필드: `configKey`, `configValue`.

```json
{
  "type": "object",
  "properties": {
    "configKey": {
      "type": "string",
      "enum": [
        "DAILY_BACKGROUND",
        "DAILY_CHECK_BUTTON",
        "DAILY_FAILED_ICON",
        "DAILY_HOLD_ICON",
        "DAILY_SUCCESS_ICON",
        "DAILY_TODAY_ICON",
        "ACC_CURRENCY_BACKGROUND",
        "ACC_HOLD_ICON",
        "DAILY_RECOVERY_CURRENCY_TYPE",
        "DAILY_RECOVERY_CURRENCY_AMOUNT",
        "DAILY_TOP_TITLE"
      ]
    },
    "configValue": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": [
    "configKey",
    "configValue"
  ]
}
```

<a id="schema-batchupdatenewslistrequest"></a>

## BatchUpdateNewsListRequest

필수 필드: `newsIds`.

```json
{
  "type": "object",
  "properties": {
    "newsIds": {
      "type": "array",
      "items": {
        "type": "integer",
        "format": "int64"
      },
      "minItems": 1
    },
    "status": {
      "type": "string",
      "enum": [
        "DRAFT",
        "PUBLISHED",
        "ARCHIVED"
      ]
    },
    "isPinned": {
      "type": "boolean"
    }
  },
  "required": [
    "newsIds"
  ]
}
```

<a id="schema-citizenproposalresponse"></a>

## CitizenProposalResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "author": {
      "type": "string"
    },
    "title": {
      "type": "string"
    },
    "background": {
      "type": "string"
    },
    "content": {
      "type": "string"
    },
    "expectedEffect": {
      "type": "string"
    },
    "referenceCase": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": [
        "RECEIVED",
        "UNDER_REVIEW",
        "ADOPTED",
        "REJECTED"
      ]
    },
    "reviewResult": {
      "type": "string"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "updatedAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-citizenproposalstatuscountresponse"></a>

## CitizenProposalStatusCountResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "received": {
      "type": "integer",
      "format": "int32"
    },
    "underReview": {
      "type": "integer",
      "format": "int32"
    },
    "adopted": {
      "type": "integer",
      "format": "int32"
    },
    "rejected": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-citizenproposalsummaryresponse"></a>

## CitizenProposalSummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "title": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": [
        "RECEIVED",
        "UNDER_REVIEW",
        "ADOPTED",
        "REJECTED"
      ]
    },
    "author": {
      "type": "string"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-citizenvotedetailresponse"></a>

## CitizenVoteDetailResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "status": {
      "type": "string",
      "enum": [
        "DRAFT",
        "UPCOMING",
        "IN_PROGRESS",
        "CLOSED",
        "CANCELLED"
      ]
    },
    "title": {
      "type": "string"
    },
    "agenda": {
      "type": "string"
    },
    "startsAt": {
      "type": "string",
      "format": "date-time"
    },
    "endsAt": {
      "type": "string",
      "format": "date-time"
    },
    "totalCount": {
      "type": "integer",
      "format": "int32"
    },
    "agreeCount": {
      "type": "integer",
      "format": "int32"
    },
    "disagreeCount": {
      "type": "integer",
      "format": "int32"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "updatedAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-citizenvotestatuscountresponse"></a>

## CitizenVoteStatusCountResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "inProgress": {
      "type": "integer",
      "format": "int64"
    },
    "closed": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-citizenvotesummaryresponse"></a>

## CitizenVoteSummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "status": {
      "type": "string",
      "enum": [
        "DRAFT",
        "UPCOMING",
        "IN_PROGRESS",
        "CLOSED",
        "CANCELLED"
      ]
    },
    "title": {
      "type": "string"
    },
    "startsAt": {
      "type": "string",
      "format": "date-time"
    },
    "endsAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-createeventattendancerequest"></a>

## CreateEventAttendanceRequest

참조 DTO: [EventAttendanceItemDto](./api-schema-catalog.md#schema-eventattendanceitemdto).

필수 필드: `code`, `endAt`, `id`, `items`, `startAt`.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string",
      "minLength": 1
    },
    "startAt": {
      "type": "string",
      "format": "date-time"
    },
    "endAt": {
      "type": "string",
      "format": "date-time"
    },
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventAttendanceItemDto"
      },
      "minItems": 1
    }
  },
  "required": [
    "code",
    "endAt",
    "id",
    "items",
    "startAt"
  ]
}
```

<a id="schema-createeventrouletterequest"></a>

## CreateEventRouletteRequest

참조 DTO: [EventRouletteItemDto](./api-schema-catalog.md#schema-eventrouletteitemdto).

필수 필드: `code`, `endAt`, `id`, `items`, `startAt`.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string",
      "minLength": 1
    },
    "startAt": {
      "type": "string",
      "format": "date-time"
    },
    "endAt": {
      "type": "string",
      "format": "date-time"
    },
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventRouletteItemDto"
      },
      "minItems": 1
    }
  },
  "required": [
    "code",
    "endAt",
    "id",
    "items",
    "startAt"
  ]
}
```

<a id="schema-createinquirytyperequest"></a>

## CreateInquiryTypeRequest

필수 필드: `code`, `name`.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string",
      "minLength": 1
    },
    "name": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": [
    "code",
    "name"
  ]
}
```

<a id="schema-createitemcategoryrequest"></a>

## CreateItemCategoryRequest

필수 필드: `name`.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    },
    "parentCatrgoryName": {
      "type": "string"
    }
  },
  "required": [
    "name"
  ]
}
```

<a id="schema-createitemrequest"></a>

## CreateItemRequest

필수 필드: `description`, `excludeFromEventReward`, `gender`, `id`, `mainCategoryId`, `name`, `newBadgeUntil`, `paymentType`, `saleAmount`, `scopeMetaverse`, `status`, `subCategoryId`.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string",
      "minLength": 1
    },
    "mainCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "subCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "gender": {
      "type": "string",
      "enum": [
        "COMMON",
        "MAN",
        "WOMAN"
      ]
    },
    "paymentType": {
      "type": "string",
      "enum": [
        "POINT"
      ]
    },
    "saleAmount": {
      "type": "integer",
      "format": "int32"
    },
    "scopeMetaverse": {
      "type": "boolean"
    },
    "imageUuid": {
      "type": "string",
      "format": "uuid"
    },
    "status": {
      "type": "string",
      "enum": [
        "PENDING",
        "ON_SALE",
        "ON_HOLD",
        "END_SALE"
      ]
    },
    "newBadgeUntil": {
      "type": "string",
      "format": "date-time"
    },
    "excludeFromEventReward": {
      "type": "boolean"
    }
  },
  "required": [
    "description",
    "excludeFromEventReward",
    "gender",
    "id",
    "mainCategoryId",
    "name",
    "newBadgeUntil",
    "paymentType",
    "saleAmount",
    "scopeMetaverse",
    "status",
    "subCategoryId"
  ]
}
```

<a id="schema-createitemresponse"></a>

## CreateItemResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-createnewsrequest"></a>

## CreateNewsRequest

필수 필드: `content`, `isPinned`, `status`, `title`, `type`.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "minLength": 1
    },
    "content": {
      "type": "string",
      "minLength": 1
    },
    "type": {
      "type": "string",
      "enum": [
        "ANNOUNCEMENT",
        "UPDATE",
        "EVENT",
        "ETC"
      ]
    },
    "status": {
      "type": "string",
      "enum": [
        "DRAFT",
        "PUBLISHED",
        "ARCHIVED"
      ]
    },
    "isPinned": {
      "type": "boolean"
    }
  },
  "required": [
    "content",
    "isPinned",
    "status",
    "title",
    "type"
  ]
}
```

<a id="schema-createplaylistrequest"></a>

## CreatePlaylistRequest

필수 필드: `name`.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    },
    "videoIds": {
      "type": "array",
      "items": {
        "type": "integer",
        "format": "int64"
      }
    }
  },
  "required": [
    "name"
  ]
}
```

<a id="schema-createrolerequest"></a>

## CreateRoleRequest

필수 필드: `code`, `name`, `permissionCodes`.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string",
      "maxLength": 50,
      "minLength": 0,
      "pattern": "^[A-Z][A-Z0-9_]*$"
    },
    "name": {
      "type": "string",
      "maxLength": 50,
      "minLength": 0
    },
    "permissionCodes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "code",
    "name",
    "permissionCodes"
  ]
}
```

<a id="schema-createroleresponse"></a>

## CreateRoleResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-createvideorequest"></a>

## CreateVideoRequest

필수 필드: `name`.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    }
  },
  "required": [
    "name"
  ]
}
```

<a id="schema-dailydashboardresponse"></a>

## DailyDashboardResponse

참조 DTO: [ExternalOsStatsResponse](./api-schema-catalog.md#schema-externalosstatsresponse), [PeriodInquiryStatsResponse](./api-schema-catalog.md#schema-periodinquirystatsresponse), [PeriodItemStatsResponse](./api-schema-catalog.md#schema-perioditemstatsresponse), [PeriodUserStatsResponse](./api-schema-catalog.md#schema-perioduserstatsresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "statDate": {
      "type": "string",
      "format": "date"
    },
    "user": {
      "$ref": "#/components/schemas/PeriodUserStatsResponse"
    },
    "os": {
      "$ref": "#/components/schemas/ExternalOsStatsResponse"
    },
    "inquiry": {
      "$ref": "#/components/schemas/PeriodInquiryStatsResponse"
    },
    "item": {
      "$ref": "#/components/schemas/PeriodItemStatsResponse"
    }
  }
}
```

<a id="schema-eventattendanceconfigresponse"></a>

## EventAttendanceConfigResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "configKey": {
      "type": "string"
    },
    "configValue": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": [
        "IMAGE",
        "TEXT"
      ]
    }
  }
}
```

<a id="schema-eventattendanceitemdto"></a>

## EventAttendanceItemDto

필수 필드: `day`, `objectId`, `type`.

```json
{
  "type": "object",
  "properties": {
    "day": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    },
    "type": {
      "type": "string",
      "enum": [
        "DAILY",
        "ACC"
      ]
    },
    "objectId": {
      "type": "integer",
      "format": "int64",
      "minimum": 1
    },
    "objectAmount": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    },
    "sortOrder": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    }
  },
  "required": [
    "day",
    "objectId",
    "type"
  ]
}
```

<a id="schema-eventattendanceitemresponse"></a>

## EventAttendanceItemResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "day": {
      "type": "integer",
      "format": "int32"
    },
    "type": {
      "type": "string",
      "enum": [
        "DAILY",
        "ACC"
      ]
    },
    "objectId": {
      "type": "integer",
      "format": "int64"
    },
    "objectName": {
      "type": "string"
    },
    "objectAmount": {
      "type": "integer",
      "format": "int32"
    },
    "sortOrder": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-eventattendanceresponse"></a>

## EventAttendanceResponse

참조 DTO: [EventAttendanceConfigResponse](./api-schema-catalog.md#schema-eventattendanceconfigresponse), [EventAttendanceItemResponse](./api-schema-catalog.md#schema-eventattendanceitemresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string"
    },
    "startAt": {
      "type": "string",
      "format": "date-time"
    },
    "endAt": {
      "type": "string",
      "format": "date-time"
    },
    "isActive": {
      "type": "boolean"
    },
    "configs": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventAttendanceConfigResponse"
      }
    },
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventAttendanceItemResponse"
      }
    }
  }
}
```

<a id="schema-eventattendancesummaryresponse"></a>

## EventAttendanceSummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string"
    },
    "startAt": {
      "type": "string",
      "format": "date-time"
    },
    "endAt": {
      "type": "string",
      "format": "date-time"
    },
    "isActive": {
      "type": "boolean"
    }
  }
}
```

<a id="schema-eventrouletteconfigresponse"></a>

## EventRouletteConfigResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "configKey": {
      "type": "string"
    },
    "configValue": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": [
        "IMAGE",
        "TEXT"
      ]
    }
  }
}
```

<a id="schema-eventrouletteitemdto"></a>

## EventRouletteItemDto

필수 필드: `chance`, `objectAmount`, `objectId`.

```json
{
  "type": "object",
  "properties": {
    "objectId": {
      "type": "integer",
      "format": "int64",
      "minimum": 1
    },
    "objectAmount": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    },
    "objectImageUrl": {
      "type": "string"
    },
    "chance": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    },
    "sortOrder": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    }
  },
  "required": [
    "chance",
    "objectAmount",
    "objectId"
  ]
}
```

<a id="schema-eventrouletteitemresponse"></a>

## EventRouletteItemResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "objectId": {
      "type": "integer",
      "format": "int64"
    },
    "objectName": {
      "type": "string"
    },
    "objectAmount": {
      "type": "integer",
      "format": "int32"
    },
    "objectImageUrl": {
      "type": "string"
    },
    "chance": {
      "type": "integer",
      "format": "int32"
    },
    "sortOrder": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-eventrouletteresponse"></a>

## EventRouletteResponse

참조 DTO: [EventRouletteConfigResponse](./api-schema-catalog.md#schema-eventrouletteconfigresponse), [EventRouletteItemResponse](./api-schema-catalog.md#schema-eventrouletteitemresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string"
    },
    "startAt": {
      "type": "string",
      "format": "date-time"
    },
    "endAt": {
      "type": "string",
      "format": "date-time"
    },
    "isActive": {
      "type": "boolean"
    },
    "configs": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventRouletteConfigResponse"
      }
    },
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventRouletteItemResponse"
      }
    }
  }
}
```

<a id="schema-eventroulettesummaryresponse"></a>

## EventRouletteSummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string"
    },
    "startAt": {
      "type": "string",
      "format": "date-time"
    },
    "endAt": {
      "type": "string",
      "format": "date-time"
    },
    "isActive": {
      "type": "boolean"
    }
  }
}
```

<a id="schema-externaldashboardresponse"></a>

## ExternalDashboardResponse

참조 DTO: [ExternalInquiryStatsResponse](./api-schema-catalog.md#schema-externalinquirystatsresponse), [ExternalItemStatsResponse](./api-schema-catalog.md#schema-externalitemstatsresponse), [ExternalOsStatsResponse](./api-schema-catalog.md#schema-externalosstatsresponse), [ExternalUserStatsResponse](./api-schema-catalog.md#schema-externaluserstatsresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "user": {
      "$ref": "#/components/schemas/ExternalUserStatsResponse"
    },
    "os": {
      "$ref": "#/components/schemas/ExternalOsStatsResponse"
    },
    "inquiry": {
      "$ref": "#/components/schemas/ExternalInquiryStatsResponse"
    },
    "item": {
      "$ref": "#/components/schemas/ExternalItemStatsResponse"
    }
  }
}
```

<a id="schema-externalinquirystatsresponse"></a>

## ExternalInquiryStatsResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "totalCount": {
      "type": "integer",
      "format": "int64"
    },
    "ongoingCount": {
      "type": "integer",
      "format": "int64"
    },
    "todayCount": {
      "type": "integer",
      "format": "int64"
    },
    "todayOngoingCount": {
      "type": "integer",
      "format": "int64"
    },
    "todayResolvedCount": {
      "type": "integer",
      "format": "int64"
    },
    "changeRate": {
      "type": "number",
      "format": "double"
    }
  }
}
```

<a id="schema-externalitemstatsresponse"></a>

## ExternalItemStatsResponse

참조 DTO: [ItemSalesRankResponse](./api-schema-catalog.md#schema-itemsalesrankresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "salesTodayCount": {
      "type": "integer",
      "format": "int64"
    },
    "salesRanks": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/ItemSalesRankResponse"
      }
    },
    "changeRate": {
      "type": "number",
      "format": "double"
    }
  }
}
```

<a id="schema-externalosstatsresponse"></a>

## ExternalOsStatsResponse

참조 DTO: [OsCountResponse](./api-schema-catalog.md#schema-oscountresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "osCounts": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/OsCountResponse"
      }
    }
  }
}
```

<a id="schema-externaluserstatsresponse"></a>

## ExternalUserStatsResponse

참조 DTO: [UserStatusCountResponse](./api-schema-catalog.md#schema-userstatuscountresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "totalCount": {
      "type": "integer",
      "format": "int64"
    },
    "statusCounts": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/UserStatusCountResponse"
      }
    },
    "newTodayCount": {
      "type": "integer",
      "format": "int64"
    },
    "loginTodayCount": {
      "type": "integer",
      "format": "int64"
    },
    "onlineCount": {
      "type": "integer",
      "format": "int64"
    },
    "changeRate": {
      "type": "number",
      "format": "double"
    }
  }
}
```

<a id="schema-getaccountlistrequest"></a>

## GetAccountListRequest

필수 필드: `page`, `size`.

```json
{
  "type": "object",
  "properties": {
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    },
    "keyword": {
      "type": "string"
    }
  },
  "required": [
    "page",
    "size"
  ]
}
```

<a id="schema-getadminallauditlogresponse"></a>

## GetAdminAllAuditLogResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "adminName": {
      "type": "string"
    },
    "service": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-geteventattendancelistrequest"></a>

## GetEventAttendanceListRequest

필수 필드: `page`, `size`.

```json
{
  "type": "object",
  "properties": {
    "page": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    },
    "size": {
      "type": "integer",
      "format": "int32",
      "maximum": 100,
      "minimum": 1
    }
  },
  "required": [
    "page",
    "size"
  ]
}
```

<a id="schema-geteventroulettelistrequest"></a>

## GetEventRouletteListRequest

필수 필드: `page`, `size`.

```json
{
  "type": "object",
  "properties": {
    "page": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    },
    "size": {
      "type": "integer",
      "format": "int32",
      "maximum": 100,
      "minimum": 1
    }
  },
  "required": [
    "page",
    "size"
  ]
}
```

<a id="schema-getinquirytyperesponse"></a>

## GetInquiryTypeResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string"
    },
    "name": {
      "type": "string"
    }
  }
}
```

<a id="schema-getitemcategoryresponse"></a>

## GetItemCategoryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    },
    "parentName": {
      "type": "string"
    }
  }
}
```

<a id="schema-getitemdetailresponse"></a>

## GetItemDetailResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "mainCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "subCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "gender": {
      "type": "string",
      "enum": [
        "COMMON",
        "MAN",
        "WOMAN"
      ]
    },
    "saleAmount": {
      "type": "integer",
      "format": "int32"
    },
    "paymentType": {
      "type": "string",
      "enum": [
        "POINT"
      ]
    },
    "newBadgeUntil": {
      "type": "string",
      "format": "date-time"
    },
    "isShowApp": {
      "type": "boolean"
    },
    "excludeFromEventReward": {
      "type": "boolean"
    },
    "status": {
      "type": "string",
      "enum": [
        "PENDING",
        "ON_SALE",
        "ON_HOLD",
        "END_SALE"
      ]
    },
    "image": {
      "type": "string"
    }
  }
}
```

<a id="schema-getitemhistorylistrequest"></a>

## GetItemHistoryListRequest

필수 필드: `endDate`, `startDate`.

```json
{
  "type": "object",
  "properties": {
    "startDate": {
      "type": "string",
      "format": "date"
    },
    "endDate": {
      "type": "string",
      "format": "date"
    },
    "by": {
      "type": "string",
      "enum": [
        "USER_ID",
        "USER_NAME",
        "ITEM_NAME"
      ]
    },
    "keyword": {
      "type": "string"
    }
  },
  "required": [
    "endDate",
    "startDate"
  ]
}
```

<a id="schema-getitemlatestidrequest"></a>

## GetItemLatestIdRequest

필수 필드: `gender`, `subCategoryId`.

```json
{
  "type": "object",
  "properties": {
    "subCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "gender": {
      "type": "string",
      "enum": [
        "COMMON",
        "MAN",
        "WOMAN"
      ]
    }
  },
  "required": [
    "gender",
    "subCategoryId"
  ]
}
```

<a id="schema-getitemsrequest"></a>

## GetItemsRequest

필수 필드: `page`, `size`.

```json
{
  "type": "object",
  "properties": {
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    },
    "mainCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "subCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "gender": {
      "type": "string",
      "enum": [
        "COMMON",
        "MAN",
        "WOMAN"
      ]
    },
    "status": {
      "type": "string",
      "enum": [
        "PENDING",
        "ON_SALE",
        "ON_HOLD",
        "END_SALE"
      ]
    },
    "keyword": {
      "type": "string"
    }
  },
  "required": [
    "page",
    "size"
  ]
}
```

<a id="schema-getitemsummaryresponse"></a>

## GetItemSummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "gender": {
      "type": "string",
      "enum": [
        "COMMON",
        "MAN",
        "WOMAN"
      ]
    },
    "paymentType": {
      "type": "string",
      "enum": [
        "POINT"
      ]
    },
    "saleAmount": {
      "type": "integer",
      "format": "int32"
    },
    "saleEnv": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": [
        "PENDING",
        "ON_SALE",
        "ON_HOLD",
        "END_SALE"
      ]
    },
    "categoryName": {
      "type": "string"
    },
    "newBadgeUntil": {
      "type": "string",
      "format": "date-time"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "excludeFromEventReward": {
      "type": "boolean"
    }
  }
}
```

<a id="schema-getmaintenanceitemrequest"></a>

## GetMaintenanceItemRequest

필수 필드: `key`.

```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": [
    "key"
  ]
}
```

<a id="schema-getplaylistresponse"></a>

## GetPlaylistResponse

참조 DTO: [PlaylistVideoResponse](./api-schema-catalog.md#schema-playlistvideoresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "isDelete": {
      "type": "boolean"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "videos": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/PlaylistVideoResponse"
      }
    }
  }
}
```

<a id="schema-getplaylistsummaryresponse"></a>

## GetPlaylistSummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "isDelete": {
      "type": "boolean"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-getpointhistorylistrequest"></a>

## GetPointHistoryListRequest

필수 필드: `endDate`, `startDate`.

```json
{
  "type": "object",
  "properties": {
    "startDate": {
      "type": "string",
      "format": "date"
    },
    "endDate": {
      "type": "string",
      "format": "date"
    },
    "by": {
      "type": "string",
      "enum": [
        "USER_ID",
        "USER_NAME"
      ]
    },
    "keyword": {
      "type": "string"
    }
  },
  "required": [
    "endDate",
    "startDate"
  ]
}
```

<a id="schema-getvideolistresponse"></a>

## GetVideoListResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "uuid": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "thumbnailUrl": {
      "type": "string"
    },
    "likeCount": {
      "type": "integer",
      "format": "int32"
    },
    "viewCount": {
      "type": "integer",
      "format": "int32"
    },
    "isDelete": {
      "type": "boolean"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-grantuserauthorityrequest"></a>

## GrantUserAuthorityRequest

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "citizenCard": {
      "type": "boolean"
    },
    "roles": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

<a id="schema-inquiryanswerrequest"></a>

## InquiryAnswerRequest

필수 필드: `content`.

```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": [
    "content"
  ]
}
```

<a id="schema-inquirycommentresponse"></a>

## InquiryCommentResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "comment": {
      "type": "string"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-inquirydetailresponse"></a>

## InquiryDetailResponse

참조 DTO: [InquiryCommentResponse](./api-schema-catalog.md#schema-inquirycommentresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "title": {
      "type": "string"
    },
    "content": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": [
        "OPEN",
        "IN_PROGRESS",
        "COMPLETED"
      ]
    },
    "typeName": {
      "type": "string"
    },
    "authorName": {
      "type": "string"
    },
    "answerContent": {
      "$ref": "#/components/schemas/InquiryCommentResponse"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-inquirysummaryresponse"></a>

## InquirySummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "title": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": [
        "OPEN",
        "IN_PROGRESS",
        "COMPLETED"
      ]
    },
    "typeName": {
      "type": "string"
    },
    "authorName": {
      "type": "string"
    },
    "answered": {
      "type": "boolean"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-item"></a>

## Item

필수 필드: `id`, `sortOrder`.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "sortOrder": {
      "type": "integer",
      "format": "int32"
    }
  },
  "required": [
    "id",
    "sortOrder"
  ]
}
```

<a id="schema-itemhistoryresponse"></a>

## ItemHistoryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "itemId": {
      "type": "integer",
      "format": "int64"
    },
    "objectName": {
      "type": "string"
    },
    "amount": {
      "type": "integer",
      "format": "int32"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "userId": {
      "type": "integer",
      "format": "int64"
    },
    "userNickname": {
      "type": "string"
    }
  }
}
```

<a id="schema-itemsalesrankresponse"></a>

## ItemSalesRankResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "rank": {
      "type": "integer",
      "format": "int32"
    },
    "itemName": {
      "type": "string"
    },
    "salesCount": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-loginrequest"></a>

## LoginRequest

필수 필드: `loginId`, `password`.

```json
{
  "type": "object",
  "properties": {
    "loginId": {
      "type": "string",
      "minLength": 1
    },
    "password": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": [
    "loginId",
    "password"
  ]
}
```

<a id="schema-maintenanceconfigitem"></a>

## MaintenanceConfigItem

필수 필드: `key`.

```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string",
      "enum": [
        "APP_VERSION",
        "ASSET_DOWNLOAD_URL",
        "MAINTENANCE",
        "MAINTENANCE_START_TIME",
        "MAINTENANCE_END_TIME",
        "ASSET_VERSION",
        "WORLD_THEME",
        "MAINTENANCE_SCHEDULE_ENABLED"
      ]
    },
    "value": {
      "type": "string",
      "maxLength": 255,
      "minLength": 0
    }
  },
  "required": [
    "key"
  ]
}
```

<a id="schema-maintenanceresponse"></a>

## MaintenanceResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "key": {
      "type": "string"
    },
    "value": {
      "type": "string"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "updatedAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-managedmenuresponse"></a>

## ManagedMenuResponse

참조 DTO: [ManagedMenuResponse](./api-schema-catalog.md#schema-managedmenuresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "key": {
      "type": "string"
    },
    "label": {
      "type": "string"
    },
    "order": {
      "type": "integer",
      "format": "int32"
    },
    "visible": {
      "type": "boolean"
    },
    "requiredPermission": {
      "type": "string"
    },
    "children": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/ManagedMenuResponse"
      }
    }
  }
}
```

<a id="schema-menugroupresponse"></a>

## MenuGroupResponse

참조 DTO: [MenuItemResponse](./api-schema-catalog.md#schema-menuitemresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string"
    },
    "label": {
      "type": "string"
    },
    "order": {
      "type": "integer",
      "format": "int32"
    },
    "children": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/MenuItemResponse"
      }
    }
  }
}
```

<a id="schema-menuitemresponse"></a>

## MenuItemResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string"
    },
    "label": {
      "type": "string"
    },
    "order": {
      "type": "integer",
      "format": "int32"
    },
    "requiredPermission": {
      "type": "string"
    }
  }
}
```

<a id="schema-meresponse"></a>

## MeResponse

참조 DTO: [RoleSummary](./api-schema-catalog.md#schema-rolesummary).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "loginId": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "department": {
      "type": "string"
    },
    "roles": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/RoleSummary"
      }
    },
    "permissions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

<a id="schema-monthlydashboardresponse"></a>

## MonthlyDashboardResponse

참조 DTO: [ExternalOsStatsResponse](./api-schema-catalog.md#schema-externalosstatsresponse), [PeriodInquiryStatsResponse](./api-schema-catalog.md#schema-periodinquirystatsresponse), [PeriodItemStatsResponse](./api-schema-catalog.md#schema-perioditemstatsresponse), [PeriodUserStatsResponse](./api-schema-catalog.md#schema-perioduserstatsresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "month": {
      "type": "string"
    },
    "startDate": {
      "type": "string",
      "format": "date"
    },
    "endDate": {
      "type": "string",
      "format": "date"
    },
    "user": {
      "$ref": "#/components/schemas/PeriodUserStatsResponse"
    },
    "os": {
      "$ref": "#/components/schemas/ExternalOsStatsResponse"
    },
    "inquiry": {
      "$ref": "#/components/schemas/PeriodInquiryStatsResponse"
    },
    "item": {
      "$ref": "#/components/schemas/PeriodItemStatsResponse"
    }
  }
}
```

<a id="schema-newsapiresponsecommentlist"></a>

## NewsApiResponseCommentList

참조 DTO: [PageResponseNewsCommentResponse](./api-schema-catalog.md#schema-pageresponsenewscommentresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/PageResponseNewsCommentResponse"
    }
  }
}
```

<a id="schema-newsapiresponsedetail"></a>

## NewsApiResponseDetail

참조 DTO: [NewsDetailResponse](./api-schema-catalog.md#schema-newsdetailresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/NewsDetailResponse"
    }
  }
}
```

<a id="schema-newsapiresponselist"></a>

## NewsApiResponseList

참조 DTO: [NewsListResponse](./api-schema-catalog.md#schema-newslistresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "$ref": "#/components/schemas/NewsListResponse"
    }
  }
}
```

<a id="schema-newsapiresponsevoid"></a>

## NewsApiResponseVoid

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "data": {
      "writeOnly": true
    }
  }
}
```

<a id="schema-newscommentresponse"></a>

## NewsCommentResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "content": {
      "type": "string"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "updatedAt": {
      "type": "string",
      "format": "date-time"
    },
    "deletedAt": {
      "type": "string",
      "format": "date-time"
    },
    "deletedBy": {
      "type": "string",
      "enum": [
        "USER",
        "ADMIN"
      ]
    },
    "userId": {
      "type": "integer",
      "format": "int64"
    },
    "userNickname": {
      "type": "string"
    }
  }
}
```

<a id="schema-newsdetailresponse"></a>

## NewsDetailResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "type": {
      "type": "string",
      "enum": [
        "ANNOUNCEMENT",
        "UPDATE",
        "EVENT",
        "ETC"
      ]
    },
    "status": {
      "type": "string",
      "enum": [
        "DRAFT",
        "PUBLISHED",
        "ARCHIVED"
      ]
    },
    "title": {
      "type": "string"
    },
    "content": {
      "type": "string"
    },
    "isPinned": {
      "type": "boolean"
    },
    "viewCount": {
      "type": "integer",
      "format": "int32"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "updatedAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-newslistresponse"></a>

## NewsListResponse

참조 DTO: [NewsSummaryResponse](./api-schema-catalog.md#schema-newssummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/NewsSummaryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    },
    "isPinnedCount": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-newssummaryresponse"></a>

## NewsSummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "type": {
      "type": "string",
      "enum": [
        "ANNOUNCEMENT",
        "UPDATE",
        "EVENT",
        "ETC"
      ]
    },
    "title": {
      "type": "string"
    },
    "viewCount": {
      "type": "integer",
      "format": "int32"
    },
    "status": {
      "type": "string",
      "enum": [
        "DRAFT",
        "PUBLISHED",
        "ARCHIVED"
      ]
    },
    "isPinned": {
      "type": "boolean"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "deletedAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-oscountresponse"></a>

## OsCountResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "os": {
      "type": "string",
      "enum": [
        "ANDROID",
        "IOS"
      ]
    },
    "count": {
      "type": "integer",
      "format": "int64"
    },
    "rate": {
      "type": "number",
      "format": "double"
    }
  }
}
```

<a id="schema-pageable"></a>

## Pageable

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "page": {
      "type": "integer",
      "format": "int32",
      "minimum": 0
    },
    "size": {
      "type": "integer",
      "format": "int32",
      "minimum": 1
    },
    "sort": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

<a id="schema-pageresponseaccountresponse"></a>

## PageResponseAccountResponse

참조 DTO: [AccountResponse](./api-schema-catalog.md#schema-accountresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/AccountResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsecitizenproposalsummaryresponse"></a>

## PageResponseCitizenProposalSummaryResponse

참조 DTO: [CitizenProposalSummaryResponse](./api-schema-catalog.md#schema-citizenproposalsummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/CitizenProposalSummaryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsecitizenvotesummaryresponse"></a>

## PageResponseCitizenVoteSummaryResponse

참조 DTO: [CitizenVoteSummaryResponse](./api-schema-catalog.md#schema-citizenvotesummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/CitizenVoteSummaryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponseeventattendancesummaryresponse"></a>

## PageResponseEventAttendanceSummaryResponse

참조 DTO: [EventAttendanceSummaryResponse](./api-schema-catalog.md#schema-eventattendancesummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventAttendanceSummaryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponseeventroulettesummaryresponse"></a>

## PageResponseEventRouletteSummaryResponse

참조 DTO: [EventRouletteSummaryResponse](./api-schema-catalog.md#schema-eventroulettesummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventRouletteSummaryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsegetadminallauditlogresponse"></a>

## PageResponseGetAdminAllAuditLogResponse

참조 DTO: [GetAdminAllAuditLogResponse](./api-schema-catalog.md#schema-getadminallauditlogresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/GetAdminAllAuditLogResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsegetinquirytyperesponse"></a>

## PageResponseGetInquiryTypeResponse

참조 DTO: [GetInquiryTypeResponse](./api-schema-catalog.md#schema-getinquirytyperesponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/GetInquiryTypeResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsegetitemsummaryresponse"></a>

## PageResponseGetItemSummaryResponse

참조 DTO: [GetItemSummaryResponse](./api-schema-catalog.md#schema-getitemsummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/GetItemSummaryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsegetplaylistsummaryresponse"></a>

## PageResponseGetPlaylistSummaryResponse

참조 DTO: [GetPlaylistSummaryResponse](./api-schema-catalog.md#schema-getplaylistsummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/GetPlaylistSummaryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsegetvideolistresponse"></a>

## PageResponseGetVideoListResponse

참조 DTO: [GetVideoListResponse](./api-schema-catalog.md#schema-getvideolistresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/GetVideoListResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponseinquirysummaryresponse"></a>

## PageResponseInquirySummaryResponse

참조 DTO: [InquirySummaryResponse](./api-schema-catalog.md#schema-inquirysummaryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/InquirySummaryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponseitemhistoryresponse"></a>

## PageResponseItemHistoryResponse

참조 DTO: [ItemHistoryResponse](./api-schema-catalog.md#schema-itemhistoryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/ItemHistoryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsenewscommentresponse"></a>

## PageResponseNewsCommentResponse

참조 DTO: [NewsCommentResponse](./api-schema-catalog.md#schema-newscommentresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/NewsCommentResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponseparcelhistoryresponse"></a>

## PageResponseParcelHistoryResponse

참조 DTO: [ParcelHistoryResponse](./api-schema-catalog.md#schema-parcelhistoryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/ParcelHistoryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponsepointhistoryresponse"></a>

## PageResponsePointHistoryResponse

참조 DTO: [PointHistoryResponse](./api-schema-catalog.md#schema-pointhistoryresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/PointHistoryResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pageresponseuserwithdrawlogresponse"></a>

## PageResponseUserWithdrawLogResponse

참조 DTO: [UserWithdrawLogResponse](./api-schema-catalog.md#schema-userwithdrawlogresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/UserWithdrawLogResponse"
      }
    },
    "total": {
      "type": "integer",
      "format": "int64"
    },
    "page": {
      "type": "integer",
      "format": "int32"
    },
    "size": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-parcelhistoryresponse"></a>

## ParcelHistoryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "recipient": {
      "type": "string"
    },
    "sentAt": {
      "type": "string",
      "format": "date-time"
    },
    "content": {
      "type": "string"
    },
    "amount": {
      "type": "integer",
      "format": "int32"
    },
    "reason": {
      "type": "string"
    }
  }
}
```

<a id="schema-patcheventattendanceconfigrequest"></a>

## PatchEventAttendanceConfigRequest

참조 DTO: [AttendanceConfigItem](./api-schema-catalog.md#schema-attendanceconfigitem).

필수 필드: `configs`.

```json
{
  "type": "object",
  "properties": {
    "configs": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/AttendanceConfigItem"
      },
      "minItems": 1
    }
  },
  "required": [
    "configs"
  ]
}
```

<a id="schema-patcheventattendancerequest"></a>

## PatchEventAttendanceRequest

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "startAt": {
      "type": "string",
      "format": "date-time"
    },
    "endAt": {
      "type": "string",
      "format": "date-time"
    },
    "isActive": {
      "type": "boolean"
    }
  }
}
```

<a id="schema-patcheventrouletteconfigrequest"></a>

## PatchEventRouletteConfigRequest

참조 DTO: [RouletteConfigItem](./api-schema-catalog.md#schema-rouletteconfigitem).

필수 필드: `configs`.

```json
{
  "type": "object",
  "properties": {
    "configs": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/RouletteConfigItem"
      },
      "minItems": 1
    }
  },
  "required": [
    "configs"
  ]
}
```

<a id="schema-patcheventrouletterequest"></a>

## PatchEventRouletteRequest

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "startAt": {
      "type": "string",
      "format": "date-time"
    },
    "endAt": {
      "type": "string",
      "format": "date-time"
    },
    "isActive": {
      "type": "boolean"
    }
  }
}
```

<a id="schema-periodinquirystatsresponse"></a>

## PeriodInquiryStatsResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "receivedCount": {
      "type": "integer",
      "format": "int64"
    },
    "ongoingCount": {
      "type": "integer",
      "format": "int64"
    },
    "resolvedCount": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-perioditemsalesrankresponse"></a>

## PeriodItemSalesRankResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "rank": {
      "type": "integer",
      "format": "int32"
    },
    "itemName": {
      "type": "string"
    },
    "salesCount": {
      "type": "integer",
      "format": "int64"
    },
    "salesQty": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-perioditemstatsresponse"></a>

## PeriodItemStatsResponse

참조 DTO: [PeriodItemSalesRankResponse](./api-schema-catalog.md#schema-perioditemsalesrankresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "salesRanks": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/PeriodItemSalesRankResponse"
      }
    }
  }
}
```

<a id="schema-perioduserstatsresponse"></a>

## PeriodUserStatsResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "totalCount": {
      "type": "integer",
      "format": "int64"
    },
    "newCount": {
      "type": "integer",
      "format": "int64"
    },
    "loginCount": {
      "type": "integer",
      "format": "int64"
    },
    "onlineAvgCount": {
      "type": "integer",
      "format": "int64"
    },
    "onlineMaxCount": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-permissioncategoryresponse"></a>

## PermissionCategoryResponse

참조 DTO: [PermissionResponse](./api-schema-catalog.md#schema-permissionresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string"
    },
    "permissions": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/PermissionResponse"
      }
    }
  }
}
```

<a id="schema-permissionresponse"></a>

## PermissionResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string"
    },
    "label": {
      "type": "string"
    },
    "resource": {
      "type": "string"
    },
    "action": {
      "type": "string"
    }
  }
}
```

<a id="schema-playlistvideoresponse"></a>

## PlaylistVideoResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "videoId": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    },
    "thumbnailUrl": {
      "type": "string"
    },
    "sortOrder": {
      "type": "integer",
      "format": "int32"
    }
  }
}
```

<a id="schema-pointhistoryresponse"></a>

## PointHistoryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "userNickname": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": [
        "DEDUCT",
        "REDEEM",
        "RECHARGE",
        "REWARD"
      ]
    },
    "action": {
      "type": "string",
      "enum": [
        "TRADE",
        "PURCHASE",
        "QUEST",
        "REGISTRATION",
        "ACHIEVEMENT",
        "MANUAL"
      ]
    },
    "objectName": {
      "type": "string"
    },
    "changeAmount": {
      "type": "integer",
      "format": "int32"
    },
    "netAmount": {
      "type": "integer",
      "format": "int64"
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-roledetailresponse"></a>

## RoleDetailResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "immutable": {
      "type": "boolean"
    },
    "permissionCodes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

<a id="schema-rolesummary"></a>

## RoleSummary

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string"
    },
    "name": {
      "type": "string"
    }
  }
}
```

<a id="schema-rolesummaryresponse"></a>

## RoleSummaryResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "code": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "immutable": {
      "type": "boolean"
    },
    "permissionCount": {
      "type": "integer",
      "format": "int32"
    },
    "adminCount": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-rouletteconfigitem"></a>

## RouletteConfigItem

필수 필드: `configKey`.

```json
{
  "type": "object",
  "properties": {
    "configKey": {
      "type": "string",
      "enum": [
        "ROULETTE_BACKGROUND",
        "ROULETTE_BACK_BOARD",
        "ROULETTE_PIN",
        "ROULETTE_START_BUTTON",
        "ROULETTE_COLOR_V1",
        "ROULETTE_COLOR_V2",
        "ROULETTE_COLOR_V3",
        "ROULETTE_TOP_TITLE"
      ]
    },
    "configValue": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": [
        "IMAGE",
        "TEXT"
      ]
    }
  },
  "required": [
    "configKey"
  ]
}
```

<a id="schema-sendparcelrequest"></a>

## SendParcelRequest

필수 필드: `amount`, `content`, `itemId`, `title`, `userId`.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "minLength": 1
    },
    "content": {
      "type": "string",
      "minLength": 1
    },
    "userId": {
      "type": "integer",
      "format": "int64"
    },
    "itemId": {
      "type": "integer",
      "format": "int64"
    },
    "amount": {
      "type": "integer",
      "format": "int32",
      "minimum": 0
    }
  },
  "required": [
    "amount",
    "content",
    "itemId",
    "title",
    "userId"
  ]
}
```

<a id="schema-setmaintenancetimerequest"></a>

## SetMaintenanceTimeRequest

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "start": {
      "type": "string",
      "pattern": "^([01]\\d|2[0-3]):[0-5]\\d$"
    },
    "end": {
      "type": "string",
      "pattern": "^([01]\\d|2[0-3]):[0-5]\\d$"
    }
  }
}
```

<a id="schema-setmaintenanceversionrequest"></a>

## SetMaintenanceVersionRequest

필수 필드: `version`.

```json
{
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "maxLength": 255,
      "minLength": 0
    }
  },
  "required": [
    "version"
  ]
}
```

<a id="schema-tokenresponse"></a>

## TokenResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "accessToken": {
      "type": "string"
    }
  }
}
```

<a id="schema-updateaccountrolesrequest"></a>

## UpdateAccountRolesRequest

필수 필드: `roleIds`.

```json
{
  "type": "object",
  "properties": {
    "roleIds": {
      "type": "array",
      "items": {
        "type": "integer",
        "format": "int64"
      }
    }
  },
  "required": [
    "roleIds"
  ]
}
```

<a id="schema-updatecitizenproposalreviewresultrequest"></a>

## UpdateCitizenProposalReviewResultRequest

필수 필드: `reviewResult`.

```json
{
  "type": "object",
  "properties": {
    "reviewResult": {
      "type": "string",
      "maxLength": 5000,
      "minLength": 0
    }
  },
  "required": [
    "reviewResult"
  ]
}
```

<a id="schema-updatecitizenproposalstatusrequest"></a>

## UpdateCitizenProposalStatusRequest

필수 필드: `status`.

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": [
        "RECEIVED",
        "UNDER_REVIEW",
        "ADOPTED",
        "REJECTED"
      ]
    }
  },
  "required": [
    "status"
  ]
}
```

<a id="schema-updateeventattendanceitemsrequest"></a>

## UpdateEventAttendanceItemsRequest

참조 DTO: [EventAttendanceItemDto](./api-schema-catalog.md#schema-eventattendanceitemdto).

필수 필드: `items`.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventAttendanceItemDto"
      },
      "minItems": 1
    }
  },
  "required": [
    "items"
  ]
}
```

<a id="schema-updateeventrouletteitemsrequest"></a>

## UpdateEventRouletteItemsRequest

참조 DTO: [EventRouletteItemDto](./api-schema-catalog.md#schema-eventrouletteitemdto).

필수 필드: `items`.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/EventRouletteItemDto"
      },
      "minItems": 1
    }
  },
  "required": [
    "items"
  ]
}
```

<a id="schema-updateinquirystatusrequest"></a>

## UpdateInquiryStatusRequest

필수 필드: `status`.

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": [
        "OPEN",
        "IN_PROGRESS",
        "COMPLETED"
      ]
    }
  },
  "required": [
    "status"
  ]
}
```

<a id="schema-updateinquirytyperequest"></a>

## UpdateInquiryTypeRequest

필수 필드: `name`.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": [
    "name"
  ]
}
```

<a id="schema-updateitemcategoryrequest"></a>

## UpdateItemCategoryRequest

필수 필드: `name`.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    },
    "parentCatrgoryName": {
      "type": "string"
    }
  },
  "required": [
    "name"
  ]
}
```

<a id="schema-updateitemrequest"></a>

## UpdateItemRequest

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "mainCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "subCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "gender": {
      "type": "string",
      "enum": [
        "COMMON",
        "MAN",
        "WOMAN"
      ]
    },
    "saleAmount": {
      "type": "integer",
      "format": "int32"
    },
    "paymentType": {
      "type": "string",
      "enum": [
        "POINT"
      ]
    },
    "newBadgeUntil": {
      "type": "string",
      "format": "date-time"
    },
    "isShowApp": {
      "type": "boolean"
    },
    "excludeFromEventReward": {
      "type": "boolean"
    },
    "status": {
      "type": "string",
      "enum": [
        "PENDING",
        "ON_SALE",
        "ON_HOLD",
        "END_SALE"
      ]
    },
    "image": {
      "type": "string"
    }
  }
}
```

<a id="schema-updateitemresponse"></a>

## UpdateItemResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "mainCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "subCategoryId": {
      "type": "integer",
      "format": "int64"
    },
    "gender": {
      "type": "string",
      "enum": [
        "COMMON",
        "MAN",
        "WOMAN"
      ]
    },
    "saleAmount": {
      "type": "integer",
      "format": "int32"
    },
    "paymentType": {
      "type": "string",
      "enum": [
        "POINT"
      ]
    },
    "newBadgeUntil": {
      "type": "string",
      "format": "date-time"
    },
    "isShowApp": {
      "type": "boolean"
    },
    "excludeFromEventReward": {
      "type": "boolean"
    },
    "status": {
      "type": "string",
      "enum": [
        "PENDING",
        "ON_SALE",
        "ON_HOLD",
        "END_SALE"
      ]
    },
    "imageUrl": {
      "type": "string"
    }
  }
}
```

<a id="schema-updateitemsliststatusrequest"></a>

## UpdateItemsListStatusRequest

필수 필드: `itemIds`, `status`.

```json
{
  "type": "object",
  "properties": {
    "itemIds": {
      "type": "array",
      "items": {
        "type": "integer",
        "format": "int64"
      },
      "minItems": 1
    },
    "status": {
      "type": "string",
      "enum": [
        "PENDING",
        "ON_SALE",
        "ON_HOLD",
        "END_SALE"
      ]
    }
  },
  "required": [
    "itemIds",
    "status"
  ]
}
```

<a id="schema-updatemaintenanceitemrequest"></a>

## UpdateMaintenanceItemRequest

참조 DTO: [MaintenanceConfigItem](./api-schema-catalog.md#schema-maintenanceconfigitem).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "config": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/MaintenanceConfigItem"
      }
    }
  }
}
```

<a id="schema-updatemenuorderrequest"></a>

## UpdateMenuOrderRequest

참조 DTO: [Item](./api-schema-catalog.md#schema-item).

필수 필드: `items`.

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/Item"
      },
      "minItems": 1
    }
  },
  "required": [
    "items"
  ]
}
```

<a id="schema-updatemenurequest"></a>

## UpdateMenuRequest

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "label": {
      "type": "string",
      "maxLength": 50,
      "minLength": 0
    },
    "visible": {
      "type": "boolean"
    }
  }
}
```

<a id="schema-updatenewsrequest"></a>

## UpdateNewsRequest

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string"
    },
    "content": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": [
        "ANNOUNCEMENT",
        "UPDATE",
        "EVENT",
        "ETC"
      ]
    },
    "status": {
      "type": "string",
      "enum": [
        "DRAFT",
        "PUBLISHED",
        "ARCHIVED"
      ]
    },
    "isPinned": {
      "type": "boolean"
    }
  }
}
```

<a id="schema-updateplaylistrequest"></a>

## UpdatePlaylistRequest

필수 필드: `name`.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    },
    "videoIds": {
      "type": "array",
      "items": {
        "type": "integer",
        "format": "int64"
      }
    }
  },
  "required": [
    "name"
  ]
}
```

<a id="schema-updaterolepermissionsrequest"></a>

## UpdateRolePermissionsRequest

필수 필드: `permissionCodes`.

```json
{
  "type": "object",
  "properties": {
    "permissionCodes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "permissionCodes"
  ]
}
```

<a id="schema-updaterolerequest"></a>

## UpdateRoleRequest

필수 필드: `name`.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "maxLength": 50,
      "minLength": 0
    }
  },
  "required": [
    "name"
  ]
}
```

<a id="schema-updateuserstatusrequest"></a>

## UpdateUserStatusRequest

필수 필드: `status`.

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": [
        "ACTIVE",
        "SUSPEND"
      ]
    },
    "reason": {
      "type": "string"
    }
  },
  "required": [
    "status"
  ]
}
```

<a id="schema-updatevideorequest"></a>

## UpdateVideoRequest

필수 필드: `name`.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    }
  },
  "required": [
    "name"
  ]
}
```

<a id="schema-uploadeventattendanceconfigimageresponse"></a>

## UploadEventAttendanceConfigImageResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string"
    }
  }
}
```

<a id="schema-uploadeventrouletteconfigimageresponse"></a>

## UploadEventRouletteConfigImageResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string"
    }
  }
}
```

<a id="schema-uploaditemimageresponse"></a>

## UploadItemImageResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "uuid": {
      "type": "string"
    },
    "url": {
      "type": "string"
    }
  }
}
```

<a id="schema-userstatuscountresponse"></a>

## UserStatusCountResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": [
        "ACTIVE",
        "SUSPENDED",
        "WITHDRAWN"
      ]
    },
    "count": {
      "type": "integer",
      "format": "int64"
    }
  }
}
```

<a id="schema-userwithdrawlogresponse"></a>

## UserWithdrawLogResponse

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "publicId": {
      "type": "string",
      "format": "uuid"
    },
    "nickname": {
      "type": "string"
    },
    "withdrawnAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

<a id="schema-weeklydashboardresponse"></a>

## WeeklyDashboardResponse

참조 DTO: [ExternalOsStatsResponse](./api-schema-catalog.md#schema-externalosstatsresponse), [PeriodInquiryStatsResponse](./api-schema-catalog.md#schema-periodinquirystatsresponse), [PeriodItemStatsResponse](./api-schema-catalog.md#schema-perioditemstatsresponse), [PeriodUserStatsResponse](./api-schema-catalog.md#schema-perioduserstatsresponse).

필수 필드: 명시된 required 목록 없음.

```json
{
  "type": "object",
  "properties": {
    "week": {
      "type": "string"
    },
    "startDate": {
      "type": "string",
      "format": "date"
    },
    "endDate": {
      "type": "string",
      "format": "date"
    },
    "user": {
      "$ref": "#/components/schemas/PeriodUserStatsResponse"
    },
    "os": {
      "$ref": "#/components/schemas/ExternalOsStatsResponse"
    },
    "inquiry": {
      "$ref": "#/components/schemas/PeriodInquiryStatsResponse"
    },
    "item": {
      "$ref": "#/components/schemas/PeriodItemStatsResponse"
    }
  }
}
```
