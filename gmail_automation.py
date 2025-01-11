import base64
import os
from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def was_downloaded_today():
    if os.path.exists('last_download.txt'):
        with open('last_download.txt', 'r') as f:
            last_download_date = f.read().strip()
            today = datetime.now().date().isoformat()
            return last_download_date == today
    return False

def update_last_download_date():
    today = datetime.now().date().isoformat()
    with open('last_download.txt', 'w') as f:
        f.write(today)


def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080, access_type='offline', prompt='consent')
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    print ("authentication succeeded")
    return build('gmail', 'v1', credentials=creds)



def download_attachments(service, user_id='me',
                         sender_email='diskalpai25@gmail.com',
                         subject='זמינות מוצרים') -> pd.DataFrame:
    today_date = (datetime.now()).strftime('%Y/%m/%d')
    query = f"from:{sender_email} after:{today_date} has:attachment subject:{subject}"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No emails found.')
        return

    all_dfs = []
    for msg in messages:
        msg_data = service.users().messages().get(userId=user_id, id=msg['id']).execute()
        part = msg_data['payload']
        if part['filename']:
            attachment_id = part['body'].get('attachmentId')
            if attachment_id:
                attachment = service.users().messages().attachments().get(
                    userId=user_id, messageId=msg['id'], id=attachment_id
                ).execute()

                all_dfs.append(_process_html_attachment_to_df(attachment['data']))
    return pd.concat(all_dfs).drop_duplicates()



def _process_html_attachment_to_df(file_data) -> pd.DataFrame:
    html_content = base64.urlsafe_b64decode(file_data).decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='rulesall')
    df =  pd.read_html(str(table))[0]
    filtered_df = df[~df.applymap(str).apply(lambda x: x.str.contains('סה"כ', na=False)).any(axis=1)]
    return filtered_df


