import requests

# 示例：假设有 API 登录/访问链接（需要你具体的 URL 和 API 密钥）
url = "https://api.anthropic.com/v1/chat/completions"
headers = {
    "Authorization": "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",  # 替换为你的 API 密钥
    "Content-Type": "application/json",
}

# 发送一个请求（可以根据需求修改为 POST 请求）
response = requests.get(url, headers=headers)

# 打印返回的 Cookie
print(response)
