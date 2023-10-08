from dynamixel_sdk import *   

class ax_12:
    def __init__(self, id, packetHandler, portHandler):
        self.id = id
        self.packetHandler = packetHandler
        self.portHandler = portHandler
        self._normalize()

    def _normalize(self):
        self.lower = self.packetHandler.read2ByteTxRx(self.portHandler, self.id, 6)[0]
        self.upper = self.packetHandler.read2ByteTxRx(self.portHandler, self.id, 8)[0]

        self.mid = int(self.lower + (0.5*(self.upper - self.lower)))

        self.inc = (self.upper - self.lower)*0.5

    # def goTo(self, targetVal, speed = 512):
    #     # print(targetVal)
    #     val = int(self.mid + targetVal*self.inc)
    #     val = min(val, self.upper)
    #     val = max(val, self.lower)
    #     self.con.goto(self.id, val, speed)

    def currentPos(self):
        return self.packetHandler.read2ByteTxRx(self.portHandler, self.id, 36)[0]
    
    def setSpeed(self, speed):
        self.packetHandler.write2ByteTxRx(self.portHandler, self.id, 32, bytes(speed))


    def readSpeed(self):
        return self.packetHandler.read2ByteTxRx(self.portHandler, self.id, 32)
    

    def param(self, targetPos):

        val = int(self.mid + targetPos*self.inc)
        val = min(val, self.upper)
        val = max(val, self.lower)

        return [DXL_LOBYTE(DXL_LOWORD(val)), DXL_HIBYTE(DXL_LOWORD(val)), DXL_LOBYTE(DXL_HIWORD(val)), DXL_HIBYTE(DXL_HIWORD(val))]
     

    def paramSpeed(self, targetPos, speed):

        val = int(self.mid + targetPos*self.inc)
        val = min(val, self.upper)
        val = max(val, self.lower)

        return [DXL_LOBYTE(DXL_LOWORD(val)), DXL_HIBYTE(DXL_LOWORD(val)), DXL_LOBYTE(DXL_LOWORD(speed)), DXL_HIBYTE(DXL_LOWORD(speed))]
     