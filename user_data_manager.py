import pymysql


class UserDataManager:
    def __init__(self):
        self.db = pymysql.connect("localhost", "root", "19970821", "recipie")
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
        cmd = "SELECT * FROM userdata WHERE Username = '%s';" % (username)
        try:
            self.cursor.execute(cmd)
            results = self.cursor.fetchall()
            if len(results) == 0:
                print(username + "用户名不存在")
                return 1
            else:
                return results
        except:
            print(username + "用户名不存在")
            return 1

    def update_inf(self, username, nickname, sex):
        cmd1 = "update userdata set Nickname='%s' where Username='%s';" % (nickname,username)
        cmd2 = "update userdata set Sex='%s' where Username='%s';" % (sex, username)
        try:
            self.cursor.execute(cmd1)
            self.db.commit()
            self.cursor.execute(cmd2)
            self.db.commit()
            print(username + "修改个人资料成功")
            return True
        except Exception as e:
            self.db.rollback()
            print(e)
            print(username + "修改个人资料失败")
            return False

    def view_inf(self, username):
        cmd = "SELECT * FROM userdata WHERE Username = '%s';" % (username)
        try:
            self.cursor.execute(cmd)
            results = self.cursor.fetchall()
            print(username + "查看个人资料成功")
            return results
        except Exception as e:
            self.db.rollback()
            print(e)
            print(username + "查看个人资料失败")
            return False
