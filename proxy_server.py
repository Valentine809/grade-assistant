from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# ========== 在这里设置你的密钥 ==========
DEEPSEEK_API_KEY = "sk-你的新密钥"  # 改成你在DeepSeek后台新生成的密钥
# =====================================

@app.route('/proxy/chat', methods=['POST'])
def proxy_chat():
    try:
        # 1. 接收前端传来的数据
        frontend_data = request.json
        messages = frontend_data.get('messages', [])
        temperature = frontend_data.get('temperature', 0.7)
        max_tokens = frontend_data.get('max_tokens', 500)

        # 2. 用你的密钥调用DeepSeek
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # 3. 把DeepSeek的回复原样返回给前端
        return jsonify(response.json())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)