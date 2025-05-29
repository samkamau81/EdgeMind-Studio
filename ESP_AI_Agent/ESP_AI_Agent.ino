#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "Kamaus";
const char* password = "G@t0t000";
const char* serverUrl = "http://192.168.0.102:8502/esp_streamlit"; // Note port changed to 8502

// Actuator pins
const int motorPin = 3;    // GPIO4
const int ledPin = 4;      // GPIO5

void setup() {
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
  Serial.println(" connected!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;

    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Read smoke sensor (assuming MQ-2 connected to A0)
    int smoke = analogRead(A0);
    
    // Create JSON payload
    String jsonPayload = "{\"smoke\": " + String(smoke) + "}";

    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
      
      // Parse the response to control actuators
      if (response.indexOf("\"motor\":\"ON\"") != -1) {
        digitalWrite(motorPin, HIGH);
        Serial.println("Motor ON");
      } else {
        digitalWrite(motorPin, LOW);
        Serial.println("Motor OFF");
      }
      
      if (response.indexOf("\"led\":\"ON\"") != -1) {
        digitalWrite(ledPin, HIGH);
        Serial.println("LED ON");
      } else {
        digitalWrite(ledPin, LOW);
        Serial.println("LED OFF");
      }
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }

  delay(10000); // Post every 10 seconds
}
