# 테스트 초안 이력

> 완료 업데이트: 두 테스트 파일을 실제 소스에 반영하고 보완했으며 EC·라우팅 테스트 41개가 통과했다. 아래는 구현 중단 당시의 초안으로, 현재 src의 테스트 코드와 final-summary.md가 정본이다.

복구 operation의 소스 snapshot을 유지하기 위해 테스트는 아직 코드 파일에 쓰지 않았다. 아래 초안을 해당 경로에 반영한 뒤 포맷·타입 검사·실행하고 발견한 오류를 수정한다. 기대값은 사용자 승인으로 작성한 예상 계약에 대한 검증이며 서버 명세의 증거가 아니다.

## src/features/ec/api/ec.api.test.ts

```ts
import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { beforeEach, describe, expect, it } from "vitest";
import { createApiClient } from "~/shared/api/api-client";
import { unwrapAxiosResponse } from "~/shared/api/unwrap-axios-response";
import { ApiFailureError, toApiFailure } from "~/shared/api/error";
import { unwrapEcResult } from "../model/apiResult";
import { ecApi } from "./ec.api";
import { ecCheckoutSourceSchema, ecCreateInquiryRequestSchema, ecShippingFormSchema } from "./ec.dto";
import { parseEcProduct, parseEcProducts } from "./ec.parser";

// 예상 계약의 로컬 전송 테스트다. 실제 서버나 개발용 mock에는 연결하지 않는다.
let received: InternalAxiosRequestConfig | undefined;
let response: unknown;
let status = 200;
let networkFailure = false;
const instance = axios.create({
  baseURL: "https://ec-contract.test",
  headers: { Authorization: "Bearer test" },
  adapter: async (config) => {
    received = config;
    if (networkFailure) throw new AxiosError("network", AxiosError.ERR_NETWORK);
    const result = { data: response, status, statusText: "", headers: {}, config };
    if (status >= 400) throw new AxiosError("server", AxiosError.ERR_BAD_RESPONSE, config, undefined, result);
    return result;
  },
});
instance.interceptors.response.use(unwrapAxiosResponse, (error: unknown) => { throw new ApiFailureError(toApiFailure(error)); });
const api = ecApi(createApiClient(instance));
const success = (data: unknown) => { response = { code: "SUCCESS", data }; };
beforeEach(() => { received = undefined; status = 200; networkFailure = false; });

describe("EC 예상 API 계약", () => {
  it("목록은 page/size와 검색·카테고리를 URLSearchParams로 보내고 공통 페이지 응답을 사용한다", async () => {
    success({ items: [], total: 0, page: 2, size: 10 });
    expect(unwrapEcResult(await api.getProducts({ page: 2, keyword: "생활 & 용품", categoryId: "all" })).items).toEqual([]);
    expect(received?.url).toBe("/ec/products");
    expect(Object.fromEntries(received?.params as URLSearchParams)).toEqual({ page: "2", size: "10", keyword: "생활 & 용품", categoryId: "all" });
    expect(received).toMatchObject({ authRequired: true });
    expect(received?.headers.get("Authorization")).toBe("Bearer test");
    expect(() => api.getProducts({ page: 0 })).toThrow();
    expect(() => api.getProducts({ size: 20 })).toThrow();
  });
  it("주문·EC 문의 목록은 10개씩 요청하며 주문 기간을 임의로 추가하지 않는다", async () => {
    success({ items: [], total: 0, page: 1, size: 10 });
    for (const send of [() => api.getOrders(), () => api.getInquiries()]) {
      await send();
      expect(Object.fromEntries(received?.params as URLSearchParams)).toEqual({ page: "1", size: "10" });
    }
    expect(received?.url).toBe("/ec/inquiries");
  });
  it("FAQ 전체 조회에 size를 추가하지 않는다", async () => {
    success([]);
    await api.getFaqs("배송");
    expect(Object.fromEntries(received?.params as URLSearchParams)).toEqual({ keyword: "배송" });
  });
  it("바로 구매와 장바구니 구매의 식별자를 분리하고 장바구니 ID를 반복 인자로 보낸다", async () => {
    success({ items: [], summary: { productAmount: 0, shippingFee: 0, totalAmount: 0 } });
    await api.getCheckout({ kind: "product", productId: 7, quantity: 2 });
    expect(Object.fromEntries(received?.params as URLSearchParams)).toEqual({ productId: "7", quantity: "2" });
    await api.getCheckout({ kind: "cart", cartItemIds: [11, 22] });
    const params = received?.params as URLSearchParams;
    expect(params.getAll("cartItemIds")).toEqual(["11", "22"]);
    expect(params.has("productId")).toBe(false);
    expect(ecCheckoutSourceSchema.safeParse(null).success).toBe(false);
    expect(ecCheckoutSourceSchema.safeParse({ kind: "cart", cartItemIds: [] }).success).toBe(false);
    expect(ecCheckoutSourceSchema.safeParse({ kind: "product", productId: 1, quantity: 0 }).success).toBe(false);
  });
  it("담기와 문의 작성은 허용 필드만 전송하며 첨부를 임의로 추가하지 않는다", async () => {
    success({ cartItemId: 11, cartCount: 1 });
    const cart = { productId: 7, quantity: 2, price: 1 };
    await api.addCartItem(cart);
    expect(JSON.parse(String(received?.data))).toEqual({ productId: 7, quantity: 2 });
    success({ inquiryId: 3 });
    const inquiry = { type: "PRODUCT" as const, title: " 제목 ", content: " 내용 ", imageFileIds: ["ignored"], authorId: 9 };
    await api.createInquiry(inquiry);
    expect(JSON.parse(String(received?.data))).toEqual({ type: "PRODUCT", title: " 제목 ", content: " 내용 " });
    expect(received?.url).toBe("/ec/inquiries");
    expect(() => api.createInquiry({ ...inquiry, title: " " })).toThrow();
  });
  it("장바구니 수량·삭제와 찜 추가·해제 메서드 및 응답을 확인한다", async () => {
    success({ items: [], summary: { productAmount: 0, shippingFee: 0, totalAmount: 0 } });
    await api.changeCartQuantity(11, 3);
    expect(received).toMatchObject({ url: "/ec/cart/items/11", method: "patch" });
    expect(JSON.parse(String(received?.data))).toEqual({ quantity: 3 });
    await api.removeCartItem(11);
    expect(received?.method).toBe("delete");
    success({ wished: true });
    await api.setWish(7, true);
    expect(received).toMatchObject({ url: "/ec/products/7/wish", method: "post" });
    success({ wished: false });
    await api.setWish(7, false);
    expect(received?.method).toBe("delete");
    expect(() => api.changeCartQuantity(11, 0)).toThrow();
    expect(() => api.getProduct(-1)).toThrow();
  });
  it("업무 실패·HTTP 실패·네트워크 실패·취소를 성공 데이터로 바꾸지 않는다", async () => {
    response = { code: "NOT_FOUND", message: "없음", data: null };
    const result = await api.getProduct(7);
    expect(() => unwrapEcResult(result)).toThrow("없음");
    status = 404;
    await expect(api.getProduct(7)).rejects.toMatchObject({ failure: { kind: "server", statusCode: 404 } });
    status = 200; networkFailure = true;
    await expect(api.getProduct(7)).rejects.toMatchObject({ failure: { kind: "transport" } });
    networkFailure = false;
    const abort = new AbortController(); abort.abort();
    await expect(api.getProduct(7, abort.signal)).rejects.toMatchObject({ failure: { kind: "canceled" } });
  });
  it("조회와 mutation에 취소 신호를 전달하고 malformed payload를 거부한다", async () => {
    const abort = new AbortController();
    success({ count: 0 });
    await api.getCartCount(abort.signal);
    expect(received?.signal).toBe(abort.signal);
    success({ inquiryId: 1 });
    await api.createInquiry({ type: "ETC", title: "제목", content: "내용" }, abort.signal);
    expect(received?.signal).toBe(abort.signal);
    success({ count: "1" });
    await expect(api.getCartCount()).rejects.toThrow();
    expect(() => parseEcProducts({ items: [], total: 0, page: 0, size: 10 })).toThrow();
    expect(() => parseEcProduct({ id: 1 })).toThrow();
  });
});

describe("EC 폼 검증", () => {
  const shipping = { recipient: "사용자", phone: "01012345678", zipCode: "형식 제한 없음", address: "주소", addressDetail: "상세", memo: "" };
  it.each(["01012345678", "010-1234-5678"])("국내 휴대전화 %s를 허용한다", (phone) => {
    expect(ecShippingFormSchema.safeParse({ ...shipping, phone }).success).toBe(true);
  });
  it.each(["", "0101234567", "010-12345678", "02-1234-5678", "010-abcd-5678"])("잘못된 번호 %s를 거부한다", (phone) => {
    expect(ecShippingFormSchema.safeParse({ ...shipping, phone }).success).toBe(false);
  });
  it("배송지 필수값과 문의 필수값만 제한하고 텍스트 길이 상한은 두지 않는다", () => {
    expect(ecShippingFormSchema.safeParse({ ...shipping, address: " " }).success).toBe(false);
    expect(ecShippingFormSchema.safeParse({ ...shipping, addressDetail: "" }).success).toBe(false);
    expect(ecCreateInquiryRequestSchema.safeParse({ type: "ETC", title: "가".repeat(10001), content: "나".repeat(100001) }).success).toBe(true);
    expect(ecCreateInquiryRequestSchema.safeParse({ type: "ETC", title: "", content: "내용" }).success).toBe(false);
  });
});
```

