from flask import Flask, render_template, request, redirect
import serial

app = Flask(__name__)
ser = serial.Serial('/dev/ttyUSB0', 9600)

led_state = False


@app.route('/')
def index():
    try:
        temperatura = ser.readline().decode().strip()
        return render_template('index.html', temperatura=temperatura, led_state=led_state)
    except serial.SerialException:
        return "Serial port error"

@app.route('/toggle_led', methods=['POST'])
def toggle_led():
    global led_state
    try:
        led_state = not led_state
        ser.write(b'A' if led_state else b'S')
        return 'status-on' if led_state else 'status-off'
    except serial.SerialException:
        return "Serial port error"

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    messages.append(message)
    # Trimiteti mesajul la Arduino prin portul serial
    # Arduino va gestiona stocarea sn EEPROM si alte actiuni
    return "Message sent to Arduino: " + message

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
