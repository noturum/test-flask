import uuid

import psycopg2
from psycopg2 import sql
from psycopg2 import OperationalError, Error
from psycopg2.errors import DuplicateTable


def init():
    execute('''CREATE table IF NOT EXISTS quests (
    id int4 NOT NULL,
	question varchar NULL,
	answer varchar NULL,
	created_at date NULL);''', True,False)
    execute('''CREATE TABLE users (
	uid int not NULL GENERATED ALWAYS AS IDENTITY,
	"name" varchar NULL,
	uuid varchar NULL);''', True,False)
    execute('''CREATE TABLE records (
	id int not NULL GENERATED ALWAYS AS IDENTITY,
	uuid varchar NULL,
	audio text NULL,
	uid int NULL);''',True,False)

def connDB():
    try:
        conn = psycopg2.connect(dbname='postgres', user='postgres',
                                password='admin', host='localhost')
        cursor = conn.cursor()
        return conn, cursor
    except Error as e:
        print(f'Error db \n {e}')
        exit(0)


def execute(sql:str, commit: bool = False,fetch=True):
    try:
        conn, cursor = connDB()
        cursor.execute(sql)
        if commit == True:
            conn.commit()
        if  fetch:
            return cursor.fetchall()
    except OperationalError as s:
        print(f'operation error \n {s}')
    except DuplicateTable:
        pass




init()