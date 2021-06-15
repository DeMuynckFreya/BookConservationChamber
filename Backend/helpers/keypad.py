from RPi import GPIO
import time
GPIO.setmode(GPIO.BCM)

class Keypad():
    def __init__(self, row_pins=[26, 19, 13, 6], column_pins=[5, 27, 17]):
        self.row_pins = row_pins
        self.column_pins = column_pins
        self.values = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            ['*', 0, '#']
        ]
    
    def _initialise_pins(self):
        for i in range(len(self.column_pins)):
            GPIO.setup(self.column_pins[i], GPIO.OUT, initial=GPIO.LOW)

        for j in range(len(self.row_pins)):
            GPIO.setup(self.row_pins[j], GPIO.IN, pull_up_down = GPIO.PUD_UP)

    def _read_key(self):
        self._initialise_pins()

        row = -1
        for i in range(len(self.row_pins)):
            temp_value = GPIO.input(self.row_pins[i])
            if temp_value == 0:
                row = i
                break
        
        if row < 0 or row > 3:
            self._leaving()
            return

        for i in range(len(self.column_pins)):
            GPIO.setup(self.column_pins[i], GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        
        GPIO.setup(self.row_pins[row], GPIO.OUT, initial=GPIO.HIGH)

        column = -1
        for i in range(len(self.column_pins)):
            temp_value = GPIO.input(self.column_pins[i])
            if temp_value == 1:
                column = i
                break
        
        if column < 0 or column > 2:
            self._leaving()
            return
        
        self._leaving()
        return self.values[row][column]

    def _leaving(self):
        for i in range(len(self.row_pins)):
            GPIO.setup(self.row_pins[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)
        for i in range(len(self.column_pins)):
            GPIO.setup(self.column_pins[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

    def get_key(self):
        value = None
        while value == None:
            value = self._read_key()
        
        print(value)
        return value
