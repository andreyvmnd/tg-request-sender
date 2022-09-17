import config
import os
import db
import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
        
async def sendfile(arguments, message: types.Message):
    await arguments[0].download(destination_file=f"docs/{arguments[0].file_name}")

    ips = db.get_ips()
    _string = ""
    for i, item in enumerate(ips):

        self_req = request(config.ACCESS_TOKEN, f"http://{item[0]}:5000/bots/sendfile", files= {'file': (arguments[0].file_name, open(f"docs/{arguments[0].file_name}", 'rb'))})
                
        server_message = self_req.error and "Server offline or down" or f"[{message.chat.username}] sendfile; file:{arguments[0].file_name} response:{self_req.response}"

        _string += log_info(f"{i}. {item[0]}: {server_message}\n")
    
    for string in [_string[x:x+4096] for x in range (0, len(_string), 4096)]:
        await message.answer(string)

def get_ip_list_forall():
    ips, ipl = db.get_ips(), {}
    for i, item in enumerate(ips, 1):
        pos = 0 if i < 101 else int(str(i)[0])
        if not pos in ipl:
            ipl[pos] = ""
        ipl[pos] += f"{i}. <code>{item[0]}</code>\n"
    return ips, ipl

async def get_ip_list(arguments, message: types.Message):
    ips, ipl = get_ip_list_forall()
    for obj in ipl:
        await message.answer(obj == 0 and f"Список IP (копируется нажатием):\n\n{ipl[obj]}" or f"{ipl[obj]}", 'HTML')

async def add_ip_list(arguments, message: types.Message):
    db.add_ip(arguments[0])
    _string = log_info(f"{arguments[0]}: [{message.chat.username}] addip")
    await message.answer(_string)

async def remove_ip_list(arguments, message: types.Message):
    db.remove_ip(arguments[0])
    _string = log_info(f"{arguments[0]}: [{message.chat.username}] removeip")
    await message.answer(_string)

async def restartconsole(arguments, message: types.Message):
    ips, ipl = get_ip_list_forall()
    _string = ""
    for i, item in enumerate(ips, 1):
        if arguments[0] == "all" or arguments[0] == item[0]:
            self_req = request(config.ACCESS_TOKEN, f"http://{item[0]}:5000/bots/restartconsole")
            
            server_message = self_req.error and "Server offline or down" or f"[{message.chat.username}] restartconsole; response:{self_req.response}"

            _string += log_info(f"{i}. {item[0]}: {server_message}\n")

    for string in [_string[x:x+4096] for x in range (0, len(_string), 4096)]:
        await message.answer(string)

async def killallrbx(arguments, message: types.Message):
    ips, ipl = get_ip_list_forall()
    _string = ""
    for i, item in enumerate(ips, 1):
        if arguments[0] == "all" or arguments[0] == item[0]:
            self_req = request(config.ACCESS_TOKEN, f"http://{item[0]}:5000/bots/killallrbx")

            server_message = self_req.error and "Server offline or down" or f"[{message.chat.username}] killallrbx; response:{self_req.response}"

            _string += log_info(f"{i}. {item[0]}: {server_message}\n")
    
    for string in [_string[x:x+4096] for x in range (0, len(_string), 4096)]:
        await message.answer(string)
    

async def getlogs(arguments, message: types.Message):
    ip, login = arguments[0], arguments[1]
    _string = ""

    if db.ip_exist(ip):
        self_req = request(config.ACCESS_TOKEN, f"http://{ip}:5000/bots/getlogs", json={'login': login})

        server_message = self_req.error and "Server offline or down" or f"[{message.chat.username}] getlogs; response:{self_req.response}"

        _string += log_info(f"{ip}: {server_message}\n")

        await bot.send_document(message.chat.id, (f"{login}.log", self_req.response.text))

        for string in [_string[x:x+4096] for x in range(0, len(_string), 4096)]:
            await message.answer(string)

    await message.answer(f"Такой IP отсутствует, начните сначала: /getlogs")
        
async def stopallbot(arguments, message: types.Message):
    ips = db.get_ips()
    _string = ""
    for it, item in enumerate(ips, 1):
        self_req = request(config.ACCESS_TOKEN, f"http://{item[0]}:5000/bots/stopallbot")

        server_message = self_req.error and "Server offline or down" or f"[{message.chat.username}] stopallbot; response:{self_req.response}"
        _string += log_info(f"{it}. {item[0]}: {server_message}\n")
        
    for string in [_string[x:x+4096] for x in range(0, len(_string), 4096)]:
        await message.answer(string)
    
async def update(arguments, message: types.Message):
    update_n = message.text == "/updateroblox" and "roblox" or "synapse"
    ips = db.get_ips()
    _string = ""

    for it, item in enumerate(ips, 1):
        self_req = request(config.ACCESS_TOKEN, f"http://{item[0]}:5000/bots/update/{update_n}")

        server_message = self_req.error and "Server offline or down" or f"[{message.chat.username}] update {update_n}; response:{self_req.response}"
        _string += log_info(f"{it}. {item[0]}: {server_message}\n")
    
    for string in [_string[x:x+4096] for x in range(0, len(_string), 4096)]:
        await message.answer(string)

async def test_server(arguments, message: types.Message):
    ips = db.get_ips()
    _string = ""

    for it, item in enumerate(ips, 1):
        self_req = request(config.ACCESS_TOKEN, f"http://{item[0]}:5000/bots/isonline")

        server_message = self_req.error and "Server offline" or "Server online"
        _string += f"{it}. {item[0]}: {server_message}\n"
    
    for string in [_string[x:x+4096] for x in range(0, len(_string), 4096)]:
        await message.answer(string)

def main():
    for dir in ["logs", "docs"]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename='logs/script.log'
    )

    cmds.add_command("/sendfile", 1, ("Отправьте файл скрипта",), sendfile, "Отправить файл")
    cmds.add_command("/restartconsole", 1, ("Выберите IP сервера консоль которого нужно рестартить:\n\n<code>all</code> (Если все)$listServer",), restartconsole, "Перезапустить консоль веб сервера")
    cmds.add_command("/stopallbot", 0, None, stopallbot, "Остановить всех ботов")
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