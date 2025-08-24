import json
import time
from datetime import datetime
import telebot
import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini',encoding="utf-8")
bot = telebot.TeleBot(cfg['TGSETTINGS']['tokenbot'])
idChat = int(cfg['TGSETTINGS']['chatid'])
idAdmin1 = int(cfg['TGSETTINGS']['adminid1'])
idAdmin2 = int(cfg['TGSETTINGS']['adminid2'])

counter = "Меню"

addBlackList = False
addWhiteList = False
print("Запуск бота успешно")
data = {} #Словарь слов

AntiSpam = {} #антиспам словарь

ManyImages = {} #обработка большого кол-ва картинок
messagetext = ""

postIdImmage = 0
postIdMessage = 0



def update_data():
    global data
    try:
        with open('Data.txt', 'r', encoding='utf-8') as file:  # Заполнение данных в переменную
            d1 = json.load(file)
            data.update(d1)  # Обновление данных
    except json.decoder.JSONDecodeError:
        pass


def write_data():
    open('Data', 'w').close()
    with open('Data.txt', 'w', encoding='utf-8') as file:  # Выгрузка данных в txt файл
        json.dump(data, file, indent=3, ensure_ascii=False)

try:
    @bot.message_handler(content_types=['new_chat_members', 'left_chat_member']) #удаление системных сообщений
    def deleteSystemIvent(message):
        bot.delete_message(message.chat.id, message.message_id)
        # try:
        #    if (message.new_chat_members[0] != None):
        #        bot.send_message(message.chat.id, f"{message.new_chat_members[0].first_name} {messageNewMembers}")
        # except Exception as e:  pass #bot.send_message(message.chat.id,e)




    @bot.message_handler(content_types=['text','photo','video','document'])
    def whiteList(message):
        global data, addWhiteList, addBlackList, counter, postIdImmage, postIdMessage,messagetext, AntiSpam,ManyImages

        if (message.text != None):
            messagetext = message.text.lower()
            print(f"1MessageID: {message.message_id}")
        else:
            if message.caption != None:
                if postIdImmage != message.date:
                    messagetext = message.caption.lower()
                if message.date in ManyImages.keys():
                    ManyImages[message.date] += 1

                else:
                    ManyImages[message.date] = 1
                    print(f"не нашел кей {ManyImages[message.date]}")

                print(f"1MessageID: {message.message_id}")
            elif message.date in ManyImages.keys():
                    ManyImages[message.date] += 1

            elif message.caption == None and postIdImmage != message.date and postIdMessage != 0 and message.from_user.id != idAdmin1 and message.from_user.id != idAdmin2:
                bot.delete_message(message.chat.id, message.message_id)
                m = bot.send_message(message.chat.id,f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> {cfg["TGSETTINGS"]["messageOnlyImage"]}',
                                     parse_mode="HTML")
                time.sleep(10)
                bot.delete_message(m.chat.id, m.message_id)
                return
        ####Антиспам
        postIdMessage = message.message_id
        if messagetext != "":
            if messagetext in AntiSpam.keys() and message.chat.id == idChat and message.from_user.id != idAdmin1 and message.from_user.id != idAdmin2:

                if ((datetime.today() - AntiSpam[messagetext]['date']).seconds / 3600) >= 1 and (message.date in ManyImages.keys() == False):
                    AntiSpam[messagetext] = datetime.today()
                elif (((datetime.today() - AntiSpam[messagetext]['date']).seconds / 3600) < 1 and message.date != AntiSpam[messagetext]['time']):
                    if (message.date in ManyImages.keys()):
                        print(f"ManyImages: {ManyImages[message.date]}\n2MessageID: {message.message_id}\nPostid {postIdMessage}")
                        i = ManyImages[message.date]
                        while i >= 0:
                            try:
                                bot.delete_message(message.chat.id, (postIdMessage-i))
                                print(f"1{postIdMessage} - {i} = {postIdMessage-i}")
                                i -= 1
                            except Exception as e:
                                i -= 1


                        m = bot.send_message(message.chat.id,
                                             f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> {cfg["TGSETTINGS"]["messagespam"]}',
                                             parse_mode="HTML")
                        time.sleep(10)
                        bot.delete_message(m.chat.id, m.message_id)
                        return

                    else:
                        print("шманаем")
                        bot.delete_message(message.chat.id, message.message_id)
                    m = bot.send_message(message.chat.id,
                                         f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> {cfg["TGSETTINGS"]["messagespam"]}',
                                         parse_mode="HTML")
                    time.sleep(10)
                    bot.delete_message(m.chat.id, m.message_id)
                    return

            else:
                print(f"postIdImmage: {postIdImmage} message.date: {message.date}")
                if postIdImmage != message.date and message.chat.id == idChat and message.from_user.id != idAdmin1 and message.from_user.id != idAdmin2:
                    AntiSpam[messagetext] = {"date": datetime.today(), "time": message.date, "quantity": 0}
                    print(f"Добавил {messagetext}")

            postIdImmage = message.date
            ####


            if (message.chat.id == idChat): #беседа

                update_data()
                if len(data) <= 0:
                    data["Стоп слова"] = []
                    data["Разрешенные слова"] = []
                for x in data["Стоп слова"]:
                    try:
                        if (messagetext.find(x.lower())) != -1 and message.from_user.id != idAdmin1 and message.from_user.id != idAdmin2:
                            print(f"\n\nНашел запрещенное слово {messagetext}\n{messagetext.find(x) != -1}")
                            bot.delete_message(message.chat.id, message.message_id)
                            m = bot.send_message(message.chat.id, f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>  {cfg["TGSETTINGS"]["messageBlackWord"]}', parse_mode="HTML")
                            time.sleep(10)
                            bot.delete_message(m.chat.id, m.message_id)
                            del AntiSpam[messagetext]
                            return
                        else:
                            pass
                    except Exception as e:
                        print("Ошибка в запрещенных словах\n",e)
                for x in data["Разрешенные слова"]:

                    if ((messagetext.find(x.lower())) != -1):
                        return
                    elif (data["Разрешенные слова"].index(x) == len(data["Разрешенные слова"])-1) and message.from_user.id != idAdmin1 and message.from_user.id != idAdmin2:
                        try:
                            print(f"\n\nНе нашел разрешенное слово {messagetext} \n{messagetext.find(x) != -1}")
                            bot.delete_message(message.chat.id, message.message_id)
                            m = bot.send_message(message.chat.id, f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> {cfg["TGSETTINGS"]["messageWhiteWord"]}', parse_mode="HTML")
                            time.sleep(10)
                            bot.delete_message(m.chat.id, m.message_id)
                            del AntiSpam[messagetext]
                            return
                        except Exception as e:
                            print("Ошибка в разрешенных словах\n",e)




    ###################################################################################
            elif (message.chat.id == idAdmin1 or message.chat.id == idAdmin2): #ЛС админа

                if messagetext == "добавить":
                    counter = "Добавить"
                    keyboard = telebot.types.ReplyKeyboardMarkup(True)
                    keyboard.row('Стоп слова', 'Разрешенные слова', 'Список', 'Назад')
                    bot.send_message(message.chat.id, "✖️ Добавить Выбор действий", reply_markup=keyboard)

                elif messagetext == "удалить":
                    counter = "Удалить"
                    keyboard = telebot.types.ReplyKeyboardMarkup(True)
                    keyboard.row('Стоп слова', 'Разрешенные слова', 'Список', 'Назад')
                    bot.send_message(message.chat.id, "➖️ Удалить Выбор действий", reply_markup=keyboard)

                elif (counter == "Добавить"):

                    if messagetext == "стоп слова":
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Стоп')
                        bot.send_message(message.chat.id,"✖️ Добавить Отправляйте стоп слова по очереди (каждое слово = 1 сообщение)\n✅ Когда введете все слова нажмите на кнопку Стоп",reply_markup=keyboard)
                        addBlackList = True

                    elif messagetext == "разрешенные слова":
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Стоп')
                        bot.send_message(message.chat.id,"✖️ Добавить Отправляйте разрешенные слова по очереди (каждое слово = 1 сообщение)\n✅ Когда введете все слова нажмите на кнопку Стоп",reply_markup=keyboard)
                        addWhiteList = True

                    elif messagetext == "список":
                        update_data()
                        if len(data) <= 0:
                            data["Стоп слова"] = []
                            data["Разрешенные слова"] = []
                        allowedwords = ', '.join(map(str, data["Разрешенные слова"]))
                        blackdwords = ', '.join(map(str, data["Стоп слова"]))
                        bot.send_message(message.chat.id, f"📃Списки:\n✅Список разрешенных слов: {allowedwords}\n⛔Список стоп слов: {blackdwords} ")

                    elif messagetext == "назад":
                        counter == "Меню"
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Добавить', 'Удалить')
                        bot.send_message(message.chat.id, "Ⓜ️ Меню бота", reply_markup=keyboard)

                    elif messagetext == "стоп":
                        addBlackList = False
                        addWhiteList = False
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Стоп слова', 'Разрешенные слова', 'Список', 'Назад')
                        bot.send_message(message.chat.id, "✖️ Добавить Выбор действий", reply_markup=keyboard)

                    elif messagetext == "назад":
                        counter = "Меню"
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Добавить', 'Удалить')
                        bot.send_message(message.chat.id, "Ⓜ️ Меню бота", reply_markup=keyboard)

                    elif addBlackList:
                        update_data()
                        if len(data) <= 0:
                            data["Стоп слова"] = []
                            data["Разрешенные слова"] = []
                        if messagetext in data["Стоп слова"]:
                            bot.send_message(message.chat.id,"👀 Это слово уже есть в стоп словах")
                        else:
                            data["Стоп слова"].append(messagetext)
                            write_data()
                            bot.send_message(message.chat.id, f"✅ Слово: {messagetext} добавлено в Стоп слова")

                    elif addWhiteList:
                        update_data()
                        if len(data) <= 0:
                            data["Стоп слова"] = []
                            data["Разрешенные слова"] = []
                        if messagetext in data["Разрешенные слова"]:
                            bot.send_message(message.chat.id, "👀 Это слово уже есть в разрешенных словах")
                        else:
                            data["Разрешенные слова"].append(messagetext)
                            write_data()
                            bot.send_message(message.chat.id, f"✅ Слово: {messagetext} добавлено в разрешенные слова")


                elif (counter == "Удалить"):
                    if messagetext == "стоп слова":
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Стоп')
                        bot.send_message(message.chat.id,"➖️ Удалить Отправляйте стоп слова для удаления по очереди (каждое слово = 1 сообщение)\n✅ Когда введете все слова нажмите на кнопку Стоп",
                                         reply_markup=keyboard)
                        addBlackList = True

                    elif messagetext == "разрешенные слова":
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Стоп')
                        bot.send_message(message.chat.id,
                                         "➖️ Удалить Отправляйте разрешенные слова для удаления по очереди (каждое слово = 1 сообщение)\n✅ Когда введете все слова нажмите на кнопку Стоп",
                                         reply_markup=keyboard)
                        addWhiteList = True

                    elif messagetext == "список":
                        update_data()
                        if len(data) <= 0:
                            data["Стоп слова"] = []
                            data["Разрешенные слова"] = []
                        allowedwords = ' ,'.join(map(str, data["Разрешенные слова"]))
                        blackdwords = ' ,'.join(map(str, data["Стоп слова"]))
                        bot.send_message(message.chat.id,f"📃Списки:\n✅Список разрешенных слов: {allowedwords}\n⛔Список стоп слов: {blackdwords} ")

                    elif messagetext == "назад":
                        counter == "Меню"
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Добавить', 'Удалить')
                        bot.send_message(message.chat.id, "Ⓜ️ Меню бота", reply_markup=keyboard)

                    elif messagetext == "стоп":
                        addBlackList = False
                        addWhiteList = False
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Стоп слова', 'Разрешенные слова', 'Список', 'Назад')
                        bot.send_message(message.chat.id, "➖️ Удалить Выбор действий", reply_markup=keyboard)

                    elif messagetext == "назад":
                        counter = "Меню"
                        keyboard = telebot.types.ReplyKeyboardMarkup(True)
                        keyboard.row('Добавить', 'Удалить')
                        bot.send_message(message.chat.id, "Ⓜ️ Меню бота", reply_markup=keyboard)

                    elif addBlackList:
                        update_data()
                        if len(data) <= 0:
                            data["Стоп слова"] = []
                            data["Разрешенные слова"] = []
                        try:
                            data["Стоп слова"].remove(messagetext)
                            write_data()
                            bot.send_message(message.chat.id, f"✅ Слово: {messagetext} удалено из в стоп слов")
                        except:
                            bot.send_message(message.chat.id,f"⚠️Слова {messagetext} нет в стоп словах вы не можете его удалить")


                    elif addWhiteList:
                        update_data()
                        if len(data) <= 0:
                            data["Стоп слова"] = []
                            data["Разрешенные слова"] = []
                        try:
                            data["Разрешенные слова"].remove(messagetext)
                            write_data()
                            bot.send_message(message.chat.id, f"✅ Слово: {messagetext} удалено из разрешенных слов")
                        except:
                            bot.send_message(message.chat.id, f"⚠️Слова {messagetext} нет в разрешенных словах, вы не можете его удалить")
                else:
                    keyboard = telebot.types.ReplyKeyboardMarkup(True)
                    keyboard.row('Добавить', 'Удалить')
                    bot.send_message(message.chat.id, "Ⓜ️ Меню бота", reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, "⛔ Вы не являетесь админом")

except Exception as e:
    print("Ошибка\n",e)
bot.polling(none_stop=True, timeout=25)