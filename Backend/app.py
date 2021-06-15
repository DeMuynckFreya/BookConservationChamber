from helpers.rc522 import RC522
from helpers.keypad import Keypad
from helpers.dht11 import DHT11
from subprocess import call
from helpers.lcd import LCD 


import time
from RPi import GPIO
import threading
import datetime
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify
import serial
import math
from repositories.DataRepository import DataRepository

# Code voor Hardware
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
btn_poweroff = 16
btn_lock = 12
lock_btn_state = 0

def btn_lock_pressed(pin):
    global lock_btn_state
    print('lock button pressed')
    lock_btn_state = not lock_btn_state
    print(lock_btn_state)

def btn_poweroff_pressed(pin):
    global lock_btn_state
    print('poweroff button pressed')
    lock_btn_state = 0
    time.sleep(2)
    call("echo W8w00rd | sudo -S shutdown -h now", shell=True)
    

GPIO.setup(btn_lock, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(btn_lock, GPIO.FALLING, bouncetime=300)
GPIO.add_event_callback(btn_lock, btn_lock_pressed)    
GPIO.setup(btn_poweroff, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(btn_poweroff, GPIO.FALLING, bouncetime=300)
GPIO.add_event_callback(btn_poweroff, btn_poweroff_pressed)
lcd = LCD()
dht = DHT11()
keypad = Keypad()
passcode = '1234'
servo_state = 1
scan_mode = 0
rc = RC522()

def serial_message(request):
    ser = serial.Serial('/dev/serial0',9600, timeout=1)
    ser.write(str.encode(request))
    line = ser.readline().decode(encoding='utf-8')
    if line == "":
        line = ser.readline().decode(encoding='utf-8').strip('\n')
    ser.close()
    return line

def get_ldr():
    line = serial_message('LDR')
    print(line)
    value = float(line)
    if (math.isnan(value) == False and value > 0):
        DataRepository.create_sensor_history(3, value)
        
def close_lock():
    global servo_state
    global scan_mode
    global lock_btn_state
    line = serial_message('close')
    print('lock: {0}'.format(line))
    DataRepository.create_actuator_history(6,0)
    servo_state = 0
    scan_mode = 0
    lock_btn_state = False

def open_lock():
    global servo_state
    global scan_mode
    global lock_btn_state
    line = serial_message('open')
    print('lock: {0}'.format(line))
    DataRepository.create_actuator_history(6,1)
    servo_state = 1
    scan_mode = 1
    lock_btn_state = True


def get_dht11():
    while True:
        result = dht.get_data()
        if result.is_valid():
            print("Temperature: %-3.1f C" % result.temperature)
            print("Humidity: %-3.1f %%" % result.humidity)
            break
        time.sleep(3)
    DataRepository.create_sensor_history(1,result.temperature)
    DataRepository.create_sensor_history(2,result.humidity)
    
    if result.temperature > 20.5:
        DataRepository.create_actuator_history(7,1)
        fan_control()
    if result.temperature < 19.5:
        DataRepository.create_actuator_history(7,0)
        fan_control()
    

def fan_control():
    # print('fan control')
    status = DataRepository.read_component_history(7,1)
    # print(status)
    status = setValidTime(status)
    # print(status)
    actuatorStatus = int(status[0]['Action'])
    print('ventilator {0}'.format(actuatorStatus))
        
    if actuatorStatus == 1:  
        GPIO.output(21,GPIO.HIGH)
    if actuatorStatus == 0:
        GPIO.output(21,GPIO.LOW)

# Code voor Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)
endpoint = '/api/v1'

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


# START een thread op. Belangrijk!!! Debugging moet UIT staan op start van de server, anders start de thread dubbel op
# werk enkel met de packages gevent en gevent-websocket.
def control_lock():
    global servo_state
    global lock_btn_state
    global scan_mode
    entered_code = ''
    while True:
        if lock_btn_state == True:
            if entered_code == '' and servo_state == 0:
                lcd.clear_LCD()
                lcd.write_message('Enter passcode')
                lcd.second_row()
            if len(entered_code) < 4 and servo_state == 0:
                digit = keypad.get_key()
                entered_code += str(digit)
                lcd.write_message(str(digit))
                print(entered_code)
            if len(entered_code) == 4:
                if entered_code == passcode and servo_state == 0:
                    print('lock will open now')
                    open_lock()
                    servo_state = 1
                    scan_mode = 1
                if entered_code != passcode:
                    time.sleep(0.5)
                    lcd.clear_LCD()
                    lcd.write_message('Wrong passcode  Try again')
                    time.sleep(1)
                    scan_mode = 0
                    print('wrong passcode')
                    entered_code = ''
                if scan_mode == 1:
                    lcd.clear_LCD()
                    lcd.write_message('Scan book')
                    id = rc.read_id_check()
                    while not id:
                        if lock_btn_state == False:
                            break
                        id = rc.read_id_check()
                    if id:
                        print(id)
                        data = DataRepository.read_book_by_rfid(id)['Title']
                        change_book_status(id)
                        print(data)
                        lcd.clear_LCD()
                        lcd.write_message(data)
                    
            time.sleep(1)

        if lock_btn_state == False:
            if servo_state != 0:
                scan_mode = 0
                print('close lock now')
                lcd.clear_LCD()
                lcd.get_ip()
                close_lock()
                servo_state = 0
                entered_code = ''
            time.sleep(1)
        time.sleep(1)
        
    
def get_sensors():
    while True:
        get_dht11()
        get_ldr()
        # get_temp_and_humid()
        # get_light()
        # get_current_stats()
        time.sleep(300)


thread = threading.Timer(1, control_lock)
thread.start()
thread2 = threading.Timer(5, get_sensors)
thread2.start()

print("**** Program started ****")

# API ENDPOINTS


@app.route('/')
def info():
    return jsonify(info='Please go to the endpoint ' + endpoint)

@app.route(endpoint + '/books', methods=['GET'])
def get_books():
    data = DataRepository.read_books_and_author()
    print(f'Data is: {data}')
    return jsonify(data), 200

@app.route(endpoint + '/books/<id>', methods=['GET'])
def get_book_by_id(id):
    data = DataRepository.read_book(id)
    print(f'Data is: {data}')
    return jsonify(data), 200


@app.route(endpoint + '/history/<id>', methods=['GET'])
def get_history_by_id(id):
    data = DataRepository.read_component_history(id)
    print(f'Data is: {data}')
    return jsonify(data), 200



@socketio.on('connect')
def initial_connection():
    print('A new client connect')


@socketio.on('F2B_get_light')
def get_light():
    get_ldr()
    today = DataRepository.read_component_history(3, 10)
    today = setValidTime(today)
    
    emit('B2F_light_history', {'today': today}, broadcast=True)

@socketio.on('F2B_get_temperature_and_humidity')
def get_temp_and_humid():
    get_dht11()
    today = DataRepository.read_component_history(1, 10)
    today1 = DataRepository.read_component_history(2, 10)
    today = setValidTime(today)
    today1 = setValidTime(today1)
    emit('B2F_temperature_and_humidity_history', {'today': today, 'humiditytoday':today1}, broadcast=True)

@socketio.on("F2B_rfidtag")
def get_tag():
    lcd.clear_LCD()
    lcd.write_message('Scan rfid tag')
    print('scan tag')
    uid = rc.read_id_check()
    while not uid:
        uid = rc.read_id_check()
    print("uid: {0}".format(uid))
    lcd.second_row()
    lcd.write_message(uid)
    emit('B2F_rfidtag', {'tag': uid}, broadcast=True)

@socketio.on('F2B_change_fan')
def change_fan(data):
    # print('change fan')
    # print(data)
    componentId = int(data['component_id'])
    status = DataRepository.read_component_history(componentId,1)
    # print(status)
    currentState = status[0]['Action']
    # print(currentState)
    newState = 0
    if currentState == 0:
        newState = 1
    elif currentState == 1:
        newState = 0
    # print(newState)
    DataRepository.create_actuator_history(componentId,newState)
    fan_control()
    emit('B2F_change_fan', {'fan': newState}, broadcast=True )

@socketio.on('F2B_get_fan_and_lock')
def get_fan_and_lock():
    # print('get fan')
    status_fan = DataRepository.read_component_history(7,1)
    status_lock = DataRepository.read_component_history(6,1)
    # print(status)
    status_fan = setValidTime(status_fan)
    status_lock = setValidTime(status_lock)
    emit('B2F_get_fan_and_lock', {'fan': status_fan, 'lock': status_lock}, broadcast=True)

@socketio.on('F2B_get_current_stats')
def get_current_stats():
    get_dht11()
    get_ldr()
    # print('current stats')
    temperature = DataRepository.read_component_history(1,1)
    humidity = DataRepository.read_component_history(2,1)
    luminosity = DataRepository.read_component_history(3,1)
    # print(temperature[0]['Value'])
    # print(humidity)
    # print(luminosity)
    temperature = setValidTime(temperature)
    humidity = setValidTime(humidity)
    luminosity = setValidTime(luminosity)
    emit('B2F_current_stats', {'temperature':temperature, 'humidity': humidity, 'luminosity':luminosity}, broadcast=True)

@socketio.on('F2B_books_in_chamber')
def books_in_chamber():
    status = DataRepository.read_books_by_present_in_chamber(1)
    emit('B2F_books_in_chamber',{'books':status}, broadcast=True)


@socketio.on('F2B_change_lock')
def change_lock(data):
    print('change lock')
    lock_state = -1
    print(data)
    componentId = int(data['component_id'])
    print(componentId)
    status = DataRepository.read_component_history(6,1)
    print(status)
    if status[0]['Action'] == 0:
        open_lock()
        lock_state = 1
    if status[0]['Action'] == 1:
        close_lock()
        lock_state = 0
    if lock_state != -1:
        emit('B2F_change_lock', {'lock': lock_state}, broadcast=True )
       

@socketio.on('F2B_get_all_books_and_authors')
def get_books_with_authors(): 
    status = DataRepository.read_books_and_author() 
    emit('B2F_get_all_books_and_authors',{'books': status}, broadcast=True)

@socketio.on('F2B_savebook')
def save_book(data):
    print(data)
    title = data['book']['title']
    firstname = data['book']['firstname']
    lastname = data['book']['lastname']
    language = data['book']['language']
    pages = data['book']['pages']
    isbn = data['book']['isbn']
    rfid = data['book']['rfid']
    inchamber = data['book']['inchamber']
    author_id = DataRepository.read__author_by_name(firstname,lastname)
    # print(author_id)
    if len(author_id) == 0:
        print('author does not exist yet')
        DataRepository.add_author(firstname, lastname)
        author_id = DataRepository.read__author_by_name(firstname,lastname)[0]['AuthorID']  
    else:
        author_id = author_id[0]['AuthorID']
    # print(author_id)
    DataRepository.create_book(rfid,isbn,title,author_id,language,pages,inchamber)
    print('book saved')
    emit('B2F_savebook',{'status': 'succes'}, broadcast=True)

# ANDERE FUNCTIES
def setValidTime(status):
    for i in range(len(status)):
        status[i]['EntryDate'] = status[i]['EntryDate'].strftime("%Y-%m-%dT%H:%M:%S+01:00")
    return status

def change_book_status(id):
    current = DataRepository.read_book_by_rfid(id)
    current_state = current['PresentInChamber']
    current_id = current['BookID']
    if current_state == 1:
        DataRepository.update_book_present_in_chamber(0,current_id)
    if current_state == 0:
        DataRepository.update_book_present_in_chamber(1,current_id)
    


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
