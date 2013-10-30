// 
//   FILE:  dht_test.pde
// PURPOSE: DHT library test sketch for Arduino
//

#include <dht.h>
#include <OneWire.h>
#include <DallasTemperature.h>

dht DHT;
dht DHT2;
int led = 8;

#define DHT22_PIN 11
#define DHT22_PIN2 12
#define ONE_WIRE_BUS 9
#define LRD_PIN 10

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);
//  Serial.println();
DeviceAddress TubTemp = { 0x28, 0x2E, 0x18, 0xA8, 0x04, 0x00, 0x00, 0xD2 };
//DeviceAddress TubTemp = { 0x28, 0x93, 0xA4, 0xA8, 0x4, 0x0, 0x0, 0xF1 };

void setup()
{
    Serial.begin(115200);
    sensors.begin();
    sensors.setResolution(TubTemp, 10);
    pinMode(led, OUTPUT);

}

void loop()
{
    handleSerialCommunication();
    //delays
    delay(1000);
    //delay(3000); // 3 seconds
    //delay(600000); //10 minutes
    //delay(3600000);//1 hour
}

void handleSerialCommunication(void) {
    if (Serial.available() > 0 )
    {
        char inByte = Serial.read();
        int chk;
        int chk2;
        switch(inByte)
        {
        case 'r':
            // READ DATA
            digitalWrite(led, HIGH);
            chk = DHT.read22(DHT22_PIN);
            chk2 = DHT2.read22(DHT22_PIN2);
            //DS18B20 data
            sensors.requestTemperatures();
            printTemperature(TubTemp);
            Serial.print(",");
            //DHT22 data Out
            Serial.print(DHT.humidity, 1);
            Serial.print(",");
            Serial.print(DHT.temperature, 1);
            Serial.print(",");
            //DHT22 data In
            Serial.print(DHT2.humidity, 1);
            Serial.print(",");
            Serial.print(DHT2.temperature, 1);
            Serial.print(",");
            Serial.print(analogRead(LRD_PIN));
            Serial.println(",");
            //Turn the LED off
            digitalWrite(led, LOW);
            break;
        case 't':
            //DS18B20 data
            sensors.requestTemperatures();
            printTemperature(TubTemp);
            Serial.print("\n");
            break;
        case 'd':
            //DHT22 data Outside
            Serial.print(DHT.humidity, 1);
            Serial.print(",");
            Serial.println(DHT.temperature, 1);
            Serial.print("\n");
            break;
        case 'e':
            //DHT22 data Inside
            Serial.print(DHT2.humidity, 1);
            Serial.print(",");
            Serial.println(DHT2.temperature, 1);
            Serial.print("\n");
            break;
         case 'f':
            Serial.println(analogRead(LRD_PIN));
            break;
        }
    } 
}

void printTemperature(DeviceAddress deviceAddress)
{
    float tempC = sensors.getTempC(deviceAddress);
    if (tempC == -127.00) {
        Serial.print("Error getting temperature");
    } else {
        //Serial.print("C: ");
        Serial.print(tempC);
    }
}
//
// END OF FILE
//
