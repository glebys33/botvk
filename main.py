import socket

import requests.exceptions
import urllib3.exceptions
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from config import token_bot


vk_session = vk_api.VkApi(token=token_bot)
longpoll = VkBotLongPoll(vk_session, 209322786)
print('бот запущен')


def sender(id, text):
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})


def admin(id, text):
    t = text
    t1 = t
    f = True
    a = 0
    for i in range(len(t)):
        if t[i] == '%' and f:
            f = False
            a = i
        elif t[i] == '%' and not f:
            t1 = t1[:a] + t1[i + 1:]
            f = True
    if f:
        if t1:
            vk_session.method('messages.send', {'chat_id': id, 'message': random.choice(t1.split()), 'random_id': 0})
        else:
            vk_session.method('messages.send', {'chat_id': id, 'message': 'Ты что дурак? Я из чего должен выбирать?', 'random_id': 0})
    else:
        vk_session.method('messages.send', {'chat_id': id, 'message': 'Ты дебил. Исправь комментарии', 'random_id': 0})


for event in longpoll.listen():
    try:
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                msg = event.object.message['text'].lower()
                id = event.chat_id
                if msg[:7] == '!выбор ':
                    admin(id, msg[7:])
                if msg[:8] == '!выбери ':
                    admin(id, msg[8:])
                if msg[:7] == '!админ ':
                    admin(id, msg[7:])
                if msg[:6] == '!pick ':
                    admin(id, msg[6:])
                if msg[:8] == '!choice ':
                    admin(id, msg[8:])
                if msg[:8] == '!choose ':
                    admin(id, msg[8:])
                if msg[:6] == '!спам ':
                    try:
                        for _ in range(int(msg.split()[-1])):
                            sender(id, ' '.join(msg.split()[1:-1]))
                    except ValueError:
                        sender(id, 'Дурак Последнее должно быть число')
                if msg == '!геншин':
                    sender(id, 'ГЕНШИН ТОООООООООП!!!!!!!')
    except requests.exceptions.ReadTimeout:
        pass
    except socket.timeout:
        pass
    except urllib3.exceptions.ReadTimeoutError:
        pass