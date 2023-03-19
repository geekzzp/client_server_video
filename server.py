import socket
import time
import uuid
# import threading
from threading import Thread
from threading import Event
from flask import Flask, jsonify
 
IP = '127.0.0.1'
PORT = 6633
DELAY = 2  # 延迟时间
DELAY_1 = 1

request_record={}
text="This is a string that is used to test extraction every 100 bytes."*100
class HTTPRequest:
    def __init__(self):
        self.headers = {}

    def analysis(self, text):
        lines = text.split('\r\n')
        words = lines[0].split(' ')
        self.method = words[0]
        self.url = words[1]
        self.version = words[2]
        for line in lines:
            if line=='':
                break
            if line!=lines[0]:
                linejs=line.split(':')
                self.headers[linejs[0]] = linejs[1]
        
class HTTPres:
    def res_options(request,server,conn):
        headers={'CSeq':request.headers['CSeq'], 'OPTIONS':'SETUP,PLAY,TEARDOWN'}
        response_data = HTTPResponse('0.5', '200', 'OK', headers)
        server.sendall(conn, response_data.__str__().encode("utf-8"))  # 然后再发送数据
        print(response_data, "已发送")

    def res_setup(request,server,conn):
        session_id = str(uuid.uuid4())
        headers={'CSeq':request.headers['CSeq'], 'session_id' : session_id}
        response_data = HTTPResponse('0.5', '200', 'OK', headers)
        server.sendall(conn, response_data.__str__().encode("utf-8"))  # 然后再发送数据

    def res_play(request,server,conn,event,start,end):
        for i in range(start, end, 100):
            if event.is_set():
                break
            body = text[i:i+100].encode("utf-8")
            headers={'CSeq':request.headers['CSeq'], 'session_id' : request.headers['session_id']}
            response_data = HTTPResponse('0.5', '200', 'OK', headers, body)
            server.sendall(conn, response_data.__str__().encode("utf-8"))  # 然后再发送数据
            print(response_data, "已发送")
            time.sleep(DELAY)

    def res_teardown(request,server,conn):
        headers={'CSeq':request.headers['CSeq'], 'session_id' : request.headers['session_id']}
        response_data = HTTPResponse('0.5', '200', 'OK', headers)
        server.sendall(conn, response_data.__str__().encode("utf-8"))  # 然后再发送数据
        print(response_data, "已发送")

class HTTPResponse:
    def __init__(self, version, status_code, status_text, headers=None, body=None):
        self.version = version
        self.status_code = status_code
        self.status_text = status_text
        self.headers = headers or {}
        self.body = body or b''
        self.CSeq = headers['CSeq']

    def __str__(self):
        lines = []
        lines.append(f'HTTP/1.1 {self.status_code} {self.status_text}')
        for key, value in self.headers.items():
            lines.append(f'{key}:{value}')
        lines.append('')
        lines.append(self.body.decode())
        return '\r\n'.join(lines)

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self, host, port):
        self.host = host
        self.port = port
        self.sock.bind((host, port))

    def listen(self, link):
        self.sock.listen(link)

    def accept(self):
        client_sock, client_addr = self.sock.accept()
        return client_sock, client_addr

    def recv(self, client_sock, buffer_size=1024):
        data = client_sock.recv(buffer_size)
        return data

    def sendall(self, client_sock, data):
        client_sock.sendall(data)

    def close(self, client_sock):
        client_sock.close()

def options():
    # 返回可用的方法列表
    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    resp = jsonify({'Allow': allowed_methods})
    resp.headers['Allow'] = ', '.join(allowed_methods)
    return resp

def handle_client(server, conn, addr):
    while True:
        try:
            data = server.recv(conn, 1024).decode()  # 接收数据
            if data=='':
                break
            print("接收到:", data)
            request = HTTPRequest()
            request.analysis(data)
            if request.method=='OPTIONS':
                HTTPres.res_options(request,server,conn)
            elif request.method == 'SETUP':
                HTTPres.res_setup(request,server,conn)
                data = server.recv(conn, 1024).decode()
                print("接收到:", data)
                request = HTTPRequest()
                request.analysis(data)
                if request.method == 'PLAY':
                    global request_record
                    if request.headers['session_id'] not in request_record:
                        request_record[request.headers['session_id']]=[]
                    request_record[request.headers['session_id']].append(data)
                    event = Event()
                    start = int(request.headers['Range'][4:7:])
                    end = int(request.headers['Range'][8:11:])
                    send_thread = Thread(target=HTTPres.res_play, args=(request,server,conn,event,start,end))
                    send_thread.start()
                    data = server.recv(conn, 1024).decode()
                    event.set()
                    print("接收到:", data)
                    request_4 = HTTPRequest()
                    request_4.analysis(data)
                    if request_4.method == 'TEARDOWN':
                        HTTPres.res_teardown(request_4,server,conn)
                        for i in request_record[request_4.headers['session_id']]:
                            print(i)
        except KeyboardInterrupt:
            server.close(conn)
            print("Tcp 服务器已关闭")
            exit(0)
    server.close(conn)

# 将数据返回客户端的Tcp服务器
def TcpServer():
    # 建立一个服务端
    server = Server()
    server.bind(IP, PORT)  # 绑定要监听的端口
    server.listen(5)  # 开始监听 表示可以使python用五个链接排队
    while True:  # conn就是客户端链接过来而在服务端为期生成的一个链接实例
        conn, addr = server.accept()  # 等待链接
        print("连接成功:", conn, addr)
        t = Thread(target=handle_client, args=(server, conn, addr))
        t.start()

 
if __name__ == "__main__":
    TcpServer()