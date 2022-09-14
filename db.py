import sqlite3
import threading

lock = threading.Lock()

# Подключаемся к файлу базы данных
con = sqlite3.connect("db.db", check_same_thread=False)
# Берём управление базой данных
cur = con.cursor()

# Создаём таблицу ботов, если не создана
cur.execute("create table if not exists ips (ip TEXT NOT NULL)")

def execute_and_commit(sql, parameters = ()):
    """Выполняем sql команду и сразу возвращаем результат"""
    try:
        lock.acquire(True)

        cur.execute(sql, parameters)
        con.commit()
    finally:
        lock.release()

def execute_and_fetchall(sql, parameters = ()):
    """Выполняем sql команду и сразу сохраняем её в файл"""
    try:
        lock.acquire(True)

        cur.execute(sql, parameters)
        ret = cur.fetchall()
    finally:
        lock.release()

    return ret

def get_ips():
    return execute_and_fetchall("select * from ips")

def ip_exist(name):
    ips = execute_and_fetchall("select * from ips")

    for i in ips:
        if i[0] == name:
            return True

    return False

def add_ip(ip):
    if not ip_exist(ip):
        execute_and_commit("INSERT or REPLACE into ips values (?)", (ip,))
        return True
    else:
        return False

def remove_ip(ip):
    if ip_exist(ip):
        execute_and_commit("delete from ips where ip like (?)", (ip,))
        return True
    else:
        return False