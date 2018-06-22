# -*-coding:utf-8-*-
# 服务端
import socket
import threading


def client_thread_in(conn, nick):
    global data
    while True:
        try:
            temp = conn.recv(1024).decode(encoding)
            if not temp:
                conn.close()
                return
            notify_all(temp)
            print(data)

        except:
            notify_all(nick + ' 离开聊天室')
            print(data)
            return


def client_thread_out(conn, nick):
    global data
    while True:
        if con.acquire():
            con.wait()
            if data:
                try:
                    conn.send(data.encode(encoding))
                    con.release()
                except:
                    con.release()
                    return


def notify_all(ss):
    global data
    if con.acquire():
        data = ss
        con.notifyAll()
        con.release()


con = threading.Condition()
HOST = ""
PORT = 8964
data = ''
encoding = 'utf-8'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socke建立')
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)
print('开始监听端口')

while True:
    conn, addr = s.accept()
    print(addr[0] + ':' + str(addr[1]) + " 连入服务器")
    nick = conn.recv(1024).decode(encoding)
    notify_all('欢迎 ' + nick + ' 进入聊天室！')
    print(data)
    print('当前 ' + str(int((threading.activeCount() + 1) / 2)) + ' 人在线')
    conn.sendall(data.encode(encoding))
    threading.Thread(target=client_thread_in, args=(conn, nick)).start()
    threading.Thread(target=client_thread_out, args=(conn, nick)).start()
