import asyncio
import config
import os
import requests
import db
import logging
from request import *

from aiogram import Bot, Dispatcher, types, executor

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, ParseMode

from commands import Commands


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename='logs/script.log'
)

def log_info(info):
    print(info)
    logging.log(logging.INFO, info)


cmds = Commands()
commandInfo = []

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot=bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.row(KeyboardButton("/sendfile"), KeyboardButton("/restartconsole"), KeyboardButton("/stopallbot"))
kb.row(KeyboardButton("/listip"),KeyboardButton("/addip"),KeyboardButton("/removeip"))

def is_white(username):
    """Проверяет есть ли username в списке людей которые могут пользоваться ботом"""

    if username in config.white_list:
        return True

    return False

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Обработчик команды /start"""
    username = message.chat.username

    # Проверяем, может ли этот пользователь пользоваться ботом
    if is_white(username) == False:
        await message.answer("Вы кто?")
        return

    global commandInfo
    await dp.bot.set_my_commands(commandInfo)
    await message.answer("Продолжайте работу", reply_markup=kb)

nextstep = False
@dp.message_handler()
async def message_handler(message: types.Message):
    """Обработчик сообщений в чатах"""
    username = message.chat.username

    # Проверяем, может ли этот пользователь пользоваться ботом
    if is_white(username) == False:
        return

    global nextstep
    if nextstep == "photo_or_doc_handler":
        nextstep = False
        await bot.send_message(message.chat.id, "Это не файл, если хотите скинуть файл снова отправьте команду /sendfile и отправляйте файл")
    elif nextstep == "add_ip_list":
        await add_ip_list(None, message)
    elif nextstep == "remove_ip_list":
        await remove_ip_list(None, message)
    elif nextstep == "restartconsole":
        await restartconsole(None, message)
    elif nextstep == "killallrbx":
        await killallrbx(None, message)
    elif nextstep == "getlogs":
        await getlogs(None, message)
    else:
        await cmds.message_handler(message)

@dp.message_handler(content_types=['photo', 'document'])
async def photo_or_doc_handler(message: types.Message):
    global nextstep

    if nextstep == "photo_or_doc_handler":
        nextstep = False
        await message.document.download(destination_file=f"docs/{message.document.file_name}")

        ips = db.get_ips()
        for item in ips:
            try:
                c = requests.Session()
                response = c.post(
                        headers={"Authorization": f'Bearer {config.ACCESS_TOKEN}'},
                        url=f"http://{item[0]}:5000/bots/sendfile",
                        files = {'file': (message.document.file_name, open(f"docs/{message.document.file_name}", 'rb'))},
                        allow_redirects=False
                    )
                if response.ok:
                    log_info(f"{message.chat.username} - command:sendfile IP:{item[0]} File:{message.document.file_name} Status:Success")
                    await bot.send_message(message.chat.id, f"{item[0]} {response.json()}")
                else:
                    await bot.send_message(message.chat.id, "error: "+item[0])
            except:
                await bot.send_message(message.chat.id, "error2: "+item[0])

def get_ip_list_forall():
    ips = db.get_ips()
    ipl = {}
    pos = 0
    it = 1
    for item in ips:
        if not pos in ipl:
            ipl[pos] = ""
        ipl[pos] += f"{it}. <code>{item[0]}</code>\n"
        it += 1
        if it == 100:
            pos += 1
            it = 1
    return ips, ipl

async def get_ip_list(arguments, message: types.Message):
    ips, ipl = get_ip_list_forall()
    for obj in ipl:
        await bot.send_message(message.chat.id, obj == 0 and f"Список IP (копируется нажатием):\n\n{ipl[obj]}" or f"{ipl[obj]}", 'HTML')

async def add_ip_list(arguments, message: types.Message):
    global nextstep
    if nextstep == "add_ip_list":
        nextstep = False
        db.add_ip(message.text)
        log_info(f"{message.chat.username} - command:/addip IP:{message.text}")
        await bot.send_message(message.chat.id, message.text+" добавлен")
        return

    nextstep = "add_ip_list"
    await bot.send_message(message.chat.id, "Введите IP который нужно добавить")

async def remove_ip_list(arguments, message: types.Message):
    global nextstep
    if nextstep == "remove_ip_list":
        nextstep = False
        db.remove_ip(message.text)
        log_info(f"{message.chat.username} - command:/removeip IP:{message.text}")
        await bot.send_message(message.chat.id, message.text+" удалён")
        return
    nextstep = "remove_ip_list"
    await bot.send_message(message.chat.id, "Введите IP который нужно удалить")

async def sendfile(arguments, message: types.Message):
    global nextstep
    nextstep = "photo_or_doc_handler"
    await bot.send_message(message.chat.id, "Отправьте файл скрипта")

async def restartconsole(arguments, message: types.Message):
    global nextstep        
    ips, ipl = get_ip_list_forall()
    if nextstep == "restartconsole":
        nextstep = False
        for item in ips:
            if message.text == "all" or message.text == item[0]:
                log_info(f"{message.chat.username} - command:/restartconsole IP:{item[0]}")
                try:
                    c = requests.Session()
                    response = c.post(
                            headers={"Authorization": f'Bearer {config.ACCESS_TOKEN}'},
                            url=f"http://{item[0]}:5000/bots/restartconsole",
                            allow_redirects=False
                        )
                    await bot.send_message(message.chat.id, response.json()["msg"])
                except:
                    pass
        return True
    nextstep = "restartconsole"
    for obj in ipl:
        await bot.send_message(message.chat.id, obj == 0 and f"Выберите IP сервера консоль которого нужно рестартить:\n\n<code>all</code> (Если все)\n{ipl[obj]}" or f"{ipl[obj]}", 'HTML')

async def killallrbx(arguments, message: types.Message):
    global nextstep        
    ips, ipl = get_ip_list_forall()
    if nextstep == "killallrbx":
        nextstep = False
        _string = ""
        for item in ips:
            if message.text == "all" or message.text == item[0]:
                log_info(f"{message.chat.username} - command:/killallrbx IP:{item[0]}")
                try:
                    c = requests.Session()
                    response = c.post(
                            headers={"Authorization": f'Bearer {config.ACCESS_TOKEN}'},
                            url=f"http://{item[0]}:5000/bots/killallrbx",
                            allow_redirects=False
                        )
                    if response.ok:
                        _string += f"{message.chat.username} - {message.text} IP:{item[0]} Status:Success"
                    else:
                        _string += f"Error: {item[0]}"
                except Exception as e:
                    _string += f"Exception: {item[0]} - {e}"
                    print(f"Unknown exception:\nClass - {e.__class__}\nData - {e}")
        
        _string = [_string[x:x+4096] for x in range (0, len(_string), 4096)]
        for string in _string:
            await bot.send_message(message.chat.id, string)
        return True
    nextstep = "killallrbx"
    for obj in ipl:
        await bot.send_message(message.chat.id, obj == 0 and f"Выберите IP сервера на котором нужно остановить процессы роблокс:\n\n<code>all</code> (Если все)\n{ipl[obj]}" or f"{ipl[obj]}", 'HTML')

getlogs_info = {
    "ip": None,
    "login": None
}
async def getlogs(arguments, message: types.Message):
    global nextstep
    ips, ipl = get_ip_list_forall()
    if nextstep == "getlogs":
        if getlogs_info.get("ip"):
            getlogs_info.update({"login": message.text})
            nextstep = False

            ip = getlogs_info.get("ip")
            login = getlogs_info.get("login")
            try:
                c = requests.Session()
                response = c.post(
                        headers={"Authorization": f'Bearer {config.ACCESS_TOKEN}'},
                        url=f"http://{ip}:5000/bots/getlogs",
                        allow_redirects=False,
                        json={'login': login}
                    )
                if response.ok:
                    await bot.send_document(message.chat.id, (f"{login}.log", response.text))
                else:
                    await bot.send_message(message.chat.id, f"Response error: {response.json()['msg']}")
            except Exception as e:
                print(e)
                await bot.send_message(message.chat.id, f"Error: {e}")
            getlogs_info.update({"ip": None})
        else:
            for item in ips:
                if message.text == item[0]:
                    getlogs_info.update({"ip": message.text})
                    await bot.send_message(message.chat.id, f"Введите логин бота логи которого хотите скачать")
                    return
            await bot.send_message(message.chat.id, f"Такой IP отсутствует, начните сначала: /getlogs")
            nextstep = False
                    
        return
    nextstep = "getlogs"
    for obj in ipl:
        await bot.send_message(message.chat.id, obj == 0 and f"Выберите IP сервера с которого планируете взять логи:\n\n{ipl[obj]}" or f"{ipl[obj]}", 'HTML')
        

async def stopallbot(arguments, message: types.Message):
    ips = db.get_ips()
    _string = ""
    for item in ips:
        try:
            c = requests.Session()
            response = c.post(
                    headers={"Authorization": f'Bearer {config.ACCESS_TOKEN}'},
                    url=f"http://{item[0]}:5000/bots/stopallbot",
                    allow_redirects=False
                )
            
            if response.ok:
                log_info(f"{message.chat.username} - stopallbot IP:{item[0]} Status:Success")
                _string += f"{message.chat.username} - stopallbot IP:{item[0]} Status:Success"
            else:
                _string += f"Responce error: {item[0]}"
        except Exception as e:
            _string += f"Error: {e}"
        
    _string = [_string[x:x+4096] for x in range (0, len(_string), 4096)]
    for string in _string:
        await bot.send_message(message.chat.id, string)
    
async def update(arguments, message: types.Message):
    update_n = message.text == "/updateroblox" and "roblox" or "synapse"
    
    ips = db.get_ips()
    _string = ""
    for item in ips:
        try:
            response = request(config.ACCESS_TOKEN, f"http://{item[0]}:5000/bots/update/{update_n}")
            if response.ok:
                log_info(f"{message.chat.username} - {message.text} IP:{item[0]} Resp:{response} Status:Success")
                _string += f"{message.chat.username} - {message.text} IP:{item[0]} Status:Success"
            else:
                _string += f"Responce error: {item[0]}"
        except Exception as e:
            _string += f"Error: {e}"
    
    _string = [_string[x:x+4096] for x in range (0, len(_string), 4096)]
    for string in _string:
        await bot.send_message(message.chat.id, string)

async def test_server(arguments, message: types.Message):
    ips = db.get_ips()
    it = 1
    _string = ""
    for item in ips:
        self_req = request(config.ACCESS_TOKEN, f"http://{item[0]}:5000/")
        if self_req.error:
            _string += f"{it}. {item[0]}: {self_req.error}"
        else:
            _string += f"{it}. {item[0]}: Server online"
        it += 1
    
    _string = [_string[x:x+4096] for x in range (0, len(_string), 4096)]
    for string in _string:
        await bot.send_message(message.chat.id, string)

def main():
    for dir in ["logs", "docs"]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    global cmds
    global commandInfo

    cmds.add_command("/sendfile", 0, None, sendfile, "Отправить файл")
    cmds.add_command("/restartconsole", 0, None, restartconsole, "Перезапустить консоль веб сервера")
    cmds.add_command("/stopallbot", 0, None, stopallbot, "Остановить всех ботов")
    cmds.add_command("/killallrbx", 0, None, killallrbx, "Выключить все процесы роблокс")
    cmds.add_command("/listip", 0, None, get_ip_list, "Список веб серверов")
    cmds.add_command("/addip", 0, None, add_ip_list, "Добавить IP веб сервера")
    cmds.add_command("/removeip", 0, None, remove_ip_list, "Удалить IP веб сервера")
    cmds.add_command("/updateroblox", 0, None, update, "Обновить Роблокс")
    cmds.add_command("/updatesynapse", 0, None, update, "Обновить синапс")
    cmds.add_command("/getlogs", 0, None, getlogs, "Download logs")
    
    cmds.add_command("/test", 0, None, test_server, "Для тестирования ответов от серверов")
    
    commands = cmds.get_commands()
    for item in commands:
        commandInfo.append(types.BotCommand(commands[item][0], commands[item][4]))
    
    executor.start_polling(dp)

if __name__ == '__main__':
    main()