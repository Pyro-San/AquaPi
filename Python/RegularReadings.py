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
        self.pidfile_path =  '/tmp/AquaPiRR.pid'
        self.pidfile_timeout = 5

    def run(self):

        add_reading = ("INSERT INTO readings "
               "(CreateDate, WaterTemp, OutsideTemp, OutsideHumidity, InsideTemp, InsideHumidity, Lux, Lux2) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        locations=['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3','/dev/ttyACM4', '/dev/ttyACM5', 'end']

        lineDupe = ''

        while True:
            # Open the log file
            f = open('/mnt/winsvr/readingsRR.csv','a')
            try:
                line = ""
                # Find the correct USB Device, connect to it, send 'r' then read the results into a string.
                for device in locations:
                    try:
                        #print "Trying...",device
                        ser = serial.Serial(device, 115200, timeout = 60)
                        ser.write('r')
                        line = datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "," + ser.readline().strip()
                        ser.close()
                        break
                    except:
                        #print "Failed to connect on",device
                        if device == 'end':
                            line = "Unable to find Serial Port. Try again later"
                            exit()
                # Write the string to the log file
                f.write(line + "\n")
                f.flush()

                #App.AddToDatabase(line)
                # Put this in a seperate function later
                aLine = line.split(',')
                if len(aLine) == 8:
                    # Timestamp, WaterTemp, Out Temp, Out Humid, In Temp, In Humid, Lux
                    data_reading = (str(datetime.now()), aLine[1], aLine[3], aLine[2], aLine[5], aLine[4], aLine[7], aLine[6])
                    # Connect to the database
                    cnx = mysql.connector.connect(host=accesscodes.DATABASE_HOST,
                                                database=accesscodes.DATABASE_NAME,
                                                user=accesscodes.DATABASE_USER,
                                                password=accesscodes.DATABASE_PASS)
                    cursor = cnx.cursor()
                    # Write to the database
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

