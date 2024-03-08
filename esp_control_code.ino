#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;
String message = ""; // Stores the incoming message

void setup() {
  Serial.begin(115200);
  SerialBT.begin("Iracingv1"); // Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");
}

void loop() {

  while (Serial.available()) {
    char inChar = (char)Serial.read();
    message += inChar;
    if (inChar == '\n') {
      message.remove(message.length() - 1); // Remove the newline character from the message
      // Casting message.c_str() to const uint8_t* to match the write method's expected argument type
      SerialBT.write(reinterpret_cast<const uint8_t*>(message.c_str()), message.length()); // Send the message without the newline
      message = ""; // Clear the message buffer
      break; // Exit the loop after sending the message
    }
  }
  
}
