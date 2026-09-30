from __future__ import annotations
import streamlit as st
from core import api_client
from ui.card import page_header

def render()->None:
    # 
    page_header('AI helper', subtitle='the responds are based on the company rule')
    # 
    if 'chat' not in st.session_state:
        st.session_state['chat']=[]
    # 기존 대화내용 화면에 출력
    for message in st.session_state['chat']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # 채팅 입력창 생성
    question=st.chat_input('How may I help you?')
    if not question:
        return
    # 대화 내역에 질문 추가
    st.session_state['chat'].append({'role':'user', 'content':question})
    # 질문 화면에 출력
    with st.chat_message('user'):
        st.markdown(question)
    # 답변 화면에 출력
    with st.chat_message('assistant'):
        with st.spinner('looking up the company rules...'):
            # 백엔드에 질문 주고 답변 요청
            try:
                response=api_client.ask(question)
            except api_client.ApiError as e:
                st.error(str(e))
                return
        # 답변 화면에 띄우기
        answer=response.get('answer','')
        st.markdown(answer)
    # 대화 내역에 답변 추가
    st.session_state['chat'].append({'role':'assistant','content':answer})