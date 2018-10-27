import json
import requests
import os
import time

import errno
import sys
import tempfile
import random
from argparse import ArgumentParser
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
# change channel_secret and channel_access_token from your line developer


line_bot_api = LineBotApi('XmfQvyUoEaw8l2kUw+bBAVDEUpW66IGgQ79AhTyw11gCDzQdE6Fk1T2IrIFM1ZGHJEicBb4nNA65hCtWe49p/9V5Rh/bFdfij14WnDpqq76JYK2cMC19PTA4n8rXvHyiT8F+Tznov5wjRmxV4X05PQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a595a1580b3f5399ad9175c7b8e18f6c')

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# change this variable with your server API 
api_url = "http://35.229.124.57"
api_port = ":5000"
api_route = "/predict"

@app.route("/test", methods=['GET'])
def test():
    sys.stdout.write("test request received\n")
    return "test"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Nanti fungsi request_api ini diletakkan seperti ini:
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    question = event.message.text
    if(question=='halochatbotdara'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='hai'))
    else:
        answer = request_api(question)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answer))

def request_api(question):
    url = api_url + api_port + api_route
    payload = {"question": question}

    response_data = ""
    while response_data == "":
        try:
            print "ISSUING POST REQUEST..."
            session = requests.Session()
            req = session.post(url, data=payload, timeout=15)
            response_data = str(req.text)
        except:
            print "Connection timeout..."
            print "Retrying post request..."
            time.sleep(1)
            continue
    
    response_data = json.JSONDecoder().decode(response_data)
    return response_data["answer"]

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)

