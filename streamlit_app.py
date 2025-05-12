import streamlit as st
import openai

# API 키 입력 받기 (비밀번호 형식)
api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

# session_state에 저장
if api_key:
    st.session_state["api_key"] = api_key

# 질문 입력
question = st.text_input("질문을 입력하세요")

# GPT 호출 함수 - 캐시 적용
@st.cache_data(show_spinner="GPT에게 묻는 중...")
def get_gpt_response(api_key, user_input):
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content

# 응답 출력
if st.button("응답 받기") and "api_key" in st.session_state and question:
    with st.spinner("GPT가 생각 중..."):
        answer = get_gpt_response(st.session_state["api_key"], question)
        st.write("💬 GPT의 응답:")
        st.success(answer)

import streamlit as st
import openai

# 페이지 구성
st.set_page_config(page_title="GPT Chat", layout="centered")
st.title("🧠 GPT ChatBot")

# --- API 키 입력 ---
api_key = st.text_input("🔑 OpenAI API Key 입력", type="password")
if api_key:
    st.session_state["api_key"] = api_key

# --- 대화 기록 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Clear 버튼 ---
if st.button("🧹 Clear"):
    st.session_state.messages = []
    st.success("대화가 초기화되었습니다.")

# --- 질문 입력 ---
user_input = st.chat_input("메시지를 입력하세요")

# --- 메시지 표시 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- GPT 응답 처리 ---
if user_input and "api_key" in st.session_state:
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # GPT 응답
    try:
        client = openai.OpenAI(api_key=st.session_state["api_key"])
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=st.session_state.messages,
        )
        reply = response.choices[0].message.content

        # GPT 메시지 저장 및 표시
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
