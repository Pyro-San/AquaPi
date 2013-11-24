#!/usr/bin/python
### Playing around with reading temps from the arduino
### and from the DHT22
import time
import serial
from daemon import runner
from datetime import datetime
import mysql.connector
import accesscodes

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/aquapiRR.pid'
        self.pidfile_timeout = 5

    def run(self):

        add_reading = ("INSERT INTO readings "
               "(CreateDate, WaterTemp, OutsideTemp, OutsideHumidity, InsideTemp, InsideHumidity, Lux) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        locations=['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3','/dev/ttyACM4', '/dev/ttyACM5', 'end']

        lineDupe = ''

        while True:
            f = open('/mnt/winsvr/aquaponicLog.csv','a')
            try:
                line = ""
                for device in locations:
                    try:
                        #print "Trying...",device
                        ser = serial.Serial(device, 115200, timeout = 60)
                        ser.write('r')
                        line = str(datetime.now()) + "," + ser.readline().strip()
                        ser.close()
                        break
                    except:
                        #print "Failed to connect on",device
                        if device == 'end':
                            print "Unable to find Serial Port."
                            exit()

                f.write(line + "\n")
                f.flush()
                #App.AddToDatabase(line)
                # Put this in a seperate function later
                aLine = line.split(',')
                print "Line Count: %d", len(aLine)
                if len(aLine) == 8:
                    TimeStamp = aLine[0]  # Timestamp
                    WaterTemp = aLine[1]  # WaterTemp
                    OutHumid = aLine[2]  # Out Humid
                    OutTemp = aLine[3]  # Out Temp
                    InHumid = aLine[4]  # In Humid
                    InTemp = aLine[5]  # In Temp
                    Lux = aLine[6]  # Lux

                    data_reading = (TimeStamp, WaterTemp, OutTemp, OutHumid, InTemp, InHumid, Lux)

                    cnx = mysql.connector.connect(host=accesscodes.DATABASE_HOST,
                                                database=accesscodes.DATABASE_NAME,
                                                user=accesscodes.DATABASE_USER,
                                                password=accesscodes.DATABASE_PASS)
                    cursor = cnx.cursor()
                    cursor.execute(add_reading, data_reading)
                    # Make sure data is committed to the database
                    cnx.commit()
                    # Clean up
                    cursor.close()
                    cnx.close()

                f.close()
                time.sleep(600)
            except Exception, e:
                f.write('An error has occoured: %s \n' % str(e))
                f.flush()
                f.close()
                time.sleep(600)

#    def AddToDatabase(line):


app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

