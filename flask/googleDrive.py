from calendar import c
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def make_token():
    try :
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('./credentials/storage.json')
    creds = store.get()

    if not creds or creds.invalid:
        print("make new storage data file ")
        flow = client.flow_from_clientsecrets('./credentials/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store, flags) \
                if flags else tools.run(flow, store)
    return creds
    

def upload(upload_f, creds):
    DRIVE = build('drive', 'v3', http=creds.authorize(Http()))

    FILES = (
        (upload_f),
    )

    for file_title in FILES :
        file_name = file_title
        print(f'file_name : {file_name}')
        metadata = {'name': file_name,
                    'mimeType': None
                    }

        res = DRIVE.files().create(body=metadata, media_body=file_name).execute()
        if res:
            print(f'metadata : {metadata}')
            print(f'file_name : {file_name}')
            print('Uploaded "%s" (%s)' % (file_name, res['mimeType']))


if __name__ == '__main__':
    upload('all.jpg', make_token())