import streamlit as st
from github_client import GitHubPRFetcher
from llm_analyzer import PRAnalyzer

st.set_page_config(page_title="AI PR Reviewer", page_icon="🤖", layout="centered")

st.title("🤖 自动代码审查助手")
st.markdown("输入一个 GitHub PR 链接，让大模型帮你一键查 Bug + 查规范！")

@st.cache_resource
def get_fetcher():
    return GitHubPRFetcher()

@st.cache_resource
def get_analyzer():
    return PRAnalyzer()

fetcher = get_fetcher()
analyzer = get_analyzer()

pr_url = st.text_input("🔗 请输入 GitHub PR 链接:", placeholder="例如: [https://github.com/tiangolo/fastapi/pull/10000](https://github.com/tiangolo/fastapi/pull/10000)")
# --- 增加：一键体验按钮 ---
if st.button("✨ 帮我随机体验一个真实开源 PR"):
    # 这里放一个你觉得最具代表性的、不规范的 PR 链接
    st.session_state.pr_url = "https://github.com/tiangolo/fastapi/pull/10000"
else:
    # 默认值处理
    st.session_state.setdefault('pr_url', "")

# 绑定输入框的 value 到 session_state
pr_url = st.text_input("🔗 请输入 GitHub PR 链接:", value=st.session_state.pr_url, placeholder="例如: https://github.com/tiangolo/fastapi/pull/10000")

if st.button("🚀 开始 AI 审查", type="primary"):
    if not pr_url:
        st.warning("请先输入链接哦！")
    else:
        try:
            with st.spinner('正在潜入 GitHub 抓取 PR 信息...'):
                # 调用升级后的方法，拿到字典
                pr_data = fetcher.fetch_pr_details(pr_url)
            
            st.success(f"✅ 成功抓取！标题：{pr_data['title']}")

            with st.spinner('大模型正在进行代码 + 规范双重审查，请稍候...'):
                # 把整个字典传给大模型
                report = analyzer.analyze_code(pr_data)
            
            st.success("🎉 AI 审查完毕！")
            
            st.markdown("---")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(label="🌟 AI 评分", value=f"{report.get('score', 'N/A')} 分")
            with col2:
                st.markdown("**📝 总结：**")
                st.write(report.get('summary', '无'))

            st.markdown("### 🔍 发现的问题")
            
            issues = report.get('issues', [])
            if not issues:
                st.info("太棒了！大模型没有发现任何代码 Bug 和规范问题，满分通过！💯")
            else:
                for idx, issue in enumerate(issues):
                    # 专属图标判断逻辑
                    icon = "🐛" if issue['type'] == 'bug' else "💅" if issue['type'] == 'style' else "👮‍♂️" if issue['type'] == 'standard' else "⚡"
                    
                    with st.expander(f"{icon} 问题 {idx + 1}: [{issue['type'].upper()}] {issue['description'][:30]}..."):
                        st.markdown("**详细描述：**")
                        st.write(issue['description'])
                        st.markdown("**💡 建议：**")
                        st.info(issue['suggestion'])
                    
        except Exception as e:
            # --- 优化：人性化的错误提示 ---
            st.error("哎呀，审查遇到了小阻碍：")
            st.caption(f"具体原因: {e}")
            st.info("💡 小贴士：请检查链接是否正确，或者该 PR 是否已经合并？如果是网络问题，请重试一下哦！")