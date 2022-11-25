# Валютный телеграм-бот
# Переводит заданное количество средств из одной валюты в другую по актуальному курсу
# (с использованием Currency Data API ресурса apilayer.com)

# Из сопряжённого файла config.py импортируем токен телеграм-бота, а также список всех доступных для перевода валют
# (в формате словаря "краткое название валюты (ключ): полное название валюты (значение)")
from config import TOKEN, currency_keys
# Из сопряжённого файла utils.py импортируем класс ConversionException, ответственный за отлов как пользовательских,
# так и потенциальных системных ошибок (исключений). Кроме того, импортируем класс Conversion, статическими методами
# которого является основной функционал бота: перевод из одной валюты в другую и получение краткого наименования той
# или иной валюты по полному её наименованию (подробнее описаны в файле utils.py)
from utils import ConversionException, Conversion
# Импортируем заранее предустановленную библиотеку telebot, с помощью инструментов которой реализована логика бота
import telebot

# Создаём эксземпляр класса Telebot, присваиваем ему имя bot и инициализируем его с помощью импортированного из
# сопряжённого файла токена бота
bot = telebot.TeleBot(TOKEN)


# Создаём функцию (задекорированную методом бота), отвечающую за пользовательские команды /start и /help (которые
# выводят сообщение с подробной инструкцией о том, как использовать данного бота)
@bot.message_handler(commands=["start", "help"])
def start_help(message: telebot.types.Message):
    # Переменная text содержит в себе текст, который пользователь увидит при выполнении команды /start или /help
    text = """

Hello! 
I am the CURRENCY BOT.
I convert any currency into any currency in any amount.

To see the list of available currencies (short names and full names):
/list

To convert currencies:
Enter currency to convert FROM, then currency to convert TO, then AMOUNT.
(separated by a 'space' with NO COMMAS)

Note: use currencies' short names in your conversion requests
Note: the amount of converting currency must be less than 1000000

Example: "EUR USD 1000"

To get a currency short name:
'get [currency full name]'

To see instructions:
/start
/help

"""
    # Вызываем метод бота, оформляющий подачу вышеизложенного текста в виде ответного сообщения на запрос пользователя
    bot.reply_to(message, text)


# Создаем функцию (задекорированную методом бота), отвечающую за пользовательскую команду /list (которая выводит
# список всех доступных для конвертирования валют в виде: {краткое название: полное название})
@bot.message_handler(commands=["list"])
def list_(message: telebot.types.Message):
    # В переменную text записываем заголовок списка валют: "Доступные валюты"
    text = "Available currencies:"
    # Создаём цикл, перебирающий все ключи и соответствующие им значения импортированного словаря currency_keys
    # (список доступных валют) и выводящий их пользователю
    for key, value in currency_keys.items():
        text = "\n".join((text, key, value))
    # Вызываем метод бота, оформляющий подачу вышеизложенного текста в виде ответного сообщения на запрос пользователя
    bot.reply_to(message, text)


# Создаем функцию (задекорированную методом бота), отвечающую за конвертацию валют (основная функция бота), а также
# за получение краткого наименования валюты по его полному названию
@bot.message_handler(content_types=["text"])
def convert(message: telebot.types.Message):
    # Открываем конструкцию try - except, чтобы отлавливать исключения в последующем блоке кода
    try:
        # Переменной values присваиваем текст сообщения пользователя, попутно убирая лишние пробелы в начале и в конце
        # и убирая запятые, а также разбиваем исходную строку на список отдельных строк
        values = message.text.strip().replace(",", "").split(" ")
        # Проверяем, введено ли первым словом get (в трёх разных вариациях), чтобы определить, в чём состоит запрос
        # пользователя: в запросе на конвертацию валют или на получение краткого имени валюты по его полному имени
        if values[0] == "GET" or values[0] == "Get" or values[0] == "get":
            # Проверяем наличие введённого пользователем полного имени валюты в списке доступных валют и
            # если введённое имя в списке не обнаружено - выводим сообщение об этом
            if Conversion.get_short_name(message) is None:
                text = "Couldn't find the currency in the list of available currencies"
                bot.reply_to(message, text)
            # Если введённое пользователем имя в списке доступных имён обнаружено - вызываем метод get_short_name
            # импортированного в данный файл класса Conversion. В качестве возвращаемого значения у данного метода
            # выступает строка с кратким именем запрошенной валюты
            else:
                bot.reply_to(message, Conversion.get_short_name(message))
        # Если первым введённым пользователем словом не является get, инициализируется блок кода, отвечающий
        # непосредственно за конвертацию
        else:
            # Проверяем количество введённых аргументов, если оно не равно трём - поднимаем исключение (импортированного
            # класса ConversionException) с соответствующим сообщением
            if len(values) != 3:
                raise ConversionException("Invalid number of arguments was given!")
            # Продолжение скрипта при прохождении предыдущей проверки
            else:
                # Присваиваем трём новым переменным from_ (валюта, которую мы собираемся конвертировать), to_ (валюта,
                # в которую мы собираемся конвертировать) и amount_ (количество) значение переменной values
                from_, to_, amount_ = values
                # Проверяем, входит ли введённая пользователем валюта (переменная from_) в список доступных валют. Если
                # данной валюты нет в списке - поднимаем исключение (импортированного класса ConversionException) с
                # соответствующим сообщением
                if from_.upper() not in currency_keys.keys():
                    raise ConversionException(f"Couldn't process currency '{from_}'")
                # Проверяем, входит ли введённая пользователем валюта (переменная to_) в список доступных валют. Если
                # данной валюты нет в списке - поднимаем исключение (импортированного класса ConversionException) с
                # соответствующим сообщением
                elif to_.upper() not in currency_keys.keys():
                    raise ConversionException(f"Couldn't process currency '{to_}'")
                # Проверяем, является ли введённое пользователем количество (переменная amount_) числом, а также
                # проверяем, не превышает ли оно значение 1000000. Если хотя бы одна из проверок не пройдена - поднимаем
                # исключение (импортированного класса ConversionException) с соответствующим сообщением
                elif not amount_.isdigit() or int(amount_) > 1000000:
                    raise ConversionException(f"Couldn't process amount '{amount_}'")
                # Если все проверки пройдены - переходим к конвертации
                else:
                    # В переменную result записываем результат конвертации, которая осуществляется при помощи метода
                    # convert класса Conversion
                    result = Conversion.convert(from_, to_, amount_)
                    # Оформляем финальное сообщение для пользователя, объединяя переменные from_, to_, amount_ и
                    # result в единую отформатированную строку
                    text = f"The price of {amount_} {from_.upper()} in {to_.upper()} = {result}"
                    # Вызываем метод бота, оформляющий подачу переменной text в виде ответного сообщения бота на
                    # запрос пользователя
                    bot.send_message(message.chat.id, text)
    # Замыкаем конструкцию try - except блоком except, рассчитанным на отлов как пользовательских ошибок, так и
    # потенциальных системных ошибок. Оформляем вывод сообщения об ошибке с помощью метода бота reply_to
    except ConversionException as e:
        bot.reply_to(message, f"An error occured!\n{e}")
    except Exception as e:
        bot.reply_to(message, f"An error occured!\n{e}")


# Запускаем бота
bot.polling(none_stop=True)
