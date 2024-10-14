// LogTracer.cpp
#include "LogTracer.h"

/**
 * @brief Constructor to initialize LogTracer with WiFi credentials and port.
 * @param ssid WiFi SSID
 * @param password WiFi password
 * @param port WebSocket server port (default is 81)
 */
LogTracer::LogTracer(const char* ssid, const char* password, int port)
    : ssid(ssid), password(password), webSocket(port), interval(2000) {
}

/**
 * @brief Initializes WiFi connection and starts the WebSocket server.
 */
void LogTracer::begin() {
    Serial.begin(115200);
  
    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("");
    Serial.print("Connected to WiFi. IP Address: ");
    Serial.println(WiFi.localIP());

    // Start WebSocket server
    webSocket.begin();
    webSocket.onEvent([](uint8_t num, WStype_t type, uint8_t *payload, size_t length) {
        if (type == WStype_CONNECTED) {
            Serial.printf("Client %u connected\n", num);
        } else if (type == WStype_DISCONNECTED) {
            Serial.printf("Client %u disconnected\n", num);
        }
    });

    dataToSend = jsonDoc.createNestedArray("DataToSend");
    previousMillis = 0;
}

/**
 * @brief Call this method in the loop to handle WebSocket events and send data at intervals.
 */
void LogTracer::update() {
    webSocket.loop();  // Handle WebSocket events

    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        sendData();
    }
}

/**
 * @brief Adds a float data entry to the specified category.
 * @param category The category of data (e.g., "Weather", "System").
 * @param key The key for the data entry.
 * @param value The float value to be sent.
 */
void LogTracer::addData(const char* category, const char* key, float value) {
    JsonObject container = dataToSend.createNestedObject();
    JsonArray dataArray = container.createNestedArray(category);
    JsonObject dataObject = dataArray.add<JsonObject>();  // Fix here
    dataObject[key] = value;
}

/**
 * @brief Adds a string data entry to the specified category.
 * @param category The category of data (e.g., "Weather", "System").
 * @param key The key for the data entry.
 * @param value The string value to be sent.
 */
void LogTracer::addData(const char* category, const char* key, const char* value) {
    JsonObject container = dataToSend.createNestedObject();
    JsonArray dataArray = container.createNestedArray(category);
    JsonObject dataObject = dataArray.add<JsonObject>();  // Fix here
    dataObject[key] = value;
}

/**
 * @brief Sets up the port for the WebSocket server.
 * @param port The port number to be used (default is 81).
 */
void LogTracer::setPort(int port) {
    webSocket = WebSocketsServer(port);
}

/**
 * @brief Fixes the IP address of the ESP32 (if needed).
 * @param ip The desired static IP address (in string format).
 * @param gateway The gateway address (usually your router's IP).
 * @param subnet The subnet mask.
 */
void LogTracer::fixIPAddress(const char* ip, const char* gateway, const char* subnet) {
    IPAddress local_ip;
    local_ip.fromString(ip);
    IPAddress gateway_ip;
    gateway_ip.fromString(gateway);
    IPAddress subnet_mask;
    subnet_mask.fromString(subnet);
    
    if (!WiFi.config(local_ip, gateway_ip, subnet_mask)) {
        Serial.println("Failed to configure IP address");
    }
}

/**
 * @brief Fixes the IP address of the ESP32 (if needed).
 * @param ip The desired static IP address (in string format).
 */
void LogTracer::fixIPAddress(const char* ip) {
    IPAddress local_ip;
    local_ip.fromString(ip);
    
    // Use current gateway and subnet
    if (!WiFi.config(local_ip, WiFi.gatewayIP(), WiFi.subnetMask())) {
        Serial.println("Failed to configure IP address");
    }
}

/**
 * @brief Sends the accumulated data as a JSON string over WebSocket.
 */
void LogTracer::sendData() {
    // Serialize JSON to string
    String jsonString;
    serializeJson(jsonDoc, jsonString);

    // Send JSON string over WebSocket
    webSocket.broadcastTXT(jsonString);
    
    // Print the JSON for debugging
    Serial.println(jsonString);
}
