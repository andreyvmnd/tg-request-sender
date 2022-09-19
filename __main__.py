import os
import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import config
import db
from commands import Commands
from request import *

cmds = Commands()
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot=bot)
kb = ReplyKeyboardMarkup(resize_keyboard=True)

def log_info(info):
    print(info)
    logging.log(logging.INFO, info)

    return info

def is_white(username):
    """Проверяет есть ли username в списке людей которые могут пользоваться ботом"""

    if username in config.white_list:
        return True

    return False

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Обработчик команды /start"""

    # Проверяем, может ли этот пользователь пользоваться ботом
    if is_white(message.chat.username) == False:
        await message.answer("Вы кто?")
        return

    await message.answer("Продолжайте работу", reply_markup=kb)

@dp.message_handler(content_types=['text', 'photo', 'document'])
async def message_handler(message: types.Message):
    """Обработчик сообщений в чатах"""

    # Проверяем, может ли этот пользователь пользоваться ботом
    if is_white(message.chat.username) == False:
        return

    await cmds.message_handler(message)

def get_ip_list_forall():
    ips, ipl = db.get_ips(), {}
    for i, item in enumerate(ips, 1):
        pos = 0 if i < 101 else int(str(i)[0])
        if not pos in ipl:
            ipl[pos] = ""
        ipl[pos] += f"{i}. <code>{item[0]}</code>\n"
    return ipl

async def get_ip_list(arguments, message: types.Message):
    ips, ipl = get_ip_list_forall()
    for obj in ipl:
        await message.answer(f"Список IP (копируется нажатием):\n\n{ipl[obj]}" if obj == 0 else f"{ipl[obj]}", 'HTML')

async def add_ip_list(arguments, message: types.Message):
    db.add_ip(arguments[0])
    _string = log_info(f"[{message.chat.username}] {arguments[0]}: addip")
    await message.answer(_string)

async def remove_ip_list(arguments, message: types.Message):
    db.remove_ip(arguments[0])
    _string = log_info(f"[{message.chat.username}] {arguments[0]}: removeip")
    await message.answer(_string)

async def sendfile(arguments, message: types.Message):
    await arguments[0].download(destination_file=f"docs/{arguments[0].file_name}")
    ips = db.get_ips()

    quickReq = quickrequest(ips, f"http://$ip:5000/bots/sendfile", config.ACCESS_TOKEN, files={'file': (arguments[0].file_name, open(f"docs/{arguments[0].file_name}", 'rb'))})
    quickReq.start()

    _string = quickReq.handler_requests("{i}. ["+message.chat.username+"] {serverIP}: {server_message}\n", "sendfile; file: "+arguments[0].file_name+" message: {response_message}")
    
    for string in _string:
        await message.answer(log_info(string))

async def restartconsole(arguments, message: types.Message):
    ips = db.get_ips()

    ips = ips if arguments[0] == "all" else [(arguments[0],)]
    quickReq = quickrequest(ips, f"http://$ip:5000/bots/isonline", config.ACCESS_TOKEN)
    quickReq.start()

    _string, _torestart = "", []
    for i, item in enumerate(ips, 1):
        if quickReq.list_map[i-1]:
            _torestart.append((item[0],))
        else:
            server_message = f"restartconsole; ERROR: Server is offline"
            _string += log_info(f"{i}. [{message.chat.username}] {item[0]}: {server_message}\n")
            
    quickReq_2 = quickrequest(_torestart, f"http://$ip:5000/bots/restartconsole", config.ACCESS_TOKEN)
    quickReq_2.start()
    for i, item in enumerate(quickReq_2.list, 1):
        req = quickReq_2.list_map[i-1]
        server_message = "SERVER RESTART" if req == None else f"restartconsole; message: {req.json()['msg']}"
        _string += f"{i}. [{message.chat.username}] {item[4]}: {server_message}\n"
    
    for string in [*stringtolist(_string)]:
        await message.answer(log_info(string))
    
async def stopallbot(arguments, message: types.Message):
    ips = db.get_ips()

    quickReq = quickrequest(ips if arguments[0] == "all" else [(arguments[0],)], f"http://$ip:5000/bots/stopallbot", config.ACCESS_TOKEN)
    quickReq.start()

    _string = quickReq.handler_requests("{i}. ["+message.chat.username+"] {serverIP}: {server_message}\n", "stopallbot; message: {response_message}")
        
    for string in _string:
        await message.answer(log_info(string))

async def killallrbx(arguments, message: types.Message):
    ips = db.get_ips()

    quickReq = quickrequest(ips if arguments[0] == "all" else [(arguments[0],)], f"http://$ip:5000/bots/killallrbx", config.ACCESS_TOKEN)
    quickReq.start()

    _string = quickReq.handler_requests("{i}. ["+message.chat.username+"] {serverIP}: {server_message}\n", "killallrbx; message: {response_message}")
    
    for string in _string:
        await message.answer(log_info(string))
    
async def update(arguments, message: types.Message):
    update_n = message.text == "/updateroblox" and "roblox" or "synapse"
    ips = db.get_ips()
    _string = ""

    quickReq = quickrequest(ips, f"http://$ip:5000/bots/update/{update_n}", config.ACCESS_TOKEN)
    quickReq.start(100)

    _string = quickReq.handler_requests("{i}. ["+message.chat.username+"] {serverIP}: {server_message}\n", "update "+update_n+"; message: {response_message}")
    
    for string in _string:
        await message.answer(log_info(string))

async def getlogs(arguments, message: types.Message):
    ip, login = arguments[0], arguments[1]

    if db.ip_exist(ip):
        quickReq = quickrequest(((ip,)), "http://$ip:5000/bots/getlogs", config.ACCESS_TOKEN, json={'login': login})
        quickReq.start()

        _string = quickReq.handler_requests("{i}. ["+message.chat.username+"] {serverIP}: {server_message}\n", "getlogs; message: {response_message}")
        for string in _string:
            await message.answer(log_info(string))
        
        for item in quickReq.list_map:
            if item:
                await bot.send_document(message.chat.id, (f"{login}.log", item.text))
            else:
                message.answer(f"Логи этого бота отсутствуют")

    else:
        await message.answer(f"Такой IP отсутствует, начните сначала: /getlogs")

async def test_server(arguments, message: types.Message):
    ips = db.get_ips()

    quickReq = quickrequest(ips, "http://$ip:5000/bots/isonline", config.ACCESS_TOKEN)
    quickReq.start()

    for string in quickReq.handler_requests("{i}. {serverIP}: {server_message}\n", "online"):
        await message.answer(string)

def main():
    for dir in ["logs", "docs"]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename='logs/script.log')

    cmds.add_command("/sendfile", 1, ("Отправьте файл скрипта",), sendfile, "Отправить файл")
    cmds.add_command("/restartconsole", 1, ("Выберите IP сервера консоль которого нужно рестартить:\n\n<code>all</code> (Если все)$listServer",), restartconsole, "Перезапустить консоль веб сервера")
    cmds.add_command("/stopallbot", 1, ("Выберите IP сервера на котором нужно остановить всех ботов:\n\n<code>all</code> (Если все)$listServer",), stopallbot, "Остановить всех ботов")
    cmds.add_command("/killallrbx", 1, ("Выберите IP сервера на котором нужно остановить процессы роблокс:\n\n<code>all</code> (Если все)$listServer",), killallrbx, "Выключить все процесы роблокс")
    cmds.add_command("/listip", 0, None, get_ip_list, "Список веб серверов")
    cmds.add_command("/addip", 1, ("Введите IP который нужно добавить",), add_ip_list, "Добавить IP веб сервера")
    cmds.add_command("/removeip", 1, ("Введите IP который нужно удалить",), remove_ip_list, "Удалить IP веб сервера")
    cmds.add_command("/updateroblox", 0, None, update, "Обновить Роблокс")
    cmds.add_command("/updatesynapse", 0, None, update, "Обновить синапс")
    cmds.add_command("/getlogs", 2, ("Выберите IP сервера с которого планируете взять логи:$listServer","Введите логин бота логи которого хотите скачать"), getlogs, "Download logs")
    cmds.add_command("/test", 0, None, test_server, "Для тестирования ответов от серверов")
    
    commands = cmds.funcs
    keyboard = []
    for i, item in enumerate(commands):
        keyboard.append(KeyboardButton(commands[item][0]))
        if len(keyboard) == 5 or len(commands) == i+1:
            kb.row(*keyboard)
            keyboard = []
    
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()