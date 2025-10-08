#Date: 2025/06/02
#Desc: Assistant main func
#Author: lebin.lv
import os
import json
from datetime import datetime,timezone
from telegram_chat_bot import get_telegram_message,send_telegram_message
from chatgpt_conversations import chat_with_chatgpt
from prompts_config import SummarizeMessageByConversationPrompt
from request_config import request_chatgpt
from param_config import GlobalState as GS

# 默认保存地址
json_file = GS.json_file

#历史对话数量
limit = GS.history_limit

def read_conversations(chat_id):

    if not os.path.exists(json_file+str(chat_id)+'.json'):
        return '暂时没有历史对话消息'

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if len(data) == 0:
        return '暂时没有历史对话消息'

    # 防止记录不足
    recents = data[-limit:] if len(data) >= limit else data

    histories = ''
    for msgs in recents:
        histories += '\t- 当前聊天记录的时间：' + str(msgs['timestamp']) + '；\n '
        histories += '\t\t-- 发信人发来的消息是：' + str(msgs['message'][0]['content']).replace('\n','。') + '\n'
        histories += '\t\t-- 最后老人发出去的消息是：' + str(msgs['send_messages']).replace('\n','。') + '\n'

    histories = histories.strip('\t').strip('\n')
    return histories

def save_conversations(received_messages,interactive_messages,localtime,send_messages,chat_id):

    messages = [{'role':'sender','content':received_messages}]
    messages.extend(interactive_messages[1:])

    new_entry = {
        "message": messages,
        "timestamp": localtime,
        "send_messages": str(send_messages).strip('\n')
    }

    try:
        with open(json_file+str(chat_id)+'.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data.append(new_entry)
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)
    except FileNotFoundError:
        with open(json_file+str(chat_id)+'.json', 'w', encoding='utf-8') as f:
            json.dump([new_entry], f, indent=2, ensure_ascii=False)

def start():
    # 当GIPO收到消息时，获取telegram的最新消息
    received_messages, chat_id, utc_time = get_telegram_message()

    if not received_messages:
        # 如果没有收到任何消息，则默认时间为当前时间、chat_id为默认id，目标保存目录为当前时间戳的文件夹
        # 默认没有收到消息的回复
        received_messages = '您好，您的telegram当前还没有收到最新的消息。'
        # 当前时间的默认时间戳
        utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H:%M:%S")
        # 默认文件保存路径：判断文件夹是否存在，不存在则创建
        GS.FOLDER_PATH = "./AudioFiles/" + "audio_files_" + str(utc_time)
        if not os.path.exists(GS.FOLDER_PATH):
            os.makedirs(GS.FOLDER_PATH)
            print(f"文件夹已创建：{GS.FOLDER_PATH}")
        else:
            print(f"文件夹已存在：{GS.FOLDER_PATH}")
        # 默认发送消息目标的id
        chat_id = GS.chat_id

    # 读取历史对话记录
    histories = read_conversations(chat_id)

    # 利用chatgpt进行本地交互
    interactive_messages = chat_with_chatgpt(received_messages, histories)

    # 将交互的对话信息进行问题总结Messages
    send_messages_prompt = SummarizeMessageByConversationPrompt(received_messages, interactive_messages)
    print(send_messages_prompt)
    send_messages = request_chatgpt([{"role": "system", "content": send_messages_prompt}])
    print("MessagesToSendAfterSummary：\n", send_messages)

    # 将当前对话保存到json
    save_conversations(received_messages, interactive_messages, utc_time, send_messages, chat_id)

    if 'no_question' not in str(send_messages):
        for send_msg in str(send_messages).split('\n'):
            send_telegram_message(chat_id, send_msg)


if __name__ == '__main__':

    start()


