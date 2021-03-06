import time
import requests.exceptions
import vk_api
import requests
import wikipedia
from vk_api.exceptions import ApiHttpError, ApiError
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from threading import Thread
from datetime import datetime
from config import TOKEN
from bs4 import BeautifulSoup as BS
from sympy import sympify, Symbol, expand
import sqlite3
import json
import random

vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk_session, 209322786)
vk = vk_session.get_api()
''' ✓ / ❌
❌сообщения как валюта
✓счётчик дней / !доска
✓!когда
✓!праздник
✓доброе утро + сн
ежедневное ограничение на анекдоты
сделать авто определение +/- у !доски
добавить wifi.py в main.py
✓!пабло
!через+'''


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
    query_json = json.dumps({"peer_id": peer_id, "conversation_message_ids": [message_id], "is_reply": True})
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
            vk_session.method('messages.send', {'chat_id': id, 'message': r, 'random_id': 0})
        else:
            vk_session.method('messages.send',
                              {'chat_id': id, 'message': 'Ты что дурак? Я из чего должен выбирать?', 'random_id': 0})
    else:
        vk_session.method('messages.send', {'chat_id': id, 'message': 'Ты дебил. Исправь комментарии', 'random_id': 0})


def spam(id, msg, us):
    try:
        if len(msg) != 2:
            if msg[-1] != '0':
                with open('data/spam.txt') as file, open('data/money.txt') as m:
                    a = {int(i.split()[0]): i.split()[1:] for i in m.readlines() if len(i.split()) > 0}
                    spam = file.readlines()
                if int(msg[-1]) <= int(spam[int(a[us][1])]):
                    for _ in range(int(msg[-1])):
                        sender(id, f' '.join(msg[1:-1]))
                else:
                    sender(id, 'Много хочешь))')
        elif len(msg) == 2 and isdigit(msg[1]):
            sender(id, f'И что я по твоему должен сделать {msg[-1]} раз?')
        else:
            sender(id, 'Дурак Последнее должно быть число')
    except ValueError:
        sender(id, 'Дурак Последнее должно быть число')


def anecdot(id):
    con = sqlite3.connect('data/анекдоты.sqlite')
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
    except ZeroDivisionError:
        sender(id, 'Дурак')


def idvk(id, id1=1, id2=100):
    for i in range(id1, id2 + 1):
        sender(id, f'[id{i}|{i}]')


def date(id, date):
    try:
        sender(id, f'{(datetime.strptime(date, "%d.%m.%Y") - datetime.now()).days + 1} дней')
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
        sender(id, 'некорректные данные')


def new_anecdot(text):
    con = sqlite3.connect('data/анекдоты.sqlite')
    cur = con.cursor()
    cur.execute('''INSERT INTO anecdotes(anecdote) VALUES (?)''', (" ".join(text),))
    con.commit()


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
    r.close()
    title = html.select('.today > .holidays-list')
    sender(id, '•' + '\n\n•'.join([' '.join(i.split()) for i in title[0].text.split('\n') if i][:10]))


