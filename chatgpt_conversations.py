#Date: 2025/06/02
#Desc: chatgpt chatting
#Author: lebin.lv
import os
import time
from prompts_config import InteractivatePrompt
from request_config import request_chatgpt,text_to_speech_openai,speech_to_text,text_to_speech_elevenlabs
import sounddevice as sd
from scipy.io.wavfile import write
from param_config import GlobalState as GS


def load_voice_and_stt():
    # 参数设置
    duration = GS.duration  # 录音时长（秒）
    samplerate = GS.samplerate  # 采样率（Hz）

    print("Start Recording...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # 等待录音结束
    print("Recording finished. Saving file ...")

    timestamp = str(time.time_ns())
    filename = f'{GS.FOLDER_PATH}/user_' + 'input' + str(timestamp) +'.wav'  # 输出文件名
    write(filename, samplerate, recording)
    print(f"Save Audio File {filename}")
    transcription = speech_to_text(filename)

    return transcription

def generate_and_tts(return_message,role):
    # 两种转语音方式可选
    timestamp = text_to_speech_openai(return_message,GS.FOLDER_PATH,role)
    # timestamp = text_to_speech_elevenlabs(return_message,GS.FOLDER_PATH,role)

    print("Play Audio：",f"{GS.FOLDER_PATH}/output_" + timestamp + '_' + role + ".mp3")
    os.system(f"afplay {GS.FOLDER_PATH}/output_" + timestamp + '_' + role + ".mp3")  # macOS 播放命令
    # os.system("mpg123 output.mp3")  # Linux 树莓派使用 mpg123 播放ni

def chat_with_chatgpt(new_message,histories):

    # 首先将获取到的最新消息进行播报
    generate_and_tts(new_message,'sender')

    # 封装当前内容为历史前文
    messages = [{"role": "system", "content": InteractivatePrompt(new_message,histories)}]

    while True:
        # 等待用户回复
        user_message = load_voice_and_stt()
        print("user message: ", user_message)
        messages.append({"role": "user", "content": user_message})

        # 根据用户回复发送给chatgpt进行交互
        return_message = str(request_chatgpt(messages)).replace('\n','')
        generate_and_tts(return_message,'assistant')
        print("ChatGPT :", return_message)

        messages.append({"role": "assistant", "content": return_message})

        if '【END】' in return_message:  # 退出检测
            break

    return messages
