from calendar import c
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests
import pickle
from os.path import getsize


# def make_token():
#     try :
#         import argparse
#         flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#     except ImportError:
#         flags = None

#     SCOPES = 'https://www.googleapis.com/auth/drive'
#     store = file.Storage('./credentials/storage.json')
#     creds = store.get()

#     if not creds or creds.invalid:
#         print("make new storage data file ")
#         flow = client.flow_from_clientsecrets('./credentials/credentials.json', SCOPES)
#         creds = tools.run_flow(flow, store, flags) \
#                 if flags else tools.run(flow, store)
#     return creds

def make_token():
    params={
        'client_id' : "303423050557-q0j988opbao7sgqefm2roi7cam0rk1i6.apps.googleusercontent.com", # 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
        'redirect_uri' : "http://localhost:9999/authcode",
        'scope' : "https://www.googleapis.com/auth/drive.file",
        'response_type' : "code"
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth"
    response = requests.get(url, params = params)

def upload(access_token, file_path):
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
    Authorization = "Bearer " + access_token
   
    with open(file_path, 'rb') as file:
        data = file.read()
        headers = {"Content-Type" : "image/jpeg","Content-Length" : str(getsize(file_path)) , "Authorization" : Authorization}
        r = requests.post(url, headers = headers, data = data)
        print(r.text)

if __name__ == '__main__':
    upload("ya29.a0ARrdaM_pGJ03oqBLGiqUD-aZzwno0xSEu8ZHVEfyx2_4-kjI645J5kHBtigfAlkqhjQ6hs9rdqoLPfgusTK8cyWPPzWypSR4tDwr3DcFGYh9q131hF_MupX3uVOohW8UTF8alu9tQ9uMLLiwpyL0yF8BoQuZEw", "all.jpg")