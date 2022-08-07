import sqlite3

TOKEN = '5502436426:AAEP1C5ZG5-CXfgdE6Kt0Xt2XkeWK1LYnA8'

try:
    #usersdb = sqlite3.connect('app.db')
    #cursor = usersdb.cursor()
    print("База данных успешно подключена к SQLite")
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)

STARTMSG = 'Здравствуйте!'
