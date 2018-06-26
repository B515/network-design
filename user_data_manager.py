import pymysql


class UserDataManager:
    def __init__(self):
        self.db = pymysql.connect("localhost", "root", "19970821", "recipie")
        print("连接数据库")
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()

    def register(self, username, password, nickname):
        cmd = "SELECT Username FROM userdata WHERE Username='%s';" % username
        try:
            self.cursor.execute(cmd)
            results = self.cursor.fetchall()
        except:
            print("Error: unable to fetch data")
            return 4
        if len(results) == 0:
            cmd = "INSERT INTO userdata(Username, Password, Nickname) VALUES ('%s', '%s', '%s');" % (username, password, nickname)
            try:
                self.cursor = self.db.cursor()
                self.cursor.execute(cmd)
                self.db.commit()
                print(username + "注册成功")
                return 2
            except Exception as e:
                self.db.rollback()
                print(e)
                print(username + "注册失败")
                return 4
        else:
            print("用户名重复")
            return 3

    def login(self, username):
        cmd = "SELECT * FROM userdata WHERE Username = '%s'" % (username)
        try:
            self.cursor.execute(cmd)
            results = self.cursor.fetchall()
            print(results)
            return results
        except:
            print(username + "用户名不存在")
            return 1
