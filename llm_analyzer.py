import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 获取当前脚本所在绝对路径，强行加载 .env (吸取之前的教训，绝对不翻车！)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path)

class PRAnalyzer:
    def __init__(self):
        # 提取你的大模型 API Key
        self.api_key = os.getenv("LLM_API_KEY")
        if not self.api_key:
            raise ValueError("🚨 找不到 LLM_API_KEY！请检查 .env 文件。")
        
        # 初始化大模型客户端
        # 因为我们用的是 DeepSeek，所以 base_url 要指向 DeepSeek 的服务器
        # (国内绝大多数大模型都完美兼容 OpenAI 的代码格式，直接套用最爽)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"  # 👈 DeepSeek 官方接口地址
        )
        self.model_name = "deepseek-chat"        # 👈 使用的模型名字

    def analyze_code(self, diff_content: str) -> dict:
        """
        核心方法：将代码 Diff 发给大模型，并强制它返回 JSON 格式的评审报告
        """
        print("🧠 正在呼叫大模型进行代码评审，请稍候...")
        
        # 这是我们给大模型设定的“人设”和“任务要求”（你可以随意修改调教它）
        system_prompt = """
        你是一个资深的研发工程师和严格的代码审查专家。
        你的任务是审查提供的 GitHub PR 代码变更（Diff），并提供专业的评审意见。
        
        请重点关注：
        1. 代码是否有明显的 Bug（比如除以0、空指针）或潜在的崩溃风险？
        2. 代码可读性和可维护性如何？有没有更好的写法？
        
        【极其重要】你必须严格以合法的 JSON 格式输出你的评审结果，不要包含任何 Markdown 代码块包裹（如 ```json），直接输出 JSON 文本，不要有任何其他废话！
        
        输出的 JSON 结构必须如下：
        {
            "summary": "一句话总结这个 PR 主要做了什么变更",
            "issues": [
                {
                    "type": "bug | style | performance",
                    "description": "问题的详细描述",
                    "suggestion": "你给出的具体修改建议"
                }
            ],
            "score": 85
        }
        """

        try:
            # 正式向大模型发送请求
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请审查以下代码变更：\n\n{diff_content}"}
                ],
                # 强迫模型输出 JSON 格式
                response_format={"type": "json_object"}, 
                # 温度调低（0.3），让它的回答更严谨、少点天马行空
                temperature=0.3 
            )
            
            # 获取大模型的文字回复
            raw_reply = response.choices[0].message.content
            
            # 将文字格式的 JSON 转化为 Python 的字典对象，方便后续使用
            result_dict = json.loads(raw_reply)
            return result_dict
            
        except json.JSONDecodeError:
            raise Exception("❌ 大模型没有乖乖返回 JSON 格式，解析失败！请重试。")
        except Exception as e:
            raise Exception(f"❌ 调用大模型 API 失败: {e}")

# ==========================================
# 本地测试代码：只在直接运行本文件时执行
# ==========================================
if __name__ == "__main__":
    try:
        # 我们在这里伪造一段有明显 Bug 的代码 Diff 喂给它，看看它能不能揪出来
        test_diff = '''
diff --git a/calculator.py b/calculator.py
index 1234567..890abcd 100644
--- a/calculator.py
+++ b/calculator.py
@@ -10,3 +10,4 @@ def add(a, b):
     return a + b
 
 def divide(a, b):
-    return a / b
+    # 开发者瞎改的，完全没考虑 b 是 0 的情况
+    return a / b
        '''
        
        analyzer = PRAnalyzer()
        print("\n--- 开始执行 AI 分析测试 ---")
        
        report = analyzer.analyze_code(test_diff)
        
        print("\n✅ 分析成功！大模型给出的 JSON 报告如下：\n")
        # 漂亮地打印出 JSON 结果
        print(json.dumps(report, indent=4, ensure_ascii=False))
        
    except Exception as err:
        print(f"\n💀 哎呀，报错了:\n{err}")