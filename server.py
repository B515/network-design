# -*-coding:utf-8-*-
# 服务端
import socket
import threading
import json
import time
from collections import defaultdict


def client_thread_in(conn, nick):
    global data, online_user
    while True:
        try:
            jmsg = conn.recv(1024).decode(encoding)
            if not jmsg:
                conn.close()
                return
            msg = json.loads(jmsg)
            if msg['Object'] == 'all':
                notify_all(msg)
        except:
            del online_user[nick]
            temp = {'Object': 'all', 'FromUser': 'system',
                    'CreateTime': time.strftime("%H:%M:%S", time.localtime()), 'MsgType': 'text',
                    'Content': nick + ' 离开聊天室', 'OnlineUser': list(online_user.keys())}
            notify_all(temp)
            return


def client_thread_out(conn, nick):
    global data, online_user
    while True:
        if nick not in online_user.keys():
            return
        if len(data[nick]) > 0 and data[nick][0]['ToUser'] == nick:
            msg = data[nick][0].copy()
            msg['OnlineUser'] = list(online_user.keys())
            jmsg = json.dumps(msg) + '\n'
            try:
                conn.send(jmsg.encode(encoding))
                threadLock.acquire()
                data[nick].pop(0)
                threadLock.release()
            except:
                return


def notify_all(msg):
    for user in online_user.keys():
        temp = msg.copy()
        if user != msg['FromUser']:
            temp['ToUser'] = user
            data[user].append(temp)


HOST = ""
PORT = 8964
data = defaultdict(list)
encoding = 'utf-8'
online_user = {}  # { nick:{ ip:'', port:''}}

threadLock = threading.Lock()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socke建立')
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)
print('开始监听端口')

while True:
    conn, addr = s.accept()
    print(addr[0] + ':' + str(addr[1]) + " 连入服务器")
    try:
        jnick = conn.recv(1024).decode(encoding)
        nick = json.loads(jnick)['nick']
    except:
        continue
    online_user[nick] = {}
    online_user[nick]['ip'] = addr[0]
    online_user[nick]['port'] = addr[1]
    temp = {'Object': 'all', 'FromUser': 'system', 'ToUser': list(online_user.keys()),
            'CreateTime': time.strftime("%H:%M:%S", time.localtime()), 'MsgType': 'text',
            'Content': '欢迎 ' + nick + ' 进入聊天室！', 'OnlineUser': list(online_user.keys())}
    notify_all(temp)
    print('当前 ' + str(int((threading.activeCount() + 1) / 2)) + ' 人在线')
    threading.Thread(target=client_thread_in, args=(conn, nick)).start()
    threading.Thread(target=client_thread_out, args=(conn, nick)).start()
