import os
import json
from openai import OpenAI
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path)

class PRAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        if not self.api_key:
            raise ValueError("🚨 找不到 LLM_API_KEY！请检查 .env 文件。")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com" 
        )
        self.model_name = "deepseek-chat"

    def analyze_code(self, pr_data: dict, focus_mode: str) -> dict:
        # 在 prompt 中加入动态权重
       system_prompt = f"""
        你是一个严苛的资深代码架构师。
        当前审查侧重点为：{focus_mode}。

        【审查要求】：
        1. 必须深入代码 Diff 内容进行分析，不要只看 PR 描述。
        2. 【强制约束】：你必须至少找出 3 个且最多 6 个不同维度的代码问题。
        3. 如果代码中存在性能瓶颈（如循环效率、算法复杂度），请在结果中优先列出并详细分析。
        4. 每个问题必须包含 'type'（分类: bug, style, standard, performance, security）、'description' 和 'suggestion'。
        5. 以合法的 JSON 格式返回，格式如下：
        {{
            "score": 0-100的整数,
            "summary": "一段关于本次PR的总体评价",
            "issues": [
                {{"type": "...", "description": "...", "suggestion": "..."}},
                ...
            ]
        }}
        
        如果代码非常完美，issues 字段请返回空列表 []。
        """
       print("🧠 正在呼叫大模型进行代码+规范审查，请稍候...")
        
       system_prompt = """
        你是一个资深的研发工程师和严格的代码审查专家。
        你的任务是审查提供的 GitHub PR 代码变更（Diff），并检查 PR 的提交规范。
        
        【任务 1：代码审查】
        1. 代码是否有明显的 Bug（比如除以0、空指针）或潜在的崩溃风险？
        2. 代码可读性和可维护性如何？有没有更好的写法？

        【任务 2：规范检查】
        请检查用户提供的 PR 标题和描述：
        1. 标题是否符合规范（例如：以 feat:, fix:, docs:, chore: 等开头）？
        2. 描述是否为空？是否过于简略？

        【极其重要】必须严格以合法的 JSON 格式输出你的评审结果，直接输出 JSON 文本，不要有 ```json 代码块包裹！
        
        输出的 JSON 结构必须严格如下：
        {
            "summary": "一句话总结这个 PR 主要做了什么变更",
            "issues": [
                {
                    "type": "bug | style | performance | standard",  
                    "description": "问题的详细描述",
                    "suggestion": "你给出的具体修改建议"
                }
            ],
            "score": 85
        }
        """

       user_content = f"""
        请审查以下 PR：
        【PR 标题】：{pr_data.get('title', '无标题')}
        【PR 描述】：{pr_data.get('body', '无描述')}

        【代码变更 (Diff)】：
        {pr_data.get('diff', '')}
        """

       try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"}, 
                temperature=0.3 
            )
            return json.loads(response.choices[0].message.content)
            
       except Exception as e:
            raise Exception(f"❌ 调用大模型 API 失败: {e}")