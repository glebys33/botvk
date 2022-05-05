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
from datetime import datetime, date, timedelta
from config import TOKEN
from bs4 import BeautifulSoup as BS
from sympy import sympify, Symbol, expand
import sqlite3
import json
import random

vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk_session, 209322786)
vk = vk_session.get_api()
print("Бот запущен")
''' ✓ / ❌
❌сообщения как валюта
✓счётчик дней / !доска
✓!когда
✓!праздник
✓доброе утро + сн
ежедневное ограничение на анекдоты
сделать авто определение +/- у !доски
❌добавить wifi.py в main.py
✓!пабло
✓!через
фото карты местности'''


# функция для отправки сообщения
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


# функция для отправки сообщения с ответом
def answer_message(chat_id, message_id, peer_id, text):
    query_json = json.dumps({"peer_id": peer_id, "conversation_message_ids": [message_id], "is_reply": True})
    vk_session.method('messages.send', {
        'chat_id': chat_id,
        'forward': [query_json],
        'message': text,
        'random_id': 0})


# функция для выбора случайного сообщения
def random_word(id, text):
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
                              {'chat_id': id, 'message': 'Из чего я должен выбирать?', 'random_id': 0})
    else:
        vk_session.method('messages.send', {'chat_id': id, 'message': 'Исправь комментарии', 'random_id': 0})


