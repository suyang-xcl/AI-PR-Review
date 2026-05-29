import os
import requests  # 👈 就是这句不小心失踪了！
from dotenv import load_dotenv

# 获取当前脚本所在的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

# 强行加载这个绝对路径下的 .env 文件
load_dotenv(dotenv_path=env_path)

class GitHubPRFetcher:
    def __init__(self):
        # 从环境变量获取 Token
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("🚨 找不到 GITHUB_TOKEN！请检查 .env 文件是否配置正确。")
        
        # 统一设置请求头，必须带上这个特殊的 Accept 才能直接拿到 .diff 格式
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # ⚠️ 黑名单过滤：这些文件发生改动时，不要喂给大模型看，浪费钱且容易把模型搞晕
        self.ignore_extensions = (
            '.lock', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.mp4', 
            '.csv', '.json', '.min.js', '.min.css', '.map'
        )

    def _parse_github_url(self, pr_url: str) -> tuple:
        """从用户输入的 URL 中提取 owner, repo, pull_number"""
        try:
            parts = pr_url.rstrip('/').split('/')
            pull_number = parts[-1]
            repo = parts[-3]
            owner = parts[-4]
            return owner, repo, pull_number
        except Exception:
            raise ValueError(f"🚨 PR 链接格式解析失败，请确保链接是标准的 GitHub PR 地址: {pr_url}")

    def fetch_pr_diff(self, pr_url: str) -> str:
        """核心方法：传入 PR 链接，返回过滤后的 Diff 文本"""
        owner, repo, pull_number = self._parse_github_url(pr_url)
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
        
        print(f"⏳ 正在连接 GitHub 拉取 {owner}/{repo} 的 PR #{pull_number} ...")
        
        try:
            # 发起 GET 请求
            response = requests.get(api_url, headers=self.headers, timeout=15)
            response.raise_for_status() 
            
            raw_diff = response.text
            filtered_diff = self._filter_diff(raw_diff)
            
            return filtered_diff
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ 请求 GitHub API 失败: {e}")

    def _filter_diff(self, raw_diff: str) -> str:
        """清洗数据：把没用的文件变更从 diff 中剔除掉"""
        filtered_lines = []
        skip_current_file = False
        
        for line in raw_diff.split('\n'):
            if line.startswith('diff --git'):
                file_path = line.split(' b/')[-1] if ' b/' in line else ""
                if file_path.lower().endswith(self.ignore_extensions):
                    print(f"♻️ 已过滤无关文件: {file_path}")
                    skip_current_file = True
                else:
                    skip_current_file = False
                    
            if not skip_current_file:
                filtered_lines.append(line)
                
        return '\n'.join(filtered_lines)

# ==========================================
# 本地测试代码
# ==========================================
if __name__ == "__main__":
    try:
        fetcher = GitHubPRFetcher()
        test_url = "https://github.com/tiangolo/fastapi/pull/10000"
        
        print("\n--- 开始执行抓取测试 ---")
        diff_result = fetcher.fetch_pr_diff(test_url)
        
        print("\n✅ 抓取成功！Diff 的前 500 个字符如下：\n")
        print("="*40)
        print(diff_result[:500]) 
        print("="*40)
        print(f"\n📏 过滤后的 Diff 总长度: {len(diff_result)} 字符")
        
    except Exception as err:
        print(f"\n💀 哎呀，报错了:\n{err}")