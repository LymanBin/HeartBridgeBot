# -*- coding: utf-8 -*-
# Date: 2025/08/02
# Desc: param config
# Author: lebin.lv
# 定义全局变量，可被修改

class GlobalState:
    # telegram 账号信息配置，要自己申请配置
    BOT_TOKEN = 'telegrams_BOT_TOKEN'
    BASE_URL = f'telegrams_base_url'
    FOLDER_PATH = './outputs/'
    offset = None

    # openai api key，要自己申请配置
    openai_key = "openai_api_key"

    # eleven labs settings ，要自己申请配置
    eleven_key = "eleven_labs_api_key"
    voice_id = "eleven_labs_voice_id"

    # 文本数据保存路径
    json_file = './Histories/conversation_histories.json'

    # 录音参数设置
    duration = 10  # 录音时长（秒）
    samplerate = 44100  # 采样率（Hz）


