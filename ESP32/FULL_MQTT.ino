#include "secrets.h"
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ---- WiFi credentials ----
const char *ssid = WIFI_SSID;
const char *password = WIFI_PASSWORD;

// ---- MQTT broker settings and topics ----
const char *mqtt_server = MQTT_BROKER_IP;   // Raspberry Pi IP address
const int   mqtt_port   = 1883;
const char *mqtt_client_id = "esp32_fan_client";
const char *topic_fanSpeed = "home/esp32/fanSpeed";
const char *topic_lcdScreen = "home/esp32/lcd";
const char *topic_relay = "home/esp32/relay";
const char *topic_gesture = "home/esp32/gesture";

// ---- LCD Screen ----
LiquidCrystal_I2C lcd(0x27, 20, 4);

// ---- Networking objects ----
WiFiClient espClient;
PubSubClient client(espClient);

// ---- Variables ----
String message;
int speed;
int targetSpeed;
const int fanPin = 26;
const int relayPin1 = 32;
const int relayPin2 = 33;
const int rampStep = 5;
const int rampInterval = 100;
const int statusLedPin = 27;
unsigned long lastStep;
bool toggle;
bool fanOn, fanOnDisplayed; 

// ---- Called automatically whenever a subscribed message arrives ----
void callback(char* topic, byte* payload, unsigned int length) {
  
  // FanSpeed
  if(strcmp(topic, topic_fanSpeed) == 0){
    Serial.print("Message arrived on topic: ");
    Serial.println(topic);
    message = "";
    for (unsigned int i = 0; i < length; i++) {
      message+=(char)payload[i];
    }
    if (message == "increase") {
      targetSpeed+=85;
      if(targetSpeed > 255){
        targetSpeed = 255;
      }
      
    } else if (message == "decrease") {
      targetSpeed-=85;
      if(targetSpeed < 0){
        targetSpeed = 0;
      }
    } else{
      lcd.setCursor(0, 2);
      lcd.print("                    "); // Clear any lcd diplayed message
      lcd.setCursor(0, 2);
      lcd.print("Unknown cmd");
    }
    
  } 
  // LCD Screen
  else if(strcmp(topic, topic_lcdScreen) == 0){
    Serial.print("Message arrived on topic: ");
    Serial.println(topic);
    message = "";
    for (unsigned int i = 0; i < length; i++) {
      message+=(char)payload[i];
    }
    if(message == "on"){
      lcd.backlight();
    }else if(message == "off"){
      lcd.noBacklight();
    }else if(message == "clear"){
      lcd.clear();
    }
  } 
  //  Relay
  else if(strcmp(topic, topic_relay) == 0){
    Serial.print("Message arrived on topic: ");
    Serial.println(topic);
    message = "";
    for (unsigned int i = 0; i < length; i++) {
      // Serial.print((char)payload[i]);
      message+=(char)payload[i];
    }
    if(message == "toggle"){
      toggle = !toggle;
      digitalWrite(relayPin1, toggle);
      digitalWrite(relayPin2, toggle);

      if(toggle == 0){
        lcd.setCursor(0, 3);
        lcd.print("                    "); // Clear any lcd diplayed message
        lcd.setCursor(0, 3);
        lcd.print("Bulb: ON");
      }else{
        lcd.setCursor(0, 3);
        lcd.print("                    "); // Clear any lcd diplayed message
        lcd.setCursor(0, 3);
        lcd.print("Bulb: OFF");
      }
    }
  }
  // Gesture
  else if(strcmp(topic, topic_gesture) == 0){
    Serial.print("Message arrived on topic: ");
    Serial.println(topic);
    message = "";
    for (unsigned int i = 0; i < length; i++) {
      message+=(char)payload[i];
    }
    lcd.setCursor(0, 1);
    lcd.print("                    "); // Clear any lcd diplayed message
    lcd.setCursor(0, 1);
    lcd.print("Gesture: ");
    lcd.setCursor(9, 1);
    lcd.print(message);
  }


  else{
    Serial.println("Topic not found");
  }
  
}

// ---- Reconnect logic: only called when NOT connected ----
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(mqtt_client_id)) {
      Serial.println("connected");
      client.subscribe(topic_fanSpeed);
      client.subscribe(topic_lcdScreen);
      client.subscribe(topic_relay);
      client.subscribe(topic_gesture);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" trying again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(fanPin, OUTPUT);
  pinMode(relayPin1, OUTPUT);
  pinMode(relayPin2, OUTPUT);
  // --- WiFi connect ---
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // --- MQTT setup ---
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // ---- Initialize the LCD screen ----
  lcd.init();
  lcd.backlight();


  speed = 0;
  targetSpeed = 0;
  lastStep = 0;
  toggle = true; // The relay is active LOW
  fanOn = false;
  fanOnDisplayed = false;
  analogWrite(fanPin, speed);
  digitalWrite(relayPin1, toggle);
  digitalWrite(relayPin2, toggle);
  // ---- Initial LCD Prints ----
  lcd.setCursor(0, 0);
  lcd.print("                    "); // Clear any lcd diplayed message
  lcd.setCursor(0, 0);
  lcd.print("GESTURE RECOG SYSTEM");

  lcd.setCursor(0, 1);
  lcd.print("                    "); // Clear any lcd diplayed message
  lcd.setCursor(0, 1);
  lcd.print("Gesture: NONE");


  lcd.setCursor(0, 2);
  lcd.print("                    "); // Clear any lcd diplayed message
  lcd.setCursor(0, 2);
  lcd.print("Fan: OFF");

  lcd.setCursor(0, 3);
  lcd.print("                    "); // Clear any lcd diplayed message
  lcd.setCursor(0, 3);
  lcd.print("Bulb: OFF");

}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  digitalWrite(statusLedPin, client.connected() ? HIGH : LOW);
  
  // Increase fan speed gradually
  if(millis() - lastStep >= rampInterval && (speed != targetSpeed)){
    if(speed < targetSpeed){
      speed = min(speed + rampStep, targetSpeed);
    }else if(speed > targetSpeed){
      speed = max(speed - rampStep, targetSpeed);
    }
    analogWrite(fanPin, speed);
    fanOn = (speed >= 85);
    if (fanOn != fanOnDisplayed) {
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("Fan: ");
      lcd.setCursor(5, 2);
      lcd.print(fanOn ? "ON " : "OFF");
      fanOnDisplayed = fanOn;
    }
    lastStep = millis();
  }
}