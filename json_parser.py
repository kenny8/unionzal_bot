import sys  # импортируем модуль sys для использования функции exit()
import requests  # модуль для выполнения HTTP-запросов
import json  # модуль для работы с JSON-данными
import re  # модуль для работы с регулярными выражениями
from bs4 import BeautifulSoup  # библиотека для парсинга HTML-страниц
from datetime import datetime, time #для работы с временим
import settings

def json_afisha() -> None:
    import time as tm
    # выполнение HTTP-запроса и проверка на ошибки
    try:
        response = requests.get(settings.JSON_AFISHA_URL)
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
        if dt_start.date() < datetime.today().date():
            continue  # если дата начала уже прошла, пропускаем мероприятие
        time_start = [dt_start.strftime('%d.%m.%y'), tm.strftime('%H:%M', tm.gmtime(
            dt_start.timestamp()))]  # преобразование даты в строку в формате ['дд.мм.гг', 'чч:мм']
        dt_end = datetime.fromisoformat(
            item['field_data_koncerta_end'][0]['value'])  # получаем дату и время окончания мероприятия
        time_end = [dt_end.strftime('%d.%m.%y'), tm.strftime('%H:%M', tm.gmtime(
            dt_end.timestamp()))]  # преобразование даты в строку в формате ['дд.мм.%гг', 'чч:мм']
        banner = item['field_banner_dlya_glavnoy'][0]['url']  # получаем ссылку на баннер мероприятия
        ticket = "https://quicktickets.ru/lipetsk-filarmoniya/" + item['field_qt_id'][0][
            'value']  # получаем ссылку на покупку билетов мероприятия
        afisha.extend([title, txt, time_start, time_end, banner, ticket])
        afisha_card.append(afisha)
    print(afisha_card)
    return sorted(afisha_card, key=lambda x: datetime.strptime(x[2][0], '%d.%m.%y'))

def json_persons() -> None:
    import time as tm
    # выполнение HTTP-запроса и проверка на ошибки
    try:
        response = requests.get(settings.JSON_PERSONS_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)  # выходим из программы в случае ошибки
    data = json.loads(response.text)  # преобразуем полученные данные в формат JSON
    persons_card = []  # список для хранения полученной информации
    # обработка данных из формата JSON и сохранение в списке persons_card
    #print(data)
    for item in data:
        persons = []
        persons_name = item['title'][0]['value'] # получаем имя персоны, если оно есть
        # получаем описание персоны, если оно есть
        soup = BeautifulSoup(item['body'][0]['summary'], 'html.parser')  # получаем HTML-код описания мероприятия
        persons_description = re.sub(r'\s+', ' ',
                     soup.get_text()).strip()  # получаем текст из HTML-кода и Очищаем текст от управляющих символов
        persons_url = "https://unionzal.ru/node/" + str(
            item['nid'][0]['value'])  # получаем ссылка на сайт
        persons_tags = settings.TIPE[item['field_tags'][0]['target_id']] # получаем список тегов персоны, если они есть
        persons_image = item['field_image'][0]['url'] # получаем изображение персоны, если оно есть
        persons.extend([persons_name, persons_description, persons_tags, persons_url, persons_image])
        persons_card.append(persons)  # добавляем полученную информацию в список persons_card
        #print(persons)
    return persons_card
