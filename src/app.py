import json
import streamlit as st
from main import run_pipeline


# ===== 页面配置 =====
st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🧠",
    layout="wide"
)

# ===== 顶部标题 =====
st.markdown(
    """
    <h1 style='text-align: center;'>🧠 AI会议纪要助手</h1>
    <p style='text-align: center; color: gray;'>自动提取会议重点、行动项与风险点</p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ===== 输入区 =====
col1, col2 = st.columns([2, 1])

with col1:
    meeting_text = st.text_area(
        "📄 输入会议内容",
        height=300,
        placeholder="把会议纪要粘贴在这里..."
    )

with col2:
    st.markdown("### ⚙️ 操作")
    run_btn = st.button("🚀 开始分析", use_container_width=True)

# ===== 处理逻辑 =====
if run_btn:
    if not meeting_text.strip():
        st.warning("请输入会议内容")
    else:
        with st.spinner("AI 正在分析中..."):
            result = run_pipeline(meeting_text)

        st.success("分析完成")

        st.divider()

        # ===== 结果展示 =====
        col1, col2 = st.columns(2)

        # JSON
        with col1:
            st.markdown("### 📦 JSON结果")
            st.json(result)

        # 美化展示
        with col2:
            st.markdown("### 📊 结构化展示")

            st.markdown(f"#### 📝 会议主题")
            st.info(result.get("meeting_topic", ""))

            st.markdown(f"#### 📌 会议总结")
            st.write(result.get("summary", ""))

            st.markdown("#### ✅ 关键决策")
            for item in result.get("key_decisions", []):
                st.markdown(f"- {item}")

            st.markdown("#### 📍 待办事项")
            for item in result.get("action_items", []):
                st.markdown(
                    f"- **{item.get('task','')}**（负责人：{item.get('owner','')}）"
                )

            st.markdown("#### ⚠️ 风险点")
            for item in result.get("risk_points", []):
                st.markdown(
                    f"- {item.get('issue','')}（原因：{item.get('reason','')}）"
                )

        st.divider()

        st.markdown("### 📋 可复制 JSON")
        st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")