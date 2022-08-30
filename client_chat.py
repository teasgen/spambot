from telethon import TelegramClient
import asyncio
import csv
import pandas as pd
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import time

account = int(input('Input account number: '))

acc = pd.read_csv("accounts.csv")
username = acc.iloc[account - 1].username
api_id = acc.iloc[account - 1].api_id
api_hash = acc.iloc[account - 1].hash_id

client = TelegramClient(username, api_id, api_hash)
client.start()

loop = asyncio.get_event_loop()
# cash
dialogs = loop.run_until_complete(client.get_dialogs())
dialog_names = [dialogs[i].name for i in range(len(dialogs))]
enc = 'utf-16-be'


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
    with open('total_users.csv', 'r', encoding=enc) as csv_total:
        reader = csv.reader(csv_total)
        for i, user in enumerate(reader):
            if i:
                total.add(int(user[0]))

    with open('total_users.csv', 'a', newline='', encoding=enc) as csv_total:
        writer = csv.writer(csv_total)
        for user in ids:
            if user.id not in total:
                try:
                    writer.writerow([user.id] + [user.username] + [user.first_name] + [user.last_name] + [user.phone] +
                                    [chat_name] + [0])
                except:
                    writer.writerow([user.id] + [0] + [0] + [0] + [0] +
                                    [0] + [0])


def write_chat(delete=0):
    with open('total_users.csv', 'r', encoding=enc) as csvfile:
        reader = csv.reader(csvfile)
        users = []
        for i, user in enumerate(reader):
            if i and user[6] == '0':
                users.append(int(user[0]))
    photo = input('Send photo (yes or no): ')
    with open('message.txt', encoding=enc) as file_message:
        message = file_message.read()
        for i, user in enumerate(users):
            loop.run_until_complete(client.send_message(user, message))
            if photo == 'yes':
                loop.run_until_complete(client.send_file(user, 'photo.jpg'))
            if i != len(users) - 1:
                time.sleep(181)

    df = pd.read_csv("total_users.csv", encoding=enc)
    df['status'] = df['status'].replace({0: 1})
    df.to_csv("total_users.csv", index=False, encoding=enc)

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