import socket
import time
import http.client
from flask import Flask, jsonify
 
IP = '127.0.0.1'
PORT = 6633
DELAY = 2  # 延迟时间

method='GET'
url='diantp://127.0.0.1:6633'
version='0.5'
CSeq='1'
client_port=PORT
Session_id='1'
ntp='0-'

# 请求行
response_line = version+" 200 OK\r\n"
# 请求头
response_header = "CSeq:"+CSeq+"\r\n"
response_data = response_line + response_header


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
    def res(self):
        if self.method=='OPTIONS':
            headers={'CSeq':self.headers['CSeq'],'OPTIONS':'SETUP,PLAY,TEARDOWN'}
            return headers
        elif self.method == 'SETUP':
            headers={'CSeq':self.headers['CSeq'],'Transport':'TCP','client_port':PORT}
            return headers
        elif self.method == 'PLAY':
            headers={'CSeq':self.headers['CSeq'],'Session_id':'xxx','Range':'ntp=xxx-xxx'}
            return headers
        elif self.method == 'TEARDOWN':
            headers={'CSeq':self.headers['CSeq'],'Session_id':'xxx'}
            return headers

class HTTPResponse:
    def __init__(self, version, status_code, status_text, headers=None, body=None):
        self.version = version
        self.status_code = status_code
        self.status_text = status_text
        self.headers = headers or {}
        self.body = body or b''
        self.CSeq = CSeq

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

    def close(self):
        self.sock.close()

def options():
    # 返回可用的方法列表
    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    resp = jsonify({'Allow': allowed_methods})
    resp.headers['Allow'] = ', '.join(allowed_methods)
    return resp

# 将数据返回客户端的Tcp服务器
def TcpServer():
    # 建立一个服务端
    server = Server()
    server.bind(IP, PORT)  # 绑定要监听的端口
    server.listen(5)  # 开始监听 表示可以使python用五个链接排队
    while True:  # conn就是客户端链接过来而在服务端为期生成的一个链接实例
        conn, addr = server.accept()  # 等待链接
        print("连接成功:", conn, addr)
        while True:
            try:
                data = server.recv(conn, 1024).decode()  # 接收数据
                print("接收到:", data)
                request = HTTPRequest()
                request.analysis(data)
                headers=request.res()
                response_data = HTTPResponse('0.5', '200', 'OK', headers, body=b'<html><body>Hello, world!</body></html>')
                server.sendall(conn, response_data.__str__().encode("utf-8"))  # 然后再发送数据
                print(response_data, "已发送")
                time.sleep(DELAY)
            except KeyboardInterrupt:
                server.close()
                print("Tcp 服务器已关闭")
                exit(0)
 
 
if __name__ == "__main__":
    TcpServer()