def new_user(id):
    con = sqlite3.connect('data/rich.db')
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO money(user_id, score, spam, booster, page, date) VALUES({id}, 50, 0, 1, 0,
    {datetime.now().day - 1}) ''')
    cur.execute(
        f'''INSERT INTO levels(user_id, level) VALUES({id}, 
                            "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0") ''')
    con.commit()
    con.close()


# функция для спама
def spam(id, msg, us):
    try:
        if len(msg) != 2:
            if msg[-1] != '0':
                con = sqlite3.connect('data/rich.db')
                cur = con.cursor()
                res = cur.execute('''SELECT spam FROM money WHERE user_id = ?''', (us,)).fetchone()
                if res is None:
                    new_user(us)
                    spam(id, msg, us)
                else:
                    n_spam = [99, 228, 365, 500, 666, 777, 889, 999]
                    if int(msg[-1]) <= n_spam[[*res][0]]:
                        for _ in range(int(msg[-1])):
                            sender(id, f' '.join(msg[1:-1]))
                    else:
                        sender(id, 'Много хочешь')
        elif len(msg) == 2 and isdigit(msg[1]):
            sender(id, f'И что я должен сделать {msg[-1]} раз?')
        else:
            sender(id, 'Последнее должно быть число')
    except ValueError:
        sender(id, 'Последнее должно быть число')


# функция для отправки анекдота
def joke(id):
    con = sqlite3.connect('data/jokes.db')
    cur = con.cursor()
    res = cur.execute('''SELECT joke FROM jokes WHERE chat_id = ? ORDER BY RANDOM() LIMIT 1''', (id,)).fetchall()
    con.close()
    if len(res) == 0:
        sender(id, 'У вас нет анекдотов')
    else:
        sender(id, res)


# функция для решения математических примеров
def task(id, text):
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
        sender(id, 'На ноль делить нельзя')


# функция для отправки ссылок на пользователей с сзаданным id
def id_vk(id, id1=1, id2=100):
    for i in range(id1, id2 + 1):
        sender(id, f'[id{i}|{i}]')


# функция для отправки сообщения с количеством дней до указанной даты
def when(id, day_date):
    try:
        sender(id, f'{(datetime.strptime(day_date, "%d.%m.%Y") - datetime.now()).days + 1} дней')
    except ValueError:
        sender(id, 'Я не понимаю что ты хочешь')


# функция для отправки случайного числа
def number(id, text):
    try:
        if len(text) == 2:
            sender(id, random.choice([i for i in range(int(text[0]), int(text[1]))]))
        elif len(text) == 3:
            sender(id, random.choice([i for i in range(int(text[0]), int(text[1]), int(text[2]))]))
        else:
            raise ValueError
    except ValueError:
        sender(id, 'Некорректные данные')


# функция для добавления нового анекдота
def new_joke(text, id):
    con = sqlite3.connect('data/jokes.db')
    cur = con.cursor()
    cur.execute('''INSERT INTO jokes(joke, chat_id) VALUES (?, ?)''', (" ".join(text), id))
    con.commit()
    con.close()


# функция для отправки сообщения в котором указано время до нового года
def ng(id):
    t = datetime.now()
    ng = datetime(2023, 1, 1, 0, 0, 0)
    d = ng - t
    sender(id,
           f'Дней до нового года  {d.days}²  \nЧасов до нового года  {d.seconds // 3600}²  \nМинут до нового года '
           f' {d.seconds % 3600 // 60}²')


# функция для отправки сегоднешни праздников
def holiday(id):
    r = requests.get('https://calend.online/holiday/')
    html = BS(r.content, 'html.parser')
    r.close()
    title = html.select('.today > .holidays-list')
    sender(id, '•' + '\n\n•'.join([' '.join(i.split()) for i in title[0].text.split('\n') if i][:10]))


# функция для желания спокойной ночи и доброго утра
def good_morning_and_good_night(chat_id):
    while True:
        if (dt := datetime.now()).hour == 23 and dt.minute == 30:
            sender(chat_id, "Всем спокойной ночи")
        elif dt.hour == 6 and dt.minute == 40 and dt.weekday() != 6:
            sender(chat_id, "Всем доброе утро")
        elif dt.hour == 11 and dt.minute == 0 and dt.weekday() == 6:
            sender(chat_id, "Всем ДОБРОЕ УТРО!!!")
        time.sleep(60)


# функция для игра в крестики нолики
def tic_tac_toe(id, id1, id2):
    try:
        if id2[:3] == '[id':
            p1, p2 = id1, int(id2.split('|')[0][3:])
        elif isdigit(id2):
            p1, p2 = id1, int(id2)
        else:
            sender(id, 'Последним должны быть число (id противника) либо ссылка на него через @')
            return
    except ValueError:
        sender(id, 'Последним должны быть число (id противника) либо ссылка на него через @')
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


# функция для отправки мема с пабло
def pablo(id):
    try:
        vk_session.method('messages.send', {
            'chat_id': id,
            'attachment': 'audio529651364_456239047',
            'random_id': 0})
    except ApiHttpError:
        sender(id, 'не хочю')
    except ApiError:
        sender(id, 'слишком длинный ответ')


# функция для отправки сообщения с курсом валюты
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


# функция для запросса в википедию
def wiki(id, msg):
    wikipedia.set_lang('ru')
    try:
        sender(id, wikipedia.page(' '.join(msg)).content.split('==')[0][:4096])
    except wikipedia.exceptions.DisambiguationError:
        sender(id, 'В скобках укажите тип желаемого запроса')
    except wikipedia.exceptions.PageError:
        sender(id, 'Некорректный запрос')


# функция для отправки дня недели в указанный день
def weekday(id, msg):
    dn = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    try:
        if len(msg) == 2:
            sender(id, dn[datetime.strptime(msg[-1], "%d.%m.%Y").weekday()])
        else:
            raise ValueError
    except ValueError:
        sender(id, 'Неверный формат даты')


# функция для отправки даты которая будет через указанное количство дней
def through(id, msg):
    try:
        if isdigit(msg):
            sender(id, date.today() + timedelta(days=int(msg)))
        else:
            sender(id, 'После слова !через должно быть число')
    except ValueError:
        sender(id, 'После слова !через должно быть число')


# функция для проверки строки - может ли она быть числом
def isdigit(test_str: str):
    return test_str[-1].isdigit() or (test_str[-1][0] == '-' and test_str[-1][1:].isdigit())


# функция для нахождения производной
def derivative(id, msg):
    try:
        if len(msg) == 1:
            sender(id, 'Укажи функцию после главного слова\n' +
                   'А ткже можешь найти значение производной в точке Хo черз запятую')
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
        sender(id, 'Что ты написал? Я не понял')


# функция для отправки касательной к графику
def tangent(id, msg):
    try:
        if len(msg) == 1:
            sender(id, 'Укажи функцию после главного слова и точку Хo через которую проходит касательная')
            return
        if isdigit(msg[-1]):
            expr = sympify(' '.join(msg[1:-1]))
            pr = expr.diff()
            x = Symbol('x')
            fx = expr.subs(x, int(msg[-1]))
            fsx = pr.subs(x, int(msg[-1]))
            ans = fx + fsx * (x - int(msg[-1]))
            sender(id, f'y = {expand(ans)}')
        else:
            sender(id, 'Последним должно быть число')
    except ValueError:
        sender(id, 'Что ты написал? Я не понял')


# функция для отправки клавиатуры в главном меню
def regular_keyboard(text: str, id: int):
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


# функция для отправки клавиатуры в магазине заводов
def surrender_keyboard(text: str, house: str, lvl: int, id: int):
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


# функция для отправки клавиатуры в магазине улучшений
def store_keyboard(text: str, id: int):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('прокачка !спам', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()

    keyboard.add_button('неАСУ', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Обращения', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Таблицы', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()

    keyboard.add_button('Выход', color=VkKeyboardColor.SECONDARY)

    vk.messages.send(
        peer_id=id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=text
    )


# функция для отправки клавиатуры по прокачке спама
def spam_keyboard(text, id):
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


# функция для улучшения спама
def spam_pumping(lvl, id):
    if lvl == 8:
        spam_keyboard('У тебя максимальный уровень', id)
    else:
        con = sqlite3.connect('data/rich.db')
        cur = con.cursor()
        res = cur.execute('''SELECT score, spam FROM money WHERE user_id = ?''', (id,)).fetchone()
        if [*res][0] >= lvl * 1000:
            cur.execute('''UPDATE money
            SET score = ?
            WHERE user_id = ?''', ([*res][0] - lvl * 1000, id))
            cur.execute('''UPDATE money
            SET spam = ?
            WHERE user_id = ?''', (lvl, id))
            con.commit()
            con.close()
            spam_keyboard(f'Твой уровень: {lvl + 1} \nСтоимость улучшения:{(lvl + 1) * 1000}', id)
        else:
            spam_keyboard('У тебя недостаточно средств', id)


# функция для отправки клавиатуры в беседу
def keyboard(id, msg=None):
    keyboard = VkKeyboard(one_time=False)

    if msg != []:
        keyboard.add_button(' '.join(msg), color=VkKeyboardColor.NEGATIVE)

        keyboard.add_line()

    keyboard.add_button('!пабло', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('!праздник', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('!топ', color=VkKeyboardColor.POSITIVE)

    keyboard.add_line()

    keyboard.add_button('!курс', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('!нг', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('!бен', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()

    keyboard.add_button('!анекдот', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('!помощь', color=VkKeyboardColor.SECONDARY)

    vk_session.method('messages.send', {
        'chat_id': id,
        'message': 'ну держи',
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard()})


# функция для покупки завода
def buy_factory(zav, id):
    con = sqlite3.connect('data/rich.db')
    cur = con.cursor()
    res = cur.execute('''SELECT * FROM factories''').fetchall()
    h = {i[1]: i[2:] for i in [*res]}
    factory = list(h.keys()).index(zav)
    res = cur.execute('''SELECT level FROM levels WHERE user_id = ?''', (id,)).fetchone()
    lvl = [*res][0].split()
    res = cur.execute('''SELECT score FROM money WHERE user_id = ?''', (id,)).fetchone()
    if res is None:
        new_user(id)
        buy_factory(zav, id)
    money = [*res][0]
    if (int(lvl[factory]) < 3) and (money >= h[zav][3 + int(lvl[factory])]):
        cur.execute('''UPDATE money
