# -*- coding: utf-8 -*-
# Date: 2025/05/12
# Desc: external control
# Author: lebin.lv
import RPi.GPIO as GPIO
import time
from main import start

# 设置为 BCM 编号模式
GPIO.setmode(GPIO.BCM)

# 假设传感器连接在 GPIO17（BCM 编号）
SENSOR_PIN = 21

# 设置为输入引脚，使用上拉电阻（如果传感器是“低电平触发”）
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("开始监听传感器信号（低电平触发）...")

try:
    while True:
        if GPIO.input(SENSOR_PIN) == GPIO.LOW:
            start()
            print("✅ 检测到传感器信号（低电平）")
        else:
            print("🔍 无信号（高电平）")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("⛔️ 程序终止，清理 GPIO...")
    GPIO.cleanup()