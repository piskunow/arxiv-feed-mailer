#!/usr/bin/env python

import pickle
import os.path
import base64

from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import sys

home_path = os.path.expanduser("~")
secrets_path = home_path + "/Dropbox/arxiv/"
sys.path.append(secrets_path)

from private_variables import my_mail

SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          ]
CLIENT_SECRET_FILE = secrets_path + '/client_secret.json'


def get_credentials():
    """Gets valid user credentials from storage.

    Returns:
        Credentials, the obtained credential.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(secrets_path, 'token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_path = os.path.join(secrets_path, 'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_service():
    credentials = get_credentials()
    service = build('gmail', 'v1', credentials=credentials)
    return service


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text, 'html')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_string().encode()).decode()
    return {'raw': raw}


def send_message(message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    service = get_service()
    user_id = 'me'
    try:
        message = (service.users().messages().send(
            userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:  # urllib2.HTTPError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    message = create_message(sender='',
                             to=my_mail,
                             subject='Test message succeeded',
                             message_text='Test message')

    send_message(message)
    print("You should have received a test message now.")
