#include <LogTracer.h>

const char* ssid = "*****";
const char* password = "****";
LogTracer logger(ssid, password);

void setup() {
    // Set a static IP address
    logger.fixIPAddress("192.168.1.100");
    
    // Optionally set a custom port
    logger.setPort(81);
    
    // Initialize the logger
    logger.begin();
}

void loop() {
    // Add data to be sent
    logger.addData("Weather", "temperature", random(15, 35)); // Random temperature
    logger.addData("Weather", "humidity", random(30, 70) / 1.0); // Random humidity
    logger.addData("System", "CPU_usage", random(0, 100)); // Random CPU usage
    logger.addData("System", "RAM_usage", random(50, 200) / 1.0); // Random RAM usage in MB
    
    logger.update();  // Update the WebSocket server
}
