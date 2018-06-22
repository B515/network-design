# -*-coding:utf-8-*-
# 客户端（测试用）
import socket
import threading

outString = ''
inString = ''
nick = ''
encoding = 'utf-8'
# ip = "123.207.164.148"  # 正式服务器
ip = "123.206.13.211"  # 测试服务器
PORT = 8964


def deal_out(sock):
    global nick, outString
    while True:
        outString = input()
        outString = nick + ':' + outString
        sock.send(outString.encode(encoding))


def deal_in(sock):
    global inString
    while True:
        try:
            inString = sock.recv(1024).decode(encoding)
            if not inString:
                break
            if outString != inString:
                print(inString)
        except:
            break


nick = input('请输入昵称：')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, PORT))
print('成功连入服务器(' + ip + ')')
sock.send(nick.encode(encoding))

thin = threading.Thread(target=deal_in, args=(sock,))
thin.start()

thout = threading.Thread(target=deal_out, args=(sock,))
thout.start()
