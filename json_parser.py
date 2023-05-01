import sys  # импортируем модуль sys для использования функции exit()
import requests  # модуль для выполнения HTTP-запросов
import json  # модуль для работы с JSON-данными
import re  # модуль для работы с регулярными выражениями
from bs4 import BeautifulSoup  # библиотека для парсинга HTML-страниц
from datetime import datetime, time #для работы с временим

def json_afisha() -> None:
    import time as tm
    # выполнение HTTP-запроса и проверка на ошибки
    try:
        response = requests.get('https://unionzal.ru/rest/export/json/afisha')
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)  # выходим из программы в случае ошибки

    data = json.loads(response.text)  # преобразуем полученные данные в формат JSON
    afisha_card = []  # список для хранения полученной информации

    # обработка данных из формата JSON и сохранение в списке afisha_card
    for item in data:
        afisha = []
        title = item['title'][0]['value']  # получаем название мероприятия
        soup = BeautifulSoup(item['body'][0]['value'], 'html.parser')  # получаем HTML-код описания мероприятия
        txt = re.sub(r'\s+', ' ',
                     soup.get_text()).strip()  # получаем текст из HTML-кода и Очищаем текст от управляющих символов
        dt_start = datetime.fromisoformat(
            item['field_data_koncerta'][0]['value'])  # получаем дату и время начала мероприятия
        time_start = [dt_start.strftime('%d.%m.%y'), tm.strftime('%H:%M', tm.gmtime(
            dt_start.timestamp()))]  # преобразование даты в строку в формате ['дд.мм.гг', 'чч:мм']
        dt_end = datetime.fromisoformat(
            item['field_data_koncerta_end'][0]['value'])  # получаем дату и время окончания мероприятия
        time_end = [dt_end.strftime('%d.%m.%y'), tm.strftime('%H:%M', tm.gmtime(
            dt_end.timestamp()))]  # преобразование даты в строку в формате ['дд.мм.гг', 'чч:мм']
        banner = item['field_banner_dlya_glavnoy'][0]['url']  # получаем ссылку на баннер мероприятия
        ticket = "https://quicktickets.ru/lipetsk-filarmoniya/" + item['field_qt_id'][0][
            'value']  # получаем ссылку на покупку билетов мероприятия
        afisha.extend([title, txt, time_start, time_end, banner, ticket])
        afisha_card.append(afisha)  # добавляем полученную информацию в список afisha_card
        #print(afisha)  # выводим полученную информацию на экран

    #print("\n", afisha_card, "\n")  # выводим итоговый список на экран
    #print(data)  # выводим исходные данные в формате JSON на экран
    return afisha_card