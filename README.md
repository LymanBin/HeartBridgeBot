# 项目名称

HeartBridge-老人陪护机器人

## 🧠 项目简介

帮助老人接收家人发来的telegram消息，并通过语音告诉老人，与老人进行多轮交互，将老人的问题或者回复再转发给发信人，实现全语音沟通。
合作伙伴：@RUTH @W

例如：
[查看对话示例](./Histories/conversation_histories.json)

## 🛠️ 技术栈

- Python 3.11
- 依赖库：AI能力全部基于外部接口调用，包括openai、eleven labs、hume。基本只需要考虑本地录音与播放的工具包需要与本身环境适配


## 📦 安装与运行
- 可以通过gpio_control.py实现外部硬件控制启动聊天，这里采用的是一个简单的电位器进行控制。
- main.py直接实现本地代码执行交互


欢迎 PR 和 issue！