import serial
import csv
import time

# Serial port settings
SERIAL_PORT = "/dev/tty.usbmodem1101"  # Update to your serial port
BAUD_RATE = 115200
LOG_FILE = "/Users/gabrielsalgado/downloads/tree_root_data.csv"
try:
    # Open Serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"Error: Could not open serial port. {e}")
    exit()

# Open CSV file for logging
with open(LOG_FILE, mode="w", newline="") as file:

    writer = csv.writer(file)
    writer.writerow(["distance", "temperature", "humidity", "label", "timestamp"])  # Header row
    writer.writerow([0, 0, 0, 0, "test"])  # Test row
    print("Test row written to CSV.")
    print("Logging data... Press Ctrl+C to stop.")
    try:
        while True:
            if ser.in_waiting > 0:
                # Read line from serial
                line = ser.readline().decode("utf-8").strip()
                print(f"Raw data: {line}")  # Debugging: Print raw data

                # Parse data
                if "Distance:" in line and "Temperature:" in line and "Humidity:" in line:
                    try:
                        # Extract values
                        distance = float(line.split("Distance: ")[1].split(" cm")[0])
                        temperature = float(line.split("Temperature: ")[1].split(" °C")[0])
                        humidity = float(line.split("Humidity: ")[1].split(" %")[0])

                        # Add a label for tree root detection (Example logic: Adjust as needed)
                        label = 1 if distance < 10 else 0

                        # Get timestamp
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                        # Write to CSV
                        writer.writerow([distance, temperature, humidity, label, timestamp])
                        print(f"Logged: {distance}, {temperature}, {humidity}, {label}, {timestamp}")
                    except ValueError as e:
                        print(f"Error parsing data: {line}. {e}")
    except KeyboardInterrupt:
        print("\nLogging stopped.")
    except Exception as e:
        print(f"Error: {e}")
        

