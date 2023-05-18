import psycopg2
import requests
import base64

with open('sample.wav',encoding='cp437') as f:


    requests.post('http://127.0.0.1:1122/add-audio',json= {'uid':1,'uuid':'b5f3eeb8-b068-4ce2-b45d-426d568b9320','audio':base64.b64decode(f.read())})
