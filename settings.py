from json_parser import json_afisha, json_persons
from datetime import datetime

MAX_MESSAGE_LENGTH = 900
MAIN_WALLPAPERS = "https://unionzal.ru/sites/default/files/2020-11/presentation-wrapper.jpg"
TOKEN_BOT = "6241891253:AAEtTI5Ma8z34FM3fOusBJoLqI7xtRGLnTU"
JSON_AFISHA_URL = "https://unionzal.ru/rest/export/json/afisha"
JSON_PERSONS_URL = "https://unionzal.ru/rest/export/json/persons"
TIPE = {2: "Солисты", 20: "Коллективы", 4: "Ведущие концертов", 51: "Концертмейстеры"}
PASSWORD = "o76cy5zl2y"
START_GIVEAWAY = [True, "пример текста розыгрыша", 1, "Geralt_f_r_o_m_Rivia", []]
FEEDBACK_USER = [["@Geralt_f_r_o_m_Rivia", "1 сообщение"], ["@Geralt_f_r_o_m_Rivia", "2 сообщение"], ["@Geralt_f_r_o_m_Rivia", "3 сообщение"]]
USERS = []
CHAT = "test12345671235"
now = datetime.now()
AFISHA_CARD = json_afisha()
PERSONS_CARD = json_persons()
AFISHA_CARD_TIME = PERSONS_CARD_TIME = now
print(AFISHA_CARD_TIME)
