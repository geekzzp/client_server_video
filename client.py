import socket
import time
import threading
from threading import Event
 
IP = '127.0.0.1'
PORT = 6633
DELAY = 2  # 延迟时间
DELAY_1 = 1
DELAY_6 = 6

methods=[]
resdata=""
class RTSPMessage:
    def __init__(self):
        self.cseq = 0
    
    def get_next_cseq(self):
        self.cseq += 1
        return self.cseq

class HTTPRequest:
    def __init__(self, method, url, version, CSeq, headers={}, body=None):
        self.headers={}
        self.headers['CSeq'] = CSeq
        self.method = method
        self.url = url
        self.version = version
        for key,value in headers.items():
            self.headers[key]=value
        self.body = body or b''
    #__str__方法用于将HTTP请求或响应报文转换为字符串表示
    def __str__(self):
        lines = []
        lines.append(f'{self.method} {self.url} {self.version}')
        for key, value in self.headers.items():
            lines.append(f'{key}:{value}')
        lines.append('')
        lines.append(self.body.decode())
        return '\r\n'.join(lines)

class HTTPResponse:
    def __init__(self):
        self.headers = {}

    def analysis(self, text):
        lines = text.split('\r\n')
        words = lines[0].split(' ')
        self.version = words[0]
        self.status_code = words[1]
        self.status_text = words[2]
        for line in lines:
            if line=='':
                break
            if line!=lines[0]:
                linejs=line.split(':')
                self.headers[linejs[0]] = linejs[1]
        self.body=lines[len(lines)-1]

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.host = host
        self.port = port
        self.sock.connect((host, port))

    def sendall(self, data):
        self.sock.sendall(data)

    def recv(self, buffer_size=1024):
        data = self.sock.recv(buffer_size)
        return data

    def close(self):
        self.sock.close()

class HTTPreq:
    def req_play(response,client):
        start_time = time.time()
        while True:
            try:
                global resdata
                data = client.recv(1024).decode()  # 接收一个信息，并指定接收的大小 为1024字节
                print("接收到:", data)
                response = HTTPResponse()
                response.analysis(data)
                resdata = resdata + response.body
                if time.time() - start_time >= 6:
                    break
            except ConnectionAbortedError:
                print("服务器无法连接，请确保服务器端已打开。")
                exit(0)

def TcpClient():
    # 建立一个客户端
    client = Client()
    RTSP = RTSPMessage()
    try:
        client.connect(IP, PORT)  # 建立一个链接
    except ConnectionRefusedError:
        print("服务器无法连接，请确保服务器端已打开。")
        exit(0)
    while True:
        try:
            request_data = HTTPRequest('OPTIONS', 'diantp://127.0.0.1:6633', '0.5', RTSP.get_next_cseq())
            client.sendall(request_data.__str__().encode("utf-8"))
            print(request_data, "已发送")
            data = client.recv(1024).decode()  # 接收一个信息，并指定接收的大小 为1024字节
            print("接收到:", data)
            response = HTTPResponse()
            response.analysis(data)
            methods = response.headers['OPTIONS'].split(",")
            time.sleep(DELAY)

            request_data = HTTPRequest(methods[0], 'diantp://127.0.0.1:6633', '0.5', RTSP.get_next_cseq(), headers={'Transport':'TCP','client_port':PORT})
            client.sendall(request_data.__str__().encode("utf-8"))
            print(request_data, "已发送")
            data = client.recv(1024).decode()  # 接收一个信息，并指定接收的大小 为1024字节
            print("接收到:", data)
            response = HTTPResponse()
            response.analysis(data)
            session_id=response.headers['session_id']
            time.sleep(DELAY)
            
            request_data = HTTPRequest(methods[1], 'diantp://127.0.0.1:6633', '0.5', RTSP.get_next_cseq(), headers={'session_id':session_id,'Range':'ntp=xxx-xxx'})
            client.sendall(request_data.__str__().encode("utf-8"))
            print(request_data, "已发送")
            data = client.recv(1024).decode()  # 接收一个信息，并指定接收的大小 为1024字节
            print("接收到:", data)
            response = HTTPResponse()
            response.analysis(data)
            time.sleep(DELAY)
            HTTPreq.req_play(response,client)
            # time.sleep(DELAY_6)
            try:
                request_data = HTTPRequest(methods[2], 'diantp://127.0.0.1:6633', '0.5', RTSP.get_next_cseq(), headers={'session_id':session_id})
                client.sendall(request_data.__str__().encode("utf-8"))
                print(request_data, "已发送")
                data = client.recv(1024).decode()  # 接收一个信息，并指定接收的大小 为1024字节
                print("接收到:", data)
                response_4 = HTTPResponse()
                response_4.analysis(data)
                client.close()
                exit(0)
            except KeyboardInterrupt:
                client.close()
                print("Tcp 服务器已关闭")
                exit(0)
        except KeyboardInterrupt:
            client.close()
            print("Tcp 客户端已关闭")
            exit(0)
 
if __name__ == "__main__":
    TcpClient()