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

    # STT prompt优化语音识别能力
    SttPrompt = "这段音频为中文"

    # 文本数据保存路径
    json_file = './Histories/conversation_histories_'

    # 录音参数设置
    duration = 10  # 录音时长（秒）
    samplerate = 44100  # 采样率（Hz）
    threshold = -55.0  # 判断总音量的阈值

    # 流式录音/分块录音 参数
    block_duration_sec = 0.5
    threshold2 = 0.01  # 流式录音音量阈值
    silence_duration = 5.0  # 说话后静默时长超过 5 秒静音就停止
    not_start_duration = 3.0  # 开始录音后多久时间内都没有说话，则直接停止进行反问

    # 历史消息轮数
    history_limit = 5

    # 默认消息发送的id
    chat_id = ''
    