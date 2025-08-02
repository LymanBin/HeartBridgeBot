# -*- coding: utf-8 -*-
# Date: 20250309
# Author: lebin.lv
# Desc: 用于存放访问 接口地址
import os
import time
import openai
import requests
from param_config import GlobalState as GS


if not GS.openai_key:
    raise EnvironmentError("OPENAI_KEY not found in environment variables.")

# chatgpt
def request_chatgpt(message):
    client = openai.OpenAI(api_key=GS.openai_key)

    response = client.chat.completions.create(
        model="o4-mini-2025-04-16",  # 改为 gpt-3.5-turbo
        messages=message
        )
    # print(response)
    message_content = response.choices[0].message.content

    return message_content

# STT
def speech_to_text(path):
    client = openai.OpenAI(api_key=GS.openai_key)
    audio_file = open(path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

    return transcription

# TTS
def text_to_speech_openai(text,folder_path,role):
    openai.api_key = GS.openai_key  # 建议使用环境变量

    # 发送请求
    response = openai.audio.speech.create(
        model="tts-1",           # 可选："tts-1" 或 "tts-1-hd"
        voice="onyx",            # 可选：alloy, echo, fable, onyx, nova, shimmer
        input=text
    )

    timestamp = str(time.time_ns()).replace(' ','_')

    # 保存到本地文件
    with open(f"{folder_path}/output_"+timestamp+"_"+role+".mp3", "wb") as f:
        f.write(response.content)

    print("✅ Save Audio File "+folder_path+"/output_"+timestamp+"_"+role+".mp3")

    return timestamp


def text_to_speech_elevenlabs(text,folder_path,role):
    api_key = GS.eleven_key

    voice_id = GS.voice_id
    voice_dict_v2 = {'Rachel': '21m00Tcm4TlvDq8ikWAM', 'Drew': '29vD33N1CtxCmqQRPOHJ', 'Clyde': '2EiwWnXFnvU5JabPnv8n',
                     'Paul': '5Q0t7uMcjvnagumLfvZi', 'Aria': '9BWtsMINqrJLrRacOk9x', 'Domi': 'AZnzlk1XvdvUeBnXmlld',
                     'Dave': 'CYw3kZ02Hs0563khs1Fj', 'Roger': 'CwhRBWXzGAHq8TQ4Fs17', 'Fin': 'D38z5RcWu1voky8WS1ja',
                     'Sarah': 'EXAVITQu4vr4xnSDxMaL'}


    # === 请求地址 ===
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    # === 请求头 ===
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    # === 请求体 ===
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # 可选模型，也可尝试 "eleven_multilingual_v2"
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    # === 发起请求 ===
    response = requests.post(url, headers=headers, json=data)

    # === 处理返回结果 ===
    timestamp = str(time.time_ns()).replace(' ','_')

    # 保存到本地文件
    with open(f"{folder_path}/output_"+timestamp+"_"+role+".mp3", "wb") as f:
        f.write(response.content)

    print("✅ Save Audio File "+folder_path+"/output_"+timestamp+"_"+role+".mp3")

    return timestamp