SET score = ?
WHERE user_id = ?''', (money - h[zav][3 + int(lvl[factory])], id))
        lvl[factory] = str(int(lvl[factory]) + 1)
        cur.execute('''UPDATE levels
SET level = ?
WHERE user_id = ?''', (' '.join(lvl), id))
        con.commit()
        con.close()
        if int(lvl[factory]) == '1':
            surrender_keyboard(f'Вы преобрели {zav}', zav, int(lvl[factory]), id)
        else:
            surrender_keyboard('Уровень повышен', zav, int(lvl[factory]), id)
    elif int(lvl[factory]) == 3:
        surrender_keyboard('Это здание максимального уровня', zav, 3, id)
    else:
        surrender_keyboard('Недостаточно средств', zav, int(lvl[factory]), id)


# функция для отправки клавиатуры по покупки таблицы
def table_keyboard(text, id):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Преобрести', color=VkKeyboardColor.POSITIVE)

    keyboard.add_line()

    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    vk.messages.send(
        peer_id=id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=text
    )


# функция для покупки таблицы
def buy_table(id):
    con = sqlite3.connect('data/rich.db')
    cur = con.cursor()
    res = cur.execute('''SELECT score FROM money WHERE user_id = ?''', (id,)).fetchone()
    money = [*res][0]
    vk.messages.send(
        peer_id=id,
        random_id=get_random_id(),
        attachment='doc-209322786_635506087'
    )
    if money >= 4321:
        cur.execute('''UPDATE money
        SET score = ?
        WHERE user_id = ?''', (money - 4321, id))
        con.commit()

    else:
        sender(id, 'У вас недостаточно средств')
    con.close()


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
                con = sqlite3.connect('data/top.db')
                cur = con.cursor()
                res = cur.execute('''SELECT user_id, score FROM top
                WHERE chat_id = ?''', (id,))
                top = {i[0]: i[1] for i in [*res]}
                if us in top:
                    top[us] += 1
                    cur.execute('''UPDATE top
                SET score = ?
                WHERE user_id = ? AND chat_id = ?''', (top[us], us, id))
                else:
                    cur.execute('INSERT INTO top(score, user_id, chat_id) VALUES(1, ?, ?)', (us, id))
                    top[us] = 1
                con.commit()
                con.close()
                sor_tup = sorted(top.items(), key=lambda item: item[1], reverse=True)
                sor_top = {k: v for k, v in sor_tup}
                msg = msg.split()
                if "action" in event.object.message:
                    if event.object.message['action']['type'] == 'chat_kick_user':
                        sender(id, 'F')
                    if event.object.message['action']['type'] == 'chat_invite_user':
                        sender(id, 'Прииивеееееет!!!')
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
        
!реши - бот решит математическое выражение,
которое было написано после ключевого слова.
        
!анекдот - отправляет случайный анекдот из бд.
        
!id (n, m) – команда, которая отправит пользователей с id от n до m.
Если не указать n и m тогда отправит первые 100.
        
!число n m (k) – отправляет случайное число от n до m (с шагом k).
        
!нг – команда, которая выводит сколько времени осталось до нового года.

!добавить s - добавляет анекдота s в бд.

!праздник - команда, выводящая 10 сегодняшних праздников

!дуэль (!крестики-нолики, !кн) id[или ссылка через @] - запускается игра крестики-нолики,
в которую вы играете человеком, айди которого указан после ключевого
слова (айди указывать только цифрами).
 
!курс - команда выводит курс евро и доллара. Курсы берутся с 
официального сайта Центрального Банка России.
 
!вики (запрос) - поиск на Википедии введённого запроса (писать без скобок).

!когда ДД.ММ.ГГГГ - команда, которая выводит точное время 
до указанной даты (дата пишется именно в указанном формате).

!день ДД.ММ.ГГГГ - выводит день недели, который будет в указанную дату

!через x - Бот присылает точную дату, которая будет через x дней (писать без скобок).

!бен (комментарий) - схож с командой !выбор, но выводит либо yes, либо no, либо ho-ho-ho, либо uue.

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
                            random_word(id, msg[1:])
                        elif msg[0] == '!топ':
                            sender(id, '\n'.join([vk.users.get(user_ids=i)[0]['first_name'] + ': ' + str(sor_top[i])
                                                  for i in sor_top]))
                        elif msg[0] == '!спам':
                            th = Thread(target=spam, args=(id, msg, us))
                            th.start()
                        elif msg[0] == '!реши':
                            task(id, msg[1:])
                        elif msg[0] == '!анекдот':
                            joke(id)
                        elif msg[0] == '!когда':
                            if len(msg) == 2:
                                when(id, msg[1])
                            else:
                                sender(id, 'Я не ИИ чтобы додуматься что ты хочешь)')
                        elif msg[0] == '!id':
                            try:
                                if len(msg) == 1:
                                    id_vk(id)
                                elif len(msg) == 3:
                                    if int(msg[1]) < int(msg[2]):
                                        id_vk(id, int(msg[1]), int(msg[2]))
                                    else:
                                        raise ValueError
                                else:
                                    raise ValueError
                            except ValueError:
                                sender(id, 'нормально попроси')
                        elif msg[0] == '!число':
                            number(id, msg[1:])
                        elif msg[0] == '!нг':
                            ng(id)
                        elif msg[0] == '!добавить':
                            new_joke(msg[1:], id)
                        elif msg[0] == '!праздник':
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
                            through(id, msg[1])
                        elif msg[0] == '!клава':
                            keyboard(id, msg[1:])
                        elif msg[0] == '!бен':
                            if ' '.join(msg[1:]).lower() == 'do you love god?':
                                sender(id, 'no')
                            else:
                                random_word(id, ['yes', 'no', 'ho-ho-ho', 'uue'])
                        elif msg[0] == '!производная':
                            derivative(id, msg)
                        elif msg[0] == '!касательная':
                            tangent(id, msg)
                    except IndexError:
                        pass
            elif event.from_user:
                msg = event.object.message['text']
                id = event.obj.message['from_id']
                user = vk.users.get(user_ids=id)[0]
                con = sqlite3.connect('data/rich.db')
                cur = con.cursor()
                building = [i[0] for i in cur.execute('''SELECT building FROM factories''').fetchall()]
                if msg == 'Баланс':
                    res = cur.execute('''SELECT score, booster FROM money WHERE user_id = ?''', (id,)).fetchone()
                    con.close()
                    regular_keyboard(f'Ваш баланс {res[0]} \nБустер: {res[1]}', id)

                elif msg == 'Бусты':
                    regular_keyboard('В разработке', id)

                elif msg == 'Здания':
                    res = cur.execute('''SELECT page FROM money WHERE user_id = ?''', (id,)).fetchone()
                    page = [*res][0]
                    res = cur.execute('''SELECT * FROM factories''').fetchall()
                    h = {i[1]: i[2:] for i in [*res]}
                    house = [*res][page % len([*res])][1]
                    factory = list(h.keys()).index(house)
                    res = cur.execute('''SELECT level FROM levels WHERE user_id = ?''', (id,)).fetchone()
                    con.close()
                    lvl = [*res][0].split()
                    surrender_keyboard(house + f': \nЦена: {h[house][-3 + int(lvl[factory])]}', house, int(lvl[factory]), id)

                elif msg == '--->':
                    res = cur.execute('''SELECT page FROM money WHERE user_id = ?''', (id,)).fetchone()
                    page = [*res][0]
                    page += 1
                    cur.execute(f'''UPDATE money
                    SET page = {page}
                    WHERE user_id = {id}''')
                    con.commit()
                    res = cur.execute('''SELECT * FROM factories''').fetchall()
                    h = {i[1]: i[2:] for i in [*res]}
                    house = [*res][page % len([*res])][1]
                    factory = list(h.keys()).index(house)
                    res = cur.execute('''SELECT level FROM levels WHERE user_id = ?''', (id,)).fetchone()
                    lvl = [*res][0].split()
                    surrender_keyboard(house + f': \nЦена: {h[house][-3 + int(lvl[factory])]}', house, int(lvl[factory]), id)

                elif msg == '<---':
                    res = cur.execute('''SELECT page FROM money WHERE user_id = ?''', (id,)).fetchone()
                    page = [*res][0]
                    page -= 1
                    cur.execute(f'''UPDATE money
                    SET page = {page}
                    WHERE user_id = {id}''')
                    con.commit()
                    res = cur.execute('''SELECT * FROM factories''').fetchall()
                    h = {i[1]: i[2:] for i in [*res]}
                    house = [*res][page % len([*res])][1]
                    factory = list(h.keys()).index(house)
                    res = cur.execute('''SELECT level FROM levels WHERE user_id = ?''', (id,)).fetchone()
                    lvl = [*res][0].split()
                    surrender_keyboard(house + f': \nЦена: {h[house][-3 + int(lvl[factory])]}', house, int(lvl[factory]), id)

                elif msg in building:
                    buy_factory(msg, id)

                elif msg == 'Магазин улучшений':
                    store_keyboard('Выбирай с умом', id)

                elif msg == 'прокачка !спам':
                    res = cur.execute('''SELECT spam FROM money WHERE user_id = ?''', (id,)).fetchone()
                    spam_keyboard(f'Твой уровень: {[*res][0] + 1} \nСтоимость улучшения:{([*res][0] + 1) * 1000}', id)

                elif msg == 'Назад':
                    store_keyboard('Пожалуйста', id)

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
                    res = cur.execute('''SELECT spam FROM money WHERE user_id = ?''', (id,)).fetchone()
                    spam_pumping([*res][0] + 1, id)

                elif msg == 'Получить прибыль':
                    res = cur.execute('''SELECT level FROM levels WHERE user_id = ?''', (id,)).fetchone()
                    lvl = [*res][0].split()
                    res = cur.execute('''SELECT score, booster, date FROM money WHERE user_id = ?''', (id,)).fetchone()
                    money = [*res]
                    res = cur.execute('''SELECT * FROM factories''').fetchall()
                    h = {i[1]: i[2:] for i in [*res]}
                    last_data = datetime.strptime(
                        '.'.join([str(money[2]), str(datetime.now().month), str(datetime.now().year)]),
                        "%d.%m.%Y")
                    if last_data.date() == datetime.now().date():
                        regular_keyboard('Ты сегодня уже получал прибыль', id)
                    elif lvl == ['0' for _ in range(len(h))]:
                        regular_keyboard('Тебе нечего получать', id)
                    else:
                        cur.execute('''UPDATE money
                        SET date = ?
                        WHERE user_id = ?''', (datetime.now().day, id))
                        sum_money = 0
                        for i, j in enumerate(lvl):
                            if j != '0':
                                sum_money += int([*res][i][int(j) + 1])
                        sum_money *= money[1]
                        money[0] += round(sum_money)
                        cur.execute('''UPDATE money
                        SET score = ?
                        WHERE user_id = ?''', (money[0], id))
                        con.commit()
                        regular_keyboard(f'Ты получил прибыль: {round(sum_money)}', id)

                elif msg == 'Выход':
                    regular_keyboard('Главное меню', id)

                elif msg == 'Таблицы':
                    table_keyboard('Цена 4321', id)

                elif msg == 'Преобрести':
                    buy_table(id)

                elif msg == 'Начать':
                    res = cur.execute('''SELECT spam FROM money WHERE user_id = ?''', (id,)).fetchone()
                    if res is None:
                        cur.execute(
                            f'''INSERT INTO money(user_id, score, spam, booster, page, date) VALUES({id}, 50, 0, 1, 0,
{datetime.now().day - 1})''')
                        cur.execute(
                            f'''INSERT INTO levels(user_id, level) VALUES({id},
                             "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0") ''')
                        con.commit()
                        regular_keyboard('Дароу новый богачъ', id)
                con.close()


if __name__ == '__main__':
    th = Thread(target=start, args=())
    th.start()
    chat_ids = [i for i in range(1, 100)]
    for chat_id in chat_ids:
        th = Thread(target=good_morning_and_good_night, args=(chat_id, ))
        th.start()
