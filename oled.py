import math,threading
import time,sys,string

from datetime import datetime, timedelta

import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import paho.mqtt.client as mqtt

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

disp = Adafruit_SSD1306.SSD1306_128_32(rst=24)
disp.begin()
disp.clear()
disp.display()

print(GPIO.getmode())

rows = [(0,0),(0,10),(0,20),(40,0),(40,10),(40,20), (80,0),(80,10),(80,20)]
rowvalues = []

#
# THREAD
#
class DestroyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Thread RUN")
        global rowvalues
        while True:
            time.sleep(1)
            date = datetime.now()
            todel = []
            for i,tab in enumerate(rowvalues):
                if (tab[1] + timedelta(seconds=10)) < date:
                    todel.append(i)
                    #print("appended! : "+str(i)+", "+str(tab[1]))
            for i in todel:
                try:
                    rowvalues.pop(i)
                except IndexError:
                    pass
            if (len(todel) > 0):
                display()

#
# FIN PARTIE THREAD
#

def display():
    global rowvalues
    global rows
    image = Image.new('1', (disp.width, disp.height))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    for row,i in enumerate(rowvalues):
        draw.text(rows[row], i[0], font=font, fill=255)
    disp.image(image)
    disp.display()
    
def oled_handle(planestr):
    global rowvalues
    
    tab = planestr.split("!!")
    rowvalues.append([tab[0], datetime.now()])
    while len(rowvalues) > 9:
        rowvalues.pop(0)
    display()
    
def on_connect(client, userdata, flags, rc):
    if rc != 0:
       print("result code : "+str(rc))
    print("Connection successful")
    client.subscribe("avion")
    
def filter(strin):
    for c in strin:
        for letter in (string.ascii_letters + string.digits):
            if c == letter: return True
    return False
                

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if not filter(payload): return
    print("'"+payload+"' ["+str(len(payload))+"]")
    oled_handle(payload)

client = mqtt.Client()
client.username_pw_set("adsb", password="XXXXXXXXX")
client.connect("194.199.227.235", 1136, 60)

client.on_connect = on_connect
client.on_message = on_message

DestroyThread().start()

client.loop_forever()
