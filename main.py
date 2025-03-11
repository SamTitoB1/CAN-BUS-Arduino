import serial
import cantools
from cantools.database.can import Database, Message, Signal

# Connect to Arduino Serial (Change port if needed)
SERIAL_PORT = "COM5"  # Change "COMx" to the correct port (e.g., "COM3" or "/dev/ttyUSB0")
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Create a new DBC database
db = Database()
message_dict = {}

print("Listening for CAN messages...")

while True:
    try:
        line = ser.readline().decode().strip()

        # Ignore non-CAN messages
        if not line or not line[0].isalnum():
            continue

        # Split the message into CAN ID and Data bytes
        parts = line.split(",")

        # Ensure at least 2 parts (ID + Data)
        if len(parts) < 2:
            continue  

        can_id = parts[0].strip()

        # Check if the first part is a valid hex CAN ID
        if not all(c in "0123456789ABCDEFabcdef" for c in can_id):
            print(f"Ignoring non-CAN message: {line}")
            continue

        # Convert CAN ID from HEX to integer
        can_id = int(can_id, 16)
        data_bytes = [int(x.strip(), 16) for x in parts[1:] if x]

        # If this is a new message ID, add it to the DBC
        if can_id not in message_dict:
            signals = [
                Signal(name=f"Signal_{i}", start=i * 8, length=8, scale=1, offset=0, unit="raw")
                for i in range(len(data_bytes))
            ]

            message = Message(frame_id=can_id, name=f"Message_{hex(can_id)}", length=len(data_bytes), signals=signals)
            db.messages.append(message)
            message_dict[can_id] = message

            # Update the DBC file immediately
            with open("arduino_can.dbc", "w") as f:
                f.write(db.as_dbc_string())

            print(f"Added new CAN ID: {hex(can_id)} -> DBC updated.")

    except Exception as e:
        print(f"Error: {e}")
