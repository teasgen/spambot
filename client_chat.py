from telethon import TelegramClient
import asyncio
import csv

# username = input('Input your username: ')
# api_id = int(input('Input your api_id: '))
from telethon import TelegramClient
import asyncio
import csv

# username = input('Input your username: ')
# api_id = int(input('Input your api_id: '))
# api_hash = input('Input your hash_id: ')
username = '@teasgen'
api_id = 18822033
api_hash = 'd6afbf228951e9bd4cd994530b56b119'

client = TelegramClient(username, api_id, api_hash)
client.start()

loop = asyncio.get_event_loop()
# cash
dialogs = loop.run_until_complete(client.get_dialogs())


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
        for user in participants:
            if not user.bot and user.id not in bad_ids:
                try:
                    writer.writerow([user.id] + [user.username] + [user.first_name] + [user.last_name] + [user.phone])
                except:
                    writer.writerow([user.id] + [user.username] + [user.phone])


def write_chat(file_name):
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile)
        users = [int(user[0]) for user in reader]
    with open('message.txt') as file_message:
        message = file_message.read()
        for user in users:
            loop.run_until_complete(client.send_message(user, message))
    for dialog in client.iter_dialogs():
        if dialog.entity.id in users:
            loop.run_until_complete(dialog.delete())


chat_name = input('Input chat name: ')
action = int(input('Do you want to remember chat members (1), or to write them (2), or to use both options (3): '))

file_name = chat_name + '.csv'

if action == 1:
    read_chat(file_name)
elif action == 2:
    write_chat(file_name)
else:
    read_chat(file_name)
    write_chat(file_name)




