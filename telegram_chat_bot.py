#Date: 2025/06/02
#Desc: use telegram to receive and send messages
#Author: lebin.lv
import os
from datetime import datetime,timezone
import requests
from request_config import speech_to_text
from param_config import GlobalState as GS


def get_updates(offset=None):
    url = f'https://api.telegram.org/bot{GS.BOT_TOKEN}/getUpdates'
    params = {'timeout': 5, 'offset': offset}
    response = requests.get(url, params=params)
    # print("response:",response.json())
    return response.json()

def send_telegram_message(chat_id, text):
    url = f'https://api.telegram.org/bot{GS.BOT_TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=payload)

def download_file(file_path, file_name):
    file_url = f'https://api.telegram.org/file/bot{GS.BOT_TOKEN}/{file_path}'
    response = requests.get(file_url)
    with open(file_name, 'wb') as f:
        f.write(response.content)
    print(f'语音已保存为：{file_name}')


def get_telegram_message():
    offset = None

    chat_id = ''
    utc_time = ''
    updates = get_updates(offset)
    received_messages = ''
    for update in updates['result']:
        message = update.get('message')
        print(message)

        # 获取chat_id
        chat_id = message['chat']['id']
        # 将时间戳转换为UTC时间
        if len(str(utc_time)) == 0:
            date_time = message['date']
            utc_time = datetime.fromtimestamp(date_time,tz=timezone.utc).strftime("%Y-%m-%d_%H:%M:%S")

            GS.FOLDER_PATH = "./AudioFiles/" + "audio_files_" + str(utc_time)
            # 判断文件夹是否存在，不存在则创建
            if not os.path.exists(GS.FOLDER_PATH):
                os.makedirs(GS.FOLDER_PATH)
                print(f"文件夹已创建：{GS.FOLDER_PATH}")
            else:
                print(f"文件夹已存在：{GS.FOLDER_PATH}")

        # 检查是否有语音消息
        if 'voice' in message:
            voice = message['voice']
            file_id = voice['file_id']

            # 获取文件路径
            file_info_url = f'{GS.BASE_URL}/getFile?file_id={file_id}'
            file_info = requests.get(file_info_url).json()
            file_path = file_info['result']['file_path']

            # 下载文件
            filename = f"{GS.FOLDER_PATH}/{file_id}_from_sender.wav"
            download_file(file_path, filename)
            text = speech_to_text(filename)

        else:

            text = message.get('text', '')

        received_messages += text + '\n'

        offset = update['update_id'] + 1

    # 将历史对话置空，保证最新访问是新的消息
    if offset:
        get_updates(offset)

    return received_messages, chat_id, utc_time

if __name__ == '__main__':
    get_telegram_message()