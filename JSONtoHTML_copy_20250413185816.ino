#include <WiFi.h>
#include <WebServer.h>
#include <U8g2lib.h>
#include <DHT.h>

// Pin definitions
#define TRIG_PIN 5
#define ECHO_PIN 4
#define DHT_PIN 10
#define DHT_TYPE DHT11
#define SMP A0

// WiFi Credentials
const char* ssid = "Lopez-Moris";
const char* password = "3058043810";

// Initialize sensors
DHT dht(DHT_PIN, DHT_TYPE);
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE, 9, 8);
WebServer server(80);

// Soil calibration
int dryValue = 800;
int wetValue = 300;

// Sensor variables
float temperature, humidity, distance;
int moisturePercent;
bool rootsDetected = false;

// Root detection logic
bool detectRoots(float distance, float humidity, int moisture) {
  return (distance < 10.0 && humidity > 60.0 && moisture > 40);
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
  delay(1000);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP Address:");
  Serial.println(WiFi.localIP());

  // Define JSON data endpoint
  server.enableCORS();
  server.on("/data", HTTP_GET, []() {
    String json = "{";
    json += "\"temperature\":" + String(temperature, 1) + ",";
    json += "\"humidity\":" + String(humidity, 1) + ",";
    json += "\"distance\":" + String(distance, 1) + ",";
    json += "\"moisture\":" + String(moisturePercent) + ",";
    json += "\"rootsDetected\":" + String(rootsDetected ? "true" : "false");
    json += "}";
    server.send(200, "application/json", json);
  });

  server.begin();
}

void loop() {
  // Read sensors
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  int sensorValue = analogRead(SMP);
  sensorValue = constrain(sensorValue, wetValue, dryValue);
  moisturePercent = map(sensorValue, dryValue, wetValue, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);

  rootsDetected = detectRoots(distance, humidity, moisturePercent);

  // Update OLED
  u8g2.clearBuffer();
  u8g2.setCursor(0, 10);
  u8g2.print("Temp: "); u8g2.print(temperature); u8g2.print(" C");
  u8g2.setCursor(0, 22);
  u8g2.print("Hum: "); u8g2.print(humidity); u8g2.print(" %");
  u8g2.setCursor(0, 34);
  u8g2.print("Dist: "); u8g2.print(distance); u8g2.print(" cm");
  u8g2.setCursor(0, 46);
  u8g2.print("Soil: "); u8g2.print(moisturePercent); u8g2.print(" %");
  u8g2.setCursor(0, 58);
  u8g2.print(rootsDetected ? "Roots Detected!" : "No Roots Found");
  u8g2.sendBuffer();

  // Handle incoming HTTP requests
  server.handleClient();

  // Debug
  Serial.println("Sending data to web:");
  Serial.println("Temperature: " + String(temperature) + ", Humidity: " + String(humidity) + ", Distance: " + String(distance) + ", Soil: " + String(moisturePercent));
  
  delay(1000);
}
