from flask import Flask, render_template, request, redirect, url_for
import serial
import time
from datetime import datetime

app = Flask(__name__)
ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.flushInput()

led_state = False

def get_temperature():
    try:
        ser.write(b'T\n')
        time.sleep(1)
        lines = []
        while ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            lines.append(line)
            if line.startswith("Temperature:"):
                return line.split(' ')[1]
        print("Debug: Received lines for temperature:", lines)
    except serial.SerialException:
        return "Serial port error"
    return "N/A"

def get_last_10_messages():
    try:
        ser.write(b'R\n')
        time.sleep(1)
        messages = []
        while len(messages) < 10:
            if ser.in_waiting > 0:
                message = ser.readline().decode().strip()
                if message:
                    messages.append(message)
                else:
                    messages.append("")  # Add empty message if none is received
        return messages
    except serial.SerialException:
        return ["Serial port error"]

def get_last_10_water_levels():
    try:
        ser.write(b'S\n')
        time.sleep(1)
        water_levels = []
        while len(water_levels) < 10:
            if ser.in_waiting > 0:
                water_level = ser.readline().decode().strip()
                if water_level:
                    water_levels.append(water_level)
                else:
                    water_levels.append("")  # Add empty water level if none is received
        return water_levels
    except serial.SerialException:
        return ["Serial port error"]

@app.route('/')
def index():
    temperatura = get_temperature()
    messages = get_last_10_messages()
    water_levels = get_last_10_water_levels()
    return render_template('index.html', temperatura=temperatura, led_state=led_state, messages=messages, water_levels=water_levels)

@app.route('/toggle_led', methods=['POST'])
def toggle_led():
    global led_state
    try:
        led_state = not led_state
        ser.write(b'L\n')
        time.sleep(1)
        return 'status-on' if led_state else 'status-off'
    except serial.SerialException:
        return "Serial port error"

@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        message = request.form['message']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            ser.write(('W:' + timestamp + '|' + message + "\n").encode())
            time.sleep(1)
            return redirect(url_for('index'))
        except serial.SerialException:
            return "Serial port error"

@app.route('/delete_message/<int:message_index>', methods=['POST'])
def delete_message(message_index):
    try:
        ser.write(('DM:' + str(message_index) + '\n').encode())
        time.sleep(1)
        return redirect(url_for('index'))
    except serial.SerialException:
        return "Serial port error"

@app.route('/delete_water_message/<int:message_index>', methods=['POST'])
def delete_water_message(message_index):
    try:
        ser.write(('DW:' + str(message_index) + '\n').encode())
        time.sleep(1)
        return redirect(url_for('index'))
    except serial.SerialException:
        return "Serial port error"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
