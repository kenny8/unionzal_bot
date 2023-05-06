from json_parser import json_afisha, json_persons
from datetime import datetime
import pickle

MAX_MESSAGE_LENGTH = 900
MAIN_WALLPAPERS = "https://unionzal.ru/sites/default/files/2020-11/presentation-wrapper.jpg"
TOKEN_BOT = "6241891253:AAEtTI5Ma8z34FM3fOusBJoLqI7xtRGLnTU"
JSON_AFISHA_URL = "https://unionzal.ru/rest/export/json/afisha"
JSON_PERSONS_URL = "https://unionzal.ru/rest/export/json/persons"
TIPE = {2: "Солисты", 20: "Коллективы", 4: "Ведущие концертов", 51: "Концертмейстеры"}
PASSWORD = "o76cy5zl2y"

FEEDBACK_TXT = 'feedback_fl.txt'
USERS_TXT = 'users_chat_fl.txt'
GIVEAWAY_TXT = 'giveway_fl.txt'

START_GIVEAWAY = []
with open(GIVEAWAY_TXT, 'rb') as file:
    START_GIVEAWAY = pickle.load(file)

FEEDBACK_USER = []
with open(FEEDBACK_TXT, 'rb') as file:
    FEEDBACK_USER = pickle.load(file)

USERS = []
with open(USERS_TXT, 'rb') as file:
    USERS = pickle.load(file)

print(FEEDBACK_USER)
print(USERS)
print(START_GIVEAWAY)

CHAT = "test12345671235"

now = datetime.now()
AFISHA_CARD = json_afisha()
PERSONS_CARD = json_persons()
AFISHA_CARD_TIME = PERSONS_CARD_TIME = now
print(AFISHA_CARD_TIME)
