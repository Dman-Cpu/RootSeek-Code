#include <U8g2lib.h>
#include <DHT.h>
#include <DHT_U.h>
#include <Wire.h>

// Pin definitions
#define TRIG_PIN 5
#define ECHO_PIN 4
#define DHT_PIN 10
#define DHT_TYPE DHT11
#define SMP A0  // Change to A0 or A1 if needed

// Initialize sensors
DHT dht(DHT_PIN, DHT_TYPE);

// Initialize U8g2 for I2C OLED
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE, /* clock=*/ 9, /* data=*/ 8);

// Calibration values for soil moisture sensor (Adjust based on real readings)
int dryValue = 800;  // Adjust this based on real dry sensor readings
int wetValue = 300;  // Adjust this based on real wet sensor readings

// Variables for other sensors
float temperature, humidity;
long duration;
float distance;

bool detectRoots(float distance, float humidity) {
  return (distance < 10.0 && humidity > 60.0);
}

void setup() {
  Serial.begin(115200);
  
  dht.begin();
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  u8g2.begin();
  
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_6x10_tr);
  u8g2.drawStr(0, 12, "Tree Root Detect");
  u8g2.sendBuffer();
  delay(2000);
}

void loop() {
  // Read DHT11 sensor data
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // Read ultrasonic sensor data
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  // Read soil moisture sensor data
  int sensorValue = analogRead(SMP);

  // Validate and adjust calibration values dynamically
  if (sensorValue < wetValue) {
    wetValue = sensorValue;
  }
  if (sensorValue > dryValue) {
    dryValue = sensorValue;
  }

  int moisturePercent = map(sensorValue, dryValue, wetValue, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);
  
  bool rootsDetected = detectRoots(distance, humidity);

  // Update OLED display
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_6x10_tr);

  u8g2.setCursor(0, 10);
  u8g2.print("Temp: ");
  u8g2.print(temperature);
  u8g2.print(" C");

  u8g2.setCursor(0, 22);
  u8g2.print("Hum: ");
  u8g2.print(humidity);
  u8g2.print(" %");

  u8g2.setCursor(0, 34);
  u8g2.print("Dist: ");
  u8g2.print(distance);
  u8g2.print(" cm");

  u8g2.setCursor(0, 46);
  u8g2.print("Soil: ");
  u8g2.print(moisturePercent);
  u8g2.print("%");

  u8g2.setCursor(0, 58);
  if (rootsDetected) {
    u8g2.print("Roots Detected!");
  } else {
    u8g2.print("No Roots Found");
  }

  u8g2.sendBuffer();

  // Debugging output to Serial Monitor
  Serial.print("Temp: ");
  Serial.print(temperature);
  Serial.print(" C, Hum: ");
  Serial.print(humidity);
  Serial.print(" %, Dist: ");
  Serial.print(distance);
  Serial.print(" cm, Soil: ");
  Serial.print(moisturePercent);
  Serial.println("%");

  delay(1000);
}
