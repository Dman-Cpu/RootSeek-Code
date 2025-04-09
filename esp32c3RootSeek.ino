#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <U8g2lib.h>
#include <Wire.h>
#include <esp_sleep.h>

// Wi-Fi credentials
const char* ssid = "FIU_WiFi";
const char* password = "";

// Sensor pin definitions
#define TRIG_PIN 5
#define ECHO_PIN 4
#define DHT_PIN 10
#define DHT_TYPE DHT11
#define SMP_PIN A0  // Soil moisture sensor

// Deep Sleep config
#define WAKEUP_TIME_SEC 60  // Wake up every 60 seconds

// Sensor objects
DHT dht(DHT_PIN, DHT_TYPE);
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE, 9, 8);
WebServer server(80);

// Sensor data
float temperature, humidity, distance;
int soilValue, moisturePercent;
bool rootsDetected = false;
String jsonData = "{}";

// Moisture calibration (adjust based on your sensor)
int dryValue = 800;
int wetValue = 300;

// ====== Function Definitions ======

bool detectRoots(float distance, float humidity) {
  return (distance < 10.0 && humidity > 60.0);
}

float readDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  return duration * 0.034 / 2;
}

int readSoilMoisture() {
  int value = analogRead(SMP_PIN);
  // Adjust calibration dynamically
  if (value < wetValue) wetValue = value;
  if (value > dryValue) dryValue = value;
  int percent = map(value, dryValue, wetValue, 0, 100);
  return constrain(percent, 0, 100);
}

void enterDeepSleep() {
  esp_sleep_enable_timer_wakeup(WAKEUP_TIME_SEC * 1000000);
  Serial.println("Entering deep sleep...");
  esp_deep_sleep_start();
}

void updateOLED() {
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_6x10_tr);

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
}

void setup() {
  Serial.begin(115200);

  // Init sensors
  dht.begin();
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(SMP_PIN, INPUT);

  // Init OLED
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 10, "Initializing...");
  u8g2.sendBuffer();

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wi-Fi...");
  }
  Serial.println("Connected to Wi-Fi!");
  Serial.println(WiFi.localIP());

  // Web server route
  server.on("/data", []() {
    server.send(200, "application/json", jsonData);
  });
  server.begin();
}

void loop() {
  // Sensor readings
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  distance = readDistance();
  moisturePercent = readSoilMoisture();

  rootsDetected = detectRoots(distance, humidity);

  // Generate JSON response
  jsonData = "{ \"temperature\": " + String(temperature) +
             ", \"humidity\": " + String(humidity) +
             ", \"distance\": " + String(distance) +
             ", \"moisture\": " + String(moisturePercent) +
             ", \"rootsDetected\": " + String(rootsDetected ? "true" : "false") + " }";

  // Update OLED
  updateOLED();

  // Serial log for debugging and labeling
  int label = (distance < 10) ? 1 : 0;
  if (!isnan(temperature) && !isnan(humidity)) {
    Serial.print("Distance: "); Serial.print(distance);
    Serial.print(" cm, Temp: "); Serial.print(temperature);
    Serial.print(" C, Hum: "); Serial.print(humidity);
    Serial.print(" %, Soil: "); Serial.print(moisturePercent);
    Serial.print(" %, Label: "); Serial.println(label);
  } else {
    Serial.println("Error reading sensors!");
  }

  // Handle requests
  server.handleClient();

  // Optional deep sleep (uncomment to enable)
  // enterDeepSleep();

  delay(2000);
}
