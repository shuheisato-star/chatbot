import streamlit as st
import google.generativeai as genai

# fitz(Pymupdf)が使えるか判定
try:
    import fitz
    SUPPORT_PDF = True
except ImportError:
    SUPPORT_PDF = False

st.title("💬 ドキュメント連携型 Chatbot (Gemini 2.5 Flash 日本語対応)")

st.write(
    "ドキュメントをアップロードして、内容に関する質問ができます。"
    "また、要約・根拠表示・クイズ機能も利用できます。"
)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.info(
        "続行するには .streamlit/secrets.toml に GEMINI_API_KEY を設定してください。\n"
        "例:\n[GEMINI_API_KEY]\nGEMINI_API_KEY = \"your-api-key\"",
        icon="🗝️"
    )
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text(file):
    if SUPPORT_PDF and file.name.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    else:
        return file.read().decode("utf-8")

def get_summary_and_highlights(text):
    prompt = f"""
    以下はドキュメントです。内容の要約（300文字以内）と、重要ポイント・ハイライト（箇条書き）を日本語で出力してください。

    ドキュメント:
    {text}
    """
    response = model.generate_content(prompt)
    return response.candidates[0].content.parts[0].text

def get_answer_and_highlight(text, question):
    prompt = f"""
    以下のドキュメント内容に基づき、質問に日本語で答えてください。
    また、回答の根拠となる文（最大3つ）をドキュメントから抜き出し「根拠」として明示してください。

    ドキュメント:
    {text}

    質問:
    {question}
    """
    response = model.generate_content(prompt)
    answer = response.candidates[0].content.parts[0].text
    return answer

def generate_quiz_split(text, quiz_type="穴埋め", prev_score=None):
    quiz_prompt = f"""
    以下のドキュメントから{quiz_type}形式のクイズを1問、日本語で出題してください。
    必ず以下の形式で出力してください：

    問題: <問題文>
    正答: <正答>
    解説: <解説>

    ドキュメント:
    {text}
    """
    if prev_score is not None:
        quiz_prompt += f"\nユーザーの正答率は{prev_score*100:.0f}%です。おすすめの関連セクションも1つ推薦してください。"
    response = model.generate_content(quiz_prompt)
    output = response.candidates[0].content.parts[0].text
    # 問題・正答・解説に分割
    q, a, e = "", "", ""
    for line in output.splitlines():
        if line.startswith("問題:"):
            q = line.replace("問題:", "").strip()
        elif line.startswith("正答:"):
            a = line.replace("正答:", "").strip()
        elif line.startswith("解説:"):
            e = line.replace("解説:", "").strip()
    return q, a, e

# ドキュメントアップロード
file_types = ["txt"]
if SUPPORT_PDF:
    file_types.insert(0, "pdf")

uploaded_file = st.file_uploader(f"ドキュメントをアップロード（{'/'.join(file_types).upper()}）", type=file_types)
if uploaded_file:
    doc_text = extract_text(uploaded_file)
    st.session_state["doc_text"] = doc_text
    summary_highlights = get_summary_and_highlights(doc_text)
    st.subheader("ドキュメント要約 ＆ ハイライト")
    st.markdown(summary_highlights)
else:
    st.info(f"まずドキュメントをアップロードしてください。対応形式：{'/'.join(file_types).upper()}")
    st.stop()

# チャット履歴初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "今後の返答はすべて日本語でお願いします。"}
    ]

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = []
if "last_quiz" not in st.session_state:
    st.session_state.last_quiz = None
if "last_quiz_answer" not in st.session_state:
    st.session_state.last_quiz_answer = None
if "last_quiz_explain" not in st.session_state:
    st.session_state.last_quiz_explain = None

# これまでのメッセージ表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 質問入力
with st.expander("ドキュメント内容に質問する"):
    if prompt := st.chat_input("質問を入力してください"):
        prompt_with_lang = prompt + "\n日本語で答えてください。"
        st.session_state.messages.append({"role": "user", "content": prompt_with_lang})
        with st.chat_message("user"):
            st.markdown(prompt)

        response_text = get_answer_and_highlight(st.session_state["doc_text"], prompt_with_lang)
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

# クイズ機能
with st.expander("ドキュメントでクイズに挑戦！"):
    quiz_types = ["穴埋め", "正誤問題", "応用問題"]
    selected_quiz = st.selectbox("クイズ形式を選択", quiz_types)
    if st.button("クイズを出題"):
        prev_score = sum(st.session_state.quiz_score)/max(len(st.session_state.quiz_score),1) if st.session_state.quiz_score else None
        q, a, e = generate_quiz_split(st.session_state["doc_text"], selected_quiz, prev_score)
        st.session_state.last_quiz = q
        st.session_state.last_quiz_answer = a
        st.session_state.last_quiz_explain = e
        st.markdown(f"**問題：** {q}")
    # 問題が表示されているなら回答欄を表示
    if st.session_state.last_quiz:
        user_answer = st.text_input("あなたの答え（自分で答えてみてください）")
        if user_answer and st.button("答え合わせ"):
            # 正誤判定
            check_prompt = f"""
            以下はクイズの問題・正答・解説・ユーザー回答です。正誤判定と「正解/不正解」表示＋解説を日本語で出してください。

            問題: {st.session_state.last_quiz}
            正答: {st.session_state.last_quiz_answer}
            解説: {st.session_state.last_quiz_explain}
            ユーザー回答: {user_answer}
            """
            check_response = model.generate_content(check_prompt)
            result = check_response.candidates[0].content.parts[0].text
            st.markdown(result)
            if "正解" in result:
                st.session_state.quiz_score.append(1)
            else:
                st.session_state.quiz_score.append(0)
            st.session_state.last_quiz = None
            st.session_state.last_quiz_answer = None
            st.session_state.last_quiz_explain = None
