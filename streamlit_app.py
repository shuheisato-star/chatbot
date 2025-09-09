import streamlit as st
import random
import time

# PDF抽出用
try:
    import fitz  # PyMuPDF
    SUPPORT_PDF = True
except ImportError:
    SUPPORT_PDF = False

# 猫画像: 添付画像（ローカル保存 or Web公開URLを推奨）
CAT_IMAGE_PATH = "cat_image2.png"  # 添付画像を同じディレクトリに保存してください

GOALS = [
    "人材",
    "産業競争力",
    "技術体系",
    "国際",
    "差し迫った危機への対処"
]

def neko_speak(text, mode="normal"):
    if mode == "happy":
        return f"にゃるほど！{text} ……だにゃ！"
    elif mode == "confused":
        return f"うーん、{text} ……ちょっと難しいにゃ。"
    elif mode == "thinking":
        return f"ちょっと待ってにゃ。{text}"
    elif mode == "play":
        return f"そろそろ遊びたいにゃ〜！{text}"
    else:
        return f"{text} ……だにゃ。"

def extract_text(file):
    if SUPPORT_PDF and file.name.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    else:
        return file.read().decode("utf-8")

st.set_page_config(page_title="猫キャラのドキュメントチャットボット", page_icon="🐾")
st.markdown(
    "<h1 style='text-align: center;'>🐾 猫キャラのドキュメントチャットボット</h1>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='text-align:center'><img src='data:image/png;base64,{st.image(CAT_IMAGE_PATH, use_column_width=False, output_format='auto', clamp=True).image_to_bytes().decode() if hasattr(st, 'image_to_bytes') else ''}' width='160'></div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='text-align:center;font-size:20px;'>猫と一緒にドキュメントを探検しよう！</div>",
    unsafe_allow_html=True
)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.warning("APIキーが設定されていません。`.streamlit/secrets.toml` に `GEMINI_API_KEY` を記載してください。")
    st.stop()

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

st.subheader("毛糸玉（ドキュメント）をアップロードしてにゃ")
file_types = ["txt"]
if SUPPORT_PDF:
    file_types.insert(0, "pdf")
uploaded_file = st.file_uploader(f"{'PDF/TXT' if SUPPORT_PDF else 'TXT'}ファイルのみ対応", type=file_types)
if uploaded_file:
    doc_text = extract_text(uploaded_file)
    st.session_state["doc_text"] = doc_text
    st.markdown(
        f"<div style='text-align:center;font-size:24px;'>毛糸玉（ドキュメント）をゲット！</div>",
        unsafe_allow_html=True
    )
    # Geminiによる要約
    if GEMINI_AVAILABLE:
        try:
            prompt = f"このドキュメントの要約を猫語で100文字以内で書いてください。"
            response = model.generate_content(prompt + "\n\n" + doc_text[:2000])
            summary = response.candidates[0].content.parts[0].text
        except Exception:
            summary = doc_text[:150] + "..." + doc_text[-50:]
    else:
        summary = doc_text[:150] + "..." + doc_text[-50:]
    st.markdown(f"<div style='background:#f4f0e6;padding:10px;border-radius:10px'><b>猫のひとこと要約:</b> <br>{neko_speak(summary, 'happy')}</div>", unsafe_allow_html=True)
else:
    st.info("まず毛糸玉（ドキュメント）をアップロードしてにゃ。")
    st.stop()

if "last_action_time" not in st.session_state:
    st.session_state["last_action_time"] = time.time()
if time.time() - st.session_state["last_action_time"] > 120:
    st.markdown(
        f"<div style='text-align:center'><img src='{CAT_IMAGE_PATH}' width='160'></div>",
        unsafe_allow_html=True
    )
    st.info(neko_speak("そろそろ遊ぼうにゃ！", "play"))

