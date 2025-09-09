import streamlit as st
import google.generativeai as genai

st.title("💬 Chatbot (Gemini 2.5 Flash 日本語対応)")
st.write(
    "このチャットボットは Google Gemini 2.5 Flash モデルを利用し、日本語で会話します。"
    "Google API Key が必要です。[取得はこちら](https://ai.google.dev/)。"
)

api_key = st.text_input("Google API Key", type="password")
if not api_key:
    st.info("続行するには Google API Key を入力してください。", icon="🗝️")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # セッションに会話履歴を保存（日本語指示を最初に追加）
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": "今後の返答はすべて日本語でお願いします。"}
        ]

    # これまでのメッセージを表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください"):
        # 各質問にも日本語指示文を追加（より確実に日本語返答のため）
        prompt_with_lang = prompt + "\n日本語で答えてください。"
        st.session_state.messages.append({"role": "user", "content": prompt_with_lang})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini 2.5 Flash へ問い合わせ（str型で渡す）
        response = model.generate_content(prompt_with_lang)

        # 返答本文のみ抽出して表示
        response_text = response.candidates[0].content.parts[0].text
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
