# -*-coding:utf-8-*-
# 客户端（测试用）
import socket
import threading
import json
import time

outString = ''
inString = ''
nick = ''
encoding = 'utf-8'
# ip = "123.207.164.148"  # 正式服务器
ip = "123.206.13.211"  # 测试服务器
# ip = "127.0.0.1"
PORT = 8964


def deal_out(sock):
    global nick, outString
    while True:
        content = input()
        outString = content
        msg = {'Object': 'all', 'FromUser': 'nick', 'CreateTime': time.strftime("%H:%M:%S", time.localtime()),
               'MsgType': 'text', 'Content': content}
        jmsg = json.dumps(msg)
        sock.send(jmsg.encode(encoding))


def deal_in(sock):
    global inString
    while True:
        try:
            jmsg = sock.recv(1024).decode(encoding)
            if not jmsg:
                break
            msg = json.loads(jmsg)
            inString = msg['Content']
            if outString != inString:
                print('[' + msg['CreateTime'] + ']' + msg['FromUser'] + ':' + inString)
        except:
            break


nick = input('请输入昵称：')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, PORT))
print('成功连入服务器(' + ip + ')')
login = {'nick': nick}
jlogin = json.dumps(login)
sock.send(jlogin.encode(encoding))

thin = threading.Thread(target=deal_in, args=(sock,))
thin.start()

thout = threading.Thread(target=deal_out, args=(sock,))
thout.start()
