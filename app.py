
import requests
from psycopg2 import sql
from requests import Timeout,ConnectionError
from flask import Flask, request, render_template, jsonify, send_file, url_for
from dbController import *
from abc import ABC, abstractmethod
from pydub import AudioSegment
import io

ERROR={'status':'error'}
OK={'status':'ok'}
class Model(ABC):
    @abstractmethod
    def save(self):
        pass
    @abstractmethod
    def getById(self):
        pass

    @abstractmethod
    def validate(self):
        pass
class User(Model):
    require=['name']
    def __init__(self,uid=None,uuid=None,name=None):
            self.uid,self.uuid,self.name=id,uuid,name
    def save(self):
        self.uuid = uuid.uuid4()
        while not self.validate():
            self.uuid = uuid.uuid4()
        else:
            self.id=execute(sql.SQL(f"insert into users(name,uuid) values ('{self.name}','{str(self.uuid)}') returning uid"), True)[0][0]
    def getById(self,uid):
        req=execute(f'select uid,uuid,name from users where uid={uid}')
        self.uid,self.uuid,self.name=req[0][0],req[0][1],req[0][2] if req else None
    def validate(self):
        return  execute(sql.SQL(f"select exists(select uuid from users where uuid ='{self.uuid}')"))
class Quest(Model):
    require = ['questions_num']
    def __init__(self, id=None,question=None,answer=None,created_at=None):
        self.id, self.question, self.answer, self.created_at  = id,question,answer,created_at
    def save(self):
        print(self.id)
        print(self.validate())
        if self.validate():
            self.id=execute(sql.SQL(f"insert into quests(id,question,answer,created_at) values ({self.id},'{self.question}','{self.answer}','{self.created_at}') returning id"),
                True)[0][0]
            return True
        else:
            return False
    def getById(self, id):
        req = execute(f'select id,question,answer,created_at from quests where id={id}')
        self.id, self.question, self.answer, self.created_at =req[0][0],req[0][1], req[0][2],req[0][3] if req else None
    def validate(self):
        return execute(f'select exists(select id from quests where id ={self.id})')

class Record(Model):
    require=['audio','uid','uuid']
    def __init__(self,id=None,uuid=None,audio=None,uid=None):
            self.id,self.uuid,self.audio,self.uid=id,uuid,audio,uid
    def save(self):
        self.uuid = uuid.uuid4()
        while not self.validate():
            self.uuid = uuid.uuid4()
        else:
             self.id=execute(f"insert into users(name,uuid,uid) values ({self.audio},{str(self.uuid)},{self.uid}) returning id",True)[0][0]
    def getById(self,id):
        req=execute(f'select id,uuid,audio,uid from records where id={id}')
        self.id,self.uuid,self.audio,self.uid=req[0][0],req[0][1],req[0][2] if req else None
    def validate(self):
        return not execute(f'select exists(select uuid from records where uuid ={self._uuid})')
class Response():
    def __init__(self,json):
        self.data=dict(json)
    def validate(self,require):
        return self.data if len(require) ==len([True for r in require if r in self.data]) else None

def convertToMp3(audio):


    with io.BytesIO(bytes(audio,'cp437')) as file:
        open('tmp.wav','a').write(file)
        # return AudioSegment.from_wav(file).export()


def getquest(count: int) -> dict:
    drops = count
    try:
        while drops != 0:
            print(drops)
            quests = [True for quest in requests.get(f'http://jservice.io/api/random?count={drops}').json() if
                      Quest(id=quest['id'],question=quest['question'], answer=quest['answer'], created_at=quest['created_at']).save()]
            print(quests)
            drops = count - len(quests)
    except ConnectionError:
        return {'status': 'error'}
    except Timeout:
        return {'status': 'error'}


app = Flask('__name__')

@app.route('/quest', methods=['POST'])
def quest():
    if data:=Response(request.json).validate(Quest.require):
        getquest(int(data[Quest.require[0]]))
        return jsonify(ERROR)
    else:
        return jsonify(ERROR)
@app.route('/create-user', methods=['POST'])
def user():
    if data:=Response(request.json).validate(User.require):
        User(name=data['name']).save()
        return jsonify(OK)
    else:
        return jsonify(ERROR)
@app.route('/add-audio', methods=['POST'])
def add_record():
    if data:=Response(request.json).validate(Record.require):
        user=User()
        user.getById(data['uid'])
        if user.uuid==data['uuid']:
            mp3=convertToMp3(data['audio'])
            record=Record(audio=mp3,uid=user.id)
            record.save()
            return url_for(f'records?id={record.id}&uid={record.uid}', _external=True)
        else:
            return jsonify(ERROR)
    else:
        return jsonify(ERROR)
@app.route('/records', methods=['get'])
def get_record():
    if data:=Response(request.json).validate(['id','uid']):
        record=Record()
        record.getById(data['id'])
        with io.BytesIO(record.audio) as file:
            send_file(file,download_name=f'{record.uid}')

if __name__ == '__main__':
    app.run(port=1122)


