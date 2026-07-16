# ========== 导入库 ==========
import streamlit as st
import requests
import json

# 🔴 在这里填你的API Key
API_KEY = "sk-cb5220420a0b4892bfbaa09452dbfaf4"

# ========== 页面设置 ==========
st.set_page_config(page_title="成绩分析小助手", page_icon="📊")
st.title("📊 成绩分析小助手")
st.write("输入你的各科成绩，AI帮你分析学习情况！")

# ========== 初始化 session_state（保存所有数据） ==========
if "step" not in st.session_state:
    st.session_state.step = "input"  # input / confirm / analyzing / chatting
    st.session_state.subjects = []
    st.session_state.scores = []
    st.session_state.full_marks = []
    st.session_state.messages = []  # 存整个对话历史
    st.session_state.analysis_done = False  # 是否已完成初次分析

# ========== 第一步：输入科目数 ==========
if st.session_state.step == "input":
    with st.form("input_form"):
        count = st.number_input("你这次考了几科？", min_value=1, max_value=10, step=1, value=3)
        submitted = st.form_submit_button("下一步")
        if submitted:
            st.session_state.count = count
            st.session_state.step = "input_scores"
            st.rerun()

# ========== 第二步：输入科目名和成绩 ==========
elif st.session_state.step == "input_scores":
    st.write(f"请录入 **{st.session_state.count}** 科的成绩：")
    with st.form("score_form"):
        subjects_temp = []
        scores_temp = []
        full_marks_temp = []
        for i in range(st.session_state.count):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input(f"第{i+1}科名称", key=f"name_{i}")
            with col2:
                score = st.number_input(f"{name or '科目'}成绩", min_value=0, max_value=150, key=f"score_{i}")
            with col3:
                full = st.number_input(f"{name or '科目'}满分", min_value=1, max_value=150, key=f"full_{i}")
            if name:
                subjects_temp.append(name)
                scores_temp.append(score)
                full_marks_temp.append(full)
        submitted = st.form_submit_button("确认录入")
        if submitted and len(subjects_temp) == st.session_state.count:
            st.session_state.subjects = subjects_temp
            st.session_state.scores = scores_temp
            st.session_state.full_marks = full_marks_temp
            st.session_state.step = "confirm"
            st.rerun()
        elif submitted:
            st.warning("请完整填写所有科目名称！")

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
            st.session_state.step = "input"
            st.rerun()

# ========== 第四步：调用AI分析（初次） ==========
elif st.session_state.step == "analyzing":
    st.info("🤖 正在向DeepSeek请教学习建议，请稍候...")
    subjects = st.session_state.subjects
    scores = st.session_state.scores
    full_marks = st.session_state.full_marks

    subject_score_pairs = ""
    for i in range(len(subjects)):
        subject_score_pairs += f"{subjects[i]}: {scores[i]}/{full_marks[i]}分  "

    initial_prompt = f"""我这次考试成绩如下：
{subject_score_pairs}

请帮我分析：
1. 哪些科目是优势科目？
2. 哪些科目需要重点加强？
3. 给出3条具体、可操作的学习建议。
要求：语气鼓励，简洁有力，每条建议不超过30字。"""

    # 初始化消息历史（带系统提示词）
    st.session_state.messages = [
        {"role": "system", "content": "你是一个温和、有经验的学习规划师，擅长帮学生分析成绩并给出建议。"},
        {"role": "user", "content": initial_prompt}
    ]

    # 调用API
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
        st.session_state.analysis_done = True
        st.session_state.step = "chatting"
        st.rerun()
    except Exception as e:
        st.error(f"❌ 调用失败：{e}")
        if st.button("🔙 返回重试"):
            st.session_state.step = "confirm"
            st.rerun()

# ========== 第五步：多轮对话模式 ==========
elif st.session_state.step == "chatting":
    # 显示历史对话
    st.subheader("💬 对话记录")
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**你：** {msg['content']}")
            elif msg["role"] == "assistant":
                st.markdown(f"**AI：** {msg['content']}")
            # system消息不显示

    # 分隔线
    st.divider()

    # 用户输入框
    with st.form(key="chat_form", clear_on_submit=True):
        user_question = st.text_input("💬 输入你的问题（比如：我英语怎么提分？）：")
        col1, col2 = st.columns([1, 5])
        with col1:
            submitted = st.form_submit_button("发送")
        with col2:
            if st.button("🔄 重新开始"):
                for key in ["step", "subjects", "scores", "full_marks", "messages", "analysis_done"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        if submitted and user_question:
            # 把用户问题加入历史
            st.session_state.messages.append({"role": "user", "content": user_question})

            # 调用API
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

            with st.spinner("🤖 AI思考中..."):
                try:
                    response = requests.post(url, headers=headers, data=json.dumps(data))
                    result = response.json()
                    reply = result["choices"][0]["message"]["content"]
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 出错了：{e}")

    # 显示当前成绩数据（方便参考）
    with st.expander("📊 查看当前成绩数据"):
        data = []
        for i in range(len(st.session_state.subjects)):
            data.append({
                "科目": st.session_state.subjects[i],
                "成绩": st.session_state.scores[i],
                "满分": st.session_state.full_marks[i]
            })
        st.table(data)