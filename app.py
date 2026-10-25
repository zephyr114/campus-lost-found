# -*- coding: utf-8 -*-
"""
app.py  Streamlit 网页主程序
运行方式：streamlit run app.py
"""
import streamlit as st
from database import init_db, add_lost, add_found, get_all_lost, get_all_found, delete_lost, delete_found
from matching import match_all, client

# 页面基础设置
st.set_page_config(page_title="校园AI失物招领匹配系统", layout="wide")
init_db()  # 启动自动初始化数据库

st.title("🎓 校园AI失物招领智能匹配系统")

# API Key 未配置时在顶部给一个醒目的提示
if client is None:
    st.error("⚠️ 尚未配置智谱 API_KEY：请打开 matching.py，把 API_KEY 换成你自己的智谱 Key，然后重启本页面。")

tab1, tab2, tab3, tab4 = st.tabs(["失物登记", "拾物登记", "AI智能匹配", "查看全部记录"])

# ========== 标签页1：失物登记 ==========
with tab1:
    st.subheader("📥 失物信息登记")
    name = st.text_input("物品名称（例：黑色折叠伞）")
    desc = st.text_area("物品特征描述")
    loc = st.text_input("丢失地点")
    t_lost = st.text_input("丢失时间")
    contact = st.text_input("联系方式（仅后台可见）")
    if st.button("提交失物信息"):
        if name and desc:
            add_lost(name, desc, loc, t_lost, contact)
            st.success("✅ 失物信息提交成功！")
        else:
            st.warning("请填写物品名称和描述！")

# ========== 标签页2：拾物登记 ==========
with tab2:
    st.subheader("📤 拾物信息登记")
    name_f = st.text_input("捡到物品名称")
    desc_f = st.text_area("捡到物品特征描述")
    loc_f = st.text_input("捡拾地点")
    t_found = st.text_input("捡拾时间")
    contact_f = st.text_input("拾主联系方式（仅后台可见）")
    if st.button("提交拾物信息"):
        if name_f and desc_f:
            add_found(name_f, desc_f, loc_f, t_found, contact_f)
            st.success("✅ 拾物信息提交成功！")
        else:
            st.warning("请填写物品名称和描述！")

# ========== 标签页3：AI智能匹配【核心演示页面】 ==========
with tab3:
    st.subheader("🤖 AI语义智能匹配")
    threshold = st.slider("匹配阈值（推荐0.7）", min_value=0.4, max_value=0.9, value=0.7, step=0.05)
    if st.button("开始AI匹配"):
        with st.spinner("AI正在比对物品描述..."):
            lost_data = get_all_lost()
            found_data = get_all_found()
            try:
                match_result = match_all(lost_data, found_data, threshold)
            except RuntimeError as e:
                st.error(f"❌ {e}")
                match_result = []
        if len(match_result) == 0:
            if lost_data and found_data:
                st.info("🔍 未找到高相似度匹配记录，请尝试调低阈值或者新增记录")
            else:
                st.info("📝 暂时没有可匹配的数据，请先在「失物登记」和「拾物登记」录入记录")
        else:
            st.success(f"找到 {len(match_result)} 组候选匹配！")
            for item in match_result:
                score = item["score"]
                lost = item["lost"]
                found = item["found"]
                st.markdown(f"""
> **匹配相似度：{score}**
> 【失物】物品：{lost[1]}，描述：{lost[2]}，丢失地点：{lost[3]}
> 【拾物】物品：{found[1]}，描述：{found[2]}，捡拾地点：{found[3]}
                """)

# ========== 标签页4：查看全部记录（含撤回功能） ==========
with tab4:
    col1, col2 = st.columns(2)

    def render_records(title, records, kind, delete_fn):
        """渲染一个记录列表，每条记录带「撤回」按钮 + 二次确认"""
        st.subheader(title)
        if not records:
            st.caption("暂无记录")
        for row in records:
            c1, c2, c3 = st.columns([2, 3, 2])
            c1.write(f"#{row[0]} {row[1]}")
            c2.write(row[2])
            c3.write(f"{row[3]}")
            if st.button("撤回", key=f"del_{kind}_{row[0]}"):
                st.session_state["pending_del"] = (kind, row[0])
                st.rerun()
        # 二次确认：撤回是不可恢复操作
        pending = st.session_state.get("pending_del")
        if pending and pending[0] == kind:
            _, rid = pending
            st.warning(f"⚠️ 确认撤回这条{'失物' if kind == 'lost' else '拾物'}记录（ID=#{rid}）？撤回后不可恢复。")
            a1, a2 = st.columns(2)
            if a1.button("确认撤回", key=f"confirm_{kind}_{rid}"):
                delete_fn(rid)
                st.session_state.pop("pending_del", None)
                st.success("✅ 已撤回该记录")
                st.rerun()
            if a2.button("取消", key=f"cancel_{kind}_{rid}"):
                st.session_state.pop("pending_del", None)
                st.rerun()

    with col1:
        render_records("所有失物记录", get_all_lost(), "lost", delete_lost)
    with col2:
        render_records("所有拾物记录", get_all_found(), "found", delete_found)
