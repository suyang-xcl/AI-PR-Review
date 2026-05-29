import os
import requests
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path)

class GitHubPRFetcher:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("🚨 找不到 GITHUB_TOKEN！请检查 .env 文件是否配置正确。")
        
        # 抓取代码用的专属请求头
        self.diff_headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        # 抓取标题和描述用的 JSON 请求头 (新增)
        self.json_headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        self.ignore_extensions = (
            '.lock', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.mp4', 
            '.csv', '.json', '.min.js', '.min.css', '.map'
        )

    def _parse_github_url(self, pr_url: str) -> tuple:
        try:
            parts = pr_url.rstrip('/').split('/')
            pull_number = parts[-1]
            repo = parts[-3]
            owner = parts[-4]
            return owner, repo, pull_number
        except Exception:
            raise ValueError(f"🚨 PR 链接格式解析失败，请确保链接是标准的 GitHub PR 地址: {pr_url}")

    def fetch_pr_details(self, pr_url: str) -> dict:
        """
        🚀 升级版核心方法：不仅返回代码，还返回标题和描述！
        """
        owner, repo, pull_number = self._parse_github_url(pr_url)
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
        
        print(f"⏳ 正在连接 GitHub 拉取 {owner}/{repo} 的 PR #{pull_number} ...")
        
        try:
            # 1. 抓取 PR 的基本信息（标题、描述）
            info_resp = requests.get(api_url, headers=self.json_headers, timeout=15)
            info_resp.raise_for_status() 
            pr_info = info_resp.json()
            
            title = pr_info.get("title", "")
            body = pr_info.get("body", "") or "无描述"
            
            # 2. 抓取代码 Diff
            diff_resp = requests.get(api_url, headers=self.diff_headers, timeout=15)
            diff_resp.raise_for_status()
            filtered_diff = self._filter_diff(diff_resp.text)
            
            # 把三个宝贝打包成一个字典返回
            return {
                "title": title,
                "body": body,
                "diff": filtered_diff
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ 请求 GitHub API 失败: {e}")

    def _filter_diff(self, raw_diff: str) -> str:
        filtered_lines = []
        skip_current_file = False
        
        for line in raw_diff.split('\n'):
            if line.startswith('diff --git'):
                file_path = line.split(' b/')[-1] if ' b/' in line else ""
                if file_path.lower().endswith(self.ignore_extensions):
                    skip_current_file = True
                else:
                    skip_current_file = False
                    
            if not skip_current_file:
                filtered_lines.append(line)
                
        return '\n'.join(filtered_lines)

if __name__ == "__main__":
    try:
        fetcher = GitHubPRFetcher()
        test_url = "https://github.com/tiangolo/fastapi/pull/10000" 
        
        print("\n--- 开始执行抓取测试 ---")
        # 注意这里的方法名变了
        result = fetcher.fetch_pr_details(test_url)
        
        print(f"\n✅ 抓取成功！")
        print(f"📌 PR 标题: {result['title']}")
        print(f"📝 描述长度: {len(result['body'])} 字符")
        print(f"📏 Diff 长度: {len(result['diff'])} 字符")
        
    except Exception as err:
        print(f"\n💀 哎呀，报错了:\n{err}")