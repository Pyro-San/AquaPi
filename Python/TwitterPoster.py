#!/usr/bin/python
### Playing around with reading temps from the arduino
### and from the DHT22
### using PySerial : http://pyserial.sourceforge.net/pyserial.html
### and Python Daemon : https://pypi.python.org/pypi/python-daemon/
### and Twitter Tools : https://pypi.python.org/pypi/twitter


import time
import serial
from daemon import runner
from datetime import datetime
from twitter import *
import accesscodes

def calcLums(ser):
    aveRes = 0
    ## get the average of 10 readings
    for i in range(0,10):
        ser.write('f')
        tmpRead = float(ser.readline().strip())
        aveRes += tmpRead

    averes = round(aveRes/10,2)

    return str(averes)

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/AquiPiMain.pid'
        self.pidfile_timeout = 5
    def run(self):

        locations=['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3','/dev/ttyACM4', '/dev/ttyACM5', 'end']
        t = Twitter(
                    auth=OAuth(accesscodes.OAUTH_TOKEN, 
                        accesscodes.OAUTH_SECRET,
                        accesscodes.CONSUMER_KEY, 
                        accesscodes.CONSUMER_SECRET)
                    )
        t.statuses.home_timeline()

        while True:
            try:
                f = open('/mnt/winsvr/readingsTP.csv','a')
                line = ""
                # Find the correct USB Device, connect to it, send 'r' then read the results into a string.
                for device in locations:
                    try:
                        #print "Trying...",device
                        ser = serial.Serial(device, 115200, timeout = 60)
                        ser.write('r')
                        line = datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "," + ser.readline().strip() + calcLums(ser)
                        ser.close()
                        break
                    except:
                        #print "Failed to connect on",device
                        if device == 'end':
                            line = "Unable to find Serial Port. Try again later"
                            exit()
                
                dets = line.split(',')
                if len(dets) == 8:
                    lineOut = dets[0]
                    lineOut += "| Water: " + dets[1] 
                    lineOut += "c | Out Humidity: " + dets[2] 
                    lineOut += "%| Temp: " + dets[3] 
                    lineOut += "c | In Humidity: " + dets[4] 
                    lineOut += "%| Temp: " + dets[5] 
                    lineOut += "c | " + dets[7]
                    t.statuses.update(status=str(lineOut[:139]))
                    f.write(str(datetime.now()) + "," + line + "\n")
                    f.flush()

                f.close()
                time.sleep(1800)
            except Exception, e:
                f.write('An error has occoured: %s \n' % str(e))
                f.flush()
                time.sleep(600)

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

