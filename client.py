import requests
import base64

def fileTostr(path: str) -> str:
    with open(path, 'rb') as data:
        return base64.b64encode(data.read()).decode('utf-8')
#a=requests.post('http://127.0.0.1:1122/add-audio',json= {'uid':1,'uuid':'02def3ab-809a-4105-b2d5-d56994628488','audio':fileTostr('./sample.wav')}) #### отправка wav
#print(a.text)
# requests.post('http://127.0.0.1:1122/quest',json= {'questions_num':1}) ### запись вопросов в базу
requests.post('http://127.0.0.1:5000/create-user',json= {'name':'admin'}) #### создание пользователя




