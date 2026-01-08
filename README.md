# RFID Cloner Studio

> 🎓 **Learning Project** - Beginner-friendly GUI for duplicating 13.56MHz RFID tags using Arduino + MFRC522.

⚠️ **Disclaimer**: This tool is for educational purposes only. Only clone cards you own or have permission to duplicate.

## Features

- Step-by-step wizard interface
- Hardware self-test on startup
- Read UID from source RFID card
- Write UID to Chinese "Magic" cards (CUID/Gen1a)
- Real-time status logging

## Hardware Requirements

- Arduino Uno or Nano
- MFRC522 RFID Reader Module
- 13.56MHz RFID cards (Magic/CUID cards for writing)

## Wiring Diagram

```
MFRC522  →  Arduino Uno/Nano
───────────────────────────────
SDA (SS)  →  Pin 10
SCK       →  Pin 13
MOSI      →  Pin 11
MISO      →  Pin 12
IRQ       →  (not connected)
GND       →  GND
RST       →  Pin 9
3.3V      →  3.3V ⚠️ (NOT 5V!)
```

## Installation

### 1. Firmware (Arduino)

```bash
cd firmware
# Using PlatformIO CLI
pio run --target upload

# Or open in PlatformIO IDE and upload
```

### 2. Desktop App (Python)

```bash
cd app
pip install -r requirements.txt
python main.py
```

## Usage

1. **Connect** - Select COM port and connect to Arduino
2. **Read** - Tap your original RFID card on the reader
3. **Write** - Tap a blank Magic card to clone the UID

## Project Structure

```
rfid-cloner-studio/
├── firmware/           # Arduino/PlatformIO code
│   ├── src/
│   │   └── main.cpp    # MFRC522 communication logic
│   └── platformio.ini  # Build configuration
├── app/                # Python GUI application
│   ├── main.py         # CustomTkinter interface
│   └── requirements.txt
└── README.md
```

## Serial Protocol

| Command | Response | Description |
|---------|----------|-------------|
| `CHECK_HW` | `{"status":"READY"}` | Hardware self-test |
| `READ_UID` | `{"status":"UID_READ","message":"AABBCCDD\|MIFARE 1K"}` | Read card UID |
| `WRITE_UID:AABBCCDD` | `{"status":"SUCCESS"}` | Write UID to magic card |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "HW_FAILURE" on connect | Check wiring, ensure 3.3V power |
| "ERROR_LOCKED" on write | Card is not a Magic/CUID card |
| No COM ports found | Install Arduino drivers |

## License

MIT License - See [LICENSE](LICENSE)

## Contributing

This is a learning project! Feel free to:
- Open issues for bugs or questions
- Submit PRs with improvements
- Fork and customize for your needs