## src/pages/ec/model/useEcControllers.test.tsx

```tsx
// @vitest-environment jsdom
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, useState } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { ecClient } from "~/features/ec/api/client";
import type { EcProductDetailResponseDto } from "~/features/ec/api/ec.dto";
import { ecKeys } from "~/features/ec/model/queryKeys";
import { useEcCartMutation } from "~/features/ec/hook/useEcMutation";
import { useEcProductQuery } from "~/features/ec/hook/useEcQueries";
import type { ApiResult } from "~/shared/api/common/api-result";
import { useDialogStore } from "~/shared/ui/dialog/dialog.store";
import { useEcMarketController } from "./useEcMarketController";
import { useEcProductController } from "./useEcProductController";
import { useEcCartController } from "./useEcCartController";
import { useEcCheckoutController } from "./useEcCheckoutController";
import { useEcInquiryListController, useEcInquiryWriteController, useEcSupportController } from "./useEcSupportControllers";
import { useEcListLocation } from "./useEcListLocation";

const success = <T,>(data: T): ApiResult<T> => ({ success: true, data, error: null });
const product: EcProductDetailResponseDto = {
  id: 7, name: "상품", price: 1000, rating: null, imageUrls: [], originalPrice: null,
  stockQuantity: 3, maxOrderQuantity: 2, reviewCount: 0, delivery: null, features: [],
  usageGuide: null, shippingGuide: null, wished: false,
};
const cartItem = { id: 11, productId: 7, name: "상품", optionLabel: null, thumbnailUrl: null, price: 1000, quantity: 1, maxOrderQuantity: 2 };
const cart = { items: [cartItem], summary: { productAmount: 1000, shippingFee: 0, totalAmount: 1000 } };
const cleanups: (() => void)[] = [];
beforeAll(() => { Object.defineProperty(globalThis, "IS_REACT_ACT_ENVIRONMENT", { value: true }); });
beforeEach(() => {
  useDialogStore.setState({ isOpen: false, payload: null, confirmResolve: null });
  vi.spyOn(ecClient, "getCartCount").mockResolvedValue(success({ count: 1 }));
});
afterEach(() => {
  cleanups.splice(0).reverse().forEach((cleanup) => cleanup());
  vi.restoreAllMocks();
});
const renderHook = <T,>(useHook: () => T, entry = "/ec") => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, staleTime: Infinity }, mutations: { retry: false } } });
  cleanups.push(() => client.clear());
  let value: T;
  const Harness = () => { value = useHook(); return null; };
  const root = createRoot(document.createElement("div"));
  let mounted = true;
  const unmount = () => { if (mounted) { act(() => root.unmount()); mounted = false; } };
  cleanups.push(unmount);
  act(() => root.render(<QueryClientProvider client={client}><MemoryRouter initialEntries={[entry]}><Harness /></MemoryRouter></QueryClientProvider>));
  return { result: () => value, client, unmount };
};
const waitFor = (assertion: () => void) => act(async () => { await vi.waitFor(assertion); });

describe("EC controller 계약", () => {
  it("상품 검색은 제출까지 요청하지 않고 전체 카테고리와 10개 페이지 정보를 제공한다", async () => {
    const get = vi.spyOn(ecClient, "getProducts").mockResolvedValue(success({ items: [], total: 21, page: 1, size: 10 }));
    vi.spyOn(ecClient, "getCategories").mockResolvedValue(success([{ id: "all", name: "전체라는 ID" }]));
    const change = vi.fn();
    const h = renderHook(() => useEcMarketController({ page: 1, size: 10 }, change));
    await waitFor(() => expect(h.result().pageCount).toBe(3));
    expect(h.result().categories).toEqual([{ label: "전체", value: "all" }, { label: "전체라는 ID", value: "category:all" }]);
    act(() => h.result().onKeywordChange(" 새 검색 "));
    expect(get).toHaveBeenCalledTimes(1);
    act(() => h.result().onKeywordSubmit());
    expect(change).toHaveBeenLastCalledWith({ page: 1, size: 10, keyword: "새 검색" });
    act(() => h.result().onCategoryChange("category:all"));
    expect(change).toHaveBeenLastCalledWith({ page: 1, size: 10, categoryId: "all" });
    act(() => h.result().onCategoryChange("all"));
    expect(change).toHaveBeenLastCalledWith({ page: 1, size: 10 });
  });
  it("목록 실패를 정상 빈 목록으로 분류하지 않는다", async () => {
    vi.spyOn(ecClient, "getProducts").mockRejectedValue(new Error("조회 실패"));
    vi.spyOn(ecClient, "getCategories").mockResolvedValue(success([]));
    const h = renderHook(() => useEcMarketController({}, vi.fn()));
    await waitFor(() => expect(h.result().error).toBeInstanceOf(Error));
    expect(h.result().isEmpty).toBe(false);
  });
  it("상품 수량 제한과 구매 state를 지키며 서버 찜 결과로 표시를 갱신한다", async () => {
    vi.spyOn(ecClient, "getProduct").mockResolvedValue(success(product));
    const wish = vi.spyOn(ecClient, "setWish").mockResolvedValue(success({ wished: true }));
    const checkout = vi.fn();
    const h = renderHook(() => useEcProductController(7, checkout));
    await waitFor(() => expect(h.result().product?.id).toBe(7));
    act(() => h.result().onQuantityChange(3));
    expect(h.result().quantity).toBe(1);
    act(() => h.result().onQuantityChange(2));
    act(() => h.result().onBuyNow());
    expect(checkout).toHaveBeenCalledWith({ kind: "product", productId: 7, quantity: 2 });
    act(() => { h.result().onWishToggle(); h.result().onWishToggle(); });
    await waitFor(() => expect(h.result().isWished).toBe(true));
    expect(wish).toHaveBeenCalledTimes(1);
  });
  it("장바구니 중복 담기를 막고 기존 알림 모달을 연다", async () => {
    vi.spyOn(ecClient, "getProduct").mockResolvedValue(success(product));
    let release: (() => void) | undefined;
    const gate = new Promise<void>((resolve) => { release = resolve; });
    const add = vi.spyOn(ecClient, "addCartItem").mockImplementation(async () => { await gate; return success({ cartItemId: 11, cartCount: 1 }); });
    const h = renderHook(() => useEcProductController(7, vi.fn()));
    await waitFor(() => expect(h.result().product?.id).toBe(7));
    try {
      act(() => { h.result().onAddToCart(); h.result().onAddToCart(); });
      await waitFor(() => expect(add).toHaveBeenCalledTimes(1));
    } finally { release?.(); }
    await waitFor(() => expect(useDialogStore.getState().payload?.content).toContain("담았습니다"));
  });
  it("장바구니 변경은 관련 캐시만 무효화한다", async () => {
    vi.spyOn(ecClient, "changeCartQuantity").mockResolvedValue(success(cart));
    const h = renderHook(useEcCartMutation);
    const keys = [ecKeys.cart, ecKeys.cartCount, ecKeys.checkout({ kind: "cart", cartItemIds: [11] }), ecKeys.orders({}), ["inquiries"]];
    keys.forEach((key) => h.client.setQueryData(key, {}));
    await act(async () => { await h.result().mutateAsync({ kind: "quantity", id: 11, quantity: 2 }); });
    expect(keys.map((key) => h.client.getQueryState(key)?.isInvalidated)).toEqual([true, true, true, false, false]);
  });
  it("장바구니 주문은 상품 ID가 아닌 장바구니 항목 ID를 전달한다", async () => {
    vi.spyOn(ecClient, "getCart").mockResolvedValue(success(cart));
    const checkout = vi.fn();
    const h = renderHook(() => useEcCartController(checkout));
    await waitFor(() => expect(h.result().items).toHaveLength(1));
    act(() => h.result().onOrder());
    expect(checkout).toHaveBeenCalledWith({ kind: "cart", cartItemIds: [11] });
  });
  it("checkout에 유효한 state가 없으면 요청하지 않으며 배송지 기본값은 비어 있다", async () => {
    const get = vi.spyOn(ecClient, "getCheckout").mockResolvedValue(success(cart));
    const h = renderHook(() => useEcCheckoutController(null));
    expect(get).not.toHaveBeenCalled();
    expect(h.result().isValidSource).toBe(false);
    expect(h.result().values).toEqual({ recipient: "", phone: "", zipCode: "", address: "", addressDetail: "", memo: "" });
    await act(async () => { expect(await h.result().validate()).toBe(false); });
    expect(h.result().errors.phone).toBeDefined();
  });
  it("checkout 조회 후에도 배송지 자동 초기화 없이 입력·검증만 제공한다", async () => {
    vi.spyOn(ecClient, "getCheckout").mockResolvedValue(success(cart));
    const h = renderHook(() => useEcCheckoutController({ kind: "product", productId: 7, quantity: 1 }));
    await waitFor(() => expect(h.result().items).toHaveLength(1));
    act(() => {
      h.result().onChange("recipient", "받는 분"); h.result().onChange("phone", "010-1234-5678");
      h.result().onChange("zipCode", "문자도 허용"); h.result().onChange("address", "주소"); h.result().onChange("addressDetail", "상세");
    });
    await act(async () => { expect(await h.result().validate()).toBe(true); });
    expect(h.result().errors).toEqual({});
  });
  it("FAQ는 제출 후 검색하고 전체 응답을 유지한다", async () => {
    const items = Array.from({ length: 8 }, (_, index) => ({ id: index + 1, question: "질문", answer: "답변" }));
    const get = vi.spyOn(ecClient, "getFaqs").mockResolvedValue(success(items));
    const h = renderHook(useEcSupportController);
    await waitFor(() => expect(h.result().faqs).toHaveLength(8));
    act(() => h.result().onKeywordChange("배송"));
    expect(get).toHaveBeenCalledTimes(1);
    act(() => h.result().onKeywordSubmit());
    await waitFor(() => expect(get).toHaveBeenCalledTimes(2));
    expect(get.mock.calls[1]?.[0]).toBe("배송");
  });
  it("EC 문의 목록은 EC API와 페이지 번호를 사용한다", async () => {
    const get = vi.spyOn(ecClient, "getInquiries").mockResolvedValue(success({ items: [{ id: 3, type: "ETC", title: "문의", status: "OPEN", createdAt: "2026-09-28T01:00:00Z" }], total: 11, page: 2, size: 10 }));
    const h = renderHook(() => useEcInquiryListController(2));
    await waitFor(() => expect(h.result().items[0]?.title).toBe("문의"));
    expect(get.mock.calls[0]?.[0]).toEqual({ page: 2, size: 10 });
    expect(h.result().pageCount).toBe(2);
  });
  it("문의 필수 검증·중복 제출 방지·완료 알림 후 이동을 제공한다", async () => {
    let release: (() => void) | undefined;
    const gate = new Promise<void>((resolve) => { release = resolve; });
    const create = vi.spyOn(ecClient, "createInquiry").mockImplementation(async () => { await gate; return success({ inquiryId: 3 }); });
    const completed = vi.fn();
    const h = renderHook(() => useEcInquiryWriteController(completed));
    await act(async () => { await h.result().submit(); });
    expect(create).not.toHaveBeenCalled();
    expect(h.result().errors.type).toBeDefined();
    act(() => {
      h.result().onTypeChange("ETC"); h.result().onChange("title", "문의"); h.result().onChange("content", "내용");
    });
    try {
      await act(async () => { await Promise.all([h.result().submit(), h.result().submit()]); });
      expect(create).toHaveBeenCalledTimes(1);
      expect(create).toHaveBeenCalledWith({ type: "ETC", title: "문의", content: "내용" });
      expect(completed).not.toHaveBeenCalled();
    } finally { release?.(); }
    await waitFor(() => expect(h.result().isSuccess).toBe(true));
    const payload = useDialogStore.getState().payload;
    expect(payload?.content).toContain("등록되었습니다");
    if (payload && "callback" in payload) act(() => payload.callback?.());
    expect(completed).toHaveBeenCalledTimes(1);
    await act(async () => { await h.result().submit(); });
    expect(create).toHaveBeenCalledTimes(1);
  });
  it("문의 실패 후 입력을 보존하고 재제출한다", async () => {
    const create = vi.spyOn(ecClient, "createInquiry").mockRejectedValueOnce(new Error("실패")).mockResolvedValue(success({ inquiryId: 3 }));
    const h = renderHook(() => useEcInquiryWriteController(vi.fn()));
    act(() => { h.result().onTypeChange("PRODUCT"); h.result().onChange("title", "제목"); h.result().onChange("content", "내용"); });
    await act(async () => { await h.result().submit(); });
    await waitFor(() => expect(h.result().error).toBeInstanceOf(Error));
    expect(h.result().values.title).toBe("제목");
    await act(async () => { await h.result().submit(); });
    await waitFor(() => expect(h.result().isSuccess).toBe(true));
    expect(create).toHaveBeenCalledTimes(2);
  });
  it("목록 페이지는 URL에서 읽고 첫 페이지의 page 인자를 생략한다", () => {
    const h = renderHook(useEcListLocation, "/ec?page=2&keyword=검색");
    expect(h.result().page).toBe(2);
    act(() => h.result().changePage(1));
    expect(h.result().key).not.toContain("page=");
    expect(h.result().params.keyword).toBe("검색");
  });
  it("상세 ID가 바뀌면 이전 요청을 취소하고 최신 응답만 노출한다", async () => {
    const signals: AbortSignal[] = [];
    const get = vi.spyOn(ecClient, "getProduct").mockImplementation((id, signal) => {
      if (signal) signals.push(signal);
      return id === 7 ? new Promise(() => undefined) : Promise.resolve(success({ ...product, id }));
    });
    const h = renderHook(() => {
      const [id, setId] = useState<number>();
      return { query: useEcProductQuery(id), setId };
    });
    expect(get).not.toHaveBeenCalled();
    act(() => h.result().setId(7));
    await waitFor(() => expect(get).toHaveBeenCalledTimes(1));
    act(() => h.result().setId(8));
    await waitFor(() => expect(h.result().query.data?.id).toBe(8));
    expect(signals[0]?.aborted).toBe(true);
  });
});
```
