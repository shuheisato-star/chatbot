import streamlit as st
import random
import time

# 猫キャラクター画像URLサンプル（SVG/PNG。好みに合わせて差し替え可）
CAT_ICONS = {
    "normal": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_normal.png",        # 通常
    "thinking": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_thinking.png",    # 集中
    "happy": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_happy.png",          # ひらめき
    "confused": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_confused.png",    # 困惑
    "play": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_play.png",            # 遊んでほしい
    "yarn": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/yarn.png",                # 毛糸玉
}

# 戦略目標リスト
GOALS = [
    "人材",
    "産業競争力",
    "技術体系",
    "国際",
    "差し迫った危機への対処"
]

# --- 猫語変換ヘルパー ---
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

# --- UIヘッダー ---
st.markdown(
    "<h1 style='text-align: center;'>🐾 猫キャラのドキュメントチャットボット</h1>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='text-align:center'><img src='{CAT_ICONS['normal']}' width='120'></div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='text-align:center;font-size:20px;'>猫と一緒にドキュメントを探検しよう！</div>",
    unsafe_allow_html=True
)

# --- ドキュメントアップロード ---
st.subheader("毛糸玉（ドキュメント）をアップロードしてにゃ")
uploaded_file = st.file_uploader("TXTファイルのみ対応（PDFは別途可）", type=["txt"])
if uploaded_file:
    doc_text = uploaded_file.read().decode("utf-8")
    st.session_state["doc_text"] = doc_text
    st.markdown(
        f"<div style='text-align:center'><img src='{CAT_ICONS['yarn']}' width='60'> 毛糸玉（ドキュメント）をゲット！</div>",
        unsafe_allow_html=True
    )
    # 要約生成（簡易：先頭150文字＋末尾50文字）
    summary = doc_text[:150] + "..." + doc_text[-50:]
    st.markdown(f"<div style='background:#f4f0e6;padding:10px;border-radius:10px'><b>猫のひとこと要約:</b> <br>{neko_speak(summary, 'happy')}</div>", unsafe_allow_html=True)
else:
    st.info("まず毛糸玉（ドキュメント）をアップロードしてにゃ。")
    st.stop()

# --- 「遊んでほしい猫」表示（操作がない場合） ---
if "last_action_time" not in st.session_state:
    st.session_state["last_action_time"] = time.time()
if time.time() - st.session_state["last_action_time"] > 120:
    st.markdown(
        f"<div style='text-align:center'><img src='{CAT_ICONS['play']}' width='120'></div>",
        unsafe_allow_html=True
    )
    st.info(neko_speak("そろそろ遊ぼうにゃ！", "play"))

# --- チャットQA ---
st.markdown("---")
st.subheader("猫に質問してみよう！")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_question = st.text_input("猫に聞きたいことを入力してにゃ", key="chat_input")
if user_question:
    st.session_state["last_action_time"] = time.time()
    st.session_state["chat_history"].append(("user", user_question))
    # 疑似的に猫が「考えている」画像表示
    st.markdown(
        f"<div style='text-align:center'><img src='{CAT_ICONS['thinking']}' width='120'></div>",
        unsafe_allow_html=True
    )
    # 回答生成（簡易：ドキュメント本文から関連語を抽出する擬似実装）
    answer_mode = "happy" if any(word in doc_text for word in user_question.split()) else "confused"
    if answer_mode == "happy":
        answer = neko_speak("ドキュメントから見つけたよ！「" + user_question + "」についてはこう書かれてるにゃ：\n\n" + doc_text[:100] + "…", "happy")
        st.session_state["chat_history"].append(("cat", answer))
        st.markdown(
            f"<div style='text-align:center'><img src='{CAT_ICONS['happy']}' width='120'></div>",
            unsafe_allow_html=True
        )
    else:
        answer = neko_speak("ごめんにゃ、ちょっと分からないにゃ…別の聞き方をしてみてほしいにゃ。", "confused")
        st.session_state["chat_history"].append(("cat", answer))
        st.markdown(
            f"<div style='text-align:center'><img src='{CAT_ICONS['confused']}' width='120'></div>",
            unsafe_allow_html=True
        )
    st.markdown(f"<div style='background:#fff7e6;padding:10px;border-radius:10px'>{answer}</div>", unsafe_allow_html=True)

# 履歴表示
if st.session_state["chat_history"]:
    st.markdown("---")
    st.subheader("これまでの猫とのやりとり")
    for who, msg in st.session_state["chat_history"]:
        if who == "user":
            st.markdown(f"<div style='background:#e6f7ff;padding:8px;border-radius:8px'>🧑‍💻 {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#fff7e6;padding:8px;border-radius:8px'>🐱 {msg}</div>", unsafe_allow_html=True)

# --- クイズ（戦略目標選択式） ---
st.markdown("---")
st.subheader("猫のクイズタイム！")
if st.button("クイズを出題してにゃ"):
    # 正解目標をランダム選択
    correct_goal = random.choice(GOALS)
    wrong_goals = random.sample([g for g in GOALS if g != correct_goal], 3)
    options = wrong_goals + [correct_goal]
    random.shuffle(options)
    question = f"『{correct_goal}』はAI戦略2022の5つの戦略目標のうちどれにゃ？"
    # 保持
    st.session_state["quiz"] = {
        "question": question,
        "options": options,
        "answer": correct_goal
    }
    st.session_state["quiz_selected"] = None

# クイズ表示
if "quiz" in st.session_state and st.session_state["quiz"]:
    q = st.session_state["quiz"]
    st.markdown(f"<div style='background:#e6f7ff;padding:8px;border-radius:8px'><b>問題:</b> {q['question']}</div>", unsafe_allow_html=True)
    selected = st.selectbox("選択肢を選んでにゃ", q["options"], key="quiz_select")
    if st.button("答え合わせするにゃ"):
        st.session_state["quiz_selected"] = selected

# クイズ答え合わせ
if "quiz_selected" in st.session_state and st.session_state["quiz_selected"]:
    q = st.session_state["quiz"]
    selected = st.session_state["quiz_selected"]
    if selected == q["answer"]:
        st.markdown(
            f"<div style='text-align:center'><img src='{CAT_ICONS['happy']}' width='120'></div>",
            unsafe_allow_html=True
        )
        st.success(neko_speak("正解だにゃ！お見事にゃ！", "happy"))
    else:
        st.markdown(
            f"<div style='text-align:center'><img src='{CAT_ICONS['confused']}' width='120'></div>",
            unsafe_allow_html=True
        )
        st.error(neko_speak(f"残念…正解は「{q['answer']}」だったにゃ。", "confused"))
    # 解説
    st.info(neko_speak("AI戦略2022の5つの目標は「人材」「産業競争力」「技術体系」「国際」「差し迫った危機への対処」だにゃ。", "normal"))
    # クイズ履歴消去
    st.session_state["quiz"] = None
    st.session_state["quiz_selected"] = None

# --- フッター ---
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:13px;color:#888'>Powered by 猫キャラBot 🐾</div>",
    unsafe_allow_html=True
)
