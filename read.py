import serial
import crc16
from time import sleep
from enum import Enum

class MachineState(Enum):
    init = 1
    master_handshake=2
    slave_handshake=2

ser = serial.Serial('/dev/ptyp3', 9600, timeout=0.01)
    
SOH = chr(0x01)
STX = chr(0x02)
ETX = chr(0x03)
EOT = chr(0x04)
DLE = chr(0x10)
ENQ = chr(0x05)
NAK = chr(0x15)
ETB = chr(0x17)
state=MachineState.init

def crcblah(crc, data):
    data = ord(data)
    DATA_0 = 0
    BCC_0 = 0
    BCC_1 = 0
    BCC_14 = 0
    X2 = 0
    X15 = 0
    X16 = 0
    BCC = crc
    for j in range(0,8):
        DATA_0 = (data >> j) & 0x0001
        BCC_0  = (BCC) & 0x0001
        BCC_1  = (BCC >>  1) & 0x0001
        BCC_14 = (BCC >> 14) & 0x0001     
        X16 = (BCC_0  ^ DATA_0) & 0x0001
        X15 = (BCC_1  ^ X16) & 0x0001
        X2  = (BCC_14 ^ X16) & 0x0001     
        BCC = BCC >> 1
        BCC = BCC & 0x5FFE
        BCC = BCC | X15
        BCC = BCC | (X2  << 13)
        BCC = BCC | (X16 << 15)
    return BCC
    
def crcofstr(str):
    crc = 0
    for char in str:
        crc = crcblah(crc, char)
    return crc
    
def crccheck(str):
    crc = crcofstr(str)
    high = crc >> 8
    low = crc & 0xFF
    print crcofstr(str + chr(low) + chr(high))
   
def handleInit(data):
    if data == ENQ:
        print "Received ENQ for init"
        #ser.write(DLE)
        ser.write(ENQ) 
        state = MachineState.master_handshake
        ser.write(EOT)
    else:
        print "Data doesn't match state in init"
        
def masterHandshake():
    print "Doing master handshake"
    receivedData = ""
    while True:
        x = ser.read()
        if len(x) > 0:
            print "Recevied data in master handshake: " + x + "=" + x.encode('hex')
            receivedData += x
            
            if len(receivedData) >= 4 and \
                   receivedData[-4] == DLE and \
                   receivedData[-3] == ETX:
                print "received crc and stuff"
                ser.write(DLE)
                ser.write('0')
                #print ser.read().encode('hex')
                #return
            if len(receivedData) >= 1 and receivedData[-1] == EOT:
                print "end of master handshake"
                return
        #else:    
        #    ser.write(DLE)
        #    ser.write('0')
            
def slaveHandshake():
    print "Doing slave handshake"
    ser.flushInput()
    sleep(0.01)
    #ser.write(DLE)
    ser.write(EOT)
    ser.flush()
    #ser.write(EOT)
    #ser.write(EOT)
    #ser.write(EOT)
    #ser.flush()
    while True:
        x = ser.read()
        if len(x) > 0:
            print "Recevied data in slave handshake: " + x + "=" + x.encode('hex')
        else:
            ser.write(EOT)
            ser.flush()
            return
    print "end fo slave handshake"
    
def uploadblock(data):
    print "writing block: " + data
    crc = crc16.crc16xmodem(data  + ETX)
    print "old crc is ", crc
    crc = 0
    for char in (data  + ETX):
        crc = crcblah(crc, char)
    print "new crc is ", crc
    sleep(0.01)
    ser.write(DLE)
    ser.write(STX)
    ser.write(data)
    ser.write(DLE)
    ser.write(ETX)
    
    ser.write(chr(crc & 0xFF))
    ser.write(chr(crc >> 8))
    
    receivedData = ""
    while True:
        x = ser.read()
        if len(x) > 0:
            print "Recevied data in uploadblock: " + x + "=" + x.encode('hex')
            receivedData += x
            if len(receivedData) >= 2 and \
                    receivedData[-2] == DLE:
                print "received confirmation of block" 
    
        
def thirdHandshake():
    print "doing third handshake"
    ser.flushInput()
    sleep(0.01)
    receivedData = ""
    ser.write(ENQ)
    ser.flush()
    while True:
        ser.write(ENQ)
        ser.flush()
        x = ser.read()
        if len(x) > 0:
            receivedData += x
            if len(receivedData) >= 2 and \
                    receivedData[-2] == DLE and \
                    receivedData[-1] == '0':
                print "Recevied query response"
                break
    uploadblock("hello")        
    
    print "writing end of transmission"
    ser.write(EOT)
    
    while True:
        x = ser.read()
        if x == NAK:
            print "got a nack"
            
        if len(x) > 0:
            print "Recevied data in third handshake: " + x + "=" + x.encode('hex')
            receivedData += x
            
            if len(receivedData) >= 2 and \
                   receivedData[-2] == DLE:
                print "received response"
                break
    ser.write(EOT)
    ser.flush()
    return

    
def receiveData(data):
    if state == MachineState.init:
        handleInit(data)
    elif state == MachineState.master_handshake:
        handleMasterHandshake(data)
    elif state == MachineState.slave_handshake:
        handleSlaveHandshake(data)
        
def waitConnection():
    while True:
        x = ser.read()
        if len(x) > 0:
            print "Recevied data: " + x + "=" + x.encode('hex')
            for char in x:
                if char == ENQ:
                    print "Received ENQ for init"
                    #ser.write(ENQ)
                    #slaveHandshake()
                    #masterHandshake()
                    
                    ser.write(DLE)
                    masterHandshake()
                    slaveHandshake()
                    thirdHandshake()
                    while True:
                        x = ser.read()
                        if len(x) > 0:
                            print "Recevied data in last phase: " + x + "=" + x.encode('hex')                        

waitConnection()