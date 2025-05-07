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
