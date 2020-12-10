import os
import sys
import json
import responder
import base64
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
            MessageEvent,
            TextMessage,
            TextSendMessage,
            BeaconEvent,
            ThingsEvent,
            ScenarioResult,
            TemplateSendMessage,
            ImageSendMessage,
            TextSendMessage
        )
from pathlib import Path

print(os.getcwd())
print(__file__)
ROOT_DIR = Path(__file__).resolve().parents[0]
api = responder.API(
    static_dir = str(ROOT_DIR.joinpath("static"))
)

###
# line botのトークンなどを設定
###
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@api.route("/")
def nopage(req, resp):
    resp.text = "404: This is not a webpage you are looking for."
    resp.status_code = api.status_codes.HTTP_404

@api.route("/test")
def test(req, resp):
    resp.text = "OK"

###
# liffページを開く
###
@api.route("/open")
def open_liff(req, resp):
    resp.html = api.template("index.html")

@api.route("/callback")
async def callback(req, resp):
    signature = req.headers["X-Line-Signature"]
    body = await req.media()
    print("Request body: " + body, flush=True)
    print(signature)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
       resp.status_code = api.status_codes.HTTP_503
       return
    resp.text = "OK"
    # else:
    #     resp.text = "404: This is not a webpage you are looking for."
    #     resp.status_code = api.status_codes.HTTP_404

###
# Beaconからメッセージ受信時
###
@handler.add(BeaconEvent)
def handle_message(event):
    messages = create_carousel_column(create_carousel(carousel))
    
    line_bot_api.reply_message(event.reply_token, messages)


###
# deviceからメッセージ受信時
###
@handler.add(ThingsEvent)
def handle_message(event):
    # things auro communication
    # 始めたこと
    # 終わったこと
    # 何回ポモドーロしたか
    if event.things.type != "scenarioResult":
        print(event)
        return
    if event.things.result.result_code != "success":
        print(event)
        return
    pomodoro_num = base64.b64decode(event.things.result.ble_notification_payload).decode()
    if pomodoro_num[0] == "S":
        mes = "{}ポモドーロ始めるよ！".format(pomodoro_num[1])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=mes))
    elif pomodoro_num[0] == "F":
        mes = "{}ポモドーロ終了したよ.\nゆっくり休んでね.".format(pomodoro_num[1])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=mes))

###
# メッセージ受信時
###
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text_message = TextSendMessage(text="!")
    line_bot_api.reply_message(
       event.reply_token,
       TextSendMessage(text=text_message)
    )


if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    api.run(address="0.0.0.0", port=port)
