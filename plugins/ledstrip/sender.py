from multiprocessing.connection import Client
import logging as LOGGER
import threading
import time
from collections import deque

# Neopixel gama correction. Taken from neopixel example
gamma8 = (
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255)

def calcColor(color : tuple, brightness : int):
    return (gamma8[color[0]] * brightness // 255, gamma8[color[1]] * brightness // 255, gamma8[color[2]] * brightness // 255)


class Sender:
    def __init__(self, address : tuple, authkey : str):
        self.run = False
        self.senderThread = None
        self.queue = deque(maxlen=1024)
        self.senderSleeper = 1 # wait 1s in sender thread
        self.cond = threading.Condition()
        self.lock = threading.Lock()
        self.conn = None
        self.address = address #(config.ADDRESS, config.PORT)     # family is deduced to be 'AF_INET'
        self.authkey = authkey
        
    def stop(self):
        self.run = False
        with self.cond: 
            self.cond.notify_all()

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()
    
    def start(self):
        self.run = True
        if not self.senderThread:
            self.senderThread = threading.Thread(target=self.sender, daemon=True,name="LEDSender")
            self.senderThread.start()
        else:
            if not self.senderThread.is_alive():
                self.senderThread = threading.Thread(target=self.sender, daemon=True,name="LEDSender")
                self.senderThread.start()

    
    def sendQueue(self):
        if not self.conn:
            return
        with self.cond:
            while self.run: 
                self.cond.wait()
                if not self.run: 
                    break
                if self.queue:
                    with self.lock:
                        qcopy = self.queue.copy()
                        self.queue.clear()
                    self.send(qcopy)


    def sender(self):
        while self.run: 
            try:
                LOGGER.debug(f"Connecting to {self.address}")
                self.conn = Client(address=self.address, authkey=self.authkey)
                self.sendQueue()
                self.conn.close()
            except ConnectionError as e:
                LOGGER.error(f"Unable to connect to {self.address} {e.strerror}")
                time.sleep(1) # wait 1s then try connect again
        
    def notifyThread(self):
        with self.cond: 
            self.cond.notify_all()

    def addQueue(self,pixels):
        if  self.run:
            with self.lock:
                if isinstance(pixels,list):
                    self.queue.extend(pixels)
                else:
                    self.queue.append(pixels)
            self.notifyThread()
    
    def send(self,pixels):
        buffer = bytes()
        for pixel in pixels:
            buffer += bytes((pixel[0],))
            buffer += bytes(pixel[1])
        self.conn.send_bytes(buffer)

