import streamlit as st
st.write("Hello World")
import streamlit as st
import openai

st.title("GPT-4.1-mini 응답 웹 앱")

# OpenAI API 키 입력
api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

# 질문 입력
user_question = st.text_area("질문을 입력하세요:")

# 버튼 클릭 시 응답 처리
if st.button("질문하기"):
    if not api_key:
        st.warning("API Key를 입력하세요.")
    elif not user_question:
        st.warning("질문을 입력하세요.")
    else:
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",  # 또는 "gpt-4.0" 또는 "gpt-4.1-mini" (사용자 API 제공 모델에 따라)
                messages=[
                    {"role": "user", "content": user_question}
                ],
                temperature=0.7
            )
            answer = response["choices"][0]["message"]["content"]
            st.success("응답:")
            st.write(answer)
        except Exception as e:
            st.error(f"오류 발생: {e}")
