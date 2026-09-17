from tkinter.font import BOLD

import streamlit as st
# from ui.theme import inject_css
import pathlib
import sys

st.set_page_config(page_title='Our Space', page_icon='💬', layout='wide')

st.title('💬 우리들의 공간')
st.caption('간단한 채팅과 게시글을 함께 사용하는 예제입니다.')

# st.session_state에 초기값 넣기 ---
if "messages" not in st.session_state:
    st.session_state.messages=[
        {'role':'assistant', 'content':'안녕하세요, 무엇을 도와드릴까요?'}
    ]

if 'posts' not in st.session_state:
    st.session_state.posts=[
        {
            'title':'이번 주말에 뭐 할까요'
            "content": "이번 주말에 근교 여행을 가려고 하는데, 추천해주실 만한 곳이 있을까요?",
            "time": "2025-06-10 10:24",
        },
        {
            "title": "반갑습니다!",
            "content": "안녕하세요. 잘 부탁드려요!",
            "time": "2025-06-10 10:18",
        },
        {
            "title": "맛집 추천",
            "content": "강남 근처에 괜찮은 점심 맛집 있나요? 추천 부탁드립니다!",
            "time": "2025-06-09 16:40",
        }
    ]

col_chat, col_board = st.columns(2)

# --- left: 채팅 ---

st.subheader('채팅하기')
st.chat_message('chat_message')
st.chat_input('메시지를 입력하세요')

st.divider()

st.subheader('게시글 목록')
st.text_input('제목', placeholder='제목을 입력하세요')
st.text_area('내용', placeholder='내용을 입력하세요')
st.button('게시글 등록')

# st.write('write')

# st.success('성공')
# st.warning('경고')