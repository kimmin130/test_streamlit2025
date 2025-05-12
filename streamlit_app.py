import streamlit as st
import openai

# ✅ 페이지 설정: 항상 최상단에 위치해야 함!
st.set_page_config(page_title="GPT Chat", layout="centered")

st.title("🧠 GPT-4.1-mini 챗봇")

# ✅ OpenAI API Key 입력 받기
api_key = st.text_input("🔑 OpenAI API Key를 입력하세요", type="password")
if api_key:
    st.session_state["api_key"] = api_key

# ✅ 이전 대화 불러오기 or 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ 입력창: 질문
user_input = st.text_input("💬 질문을 입력하세요")

# ✅ GPT 응답 생성 함수 (캐싱)
@st.cache_data(show_spinner="GPT에게 묻는 중...")
def get_gpt_response(api_key, messages):
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )
    return response.choices[0].message.content

# ✅ "응답 받기" 버튼 동작
if st.button("응답 받기") and user_input and "api_key" in st.session_state:
    # 기존 대화에 사용자 질문 추가
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # GPT 응답 생성
    gpt_reply = get_gpt_response(st.session_state["api_key"], st.session_state.chat_history)

    # GPT 응답도 대화 히스토리에 추가
    st.session_state.chat_history.append({"role": "assistant", "content": gpt_reply})

# ✅ Clear 버튼: 대화 초기화
if st.button("🔄 대화 초기화"):
    st.session_state.chat_history = []

# ✅ 대화 내용 출력
st.write("### 🗨️ 대화 내용")
for msg in st.session_state.chat_history:
    speaker = "👤 사용자" if msg["role"] == "user" else "🤖 GPT"
    st.markdown(f"**{speaker}:** {msg['content']}")
