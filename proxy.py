"""
GitHub 代理服务 - 可部署到 Railway/Render
免费、稳定、全球加速
"""

from flask import Flask, request, Response, redirect
import requests
import os

app = Flask(__name__)

# GitHub 基础 URL
GITHUB_RAW = "https://raw.githubusercontent.com"
GITHUB_RELEASES = "https://github.com"

@app.route('/')
def index():
    return """GitHub 代理服务

用法：
  /gh/owner/repo@tag/file
  
示例：
  /gh/dorkrue-756/niuniu@v2.0/config.zip
"""

@app.route('/gh/<path:path>')
def proxy(path):
    """
    格式: owner/repo@tag/file
    例如: dorkrue-756/niuniu@v2.0/config.zip
    """
    # 解析路径
    parts = path.split('@')
    if len(parts) < 2:
        return "格式错误！使用: /gh/owner/repo@tag/file", 400
    
    repo_part = parts[0]  # owner/repo
    file_path = '@'.join(parts[1:])  # tag/file
    
    # 构建 GitHub URL
    if '/releases/download/' in file_path:
        # Release 文件
        github_url = f"https://github.com/{repo_part}/releases/download/{file_path}"
    else:
        # Raw 文件
        github_url = f"https://raw.githubusercontent.com/{repo_part}/{file_path}"
    
    # 转发请求
    try:
        r = requests.get(github_url, stream=True, timeout=60)
        
        if r.status_code == 404:
            return "文件不存在", 404
        elif r.status_code != 200:
            return f"GitHub 错误: {r.status_code}", r.status_code
        
        # 返回原始响应
        return Response(
            r.content,
            status=200,
            headers=dict(r.headers)
        )
    except Exception as e:
        return f"代理失败: {str(e)}", 502

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
