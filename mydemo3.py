# -*- coding: utf-8 -*-
'''
阿正原创
转载请注明出处。 wenzheng.club
视频地址：https://www.bilibili.com/video/av70428837/
2019年10月6日完结
'''

import _thread
import json
import urllib.request
from picamera import PiCamera
import paho.mqtt.client as mqtt
import snowboydecoder
from aip import AipSpeech
import sys
import time
import RPi.GPIO
import serial
import requests,json
import base64
import signal
import RPi.GPIO
import serial
import sys
import os
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)   
urllib3.disable_warnings()
#百度配置
APP_ID = '17478996' #自己的
API_KEY = 'GKIl9rhzbKGnEw7qqz1n3aMY' #自己的
SECRET_KEY = 'Di0o7CUQrF5sm7LgUsfgm16W74diBBF8'  #自己的
#mqtt配置
MQTTHOST = "121.36.111.52"
MQTTPORT = 1883
MQTTID = "pi"
MQTTUSER = "Gy"
MQTTPASSWORD = "gy"
MQTTPUB_TOPIC = "test/led"
#图灵机器人配置
TURING_KEY = "1f4ecf03da5f4b0780f9126e9fda3d23"
URL = "http://openapi.tuling123.com/openapi/api/v2"
HEADERS = {'Content-Type': 'application/json;charset=UTF-8'}

ALLMSG = ""
mqttClient = mqtt.Client(MQTTID)
interrupted = False

#---------------------------------------------------------------------------#
#问询B站粉丝数
def find_bilibili():
    host='http://api.bilibili.com/x/relation/stat?vmid=265908761'
    request=requests.get(host)
    print(request.text)
    callback=request.json()['data']['follower']
    print(callback)
    return callback
#控制onenet设备
def send_onenet(msg):
    host='http://api.heclouds.com/cmds?device_id=517254399'
    header = {'api-key':'eL2ObaFLA1UvjAfxjCBcUYKjxtY=','Content-Type':'application/x-www-form-urlencoded'}
    params = {'device_id':'517254399'}
    data = {'TEST':msg}
    request=requests.post(host,headers=header,data=data)
    callback=request.json()['error']
    print(callback)
#获取百度云token    
def getaccess_token():
    host='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=GKIl9rhzbKGnEw7qqz1n3aMY&client_secret=Di0o7CUQrF5sm7LgUsfgm16W74diBBF8'
    header_1 = {'Content-Type':'application/json; charset=UTF-8'}
    request=requests.post(host,headers =header_1)
    access_token=request.json()['access_token']
    print("at："+access_token)
    return access_token

#百度语音识别sdk函数
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

#在线语音识别  与逻辑处理
def Speech(access_token):    #语音主程序方法
    global detector
    # begin Speech
    os.system('play /home/pi/snowboy/dong.wav')
    print("dingdingding")
    baidu_tts("尊敬的老大，请讲")
    #os.system('espeak -vzh "%s"'%"你是不是傻".encode('utf-8'))
    #time.sleep(1)
    #os.system('arecord -d 5 -r 16000 -c 1 -t wav -f S16_LE -D plughw:1,0  ddd.wav')  #进行录音
    os.system('arecord -d 4 -r 16000 -c 1 -t wav -f S16_LE -D plughw:1,0  ddd.wav')  # 进行录音
    text = client.asr(get_file_content('ddd.wav'), 'wav', 16000, {'lan': 'zh'})
    print(text)
    if text['err_msg']=='success.':
        word =text['result'][0]  #对返回的json编码
        print(word)
        #baidu_tts(word)
        if "歌" in word :
            print(word)
            os.system('mpg123 /home/pi/snowboy/woceng.mp3')
        elif "你好" in word :   #http://boscdn.bpc.baidu.com/v1/developer/315e48e0-0a0d-46ab-b0d0-c217d1a77439.mp3
            #os.system('play http://boscdn.bpc.baidu.com/v1/developer/315e48e0-0a0d-46ab-b0d0-c217d1a77439.mp3')
            baidu_tts("别说那么多没用的,赶紧学习了")
        elif"晓东"in word:
            baidu_tts("就是魏苦逼那个大恶人了，怕怕")
        elif "华为手机" in word:
            #Word为：使用华为手机呼叫10086
            baidu_tts("小艺小艺")
            baidu_tts(word[6:])
        elif "苹果手机" in word:
            # Word为：使用苹果手机呼叫10086
            baidu_tts("Hi，siri")
            baidu_tts(word[6:])
        elif "我是谁" in word:
            take_picture()
            img=open_pic()
            search(img,access_token)
        elif "开灯" in word:
            baidu_tts("老板,灯已打开")
            #on_publish(client, userdata, mid)
            # 发布一个主题为'topic',内容为‘1’的信息，最后是qos
            mqttClient.publish(MQTTPUB_TOPIC,"{\"set_led\":1}", 1)
            print("灯已打开")
        elif "关灯" in word:
            baidu_tts("老板,灯已关闭")
            mqttClient.publish(MQTTPUB_TOPIC, "{\"set_led\":0}", 1)
            print("灯已关闭")
        elif "窗帘" in word:
            if "开" in word:
                send_onenet("OPEN")
            if "关" in word:
                send_onenet("CLOSE")
        elif "粉丝" in word:
            out_wav = "老大"+ "你的粉丝数为" + str(find_bilibili())+"人"
            baidu_tts(out_wav)
        elif "台灯" in word:
            if "开" in word:
                baidu_tts("小爱同学")
                baidu_tts("打开台灯")
            if "关" in word:
                baidu_tts("小爱同学")
                baidu_tts("关闭台灯")
        else :
            tuling(word)
            #baidu_tts("对不起老大,暂时无法执行该命令")
