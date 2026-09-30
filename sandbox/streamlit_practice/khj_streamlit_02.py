import datetime
import streamlit as st

st.set_page_config(page_title="퍼스트존 관리자", page_icon="🛒", layout="wide")

# 주문 데이터
orders = [
    {"주문번호": "ORD-24081", "주문일시": "08-12 09:14", "고객": "김민준", "상품명": "무선 이어폰 프로", "카테고리": "가전", "수량": 1, "결제금액": 129000, "상태": "결제 완료", "결제수단": "카드"},
    {"주문번호": "ORD-24082", "주문일시": "08-12 09:41", "고객": "이서연", "상품명": "캠핑 체어 2인용", "카테고리": "레저", "수량": 2, "결제금액": 98000, "상태": "배송 준비", "결제수단": "카드"},
    {"주문번호": "ORD-24083", "주문일시": "08-12 10:02", "고객": "박도윤", "상품명": "원두 1kg 다크로스트", "카테고리": "식품", "수량": 3, "결제금액": 42000, "상태": "배송 중", "결제수단": "간편결제"},
    {"주문번호": "ORD-24084", "주문일시": "08-12 10:35", "고객": "최지우", "상품명": "USB-C 충전기 65W", "카테고리": "가전", "수량": 1, "결제금액": 34000, "상태": "결제 완료", "결제수단": "간편결제"},
    {"주문번호": "ORD-24085", "주문일시": "08-12 11:08", "고객": "정하은", "상품명": "러닝화 270", "카테고리": "패션", "수량": 1, "결제금액": 89000, "상태": "취소", "결제수단": "카드"},
    {"주문번호": "ORD-24086", "주문일시": "08-12 11:22", "고객": "강시우", "상품명": "우드 식탁 4인", "카테고리": "가구", "수량": 1, "결제금액": 320000, "상태": "배송 준비", "결제수단": "무통장"},
    {"주문번호": "ORD-24087", "주문일시": "08-12 12:01", "고객": "윤아름", "상품명": "린넨 셔츠 화이트", "카테고리": "패션", "수량": 2, "결제금액": 56000, "상태": "배송 완료", "결제수단": "카드"},
    {"주문번호": "ORD-24088", "주문일시": "08-12 12:44", "고객": "임준호", "상품명": "텀블러 500ml", "카테고리": "생활", "수량": 4, "결제금액": 28000, "상태": "환불", "결제수단": "간편결제"},
]

# 사이드바
st.sidebar.title("퍼스트존 관리자")
st.sidebar.caption("피카츄 운영팀")
st.sidebar.write("---")

menu = st.sidebar.radio("메뉴", ["대시보드", "주문 관리", "상품 관리", "정산"], index=1)
st.sidebar.write("---")

period = st.sidebar.selectbox("조회 기간", ["오늘", "이번 주", "이번 달"])
hide_cancel = st.sidebar.checkbox("취소/환불 숨기기")
st.sidebar.caption("v0.1 테스트 데이터")

# 제목
st.title("🛒 주문 관리")
st.write("오늘 들어온 주문을 확인하고 배송 상태를 관리합니다.")

# 요약
col1, col2, col3, col4 = st.columns(4)
col1.metric("오늘 주문", 128)
col2.metric("결제 완료", 96, 12)
col3.metric("배송 준비", 18, -3)
col4.metric("취소/환불", 6)

st.write("---") # 주문 데이터 테이블로

# 검색&필터
col1, col2, col3 = st.columns(3)
search = col1.text_input("검색", placeholder="주문번호 또는 상품명")
status = col2.selectbox("상태", ["전체", "결제 완료", "배송 준비", "배송 중", "배송 완료", "취소", "환불"])
methods = col3.multiselect("결제수단", ["카드", "간편결제", "무통장"], default=["카드", "간편결제", "무통장"])

# 필터
filtered = []
total = 0
for o in orders:
    if search != "" and search not in o["주문번호"] and search not in o["상품명"]:
        continue
    if status != "전체" and o["상태"] != status:
        continue
    if o["결제수단"] not in methods:
        continue
    filtered.append(o)
    total = total + o["결제금액"]

st.write(str(len(filtered)) + "건 / 전체 " + str(len(orders)) + "건 / 합계 " + str(total) + "원")
st.table(filtered)

st.write("---") # 중간 차트

col1, col2 = st.columns(2)

with col1:
    st.subheader("카테고리별 주문 수")
    cat_count = {}  # 카테고리 개수 세기
    for o in orders:
        cat = o["카테고리"]
        if cat in cat_count:
            cat_count[cat] = cat_count[cat] + 1
        else:
            cat_count[cat] = 1
    st.bar_chart(cat_count)

with col2:
    st.subheader("오늘 배송 처리")
    st.progress(72)
    st.write("송장 등록 72%")
    st.info("결제 완료 96건 중 69건에 송장이 등록됐습니다.")
    st.warning("ORD-24086 은 무통장 입금이 확인되지 않았습니다.")
    show_log = st.checkbox("최근 처리 로그 보기")
    if show_log:
        st.write("표시할 로그가 아직 없습니다.")

st.write("---") # 최하단 입력란

st.subheader("새 상품 등록")
sku = st.text_input("상품코드", placeholder="SKU-10293")
name = st.text_input("상품명", placeholder="보온 머그컵 350ml")
category = st.selectbox("카테고리", ["가전", "가구", "레저", "생활", "식품", "패션"])
sale_status = st.selectbox("판매 상태", ["판매중", "품절", "숨김"])
price = st.number_input("판매가(원)", min_value=0, value=19800)
stock = st.number_input("재고 수량", min_value=0, value=120)
img = st.file_uploader("상품 이미지 (png, jpg)", type=["png", "jpg"])

if st.button("등록"):
    if name == "":
        st.warning("상품명을 입력해주세요.")
    else:
        st.success(name + " 상품이 등록되었습니다.")