import socket
import select
# import json
import time


class SoftChannal:
    def __init__(self):
        self.cooldown_recv = 0.1 # receive
        self.cooldown_send = 0.1

        self.last_recv = 0
        self.last_send = 0

        self.send_buff: list[str] | None = None
        self.recv_buff: str | None = None
        
    def hard_send(self):
        if self.send_buff is None:
            return False
        
        for message in self.send_buff:
            pass # код отправления acsii строки или как ты придумаешь (не ascii)


    def add(self, json_string: str):
        if self.send_buff is None:
            self.send_buff = []
        self.send_buff.append(json_string)
    
    def soft_send(self):
        cur_time = time.time()
        if cur_time < self.last_send + self.cooldown_send:
            return False
        self.last_send = cur_time

        if self.send_buff is None:
            return False
        if len(self.send_buff) == 0:
            return False
        
        return self.hard_send()

    def soft_recv(self):
        cur_time = time.time()
        if cur_time < self.last_recv + self.cooldown_recv:
            return False
        self.last_recv = cur_time

        
