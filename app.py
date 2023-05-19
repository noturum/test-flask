import requests
from requests import Timeout,ConnectionError
from flask import Flask, request, jsonify, send_file, url_for
from dbController import *
from abc import ABC, abstractmethod
from pydub import AudioSegment
import io
import base64
ERROR={'status':'error'}
OK={'status':'ok'}
class NotKey(Exception):
    def __init__(self,*args):
        if args:
            self.text=args[0]
        else:
            self.text=None
    def __str__(self):
        return f'Ошибка запроса ошибка ключей '
class EmptyKey(Exception):
    def __init__(self,*args):
        if args:
            self.text=args[0]
        else:
            self.text=None
    def __str__(self):
        return f'Ошибка запроса ошибка ключей '

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
            return True
    def getById(self,uid):
        req=execute(sql.SQL(f"select uid,uuid,name from users where uid={uid}"))
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
            self.id=execute(sql.SQL(f"insert into records(audio,uuid,uid) values ('{self.audio}','{str(self.uuid)}',{self.uid}) returning id"),True)[0][0]
            return True

    def getById(self,id):
        req=execute(f'select id,uuid,audio,uid from records where id={id}')

        self.id,self.uuid,self.audio,self.uid=req[0][0],req[0][1],req[0][2], req[0][3] if req else None
    def validate(self):
        return  execute(sql.SQL(f"select exists(select uuid from records where uuid ='{self.uuid}')"))
class Response():
    def __init__(self,json):
        self.data=dict(json)
    def validate(self,require):
        return self.data if len(require) ==len([True for r in require if r in self.data]) else None
def convertToMp3(path_inp,path_out):
    with open(path_inp,'rb') as inp:
        with open(path_out,'wb') as out:
            out.write(inp.read())
    #AudioSegment.from_wav(f"{path_inp}").export(f"{path_out}", format="mp3")
def fileToByte(path):
    with open(path, 'rb') as data:
        data=data.read()
        return data
def fileToStr(path: str) -> str:
    with open(path, 'rb') as data:
        return base64.b64encode(data.read()).decode('utf-8')
def strToByte(str):
    return base64.decodebytes(str.encode('utf-8'))

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
    try:
        if not (data:=Response(request.json).validate(User.require)):
            raise NotKey()
        else:
            if not (data['name'] ):
                raise EmptyKey()
            else:
                if User(name=data['name']).save():
                    return jsonify(OK)
                else:
                    return jsonify(ERROR)
    except NotKey:
        return jsonify(ERROR)

    except EmptyKey:
        return jsonify(ERROR)
    except Exception:
        return jsonify(ERROR)


@app.route('/add-audio', methods=['POST'])
def add_record():
    try:
        if not (data:=Response(request.json).validate(Record.require)):
            raise NotKey()
        else:
            if not (data['uid'] and data['uid'] and data['uid']):
                raise EmptyKey()
            else:
                user=User()
                user.getById(data['uid'])
                if user.uuid==data['uuid']:
                    path_wav=f'{data["uuid"]}_wav.wav'
                    path_mp3=f'{data["uuid"]}_mp3.mp3'
                    with open(path_wav,'wb') as wav:
                        wav.write(strToByte(data['audio']))
                    convertToMp3(path_wav,path_mp3)
                    print(str(fileToByte(path_mp3)))
                    record=Record(audio=fileToStr(path_mp3),uid=user.uid)
                    if record.save():
                        return f"{request.host_url}{url_for(f'get_record', id=record.id,uid=record.uid)}"
                    else:
                        return jsonify(ERROR)
    except NotKey:
        return jsonify(ERROR)
    except EmptyKey:
        return jsonify(ERROR)
    except Exception:
        return jsonify(ERROR)

@app.route('/records', methods=['get'])
def get_record():
    try:
        if not (data:=Response(request.json).validate(Record.require)):
            raise NotKey()
        else:
            if not (data['uid'] and data['uid'] and data['uid']):
                raise EmptyKey()
            else:

                record=Record()
                record.getById(data['id'])
                file=io.BytesIO(strToByte(str(record.audio,'utf8')))
                return send_file(file,download_name=f'{record.uid}.mp3',mimetype='audio/mp3',as_attachment=True)
    except NotKey:
        return jsonify(ERROR)
    except EmptyKey:
        return jsonify(ERROR)
    except Exception:
        return jsonify(ERROR)

if __name__ == '__main__':
    app.run(host='0.0.0.0')


