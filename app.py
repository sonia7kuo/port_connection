import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# 環境變數設定
LINE_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
OPENCLAW_API_KEY = os.getenv('OPENCLAW_API_KEY')
OPENCLAW_API_URL = 'https://soniaopenclaw.zeabur.app/v1/chat/completions'
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-1.5-pro')

@app.route("/webhook", methods=['POST'])
def webhook():
    body = request.get_json()
    events = body.get('events', [])
    
    for event in events:
        if event.get('type') == 'message' and event['message']['type'] == 'text':
            reply_token = event['replyToken']
            user_text = event['message']['text']
            
            # 向 OpenClaw 提問
            headers = {
                "Authorization": f"Bearer {OPENCLAW_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": user_text}]
            }
            
            try:
                res = requests.post(OPENCLAW_API_URL, json=payload, headers=headers)
                ai_reply = res.json()['choices'][0]['message']['content']
            except:
                ai_reply = "系統回應超時，請稍後再試。"

            # 回傳訊息給 Line
            line_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
            }
            line_payload = {
                "replyToken": reply_token,
                "messages": [{"type": "text", "text": ai_reply}]
            }
            requests.post("https://api.line.me/v2/bot/message/reply", 
                          json=line_payload, headers=line_headers)
            
    return 'OK'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
