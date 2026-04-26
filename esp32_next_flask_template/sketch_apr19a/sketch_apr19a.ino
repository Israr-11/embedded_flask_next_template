#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Error";
const char* password = "123456789";
const char* mqtt_server = "broker.hivemq.com"; // Free public broker for testing

WiFiClient espClient;
PubSubClient client(espClient);
const int ledPin = 2;

void callback(char* topic, byte* payload, unsigned int length) {
  char message[length + 1];
  for (int i = 0; i < length; i++) message[i] = (char)payload[i];
  message[length] = '\0';

  if (String(message) == "ON") digitalWrite(ledPin, LOW);  // Remember your inverted logic!
  else if (String(message) == "OFF") digitalWrite(ledPin, HIGH);
}

void setup() {
  Serial.begin(115200);
  delay(1000); // Give serial monitor time to catch up
  Serial.println("\n--- Booting ESP32 ---");

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH); // Start OFF

  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("Riverwalk_SWE_User_7721")) {
      client.subscribe("riverwalk/led");
    } else { delay(5000); }
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
}