# 🤖 AI-PR-Review 自动代码审查助手

本项目是一个基于大模型（DeepSeek）的自动化 GitHub PR 审查工具，专注于代码 Bug 检查与提交规范（Conventional Commits）检查。

### 🚀 在线体验 (Demo)
点击下方链接，无需下载，直接使用 AI 审查功能：
👉 **[https://ai-pr-review-lxz6lxgzqydu6bbsjiglzr.streamlit.app/]**

### 💡 功能特性
* **GitHub API 集成**：实时获取 PR 的标题、描述与代码 Diff。
* **智能审查**：利用大模型分析 Bug，并强制检查提交规范（如 `feat:`, `fix:` 等）。
* **交互友好**：支持一键随机演示，错误处理机制完善。

### ⚙️ 系统架构
```mermaid
sequenceDiagram
    participant User as 用户
    participant App as AI PR Reviewer
    participant GitHub as GitHub API
    participant DeepSeek as AI 模型

    User->>App: 提交 PR 链接
    App->>GitHub: 获取 PR 标题/描述/代码Diff
    GitHub-->>App: 返回数据
    App->>DeepSeek: 发送审查请求
    DeepSeek-->>App: 返回 JSON 格式评审报告
    App-->>User: 渲染审查结果

## 🎥 演示视频 (Demo Video)

快速了解代码助手的核心功能，请点击下方链接观看演示视频：

* 📺 **Bilibili 在线观看**：
【AI代码助手 - 核心功能演示】https://www.bilibili.com/video/BV1SjVQ68EbP?vd_source=8ab476e8dfc703b2a54a1333667664de
