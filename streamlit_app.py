import streamlit as st
import random
import time

# 猫キャラクター画像URLサンプル（URLはご自身の画像に差し替えてください）
CAT_ICONS = {
    "normal": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_normal.png",
    "thinking": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_thinking.png",
    "happy": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_happy.png",
    "confused": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_confused.png",
    "play": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/cat_play.png",
    "yarn": "https://raw.githubusercontent.com/shuheisato-star/chatbot/main/assets/yarn.png",
}

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

st.set_page_config(page_title="猫キャラのドキュメントチャットボット", page_icon="🐾")
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

# Google Gemini APIキーの取得
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
uploaded_file = st.file_uploader("TXTファイルのみ対応（PDFは別途可）", type=["txt"])
if uploaded_file:
    doc_text = uploaded_file.read().decode("utf-8")
    st.session_state["doc_text"] = doc_text
    st.markdown(
        f"<div style='text-align:center'><img src='{CAT_ICONS['yarn']}' width='60'> 毛糸玉（ドキュメント）をゲット！</div>",
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
        f"<div style='text-align:center'><img src='{CAT_ICONS['play']}' width='120'></div>",
        unsafe_allow_html=True
    )
    st.info(neko_speak("そろそろ遊ぼうにゃ！", "play"))

st.markdown("---")
st.subheader("猫に質問してみよう！")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user
