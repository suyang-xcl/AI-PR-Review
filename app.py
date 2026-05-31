import streamlit as st
from github_client import GitHubPRFetcher
from llm_analyzer import PRAnalyzer

# 页面配置
st.set_page_config(page_title="AI PR Reviewer", page_icon="🤖", layout="centered")

# --- 侧边栏 ---
st.sidebar.title("🛠️ 审查配置")
focus_mode = st.sidebar.selectbox(
    "请选择审查侧重点:",
    ["全面审计 (默认)", "性能优化优先", "安全漏洞扫描", "代码风格规范"]
)

# 标题与描述
st.title("🤖 自动代码审查助手")
st.markdown("输入 GitHub PR 链接，让 AI 进行多维度深度审查。")

# 初始化工具
@st.cache_resource
def get_fetcher(): return GitHubPRFetcher()
@st.cache_resource
def get_analyzer(): return PRAnalyzer()

fetcher = get_fetcher()
analyzer = get_analyzer()

# 体验按钮
if st.button("✨ 帮我随机体验一个真实开源 PR"):
    st.session_state.pr_url = "https://github.com/tiangolo/fastapi/pull/10000"
else:
    st.session_state.setdefault('pr_url', "")

pr_url = st.text_input("🔗 请输入 GitHub PR 链接:", value=st.session_state.pr_url)

# 审查主逻辑
if st.button("🚀 开始 AI 审查", type="primary"):
    if not pr_url:
        st.warning("请先输入链接哦！")
    else:
        try:
            with st.spinner('正在抓取 PR 信息...'):
                pr_data = fetcher.fetch_pr_details(pr_url)
            
            st.success(f"✅ 成功抓取：{pr_data['title']}")

            with st.spinner('AI 正在深度审查中...'):
                report = analyzer.analyze_code(pr_data, focus_mode)
            
            # 展示核心指标
            col1, col2 = st.columns(2)
            col1.metric("审查深度", focus_mode)
            col2.metric("AI 评分", f"{report.get('score', 'N/A')} 分")

            st.markdown("**📝 总结：**")
            st.write(report.get('summary', '无'))

            # --- 这一段代码替换你 app.py 中原有的循环展示逻辑 ---
            st.markdown("### 🔍 发现的问题")
            issues = report.get('issues', [])
            
            if not issues:
                st.info("太棒了！AI 没有发现任何代码 Bug 或规范问题！💯")
            else:
                # 使用一个纯净的循环，确保把 issues 列表里的每一个元素都渲染出来
                for i in range(len(issues)):
                    issue = issues[i]
                    # 获取类型图标，如果找不到就用默认值
                    icon = {'bug': '🐛', 'style': '💅', 'standard': '👮‍♂️', 'performance': '⚡', 'security': '🛡️'}.get(issue.get('type', '').lower(), '🔍')
                    
                    # 确保每一个 expander 都是独立的
                    with st.expander(f"{icon} 问题 {i + 1}: {issue.get('description', '')[:30]}..."):
                        st.markdown("**详细描述：**")
                        st.write(issue.get('description', ''))
                        st.markdown("**💡 建议：**")
                        st.info(issue.get('suggestion', ''))
                       # --- 修改后：更严谨的拦截逻辑 ---
                        raw_code = issue.get('fixed_code')
                        # 确保转换为字符串再去空格，防止 raw_code 是 None
                        fixed_code = str(raw_code).strip() if raw_code else ""
                        
                        # 过滤掉空的、写着 None 或者 N/A 的无效代码
                        if fixed_code and fixed_code.lower() not in ['none', 'n/a', 'null', '无']:
                            st.markdown("**💻 修复建议代码：**")
                            st.code(fixed_code, language='python')
            # 报告导出功能
            st.markdown("---")
            md_content = f"# 代码审查报告\n\n**侧重**: {focus_mode}\n**评分**: {report.get('score')} 分\n\n## 总结\n{report.get('summary')}\n\n## 详情\n"
            for i in issues:
                md_content += f"- **{i.get('type').upper()}**: {i.get('description')}\n  *建议: {i.get('suggestion')}*\n\n"
            
            st.download_button("📥 下载审查报告 (Markdown)", md_content, "pr_review_report.md", "text/markdown")
            
        except Exception as e:
            st.error(f"审查出错: {e}")