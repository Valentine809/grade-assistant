# ========== 导入库 ==========
import streamlit as st
import requests
import json

# 🔴 在这里填你的API Key
API_KEY = "sk-cb5220420a0b4892bfbaa09452dbfaf4"

# ========== 页面设置 ==========
st.set_page_config(page_title="成绩分析小助手", page_icon="📊")
st.title("📊 成绩分析小助手")

# ========== 初始化 session_state ==========
if "step" not in st.session_state:
    st.session_state.step = "input"
    st.session_state.subjects = []
    st.session_state.scores = []
    st.session_state.full_marks = []
    st.session_state.messages = []
    st.session_state.count = 3

# ========== 第一步：输入科目数 ==========
if st.session_state.step == "input":
    st.write("输入你的各科成绩，AI帮你分析学习情况！")
    with st.form("input_form"):
        count = st.number_input("你这次考了几科？", min_value=1, max_value=10, step=1, value=3)
        submitted = st.form_submit_button("下一步")
        if submitted:
            st.session_state.count = count
            st.session_state.subjects = [""] * count
            st.session_state.scores = [0.0] * count
            st.session_state.full_marks = [100.0] * count
            st.session_state.step = "input_scores"
            st.rerun()

# ========== 第二步：输入科目名和成绩 ==========
elif st.session_state.step == "input_scores":
    st.write(f"请录入 **{st.session_state.count}** 科的成绩：")
    
    with st.form("score_form"):
        cols = st.columns(3)
        with cols[0]:
            st.write("**科目名称**")
        with cols[1]:
            st.write("**成绩**")
        with cols[2]:
            st.write("**满分**")
        
        for i in range(st.session_state.count):
            cols = st.columns(3)
            with cols[0]:
                name = st.text_input(
                    f"科目{i+1}", 
                    value=st.session_state.subjects[i],
                    key=f"subject_input_{i}"
                )
                st.session_state.subjects[i] = name
            with cols[1]:
                score = st.number_input(
                    f"成绩{i+1}", 
                    min_value=0.0, 
                    max_value=150.0, 
                    step=0.5,
                    value=st.session_state.scores[i],
                    key=f"score_input_{i}"
                )
                st.session_state.scores[i] = score
            with cols[2]:
                full = st.number_input(
                    f"满分{i+1}", 
                    min_value=0.5, 
                    max_value=150.0, 
                    step=0.5,
                    value=st.session_state.full_marks[i],
                    key=f"full_input_{i}"
                )
                st.session_state.full_marks[i] = full
        
        submitted = st.form_submit_button("确认录入")
        if submitted:
            if "" in st.session_state.subjects:
                st.warning("请完整填写所有科目名称！")
            else:
                st.session_state.step = "confirm"
                st.rerun()

# ========== 第三步：确认数据 ==========
elif st.session_state.step == "confirm":
    st.subheader("📋 你录入的成绩如下")
    data = []
    for i in range(len(st.session_state.subjects)):
        data.append({
            "科目": st.session_state.subjects[i],
            "成绩": st.session_state.scores[i],
            "满分": st.session_state.full_marks[i]
        })
    st.table(data)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 正确，开始分析", use_container_width=True):
            st.session_state.step = "analyzing"
            st.rerun()
    with col2:
        if st.button("🔄 重新录入", use_container_width=True):
            st.session_state.subjects = []
            st.session_state.scores = []
            st.session_state.full_marks = []
            st.session_state.messages = []
            st.session_state.step = "input"
            st.rerun()

# ========== 第四步：初次分析 ==========
elif st.session_state.step == "analyzing":
    st.info("🤖 正在向DeepSeek请教学习建议，请稍候...")
    
    subject_score_pairs = ""
    for i in range(len(st.session_state.subjects)):
        subject_score_pairs += f"{st.session_state.subjects[i]}: {st.session_state.scores[i]}/{st.session_state.full_marks[i]}分  "

    initial_prompt = f"""我这次考试成绩如下：
{subject_score_pairs}

请帮我分析：
1. 哪些科目是优势科目？
2. 哪些科目需要重点加强？
3. 给出3条具体、可操作的学习建议。
要求：语气鼓励，简洁有力，每条建议不超过30字。"""

    st.session_state.messages = [
        {"role": "system", "content": "你是一个温和、有经验的学习规划师，擅长帮学生分析成绩并给出建议。"},
        {"role": "user", "content": initial_prompt}
    ]

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": st.session_state.messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.step = "chatting"
        st.rerun()
    except Exception as e:
        st.error(f"❌ 调用失败：{e}")
        if st.button("🔙 返回重试"):
            st.session_state.step = "confirm"
            st.rerun()

# ========== 第五步：对话模式 ==========
elif st.session_state.step == "chatting":
    # 显示历史对话
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])

    # 底部输入框
    user_question = st.chat_input("💬 输入你的问题（比如：英语怎么提分？）")

    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                url = "https://api.deepseek.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "deepseek-chat",
                    "messages": st.session_state.messages,
                    "temperature": 0.7,
                    "max_tokens": 500
                }
                try:
                    response = requests.post(url, headers=headers, data=json.dumps(data))
                    result = response.json()
                    reply = result["choices"][0]["message"]["content"]
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.write(reply)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 出错了：{e}")

    # 侧边栏
    with st.sidebar:
        st.subheader("📊 当前成绩")
        data = []
        for i in range(len(st.session_state.subjects)):
            data.append({
                "科目": st.session_state.subjects[i],
                "成绩": st.session_state.scores[i],
                "满分": st.session_state.full_marks[i]
            })
        st.table(data)
        if st.button("🔄 重新开始"):
            for key in ["step", "subjects", "scores", "full_marks", "messages"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()