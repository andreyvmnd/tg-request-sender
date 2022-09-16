from aiogram import Bot, Dispatcher, types, executor

class Commands:
    funcs = {}
    chats = {}

    def __init__(self):
        """Инициализация класса"""
        return

    def command_exist(self, name):
        """Проверяет есть ли команда в списке"""
        for i in self.funcs.items():
            if i[1][0] == name:
                return True

        return False

    def get_command_info(self, name):
        """Возвращает информацию по команде"""
        for i in self.funcs.items():
            if i[1][0] == name:
                return i[1]

        return None

    def add_command(self, name, count_args, messages, callback, description):
        """Добавить команду"""
        self.funcs[len(self.funcs)] = [name, count_args, messages, callback, description]

    def set_function(self, chat, name):
        """Установить текущую команду"""
        chat.update({"function_name": name})
        chat.update({"arg_number": 0})
        chat.update({"arguments": []})

    async def message_handler(self, message: types.Message) -> None:
        """Обработчик сообщений чтобы отлавливать команды"""
        chat_id = message.chat.id # Берём id чата
        chat = self.chats.get(chat_id)

        if chat == None:
            self.chats[chat_id] = {}
            chat = self.chats.get(chat_id)

        reply_message = ""

        if self.command_exist(message.text):
            cmd_info = self.get_command_info(message.text)

            if cmd_info[1] == 0:
                self.set_function(self.chats[chat_id], "")
                await cmd_info[3]([], message)
                return

            self.set_function(self.chats[chat_id], message.text)
            await message.answer(cmd_info[2][0])
            return

        # Какую функцию сейчас использует пользователь
        function_name = chat.get("function_name")
        # На каком аргументе функции пользователь находится
        arg_number = chat.get("arg_number")
        # все аргументы которые пользователь ввёл
        arguments = chat.get("arguments")

        if self.command_exist(function_name):
            
            cmd_info = self.get_command_info(function_name)

            arguments.append(message.text or message.document)

            arg_number += 1

            if arg_number == cmd_info[1]:
                await cmd_info[3](arguments, message)
                self.set_function(self.chats[chat_id], "")
            else:
                reply_message = cmd_info[2][arg_number]
                self.chats[chat_id].update({"arguments": arguments})
                self.chats[chat_id].update({"arg_number": arg_number})

        if len(reply_message) != 0:
            await message.answer(reply_message)
