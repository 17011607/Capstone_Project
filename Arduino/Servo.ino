#include <Servo.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>


#define LRSERVO D2
#define UDSERVO D3
#define WIFI_SSID "IoT_Test"
#define WIFI_PASS "IoT_Test0"
#define UDP_PORT 4210

Servo lrServo;
Servo udServo;
WiFiUDP UDP;

void setup() {
    lrServo.attach(LRSERVO);
    udServo.attach(UDSERVO);
    Serial.begin(9600);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting to ");
    Serial.print(WIFI_SSID);
    while (WiFi.status() != WL_CONNECTED)
    {
      delay(100);
      Serial.print(".");
    }
    Serial.println();
    Serial.print("Connected! IP address: ");
    Serial.println(WiFi.localIP());
}

void test(){
  int pos;
  for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    lrServo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(1500);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    lrServo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(1500);                       // waits 15ms for the servo to reach the position
  }
  
}

void lrMoter(char f){
  switch(f){
    case 'S':
      lrServo.write(90);
      break;
    case 'L':
      lrServo.write(70);
      break;
    case 'R':
      lrServo.write(110);
      break;
     default:
      break;
  }
}

void udMoter(char f){
  switch(f){
    case 'S':
      udServo.write(90);
      break;
    case 'U':
      udServo.write(70);
      break;
    case 'D':
      udServo.write(110);
      break;
     default:
      break;
  }
}

void loop() {
    while (Serial.available()){
      char in_char = Serial.read();
      switch(in_char){
        case 'S':
          lrMoter(in_char);
          udMoter(in_char);
          break;
        case'L' : case 'R':
          lrMoter(in_char);
          break;
        case'U' : case 'D':
          udMoter(in_char);
          break;  
        
      }
      
  }
}
 
