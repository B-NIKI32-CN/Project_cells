import socket
import select
import time


class SoftChannal:
    def __init__(self):
        self.code_format = "utf-8"
        self.connections_cnt = 0
        
        self.cooldown_recv = 0.1 # receive
        self.cooldown_send = 0.1
        self.cooldown_conn = 0.5 # connect

        self.last_recv = 0
        self.last_send = 0
        self.last_conn = 0
        self.send_buff: list[str] = []
        self.recv_buffs: list[str] = []
        
    def hard_send(self): pass
    def hard_recv(self) -> bool: return False
    def hard_conn(self) -> bool: return False

    def new_connect(self):
        self.connections_cnt += 1
        self.recv_buffs.append("")
    
    def close_connect(self, leave_socket_ind):
        self.connections_cnt -= 1
        self.recv_buffs.pop(leave_socket_ind)

    def add(self, json_string: str):
        self.send_buff.append(json_string)
    
    def soft_send(self):
        if len(self.send_buff) == 0:
            return
        
        cur_time = time.time()
        if cur_time < self.last_send + self.cooldown_send:
            return
        self.last_send = cur_time

        print("[log][Channal] send_buff", self.send_buff)
        self.hard_send()

    def soft_recv(self) -> list[str]:
        cur_time = time.time()
        if cur_time < self.last_recv + self.cooldown_recv:
            return []
        self.last_recv = cur_time
        
        recv_lists: list[str] = []

        if self.hard_recv():

            for conn_id in range(self.connections_cnt):

                splited_recv = self.recv_buffs[conn_id].split('\n')
                self.recv_buffs[conn_id] = splited_recv[-1]

                recv_lists += splited_recv[:-1]

            print("[log][Channal] recv_lists:", recv_lists)

        return recv_lists
    
    def soft_conn(self):
        cur_time = time.time()
        if cur_time < self.last_conn + self.cooldown_conn:
            return False
        self.last_conn = cur_time

        return self.hard_conn()



class SoftServer(SoftChannal):
    def __init__(self, server_addr=("127.0.0.1", 1234)):
        super().__init__()
     
        self.server_addr = server_addr

        # запуск
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.setblocking(False)  # Делаем сокет неблокирующим
        self.socket.bind(self.server_addr)
        self.socket.listen()

        print(f"[SERVER] Сервер запущен на {self.server_addr[0]}:{self.server_addr[1]}")

        self.clients_list = []
    
    def new_connect(self):
        client_socket, client_address = self.socket.accept()
        super().new_connect()
        self.clients_list.append(client_socket)
        print(f"[SERVER] Новое подключение с адреса {client_address}")
    
    def close_connect(self, leave_socket_ind):
        super().close_connect(leave_socket_ind)
        leave_socket = self.clients_list.pop(leave_socket_ind)
        print(f"[NETWORK] Пользователь {leave_socket.getpeername()} отключился.") # ВЕРОЯТНА ОШИБКА
        leave_socket.close()
        
    def hard_send(self):
        if len(self.send_buff) == 0:
            return

        for message in self.send_buff:
            formated_message = message + '\n'
            for client_socket in self.clients_list:
                client_socket.sendall(formated_message.encode(self.code_format))
        
        self.send_buff.clear()
    
    def hard_recv(self):
        if not self.clients_list: return False
        readable, _, _ = select.select(self.clients_list, [], [], 0)
        received = False

        for notified_socket in readable:
            # сообщение
            try:
                raw_data = notified_socket.recv(1024)
            except:
                raw_data = b''

            # выход клиента
            if not raw_data:
                leave_socket_ind = self.clients_list.index(notified_socket)
                self.close_connect(leave_socket_ind)
                continue

            message = raw_data.decode(self.code_format) # raw_data.decode(self.code_format).strip()
            client_ind = self.clients_list.index(notified_socket)
            self.recv_buffs[client_ind] += message
            received = True
        
        return received

    def hard_conn(self):
        readable, _, _ = select.select([self.socket], [], [], 0)
        if readable:
            self.new_connect()
            return True

        return False
        

class SoftClient(SoftChannal):
    def __init__(self, server_addr=("127.0.0.1", 1234)):
        super().__init__()

        self.server_addr = server_addr

        self.cooldown_conn_request = 1

        self.connecting = False
        self.last_conn_request = 0
        
        # запуск
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)  # Делаем сокет неблокирующим

    def reset_socket(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

    def new_connect(self): return super().new_connect()

    def close_connect(self, leave_socket_ind):
        self.socket.close()
        return super().close_connect(0)

    def conn_request(self):
        err = self.socket.connect_ex(self.server_addr)

        if err == 0:
            print("[CLIENT] Успешное подключение!")
            self.connecting = False
            self.new_connect()
            return True

        elif err in (115, 10035): # в процессе
            print(f"[CLIENT] Попытка соединения с {self.server_addr}...")
            self.connecting = True
            return False

        else:
            print(f"[ERROR] Ошибка: {err}")
            self.connecting = False
            self.reset_socket()
            return False

    def hard_send(self):
        if len(self.send_buff) == 0:
            return

        for message in self.send_buff:
            formated_message = message + '\n'
            self.socket.sendall(formated_message.encode(self.code_format))
        
        self.send_buff.clear()
    
    def hard_recv(self):
        readable, _, _ = select.select([self.socket], [], [], 0)
        received = False
    
        if readable:
        
            raw_data = self.socket.recv(1024)

            if not raw_data:
                print("[CLIENT] Соединение с сервером потеряно.")
                self.close_connect(0)
                exit()
            
            message = raw_data.decode(self.code_format)
            self.recv_buffs[0] += message
            received = True
        
        return received

    def hard_conn(self):
        if self.connections_cnt != 0:
            return True

        if not self.connecting:

            self.last_conn_request = time.time()
            return self.conn_request()

        else:

            _, writable, _ = select.select([], [self.socket], [], 0)
            
            if writable:
                err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err == 0:
                    print("[CLIENT] Успешное подключение!")
                    self.new_connect()
                    self.connecting = False
                    return True
                else:
                    print(f"[ERROR] Ошибка подключения: {err}")
                    self.connecting = False
                    self.reset_socket()
                    return False

            else:
                cur_time = time.time()
                if cur_time < self.last_conn_request + self.cooldown_conn_request:
                    return False
                self.last_conn_request = cur_time

                print(f"[CLIENT] Таймаут! ({self.cooldown_conn_request}c)")
                self.connecting = False
                self.reset_socket()
                self.conn_request()

        return False
