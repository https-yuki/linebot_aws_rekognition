"""
オウム返し Line Bot
"""

import os
import boto3

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)

handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
client = boto3.client('rekognition')

def lambda_handler(event, context):
    headers = event['headers']
    body = event['body']

    # get X-Line-Signature header value
    signature = headers['x-line-signature']

    # handle webhook body
    handler.handle(body, signature)

    return {'statusCode': 200, 'body': 'OK'}

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """ TextMessage handler """
    input_text = event.message.text

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=input_text))
    
@handler.add(MessageEvent, message=ImageMessage)
def hongle_image_message(event):

    # ユーザーから送られてきた画像を一時ファイルとして保存
    message_content = line_bot_api.get_message_content(event.message.id)
    temp_dir = '/tmp'
    file_path = os.path.join(temp_dir, 'sent-image.jpg')
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    # Rekognitionで感情分析する
    with open(file_path, 'rb') as fd:
        sent_image_binary = fd.read()
        response = client.detect_faces(
            Image={'Bytes': sent_image_binary},
            Attributes=['ALL']
        )

    # 返信内容を取得する
    most_confidence_emotion = max(response['FaceDetails'][0]['Emotions'], key=lambda x: x["Confidence"])['Type']
    message = response_message(most_confidence_emotion)

    # 返信内容を送信する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

    # file_pathの画像を削除する
    os.remove(file_path)

# 返信内容を作成する
def response_message(emotion):
    if emotion == 'HAPPY':
        result = 'いい笑顔ですね！'
    elif emotion == 'CONFUSED':
        result = '考え事してますね。'
    elif emotion == 'CALM':
        result = '落ち着いてますね。'
    elif emotion == 'ANGRY':
        result = '怒ってますね。'
    elif emotion == 'DISGUSTED':
        result = 'うんざりしてますね。'
    elif emotion == 'FEAR':
        result = '何かを恐れていますね。'
    elif emotion == 'SAD':
        result = '悲しんでますね。'
    elif emotion == 'SURPRISED':
        result = '驚いていますね。'
    else:
        result = 'どんな表情かわかりません。'
    return result