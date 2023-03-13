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
response_line = version+" 200 OK\r\n"
# 请求头
response_header = "CSeq:"+CSeq+"\r\n"
response_data = response_line + response_header

# 将数据返回客户端的Tcp服务器
def TcpServer():
    # 建立一个服务端
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 声明socket类型，同时生成链接对象
    server.bind((IP, PORT))  # 绑定要监听的端口
    server.listen(5)  # 开始监听 表示可以使用五个链接排队
    while True:  # conn就是客户端链接过来而在服务端为期生成的一个链接实例
        conn, addr = server.accept()  # 等待链接
        print("连接成功:", conn, addr)
        while True:
            try:
                data = conn.recv(1024)  # 接收数据
                print("接收到:", data)
                conn.sendall(response_data)  # 然后再发送数据
                print(response_data, "已发送")
                time.sleep(DELAY)
            except KeyboardInterrupt:
                conn.close()
                print("Tcp 服务器已关闭")
                exit(0)
 
 
if __name__ == "__main__":
    TcpServer()