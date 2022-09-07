from telethon import TelegramClient
import asyncio
import csv
import pandas as pd
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import time
import random

account = int(input('Input account number: '))

acc = pd.read_excel("accounts.xlsx")
username = acc.iloc[account - 1].username
api_id = acc.iloc[account - 1].api_id
api_hash = acc.iloc[account - 1].hash_id

client = TelegramClient(username, api_id, api_hash)
client.start()

loop = asyncio.get_event_loop()
# cash
dialogs = loop.run_until_complete(client.get_dialogs())
dialog_names = [dialogs[i].name for i in range(len(dialogs))]


def read_chat(chat_name):
    try:
        participants = []
        while_condition = True
        my_filter = ChannelParticipantsSearch('')
        offset = 0
        while while_condition:
            participants2 = loop.run_until_complete(client(
                GetParticipantsRequest(channel=chat_name, offset=offset, filter=my_filter, limit=200, hash=0)))

            participants.extend(participants2.users)
            offset += len(participants2.users)

            if len(participants2.users) < 1:
                while_condition = False
    except:
        participants = loop.run_until_complete(client.get_participants(chat_name))

    ids = []
    for user in participants:
        if not user.bot:
            ids.append(user)

    total = set()
    df = pd.read_excel("total_users.xlsx")
    for i in range(len(df)):
        total.add(int(df.iloc[i]['user id']))

    for user in ids:
        if user.id not in total:
            try:
                new = pd.DataFrame(
                    {"user id": [user.id], "username": [user.username], "user first name": [user.first_name],
                     "user last name": [user.last_name],
                     "user phone": [user.phone], "chat name": [chat_name], "status": [0]})
            except:
                new = pd.DataFrame(
                    {"user id": [user.id], "username": [0], "user first name": [0],
                     "user last name": [0],
                     "user phone": [0], "chat name": [0], "status": [0]})
            df = pd.concat([df, new])
    df.index = [0] * len(df)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.to_excel("total_users.xlsx")


def write_chat(delete=0):
    df = pd.read_excel("total_users.xlsx")
    users = []
    for i in range(len(df)):
        if len(users) == 20:
            break
        if df.iloc[i]['status'] == 0:
            users.append(int(df.iloc[i]['user id']))
            df.loc[i, 'status'] = 2
    photo = input('Send photo (yes or no): ')
    for i, user in enumerate(users):
        message_name = 'message' + str(random.randint(0, 9)) + '.txt'
        with open(message_name, encoding='windows-1251') as file_message:
            message = file_message.read()
            loop.run_until_complete(client.send_message(user, message))
            print(f'{i + 1} user\'s id = {user}')
            if photo == 'yes':
                loop.run_until_complete(client.send_file(user, 'photo.jpg'))
            if i != len(users) - 1:
                time.sleep(random.randint(30, 61))

    df['status'] = df['status'].replace({2: 1})
    df.index = [0] * len(df)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.to_excel("total_users.xlsx")

    if not delete:
        return
    for dialog in client.iter_dialogs():
        if dialog.entity.id in users:
            loop.run_until_complete(dialog.delete())


while True:
    action = int(input('Action:\n'
                       '    1: Remember chat members,\n'
                       '    2: Write to all, \n'
                       '    3: Write to all and delete chats,\n'
                       '    4: Exit\n'))

    while action not in [1, 2, 3, 4]:
        action = int(input('Incorrect number. Please, try again: '))

    if action == 1:
        chat_name = input('Input chat name: ')
        while chat_name not in dialog_names:
            chat_name = input('Incorrect chat name. Please, try again: ')
        read_chat(chat_name)
    elif action == 2:
        write_chat(0)
    elif action == 3:
        write_chat(1)
    else:
        break
    print()
loop.stop()
