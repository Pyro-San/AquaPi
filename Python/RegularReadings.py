#!/usr/bin/python
### Playing around with reading temps from the arduino
### and from the DHT22
import glob
import time
import serial
from daemon import runner
from datetime import datetime

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/pyroaquaRR.pid'
        self.pidfile_timeout = 5
    def run(self):

        f = open('/mnt/winsvr/aquaponicLog.csv','a')
        ###fweb = open('/var/www/data/aquaponicLog.csv','a')
        sPort = "%s" % glob.glob("/dev/ttyACM*")
        ser = serial.Serial(sPort.replace("'","").replace("[","").replace("]",""), 115200)
        lineDupe = ''

        while True:
            try:
                ser.write('r')
                line = ser.readline().strip()
                f.write(str(datetime.now()) + "," + line + "\n")
                f.flush()
                ###fweb.write(str(datetime.now()) + "," + line + "\n")
                ###fweb.flush()
                time.sleep(600)
            except Exception, e:
                f.write('An error has occoured: %s \n' % str(e))
                f.flush()
                sPort = "%s" % glob.glob("/dev/ttyACM*")
                ser = serial.Serial(sPort.replace("'","").replace("[","").replace("]",""), 115200)
                time.sleep(600)

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
