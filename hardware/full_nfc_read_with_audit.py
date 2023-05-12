from pn532 import *
import RPi.GPIO as GPIO
from gpiozero import LED
from DFRobot_RGBLCD1602 import *  
import mysql.connector
import time
from datetime import datetime
import pytz
import re

def open_door(delay_time):
    lcd.set_RGB(0, 255, 0)
    lcd.print_out("ACCESS GRANTED")
    pwm.ChangeDutyCycle(5)
    time.sleep(delay_time)
    pwm.ChangeDutyCycle(10)
    lcd.clear()

def close_door(delay_time):
    lcd.set_RGB(255, 0, 0)
    lcd.print_out("ACCESS DENIED")
    time.sleep(delay_time)
    lcd.clear()

def erase_ntag215():
    print("Erasing...")
    data = bytes([0x00, 0x00, 0x00, 0x00])
    for block_number in range(5, 15):
        pn532.ntag2xx_write_block(block_number, data)
        #if pn532.ntag2xx_read_block(block_number) == data:
            #data = pn532.ntag2xx_read_block(block_number)
            #print('write block %d successfully' % block_number)
            #print("Block {0}: {1}".format(block_number, [hex(i) for i in data]))
    
def get_current_time_iso(timezone: str = 'UTC') -> str:
    timezone1 = pytz.timezone(timezone)
    return datetime.now(timezone1).isoformat()

# Pin Assignments
power_pin = 25
servo_pin = 12

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# initialize GPIO for power pin
GPIO.setup(power_pin, GPIO.OUT)
GPIO.output(power_pin, GPIO.HIGH)

# initialize GPIO pin for servo control pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, 50)

# set servo motor in locked position
pwm.start(10)

# initialize lcd screen | LCD1602 RGB Module V1.0 rgb_addr = 0x60
lcd = DFRobot_RGBLCD1602(rgb_addr=0x60,col= 16,row = 1)
time.sleep(1)
lcd.clear()
lcd.set_color_white()

# Getting serial number of Raspberry Pi
with open('/proc/cpuinfo', 'r') as f:
    for line in f:
        if line[0:6] == 'Serial':
            serial_number = line[10:26]
print("Serial Number: ", serial_number)

# Set up the database connection
db = mysql.connector.connect(
    user="root", 
    password="TBUASv565GdfPByVKdx2", 
    host="senior-project.cqpzjknbrdd2.us-west-2.rds.amazonaws.com", 
    database="SJSU"
)

# Set up the PN532 object for the Raspberry Pi's UART interface
pn532 = PN532_UART(debug=False, reset=20)

# Configure the PN532 to communicate with NTAG215 cards
pn532.SAM_configuration()

num_blocks = 15
uid = None
erase = False

# Loop forever, waiting for a tag to be scanned
while True:
    
    # Wait for a tag to be detected
    while uid is None:
        # Set up the database connection
        db = mysql.connector.connect(
            user="root", 
            password="TBUASv565GdfPByVKdx2", 
            host="senior-project.cqpzjknbrdd2.us-west-2.rds.amazonaws.com", 
            database="SJSU"
        )
        
        print("Checking NFC...")
        # reset NFC Hat (deactivating 13.56 MHz aura)
        GPIO.output(power_pin, GPIO.HIGH)
        pn532 = PN532_UART(debug=False, reset=20)
        time.sleep(1) # 1 second delay to allow off time for reading NFC from smart phone
        
        # activate NFC Hat for reading (activating 13.56 MHz aura)
        uid = pn532.read_passive_target(timeout=0.1)

    # If we detected a tag, try to read its NDEF message
    if uid is not None:
        try:
            # putting together data read from NFC tag
            ndef_data = b""
            for i in range(num_blocks):
                block_data = pn532.ntag2xx_read_block(i)
                ndef_data += block_data
            
            try:
                # parsing and getting payload from NDEF data taken from NFC tag
                ndef_payload = ndef_data.split(b"\xfe")[0].split(b"U\x00")[1].decode("latin-1")   
                
                if re.search(r"[abcdef0-9]{32}", ndef_payload) is None:
                    print("DOOR LOCKED: Payload is not recognized and cannot be accepted for process.")
                    close_door(2)
                    erase_ntag215()
                    uid = None
                    continue
                    
                # searching for any "UUID" matches in database
                cursor = db.cursor()
                cursor.execute(f"SELECT ID, UUID, ACTIVE from SJSU.PERSONNELS WHERE UUID = '{ndef_payload}'")
                row = cursor.fetchone()
                
                print("Checking...")
                # if no instance of UUID in the database was found...
                if row is None:
                    print('DOOR LOCKED: No UUID found in database.')
                    close_door(2)
                    cursor.close()
                    uid = None
                # If there is an instance of the UUID found in the database...
                else:
                    user_id, uuid, active = row[0], row[1], row[2]
                    print("USER_ID, UUID, ACTIVE: {}, {}, {}".format(user_id, uuid, active))
                    
                    # if the personnel's status is not active...
                    if(active == 0):
                        # auditing denied attempt to database
                        print('DOOR LOCKED: User is not an active personnel.')
                        cursor.execute(f"""INSERT INTO SJSU.AUDIT_ACCESS (TIMESTAMP, SERIAL_NUMBER, READER_NAME, USER_ID, DECISION, REASON) VALUES
                                        ("{get_current_time_iso().split('.')[0] + 'Z'}", {serial_number}, "FRONT_DOOR", "{user_id}"", "0", "User is not an active personnel.")""")
                        db.commit()
                        close_door(2)
                    # if the personnel's status is active...
                    else:
                        # auditing granted access to database
                        print("DOOR OPENED: UUID valid and active status true")
                        cursor.execute(f"""INSERT INTO SJSU.AUDIT_ACCESS (TIMESTAMP, SERIAL_NUMBER, READER_NAME, USER_ID, DECISION, REASON) VALUES
                                        ("{get_current_time_iso().split('.')[0] + 'Z'}", "{serial_number}", "FRONT_DOOR", "{user_id}", 1, "UUID valid and active status true")""")
                        db.commit()
                        open_door(5)
                    cursor.close()
                erase_ntag215()
                        
            except RuntimeError:
                print("Incomplete reading. Try again.")
                pass
        
        except TypeError:
            # auditing denied attempt to database (no instance of UUID match)
            print('DOOR LOCKED: UUID does not correspond to any user on database.')
            cursor.execute(f"""INSERT INTO SJSU.AUDIT_ACCESS (TIMESTAMP, SERIAL_NUMBER, READER_NAME, USER_ID, DECISION, REASON) VALUES
                                        ("{get_current_time_iso().split('.')[0] + 'Z'}", "{serial_number}", "FRONT_DOOR", "N/A", 0, "UUID does not correspond to any user on database")""")
            db.commit()
            close_door(2)
            cursor.close()
            erase_ntag215()
        
        except IndexError:
            print("Waiting for valid reading from NFC...")
        
        except Exception as e:
            print("Error:", e)
            uid = None
            erase_ntag215()
        
        # Wait a moment before scanning again
        uid = None
        db.disconnect()
        lcd.set_color_white()
