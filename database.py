import sqlite3

from datetime import datetime

def create_db(chat_id):
    try:
        con = sqlite3.connect('misc/files.db')
        cur = con.cursor()
        db = sqlite3.connect('misc/users.db')
        sql = db.cursor()

        sql.execute("""CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER,
                ruz_id INTEGER,
                status INTEGER,
                date_reg DATETIME,
                num_files INTEGER
            )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS files (
                        count INTEGER,
                        id INTEGER
                    )""")
        db.commit()
        con.commit()
        tg_id = int(chat_id)
        status = 1
        ruz_id = 0
        num_files = 0
        sq = sql.execute(f"SELECT * FROM users WHERE tg_id = ?", (int(chat_id),))
        chkbase = sq.fetchone()
        if sq.fetchone() is None:
            sql.execute(f"INSERT INTO users VALUES (?,?,?,?,?)", (tg_id, ruz_id, status, datetime.today(), num_files))
        if cur.fetchone() is None:
            cur.execute(f"INSERT INTO files VALUES (0,1)")
        db.commit()
        con.commit()
        return chkbase
    except Exception as e:
        print("db err: ", e)

def up_user_files(chat_id):
    try:
        db = sqlite3.connect('misc/users.db')
        sql = db.cursor()
        sql.execute("UPDATE users SET num_files=num_files+1 WHERE tg_id=?", (chat_id,))
        db.commit()
    except Exception as e:
        print("db err: ", e)


def up_all_files():
    try:
        con = sqlite3.connect('misc/files.db')
        cur = con.cursor()
        cur.execute("UPDATE files SET count=count+1 WHERE id=1")
        con.commit()
    except Exception as e:
        print("db err: ", e)


def get_file_count():
    try:
        con = sqlite3.connect('misc/files.db')
        cur = con.cursor()
        fls = cur.execute("SELECT count FROM files WHERE id = 1").fetchall()
        return fls[0][0]
    except Exception as e:
        print("db err: ", e)


def get_count_files():
    try:
        con = sqlite3.connect('misc/files.db')
        cur = con.cursor()
        result = cur.execute('SELECT count(*) FROM files WHERE status = 2').fetchall()
    except Exception as e:
        print("db err: ", e)


def up_ruz_id(st_id, chat_id):
    try:
        db = sqlite3.connect('misc/users.db')
        sql = db.cursor()
        sql.execute("UPDATE users SET ruz_id=? WHERE tg_id=?", (st_id, int(chat_id)))
        db.commit()
    except Exception as e:
        print("db err: ", e)


def get_ruz_database(user_id):
    try:
        with sqlite3.connect("misc/users.db") as con:
            cur = con.cursor()
            result = cur.execute('SELECT ruz_id FROM users WHERE tg_id = ?', (user_id,)).fetchall()
            return result[0][0]
    except Exception as e:
        print("db err: ", e)


def get_count_database():
    try:
        with sqlite3.connect("misc/users.db") as con:
            cur = con.cursor()
            result = cur.execute('SELECT count(*) FROM users').fetchall()
            return result[0][0]
    except Exception as e:
        print("db err: ", e)


def get_count_status():
    try:
        with sqlite3.connect("misc/users.db") as con:
            cur = con.cursor()
            result = cur.execute('SELECT count(*) FROM users WHERE status = 2').fetchall()
            return result[0][0]
    except Exception as e:
        print("db err: ", e)


def get_user_info(user_id):
    try:
        with sqlite3.connect("misc/users.db") as con:
            cur = con.cursor()
            result1 = cur.execute('SELECT date_reg FROM users WHERE tg_id = ?', (user_id,)).fetchall()
            result2 = cur.execute('SELECT num_files FROM users WHERE tg_id = ?', (user_id,)).fetchall()
            return str(result1[0][0])[:-10], str(result2[0][0])
    except Exception as e:
        print("db err: ", e)


def get_all_users():
    try:
        with sqlite3.connect("misc/users.db") as con:
            cur = con.cursor()
            result1 = cur.execute('SELECT * FROM users').fetchall()
            # print(result1)
            return result1
    except Exception as e:
        print("db err: ", e)
