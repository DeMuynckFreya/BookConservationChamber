from RPi import GPIO
import spidev
import time
GPIO.setmode(GPIO.BCM)

class RC522:
    #registers
    MAX_LEN = 16

    PCD_IDLE = 0x00
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F

    PICC_REQIDL = 0x26
    PICC_ANTICOLL = 0x93

    MI_OK = 0
    MI_NOTAGERR = 1
    MI_ERR = 2

    CommandReg = 0x01
    CommIEnReg = 0x02
    CommIrqReg = 0x04
    ErrorReg = 0x06
    FIFODataReg = 0x09
    FIFOLevelReg = 0x0A
    ControlReg = 0x0C
    BitFramingReg = 0x0D

    ModeReg = 0x11
    TxControlReg = 0x14
    TxAutoReg = 0x15

    TModeReg = 0x2A
    TPrescalerReg = 0x2B
    TReloadRegH = 0x2C
    TReloadRegL = 0x2D

    serNum = []

    def __init__(self, bus=0, device=0, speed=100000, reset_pin=22):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = speed
        self.reset_pin = reset_pin

        GPIO.setup(self.reset_pin, GPIO.OUT, initial=GPIO.HIGH)
        self.init_RC522()

    def init_RC522(self):
        self.reset_RC522()
        self.write_RC522(self.TModeReg, 0x8D)
        self.write_RC522(self.TPrescalerReg, 0x3E)
        self.write_RC522(self.TReloadRegL, 30)
        self.write_RC522(self.TReloadRegH, 0)
        self.write_RC522(self.TxAutoReg, 0x40)
        self.write_RC522(self.ModeReg, 0x3D)
        self.antenna_on()

    def reset_RC522(self):
        self.write_RC522(self.CommandReg, self.PCD_RESETPHASE)

    def write_RC522(self, addres, value):
        value = self.spi.xfer2([(addres << 1) & 0x7E, value])

    def read_RC522(self, addres):
        value = self.spi.xfer2([((addres << 1) & 0x7E) | 0x80, 0])
        return value[1]

    def set_bit_mask(self, register, mask):
        temp_value = self.read_RC522(register)
        self.write_RC522(register, temp_value |mask)

    def remove_bit_mask(self, register, mask):
        temp_value = self.read_RC522(register)
        self.write_RC522(register, temp_value & (~mask))

    def antenna_on(self):
        temp = self.read_RC522(self.TxControlReg)
        if (~(temp & 0x03)):
            self.set_bit_mask(self.TxControlReg, 0x03)
    
    def antenna_off(self):
        self.remove_bit_mask(self.TxControlReg, 0x03)

    def to_card_RC522(self, command, data_send):
        back_data = []
        back_len = 0
        status = self.MI_ERR
        irqEn = 0x00
        waitIRq = 0x00
        last_bits = None
        n = 0

        if command == self.PCD_TRANSCEIVE:
            irqEn = 0x77
            waitIRq = 0x30

        self.write_RC522(self.CommIEnReg, irqEn | 0x80)
        self.remove_bit_mask(self.CommIrqReg, 0x80)
        self.set_bit_mask(self.FIFOLevelReg, 0x80)
        self.write_RC522(self.CommandReg, self.PCD_IDLE)

        for i in range(len(data_send)):
            self.write_RC522(self.FIFODataReg, data_send[i])

        self.write_RC522(self.CommandReg, command)

        if command == self.PCD_TRANSCEIVE:
            self.set_bit_mask(self.BitFramingReg, 0x80)
        
        i = 2000
        while True:
            n = self.read_RC522(self.CommIrqReg)
            i -= 1
            if ~((i!=0) and ~(n & 0x01) and ~(n & waitIRq)):
                break
        
        self.remove_bit_mask(self.BitFramingReg, 0x80)

        if i != 0:
            if (self.read_RC522(self.ErrorReg) & 0x1B) == 0x00:
                status = self.MI_OK

                if n & irqEn & 0x01:
                    status = self.MI_NOTAGERR
                
                if command == self.PCD_TRANSCEIVE:
                    n = self.read_RC522(self.FIFOLevelReg)
                    last_bits = self.read_RC522(self.ControlReg) & 0x07
                    if last_bits != 0:
                        back_len = (n - 1)*8 + last_bits
                    else:
                        back_len = n*8

                    if n == 0:
                        n = 1
                    if n > self.MAX_LEN:
                        n = self.MAX_LEN
                    
                    for i in range(n):
                        back_data.append(self.read_RC522(self.FIFODataReg))
            
            else:
                status = self.MI_ERR
        
        return (status, back_data, back_len)

    def anticoll_RC522(self):
        back_data = []
        serial_number_check = 0
        serNum = []

        self.write_RC522(self.BitFramingReg, 0x00)
        serNum.append(self.PICC_ANTICOLL)
        serNum.append(0x20)

        (status, back_data, back_bits) = self.to_card_RC522(self.PCD_TRANSCEIVE, serNum)

        if status == self.MI_OK:
            i = 0
            if len(back_data) == 5:
                for i in range(4):
                    serial_number_check = serial_number_check ^ back_data[i]
                if serial_number_check != back_data[4]:
                    status = self.MI_ERR
            else:
                status = self.MI_ERR 
            
            return (status, back_data)

    def request_RC522(self, request_mode):
        status = None
        back_bits = None
        type_tag = []

        self.write_RC522(self.BitFramingReg, 0x07)
        type_tag.append(request_mode)
        (status, back_data, back_bits) = self.to_card_RC522(self.PCD_TRANSCEIVE, type_tag)
        if ((status != self.MI_OK) | (back_bits != 0x10)):
            status = self.MI_ERR

        return (status, back_bits)

    def read_id_check(self):
        (status, type_tag)= self.request_RC522(self.PICC_REQIDL)
        if status != self.MI_OK:
            return None
        (status, uid) = self.anticoll_RC522()
        if status != self.MI_OK:
            return None
        return self.uid_to_hex(uid)

    def read_id(self):
        id = self.read_id_check()
        while not id:
            id = self.read_id_check()
        return id
    
    def uid_to_hex(self, uid):
        n = '{0:02X}{1:02X}{2:02X}{3:02X}{4:02X}'.format(uid[0], uid[1], uid[2], uid[3],uid[4])
        return n

    def close_RC522(self):
        self.spi.close()
        GPIO.cleanup(self.reset_pin)
