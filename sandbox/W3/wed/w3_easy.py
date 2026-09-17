import datetime

import streamlit as st

st.set_page_config(page_title="Our Space", page_icon="💬", layout="wide")

st.title("💬 우리들의 공간")
st.caption("간단한 채팅과 게시글을 함께 사용하는 예제입니다.")

# session_state에 없으면 처음에만 초기값 넣기
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]
if "posts" not in st.session_state:
    st.session_state.posts = [
        {
            "title": "이번 주말에 뭐 할까요?",
            "content": "이번 주말에 근교 여행을 가려고 하는데, 추천해주실 만한 곳이 있을까요?",
            "time": "2025-06-10 10:24",
        },
        {
            "title": "반갑습니다!",
            "content": "안녕하세요. 잘 부탁드려요!",
            "time": "2025-06-10 10:18",
        },
    ]

col_chat, col_board = st.columns(2)

# ---------------- 왼쪽: 채팅 ----------------
with col_chat:
    st.subheader("💬 채팅하기")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        answer = f"'{prompt}'에 대한 답변입니다! 좋은 하루 되세요 😊"
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()  # 새 메시지를 바로 화면에 반영

st.divider()  # 두 컬럼 사이 구분선 (세로 배치 시), 모바일 폭에서 특히 유용

# ---------------- 오른쪽: 게시글 목록 ----------------
with col_board:
    st.subheader("📋 게시글 목록")

    title = st.text_input("제목", placeholder="제목을 입력하세요")
    content = st.text_area("내용", placeholder="내용을 입력하세요")

    if st.button("게시글 등록", type="primary", use_container_width=True):
        if title and content:
            st.session_state.posts.insert(
                0,
                {
                    "title": title,
                    "content": content,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                },
            )
            st.success("게시글이 등록되었습니다!")
        else:
            st.warning("제목과 내용을 모두 입력해주세요.")

    st.divider()

    for i, post in enumerate(st.session_state.posts, start=1):
        st.markdown(f"**{i}. {post['title']}**")
        st.write(post["content"])
        st.caption(post["time"])
