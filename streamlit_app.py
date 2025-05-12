import streamlit as st
import openai
import tempfile

# ✅ 페이지 설정
st.set_page_config(page_title="GPT 챗봇 통합", layout="centered")
st.title("🤖 GPT 챗봇 통합 페이지")

# ✅ OpenAI API Key 입력
api_key = st.text_input("🔑 OpenAI API Key를 입력하세요", type="password")
if api_key:
    st.session_state["api_key"] = api_key

# ✅ 도서관 규정 불러오기
@st.cache_data
def load_rules():
    try:
        with open("library_rules.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "도서관 규정 파일을 찾을 수 없습니다."

library_rules = load_rules()

# ✅ 탭 구성
tab1, tab2, tab3 = st.tabs(["🧠 일반 GPT 챗봇", "📚 부경대 도서관 챗봇", "📄 ChatPDF 챗봇"])

# ---------------------------- 1. 일반 챗봇 ----------------------------
with tab1:
    st.subheader("🧠 GPT-4.1-mini 일반 챗봇")

    if "chat_history_general" not in st.session_state:
        st.session_state.chat_history_general = []

    user_input = st.text_input("💬 질문을 입력하세요 (일반)", key="general_input")

    @st.cache_data(show_spinner="GPT에게 묻는 중...")
    def get_gpt_response(api_key, messages):
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )
        return response.choices[0].message.content

    if st.button("일반 챗봇 응답 받기") and user_input and "api_key" in st.session_state:
        st.session_state.chat_history_general.append({"role": "user", "content": user_input})
        reply = get_gpt_response(api_key, st.session_state.chat_history_general)
        st.session_state.chat_history_general.append({"role": "assistant", "content": reply})

    if st.button("🔄 일반 챗봇 초기화"):
        st.session_state.chat_history_general = []

    st.write("### 💬 일반 챗봇 대화 내용")
    for msg in st.session_state.chat_history_general:
        speaker = "👤 사용자" if msg["role"] == "user" else "🤖 GPT"
        st.markdown(f"**{speaker}:** {msg['content']}")

# ---------------------------- 2. 도서관 챗봇 ----------------------------
with tab2:
    st.subheader("📚 부경대 도서관 챗봇")

    if "chat_history_library" not in st.session_state:
        st.session_state.chat_history_library = []

    question = st.text_input("✏️ 도서관 관련 질문을 입력하세요", key="library_input")

    @st.cache_data(show_spinner="도서관 챗봇이 답변 중입니다...")
    def ask_library_bot(api_key, question, rules):
        client = openai.OpenAI(api_key=api_key)
        system_prompt = (
            "당신은 국립부경대학교 도서관 규정을 잘 아는 도서관 챗봇입니다.\n"
            "아래 규정을 참고하여 사용자 질문에 답변하세요.\n\n"
            f"[도서관 규정]\n{rules}"
        )
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content

    if st.button("도서관 챗봇 응답 받기") and question:
        answer = ask_library_bot(api_key, question, library_rules)
        st.session_state.chat_history_library.append(("👤 사용자", question))
        st.session_state.chat_history_library.append(("🤖 챗봇", answer))

    if st.button("🔄 도서관 챗봇 초기화"):
        st.session_state.chat_history_library = []

    st.write("### 💬 도서관 챗봇 대화 내용")
    for speaker, msg in st.session_state.chat_history_library:
        st.markdown(f"**{speaker}:** {msg}")

# ---------------------------- 3. ChatPDF 챗봇 ----------------------------
with tab3:
    st.subheader("📄 ChatPDF 기반 챗봇")

    # 파일 업로드
    uploaded_file = st.file_uploader("📎 PDF 파일을 업로드하세요", type="pdf")

    if "pdf_file_id" not in st.session_state:
        st.session_state["pdf_file_id"] = None

    # 파일 업로드 처리
    if uploaded_file and api_key:
        client = openai.OpenAI(api_key=api_key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # 업로드 및 파일 ID 저장
        with open(tmp_path, "rb") as f:
            file = client.files.create(file=f, purpose="assistants")
            st.session_state["pdf_file_id"] = file.id
            st.success(f"✅ 파일 업로드 완료! 파일 ID: {file.id}")

    # 질문 입력
    pdf_question = st.text_input("📖 PDF에 대해 질문하세요")

    if pdf_question and st.session_state.get("pdf_file_id"):
        st.write("질문 처리 중...")

        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 업로드된 PDF를 바탕으로 질문에 답하는 전문가입니다."
                },
                {"role": "user", "content": pdf_question}
            ],
            tools=[{"type": "file_search"}],
            tool_choice="auto",
            file_ids=[st.session_state["pdf_file_id"]]
        )
        st.markdown("**🤖 GPT 응답:**")
        st.write(response.choices[0].message.content)

    # 벡터 스토어 초기화
    if st.button("🧹 Clear PDF 파일"):
        if st.session_state.get("pdf_file_id"):
            client.files.delete(st.session_state["pdf_file_id"])
            st.success("📁 업로드된 PDF 파일이 삭제되었습니다.")
            st.session_state["pdf_file_id"] = None
