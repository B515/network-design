# -*-coding:utf-8-*-
# 服务端
import socket
import threading
import json
import time
import os
import hashlib
from user_data_manager import UserDataManager
from collections import defaultdict
from base64 import b64encode, b64decode


def client_thread_in(conn, user):
    global data, online_user
    cf = conn.makefile('r', encoding=encoding)
    while True:
        try:
            jmsg = cf.readline()
            if not jmsg:
                if user in online_user.keys():
                    del online_user[user]
                    temp = {'Object': 'all', 'FromUser': 'system',
                            'CreateTime': time.strftime("%H:%M:%S", time.localtime()), 'MsgType': 'text',
                            'Content': user + ' 离开聊天室', 'OnlineUser': list(online_user.keys())}
                    print(temp['Content'])
                    print('当前 ' + str(len(online_user.keys())) + ' 人在线')
                    notify_all(temp)
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
                    threading.Thread(target=deal_file, args=(msg['MsgID'], msg['FileSize'], user)).start()
                else:
                    data_file[msg['MsgID']].append(msg)
            elif msg['MsgType'] == 'system':
                if msg['Op'] == 'view_inf':
                    r = UserDataManager().view_inf(user)
                    if not r:
                        t = {'MsgType': 'system', 'Op': 'view_inf', 'Result': r}
                    else:
                        t = {'MsgType': 'system', 'Op': 'view_inf', 'Result': True, 'Nickname': r[0][2],
                             'Sex': r[0][3]}
                    data[user].insert(0, t)
                elif msg['Op'] == 'update_inf':
                    r = UserDataManager().update_inf(user, msg['Nickname'], msg['Sex'])
                    t = {'MsgType': 'system', 'Op': 'update_inf', 'Result': r}
                    data[user].insert(0, t)
                elif msg['Op'] == 'follow':
                    r = UserDataManager().follow(user, msg['User'])
                    msg['Result'] = r
                    data[user].insert(0, msg)
                elif msg['Op'] == 'unfollow':
                    r = UserDataManager().unfollow(user, msg['User'])
                    msg['Result'] = r
                    data[user].insert(0, msg)
                elif msg['Op'] == 'following':
                    r = UserDataManager().following(user)
                    if len(r) == 0:
                        msg['Result'] = True
                        msg['UserList'] = r
                    elif not r:
                        msg['Result'] = r
                    else:
                        msg['Result'] = True
                        msg['UserList'] = [u[0] for u in r]
                    data[user].insert(0, msg)
                elif msg['Op'] == 'follower':
                    r = UserDataManager().follower(user)
                    if len(r) == 0:
                        msg['Result'] = True
                        msg['UserList'] = r
                    elif not r:
                        msg['Result'] = r
                    else:
                        msg['Result'] = True
                        msg['UserList'] = [u[0] for u in r]
                    data[user].insert(0, msg)
                elif msg['Op'] == 'close':
                    del online_user[user]
                    temp = {'Object': 'all', 'FromUser': 'system',
                            'CreateTime': time.strftime("%H:%M:%S", time.localtime()), 'MsgType': 'text',
                            'Content': user + ' 离开聊天室', 'OnlineUser': list(online_user.keys())}
                    print(temp['Content'])
                    print('当前 ' + str(len(online_user.keys())) + ' 人在线')
                    notify_all(temp)
                    conn.close()
                    return
        except:
            del online_user[user]
            temp = {'Object': 'all', 'FromUser': 'system',
                    'CreateTime': time.strftime("%H:%M:%S", time.localtime()), 'MsgType': 'text',
                    'Content': user + ' 离开聊天室', 'OnlineUser': list(online_user.keys())}
            print(temp['Content'])
            print('当前 ' + str(len(online_user.keys())) + ' 人在线')
            notify_all(temp)
            return


def client_thread_out(conn, user):
    global data, online_user
    sending_file = []
    while True:
        if user not in online_user.keys():
            return
        if len(data[user]) > 0:
            msg = data[user][0].copy()
            msg['OnlineUser'] = list(online_user.keys())
            if msg['MsgType'] == 'text':
                jmsg = json.dumps(msg) + '\n'
                try:
                    conn.send(jmsg.encode(encoding))
                    data[user].pop(0)
                except:
                    return
            elif msg['MsgType'] == 'image' or msg['MsgType'] == 'file':
                jmsg = json.dumps(msg) + '\n'
                if msg['MsgID'] not in sending_file:
                    try:
                        sending_file.append(msg['MsgID'])
                        conn.send(jmsg.encode(encoding))
                        threading.Thread(target=deal_file_out, args=(msg['MsgID'], msg['MsgType'], user)).start()
                        data[user].pop(0)
                    except:
                        return
                elif msg['Status'] == 'Finished':
                    sending_file.remove(msg['MsgID'])
                    data[user].pop(0)
                else:
                    try:
                        conn.send(jmsg.encode(encoding))
                        data[user].pop(0)
                    except:
                        return
            elif msg['MsgType'] == 'system':
                jmsg = json.dumps(msg) + '\n'
                try:
                    conn.send(jmsg.encode(encoding))
                    data[user].pop(0)
                except:
                    return


