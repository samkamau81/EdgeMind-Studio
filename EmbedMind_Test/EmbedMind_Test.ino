#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "Kamaus";
const char* password = "G@t0t000";
const char* post_serverUrl = "http://192.168.100.6:8502/esp_streamlit";
const char* get_serverUrl = "http://localhost:8503/streamlit_esp";

// Actuator pins
const int motorPin = 5;    // GPIO4
const int ledPin = 4;      // GPIO5



void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  pinMode(motorPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  digitalWrite(motorPin, LOW);
  digitalWrite(ledPin, LOW);
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void checkForAgentActions() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;
    
    http.begin(client, get_serverUrl);
    int httpCode = http.GET();
    
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("Received agent actions:");
      Serial.println(payload);
      
      // Parse JSON response
      DynamicJsonDocument doc(256);
      deserializeJson(doc, payload);
      
      // Control actuators based on agent response
      const char* motorState = doc["motor"];
      const char* ledState = doc["led"];
      
      if (strcmp(motorState, "ON") == 0) {
        digitalWrite(motorPin, HIGH);
        Serial.println("Motor turned ON");
      } else {
        digitalWrite(motorPin, LOW);
        Serial.println("Motor turned OFF");
      }
      
      if (strcmp(ledState, "ON") == 0) {
        digitalWrite(ledPin, LOW);  // Active LOW
        Serial.println("LED turned ON");
      } else {
        digitalWrite(ledPin, HIGH); // Active HIGH
        Serial.println("LED turned OFF");
      }
    } else {
      Serial.printf("GET request failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  }
}

void sendSensorData() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;

    http.begin(client, post_serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Read smoke sensor (assuming MQ-2 connected to A0)
    int smoke = analogRead(A0);
    int smoke_val = map(smoke, 0, 1024, 0, 100);  // Convert to 0-1000 ppm range
    
    // Create JSON payload with timestamp
    String jsonPayload = "{\"smoke\": " + String(smoke_val) + 
                        ", \"timestamp\": \"" + String(millis()) + "\"}";
    
    Serial.println("Sending sensor data:");
    Serial.println(jsonPayload);
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response:");
      Serial.println(response);
    } else {
      Serial.printf("POST request failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  }
}

void loop() {
  sendSensorData();
  checkForAgentActions();
  delay(10000); // Run every 10 seconds
}
