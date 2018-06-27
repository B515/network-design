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

    def view_user(self):
        cmd = "SELECT username FROM userdata;"
        try:
            self.cursor.execute(cmd)
            results = self.cursor.fetchall()
            return [u[0] for u in results]
        except:
            print("显示用户列表失败")
            return False

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

    def follow(self, user1, user2):
        if user2 not in self.view_user():
            print(user2 + "不存在")
            return False
        cmd = "SELECT * FROM friends WHERE user1 = '%s' and user2 = '%s';" % (user1, user2)
        try:
            self.cursor.execute(cmd)
            results = self.cursor.fetchall()
            if len(results) != 0:
                print(user1 + "已关注" + user2)
                return False
            cmd = "INSERT INTO friends(user1, user2) VALUES ('%s', '%s');" % (user1, user2)
            try:
                self.cursor.execute(cmd)
                self.db.commit()
                print(user1 + "成功关注" + user2)
                return True
            except Exception as e:
                self.db.rollback()
                print(e)
                print(user1 + "关注" + user2 + "失败")
                return False
        except Exception as e:
            self.db.rollback()
            print(e)
            print(user1 + "关注" + user2 + "失败")
            return False

    def unfollow(self, user1, user2):
        if user2 not in self.view_user():
            print(user2 + "不存在")
            return False
        cmd = "delete from friends where user1='%s' and user2='%s';" % (user1, user2)
        try:
            self.cursor.execute(cmd)
            self.db.commit()
            print(user1 + "成功取消关注" + user2)
            return True
        except Exception as e:
            self.db.rollback()
            print(e)
            print(user1 + "取消关注" + user2 + "失败")
            return False

    def following(self, user1):
        cmd = "SELECT user2 FROM friends WHERE user1 = '%s';" % user1
        try:
            self.cursor.execute(cmd)
            results = self.cursor.fetchall()
            print(user1 + "查看关注的人成功")
            return results
        except Exception as e:
            self.db.rollback()
            print(e)
            print(user1 + "查看关注的人失败")
            return False

    def follower(self, user1):
        cmd = "SELECT user1 FROM friends WHERE user2 = '%s';" % user1
        try:
            self.cursor.execute(cmd)
            results = self.cursor.fetchall()
            print(user1 + "查看关注者成功")
            return results
        except Exception as e:
            self.db.rollback()
            print(e)
            print(user1 + "查看关注者失败")
            return False
