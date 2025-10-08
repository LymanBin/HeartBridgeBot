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
import platform
import numpy as np
from pydub import AudioSegment
import queue
system_name = platform.system()


# 流式录音，分块检测音频大小和录音时长
def load_voice_stream_and_stt():
    # 定义一个录音块的大小
    q = queue.Queue()
    block_size = int(GS.samplerate * GS.block_duration_sec)

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    with ((sd.InputStream(samplerate=GS.samplerate, channels=1, blocksize=block_size, callback=callback))):
        print("开始录音，检测到说话后，如果连续 5 秒静音就结束...")
        silent_blocks = 0
        not_start_blocks = 0
        audio = []
        heard_voice = False  # 标记是否已经检测到有人说话

        while True:
            block = q.get()
            audio.append(block)
            volume = np.sqrt(np.mean(block ** 2))
            # print(f"音量: {volume:.5f}")  # 调试用
            # print(silent_blocks)
            if volume > GS.threshold2:
                heard_voice = True
                # silent_blocks = 0  # 重置静音计数
                # not_start_blocks = 0
            else:
                if heard_voice:  # 只有在听到声音后才开始计时
                    silent_blocks += 1
                else:
                    not_start_blocks += 1

            # print(volume)
            # print(not_start_blocks)
            # 如果说话后检测静默时长是否达到阈值停止 / 多少秒内一直没有说话也停止
            if heard_voice and silent_blocks * GS.block_duration_sec > GS.silence_duration:
                print("总录音中检测到 5 秒静默，结束录音。")
                voice_flag = 1
                break
            elif not heard_voice and not_start_blocks * GS.block_duration_sec > GS.not_start_duration:
                print("检测到 3 秒仍没有满足阈值的声音，结束录音。")
                voice_flag = 2
                break

    if voice_flag == 1:
        recorded = np.concatenate(audio, axis=0)
        print(f"录音长度: {len(recorded) / GS.samplerate:.2f} 秒")
        print("Recording finished. Saving file ...")

        timestamp = str(time.time())
        filename = f'{GS.FOLDER_PATH}user_' + 'input_' + str(timestamp) + '.wav'  # 输出文件名
        write(filename, GS.samplerate, recorded)
        print(f"Save Audio File {filename}")
        transcription = speech_to_text(filename)
        print(transcription)

        return transcription
    else:
        print("音量太低，可能无语音")
        return False


# 固定对用户录音10S
def load_voice_and_stt():

    print("Start Recording...")
    recording = sd.rec(int(GS.duration * GS.samplerate), samplerate=GS.samplerate, channels=1, dtype='int16')
    sd.wait()  # 等待录音结束

    # 音量检测
    # audio_data 是 NumPy 数组，需要转换成 AudioSegment
    audio_segment = AudioSegment(
        recording.tobytes(),  # 转为字节
        frame_rate=GS.samplerate,
        sample_width=recording.dtype.itemsize,  # int16 -> 2 bytes
        channels=1
    )

    # 检测音量
    print("平均音量 dBFS:", audio_segment.dBFS)

    # 判断是否有语音（阈值可调）
    if audio_segment.dBFS <= GS.threshold:
        print("音量太低，可能无语音")
        return False

    print("Recording finished. Saving file ...")

    timestamp = str(time.time())
    filename = f'{GS.FOLDER_PATH}/user_' + 'input_' + str(timestamp) +'.wav'  # 输出文件名
    write(filename, GS.samplerate, recording)
    print(f"Save Audio File {filename}")
    transcription = speech_to_text(filename)

    return transcription

def generate_and_tts(return_message,role):
    timestamp = text_to_speech_openai(return_message,GS.FOLDER_PATH,role)
    # timestamp = text_to_speech_elevenlabs(return_message,GS.FOLDER_PATH,role)

    print("Play Audio：",f"{GS.FOLDER_PATH}/output_" + timestamp + '_' + role + ".mp3")
    if system_name == "Linux":
        os.system(f"mpg123 -q {GS.FOLDER_PATH}/output_" + timestamp + '_' + role + ".mp3")  # macOS 播放命令
    else:
        os.system(f"afplay {GS.FOLDER_PATH}/output_" + timestamp + '_' + role + ".mp3")  # macOS 播放命令
    # os.system("mpg123 output.mp3")  # Linux 树莓派使用 mpg123 播放ni

def chat_with_chatgpt(new_message,histories):

    # 首先将获取到的最新消息进行播报
    generate_and_tts(new_message,'sender')

    # 封装当前内容为历史前文
    messages = [{"role": "system", "content": InteractivatePrompt(new_message,histories)}]

    while True:
        # 录音，等待用户回复
        ## 固定时长的录音
        # user_message = load_voice_and_stt()
        ## 流式录音
        user_message = load_voice_stream_and_stt()

        # 如果音量过低或者没有收到任何语音回复
        if not user_message:
            user_message = '[用户无语音回复]'

        print("user message: ", user_message)
        messages.append({"role": "user", "content": user_message})

        if user_message == '[用户无语音回复]':
            return_message = '不好意思，我没有听清您说什么，可以麻烦您再大声说一点吗。'
        else:
            # 根据用户回复发送给chatgpt进行交互
            return_message = str(request_chatgpt(messages)).replace('\n','')

        generate_and_tts(return_message,'assistant')
        print("ChatGPT :", return_message)
        messages.append({"role": "assistant", "content": return_message})

        if '【END】' in return_message:  # 退出检测
            break

    return messages

if __name__ == '__main__':

    load_voice_stream_and_stt()