def notify_all(msg):
    global data
    for user in online_user.keys():
        temp = msg.copy()
        if user != msg['FromUser']:
            temp['ToUser'] = user
            data[user].append(temp)


def deal_file(f_id, f_size, user):
    global temp_file, data_file, data
    print("创建" + str(f_id) + "文件接收线程")
    recv_size = 0
    filename = os.path.join('./temp/', str(f_id))
    fp = open(filename, 'wb')
    while not recv_size == f_size:
        if len(data_file[f_id]) > 0:
            try:
                temp = b64decode(data_file[f_id][0]['Content'])
            except:
                data_file[f_id].pop(0)
                continue
            if f_size - recv_size > 8192:
                recv_size += len(temp)
            else:
                recv_size = f_size
            fp.write(temp)
            data_file[f_id].pop(0)
        if user not in online_user.keys():
            fp.close()
            os.remove(filename)
            del temp_file[f_id]
            del data_file[f_id]
            print("接收" + str(f_id) + "文件失败")
            return
    fp.close()
    if temp_file[f_id]['Object'] == 'all':
        notify_all(temp_file[f_id])
    elif temp_file[f_id]['Object'] == 'personal':
        data[temp_file[f_id]['ToUser']].append(temp_file[f_id])
    del temp_file[f_id]
    del data_file[f_id]
    print("结束" + str(f_id) + "文件接收线程")
    return


def deal_file_out(msg_id, msg_type, user):
    global data
    print("创建" + str(msg_id) + "文件发送线程")
    fp = open("./temp/" + str(msg_id), "rb")
    while True:
        if user not in online_user.keys():
            fp.close()
            print("发送" + str(msg_id) + "文件失败")
            return
        text = b64encode(fp.read(8192)).decode(encoding)
        if not text:
            msg = {
                'MsgType': msg_type,  # 消息类型：image（图片）、file（文件）
                'MsgID': msg_id,  # 本次传输id，8位数字，需与首次发送id相同
                'Status': 'Finished'
            }
            data[user].append(msg)
            print("发送完毕")
            break
        msg = {
            'MsgType': msg_type,  # 消息类型：image（图片）、file（文件）
            'MsgID': msg_id,  # 本次传输id，8位数字，需与首次发送id相同
            'Content': text,  # 图片\文件内容，每次最大传输8192
            'Status': 'Unfinished'
        }
        data[user].append(msg)
    fp.close()
    print("结束" + str(msg_id) + "文件发送线程")
    return


HOST = ""
PORT = 8964
data = defaultdict(list)
data_file = defaultdict(list)  # 待处理文件消息
temp_file = defaultdict(dict)  # 临时存储文件
encoding = 'utf-8'
online_user = {}  # { nick:{ ip:'', port:''}}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socke建立')
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)
print('开始监听端口')

while True:
    conn, addr = s.accept()
    print(addr[0] + ':' + str(addr[1]) + " 连入服务器")
    cf = conn.makefile('r', encoding=encoding)
    try:
        jmsg = cf.readline()
        msg = json.loads(jmsg)
        password_sha1 = hashlib.sha1(msg['Password'].encode(encoding)).hexdigest()
        if msg['Op'] == 'register':
            result = UserDataManager().register(msg['Username'], password_sha1, msg['Nickname'])
            if result == 2:
                username = msg['Username']
                temp = {'Result': result}
            else:
                temp = {'Result': result}
                jtemp = json.dumps(temp) + '\n'
                conn.send(jtemp.encode(encoding))
                continue
            jtemp = json.dumps(temp) + '\n'
            conn.send(jtemp.encode(encoding))
        elif msg['Op'] == 'login':
            result = UserDataManager().login(msg['Username'])
            if result == 1:
                temp = {'Result': result}
                jtemp = json.dumps(temp) + '\n'
                conn.send(jtemp.encode(encoding))
                continue
            else:
                if password_sha1 == result[0][1]:
                    username = result[0][0]
                    temp = {'Result': 0}
                else:
                    print("密码错误")
                    temp = {'Result': 1}
                    jtemp = json.dumps(temp) + '\n'
                    conn.send(jtemp.encode(encoding))
                    continue
            jtemp = json.dumps(temp) + '\n'
            conn.send(jtemp.encode(encoding))
    except:
        continue
    online_user[username] = {}
    online_user[username]['ip'] = addr[0]
    online_user[username]['port'] = addr[1]
    temp = {'Object': 'all', 'FromUser': 'system', 'ToUser': list(online_user.keys()),
            'CreateTime': time.strftime("%H:%M:%S", time.localtime()), 'MsgType': 'text',
            'Content': '欢迎 ' + username + ' 进入聊天室！', 'OnlineUser': list(online_user.keys())}
    print(temp['Content'])
    notify_all(temp)
    print('当前 ' + str(len(online_user.keys())) + ' 人在线')
    threading.Thread(target=client_thread_in, args=(conn, username)).start()
    threading.Thread(target=client_thread_out, args=(conn, username)).start()
