import streamlit as st
import google.generativeai as genai

# Show title and description.
st.title("💬 Chatbot (Gemini 2.5 Flash)")
st.write(
    "このチャットボットは Google Gemini 2.5 Flash モデルを利用して会話します。"
    "ご利用には Google API Key が必要です。[こちら](https://ai.google.dev/) から取得できます。"
    "また、Gemini APIの公式チュートリアルは [こちら](https://ai.google.dev/tutorials/python_quickstart) をご参照ください。"
)

# Ask user for their Google API key via `st.text_input`.
api_key = st.text_input("Google API Key", type="password")
if not api_key:
    st.info("続行するには Google API Key を入力してください。", icon="🗝️")
else:
    # Configure Gemini API client
    genai.configure(api_key=api_key)
    # Gemini 2.5 Flash モデル名（2024年6月現在）
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input field
    if prompt := st.chat_input("メッセージを入力してください"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare message history for Gemini
        history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            else:
                history.append({"role": "model", "parts": [m["content"]]})

        # Gemini API: Send prompt and stream response
        response_stream = model.generate_content(history, stream=True)

        with st.chat_message("assistant"):
            response = st.write_stream(response_stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
