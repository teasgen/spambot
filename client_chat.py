from telethon import TelegramClient
import asyncio
import csv
import time

username = input('Input your username: ')
api_id = int(input('Input your api_id: '))
api_hash = input('Input your hash_id: ')

client = TelegramClient(username, api_id, api_hash)
client.start()

loop = asyncio.get_event_loop()
# cash
dialogs = loop.run_until_complete(client.get_dialogs())
dialog_names = [dialogs[i].name for i in range (len(dialogs))]


def read_chat(file_name):
    participants = loop.run_until_complete(client.get_participants(chat_name))
    ids = []
    for user in participants:
        if not user.bot:
            ids.append(user.id)

    total = set()
    with open('total_users.csv', 'r') as csv_total:
        reader = csv.reader(csv_total)
        for user in reader:
            total.add(int(user[0]))

    bad_ids = set()
    with open('total_users.csv', 'a', newline='') as csv_total:
        writer = csv.writer(csv_total)
        for user_id in ids:
            if user_id not in total:
                writer.writerow([user_id])
            else:
                bad_ids.add(user_id)

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user id'] + ['username'] + ['user first name'] + ['user last name'] + ['user phone'])
        for user in participants:
            if not user.bot and user.id not in bad_ids:
                try:
                    writer.writerow([user.id] + [user.username] + [user.first_name] + [user.last_name] + [user.phone])
                except:
                    writer.writerow([user.id] + [user.username] + [user.phone])


def write_chat(file_name, delete=0):
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile)
        # users = [int(user[0]) for user in reader]
        users = []
        for i, user in enumerate(reader):
            if i:
                users.append(int(user[0]))

    with open('message.txt') as file_message:
        message = file_message.read()
        for user in users:
            loop.run_until_complete(client.send_message(user, message))
    if not delete:
        return
    for dialog in client.iter_dialogs():
        if dialog.entity.id in users:
            loop.run_until_complete(dialog.delete())


chat_name = input('Input chat name: ')
while chat_name not in dialog_names:
    chat_name = input('Incorrect chat name. Please, try again: ')
action = int(input('Action:\n'
                   '    1: Remember chat members,\n'
                   '    2: Write them, \n'
                   '    3: Write them and delete chats,\n'
                   '    4: Remember and write\n'
                   '    5: Remember, write and delete\n'))

while action not in [1, 2, 3, 4, 5]:
    action = int(input('Incorrect number. Please, try again: '))

file_name = chat_name + '.csv'

if action == 1:
    read_chat(file_name)
elif action == 2:
    write_chat(file_name, 0)
elif action == 3:
    write_chat(file_name, 1)
elif action == 4:
    read_chat(file_name)
    write_chat(file_name, 0)
elif action == 5:
    read_chat(file_name)
    write_chat(file_name, 1)
