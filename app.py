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
        time.sleep(2)
        ser.close()
    except serial.SerialException:
        return "Serial port error"

@app.route('/toggle_led', methods=['POST'])
def toggle_led():
    global led_state
    try:
        led_state = not led_state
        ser.write(b'A' if led_state else b'S')
        return 'status-on' if led_state else 'status-off'
        time.sleep(2)
        ser.close()
    except serial.SerialException:
        return "Serial port error"

@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        message = request.form['message']
        ser.write((message + "\n").encode())
        return "Message sent to Arduino: " + message
        time.sleep(2)
        ser.close()

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
