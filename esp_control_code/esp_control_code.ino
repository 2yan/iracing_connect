#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;
String message = "";
unsigned long lastMessageTime = 0; // Track the last time a message was received

void setup() {
  Serial.begin(115200);
  SerialBT.begin("RyGuysAdapter S0X BETA"); // Bluetooth device name
  Serial.println("ID: RyGuysAdapter S0X BETA");
}

void loop() {
  if (Serial.available()) {
    lastMessageTime = millis(); // Update the last message time
    while (Serial.available()) {
      char inChar = (char)Serial.read();
      message += inChar;
      if (inChar == '\n') {
        message.remove(message.length() - 1);
        SerialBT.write(reinterpret_cast<const uint8_t*>(message.c_str()), message.length());
        message = "";
        return; // Changed from break to return to exit the function after processing input
      }
    }
  }
  
  // If more than 3 seconds have passed since the last message, send the unique ID
  if (millis() - lastMessageTime > 3000) {
    Serial.println("ID: RyGuysAdapter S0X BETA");
    lastMessageTime = millis(); // Reset the timer after sending the ID
  }
}
