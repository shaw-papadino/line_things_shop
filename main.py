import os
import sys
import json
import responder
import base64
import asyncio
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
from write import run, mac_addr, WRITE_CHARACTERISTIC_UUID

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
    body = json.dumps(body, ensure_ascii=False).replace(' ', '')

    try:
        handler.handle(body, signature)
        resp.status_code = 200
        resp.text = "OK"
    except InvalidSignatureError:
       resp.status_code = api.status_codes.HTTP_503
       resp.text = "miss"

###
# deviceからメッセージ受信時
###
@handler.add(ThingsEvent)
def handle_message(event):

    if event.things is None:
        print(event)
        return
    if event.things.type != "scenarioResult":
        print(event)
        return
    if event.things.result.result_code != "success":
        print(event)
        return

    message = base64.b64decode(event.things.result.ble_notification_payload).decode()
    if message[0] == "S":
        liff_url = "https://liff.line.me/1655338407-PZBX17Wz"
        line_bot_api.reply_message(
           event.reply_token,
           TextSendMessage(text="今アンケートに答えると割引チャンス!\n" + liff_url)
        )
    else:
        line_bot_api.reply_message(
           event.reply_token,
           TextSendMessage(text="対応していません")
        )


###
# メッセージ受信時
###
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "送信しました":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run(mac_addr, loop))
        line_bot_api.reply_message(
           event.reply_token,
           TextSendMessage(text="割引されるのでお待ちを")
        )
        


if __name__=="__main__":
    # port = int(os.environ.get("PORT", 5000))
    api.run(address="0.0.0.0")
