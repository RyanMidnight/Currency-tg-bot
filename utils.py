# Импортируем необходимые для функционала бота библиотеки requests и json
import requests
import json
# Из файла config импортируем переменную currency_keys, содержащую список всех доступных для конвертации валют
from config import currency_keys


# Создаём пустой класс ConversionException и наследуем его от класса-родителя Exception для дальнейшего использования в
# отлове исключений в основном файле
class ConversionException(Exception):
    pass


# Создаём класс Conversion, содержащий в себе два статических метода: отвечающий за проведение конвертации и
# отвечающий за получение короткого имени валюты по запросу с полным именем валюты
class Conversion:
    # Создаём статический метод, отвечающий за конвертацию валют (принимает на вход три аргумента: from_ (валюта,
    # которую мы собираемся конвертировать), to_ (валюта, в которую мы собираемся конвертировать) и amount_ (количество)
    @staticmethod
    def convert(from_, to_, amount_):
        # В переменную url помещаем ссылку на API (отвечающий за конвертацию), внутрь ссылки в соответствующие места
        # помещаем вышеупомянутые переменные from_, to_ и amount_
        url = f"https://api.apilayer.com/currency_data/convert?to={to_}&from={from_}&amount={amount_}"
        payload = {}
        # В переменную headers помещаем уникальный токен API
        headers = {"apikey": "IeVyhXCdqry0AdXj61eB1k48FWU4LfUf"}
        # С помощью метода requests.request получаем экземпляр класса requests.models.Response с необходимой информацией
        response = requests.request("GET", url, headers=headers, data=payload)
        # В переменную result помещаем расшифрованный с помощью метода json.loads итоговый результат конвертации
        # в виде числа
        result = json.loads(response.content)["result"]
        # Возвращаемым значением данного метода является переменная result, содержащая в себе итоговый результат
        # конвертации валют в виде числа
        return result

    # Создаём статический метод, отвечающий за получение краткого имени валюты по введенному пользователем полному имени
    # валюты (передаваемым в метод аргументом является сообщение пользователя, начинающееся с кодового слова get и далее
    # содержащее в себе полное наименование валюты)
    @staticmethod
    def get_short_name(message):
        # Создаём переменную full_name_list и помещаем в неё пустой список, который понадобится позже
        full_name_list = []
        # В переменную full_name помещаем исходное пользовательское сообщение, попутно избавляясь от лишних пробелов и
        # разделяя его на отдельные строки в виде списка
        full_name = message.text.strip().split(" ")
        # При помощи цикла for перебираем все слова в списке full_name и приводим их к правильному формату с помощью
        # функций lower() и capitalize(), отформатированные слова добавляем в заранее созданный пустой список
        # full_name_list
        for word in full_name:
            final_word = word.lower().capitalize()
            full_name_list.append(final_word)
        # Удаляем из списка первый элемент (кодовое слово get)
        full_name_list.pop(0)
        # Превращаем список full_name_list обратно в строку с помощью метода join и присваиваем её переменной full_name
        full_name = " ".join(full_name_list)
        # С помощью цикла for перебираем ключи и значения словаря доступных валют currency_keys, при совпадении
        # введённого пользователем полного названия валюты с указанным в словаре метод возвращает строку, в которой
        # указано соответствующее краткое название валюты
        for i, j in currency_keys.items():
            if j == full_name:
                return f"The short name for '{full_name}' is '{i}'"
