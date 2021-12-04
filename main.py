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
            vk_session.method('messages.send', {'chat_id': id, 'message': random.choice(t1), 'random_id': 0})
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
                        if msg.split()[-1] != '0':
                            for _ in range(int(msg.split()[-1])):
                                sender(id, ' '.join(msg.split()[1:-1]))
                    except ValueError:
                        sender(id, 'Дурак Последнее должно быть число')
                if msg == '!геншин':
                    sender(id, 'ГЕНШИН ТОООООООООП!!!!!!!')
    except requests.exceptions.ReadTimeout:
        continue
    except socket.timeout:
        continue
    except urllib3.exceptions.ReadTimeoutError:
        continue