import pandas as pd
import streamlit as st

st.set_page_config(page_title="퍼스트존 관리자", page_icon="🛒", layout="wide")

orders = pd.DataFrame([
    {"주문번호": "ORD-24081", "주문일시": "08-12 09:14", "고객": "김민준", "상품명": "무선 이어폰 프로", "카테고리": "가전", "수량": 1, "결제금액": 129000, "상태": "결제 완료", "결제수단": "카드"},
    {"주문번호": "ORD-24082", "주문일시": "08-12 09:41", "고객": "이서연", "상품명": "캠핑 체어 2인용", "카테고리": "레저", "수량": 2, "결제금액": 98000, "상태": "배송 준비", "결제수단": "카드"},
    {"주문번호": "ORD-24083", "주문일시": "08-12 10:02", "고객": "박도윤", "상품명": "원두 1kg 다크로스트", "카테고리": "식품", "수량": 3, "결제금액": 42000, "상태": "배송 중", "결제수단": "간편결제"},
    {"주문번호": "ORD-24084", "주문일시": "08-12 10:35", "고객": "최지우", "상품명": "USB-C 충전기 65W", "카테고리": "가전", "수량": 1, "결제금액": 34000, "상태": "결제 완료", "결제수단": "간편결제"},
    {"주문번호": "ORD-24085", "주문일시": "08-12 11:08", "고객": "정하은", "상품명": "러닝화 270", "카테고리": "패션", "수량": 1, "결제금액": 89000, "상태": "취소", "결제수단": "카드"},
    {"주문번호": "ORD-24086", "주문일시": "08-12 11:22", "고객": "강시우", "상품명": "우드 식탁 4인", "카테고리": "가구", "수량": 1, "결제금액": 320000, "상태": "배송 준비", "결제수단": "무통장"},
    {"주문번호": "ORD-24087", "주문일시": "08-12 12:01", "고객": "윤아름", "상품명": "린넨 셔츠 화이트", "카테고리": "패션", "수량": 2, "결제금액": 56000, "상태": "배송 완료", "결제수단": "카드"},
    {"주문번호": "ORD-24088", "주문일시": "08-12 12:44", "고객": "임준호", "상품명": "텀블러 500ml", "카테고리": "생활", "수량": 4, "결제금액": 28000, "상태": "환불", "결제수단": "간편결제"},
])

# --- 사이드바 ---
with st.sidebar:
    st.title("퍼스트존 관리자")
    st.caption("피카츄 · 운영팀")
    st.divider()

    st.subheader("메뉴")
    st.radio("메뉴", ["대시보드", "주문 관리", "상품 관리", "정산"], index=1, label_visibility="collapsed")
    st.divider()

    st.subheader("조회 기간")
    st.selectbox("조회 기간", ["오늘", "이번 주", "이번 달"], label_visibility="collapsed")
    st.checkbox("취소·환불 숨기기")
    st.caption("v0.1 · 테스트 데이터")

# --- 헤더 ---
st.title("🛒 주문 관리")
st.caption("오늘 들어온 주문을 확인하고 배송 상태를 관리합니다.")

# --- 요약 ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("오늘 주문", 128)
col2.metric("결제 완료", 96, delta=12)
col3.metric("배송 준비", 18, delta=-3)
col4.metric("취소·환불", 6)

st.divider()

# --- 검색 ---
f1, f2, f3 = st.columns(3)
search = f1.text_input("검색", placeholder="주문번호 또는 상품명")
status = f2.selectbox("상태", ["전체"] + sorted(orders["상태"].unique()))
methods = f3.multiselect("결제수단", orders["결제수단"].unique(), default=list(orders["결제수단"].unique()))

filtered = orders.copy()
if search:
    filtered = filtered[
        filtered["주문번호"].str.contains(search, case=False)
        | filtered["상품명"].str.contains(search, case=False)
    ]
if status != "전체":
    filtered = filtered[filtered["상태"] == status]
if methods:
    filtered = filtered[filtered["결제수단"].isin(methods)]

st.caption(f"{len(filtered)}건 / 전체 {len(orders)}건 · 합계 {filtered['결제금액'].sum():,}원")
st.dataframe(filtered, use_container_width=True, hide_index=True)

st.divider()

# --- 현황 ---
chart_col, log_col = st.columns(2)

with chart_col:
    st.subheader("카테고리별 주문 수")
    st.bar_chart(orders["카테고리"].value_counts())

with log_col:
    st.subheader("오늘 배송 처리")
    st.progress(72, text="송장 등록 72%")
    st.info("결제 완료 96건 중 69건에 송장이 등록됐습니다.")
    st.warning("ORD-24086 은 무통장 입금이 확인되지 않았습니다.")
    with st.expander("최근 처리 로그 보기"):
        st.write("표시할 로그가 아직 없습니다.")

st.divider()

# --- 등록 ---
tab_register, tab_help = st.tabs(["새 상품 등록", "도움말"])

with tab_register:
    with st.form("new_product_form"):
        c1, c2 = st.columns(2)
        sku = c1.text_input("상품코드", placeholder="SKU-10293")
        name = c2.text_input("상품명", placeholder="보온 머그컵 350ml")

        c3, c4 = st.columns(2)
        category = c3.selectbox("카테고리", ["가전", "가구", "레저", "생활", "식품", "패션"])
        on_sale = c4.selectbox("판매 상태", ["판매중", "품절", "숨김"])

        c5, c6 = st.columns(2)
        price = c5.number_input("판매가(원)", min_value=0, step=100, value=19800)
        stock = c6.number_input("재고 수량", min_value=0, step=1, value=120)

        st.file_uploader("상품 이미지 (png · jpg)", type=["png", "jpg"])

        if st.form_submit_button("등록", type="primary"):
            st.success(f"'{name}' 상품이 등록되었습니다.")

with tab_help:
    st.write("주문 상태와 결제수단으로 필터링해 원하는 주문만 확인할 수 있습니다.")
