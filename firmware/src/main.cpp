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

void setup() {
    // TODO: Initialize Serial communication (115200 baud)
    // TODO: Initialize SPI bus
    // TODO: Initialize MFRC522 reader
}

void loop() {
    // TODO: Check for incoming Serial commands and dispatch to handlers
}

void handleCommand(String command) {
    /**
     * Parse and execute incoming commands:
     *   - "CHECK_HW" -> Run PCD_DumpVersionToSerial(), return "READY" or "HW_FAILURE"
     *   - "READ_UID" -> Wait for card, read UID, return "UID:XXXXXXXXXXXX"
     *   - "WRITE_UID:XXXX" -> Attempt magic backdoor write to blank card
     */
    // TODO: Implement command parsing and routing
}

void checkHardware() {
    /**
     * Verify MFRC522 is connected and responding.
     * Use mfrc522.PCD_DumpVersionToSerial() or version register check.
     * Send "READY" or "HW_FAILURE" via Serial.
     */
    // TODO: Implement hardware self-test
}

void readUID() {
    /**
     * Wait for PICC (card) to be presented.
     * Read the UID bytes from the card.
     * Send "UID:XXXXXXXXXXXX" (hex string) via Serial.
     * Handle timeout and read errors.
     */
    // TODO: Implement UID reading
}

void writeUID(String newUID) {
    /**
     * Attempt to write a new UID to a "magic" Chinese clone card.
     * Use backdoor commands (halt, wake with 0x40, write block 0).
     * Send "SUCCESS" or "ERROR_LOCKED" via Serial.
     */
    // TODO: Implement magic backdoor UID write for CUID/Gen1a cards
}
