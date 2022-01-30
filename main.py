import time
import requests.exceptions
import vk_api
import sqlite3
from vk_api.exceptions import ApiHttpError, ApiError
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from datetime import datetime
from config import token_bot


vk_session = vk_api.VkApi(token=token_bot)
longpoll = VkBotLongPoll(vk_session, 209322786)
print('бот запущен')


def sender(id, text):
    try:
        vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})
    except ApiHttpError:
        sender(id, 'не хотю')
    except ApiError:
        sender(id, 'слишком длинный ответ')


def admin(id, text):
    t = text.split()
    t1 = t.copy()
    f = True
    for j in t:
        if j[0] == '%' and j[-1] == '%' and len(j) != 1:
            t1.remove(j)
        elif j[0] == '%' and f:
            t1.remove(j)
            f = False
        elif j[-1] == '%' and f:
            t1.remove(j)
            f = False
        elif j[-1] == '%' and not f:
            t1.remove(j)
            f = True
        elif j[0] == '%' and not f:
            t1.remove(j)
            f = True
        elif not f:
            t1.remove(j)
    if f:
        if t1:
            r = random.choice(t1)
            print('бот выбрал:', r)
            vk_session.method('messages.send', {'chat_id': id, 'message': r, 'random_id': 0})
        else:
            vk_session.method('messages.send', {'chat_id': id, 'message': 'Ты что дурак? Я из чего должен выбирать?', 'random_id': 0})
    else:
        vk_session.method('messages.send', {'chat_id': id, 'message': 'Ты дебил. Исправь комментарии', 'random_id': 0})


def anecdot(id):
    con = sqlite3.connect('анекдоты.sqlite')
    cur = con.cursor()
    res = cur.execute('''SELECT anecdote FROM anecdotes ORDER BY RANDOM() LIMIT 1;''').fetchall()
    sender(id, res)


def primer(id, text):
    try:
        s = time.time()
        if text in ['1000-7', '1000 -7', '1000- 7', '1000 - 7']:
            t = 'ГУЛЬ'
            sender(id, 'ГУЛЬ')
        else:
            t = eval(text)
            e = time.time()
            sender(id, f'{t}\nВремя решения{e - s}')
    except (NameError, SyntaxError):
        sender(id, 'Не коректный запрос')
    except MemoryError:
        sender(id, 'Мне плохо')


def idvk(id, id1=1, id2=100):
    for i in range(id1, id2 + 1):
        sender(id, f'[id{i}|{i}]')


def chislo(id, text):
    text = text.split()
    try:
        if len(text) == 2:
            sender(id, random.choice([i for i in range(int(text[0]), int(text[1]))]))
        elif len(text) == 3:
            sender(id, random.choice([i for i in range(int(text[0]), int(text[1]), int(text[2]))]))
        else:
            raise ValueError
    except ValueError:
        sender(id, 'не корректные данные')


def new_anecdot(text):
    con = sqlite3.connect('анекдоты.sqlite')
    cur = con.cursor()
    cur.execute('''INSERT INTO anecdotes(anecdote) VALUES (?)''', (text, ))
    con.commit()


def ng(id):
    t = datetime.now()
    ng = datetime(2023, 1, 1, 0, 0, 0)
    d = ng - t
    sender(id, f'Дней до нового года  {d.days}²  \nЧасов до нового года  {d.seconds//3600}²  \nМинут до нового года  {d.seconds%3600//60}²')


def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                msg = event.object.message['text']
                id = event.chat_id
                try:
                    us = event.object.message['from_id']
                    ch = event.object
                    if us == 384865257:
                        us = 'Глеб'
                    elif us == 645594285:
                        us = 'Кирилл'
                    elif us == 321798834:
                        us = 'Cергий'
                    elif us == 320139123:
                        us = 'Ксюща'
                    elif us == 529651364:
                        us = 'Андрей'
                    if id == 2:
                        print('CТРИМ', end=' ')
                    elif id == 3:
                        print('Игнорщики', end=' ')
                    elif id == 4:
                        print('География', end=' ')
                    print(us, end=': ')
                    print(event.object.message["text"])
                    print(event.object.message["action"]["type"])
                    if event.object.message['action']['type'] == 'chat_kick_user':
                        if event.object.message['from_id'] == 645594285:
                            sender(id, '[id320139123|Ксения]\n КИРИЛЛ БУЯНИТ')
                        if event.object.message['action']['member_id'] == 645594285:
                            sender(id, 'Туда его')
                        else:
                            sender(id, 'F')
                    if event.object.message['action']['type'] == 'chat_invite_user':
                        if event.object.message['action']['member_id'] == 645594285:
                            sender(id, 'C вовращением!!! ЛОООООООХ')
                        else:
                            sender(id, 'C вовращением!!!')
                except KeyError:
                    pass
                if msg[:7] in ['!выбор ', '!админ ']:
                    admin(id, msg[7:])
                elif msg[:8] in ['!выбери ', '!choice ', '!choose ']:
                    admin(id, msg[8:])
                elif msg[:6] == '!pick ':
                    admin(id, msg[6:])
                elif msg[:6] == '!спам ':
                    try:
                        if len(msg.split()) != 2:
                            if msg.split()[-1] != '0':
                                for _ in range(int(msg.split()[-1])):
                                    sender(id, f' '.join(msg.split()[1:-1]))
                        else:
                            sender(id, f'И что я по твоему должен сделать {msg.split()[-1]} раз?')
                    except ValueError:
                        sender(id, 'Дурак Последнее должно быть число')
                elif msg == '!геншин':
                    sender(id, 'ГЕНШИН ТОООООООООП!!!!!!!')
                elif msg[:6] == '!реши ':
                    primer(id, msg[6:])
                elif msg == '!анекдот':
                    anecdot(id)
                elif msg[:4] == '!id ':
                    a = msg.split()
                    try:
                        if len(a) == 1:
                            idvk(id)
                        elif len(a) == 3:
                            if int(a[1]) < int(a[2]):
                                idvk(id, int(a[1]), int(a[2]))
                            else:
                                raise ValueError
                        else:
                            raise ValueError
                    except ValueError:
                        sender(id, 'нормально попроси')
                elif msg == 'СК' or msg == 'CK':
                    sender(id, '[id645594285|С][id320139123|К]')
                elif msg[:7] == '!число ':
                    chislo(id, msg[7:])
                elif msg == '!нг':
                    ng(id)
                elif msg[:6] == '!глеб ':
                    sender(id, f'[id384865257|{msg[6:]}]')
                elif msg[:7] == '!ксюша ':
                    sender(id, f'[id320139123|{msg[7:]}]')
                elif msg[:8] == '!кирилл ':
                    sender(id, f'[id645594285|{msg[8:]}]')
                elif msg[:8] == '!андрей ':
                    sender(id, f'[id529651364|{msg[8:]}]')
                elif msg[:8] == '!сережа ':
                    sender(id, f'[id321798834|{msg[8:]}]')
                elif msg[:10] == '!добавить ':
                    print('''+ для добавления
- для отказа''')
                    while True:
                        if (n:=input()) == '+':
                            new_anecdot(msg[10:])
                            print("добавленно")
                            break
                        elif n == '-':
                            print('значит плохой анекдот')
                            break
                        else:
                            print('+ или -')


if __name__ == '__main__':
    while True:
        try:
            main()
        except (requests.exceptions.ConnectionError, TimeoutError, requests.exceptions.Timeout, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            continue