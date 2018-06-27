# -*-coding:utf-8-*-
# 客户端（测试用）
import socket
import threading
import json
import time
import os
from base64 import b64encode, b64decode
from collections import defaultdict
from random import randint

outString = ''
inString = ''
nick = ''
username = ''
data_file = defaultdict(list)  # 待处理文件消息
temp_file = defaultdict(dict)  # 临时存储文件
encoding = 'utf-8'
# ip = "123.207.164.148"  # 正式服务器
ip = "123.206.13.211"  # 测试服务器
# ip = "127.0.0.1"
PORT = 8964


def deal_out(sock):
    global username, outString
    while True:
        cmd = input("请输入类型{0：文字，1：图片， 2：文件, 3：查看个人资料, 4：修改个人资料, 5：关注，6：取关，7：关注了，8：关注者}：")
        if cmd == '0':
            content = input()
            outString = content
            msg = {'Object': 'all', 'FromUser': username, 'CreateTime': time.strftime("%H:%M:%S", time.localtime()),
                   'MsgType': 'text', 'Content': content}
            jmsg = json.dumps(msg) + '\n'
            sock.send(jmsg.encode(encoding))
        elif cmd == '1' or cmd == '2':
            filename = input("请输入文件名：")
            msg = {
                'Object': 'all',  # 发送对象类型：all（群体）， personal（个人）
                'FromUser': username,  # 发送方姓名；必填
                'CreateTime': time.strftime("%H:%M:%S", time.localtime()),  # 消息创建时间：形如23:59:59
                'MsgType': 'image' if cmd == '1' else 'file',  # 消息类型：image（图片）、file（文件）
                'FileName': filename,  # 图片\文件名
                'FileSize': os.stat(filename).st_size,  # 图片\文件大小
                'MsgID': randint(10000000, 99999999)  # 本次传输id，随机8位数字，用于标记本次传输
            }
            jmsg = json.dumps(msg) + '\n'
            sock.send(jmsg.encode(encoding))
            threading.Thread(target=deal_file, args=(sock, msg['MsgType'], msg['MsgID'], filename)).start()
        elif cmd == '3':
            msg = {'MsgType': 'system', 'Op': 'view_inf'}
            jmsg = json.dumps(msg) + '\n'
            sock.send(jmsg.encode(encoding))
        elif cmd == '4':
            msg = {'MsgType': 'system', 'Op': 'update_inf', 'Nickname': input("请输入新昵称："),
                   'Sex': int(input("请输入新性别：{0（女性）， 1（男性）}；"))}
            jmsg = json.dumps(msg) + '\n'
            sock.send(jmsg.encode(encoding))
        elif cmd == '5':
            msg = {'MsgType': 'system', 'Op': 'follow', 'User': input("请输入对方用户名：")}
            jmsg = json.dumps(msg) + '\n'
            sock.send(jmsg.encode(encoding))
        elif cmd == '6':
            msg = {'MsgType': 'system', 'Op': 'unfollow', 'User': input("请输入对方用户名：")}
            jmsg = json.dumps(msg) + '\n'
            sock.send(jmsg.encode(encoding))
        elif cmd == '7':
            msg = {'MsgType': 'system', 'Op': 'following'}
            jmsg = json.dumps(msg) + '\n'
            sock.send(jmsg.encode(encoding))
        elif cmd == '8':
            msg = {'MsgType': 'system', 'Op': 'follower'}
            jmsg = json.dumps(msg) + '\n'
            sock.send(jmsg.encode(encoding))


def deal_in(sock):
    global inString
    cf = sock.makefile('r', encoding=encoding)
    while True:
        try:
            jmsg = cf.readline()
            if not jmsg:
                break
            msg = json.loads(jmsg)
            if msg['MsgType'] == 'text':
                inString = msg['Content']
                if outString != inString:
                    print('[' + msg['CreateTime'] + ']' + msg['FromUser'] + ':' + inString)
            elif msg['MsgType'] == 'image' or msg['MsgType'] == 'file':
                if msg['MsgID'] not in temp_file.keys():
                    temp_file[msg['MsgID']] = msg
                    data_file[msg['MsgID']] = []
                    threading.Thread(target=deal_file_in, args=(msg,)).start()
                else:
                    data_file[msg['MsgID']].append(msg)
            elif msg['MsgType'] == 'system':
                print(msg)
        except:
            break


def deal_file(sock, msg_type, f_id, filename):
    print("开始发送" + filename)
    fp = open(filename, 'rb')
    while True:
        data = b64encode(fp.read(8192)).decode(encoding)
        if not data:
            print("发送" + filename + "完毕")
            break
        msg = {
            'MsgType': msg_type,  # 消息类型：image（图片）、file（文件）
            'MsgID': f_id,  # 本次传输id，8位数字，需与首次发送id相同
            'Content': data  # 图片\文件内容，每次最大传输960
        }
        jmsg = json.dumps(msg) + '\n'
        sock.send(jmsg.encode(encoding))
    fp.close()
    return


def deal_file_in(msg):
    global temp_file, data_file
    print("开始接收文件" + msg['FileName'])
    recv_size = 0
    filename = os.path.join('./recv/', msg['FileName'])
    fp = open(filename, 'wb')
    while not recv_size == msg['FileSize']:
        if len(data_file[msg['MsgID']]) > 0:
            temp = b64decode(data_file[msg['MsgID']][0]['Content'])
            if msg['FileSize'] - recv_size > 8192:
                recv_size += len(temp)
            else:
                recv_size = msg['FileSize']
            fp.write(temp)
            data_file[msg['MsgID']].pop(0)
    fp.close()
    del temp_file[msg['MsgID']]
    del data_file[msg['MsgID']]
    print("接收" + msg['FileName'] + "成功")
    return


while True:
    op = input("请输入操作{0：登录，1：注册}：")
    username = input("请输入用户名：")
    password = input("请输入密码：")
    data = {'Op': 'register' if op == '1' else 'login', 'Username': username, 'Password': password, }
    if op == '1':
        nick = input("请输入昵称：")
        data['Nickname'] = nick
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, PORT))
    print('成功连入服务器(' + ip + ')')
    jdata = json.dumps(data) + '\n'
    sock.send(jdata.encode(encoding))

    jresult = sock.recv(20).decode(encoding)
    result = json.loads(jresult)

    if result['Result'] == 0:
        print("登录成功")
        break
    elif result['Result'] == 2:
        print("注册成功")
        break
    elif result['Result'] == 1:
        print("用户名或密码错误")
        continue
    elif result['Result'] == 3:
        print("用户名重复")
        continue

thin = threading.Thread(target=deal_in, args=(sock,))
thin.start()

thout = threading.Thread(target=deal_out, args=(sock,))
thout.start()
