import socket
import time
 
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
request_line = method+" "+url+" "+version+"\r\n"
# 请求头
request_header = "CSeq:"+CSeq+"\r\n"
request_data = request_line + request_header
 
def TcpClient():
    # 建立一个客户端
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 声明socket类型，同时生成链接对象
    try:
        client.connect((IP, PORT))  # 建立一个链接
    except ConnectionRefusedError:
        print("服务器无法连接，请确保服务器端已打开。")
        exit(0)
    while True:
        try:
            client.sendall(request_data.encode("utf-8"))
            print(request_data, "已发送")
            data = client.recv(1024)  # 接收一个信息，并指定接收的大小 为1024字节
            print("接收到:", data)
            time.sleep(DELAY)
        except ConnectionAbortedError:
            print("服务器无法连接，请确保服务器端已打开。")
            exit(0)
        except KeyboardInterrupt:
            client.close()
            print("Tcp 客户端已关闭")
            exit(0)
 
 
if __name__ == "__main__":
    TcpClient()