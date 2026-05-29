import streamlit as st
from github_client import GitHubPRFetcher
from llm_analyzer import PRAnalyzer

# 页面配置
st.set_page_config(page_title="AI PR Reviewer", page_icon="🤖", layout="centered")

# --- 侧边栏：进阶配置 ---
st.sidebar.title("🛠️ 审查配置")
focus_mode = st.sidebar.selectbox(
    "请选择审查侧重点:",
    ["全面审计 (默认)", "性能优化优先", "安全漏洞扫描", "代码风格规范"]
)
st.sidebar.info("侧重点会引导 AI 在审查时侧重于特定维度。")

# 标题
st.title("🤖 自动代码审查助手")
st.markdown("输入一个 GitHub PR 链接，让 AI 帮你一键查 Bug + 查规范！")

# @st.cache_resource
def get_fetcher():
    return GitHubPRFetcher()

# @st.cache_resource
def get_analyzer():
    return PRAnalyzer()

fetcher = get_fetcher()
analyzer = get_analyzer()

# 一键体验按钮逻辑
if st.button("✨ 帮我随机体验一个真实开源 PR"):
    st.session_state.pr_url = "https://github.com/tiangolo/fastapi/pull/10000"
else:
    st.session_state.setdefault('pr_url', "")

pr_url = st.text_input("🔗 请输入 GitHub PR 链接:", value=st.session_state.pr_url, placeholder="例如: https://github.com/tiangolo/fastapi/pull/10000")

# 审查逻辑
if st.button("🚀 开始 AI 审查", type="primary"):
    if not pr_url:
        st.warning("请先输入链接哦！")
    else:
        try:
            with st.spinner('正在潜入 GitHub 抓取 PR 信息...'):
                pr_data = fetcher.fetch_pr_details(pr_url)
            
            st.success(f"✅ 成功抓取！标题：{pr_data['title']}")

            with st.spinner('大模型正在进行深度审查...'):
                report = analyzer.analyze_code(pr_data, focus_mode)
                
            # --- 关键调试：把这行加进去 ---
            st.warning(f"DEBUG (临时): AI 原始数据长度: {len(report.get('issues', []))}")
            st.json(report) # 直接在网页上显示解析后的完整数据
            # ----------------------------
            
            st.success("🎉 AI 审查完毕！")
            
            # --- 优化：可视化展示卡片 ---
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("审查深度", focus_mode)
            with col2:
                st.metric("AI 评分", f"{report.get('score', 'N/A')} 分")

            st.markdown("**📝 总结：**")
            st.write(report.get('summary', '无'))

            st.markdown("### 🔍 发现的问题")
            
            issues = report.get('issues', [])
            if not issues:
                st.info("太棒了！AI 没有发现任何代码 Bug 或规范问题！💯")
            else:
                for idx, issue in enumerate(issues):
                    # 图标区分
                    type_icon = {
                        'bug': '🐛', 
                        'style': '💅', 
                        'standard': '👮‍♂️', 
                        'performance': '⚡',
                        'security': '🛡️'
                    }
                    # --- 把下面这段代码粘在 for 循环结束的后面 ---
            st.markdown("---")
            
            # 整理数据为 Markdown 文本
            markdown_report = f"# 代码审查报告\n\n**审查深度**: {focus_mode}\n**AI 评分**: {report.get('score', 'N/A')} 分\n\n## 总结\n{report.get('summary', '无')}\n\n## 发现的问题\n"
            for issue in issues:
                markdown_report += f"- **{issue.get('type', '').upper()}**: {issue.get('description', '')}\n  *建议: {issue.get('suggestion', '')}*\n\n"

            # 导出按钮
            st.download_button(
                label="📥 下载审查报告 (Markdown)",
                data=markdown_report,
                file_name="pr_review_report.md",
                mime="text/markdown",
            )
            icon = type_icon.get(issue.get('type', ''), '⚡')
                    
            with st.expander(f"{icon} 问题 {idx + 1}: [{issue.get('type', 'info').upper()}] {issue.get('description', '')[:30]}..."):
                        st.markdown("**详细描述：**")
                        st.write(issue.get('description', ''))
                        st.markdown("**💡 建议：**")
                        st.info(issue.get('suggestion', ''))
                    
        except Exception as e:
            # --- 优化：人性化的错误反馈 ---
            st.error("哎呀，审查遇到了小阻碍：")
            st.caption(f"具体原因: {e}")
            st.info("💡 小贴士：请检查链接是否正确，或者该 PR 是否已经合并？如果是网络问题，请重试一下哦！")