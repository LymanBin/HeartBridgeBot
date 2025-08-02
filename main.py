#Date: 2025/06/02
#Desc: Assistant main func
#Author: lebin.lv
import os
import json
from telegram_chat_bot import get_telegram_message,send_telegram_message
from chatgpt_conversations import chat_with_chatgpt
from prompts_config import SummarizeMessageFromOther,SummarizeMessageByConversationPrompt
from request_config import request_chatgpt
from param_config import GlobalState as GS

# 默认保存地址
json_file = GS.json_file

#历史对话数量
limit = 10

def read_conversations():

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if len(data) == 0:
        return '暂时没有历史对话'

    # 防止记录不足
    recents = data[-limit:] if len(data) >= limit else data

    histories = ''
    for msgs in recents:
        histories += '- 当前聊天记录的时间：' + msgs['timestamp'] + '\n'
        for msg in msgs['message']:
            histories += '\t-- ' + msg['role'] + ': ' + msg['content'] + '\n'
        histories += '\n'

    sender_histories = ''
    for msgs in recents:
        sender_histories += '- 当前聊天记录的时间：' + msgs['timestamp'] + '； '
        sender_histories += '发信人发来的消息是：' + msgs['message'][0]['content'].replace('\n','。')
        sender_histories += '\n'

    return sender_histories


def save_conversations(received_messages,interactive_messages,localtime):

    messages = [{'role':'sender','content':received_messages}]
    messages.extend(interactive_messages[1:])

    new_entry = {
        # "sender": sender,
        # "receiver": receiver,
        "message": messages,
        "timestamp": localtime
    }

    try:
        with open(json_file, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data.append(new_entry)
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)
    except FileNotFoundError:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([new_entry], f, indent=2, ensure_ascii=False)

def start():

    # 当GIPO收到消息时，获取telegram的最新消息
    received_messages, chat_id, local_time = get_telegram_message()

    if not received_messages:
        received_messages = '您好，您的telegram当前还没有收到最新的消息。'

    # 读取历史对话记录，近两次
    histories = read_conversations()

    # 利用chatgpt进行本地交互
    interactive_messages = chat_with_chatgpt(received_messages,histories)

    #将当前对话保存到json
    save_conversations(received_messages,interactive_messages,local_time)

    # 将交互的对话信息进行问题总结Messages
    send_messages = SummarizeMessageByConversationPrompt(received_messages,interactive_messages)
    print(send_messages)
    send_messages = request_chatgpt([{"role": "system", "content": send_messages}])
    print("MessagesToSendAfterSummary：\n",send_messages)
    if 'no_question' not in str(send_messages):
        for send_msg in str(send_messages).split('\n'):
            send_telegram_message(chat_id, send_msg)


if __name__ == '__main__':

    start()


