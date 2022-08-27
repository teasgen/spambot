from telethon import TelegramClient
import asyncio
import csv
import pandas as pd

username = input('Input your username: ')
api_id = int(input('Input your api_id: '))
api_hash = input('Input your hash_id: ')

client = TelegramClient(username, api_id, api_hash)
client.start()

loop = asyncio.get_event_loop()
# cash
dialogs = loop.run_until_complete(client.get_dialogs())
dialog_names = [dialogs[i].name for i in range(len(dialogs))]


def read_chat(chat_name):
    participants = loop.run_until_complete(client.get_participants(chat_name))
    ids = []
    for user in participants:
        if not user.bot:
            ids.append(user)

    total = set()
    with open('total_users.csv', 'r') as csv_total:
        reader = csv.reader(csv_total)
        for i, user in enumerate(reader):
            if i:
                total.add(int(user[0]))

    with open('total_users.csv', 'a', newline='') as csv_total:
        writer = csv.writer(csv_total)
        for user in ids:
            if user.id not in total:
                writer.writerow([user.id] + [user.username] + [user.first_name] + [user.last_name] + [user.phone] + [0])


def write_chat(delete=0):
    with open('total_users.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        users = []
        for i, user in enumerate(reader):
            if i and user[5] == '0':
                users.append(int(user[0]))

    with open('message.txt') as file_message:
        message = file_message.read()
        for user in users:
            loop.run_until_complete(client.send_message(user, message))

    df = pd.read_csv("total_users.csv")
    df['status'] = df['status'].replace({0: 1})
    df.to_csv("total_users.csv", index=False)

    if not delete:
        return
    for dialog in client.iter_dialogs():
        if dialog.entity.id in users:
            loop.run_until_complete(dialog.delete())


action = int(input('Action:\n'
                   '    1: Remember chat members,\n'
                   '    2: Write to all, \n'
                   '    3: Write to all and delete chats,\n'))

while action not in [1, 2, 3]:
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

loop.stop()
