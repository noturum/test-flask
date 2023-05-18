
import requests
from requests import Timeout,ConnectionError
from flask import Flask, request, render_template, jsonify, send_file, url_for
from dbController import *

from pydub import AudioSegment
import io


AudioSegment.fro
app = Flask('__name__')
def add_audio(data):
    if validate('user',[{'id':data['id']},{'uuid':data['uuid']}]):
        with io.BytesIO(data['audio']) as file:
            return saveAudio(int(data['id']), AudioSegment.from_wav(file).export())
def getquest(count:int) -> dict:
    drops=count
    try:
        while drops!=0:
            quests=[{'id':quest['question'],'question':quest['question'],'answer':quest['answer'],'date_at':quest['date_at']} for quest in dict(requests.get(f'http://jservice.io/api/random?count={drops}').json())]
            drops=insertQuest(quests)
    except ConnectionError:
        return {'status':'error'}
    except Timeout:
        return {'status': 'error'}

@app.route('/quest', methods=['POST'])
def quest():

    data=dict(request.json)
    getquest(data['questions_num']) if 'questions_num' in data else print('не правильный запрос')
    return jsonify({'status'})
@app.route('/create-user', methods=['POST'])
def user():
    data = dict(request.json)
    createUser(data['name']) if 'name' in data else print('не правильный запрос')
@app.route('/add-audio', methods=['POST'])
def user():
    data = dict(request.json)
    audio=None
    audio=add_audio(data)[0] if ['audio','id','uuid'] in data else print('не правильный запрос')
    if audio:
        id=audio[0]
        uid=audio[1]
        return url_for(f'records?id={id}&uid={uid}', _external=True)
    return 'не правильный запрос'

@app.route('/records', methods=['get'])
def user():
    data = dict(request.json)
    getAudio() if ['id','uid'] in data else print('не правильный запрос')
proxies = {
        "http": "http://marchenko_ns:Noturum2023@nov_proxy.mfnso.local:8080/",
        "https": "http://marchenko_ns:Noturum2023@nov_proxy.mfnso.local:8080/"
    }
if __name__ == '__main__':
    app.run(port=1122)


