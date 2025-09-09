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
    "また、要約・根拠表示・クイズ（選択式正誤問題）機能も利用できます。"
)

api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyBkidm9uHDeyNq8IqBmJvZOgi6vz4DrSn8")
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

def generate_choice_quiz(text):
    prompt = f"""
    以下のドキュメントから「正誤問題（選択肢付き）」を1問、日本語で作成してください。
    必ず以下の形式で出力してください：

    問題: <問題文>
    選択肢:
    1. <選択肢1>
    2. <選択肢2>
    3. <選択肢3>
    4. <選択肢4>
    正答番号: <正答の番号>（例：2）
    解説: <解説>

    ドキュメント:
    {text}
    """
    response = model.generate_content(prompt)
    output = response.candidates[0].content.parts[0].text

    # 分割処理
    question, choices, correct_num, explanation = "", [], None, ""
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("問題:"):
            question = line.replace("問題:", "").strip()
        elif line.startswith("選択肢:"):
            continue
        elif any(line.startswith(f"{i}.") for i in range(1, 10)):
            choices.append(line[line.find(".")+1:].strip())
        elif line.startswith("正答番号:"):
            try:
                correct_num = int(line.replace("正答番号:", "").strip())
            except ValueError:
                correct_num = None
        elif line.startswith("解説:"):
            explanation = line.replace("解説:", "").strip()
    return question, choices, correct_num, explanation

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
if "last_quiz_data" not in st.session_state:
    st.session_state.last_quiz_data = None
if "last_quiz_selected" not in st.session_state:
    st.session_state.last_quiz_selected = None

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

# 正誤問題クイズ
with st.expander("ドキュメントで正誤問題クイズに挑戦！"):
    if st.button("クイズを出題"):
        question, choices, correct_num, explanation = generate_choice_quiz(st.session_state["doc_text"])
        st.session_state.last_quiz_data = (question, choices, correct_num, explanation)
        st.session_state.last_quiz_selected = None

    if st.session_state.last_quiz_data:
        question, choices, correct_num, explanation = st.session_state.last_quiz_data
        st.markdown(f"**問題：** {question}")
        selected_idx = st.selectbox("選択肢を選んでください", options=range(1, len(choices)+1), format_func=lambda x: f"{x}. {choices[x-1]}")
        if st.button("答え合わせ"):
            st.session_state.last_quiz_selected = selected_idx

    # 回答後の表示
    if st.session_state.last_quiz_selected:
        selected_idx = st.session_state.last_quiz_selected
        question, choices, correct_num, explanation = st.session_state.last_quiz_data
        if selected_idx == correct_num:
            st.success(f"正解！ ({selected_idx}. {choices[selected_idx-1]})")
            st.session_state.quiz_score.append(1)
        else:
            st.error(f"不正解… 正解は {correct_num}. {choices[correct_num-1]} です。")
            st.session_state.quiz_score.append(0)
        st.info(f"解説: {explanation}")
        # クイズデータ消去
        st.session_state.last_quiz_data = None
        st.session_state.last_quiz_selected = None
