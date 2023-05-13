1. Raspberry Pi and OS is powered on when connected to power source 
2. Configure NFC PN532 Hat to UART communication by ensuring I0 and I1 are connected to L 
3. RX and TX (switches 7 and 8) must be switched on for UART communication 
4. Copy hardware folder onto raspberry pi 
5. Open terminal
6. Obtain all necessary dependencies by running in terminal: `pip install --pre -r requirements.txt`
7. run NFC polling program by running: `python3 full_nfc_read_with_audit.py` 
8. LCD screen should light up to indicate that the NFC module is polling for a personnel scan