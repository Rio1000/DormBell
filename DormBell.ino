#include <WiFi.h>
#include <HTTPClient.h>

// --- Configuration ---
const char* ssid = "csu-IoT";          // Your Wi-Fi network name
const char* password = "PJe5mzE5AKhP"; // Your Wi-Fi password
// Find your Mac Mini's local IP address in System Settings > Network
const char* serverName = "http://10.255.102.93:5120/ring";

// --- Pins ---
const int buttonPin = 13;
const int ledPin = 2; // Built-in LED on many ESP32 boards
const int buzzerPin = 12;

// --- Variables ---
int buttonState = HIGH;
int lastButtonState = HIGH;

void setup() {
  Serial.begin(115200);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  buttonState = digitalRead(buttonPin);

  // Check if the button has just been pressed (falling edge)
  if (buttonState == LOW && lastButtonState == HIGH) {
    Serial.println("Button pressed! Contacting server...");
    digitalWrite(ledPin, HIGH); // Turn on LED for immediate feedback

    // Check Wi-Fi connection before trying to send
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverName); // Specify the URL
      int httpResponseCode = http.GET(); // Send the request

      if (httpResponseCode > 0) {
        Serial.printf("Server responded with code: %d\n", httpResponseCode);
        
        // **NEW:** Get the response from the server
        String payload = http.getString();
        Serial.printf("Server response: %s\n", payload.c_str());

        // **NEW:** Only buzz if the server sends "BUZZ"
        if (payload == "BUZZ") {
            Serial.println("Buzzer enabled by server. Activating.");
            digitalWrite(buzzerPin, HIGH);
            delay(500); // Buzz for half a second
            digitalWrite(buzzerPin, LOW);
        } else {
            Serial.println("Buzzer disabled by server.");
        }

      } else {
        Serial.printf("Error on sending GET: %s\n", http.errorToString(httpResponseCode).c_str());
      }
      http.end(); // Free resources
    } else {
      Serial.println("WiFi Disconnected. Cannot send request.");
    }
    digitalWrite(ledPin, LOW); // Turn off LED after the action
  }

  // Save the current button state for the next loop
  lastButtonState = buttonState;

  // A small delay for stability
  delay(20);
}