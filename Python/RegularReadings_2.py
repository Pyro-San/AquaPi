#!/usr/bin/python
## Lets make this a bit better

import serial
import mysql.connector
import accesscodes
from datetime import datetime
from twitter import *

# This function polls the Arduino to get the readings.
def get_the_temps():
    locations=['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3','/dev/ttyACM4', '/dev/ttyACM5', 'end']

    # Find the correct USB Device, connect to it, send 'r' then read the results into a string.
    for device in locations:
        try:
            ##print "Trying...",device
            ser = serial.Serial(device, 115200, timeout = 60)
            ser.write('r')
            line = datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "," + ser.readline().strip()
            ser.close()
            break
        except:
            ##print "Failed to connect on",device
            if device == 'end':
                line = "Unable to find Serial Port. Try again later"
                exit()

    return line

# Write the details to file
def write_to_file_svr(line):
    ##print "Write to Server \n"
    try:
        f = open('/mnt/winsvr/RRR.csv','a')
        f.write(line + "\r\n")
        f.flush()
        f.close()
    except Exception, e:
        error_log(e)

# Write the details locally
def write_to_file_local(line):
    ##print "Write to Local \n"
    f = open('/home/pi/aquapi/regular_readings.log','a')
    f.write(line + "\r\n")
    f.flush()
    f.close()

# Log the errors
def error_log(e):
    ##print "Write to error \n"
    log = open('/home/pi/aquapi/error.log','a')
    log.write('[%s] Error: %s \r\n' % (datetime.now().strftime("%d-%m-%Y %H:%M:%S"),str(e)))
    log.flush()
    log.close()

# INSERT the details to the LIVE database
def insert_to_db(aLine):
    try:
        add_reading = ("INSERT INTO readings "
               "(CreateDate, WaterTemp, OutsideTemp, OutsideHumidity, InsideTemp, InsideHumidity, Lux, Lux2) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
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
    except Exception, e:
        error_log(e)

# Post to twitter
def post_to_twitter(aLine):
    try:
        t = Twitter(
                    auth=OAuth(accesscodes.OAUTH_TOKEN, 
                        accesscodes.OAUTH_SECRET,
                        accesscodes.CONSUMER_KEY, 
                        accesscodes.CONSUMER_SECRET)
                    )
        t.statuses.home_timeline()

        if len(aLine) == 8:
            lineOut = aLine[0]
            lineOut += "| Water: " + aLine[1] 
            lineOut += "c | Out Humid: " + aLine[2] 
            lineOut += "%| Temp: " + aLine[3] 
            lineOut += "c | In Humid: " + aLine[4] 
            lineOut += "%| Temp: " + aLine[5] 
            lineOut += "c | "
            if aLine[7] < 10:
                lineOut += aLine[7]
            else:
                lineOut += aLine[6]
            t.statuses.update(status=str(lineOut[:139]))
    except Exception, e:
        error_log(e)


##print "TEST"
readings = get_the_temps()
aLine = readings.split(',')
## TODO: Put a loop in here to loop until aLine len is 8, but limit the number of loops

##print "Readings:", readings
write_to_file_local(readings)
write_to_file_svr(readings)

if len(aLine) == 8:
    insert_to_db(aLine)

currentMin = datetime.now().strftime("%M")

if currentMin == "30" or currentMin == "00" :
    post_to_twitter(aLine)
