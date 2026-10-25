# -*- coding: utf-8 -*-
"""
database.py  数据库模块：建表 + 增查数据
数据保存在同目录下的 lostfound.db（SQLite）
"""
import sqlite3
import datetime

DB_FILE = "lostfound.db"


def _get_conn():
    """获取数据库连接（每张表操作独立连接，用完即关，避免占用）"""
    return sqlite3.connect(DB_FILE)


# 初始化数据库，创建两张表：lost失物表，found拾物表
def init_db():
    conn = _get_conn()
    c = conn.cursor()
    # 失物登记表
    c.execute('''CREATE TABLE IF NOT EXISTS lost
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item_name TEXT,
                  description TEXT,
                  location TEXT,
                  lost_time TEXT,
                  contact TEXT,
                  create_time TEXT)''')
    # 拾物登记表
    c.execute('''CREATE TABLE IF NOT EXISTS found
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item_name TEXT,
                  description TEXT,
                  location TEXT,
                  found_time TEXT,
                  contact TEXT,
                  create_time TEXT)''')
    conn.commit()
    conn.close()


# 添加一条失物记录
def add_lost(item_name, description, location, lost_time, contact):
    conn = _get_conn()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO lost (item_name,description,location,lost_time,contact,create_time) VALUES (?,?,?,?,?,?)",
              (item_name, description, location, lost_time, contact, now))
    conn.commit()
    conn.close()


# 添加一条拾物记录
def add_found(item_name, description, location, found_time, contact):
    conn = _get_conn()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO found (item_name,description,location,found_time,contact,create_time) VALUES (?,?,?,?,?,?)",
              (item_name, description, location, found_time, contact, now))
    conn.commit()
    conn.close()


# 获取全部失物
def get_all_lost():
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM lost")
    res = c.fetchall()
    conn.close()
    return res


# 获取全部拾物
def get_all_found():
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM found")
    res = c.fetchall()
    conn.close()
    return res


# 按 id 撤回（删除）一条失物记录
def delete_lost(record_id):
    conn = _get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM lost WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


# 按 id 撤回（删除）一条拾物记录
def delete_found(record_id):
    conn = _get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM found WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


# 初始化，运行一次创建数据表
if __name__ == "__main__":
    init_db()
    print("数据库初始化完成！")
