### Description
The hardware aspect of this project will allow people to scan their NFC cards from an app to the NFC reader on the NFC PN532 Hat, where the Raspberry Pi will parse the Near-Field Communication (NFC) information, formatted in NFC Data Exchange Format (NDEF), and return a decision for granting or denying access to a door or lock.

### Set Up Hardware for Raspberry Pi and NFC PN532 Hat, Building, and Running Program
1. Raspberry Pi and operating syetem is powered on when the Raspberry Pi is connected to power source. *You may need to restart the power source the OS it does not start up.* You will also need to hook up the Raspberry Pi to a monitor using an HDMI cable for seeing the Graphical User Interface (GUI) for the Raspberry Pi OS.
2. Configure NFC PN532 Hat to UART communication by ensuring `I0` and `I1` are connected to `L`
3. RX and TX (switches 7 and 8) on the FC PN532 Hat must be switched on **ONLY** for UART communication
4. Copy the `hardware` folder onto the Raspberry Pi
5. Connect the Raspberry Pi to Wi-Fi to have reachability to the database on AWS EC2.
6. Open the terminal on the Raspberry Pi
7. Obtain all necessary dependencies by running in terminal: `pip install --pre -r requirements.txt`
8. Run the NFC polling program by running: `python3 full_nfc_read_with_audit.py`
9. The LCD screen should light up to indicate that the NFC module is polling and ready for NFC detection.