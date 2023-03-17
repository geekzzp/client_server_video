import urllib.request

# 创建请求对象, 有 data 默认为 POST 请求, data 可以是 bytes、bytearray、字节流打开的file对象
req = urllib.request.Request("http://httpbin.org/post", data=b"name=Tom&age=25")

# 发出请求, 返回响应对象 http.client.HTTPResponse
resp = urllib.request.urlopen(req)

# 打印响应状态等信息
print(resp.status, resp.reason, resp.version)
# 打印响应头
print(resp.getheaders())
# 打印响应Body的内容
print(resp.read().decode("utf-8"))

# 关闭响应流
resp.close()



import select
import socket

# 定义服务器地址和端口
HOST = 'localhost'
PORT = 8888

# 创建一个 TCP 套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 设置套接字为非阻塞模式
server_socket.setblocking(False)

# 绑定服务器地址和端口
server_socket.bind((HOST, PORT))

# 开始监听
server_socket.listen()

# 定义存储客户端套接字的列表
client_sockets = []

# 定义一个字典存储每个套接字对应的未处理完的数据
unprocessed_data = {}

while True:
    # 使用 select 监听可读事件，阻塞时间为 1 秒
    read_sockets, _, _ = select.select([server_socket] + client_sockets, [], [], 1)

    # 处理所有可读事件
    for sock in read_sockets:
        # 如果是新的连接请求
        if sock is server_socket:
            client_socket, client_address = server_socket.accept()
            client_socket.setblocking(False)
            client_sockets.append(client_socket)
            print(f'Client {client_address} connected.')
        # 否则是客户端发送的数据
        else:
            try:
                data = sock.recv(1024)
                if data:
                    if sock not in unprocessed_data:
                        unprocessed_data[sock] = b''
                    unprocessed_data[sock] += data
                else:
                    # 客户端关闭连接
                    client_sockets.remove(sock)
                    del unprocessed_data[sock]
                    sock.close()
            except ConnectionResetError:
                # 客户端异常断开连接
                client_sockets.remove(sock)
                del unprocessed_data[sock]
                sock.close()

    # 处理所有未处理完的数据
    for sock, data in unprocessed_data.items():
        if len(data) > 0:
            # 在这里可以对收到的数据进行处理
            processed_data = data.upper()
            sock.send(processed_data)
            unprocessed_data[sock] = b''


import socket
import select

# 定义服务器地址和端口
HOST = 'localhost'
PORT = 8888

# 创建一个 TCP 套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 绑定服务器地址和端口
server_socket.bind((HOST, PORT))

# 开始监听
server_socket.listen()

# 创建 epoll 对象
epoll = select.epoll()

# 将服务器套接字加入 epoll 监听列表
epoll.register(server_socket.fileno(), select.EPOLLIN)

# 定义存储客户端套接字和地址的字典
client_sockets = {}
client_addresses = {}

while True:
    # 使用 epoll 等待事件发生，阻塞时间为 1 秒
    events = epoll.poll(1)

    # 处理所有事件
    for fileno, event in events:
        # 如果是服务器套接字发生的事件，表示有新的连接请求
        if fileno == server_socket.fileno():
            client_socket, client_address = server_socket.accept()
            print(f'Client {client_address} connected.')
            # 将客户端套接字加入 epoll 监听列表，并设置为非阻塞模式
            client_socket.setblocking(False)
            epoll.register(client_socket.fileno(), select.EPOLLIN)
            # 将客户端套接字和地址存储到字典中
            client_sockets[client_socket.fileno()] = client_socket
            client_addresses[client_socket.fileno()] = client_address
        # 否则是客户端套接字发生的事件，表示有数据可读或连接已关闭
        else:
            client_socket = client_sockets[fileno]
            client_address = client_addresses[fileno]
            if event & select.EPOLLIN:
                try:
                    data = client_socket.recv(1024)
                    if data:
                        # 在这里可以对收到的数据进行处理
                        processed_data = data.upper()
                        client_socket.send(processed_data)
                    else:
                        # 客户端关闭连接
                        epoll.unregister(fileno)
                        client_socket.close()
                        del client_sockets[fileno]
                        del client_addresses[fileno]
                        print(f'Client {client_address} closed.')
                except ConnectionResetError:
                    # 客户端异常断开连接
                    epoll.unregister(fileno)
                    client_socket.close()
                    del client_sockets[fileno]
                    del client_addresses[fileno]
                    print(f'Client {client_address} closed due to error.')
'''
在这个示例中，我们首先创建了一个 TCP 套接字并将其绑定到服务器地址和端口，然后开始监听连接请求。之后，我们创建了一个 epoll 对象，并将服务器套接字加入 epoll 监听列表中。在进入循环之后，我们使用 epoll 等待事件发生，包括新的连接请求和已连接的客户户端的数据可读或连接已关闭。如果是服务器套接字发生的事件，表示有新的连接请求，我们将新的客户端套接字加入 epoll 监听列表中，并将其存储到字典中。如果是客户端套接字发生的事件，表示有数据可读或连接已关闭，我们可以在这里对收到的数据进行处理，然后将处理后的数据发送回客户端。

需要注意的是，在高并发情况下，我们需要对客户端套接字进行非阻塞操作，这样才能够同时处理多个客户端的请求。此外，在客户端关闭连接时，需要将其从 epoll 监听列表中移除，并关闭套接字并从字典中删除。

总体来说，使用 epoll 可以很好地处理高并发情况下的网络编程，能够同时处理多个客户端的请求，提高服务器的性能。
'''