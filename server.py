# -*-coding:utf-8-*-
# 服务端
import socket
import threading
import json
import time
import os
from collections import defaultdict
from base64 import b64encode, b64decode


def client_thread_in(conn, nick):
    global data, online_user
    while True:
        try:
            jmsg = conn.recv(1024).decode(encoding)
            if not jmsg:
                conn.close()
                return
            msg = json.loads(jmsg)
            if msg['MsgType'] == 'text':
                print('[' + msg['CreateTime'] + ']' + msg['FromUser'] + ':' + msg['Content'])
                if msg['Object'] == 'all':
                    notify_all(msg)
                elif msg['Object'] == 'personal':
                    data[msg['ToUser']].append(msg)
            elif msg['MsgType'] == 'image' or msg['MsgType'] == 'file':
                if msg['MsgID'] not in temp_file.keys():
                    temp_file[msg['MsgID']] = msg
                    data_file[msg['MsgID']] = []
                    threading.Thread(target=deal_file, args=(msg['MsgID'], msg['FileSize'])).start()
                else:
                    data_file[msg['MsgID']].append(msg)
        except:
            del online_user[nick]
            temp = {'Object': 'all', 'FromUser': 'system',
                    'CreateTime': time.strftime("%H:%M:%S", time.localtime()), 'MsgType': 'text',
                    'Content': nick + ' 离开聊天室', 'OnlineUser': list(online_user.keys())}
            print(temp['Content'])
            notify_all(temp)
            return


def client_thread_out(conn, nick):
    global data, online_user
    while True:
        if nick not in online_user.keys():
            return
        if len(data[nick]) > 0:
            msg = data[nick][0].copy()
            msg['OnlineUser'] = list(online_user.keys())
            if msg['MsgType'] == 'text':
                jmsg = json.dumps(msg) + '\n'
                try:
                    conn.send(jmsg.encode(encoding))
                    threadLock.acquire()
                    data[nick].pop(0)
                    threadLock.release()
                except:
                    return
            elif msg['MsgType'] == 'image' or msg['MsgType'] == 'file':
                jmsg = json.dumps(msg) + '\n'
                try:
                    conn.send(jmsg.encode(encoding))
                    threading.Thread(target=deal_file_out, args=(conn, msg['MsgID'], msg['MsgType'])).start()
                    threadLock.acquire()
                    data[nick].pop(0)
                    threadLock.release()
                except:
                    return


def notify_all(msg):
    global data
    for user in online_user.keys():
        temp = msg.copy()
        if user != msg['FromUser']:
            temp['ToUser'] = user
            data[user].append(temp)


def deal_file(f_id, f_size):
    global temp_file, data_file, data
    recv_size = 0
    filename = os.path.join('./temp/', str(f_id))
    fp = open(filename, 'wb')
    while not recv_size == f_size:
        if len(data_file[f_id]) > 0:
            temp = b64decode(data_file[f_id][0]['Content'])
            if f_size - recv_size > 512:
                recv_size += len(temp)
            else:
                recv_size = f_size
            fp.write(temp)
            data_file[f_id].pop(0)
    fp.close()
    if temp_file[f_id]['Object'] == 'all':
        notify_all(temp_file[f_id])
    elif temp_file[f_id]['Object'] == 'personal':
        data[temp_file[f_id]['ToUser']].append(temp_file[f_id])
    del temp_file[f_id]
    del data_file[f_id]
    return


def deal_file_out(conn, msg_id, msg_type):
    fp = open("./temp/" + str(msg_id), "rb")
    while True:
        data = b64encode(fp.read(512)).decode(encoding)
        if not data:
            print("发送完毕")
            break
        msg = {
            'MsgType': msg_type,  # 消息类型：image（图片）、file（文件）
            'MsgID': msg_id,  # 本次传输id，8位数字，需与首次发送id相同
            'Content': data  # 图片\文件内容，每次最大传输960
        }
        jmsg = json.dumps(msg)
        conn.send(jmsg.encode(encoding))
        time.sleep(0.05)
    fp.close()
    return


HOST = ""
PORT = 8964
data = defaultdict(list)
data_file = defaultdict(list)  # 待处理文件消息
temp_file = defaultdict(dict)  # 临时存储文件
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
    print(temp['Content'])
    notify_all(temp)
    print('当前 ' + str(int((threading.activeCount() + 1) / 2)) + ' 人在线')
    threading.Thread(target=client_thread_in, args=(conn, nick)).start()
    threading.Thread(target=client_thread_out, args=(conn, nick)).start()
