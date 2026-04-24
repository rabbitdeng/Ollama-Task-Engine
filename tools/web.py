"""
网页内容抓取模块
===============

提供网页内容抓取和 HTML 纯文本提取功能。

本模块提供：
- fetch_page: 获取网页内容并自动提取纯文本
- extract_text_from_html: 从 HTML 内容中提取纯文本
"""

import requests
from typing import Final
from bs4 import BeautifulSoup

WEB_REQUEST_TIMEOUT: Final[int] = 15
MAX_CONTENT_LENGTH: Final[int] = 3000
USER_AGENT: Final[str] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def extract_text_from_html(html_content: str) -> str:
    """
    从 HTML 内容中提取纯文本
    
    使用 BeautifulSoup 解析 HTML，移除脚本、样式、导航栏、页脚等无关元素，
    提取可读的纯文本内容。
    
    Args:
        html_content: HTML 字符串
        
    Returns:
        纯文本字符串（去除多余空行和空格）
        
    Example:
        >>> html = "<html><body><h1>Hello</h1><p>World</p></body></html>"
        >>> extract_text_from_html(html)
        "Hello
        World"
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        text = soup.get_text(separator='\n', strip=True)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        return f"[ERROR] HTML parsing failed: {str(e)}"


def fetch_page(url: str) -> str:
    """
    获取网页内容（自动提取纯文本）
    
    抓取指定 URL 的网页内容，自动提取纯文本并进行格式化。
    内容过长时自动截断到 3000 字符。
    
    Args:
        url: 要获取的网页 URL
        
    Returns:
        格式化的页面内容字符串
        
    Example:
        >>> fetch_page("https://example.com")
        "[页面获取成功]
        URL: https://example.com
        ---
        Example Domain
        This domain is for use in illustrative examples in documents.
        ...
        --- 内容结束 ---"
        
    Note:
        - 使用自定义 User-Agent 模拟浏览器请求
        - 自动检测编码
        - 内容超过 3000 字符自动截断
        - 请求超时时间为 15 秒
    """
    try:
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        response = requests.get(url, headers=headers, timeout=WEB_REQUEST_TIMEOUT)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        content = extract_text_from_html(response.text)
        
        if len(content) > MAX_CONTENT_LENGTH:
            truncated = content[:MAX_CONTENT_LENGTH]
            return (
                f"[页面获取成功]\n"
                f"URL: {url}\n"
                f"内容长度: {len(content)} 字符 (已截断至 {MAX_CONTENT_LENGTH} 字符)\n"
                f"---\n{truncated}\n--- 内容已截断 ---"
            )
        else:
            return (
                f"[页面获取成功]\n"
                f"URL: {url}\n"
                f"---\n{content}\n--- 内容结束 ---"
            )
            
    except requests.exceptions.Timeout:
        return f"[ERROR] 页面请求超时: {url}"
    except requests.exceptions.RequestException as e:
        return f"[ERROR] 页面获取失败\nURL: {url}\n错误: {str(e)}"
    except Exception as e:
        return f"[ERROR] 页面获取失败\nURL: {url}\n错误: {str(e)}"


__all__ = ['fetch_page', 'extract_text_from_html']
