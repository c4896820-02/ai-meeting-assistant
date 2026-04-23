import json
import streamlit as st
from main import run_pipeline


st.set_page_config(page_title="AI Meeting Assistant", page_icon="📝", layout="wide")

st.title("📝 AI Meeting Assistant")
st.caption("基于大模型的会议纪要结构化提取工具")

default_text = """今天我们讨论AI会议助手的开发进度。
产品经理提出需要在一周内完成第一版原型。
技术负责人表示当前模型输出不稳定，需要优化prompt。
最终决定先完成基础版本，下周进行评审。

待办：
- 张三负责prompt优化
- 李四负责接口开发
"""

meeting_text = st.text_area(
    "请输入会议内容",
    value=default_text,
    height=260
)

if st.button("开始分析"):
    if not meeting_text.strip():
        st.warning("请输入会议内容")
    else:
        with st.spinner("模型分析中，请稍候..."):
            try:
                result = run_pipeline(meeting_text)

                st.success("分析完成")

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("结构化结果")
                    st.json(result)

                with col2:
                    st.subheader("格式化展示")

                    st.markdown(f"**会议主题：** {result.get('meeting_topic', '')}")
                    st.markdown(f"**会议总结：** {result.get('summary', '')}")

                    st.markdown("**关键决策：**")
                    for item in result.get("key_decisions", []):
                        st.markdown(f"- {item}")

                    st.markdown("**待办事项：**")
                    for item in result.get("action_items", []):
                        st.markdown(
                            f"- 任务：{item.get('task', '')} ｜ 负责人：{item.get('owner', '')}"
                        )

                    st.markdown("**风险点：**")
                    for item in result.get("risk_points", []):
                        st.markdown(
                            f"- 问题：{item.get('issue', '')} ｜ 原因：{item.get('reason', '')}"
                        )

                st.subheader("可复制 JSON")
                st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")

            except Exception as e:
                st.error(f"运行失败：{e}")