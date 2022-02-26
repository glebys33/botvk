import time
import requests.exceptions
import vk_api
import sqlite3
import json
import random
import requests
from vk_api.exceptions import ApiHttpError, ApiError
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from threading import Thread
from datetime import datetime
from config import TOKEN
from bs4 import BeautifulSoup as BS


vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk_session, 209322786)
vk = vk_session.get_api()
print('бот запущен')

''' ✓ / ❌
❌сообщения как валюта
✓счётчик дней / !доска
✓!когда
✓!праздник
✓доброе утро + сн
✓крестики нолики
мини игра - рпг(хп, хилл, спасобности и т.д)
сделать авто определение +/- у !доски
сделать кликер, мб как валюту
работа с изображениями
✓!пабло'''


def sender(id, text):
    try:
        vk_session.method('messages.send', {
            'chat_id': id,
            'message': text,
            'random_id': 0})
    except ApiHttpError:
        sender(id, 'не хотю')
    except ApiError:
        sender(id, 'слишком длинный ответ')


def answer_message(chat_id, message_id, peer_id, text):
  query_json = json.dumps({"peer_id": peer_id,"conversation_message_ids":[message_id],"is_reply":True})
  vk_session.method('messages.send', {
    'chat_id': chat_id,
    'forward': [query_json],
    'message': text,
    'random_id': 0})


def admin(id, text):
    t = text
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
            vk_session.method('messages.send',
                              {'chat_id': id, 'message': 'Ты что дурак? Я из чего должен выбирать?', 'random_id': 0})
    else:
        vk_session.method('messages.send', {'chat_id': id, 'message': 'Ты дебил. Исправь комментарии', 'random_id': 0})


def anecdot(id):
    con = sqlite3.connect('анекдоты.sqlite')
    cur = con.cursor()
    res = cur.execute('''SELECT anecdote FROM anecdotes ORDER BY RANDOM() LIMIT 1;''').fetchall()
    sender(id, res)


def primer(id, text):
    try:
        text = ' '.join(text)
        if text == '1000 - 7':
            sender(id, 'ГУЛЬ')
        else:
            try:
                t = eval(text, {'__builtins__': None})
            except TypeError:
                t = 'Не надо так делать))'
            sender(id, f'{str(t)}')
    except (NameError, SyntaxError):
        sender(id, 'Не коректный запрос')
    except MemoryError:
        sender(id, 'Мне плохо')


def idvk(id, id1=1, id2=100):
    for i in range(id1, id2 + 1):
        sender(id, f'[id{i}|{i}]')


def date(id, date):
    try:
        sender(id, f'{(datetime(int(date[-4:]), int(date[3:5]), int(date[:2]), 0, 0) - datetime.now()).days} дней')
    except ValueError:
        sender(id, 'Моя твоя не понимать, что твоя хотеть.')


def chislo(id, text):
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
    cur.execute('''INSERT INTO anecdotes(anecdote) VALUES (?)''', (" ".join(text),))
    con.commit()


def prov_anecdot(id, msg):
    print('''+ для добавления
- для отказа''')
    while True:
        if (n := input()) == '+':
            new_anecdot(msg[1:])
            print("добавленно")
            break
        elif n == '-':
            print('значит плохой анекдот')
            break
        else:
            print('+ или -')


def ng(id):
    t = datetime.now()
    ng = datetime(2023, 1, 1, 0, 0, 0)
    d = ng - t
    sender(id,
           f'Дней до нового года  {d.days}²  \nЧасов до нового года  {d.seconds // 3600}²  \nМинут до нового года '
           f' {d.seconds % 3600 // 60}²')


def holiday(id):
    r = requests.get('https://calend.online/holiday/')
    html = BS(r.content, 'html.parser')
    title = html.select('.today > .holidays-list')
    sender(id, '•' + '\n\n•'.join([' '.join(i.split()) for i in title[0].text.split('\n') if i][:10]))


