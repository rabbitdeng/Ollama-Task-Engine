"""
GitHub API 模块
==============

提供 GitHub 仓库搜索和信息获取功能。

本模块提供：
- search_github_repos: 搜索 GitHub 仓库（按关键词和编程语言）
- get_github_repo_info: 获取单个仓库的详细信息（包括 README）
"""

import re
import requests
from typing import Final

GITHUB_API_TIMEOUT: Final[int] = 15
GITHUB_USER_AGENT: Final[str] = "Code-Agent/1.0 (+https://github.com)"
MAX_CONTENT_LENGTH: Final[int] = 4000


def search_github_repos(keyword: str, language: str = "") -> str:
    """
    直接搜索 GitHub 仓库（使用 GitHub API）
    
    通过 GitHub API 搜索开源项目，返回项目名称、描述、Stars、Forks 等信息。
    结果按 Stars 数量降序排列，最多返回 8 个项目。
    
    Args:
        keyword: 搜索关键词，如 'AI', 'LLM', 'machine learning', 'deep learning'
        language: 可选，编程语言过滤，如 'Python', 'JavaScript', 'Rust'
        
    Returns:
        格式化的搜索结果字符串
        
    Example:
        >>> search_github_repos("AI", "Python")
        "[GitHub 搜索结果 - 关键词: AI] (共 12345 个结果)
        项目名: user/repo1
        描述: 一个很棒的 AI 项目
        Stars: 10,000 | Forks: 1,000
        语言: Python
        链接: https://github.com/user/repo1
        ---
        ..."
        
    Note:
        - 使用 GitHub REST API v3
        - 请求超时时间为 15 秒
        - 结果会自动格式化显示
    """
    try:
        query = keyword
        if language:
            query += f" language:{language}"
        
        url = f"https://api.github.com/search/repositories?q={requests.utils.quote(query)}&sort=stars&order=desc&per_page=8"
        headers = {
            'User-Agent': GITHUB_USER_AGENT,
            'Accept': 'application/vnd.github.v3+json',
        }
        
        response = requests.get(url, headers=headers, timeout=GITHUB_API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if data.get('total_count', 0) == 0:
            return f"[GitHub 搜索结果 - 关键词: {keyword}]\n未找到相关项目"
        
        results = []
        for item in data.get('items', [])[:8]:
            results.append(
                f"项目名: {item['full_name']}\n"
                f"描述: {item.get('description', '无描述') or '无描述'}\n"
                f"Stars: {item['stargazers_count']:,} | Forks: {item.get('forks_count', 0):,}\n"
                f"语言: {item.get('language', '未知') or '未知'}\n"
                f"链接: {item['html_url']}\n"
            )
        
        return f"[GitHub 搜索结果 - 关键词: {keyword}] (共 {data.get('total_count', 0):,} 个结果)\n" + "\n---\n".join(results)
        
    except requests.exceptions.Timeout:
        return "[ERROR] GitHub API request timeout"
    except requests.exceptions.RequestException as e:
        return f"[ERROR] GitHub API request failed: {str(e)}"
    except Exception as e:
        return f"[ERROR] GitHub 搜索失败: {str(e)}"


def get_github_repo_info(repo_url: str) -> str:
    """
    获取 GitHub 仓库详细信息（包括项目描述和 README）
    
    解析 GitHub 仓库 URL，调用 GitHub API 获取项目元数据，
    并尝试获取 README.md 文件内容。
    
    Args:
        repo_url: GitHub 仓库 URL，格式如 https://github.com/username/repo
        
    Returns:
        格式化的仓库信息字符串
        
    Example:
        >>> get_github_repo_info("https://github.com/user/repo")
        "[仓库信息]
        名称: repo
        描述: 项目描述
        Stars: 10,000
        Forks: 1,000
        语言: Python
        最后更新: 2024-01-01T12:00:00Z
        项目主页: https://github.com/user/repo
        
        [README 内容]
        # 项目标题
        ..."
        
    Note:
        - 会自动尝试多个分支获取 README (master, main, dev)
        - README 内容超过 4000 字符时会自动截断
    """
    try:
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            return f"[错误] 不是有效的 GitHub 仓库URL: {repo_url}"
        
        owner, repo = match.groups()
        repo = repo.rstrip('/')
        
        headers = {
            'User-Agent': GITHUB_USER_AGENT,
            'Accept': 'application/vnd.github.v3+json',
        }
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        api_response = requests.get(api_url, headers=headers, timeout=GITHUB_API_TIMEOUT)
        
        repo_info = ""
        if api_response.status_code == 200:
            data = api_response.json()
            repo_info = (
                f"[仓库信息]\n"
                f"名称: {data.get('name', 'N/A')}\n"
                f"描述: {data.get('description', '无描述') or 'N/A'}\n"
                f"Stars: {data.get('stargazers_count', 0):,}\n"
                f"Forks: {data.get('forks_count', 0):,}\n"
                f"语言: {data.get('language', 'N/A') or 'N/A'}\n"
                f"最后更新: {data.get('updated_at', 'N/A')}\n"
                f"项目主页: {data.get('html_url', 'N/A')}\n"
            )
        else:
            repo_info = f"[仓库信息] 获取失败 (HTTP {api_response.status_code})\n"
        
        readme_content = ""
        for branch in ['master', 'main', 'dev']:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            try:
                readme_response = requests.get(readme_url, headers=headers, timeout=GITHUB_API_TIMEOUT)
                if readme_response.status_code == 200:
                    readme_content = readme_response.text
                    if len(readme_content) > MAX_CONTENT_LENGTH:
                        readme_content = readme_content[:MAX_CONTENT_LENGTH] + "\n--- README已截断 ---"
                    break
            except Exception:
                continue
        
        if not readme_content:
            readme_content = "无法获取 README 文件"
        
        result = repo_info + "\n[README 内容]\n" + readme_content
        return result
        
    except Exception as e:
        return f"[GitHub 仓库获取失败]\nURL: {repo_url}\n错误: {str(e)}"


__all__ = ['search_github_repos', 'get_github_repo_info']
