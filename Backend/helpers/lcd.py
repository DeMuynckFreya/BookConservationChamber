from subprocess import check_output
from RPi import GPIO
import time
from helpers.pcf import PCF
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#variabelen
E = 23 #LCD
RS = 24 #LCD

addr = 0x38 # adres PCF8574

class LCD:
    i2c = PCF()
    def __init__(self, I2C=i2c, E=23, RS=24):
        self.E = E
        self.RS = RS
        self.I2C = I2C
        GPIO.setup([self.RS, self.E], GPIO.OUT, initial=GPIO.LOW)
        self.init_LCD()
        self.get_ip()

    def _send_instruction(self, value):
        GPIO.output(self.RS, GPIO.LOW)
        GPIO.output(self.E, GPIO.HIGH)
        self._set_data_bits(value)
        GPIO.output(self.E, GPIO.LOW)
        time.sleep(0.01)

    def _send_character(self, value):
        GPIO.output(self.RS, GPIO.HIGH)
        GPIO.output(self.E, GPIO.HIGH)
        self._set_data_bits(value)
        GPIO.output(self.E, GPIO.LOW)
        time.sleep(0.01)

    def _set_data_bits(self, value):
        self.I2C._write_byte(value)

    def init_LCD(self):
        self._send_instruction(0x38) #8bit, 2 lijnen, 5*7 display
        self._send_instruction(0x0C) #display on, cursor off, blinking off
        #self._send_instruction(0x01)
        self.clear_LCD()

    def clear_LCD(self):
        self._send_instruction(0x01)

    def second_row(self):
        self._send_instruction(0x80 | 0x40)

    def write_message(self, mesg):
        res = []
        res[:] = mesg
        for i in range(0, len(res)):
            if i == 16:
                self.second_row()
            teken = ord(res[i])
            self._send_character(teken)

    def move_cursor(self, row, column):
        value = row << 6 | column #rij 1 = 0x0*/ rij 2 = 0x4* 
        self._send_instruction(0x80 | value)

    def get_ip(self):
        ips = check_output(['hostname','--all-ip-addresses']).split()
        for i in range(len(ips)):
            test = ips[i]
            tes = test.decode('utf-8')
            ips[i] = tes
        print(ips[0])
        self.write_message(ips[0])
        if len(ips) > 1:
            print(ips[1])
            self.second_row()
            self.write_message(ips[1])