def good_morning_and_good_night():
    while True:
        if (dt := datetime.now()).hour == 23 and dt.minute == 30:
            sender(3, "Всем спокойной ночи")
        elif dt.hour == 7 and dt.minute == 0 and dt.weekday() != 6:
            sender(3, "Всем !доброе утро")
        elif dt.hour == 11 and dt.minute == 0 and dt.weekday() == 6:
            sender(3, "Всем ДОБРОЕ УТРО!!!")
        time.sleep(60)


def tic_tac_toe(id, id1, id2):
    try:
        p1, p2 = id1, int(id2)
    except ValueError:
        sender(id, 'Последним должны быть число (id противника)')
        return
    p = [p1, p2]
    m = [['--', '--', '--'], ['--', '--', '--'], ['--', '--', '--']]
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                us = event.object.message['from_id']
                msg = event.object.message['text']
                if us == p[0]:
                    if len(msg) == 1:
                        if msg.isdigit():
                            if m[(int(msg)-1) // 3][(int(msg)-1) % 3] == '--':
                                if p == [p1, p2]:
                                    m[(int(msg)-1) // 3][(int(msg)-1) % 3] = 'X'
                                elif p == [p2, p1]:
                                    m[(int(msg)-1) // 3][(int(msg)-1) % 3] = 'O'
                                p.reverse()
                                sender(id, '○○○○○\n' + ' '.join([str(i + 1) if m[0][i] == '--' else m[0][i]  for i in range(
                                    3)]) + '\n' + ' '.join([str(i + 4) if m[1][i] == '--' else m[1][i]  for i in range(
                                    3)]) + '\n' + ' '.join([str(i + 7) if m[2][i] == '--' else m[2][i]  for i in range(
                                    3)]))
                                if (m[0] == ['X', 'X', 'X']) or (m[1] == ['X', 'X', 'X']) or (m[2] == ['X', 'X', 'X']) \
                                        or (m[0][0] == m[1][0] == m[2][0] == 'X') or \
                                        (m[0][1] == m[1][1] == m[2][1] == 'X') \
                                        or (m[0][2] == m[1][2] == m[2][2] == 'X') or \
                                        (m[0][0] == m[1][1] == m[2][2] == 'X') \
                                        or (m[0][2] == m[1][1] == m[2][0] == 'X'):
                                    sender(id, f'[id{p1}|1 игрок] выйграл')
                                    break
                                if (m[0] == ['O', 'O', 'O']) or (m[1] == ['O', 'O', 'O']) or (m[2] == ['O', 'O', 'O']) \
                                        or (m[0][0] == m[1][0] == m[2][0] == 'O') or (
                                        m[0][1] == m[1][1] == m[2][1] == 'O') \
                                        or (m[0][2] == m[1][2] == m[2][2] == 'O') or (
                                        m[0][0] == m[1][1] == m[2][2] == 'O') \
                                        or (m[0][2] == m[1][1] == m[2][0] == 'O'):
                                    sender(id, f'[id{p2}|2 игрок] выйграл')
                                    break
                                f = False
                                for i in m:
                                    for j in i:
                                        if j == '--':
                                            f = True
                                if not f:
                                    sender(id, 'Никто не выйграл')
                                    break


def pablo(id):
    try:
        vk_session.method('messages.send', {
            'chat_id': id,
            'attachment': 'audio529651364_456239047',
            'random_id': 0})
    except ApiHttpError:
        sender(id, 'не хотю')
    except ApiError:
        sender(id, 'слишком длинный ответ')


def course(id):
    r = requests.get('https://cbr.ru/currency_base/daily/')
    html = BS(r.content, 'html.parser')
    title = html.select('.table > .data')
    sender(id, '\n'.join((a:=i.split('\n'))[2] + ' ' + a[4] + '\n' + a[3] + ' - ' + a[5] + '\n' for i in
                         title[0].text.split('\n\n')[12:14]))


def update():
    with open('data/board.txt', 'r+') as file:
        file.seek(0)
        ckvsck = file.readline().split()
        a = file.readlines()
        spp = {}
        smm = {}
        pinf = {}
        minf = {}
        const = {}
        for i in a:
            i = i.split()
            if i[-1] == '+':
                spp[' '.join(i[:-2])] = i[-2]
            elif i[-1] == '-':
                smm[' '.join(i[:-2])] = i[-2]
            elif i[-1] == 'inf':
                pinf[' '.join(i[:-1])] = i[-1]
            elif i[-1] == '-inf':
                minf[' '.join(i[:-1])] = i[-1]
            else:
                const[' '.join(i[:-1])] = i[-1]
        for i in spp:
            spp[i] = str(int(spp[i]) + 1)
        for i in smm:
            smm[i] = str(int(smm[i]) - 1)
        save_board(ckvsck, spp, smm, pinf, minf, const)


def update_board():
    while True:
        if (dt := datetime.now()).hour == 00 and dt.minute == 00:
            update()
        time.sleep(60)


def forced_update_board():
    print('''да для обновления
нет для отказа''')
    while True:
        n = input()
        if n == 'да':
            f = True
            break
        elif n == 'нет':
            f = False
            break
        else:
            print("да или нет")
    if f:
        update()


def save_board(ckvsck, spp, smm, pinf, minf, const):
    with open('data/board.txt', 'w+') as file:
        file.seek(0)
        file.write(ckvsck[0] + ' ' + ckvsck[1] + '\n')
        for i in spp:
            file.write(i + " " + spp[i] + ' +\n')
        for i in smm:
            file.write(i + " " + smm[i] + ' -\n')
        for i in pinf:
            file.write(i + " " + ' inf\n')
        for i in minf:
            file.write(i + " " + ' -inf\n')
        for i in const:
            file.write(i + " " + const[i] + '\n')


def isdigit(str: str):
    return str[-1].isdigit() or (str[-1][0] == '-' and str[-1][1:].isdigit())


def board(id, msg):
    with open('data/board.txt', 'r+') as file:
        file.seek(0)
        ckvsck = file.readline().split()
        a = file.readlines()
        spp = {}
        smm = {}
        pinf = {}
        minf = {}
        const = {}
        for i in a:
            i = i.split()
            if i[-1] == '+':
                spp[' '.join(i[:-2])] = i[-2]
            elif i[-1] == '-':
                smm[' '.join(i[:-2])] = i[-2]
            elif i[-1] == 'inf':
                pinf[' '.join(i[:-1])] = i[-1]
            elif i[-1] == '-inf':
                minf[' '.join(i[:-1])] = i[-1]
            else:
                const[' '.join(i[:-1])] = i[-1]
    if len(msg) == 1:
        s = "СК доска 2.0 изи 30.11.20" + f"\n {datetime.now().date()}\n"
        for i in pinf:
            s += ' '.join([i, str(pinf[i])])
            s += '\n'
        for i in minf:
            s += ' '.join([i, str(minf[i])])
            s += '\n'
        for i in spp:
            s += ' '.join([i, str(spp[i])])
            s += '\n'
        for i in smm:
            s += ' '.join([i, str(smm[i])])
            s += '\n'
        for i in const:
            s += ' '.join([i, str(const[i])])
            s += '\n'
        s += '"2" + "1"' + '   CK '
        s += str(ckvsck[0]) + ' VS ' + str(ckvsck[1])
        s += '  CK'
        sender(id, s)
    else:
        if msg[1] == 'set':
            if (msg[-1] in ['-', '+', 'inf', '-inf']) or isdigit(msg[-1]):
                try:
                    if (msg[-1] != 'inf') and (msg[-1] != '-inf') and not isdigit(msg[-1]):
                        msg[-2] = int(msg[-2])
                        msg[-2] = str(msg[-2])
                except ValueError:
                    sender(id, 'Предпоследнее должно быть число')
                if msg[-1] == '+':
                    if (m := ' '.join(msg[2:-2])) in spp:
                        del spp[m]
                    if m in smm:
                        del smm[m]
                    if m in pinf:
                        del pinf[m]
                    if m in minf:
                        del minf[m]
                    if m in const:
                        del const[m]
                    spp[m] = msg[-2]
                elif msg[-1] == '-':
                    if (m := ' '.join(msg[2:-2])) in spp:
                        del spp[m]
                    if m in smm:
                        del smm[m]
                    if m in pinf:
                        del pinf[m]
                    if m in minf:
                        del minf[m]
                    if m in const:
                        del const[m]
                    smm[m] = msg[-2]
                elif msg[-1] == 'inf':
                    if (m := ' '.join(msg[2:-1])) in spp:
                        del spp[m]
                    if m in smm:
                        del smm[m]
                    if m in pinf:
                        del pinf[m]
                    if m in minf:
                        del minf[m]
                    if m in const:
                        del const[m]
                    pinf[m] = msg[-1]
                elif msg[-1] == '-inf':
                    if (m := ' '.join(msg[2:-1])) in spp:
                        del spp[m]
                    if m in smm:
                        del smm[m]
                    if m in pinf:
                        del pinf[m]
                    if m in minf:
                        del minf[m]
                    if m in const:
                        del const[m]
                    minf[m] = msg[-1]
                elif isdigit(msg[-1]):
                    if (m := ' '.join(msg[2:-1])) in spp:
                        del spp[m]
                    if m in smm:
                        del smm[m]
                    if m in pinf:
                        del pinf[m]
                    if m in minf:
                        del minf[m]
                    if m in const:
                        del const[m]
                    const[m] = msg[-1]
                else:
                    if msg[-1] == '-':
                        smm[' '.join(msg[2:-2])] = msg[-2]
                    elif msg[-1] == '+':
                        spp[' '.join(msg[2:-2])] = msg[-2]
                    elif msg[-1] == 'inf':
                        pinf[' '.join(msg[2:-1])] = msg[-1]
                    elif msg[-1] == '-inf':
                        minf[' '.join(msg[2:-1])] = msg[-1]
                    else:
                        const[' '.join(msg[2:-1])] = msg[-1]
                save_board(ckvsck, spp, smm, pinf, minf, const)
            else:
                sender(id, 'последнее должно быть +/-(если введите число) или inf/-inf или число')
        elif msg[1] == 'help':
            """help, но для доски"""
        elif msg[1] == 'update':
            if len(msg) == 2:
                th = Thread(target=forced_update_board, args=())
                th.start()
            else:
                if len(msg) == 4:
                    if isdigit(msg[-1]):
                        if (m := ' '.join(msg[2:-1])) in spp:
                            spp[m] = msg[-1]
                        if m in smm:
                            smm[m] = msg[-1]
                        if m in pinf:
                            pinf[m] = msg[-1]
                        if m in minf:
                            minf[m] = msg[-1]
                        if m in const:
                            const[m] = msg[-1]
                    else:
                        sender(id, 'Последнее должно быть число')
                else:
                    sender(id, "Неверный формат")
        elif msg[1] == 'del':
            m = ' '.join(msg[2:])
            if m in spp:
                del spp[m]
            elif m in smm:
                del smm[m]
            elif m in pinf:
                del pinf[m]
            elif m in minf:
                del minf[m]
            elif m in const:
                del const[m]
            else:
                sender(id, 'Такого на доске нету')
            save_board(ckvsck, spp, smm, pinf, minf, const)
        elif msg[1] in ['CK', 'СК']:
            if len(msg) == 4:
                if msg[2].isdigit() and msg[3].isdigit():
                    save_board([msg[2], msg[3]], spp, smm, pinf, minf, const)
                else:
                    sender(id, 'Последнии 2 должны быть числами')
            else:
                sender(id, 'Неверный формат')


def start():
    while True:
        try:
            main()
        except (requests.exceptions.ConnectionError, TimeoutError, requests.exceptions.Timeout,
                requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            continue


def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if True:
                    msg = event.object.message['text']
                    msg = msg.split()
                    id = event.chat_id
                    peer_id = event.object.message['peer_id']
                    message_id = event.object.message['conversation_message_id']
                    us = event.object.message['from_id']
                    top = {}
                    with open('data/top.txt', 'r+') as file:
                        r = file.readlines()
                        for i in r:
                            user = list(map(int, i.split()))
                            top[user[0]] = user[1]
                        if us in top:
                            top[us] += 1
                        else:
                            top[us] = 1
                        sor_tup = sorted(top.items(), key=lambda item: item[1])
                        sor_top = {k: v for k, v in sor_tup}
                        file.seek(0)
                        file.writelines([str(i) + ' ' + str(top[i]) + '\n' for i in sor_top])
                    user = vk.users.get(user_ids=us)[0]
                    if id == 2:
                        print('CТРИМ', end=' ')
                    elif id == 3:
                        print('Игнорщики', end=' ')
                    elif id == 4:
                        print('География', end=' ')
                    print(user['first_name'], end=': ')
                    print(event.object.message["text"])
                    if "action" in event.object.message:
                        print(event.object.message["action"]["type"])
                        if event.object.message['action']['type'] == 'chat_kick_user':
                            if event.object.message['from_id'] == 645594285:
                                sender(id, '[id320139123|КСЮШААА] КИРИЛЛ БУЯНИТ')
                            if event.object.message['action']['member_id'] == 645594285:
                                sender(id, 'Туда его')
                            else:
                                sender(id, 'F')
                        if event.object.message['action']['type'] == 'chat_invite_user':
                            if event.object.message['action']['member_id'] == 645594285:
                                sender(id, 'C вовращением!!! ЛОООООООХ')
                            else:
                                sender(id, 'C вовращением!!!')
                    buc = 'ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ '
                    m = ''
                    for i in ' '.join(msg):
                        if i in buc:
                            m += i
                    m = list(map(lambda s: s.lower(), m.split()))
                    asy = False
                    for i in ['негр', 'негра', 'негру', 'негром', 'негре', 'негры', 'негров', 'неграм', 'неграми',
                              'неграх', 'пидор', 'пидора', 'пидору', 'пидором', 'пидора', 'пидоры', 'пидоров',
                              'пидорам', 'пидорам', 'пидорах', 'пидорас', 'пидораса', 'пидорасу', 'пидорасом',
                              'пиодорасе', 'пидорасы', 'пидорасов', 'пидорасам', 'пидорасами', 'пидорасах', 'пидр',
                              'даун', 'дауна', 'дауну', 'дауном', 'дауне', 'дауны', 'даунов', 'даунам', 'даунами',
                              'даунах']:
                        if i in m:
                            answer_message(id, message_id, peer_id, 'АСУ')
                            asy = True
                            break
                    if '卐' in msg:
                        answer_message(id, message_id, peer_id, 'АСУ')
                        asy = True
                    if 'асу' in m:
                        sender(id, 'АСУ')
                if not asy:
                    try:
                        if msg[0] in ['!help', '!помощь']:
                            sender(id, '''!выбор, !админ, !выбери, !choice, !choose, !pick -
- это команды которые выбирают случайный элемент, написанный после ключевого слова.
Также, эта команда поддерживает комментарии (%комментарий%).
Пример: !выбери %бот добрый?% да нет; бот случайно выберет да или нет.
        
!топ – команда, показывающая кто сколько сообщений отправил.
        
!спам – отправляет одно и то же сообщение несколько раз.
Пример: !спам абвгд 20; бот отправит сообщение абвгд 20 раз.
        
!геншин - бот отправит сообщение "ГЕНШИН ТОООООООООП!!!!!!!".
        
!реши - бот решит математическое выражение,
которое было написано после ключевого слова.
        
!анекдот - отправляет случайный анекдот из бд.
        
!id (n, m) – команда, которая отправит пользователей с id от n до m.
Если не указать n и m тогда отправит первые 100.
        
СК - отправит сообщение "СК" где "С" - Кирилл "К" – Ксюша.
        
!число n m (k) – отправляет случайное число от n до m (с шагом k).
        
!нг – команда, которая выводит сколько времени осталось до нового года.
        
!глеб(ксюша, кирилл, андрей, сережа) s – команда, которая присылает сообщение s
с ссылкой на пользователя, чьё имя было указано.

!добавить s - запрос на добавление анекдота s в бд.

!когда ДД.ММ.ГГГГ - команда, которая выводит точное время 
до указанной даты (дата пишется именно в указанном формате).

!праздник - команда, выводящая 10 сегодняшних праздников

Бот полностью осуждает все слова, связанные с оскорблениями расс,
принадлежностей к гендерам или оскорблений людей с ограниченными
возможностями. Относитесь ко всем с толерантностью.

!дуэль (!крестики-нолики, !кн) id - запускается игра крестики-нолики,
 в которую вы играете человеком, айди которого указан после ключевого
 слова (айди указывать только цифрами).
 
 !курс - команда выводит курс евро и доллара. Курсы берутся с 
 официального сайта Центрального Банка России.
 
 Исходный код: https://github.com/glebys33/botvk''')
                        elif msg[0] in ['!выбор', '!админ', '!выбери', '!choice', '!choose', '!pick']:
                            admin(id, msg[1:])
                        elif msg[0] == '!топ':
                            with open('data/top.txt') as file:
                                a = [i.split() for i in file.readlines()]
                                a.reverse()
                                sender(id, '\n'.join([f"{vk.users.get(user_ids=i)[0]['first_name']} {i[1]}" for i in a]))
                        elif msg[0] == '!спам':
                            try:
                                if len(msg) != 2:
                                    if msg[-1] != '0':
                                        for _ in range(int(msg[-1])):
                                            sender(id, f' '.join(msg[1:-1]))
                                else:
                                    sender(id, f'И что я по твоему должен сделать {msg[-1]} раз?')
                            except ValueError:
                                sender(id, 'Дурак Последнее должно быть число')
                        elif msg[0] == '!геншин':
                            sender(id, 'ГЕНШИН ТОООООООООП!!!!!!!')
                        elif msg[0] == '!реши':
                            primer(id, msg[1:])
                        elif msg[0] == '!анекдот':
                            anecdot(id)
                        elif msg[0] == '!когда':
                            if len(msg) == 2:
                                date(id, msg[1])
                            else:
                                sender(id, 'Я не ИИ чтобы додуматься что ты хочешь))')
                        elif msg[0] == '!id':
                            try:
                                if len(msg) == 1:
                                    idvk(id)
                                elif len(msg) == 3:
                                    if int(msg[1]) < int(msg[2]):
                                        idvk(id, int(msg[1]), int(msg[2]))
                                    else:
                                        raise ValueError
                                else:
                                    raise ValueError
                            except ValueError:
                                sender(id, 'нормально попроси')
                        elif msg[0] == 'СК' or msg[0] == 'CK':
                            sender(id, '[id645594285|С][id320139123|К]')
                        elif msg[0] == '!число':
                            chislo(id, msg[1:])
                        elif msg[0] == '!нг':
                            ng(id)
                        elif msg[0] == '!глеб':
                            sender(id, f'[id384865257|{" ".join(msg[1:])}]')
                        elif msg[0] == '!ксюша':
                            sender(id, f'[id320139123|{" ".join(msg[1:])}]')
                        elif msg[0] == '!кирилл':
                            sender(id, f'[id645594285|{" ".join(msg[1:])}]')
                        elif msg[0] == '!андрей':
                            sender(id, f'[id529651364|{" ".join(msg[1:])}]')
                        elif msg[0] == '!сережа':
                            sender(id, f'[id321798834|{" ".join(msg[1:])}]')
                        elif msg[0] == '!матвей':
                            sender(id, f'[id366069942|{" ".join(msg[1:])}]')
                        elif msg[0] == '!добавить':
                            th = Thread(target=prov_anecdot, args=(id, msg))
                            th.start()
                        elif msg[0] == '!доска':
                            board(id, msg)
                        elif msg[0] in ['!праздник', '!ФЕН']:
                            holiday(id)
                        elif msg[0] in ['!крестики-нолики', '!кн', '!дуэль']:
                            th = Thread(target=tic_tac_toe, args=(id, event.object.message['from_id'], msg[1]))
                            th.start()
                        elif msg[0] == '!пабло':
                            pablo(id)
                        elif msg[0] == '!курс':
                            course(id)
                    except IndexError:
                        pass


if __name__ == '__main__':
    th = Thread(target=update_board, args=())
    th.start()
    th = Thread(target=start, args=())
    th.start()
    th = Thread(target=good_morning_and_good_night, args=())
    th.start()
