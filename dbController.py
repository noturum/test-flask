import uuid

import psycopg2
from psycopg2 import sql
from psycopg2 import OperationalError, Error


def init():
    execute('''CREATE table IF NOT EXISTS quests (
    id int4 NOT NULL,
	question varchar NULL,
	answer varchar NULL,
	date_at date NULL);''', True)
    execute('''CREATE TABLE users (
	uid int not NULL GENERATED ALWAYS AS IDENTITY,
	"name" varchar NULL,
	uuid varchar NULL);''', True)
    execute('''CREATE TABLE records (
	id int not NULL GENERATED ALWAYS AS IDENTITY,
	uuid varchar NULL,
	audio text NULL,
	uid int NULL);''',True)

def connDB():
    try:
        conn = psycopg2.connect(dbname='postgres', user='postgres',
                                password='', host='localhost')
        cursor = conn.cursor()
        return conn, cursor
    except Error as e:
        print(f'Error db \n {e}')
        exit(0)


def execute(sql:str, commit: bool = False):
    try:
        conn, cursor = connDB()
        cursor.execute(sql)
        if commit == True:
            conn.commit()
        return cursor.fetchall()
    except OperationalError as s:
        print(f'operation error \n {s}')


def validate(tb:str,params:list):
    str=''
    for i,param in enumerate(params):
        str+=f'{list(param.keys())[0]}={list(param.values())[0]}'
        if i<len(params)-1:
            str+=' and '
    return execute(f'select exists(select * from {tb} where {str})')

def validateUuid(uuid):
    return execute(f'select exists(select uuid from users where uuid ={uuid})')


def insertQuest(quests: list):
    drops = 0
    for quest in quests:
        if validate('quests',[{'id':quest['id']}]):
            execute(
                f'insert into quests(id,question,answer,date_at) values ({quest["id"]},"{quest["question"]}","{quest["answer"]}","{quest["date_at"]}")',
                True)
        else:
            drops += 1
    return drops


def createUser(name):
    token=uuid.uuid4()
    while not validate('user',[{'uuid':token}]):
        token=uuid.uuid4()
    else:
        execute(f'insert into users(name,uuid) values ("{name}","{str(token)})"', True)
def saveAudio(uid:int,audio):
    token = uuid.uuid4()
    while not validate('records', [{'uuid': token}]):
        token = uuid.uuid4()
    else:
        return execute(f'insert into users(name,uuid,uid) values ("{audio}","{str(token)}",{uid}) returning id,uid', True)



# init()