/**
 * RFID Cloner Studio - Arduino Firmware
 * 
 * Communicates with MFRC522 reader via SPI and receives commands from PC via Serial.
 * 
 * Pin Configuration:
 *   RST = 9, SS = 10, MOSI = 11, MISO = 12, SCK = 13
 */

#include <SPI.h>
#include <MFRC522.h>

// Pin definitions
#define RST_PIN 9
#define SS_PIN 10

MFRC522 mfrc522(SS_PIN, RST_PIN);
String inputBuffer = "";

// Function prototypes
void handleCommand(String command);
void checkHardware();
void readUID();
void writeUID(String newUID);

void setup() {
    Serial.begin(115200);
    while (!Serial);
    SPI.begin();
    mfrc522.PCD_Init();
    delay(100);
}

void loop() {
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            if (inputBuffer.length() > 0) {
                handleCommand(inputBuffer);
                inputBuffer = "";
            }
        } else {
            inputBuffer += c;
        }
    }
}

void handleCommand(String command) {
    command.trim();
    if (command == "CHECK_HW") {
        checkHardware();
    } else if (command == "READ_UID") {
        readUID();
    } else if (command.startsWith("WRITE_UID:")) {
        String newUID = command.substring(10);
        writeUID(newUID);
    } else {
        Serial.println("ERROR_UNKNOWN_CMD");
    }
}

void checkHardware() {
    byte v = mfrc522.PCD_ReadRegister(MFRC522::VersionReg);
    if (v == 0x00 || v == 0xFF) {
        Serial.println("HW_FAILURE");
    } else {
        Serial.println("READY");
    }
}

void readUID() {
    unsigned long startTime = millis();
    const unsigned long timeout = 5000; // 5 second timeout
    
    while (millis() - startTime < timeout) {
        if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
            Serial.print("UID:");
            for (byte i = 0; i < mfrc522.uid.size; i++) {
                if (mfrc522.uid.uidByte[i] < 0x10) Serial.print("0");
                Serial.print(mfrc522.uid.uidByte[i], HEX);
            }
            Serial.println();
            mfrc522.PICC_HaltA();
            return;
        }
        delay(50);
    }
    Serial.println("ERROR_TIMEOUT");
}

void writeUID(String newUID) {
    // TODO: Implement magic backdoor UID write for CUID/Gen1a cards
    Serial.println("ERROR_NOT_IMPLEMENTED");
}
