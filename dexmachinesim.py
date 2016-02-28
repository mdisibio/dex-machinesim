import serial
import dexcrc16
from time import sleep

    
SOH = chr(0x01)
STX = chr(0x02)
ETX = chr(0x03)
EOT = chr(0x04)
DLE = chr(0x10)
ENQ = chr(0x05)
NAK = chr(0x15)
ETB = chr(0x17)
    
class DexMachineSim:
    def __init__(self,serialPath, dexContent, stayOpen=True):
        self.path = serialPath
        self.content = dexContent
        self.stayOpen = stayOpen
        self.ser = None
    
    def run(self):
        while True:
            print "--------------------------------"
            self.openConnection()
            try:
                self.waitConnection()
            except serial.SerialException:
                print "Serial exception"
                print "Closing connection"
                self.ser.close()
                if not self.stayOpen:
                    return
            
    def openConnection(self):
        print "opening connection to " + self.path
        self.ser = serial.Serial(self.path, 9600, timeout=0.01)
                
    def waitConnection(self):
        print "Waiting for connection"
        while True:
            x = self.ser.read()
            if len(x) > 0:
                self.printReceivedData(x)
                for char in x:
                    if char == ENQ:
                        print "Received ENQ for init"
                        
                        #master mode 
                        self.ser.write(ENQ)
                        self.ser.flush()
                        self.slaveHandshake()
                        self.masterHandshake()
                        self.exchangeData()
                        
                        # slave mode
                        #ser.write(DLE)
                        #masterHandshake()
                        #slaveHandshake()
                        #exchangeData()
                        
                        while True:
                            x = self.ser.read()
                            if len(x) > 0:
                                self.printReceivedData(x)
                

    def masterHandshake(self):
        print "Entering Master Handshake"
        receivedData = ""
        
        print "Waiting for ready"
        ready = False 
        while not ready:
            for i in range(0,5):
                x = self.ser.read()
                if x == ENQ:
                    print "Received ENQ, replying.."
                    self.ser.write(DLE)
                    self.ser.write('0')
                    self.ser.flush()
                    ready = True
                    print "Received ready response"
        
        print "Waiting Master check string"
        while True:
            x = self.ser.read()
            if len(x) > 0:
                self.printReceivedData(x)
                receivedData += x
                
                if len(receivedData) >= 4 and \
                    receivedData[-4] == DLE and \
                    receivedData[-3] == ETX:
                    print "Received master check string and CRC. Auto-confirming it."
                    self.ser.write(DLE)
                    self.ser.write('0')
                    
                if len(receivedData) >= 1 and receivedData[-1] == EOT:
                    print "Received EOT, end of master handshake."
                    return
                
    def slaveHandshake(self):
        print "Entering slave handshake"
        self.ser.flushInput()
        receivedData = ""
        print "waiting for ready"
        self.ser.write(ENQ)
        self.ser.flush()   
        ready = False 
        while not ready:
            for i in range(0,5):
                x = self.ser.read()
                if len(x) > 0:
                    receivedData += x
                    if len(receivedData) >= 2 and \
                            receivedData[-2] == DLE and \
                            receivedData[-1] == '0':
                        print "Recevied ready response"
                        ready = True
                        break
            if not ready:
                self.ser.write(ENQ)
                self.ser.flush()

        
        self.ser.write(EOT)
        self.ser.flush()
        while True:
            x = self.ser.read()
            if len(x) > 0:
                self.printReceivedData(x)
                if x == ENQ:
                    self.ser.write(ENQ)
            else:
                self.ser.write(EOT)
                self.ser.flush()
                return
        print "end of slave handshake"
        
    def printReceivedData(self, data):
        print "Received data:",data,"=",data.encode('hex')
        
    def uploadblock(self,data, final):
        finalmarker = ETB
        if final:
            finalmarker = ETX

        crc = dexcrc16.crcStr(data  + finalmarker)
        print "Writing block:", data.rstrip(),"CRC=",crc
        self.ser.flushInput()
        sleep(0.01)
        self.ser.write(DLE)
        self.ser.write(STX)
        self.ser.write(data)
        self.ser.write(DLE)
        self.ser.write(finalmarker)
        
        # Write checksum
        self.ser.write(chr(crc & 0xFF))
        self.ser.write(chr(crc >> 8))
        
        receivedData = ""
        while True:
            x = self.ser.read()
            if len(x) > 0:
                self.printReceivedData(x)
                receivedData += x
                if len(receivedData) >= 2 and \
                        receivedData[-2] == DLE and \
                        (receivedData[-1] == '0' or receivedData[-1]=='1'):
                    print "received confirmation of block" 
                    return
        
    def waitForExchangeReady(self):    
        ready = False
        print "Waiting for ready signal before exchanging data" 
        self.ser.flushInput()
        sleep(0.01)
        receivedData = ""
        print "Writing ENQ"        
        self.ser.write(ENQ)
        self.ser.flush()
        while not ready:
            for i in range(0,5):
                x = self.ser.read()
                if len(x) > 0:
                    self.printReceivedData(x)
                    receivedData += x
                    if len(receivedData) >= 2 and \
                            receivedData[-2] == DLE and \
                            receivedData[-1] == '0':
                        print "Received query response"
                        ready = True
                        break
            if not ready:
                print "Not ready yet. Writing ENQ"                
                self.ser.write(ENQ)
                self.ser.flush()
               
    def exchangeData(self):
        print "Exchanging data"
        self.waitForExchangeReady()
                    
        for i,block in enumerate(self.content):
            final = i == len(self.content) -1            
            self.uploadblock(block, final)
        
        print "writing end of transmission"
        self.ser.write(EOT)
        
        while True:
            x = self.ser.read()
            if x == NAK:
                print "got a nack"
                
            if len(x) > 0:
                self.printReceivedData(x)
                receivedData += x
                
                if len(receivedData) >= 2 and \
                    receivedData[-2] == DLE:
                    print "received response"
                    break
        self.ser.write(EOT)
        self.ser.flush()
        return