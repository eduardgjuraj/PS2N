from flask import Flask, render_template, request, redirect, url_for, jsonify
import serial
import time
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl

app = Flask(__name__)
ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.flushInput()

led_state = False

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465  # For SSL
SMTP_USERNAME = 'floodalertps@gmail.com'
SMTP_PASSWORD = 'vlcp hoiu znzo cvlo '
EMAIL_FROM = 'floodalertps@gmail.com'
EMAIL_TO = 'floodalertps@gmail.com' 

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

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

def get_water_sensor():
    try:
        ser.write(b'D\n')
        time.sleep(1)
        lines = []
        while ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            lines.append(line)
            if line.startswith("Water detected:"):
                water_level = line.split(' ')[2]
                send_email("Water Level Alert", f"Detected water level: {water_level}")
                return water_level
        print("Debug: Received lines for water sensor:", lines)
    except serial.SerialException:
        return "Serial port error"
    return "N/A"

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
        print(f"Deleting message at index: {message_index}")  # Debug print
        ser.write(('M:' + str(message_index) + '\n').encode())
        time.sleep(1)
        return redirect(url_for('index'))
    except serial.SerialException:
        return "Serial port error"

@app.route('/delete_water_message/<int:message_index>', methods=['POST'])
def delete_water_message(message_index):
    try:
        print(f"Deleting water message at index: {message_index}")  # Debug print
        ser.write(('w:' + str(message_index) + '\n').encode())
        time.sleep(1)
        return redirect(url_for('index'))
    except serial.SerialException:
        return "Serial port error"

@app.route('/update_water_sensor', methods=['GET'])
def update_water_sensor():
    water_sensor_value = get_water_sensor()
    return jsonify({'water_sensor_value': water_sensor_value})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
