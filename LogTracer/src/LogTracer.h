// LogTracer.h
#ifndef LOGTRACER_H
#define LOGTRACER_H

#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>

/**
 * @class LogTracer
 * @brief A class to handle WebSocket communication for sending data in JSON format.
 */
class LogTracer {
public:
    /**
     * @brief Constructor to initialize LogTracer.
     * @param ssid WiFi SSID
     * @param password WiFi password
     * @param port WebSocket server port (default is 81)
     */
    LogTracer(const char* ssid, const char* password, int port = 81);

    /**
     * @brief Initializes WiFi connection and starts the WebSocket server.
     */
    void begin();

    /**
     * @brief Call this method in the loop to handle WebSocket events and send data at intervals.
     */
    void update();

    /**
     * @brief Adds a float data entry to the specified category.
     * @param category The category of data (e.g., "Weather", "System").
     * @param key The key for the data entry.
     * @param value The float value to be sent.
     */
    void addData(const char* category, const char* key, float value);

    /**
     * @brief Adds a string data entry to the specified category.
     * @param category The category of data (e.g., "Weather", "System").
     * @param key The key for the data entry.
     * @param value The string value to be sent.
     */
    void addData(const char* category, const char* key, const char* value);
    
    /**
     * @brief Sets up the port for the WebSocket server.
     * @param port The port number to be used (default is 81).
     */
    void setPort(int port);

    /**
     * @brief Fixes the IP address of the ESP32 (if needed).
     * @param ip The desired static IP address (in string format).
     * @param gateway The gateway address (usually your router's IP).
     * @param subnet The subnet mask.
     */
    void fixIPAddress(const char* ip, const char* gateway, const char* subnet);
    
    /**
     * @brief Fixes the IP address of the ESP32 (if needed).
     */
    void fixIPAddress(const char* ip);

    /**
     * @brief send data to gui.
     * @param None.
     */
    void sendData();

private:
    const char* ssid;               ///< WiFi SSID
    const char* password;           ///< WiFi password
    WebSocketsServer webSocket;     ///< WebSocket server object
    unsigned long previousMillis;   ///< Timestamp for data sending intervals
    const long interval;            ///< Interval for sending data
    StaticJsonDocument<200> jsonDoc; ///< JSON document for storing data
    JsonArray dataToSend;           ///< Array to hold data to be sent
};

#endif
