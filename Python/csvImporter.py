#!/usr/bin/python
import mysql.connector
import accesscodes

file = open('/mnt/winsvr/temps.csv', 'r')
cnx = mysql.connector.connect(host=accesscodes.DATABASE_HOST,
                            database=accesscodes.DATABASE_NAME,
                            user=accesscodes.DATABASE_USER,
                            password=accesscodes.DATABASE_PASS)
cursor = cnx.cursor()
add_reading = ("INSERT INTO readings "
       "(CreateDate, WaterTemp, OutsideTemp, OutsideHumidity, InsideTemp, InsideHumidity, Lux) "
       "VALUES (%s, %s, %s, %s, %s, %s, %s)")


for line in file:
    aLine = line.strip().split(',')
    TimeStamp = ""
    WaterTemp = ""
    OutHumid = ""
    OutTemp = ""
    InHumid = ""
    InTemp = ""
    Lux = ""

    if len(aLine) == 8:
        TimeStamp = aLine[0]  # Timestamp
        WaterTemp = aLine[1]  # WaterTemp
        OutHumid = aLine[2]  # Out Humid
        OutTemp = aLine[3]  # Out Temp
        InHumid = aLine[4]  # In Humid
        InTemp = aLine[5]  # In Temp
        Lux = aLine[6]  # Lux

        data_reading = (TimeStamp, WaterTemp, OutTemp, OutHumid, InTemp, InHumid, Lux)

        print data_reading

        cursor.execute(add_reading, data_reading)
        # Make sure data is committed to the database
        cnx.commit()
        
cursor.close()
cnx.close()
