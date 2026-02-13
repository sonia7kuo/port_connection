import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 這些資訊之後要在 Zeabur 的「環境變數」設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
OPENCLAW_API_URL = os.getenv('OPENCLAW_API_URL', 'https://soniaopenclaw.zeabur.app/v1/chat/completions')
OPENCLAW_API_KEY = os.getenv('OPENCLAW_API_KEY') # 這裡填你的 Gateway Token
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-1.5-pro')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # 呼叫 OpenClaw API
    headers = {
        "Authorization": f"Bearer {OPENCLAW_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": user_text}]
    }

    try:
        response = requests.post(OPENCLAW_API_URL, json=payload, headers=headers)
        response_data = response.json()
        ai_reply = response_data['choices'][0]['message']['content']
    except Exception as e:
        ai_reply = f"系統忙碌中，請稍後再試。錯誤代碼: {str(e)}"

    # 回傳給 Line 使用者
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ai_reply))

if __name__ == "__main__":
    # Zeabur 預設通常使用 8080 或環境變數中的 PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
