# -*- coding: utf-8 -*-


import _thread
import json
import urllib.request
import paho.mqtt.client as mqtt
import sys
import time
import requests,json
import base64
import signal
import RPi.GPIO
import RPi.GPIO as GPIO
import serial
import sys
import os
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings()

#mqttemq服务器配置
MQTTHOST = "121.36.111.52"
MQTTPORT = 1883
MQTTID = "pi"
MQTTUSER = "Gy"
MQTTPASSWORD = "gy"
MQTTPUB_TOPIC = "test/led"
#定义各个消息的主题信息
hum_topic = "fire/hum"
tem_topic =  "fire/tem"
mq_topic = "fire/mq"
fire_topic = "fire/fire"


ALLMSG = ""
mqttClient = mqtt.Client(MQTTID)
interrupted = False

import Adafruit_DHT #导入温度库
import time

sensor = Adafruit_DHT.DHT11
#定义数据传输接口
pin_mq = 4  #定义mq读取gpio
pin_fire = 5 #火焰传感器
pin_dht = 11 #定义温湿度口

#通过树莓派获取温湿度传感器数据，并发送到mqtt
def get_dht11():
    while (1):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)   #读取传感器数据
        if humidity is not None and temperature is not None:
            mqttClient.publish(hum_topic, humidity, 1)  #使用mqtt发送温湿度数据
            mqttClient.publish(tem_topic, temperature, 1)
            print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
            print('Failed to get reading. Try again!')
        time.sleep(1)  #每隔一秒发送



#定义树莓派获取mq2烟雾传感器的状态
def get_mq():
    CHANNEL=36 # 确定引脚口。按照真实的位置确定
    GPIO.setmode(GPIO.BOARD) # 选择引脚系统，这里我们选择了BOARD
    GPIO.setup(CHANNEL,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#初始化引脚，将36号引脚设置为输入下拉电阻，因为在初始化的时候不确定的的引电平，因此这样设置是用来保证精准，（但是也可以不写“pull_up_down=GPIO.PUD_DOWN”）
    while True: # 执行一个while死循环
        status = GPIO.input(CHANNEL) # 检测36号引脚口的输入高低电平状态
    #print(status) # 实时打印此时的电平状态
        if status == True: # 如果为高电平，说明MQ-2正常，并打印“OK”，有发送1，没有了发送0
           print ( ' 正常 ' )
           mqttClient.publish(mq_topic, 0, 1)
        else:    # 如果为低电平，说明MQ-2检测到有害气体，并打印“dangerous”
            print ( ' 检测到危险气体 ! ! ! ' )
            mqttClient.publish(mq_topic, 1, 1)
        time.sleep(0.5) # 睡眠0.1秒，以后再执行while循环
#---------------------------------------------------------------------------#
#通过树莓派采集火焰传感器数据
def get_fire():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_fire, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    while True:
       status = GPIO.input(pin_fire)
       if status == True:
          print('没有检测到火')
          mqttClient.publish(fire_topic, 0, 1)
       else:
          print('检测到火灾')
          mqttClient.publish(fire_topic, 1, 1)
       time.sleep(0.5)

#定义mqtt连接状态
def on_mqtt_connect():
    mqttClient.username_pw_set(MQTTUSER,MQTTPASSWORD)
    mqttClient.on_connect = on_connect
    #mqttClient.on_message = on_message # 消息到来处理函数
    mqttClient.connect(MQTTHOST, MQTTPORT, 60)
    mqttClient.loop_forever()
def on_connect(mqttClient, userdata, flags, rc):     #连接mqtt变量
    print("Connected with result code "+str(rc)) #打印连接状态
    #mqttClient.subscribe(MQTTSUB_TOPIC, 0)  # 接收指定服务器的消息
#开启多线程，执行mqtt
def thread1():
    on_mqtt_connect()

#主程序运行入口
if __name__ == '__main__':
    #开启多线程运行连接状态
    _thread.start_new_thread(thread1, ())
    #数据上报
    while True:
        get_dht11()
        get_mq()
        get_fire()




