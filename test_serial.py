import serial

def toggle_led():
    global led_state
    try:
        # Open serial port
        ser = serial.Serial('/dev/ttyUSB0', 9600)
        
        # Toggle LED state
        led_state = not led_state
        
        # Send command to Arduino to toggle LED
        if led_state:
            ser.write(b'A')  # Turn LED on
        else:
            ser.write(b'S')  # Turn LED off
        
        # Close serial port
        ser.close()
        
        # Redirect back to the index page
        return index()
    except serial.SerialException:
        # Handle serial port error
        return "Serial port error"


