import streamlit as st
import random
import json

# 5つの戦略目標リスト
goals = [
    "人材",
    "産業競争力",
    "技術体系",
    "国際",
    "差し迫った危機への対処"
]

def generate_quiz(goals):
    # 正解をランダムに選ぶ
    correct_goal = random.choice(goals)
    # 不正解の選択肢をランダムに3つ選ぶ（重複なし）
    wrong_goals = random.sample([g for g in goals if g != correct_goal], 3)
    # 選択肢4つをシャッフル
    options = wrong_goals + [correct_goal]
    random.shuffle(options)
    # 問題文生成
    question = f"AI戦略2022における5つの戦略目標のうち、『{correct_goal}』はどの番号の戦略目標として設定されていますか？"
    # JSON形式で返す
    return {
        "question": question,
        "options": options,
        "answer": correct_goal
    }

st.title("AI戦略2022 クイズ")
st.write("5つの戦略目標から出題されます。正しい戦略目標を選んでください。")

if st.button("クイズを出題"):
    quiz_data = generate_quiz(goals)
    st.session_state["quiz_data"] = quiz_data
    st.session_state["user_answer"] = None

if "quiz_data" in st.session_state:
    quiz_data = st.session_state["quiz_data"]
    st.markdown(f"**問題：** {quiz_data['question']}")
    selected_option = st.selectbox("選択肢を選んでください", quiz_data["options"])
    if st.button("答え合わせ"):
        st.session_state["user_answer"] = selected_option

if "user_answer" in st.session_state and st.session_state["user_answer"] is not None:
    quiz_data = st.session_state["quiz_data"]
    user_answer = st.session_state["user_answer"]
    if user_answer == quiz_data["answer"]:
        st.success("正解！")
    else:
        st.error(f"不正解… 正解は「{quiz_data['answer']}」です。")
    # JSON形式でクイズデータを表示（開発・確認用）
    st.code(json.dumps(quiz_data, ensure_ascii=False, indent=2), language="json")
    # クイズデータ消去（次回出題用）
    del st.session_state["quiz_data"]
    del st.session_state["user_answer"]
