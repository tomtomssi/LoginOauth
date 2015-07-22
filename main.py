import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import subprocess
import re

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = '.credentials/client_secrets.json'
APPLICATION_NAME = 'Manestreet'


def get_credentials():
    home_dir = os.path.expanduser('.credentials')
    if not os.path.exists(home_dir):
        os.makedirs(home_dir)
    credential_path = os.path.join(home_dir, 'secret.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def single_message(service):
    accepted_messages = []
    for response in service.users().messages().list(userId="me", labelIds="Label_1").execute()['messages']:
        message = service.users().messages().get(userId="me", id=response['id']).execute()
        headers = message['payload']['headers']
        for item in headers:
            if 'Return-Path' in item['name']:
                if 'notice' in item['value']:
                    accepted_messages.extend(message['payload']['parts'])
    find_message_with_link(accepted_messages)


def find_message_with_link(base64_messages):
    for base64_encoded in base64_messages:
        if 'text/plain' in base64_encoded['mimeType']:
            res = subprocess.Popen("echo {0} | base64 --decode".format(base64_encoded['body']['data']),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   shell=True).communicate()
            asd = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            print(re.findall(asd, str(res)))


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    single_message(service)

if __name__ == '__main__':
    main()
