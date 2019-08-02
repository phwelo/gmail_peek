#!/usr/bin/python3

from __future__ import print_function
from rofi import Rofi
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import datetime
r = Rofi()

rofi_width = 100
mail_items = 7

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def auth():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def epoch_to_datestring(epochms):
    epoch = float(epochms) / 1000.0
    return datetime.datetime.fromtimestamp(epoch).strftime('%m/%d %H:%M')

def message_list(msg_list, number: int, service):
    messages = []
    # need to put in some formatting to limit line length and assure space for date here
    for message in msg_list[:number]:
        mail = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        m_subject = ''
        m_from = ''
        for header in mail['payload']['headers']:
            if header['name'] == 'From':
                m_from = header['value']
            elif header['name'] == 'Subject':
                m_subject = header['value']
        created = epoch_to_datestring(mail['internalDate'])
        messages.append(m_from + ' - ' + m_subject + ' - ' + created)
    return messages

def main():
    """
    Lists the user's Gmail labels.
    """
    creds = auth()
    service = build('gmail', 'v1', credentials=creds)
    response = service.users().messages().list(userId='me').execute()
    msg_list = response['messages']
    trimmed_list = message_list(msg_list, 7, service)
    choice = r.select('Gmail:', trimmed_list)
    print(choice) # i think we're going to have to blindly correlate list index values to get back to the ID

if __name__ == '__main__':
    main()