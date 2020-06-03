from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import requests
from bs4 import BeautifulSoup
import re
import random

import sys
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('gUmmvJaLjzzkg+DSUBhYN0laIOwATFnWqs3fALBjUpve6/EY7gI+om7JsRHKiEPgalOnKqdLyWAAAXzq7UtNAMEJ7oIU6ozZVk0XunGo5iYhJXcU3xqqK/mCPWUGdASr+kdDwQ7+EW7nBazTvVSYkAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('7a049b14d17a6ae69f8f39aabfc0c86f')

# 監聽所有來自 /callback 的 Post Request
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


def ptt(bd):
    web='https://www.ptt.cc/bbs/'+bd+'/index.html'
    apple = requests.get(web)
    pineapple = BeautifulSoup(apple.text,'html.parser')
    last = pineapple.select('div.btn-group-paging a')
    last_web = 'https://www.ptt.cc'+last[1]['href']
    apple = requests.get(last_web)
    pineapple = BeautifulSoup(apple.text,'html.parser')
    article = pineapple.select('div.title a')
    random.shuffle(article)
    re_imgur = re.compile('http[s]?://i.imgur.com/\w+\.(?:jpg)')
    for tit in article:
        apple = requests.get('https://www.ptt.cc'+tit['href'])
        images = re_imgur.findall(apple.text)
        if len(images)!=0:
            break
    num=random.randint(0,len(images)-1)
    return images[num]



# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):


    msg = event.message.text
    #print(type(msg))
    msg = msg.encode('utf-8')  
    if "文字" in event.message.text:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
    elif event.message.text == "正":
        a=ptt("Beauty")
        print(a)
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=a, preview_image_url=a))
    elif event.message.text == "大":  #可能有1MB的限制
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='http://i.imgur.com/CS1FI7L.jpg', preview_image_url='http://i.imgur.com/CS1FI7L.jpg'))
    elif event.message.text == "貓貓":
        a=ptt("cat")
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=a, preview_image_url=a))
    elif event.message.text == "貼圖":
        line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=1, sticker_id=2))
    elif event.message.text == "圖片":
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='圖片網址', preview_image_url='圖片網址'))
    elif event.message.text == "影片":
        line_bot_api.reply_message(event.reply_token,VideoSendMessage(original_content_url='影片網址', preview_image_url='預覽圖片網址'))
    elif event.message.text == "音訊":
        line_bot_api.reply_message(event.reply_token,AudioSendMessage(original_content_url='音訊網址', duration=100000))
    elif "!" in event.message.text:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="紀錄成功"))
        pass
        #GDriveJSON就輸入下載下來Json檔名稱
        #GSpreadSheet是google試算表名稱
        GDriveJSON = 'LineBot.json'
        GSpreadSheet = 'esun108'
        while True:
            try:
                scope = ['https://docs.google.com/spreadsheets/d/1_VDqxPO3vKaiOIqDTFqtK8hayVdB3DE4n6FBgvYxt9M/edit?usp=sharing']
                key = SAC.from_json_keyfile_name(GDriveJSON, scope)
                gc = gspread.authorize(key)
                worksheet = gc.open(GSpreadSheet).sheet1
            except Exception as ex:
                print('無法連線Google試算表', ex)
                sys.exit(1)
            textt=""
            textt+=event.message.text
            if textt!="":
                worksheet.append_row((datetime.datetime.now(), textt))
                print('新增一列資料到試算表' ,GSpreadSheet)
                return textt    
    return 'OK2'

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
