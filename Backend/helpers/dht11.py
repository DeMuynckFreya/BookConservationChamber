import time
from RPi import GPIO
GPIO.setmode(GPIO.BCM)

class CheckDHT11Result:
    ERR_NO_ERROR = 0
    ERR_MISSING_DATA = 1
    ERR_CRC = 2

    error_code = ERR_NO_ERROR
    temperature = -1
    humidity = -1

    def __init__(self, error_code, humidity, temperature):
        self.error_code = error_code
        self.temperature = temperature
        self.humidity = humidity

    def is_valid(self):
        return self.error_code == CheckDHT11Result.ERR_NO_ERROR


class DHT11:

    'DHT11 sensor reader class for Raspberry'


    def __init__(self, pin=4):
        self.pin = pin

    def get_data(self):
        # send initial high for 50ms
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)
        time.sleep(0.05)

        # send low for 20 ms
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(0.02)

        # change to input
        GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_UP)

        # collect data into a list
        data = self.__collect_data()

        # parse lengths of all data pull up periods
        pull_up_lengths = self.__parse_pull_up_lengths(data)

        # if bit count is not correct, return error (4 byte data + 1 byte checksum)
        if len(pull_up_lengths) != 40:
            return CheckDHT11Result(CheckDHT11Result.ERR_MISSING_DATA, 0, 0)

        # calculate bits from lengths of the pull up periods and convert to bytes
        list_of_bytes = self.__calculate_bytes(pull_up_lengths)

        # calculate checksum and check
        checksum = list_of_bytes[0] + list_of_bytes[1] + list_of_bytes[2] + list_of_bytes[3] & 255
        if list_of_bytes[4] != checksum:
            return CheckDHT11Result(CheckDHT11Result.ERR_CRC, 0, 0)

        # list_of_bytes[0]: humidity int
        # list_of_bytes[1]: humidity decimal
        # list_of_bytes[2]: temperature int
        # list_of_bytes[3]: temperature decimal

        humidity = list_of_bytes[0] + float(list_of_bytes[1]) / 10
        temperature = list_of_bytes[2] + float(list_of_bytes[3]) / 10

        return CheckDHT11Result(CheckDHT11Result.ERR_NO_ERROR, humidity, temperature)

    def __collect_data(self):
        # collect the data while unchanged found
        unchanged_count = 0

        # determinates the end of the data
        max_unchanged_count = 100

        last = -1
        data = []
        while True:
            current = GPIO.input(self.pin)
            data.append(current)
            if last != current:
                unchanged_count = 0
                last = current
            else:
                unchanged_count += 1
                if unchanged_count > max_unchanged_count:
                    break
        return data

    def __parse_pull_up_lengths(self, data):
        INIT_PULL_DOWN_STATE = 1
        INIT_PULL_UP_STATE = 2
        FIRST_DATA_PULL_DOWN_STATE = 3
        DATA_PULL_UP_STATE = 4
        DATA_PULL_DOWN_STATE = 5

        current_state = INIT_PULL_DOWN_STATE

        pull_up_lengths = [] # will contain the lengths of data pull up periods
        current_length = 0 # will contain the length of the previous period

        for i in range(len(data)):

            current = data[i]
            current_length += 1

            if current_state == INIT_PULL_DOWN_STATE:
                if current == GPIO.LOW:
                    # initial pull down
                    current_state = INIT_PULL_UP_STATE
                    continue
                else:
                    continue
            if current_state == INIT_PULL_UP_STATE:
                if current == GPIO.HIGH:
                    # initial pull up
                    current_state = FIRST_DATA_PULL_DOWN_STATE
                    continue
                else:
                    continue
            if current_state == FIRST_DATA_PULL_DOWN_STATE:
                if current == GPIO.LOW:
                    # initial data pull down, the next will be the data pull up
                    current_state = DATA_PULL_UP_STATE
                    continue
                else:
                    continue
            if current_state == DATA_PULL_UP_STATE:
                if current == GPIO.HIGH:
                    # data pulled up, the length of this pull up will determine whether it is 0 or 1
                    current_length = 0
                    current_state = DATA_PULL_DOWN_STATE
                    continue
                else:
                    continue
            if current_state == DATA_PULL_DOWN_STATE:
                if current == GPIO.LOW:
                    # pulled down, we store the length of the previous pull up period
                    pull_up_lengths.append(current_length)
                    current_state = DATA_PULL_UP_STATE
                    continue
                else:
                    continue

        return pull_up_lengths

    def __calculate_bytes(self, pull_up_lengths):
        # find shortest and longest period
        shortest_pull_up = 1000
        longest_pull_up = 0

        for i in range(0, len(pull_up_lengths)):
            length = pull_up_lengths[i]
            if length < shortest_pull_up:
                shortest_pull_up = length
            if length > longest_pull_up:
                longest_pull_up = length

        # use the halfway to determine whether the period is long or short
        halfway = shortest_pull_up + (longest_pull_up - shortest_pull_up) / 2
        bits = []
        list_of_bytes = []
        byte = 0
        for i in range(0, len(pull_up_lengths)):
            bit = False
            if pull_up_lengths[i] > halfway:
                bit = True
            bits.append(bit)

        for i in range(0, len(bits)):
            byte = byte << 1
            if (bits[i]):
                byte = byte | 1
            else:
                byte = byte | 0
            if ((i + 1) % 8 == 0):
                list_of_bytes.append(byte)
                byte = 0

        return list_of_bytes