def good_morning_and_good_night():
    while True:
        if (dt := datetime.now()).hour == 23 and dt.minute == 30:
            sender(3, "Всем спокойной ночи")
        elif dt.hour == 6 and dt.minute == 40 and dt.weekday() != 6:
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
                            if m[(int(msg) - 1) // 3][(int(msg) - 1) % 3] == '--':
                                if p == [p1, p2]:
                                    m[(int(msg) - 1) // 3][(int(msg) - 1) % 3] = 'X'
                                elif p == [p2, p1]:
                                    m[(int(msg) - 1) // 3][(int(msg) - 1) % 3] = 'O'
                                p.reverse()
                                sender(id,
                                       '○○○○○\n' + ' '.join([str(i + 1) if m[0][i] == '--' else m[0][i] for i in range(
                                           3)]) + '\n' + ' '.join(
                                           [str(i + 4) if m[1][i] == '--' else m[1][i] for i in range(
                                               3)]) + '\n' + ' '.join(
                                           [str(i + 7) if m[2][i] == '--' else m[2][i] for i in range(
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
    r = requests.get('https://www.banki.ru/products/currency/eur/')
    html = BS(r.content, 'html.parser')
    r.close()
    eur = html.select('.currency-table__darken-bg > .currency-table__large-text')[0].text
    r = requests.get('https://www.banki.ru/products/currency/usd/')
    html = BS(r.content, 'html.parser')
    r.close()
    usd = html.select('.currency-table__darken-bg > .currency-table__large-text')[0].text
    sender(id, f'EUR Евро: {eur}\nUSD Доллар США: {usd}')


def wiki(id, msg):
    wikipedia.set_lang('ru')
    try:
        sender(id, wikipedia.page(' '.join(msg)).content.split('==')[0][:4096])
    except wikipedia.exceptions.DisambiguationError:
        sender(id, 'В скобках укажите тип желаемого запроса')
    except wikipedia.exceptions.PageError:
        sender(id, 'Некорректный запрос')


def weekday(id, msg):
    dn = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    try:
        if len(msg) == 2:
            sender(id, dn[datetime.strptime(msg[-1], "%d.%m.%Y").weekday()])
        else:
            raise ValueError
    except ValueError:
        sender(id, 'неверный формат даты')


def cherez(id, mag):
    pass


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
            sender(id, '''Функции доски писать через пробел после ключевого слова:

• set (название) (значение) ("+", "-", "inf", "-inf", " ") - добавляет новый счётчик чего-либо;
• del (название) - удаляет счётчик;
• update (название) (новое значение) - устанавливает новое значение указанному параметру, при вводе ТОЛЬКО ключевого слова обновляются все параметры;
• СК (значение 1) (значение 2) - устанавливает новое значение в соревновании СК;''')
        elif msg[1] == 'update':
            if len(msg) == 2:
                update()
            else:
                if len(msg) > 3:
                    if isdigit(msg[-1]):
                        if (m := ' '.join(msg[2:-1])) in spp:
                            spp[m] = msg[-1]
                        if m in smm:
                            smm[m] = msg[-1]
                        if m in const:
                            const[m] = msg[-1]
                        if (m in pinf) or (m in minf):
                            sender(id, 'Я так не умею')
                    elif msg[-1] == 'inf':
                        if (m := ' '.join(msg[2:-1])) in spp:
                            del spp[m]
                            pinf[m] = 'inf'
                        if m in smm:
                            del smm[m]
                            pinf[m] = 'inf'
                        if m in const:
                            del const[m]
                            pinf[m] = 'inf'
                        if m in minf:
                            del minf[m]
                            pinf[m] = 'inf'
                    elif msg[-1] == '-inf':
                        if (m := ' '.join(msg[2:-1])) in spp:
                            del spp[m]
                            minf[m] = '-inf'
                        if m in smm:
                            del smm[m]
                            minf[m] = '-inf'
                        if m in const:
                            del const[m]
                            minf[m] = '-inf'
                        if m in pinf:
                            del pinf[m]
                            minf[m] = '-inf'
                    else:
                        sender(id, 'Последнее должно быть число или inf/-inf')
                else:
                    sender(id, "Неверный формат")
            save_board(ckvsck, spp, smm, pinf, minf, const)
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


def proisvod(id, msg):
    try:
        if len(msg) == 1:
            sender(id, 'гений')
            return
        msg = ' '.join(msg[1:])
        if (',' in msg) and (msg.count(',') == 1):
            expr = sympify(msg.split(',')[0])
            x = Symbol('x')
            sender(id, f"f'(x)={expr.diff()} \nf'(x0)={expr.diff().subs('x', int(msg.split(',')[1]))}")
        elif msg.count(',') > 1:
            sender(id, 'Ты написал что-то не то')
        else:
            expr = sympify(msg)
            sender(id, expr.diff())
    except ValueError:
        sender(id, 'Чё ты написал? Я не понял')


def kas(id, msg):
    try:
        if len(msg) == 1:
            sender(id, 'гений')
            return
        if isdigit(msg[-1]):
            expr = sympify(' '.join(msg[1:-1]))
            pr = expr.diff()
            x = Symbol('x')
            fx = expr.subs(x, int(msg[-1]))
            fsx = pr.subs(x, int(msg[-1]))
            ans = fx + fsx*(x - int(msg[-1]))
            sender(id, f'y = {expand(ans)}')
        else:
            sender(id, 'Последним должно быть число')
    except ValueError:
        sender(id, 'Чё ты написал? Я не понял')


def defolt_clav(text: str, id: int):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Магазин улучшений', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()

    keyboard.add_button('Здания', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Баланс', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Бусты', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()

    keyboard.add_button('Получить прибыль', color=VkKeyboardColor.SECONDARY)

    vk.messages.send(
        peer_id=id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=text
    )


def zdan_clav(text: str, house: str, lvl: int,  id: int):
    keyboard = VkKeyboard(one_time=False)

    if lvl == 0:
        keyboard.add_button(str(house), color=VkKeyboardColor.NEGATIVE)
    elif lvl == 3:
        keyboard.add_button(str(house), color=VkKeyboardColor.POSITIVE)
    else:
        keyboard.add_button(str(house), color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('<---', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('--->', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()

    keyboard.add_button('Выход', color=VkKeyboardColor.PRIMARY)

    if lvl < 3:
        vk.messages.send(
            peer_id=id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message=text
        )
    else:
        vk.messages.send(
            peer_id=id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message=text.split('\n')[0] + '\nМаксимальный уровень'
        )


def magaz_clav(text: str, id: int):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('прокачка !спам', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()

    keyboard.add_button('неАСУ', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Обращения', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Таблицы', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()

    keyboard.add_button('Донат', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()

    keyboard.add_button('Выход', color=VkKeyboardColor.SECONDARY)

    vk.messages.send(
        peer_id=id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=text
    )


def spam_clav(text, id):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Уровни', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()

    keyboard.add_button('Улучшить', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()

    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    vk.messages.send(
        peer_id=id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=text
    )


def spam_updt(lvl, id):
    if lvl == 8:
        spam_clav('У тебя максимальный уровень', id)
    else:
        with open('data/money.txt', 'r+') as file:
            a = {int(i.split()[0]): i.split()[1:] for i in file.readlines() if len(i.split()) > 0}
            if int(a[id][0]) >= lvl * 1000:
                a[id][0] = str(int(a[id][0]) - lvl * 1000)
                a[id][1] = str(int(a[id][1]) + 1)
                spam_clav(f'Твой уровень: {int(a[id][1]) + 1} \nСтоимость улучшения:{(int(a[id][1]) + 1) * 1000}', id)
                file.seek(0)
                file.writelines([str(i) + ' ' + " ".join(a[i]) + '\n' for i in a])
            else:
                spam_clav('У тебя недостаточно средств', id)


def clav(id):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Хохла спросить забыли', color=VkKeyboardColor.POSITIVE)

    keyboard.add_line()

    keyboard.add_button('!пабло', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('!праздник', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('!топ', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()

    keyboard.add_button('!курс', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('!доска', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()

    keyboard.add_button('!нг', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('!геншин', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('!бен', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()

    keyboard.add_button('!анекдот', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('!помощь', color=VkKeyboardColor.POSITIVE)

    vk_session.method('messages.send', {
        'chat_id': id,
        'message': 'ну держи',
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard()})


def buy_zavod(zav, id):
    with open('data/houses.txt', encoding='utf8') as f, open('data/money.txt', 'r+') as m, open('data/levels.txt', 'r+') as l:
        h = {' '.join(i.split()[:-6]): i.split()[-6:] for i in f.readlines() if len(i.split()) > 0}
        zavid = list(h.keys()).index(zav)
        a = {int(i.split()[0]): i.split()[1:] for i in m.readlines() if len(i.split()) > 0}
        lvl = {int(i.split()[0]): i.split()[1:] for i in l.readlines() if len(i.split()) > 0}
        if (int(lvl[id][zavid]) < 3) and (int(a[id][0]) >= int(h[zav][3 + int(lvl[id][zavid])])):
            a[id][0] = str(int(a[id][0]) - int(h[zav][3 + int(lvl[id][zavid])]))
            lvl[id][zavid] = str(int(lvl[id][zavid]) + 1)
            if int(lvl[id][zavid]) == 1:
                zdan_clav(f'Вы преобрели {zav}', zav, int(lvl[id][zavid]), id)
            else:
                zdan_clav('Уровень повышен', zav, int(lvl[id][zavid]), id)
            m.seek(0)
            m.writelines([str(i) + ' ' + " ".join(a[i]) + '\n' for i in a])
            l.seek(0)
            l.writelines([str(i) + ' ' + " ".join(lvl[i]) + '\n' for i in lvl])
        elif int(lvl[id][zavid]) == 3:
            zdan_clav('Это здание максимального уровня', zav, 3, id)
        elif int(a[id][0]) < int(h[zav][3 + int(lvl[id][zavid])]):
            zdan_clav('Недостаточно средств', zav, int(lvl[id][zavid]), id)


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
            if event.object.message['text'][:28] == '[club209322786|@ignorshici] ':
                event.object.message['text'] = event.object.message['text'][28:]
            if event.from_chat:
                msg = event.object.message['text']
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
                msg = msg.split()
                if "action" in event.object.message:
                    if event.object.message['action']['type'] == 'chat_kick_user':
                        if event.object.message['action']['member_id'] == event.object.message['from_id']:
                            sender(id, 'Ну и пошел ты')
                        elif event.object.message['from_id'] == 645594285:
                            sender(id, '[id320139123|КСЮШААА] КИРИЛЛ БУЯНИТ')
                        elif event.object.message['action']['member_id'] == 645594285:
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
                if '卐' in ' '.join(msg):
                    answer_message(id, message_id, peer_id, 'АСУ')
                    asy = True
                if ('z' in ' '.join(msg)) or ('Z' in ' '.join(msg)):
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

!праздник - команда, выводящая 10 сегодняшних праздников

!дуэль (!крестики-нолики, !кн) id - запускается игра крестики-нолики,
в которую вы играете человеком, айди которого указан после ключевого
слова (айди указывать только цифрами).
 
!курс - команда выводит курс евро и доллара. Курсы берутся с 
официального сайта Центрального Банка России.
 
!доска - !доска - бот выводит доСКу (см. кабинет информатики).
!доска help для дополнительной информации.
 
!вики (запрос) - поиск на Википедии введённого запроса (писать без скобок).

!когда ДД.ММ.ГГГГ - команда, которая выводит точное время 
до указанной даты (дата пишется именно в указанном формате).

!день ДД.ММ.ГГГГ - выводит день недели, который будет в указанную дату

!бен комментарий - схож с командой !выбор, но выводит либо yes, либо no, либо ho-ho-ho, либо uue.

!производная - вычисляет производную заданного выражения (степень числа помечается через "**",
а квадратный корень через "sqrt()" //писать без кавычек).
Также, указав через запятую значение, можно высчитать производную в определённой точке (x0).

!касательная (выражение) (x0) - вычисляет уравнение касательной к графику заданной функции по 
формуле:y=f(x0)+f'(x0) ×(x-x0). (степень числа помечается через "**", а квадратный корень через
"sqrt()"//писать без кавычек, а задаваемые значения без скобок).

В лс бота присутствует мини-игра "Богачъ". Её суть заключается в покупке 
различных различных предприятий, приносящих прибыль. Главная цель игры стать 
Илоной Максом. Предприятия имеют три уровня, на каждом из которых 
производительность предприятий увеличивается. В боте вскоре будет 
добавлены бусты (временное увеличение производительности). 
Производительность заводов суммируется.

Бот полностью осуждает все слова, связанные с оскорблениями расс,
принадлежностей к гендерам или оскорблений людей с ограниченными
возможностями. Относитесь ко всем с толерантностью.
 
Исходный код: https://github.com/glebys33/botvk''')
                        elif msg[0] in ['!выбор', '!админ', '!выбери', '!choice', '!choose', '!pick']:
                            admin(id, msg[1:])
                        elif msg[0] == '!топ':
                            with open('data/top.txt') as file:
                                a = [i.split() for i in file.readlines()]
                                a.reverse()
                                sender(id,
                                       '\n'.join([f"{vk.users.get(user_ids=i)[0]['first_name']} {i[1]}" for i in a]))
                        elif msg[0] == '!спам':
                            th = Thread(target=spam, args=(id, msg, us))
                            th.start()
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
                            new_anecdot(msg[1:])
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
                        elif msg[0] == '!вики':
                            wiki(id, msg)
                        elif msg[0] == '!день':
                            weekday(id, msg)
                        elif msg[0] == '!через':
                            cherez(id, msg)
                        elif msg[0] == '!клава':
                            clav(id)
                        elif msg[0] == '!бен':
                            if ' '.join(msg[1:]).lower() == 'do you love god?':
                                admin(id, ['no'])
                            else:
                                admin(id, ['yes', 'no', 'ho-ho-ho', 'uue'])
                        elif msg[0] == '!производная':
                            proisvod(id, msg)
                        elif msg[0] == '!касательная':
                            kas(id, msg)
                    except IndexError:
                        pass
            elif event.from_user:
                msg = event.object.message['text']
                id = event.obj.message['from_id']
                user = vk.users.get(user_ids=id)[0]
                if id not in [521429287, 445026989, 313331381, 277784941, 366069942, 321798834, 645594285, 320139123,
                              529651364, 384865257]:
                    continue
                if msg == 'Баланс':
                    with open('data/money.txt') as file:
                        a = {int(i.split()[0]): [int(i.split()[1]), int(i.split()[2]), float(i.split()[7])] for i in
                             file.readlines() if len(i.split()) > 0}

                        if id in a:
                            defolt_clav(f'Ваш баланс {a[id][0]} \nБустер: {a[id][2]}', id)
                        else:
                            defolt_clav('Ты кто такой?', id)

                elif msg == 'Бусты':
                    defolt_clav('В разработке', id)

                elif msg == 'Здания':
                    with open('data/money.txt', 'r+') as file:
                        a = {int(i.split()[0]): i.split()[1:] for i in file.readlines() if len(i.split()) > 0}
                    with open('data/houses.txt', encoding='utf8') as f, open('data/levels.txt', 'r+') as l:
                        s = f.readlines()
                        h = {' '.join(i.split()[:-6]): i.split()[-6:] for i in s if len(i.split()) > 0}
                        house = ' '.join(s[int(a[id][5]) % len(s)].split()[:-6])
                        zavid = list(h.keys()).index(house)
                        lvl = {int(i.split()[0]): i.split()[1:] for i in l.readlines()}
                    zdan_clav(house + f': \nЦена: {s[zavid].split()[-3 + int(lvl[id][zavid])]}', house, int(lvl[id][zavid]), id)

                elif msg == '--->':
                    with open('data/money.txt', 'r+') as file:
                        a = {int(i.split()[0]): i.split()[1:] for i in file.readlines() if len(i.split()) > 0}
                        a[id][5] = str(int(a[id][5]) + 1)
                        file.seek(0)
                        file.writelines([str(i) + ' ' + " ".join(a[i]) + '\n' for i in a])
                    with open('data/houses.txt', encoding='utf8') as f, open('data/levels.txt', 'r+') as l:
                        s = f.readlines()
                        h = {' '.join(i.split()[:-6]): i.split()[-6:] for i in s if len(i.split()) > 0}
                        house = ' '.join(s[int(a[id][5]) % len(s)].split()[:-6])
                        zavid = list(h.keys()).index(house)
                        lvl = {int(i.split()[0]): i.split()[1:] for i in l.readlines()}
                    zdan_clav(house + f': \nЦена: {s[zavid].split()[-3 + int(lvl[id][zavid])]}', house, int(lvl[id][zavid]), id)

                elif msg == '<---':
                    with open('data/money.txt', 'r+') as file:
                        a = {int(i.split()[0]): i.split()[1:] for i in file.readlines() if len(i.split()) > 0}
                        a[id][5] = str(int(a[id][5]) - 1)
                        file.seek(0)
                        file.writelines([str(i) + ' ' + " ".join(a[i]) + '\n' for i in a])
                    with open('data/houses.txt', encoding='utf8') as f, open('data/levels.txt', 'r+') as l:
                        s = f.readlines()
                        h = {' '.join(i.split()[:-6]): i.split()[-6:] for i in s if len(i.split()) > 0}
                        house = ' '.join(s[int(a[id][5]) % len(s)].split()[:-6])
                        zavid = list(h.keys()).index(house)
                        lvl = {int(i.split()[0]): i.split()[1:] for i in l.readlines()}
                    zdan_clav(house + f': \nЦена: {s[zavid].split()[-3 + int(lvl[id][zavid])]}', house, int(lvl[id][zavid]), id)

                elif msg == 'Владимирский химический завод':
                    buy_zavod(msg, id)

                elif msg == 'Автоприбор':
                    buy_zavod(msg, id)

                elif msg == 'Ивановские мануфактуры':
                    buy_zavod(msg, id)

                elif msg == 'Шишкосушильная фабрика':
                    buy_zavod(msg, id)

                elif msg == 'Ашинский металлургический завод':
                    buy_zavod(msg, id)

                elif msg == 'Навозо-перегнойный завод':
                    buy_zavod(msg, id)

                elif msg == 'Конюшня':
                    buy_zavod(msg, id)

                elif msg == 'Дерьмоперегонный завод':
                    buy_zavod(msg, id)

                elif msg == 'Завод ЦЕМЕНТА':
                    buy_zavod(msg, id)

                elif msg == 'Атомно-ядерный завод':
                    buy_zavod(msg, id)

                elif msg == 'マンガファクトリー':
                    buy_zavod(msg, id)

                elif msg == 'Целюлозно-бумажный завод':
                    buy_zavod(msg, id)

                elif msg == 'Пивоварный завод':
                    buy_zavod(msg, id)

                elif msg == 'Фармацестический завод':
                    buy_zavod(msg, id)

                elif msg == 'Спермобанк':
                    buy_zavod(msg, id)

                elif msg == 'Ликёро-водочный завод':
                    buy_zavod(msg, id)

                elif msg == 'Завод по производству сала':
                    buy_zavod(msg, id)

                elif msg == 'Стекольный завод':
                    buy_zavod(msg, id)

                elif msg == 'ВАЗ':
                    buy_zavod(msg, id)

                elif msg == 'エロアニメ工房':
                    buy_zavod(msg, id)

                elif msg == 'Предприятие Россетей':
                    buy_zavod(msg, id)

                elif msg == 'Пельменная фабрика':
                    buy_zavod(msg, id)

                elif msg == 'Говновяземский мясокомбинат':
                    buy_zavod(msg, id)

                elif msg == 'Казино "NeNeabalovo100%"':
                    buy_zavod(msg, id)

                elif msg == 'Завод Ford':
                    buy_zavod(msg, id)

                elif msg == 'Завод эплокаров':
                    buy_zavod(msg, id)

                elif msg == 'Рыбный завод':
                    buy_zavod(msg, id)

                elif msg == 'Space X':
                    buy_zavod(msg, id)

                elif msg == 'Магазин улучшений':
                    magaz_clav('Выбирай с умом', id)

                elif msg == 'Донат':
                    magaz_clav('1 рубль = 50 Еврейская креативная валюта(ЕКВ)\n Сбер: 5469 1000 1372 5537 \n', id)

                elif msg == 'прокачка !спам':
                    with open('data/money.txt', 'r+') as file:
                        a = {int(i.split()[0]): i.split()[1:] for i in file.readlines() if len(i.split()) > 0}
                    spam_clav(f'Твой уровень: {int(a[id][1]) + 1} \nСтоимость улучшения:{(int(a[id][1]) + 1) * 1000 }', id)

                elif msg == 'Назад':
                    magaz_clav('Пожалуйста', id)

                elif msg == 'Уровни':
                    vk.messages.send(
                        peer_id=id,
                        random_id=get_random_id(),
                        message='''1. 99
2. 228
3. 365
4. 500
5. 666
6. 777
7. 889
8. 999'''
                    )

                elif msg == 'Улучшить':
                    with open('data/money.txt', 'r+') as file:
                        a = {int(i.split()[0]): i.split()[1:] for i in file.readlines() if len(i.split()) > 0}
                    spam_updt(int(a[id][1]) + 1, id)

                elif msg == 'Получить прибыль':
                    with open('data/money.txt', 'r+') as m, open('data/levels.txt') as l, open('data/houses.txt', encoding='utf8') as h:
                        file = h.readlines()
                        us_id = {int(i.split()[0]): i.split()[1:] for i in m.readlines() if len(i.split()) > 0}
                        lvl = {int(i.split()[0]): i.split()[1:] for i in l.readlines()}
                        last_data = datetime.strptime('.'.join([us_id[id][-2], us_id[id][-1], str(datetime.now().year)]), "%d.%m.%Y")
                        if last_data.date() == datetime.now().date():
                            defolt_clav('Ты сегодня уже получал прибыль', id)
                        elif lvl[id] == ['0' for i in range(len(file))]:
                            defolt_clav('Тебе нечего получать', id)
                        else:
                            us_id[id][-1], us_id[id][-2] = str(datetime.now().month), str(datetime.now().day)
                            sum_money = 0
                            for i, j in enumerate(lvl[id]):
                                if j != '0':
                                    sum_money += int(file[i].split()[-6:][int(j) - 1])
                            sum_money *= float(us_id[id][-3])
                            us_id[id][0] = str(int(us_id[id][0]) + round(sum_money))
                            defolt_clav(f'Ты получил прибыль: {round(sum_money)}', id)
                            m.seek(0)
                            m.writelines([str(i) + ' ' + " ".join(us_id[i]) + '\n' for i in us_id])

                elif msg == 'Выход':
                    defolt_clav('Главное меню', id)

                elif msg == 'Начать':
                    defolt_clav('Дароу новый богачъ', id)


if __name__ == '__main__':
    th = Thread(target=update_board, args=())
    th.start()
    th = Thread(target=start, args=())
    th.start()
    th = Thread(target=good_morning_and_good_night, args=())
    th.start()
