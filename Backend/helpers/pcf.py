from smbus import SMBus

class PCF:
    def __init__(self, addres=0x38):
        self.i2c = SMBus()
        self.i2c.open(1)
        self.addr = addres
        # waarde = self.i2c.read_byte(0x38)
    
    def _write_byte(self, hex_value):
        self.i2c.write_byte(self.addr, hex_value)