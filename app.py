import streamlit as st
from github_client import GitHubPRFetcher
from llm_analyzer import PRAnalyzer

# ==========================================
# 1. 网页全局设置
# ==========================================
st.set_page_config(page_title="AI PR Reviewer", page_icon="🤖", layout="centered")

st.title("🤖 自动代码审查助手")
st.markdown("输入一个 GitHub PR 链接，让大模型帮你一键找出 Bug！")

# ==========================================
# 2. 初始化核心组件
# ==========================================
# 使用 st.cache_resource 防止每次点击按钮都重新初始化
@st.cache_resource
def get_fetcher():
    return GitHubPRFetcher()

@st.cache_resource
def get_analyzer():
    return PRAnalyzer()

fetcher = get_fetcher()
analyzer = get_analyzer()

# ==========================================
# 3. 画 UI 界面
# ==========================================
# 输入框
pr_url = st.text_input("🔗 请输入 GitHub PR 链接:", placeholder="例如: https://github.com/tiangolo/fastapi/pull/10000")

# 按钮
if st.button("🚀 开始 AI 审查", type="primary"):
    if not pr_url:
        st.warning("请先输入链接哦！")
    else:
        try:
            # 第一阶段：拉取代码
            with st.spinner('正在潜入 GitHub 抓取代码变更...'):
                diff_text = fetcher.fetch_pr_diff(pr_url)
            
            st.success(f"✅ 成功抓取代码！过滤后一共 {len(diff_text)} 字符。")

            # 第二阶段：AI 分析
            with st.spinner('大模型正在玩命阅读代码，请稍候...'):
                report = analyzer.analyze_code(diff_text)
            
            st.success("🎉 AI 审查完毕！")
            
            # ==========================================
            # 4. 漂亮地展示结果
            # ==========================================
            st.markdown("---")
            
            # 顶部展示分数和总结
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(label="🌟 AI 评分", value=f"{report.get('score', 'N/A')} 分")
            with col2:
                st.markdown("**📝 总结：**")
                st.write(report.get('summary', '无'))

            st.markdown("### 🔍 发现的问题")
            
            # 循环展示每一个 issue
            for idx, issue in enumerate(report.get('issues', [])):
                # 根据问题类型给个不同的表情
                icon = "🐛" if issue['type'] == 'bug' else "💅" if issue['type'] == 'style' else "⚡"
                
                # 用扩展面板展示
                with st.expander(f"{icon} 问题 {idx + 1}: [{issue['type'].upper()}] {issue['description'][:30]}..."):
                    st.markdown("**详细描述：**")
                    st.write(issue['description'])
                    st.markdown("**💡 建议：**")
                    st.info(issue['suggestion'])
                    
        except Exception as e:
            st.error(f"发生错误啦：\n{e}")