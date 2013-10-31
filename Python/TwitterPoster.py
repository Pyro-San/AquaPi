#!/usr/bin/python
### Playing around with reading temps from the arduino
### and from the DHT22
### using PySerial : http://pyserial.sourceforge.net/pyserial.html
### and Python Daemon : https://pypi.python.org/pypi/python-daemon/
### and Twitter Tools : https://pypi.python.org/pypi/twitter


import glob
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
    ## calculate the voltage of the input
    #voltage = 5.0 * (aveRes / 1024.0)
    ## calc the voltage divider
    #resistance = (10.0 * 5.0) / voltage - 10.0
    ## calc the intensity in lux
    #illuminance = 255.84 * pow(resistance, -10/9)

    return str(averes)

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/pyroaquaMain.pid'
        self.pidfile_timeout = 5
    def run(self):

        f = open('/mnt/winsvr/temps.csv','a')
        ##f.write('Time,\tType,\tstatus,\tHumidity (%),\tTemperature (C)\n')
        sPort = "%s" % glob.glob("/dev/ttyACM*")
        ser = serial.Serial(sPort.replace("'","").replace("[","").replace("]",""), 115200)
        lineDupe = ''


        t = Twitter(
                    auth=OAuth(accesscodes.OAUTH_TOKEN, accesscodes.OAUTH_SECRET,
                               accesscodes.CONSUMER_KEY, accesscodes.CONSUMER_SECRET)
                   )
        t.statuses.home_timeline()

        while True:
            try:
                ser.write('r')
                # Put something in here to handle duplicate posts.
                
                line = ser.readline().strip()
                dets = line.split(',')
                if len(dets) >= 3:
                    lineOut = str(datetime.now()) + "| Water: " + dets[0] + "c | Out Humidity: " + dets[1] + "%| Temp: " + dets[2] + "c | In Humidity: " + dets[3] + "%| Temp: " + dets[4] + "c | " + calcLums(ser)
                    t.statuses.update(status=str(lineOut[:139]))
                    f.write(str(datetime.now()) + "," + line + "\n")
                    f.flush()
                time.sleep(1800)
            except Exception, e:
                f.write('An error has occoured: %s \n' % str(e))
                f.flush()
                sPort = "%s" % glob.glob("/dev/ttyACM*")
                ser = serial.Serial(sPort.replace("'","").replace("[","").replace("]",""), 115200)
                time.sleep(600)


app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