#图灵机器人（收费，不好玩了）           
# def tuling(words):
#     url2 = "http://i.itpk.cn/api.php?api_key=6ba480f37d92f31a0fc35721721afd23&api_secret=v42o7hn8e6zr&question= 你好呀&limit=5"
#     url = "http://openapi.tuling123.com/openapi/api/v2"
#     api_key = "556909e7a3e04c0383c6da6408559079"
#     data = {"userInfo":{"key":api_key,"userId":"wenzheng"},"info":words.encode("utf-8")}utf-8
# The Turing chatbot
def tuling(text):
    #初始的用户data信息
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": ""
            },
            "selfInfo": {
                "location": {
                    "city": "昆明",

                }
            }
        },
        "userInfo": {
            "apiKey": TURING_KEY,
            "userId": "starky"
        }
    }

    data["perception"]["inputText"]["text"] = text
    response = requests.request("post", URL, json=data, headers=HEADERS)  #发送请求
    response_dict = json.loads(response.text)   #转换为字典
    result = response_dict["results"][0]["values"]["text"]   #读取返回值
    print("the Tuling said: " + result)
    baidu_tts(result)  #百度语音读取
    return result

    #
    #
    # api_url = "http://openapi.tuling123.com/openapi/api/v2"
    # text_input = text
    #
    # req = {
    #     "perception":
    #         {
    #             "inputText":
    #                 {
    #                     "text": text_input
    #                 },
    #
    #             "selfInfo":
    #                 {
    #                     "location":
    #                         {
    #                             "city": "上海",
    #                             "province": "上海",
    #                             "street": "文汇路"
    #                         }
    #                 }
    #         },
    #
    #     "userInfo":
    #         {
    #             "apiKey": "1f4ecf03da5f4b0780f9126e9fda3d23",
    #             "userId": "OnlyUseAlphabet"
    #         }
    # }
    # # print(req)
    # # 将字典格式的req编码为utf8
    # req = json.dumps(req).encode('utf8')
    # # print(req)
    #
    # http_post = urllib.request.Request(api_url, data=req, headers={'content-type': 'application/json'})
    # response = urllib.request.urlopen(http_post)
    # response_str = response.read().decode('utf8')
    # # print(response_str)
    # response_dic = json.loads(response_str)
    # # print(response_dic)
    # intent_code = response_dic['intent']['code']
    # results_text = response_dic['results'][0]['values']['text']
    # baidu_tts(results_text)
    # # print('Turing的回答：')
    # # print('code：' + str(intent_code))
    # # print('text：' + results_text)


#百度语音合成sdk
def baidu_tts(words):
    result = client.synthesis(text = words, options={'vol':5})
    if not isinstance(result,dict):
        with open('audio.mp3','wb') as f:
            f.write(result)
        os.system('play audio.mp3')
    else:print(result)
#拍照
def take_picture():
    camera.start_preview()
    time.sleep(0.5)
    camera.capture('image.jpg')
    camera.stop_preview()
#打开图片并转码
def open_pic():
    f = open('image.jpg', 'rb')
    img = base64.b64encode(f.read())
    return img
#人脸搜索api
def search (img,access_token):
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    params = {"image":img,"image_type":"BASE64","group_id_list":"guoyue","quality_control":"NONE","liveness_control":"NORMAL"}
    request_url = request_url + "?access_token=" + access_token
    response = requests.post(request_url, data=params)
    output = response.json()
    print(output)
    if output['error_msg'] == 'SUCCESS':
        ##判断是否成功
        ##找到字典里的result－以及内层字典里的user_list
        user_list= output['result']['user_list']
        print(user_list)
        ##输出数据类型，发现其为列表
        ##利用列表的检索方式找到列表里的人脸检测分数－score
        score = user_list[0]['score']
        print(score)
        user = user_list[0]['user_id']
        if user == 'guoyue2':
            out_wav = "你是郭越!"+ "相似度为百分之" + str(score)
            baidu_tts(out_wav)
    else:
        errormsg = output['error_msg']
        out_wav = "识别错误"+ str(errormsg)
        baidu_tts(out_wav)
def callbacks():    #自定唤醒变量
    global detector
    print("Wake UP!....")
    snowboydecoder.play_audio_file() # ding
    detector.terminate()        # close
    time.sleep(1)
    Speech(access_token)
    wake_up()
def signal_handler(signal, frame):  #唤醒时操作变量
    global interrupted
    interrupted = True
def interrupt_callback():           #唤醒时操作变量
    global interrupted
    return interrupted
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
def wake_up():
    global detector
    model = '/home/pi/snowboy/resources/XHXH.pmdl'
    signal.signal(signal.SIGINT, signal_handler)
    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    print('Listening... please say wake-up word:XHXH')
    # main loop
    detector.start(detected_callback=callbacks,interrupt_check=interrupt_callback,sleep_time=0.03)
    detector.terminate()
#开启多线程，执行mqtt
def thread1():
    on_mqtt_connect()
if __name__ == '__main__':
    camera = PiCamera()
    access_token = getaccess_token()
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    _thread.start_new_thread(thread1, ())
    wake_up()

