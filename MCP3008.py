from spidev import SpiDev

class MCP3008:
    def __init__(self, bus = 0, device = 0):
        #print("\nJeremy MCP")
        self.bus, self.device = bus, device
        #print("\nJeremy spi")
        self.spi = SpiDev()
        #print("\nJeremy open")
        self.open()
        #print("\nJeremy hz")
        self.spi.max_speed_hz = 1000000 # 1MHz
        #print("\nJeremy exit")

    def open(self):
        self.spi.open(self.bus, self.device)
        self.spi.max_speed_hz = 1000000 # 1MHz
    
    def read(self, channel = 0):
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data
            
    def close(self):
        self.spi.close()
