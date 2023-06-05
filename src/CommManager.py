import serial
import serial.tools.list_ports
import time


class CommManager:
    ser = None
    run = False
    obstacleDetected = False

    def __init__(self):
        self.run = False
        self.obstacleDetected = False
        
    def start(self):
        port = self.findCOMPort()
        try:
            self.ser = serial.Serial(port, 115200)
            time.sleep(1)
        except:
            print('Failed to connect to port ' + port)
        finally:
            if self.ser is not None:
                print('Connected to port ' + port)
            else:
                print("Failed to connect to port: " + port)

    def __sendValues(self, speed, position):
        txMsg = "S:" + str(speed) + ",P:" + str(position) + "\n"
        self.ser.write(txMsg.encode(encoding='ascii'))

    def setRun(self, run):
        if (run != True or run != False):
            raise ValueError("Invalid run value, use True or False")
        else:
            self.run = run

    def findCOMPort(self):
        ports = serial.tools.list_ports.comports(include_links=False)
        for port in ports:
            print('Found port ' + port.device)
            ser = None
            try:
                ser = serial.Serial(port.device, 115200)
                time.sleep(3)
            except:
                print('Failed to open port ' + port.device)
                continue
            if ser is not None:
                chkMsg = "CHK\n"
                for i in range(3):
                    ser.write(chkMsg.encode("ascii"))
                    time.sleep(0.01)
                    reply = ser.read_until(b"\n")
                    if reply.decode("ascii") == "OK\n":
                        ser.close()
                        print('COM Port Selected: ' + port.device)
                        return port.device
                    
                    elif reply.decode("ascii") == "":
                        print("No Reply from Device at " + port.device)
                        continue
                    else:
                        continue
        print("Failed to Select Port: " + port.device)
        return None
    def eventLoop(self, speed, position):
        rxMsg = self.ser.read_until(b'\n').decode(encoding='ascii')
        if (rxMsg == "OD\n"):
                self.obstacleDetected = True

        elif (rxMsg == "OC\n"):
            self.obstacleDetected = False

        if (self.run):
            self.__sendValues(speed=speed, position=position)

        return self.obstacleDetected