st.markdown("---")
st.subheader("猫に質問してみよう！")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_question = st.text_input("猫に聞きたいことを入力してにゃ", key="chat_input")
if user_question:
    st.session_state["last_action_time"] = time.time()
    st.session_state["chat_history"].append(("user", user_question))
    st.markdown(
        f"<div style='text-align:center'><img src='{CAT_IMAGE_PATH}' width='160'></div>",
        unsafe_allow_html=True
    )
    # Geminiによる回答生成
    if GEMINI_AVAILABLE:
        try:
            prompt = f"""
            あなたは猫キャラクターです。ユーザーの質問に必ず猫語（語尾に「にゃ」など）で答えてください。回答はドキュメント内容に基づいてください。
            ドキュメント: {st.session_state['doc_text'][:2000]}
            質問: {user_question}
            """
            response = model.generate_content(prompt)
            answer = response.candidates[0].content.parts[0].text
            answer_mode = "happy"
        except Exception:
            answer = neko_speak("APIリソース制限またはエラーが発生したにゃ。時間を空けて再度お試しくださいにゃ。", "confused")
            answer_mode = "confused"
    else:
        answer_mode = "happy" if any(word in st.session_state["doc_text"] for word in user_question.split()) else "confused"
        if answer_mode == "happy":
            answer = neko_speak("ドキュメントから見つけたよ！「" + user_question + "」についてはこう書かれてるにゃ：\n\n" + st.session_state["doc_text"][:100] + "…", "happy")
        else:
            answer = neko_speak("ごめんにゃ、ちょっと分からないにゃ…別の聞き方をしてみてほしいにゃ。", "confused")
    st.session_state["chat_history"].append(("cat", answer))
    st.markdown(
        f"<div style='text-align:center'><img src='{CAT_IMAGE_PATH}' width='160'></div>",
        unsafe_allow_html=True
    )
    st.markdown(f"<div style='background:#fff7e6;padding:10px;border-radius:10px'>{answer}</div>", unsafe_allow_html=True)

if st.session_state["chat_history"]:
    st.markdown("---")
    st.subheader("これまでの猫とのやりとり")
    for who, msg in st.session_state["chat_history"]:
        if who == "user":
            st.markdown(f"<div style='background:#e6f7ff;padding:8px;border-radius:8px'>🧑‍💻 {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#fff7e6;padding:8px;border-radius:8px'>🐱 {msg}</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("猫のクイズタイム！")

def generate_strategy_quiz(goals):
    correct_goal = random.choice(goals)
    wrong_goals = random.sample([g for g in goals if g != correct_goal], 3)
    options = wrong_goals + [correct_goal]
    random.shuffle(options)
    question = f"『{correct_goal}』はAI戦略2022の5つの戦略目標のうちどれにゃ？"
    return {
        "question": question,
        "options": options,
        "answer": correct_goal
    }

if st.button("クイズを出題してにゃ"):
    quiz_data = generate_strategy_quiz(GOALS)
    st.session_state["quiz"] = quiz_data
    st.session_state["quiz_selected"] = None

if "quiz" in st.session_state and st.session_state["quiz"]:
    quiz_data = st.session_state["quiz"]
    st.markdown(f"<div style='background:#e6f7ff;padding:8px;border-radius:8px'><b>問題:</b> {quiz_data['question']}</div>", unsafe_allow_html=True)
    selected = st.selectbox("選択肢を選んでにゃ", quiz_data["options"], key="quiz_select")
    if st.button("答え合わせするにゃ"):
        st.session_state["quiz_selected"] = selected

if "quiz_selected" in st.session_state and st.session_state["quiz_selected"]:
    quiz_data = st.session_state["quiz"]
    selected = st.session_state["quiz_selected"]
    if selected == quiz_data["answer"]:
        st.markdown(
            f"<div style='text-align:center'><img src='{CAT_IMAGE_PATH}' width='160'></div>",
            unsafe_allow_html=True
        )
        st.success(neko_speak("正解だにゃ！お見事にゃ！", "happy"))
    else:
        st.markdown(
            f"<div style='text-align:center'><img src='{CAT_IMAGE_PATH}' width='160'></div>",
            unsafe_allow_html=True
        )
        st.error(neko_speak(f"残念…正解は「{quiz_data['answer']}」だったにゃ。", "confused"))
    st.info(neko_speak("AI戦略2022の5つの目標は「人材」「産業競争力」「技術体系」「国際」「差し迫った危機への対処」だにゃ。", "normal"))
    st.session_state["quiz"] = None
    st.session_state["quiz_selected"] = None

st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:13px;color:#888'>Powered by 猫キャラBot 🐾</div>",
    unsafe_allow_html=True
)
