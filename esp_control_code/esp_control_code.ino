#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;
String message = "";

void setup() {
  Serial.begin(115200);
  SerialBT.begin("Iracingv2"); // Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");
}

void loop() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    message += inChar;
    if (inChar == '\n') {
      message.remove(message.length() - 1);

      SerialBT.write(reinterpret_cast<const uint8_t*>(message.c_str()), message.length());
      message = "";
      break; 
    }
  }
  
}
