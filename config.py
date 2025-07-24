import os

API_TOKEN = 'TOKEN'
ADMIN_ID = 123456789
CHAT_ID = -123456789
PRO_CHAT_ID = -123456789
BOOSTY_URL = "https://t.me/psychobye/"
BOOSTY_PRO_URL = "https://t.me/psychobye/"

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# PVRTEXTOOL_PATH = os.path.join(BASE_PATH, "PVRTexToolCLI") # linux
# KRAM_PATH = "/usr/local/bin/kram" # linux
TEMP_DIR = os.path.join(BASE_PATH, "temp")
OUT_DIR = os.path.join(BASE_PATH, "output")
MODELS_PATH = os.path.join(BASE_PATH, "models")
SITE_PATH = os.path.join(BASE_PATH, "site") # win
# SITE_PATH = "/var/www/unware_site" # linux
DFF_PATH = os.path.join(MODELS_PATH, "dff")
TEX_PATH = os.path.join(MODELS_PATH, "tex")
BTX_PATH = os.path.join(MODELS_PATH, "btx")
CARS_IDE_PATH = os.path.join(MODELS_PATH, "cars.ide")
SKINS_IDE_PATH = os.path.join(MODELS_PATH, "skins.ide")
MAP_IDE_PATH = os.path.join(MODELS_PATH, "map.ide")
CARS_JSON_PATH = os.path.join(SITE_PATH, "cars.json")
SKINS_JSON_PATH = os.path.join(SITE_PATH, "skins.json")
MAP_JSON_PATH = os.path.join(SITE_PATH, "map.json")
LOG_FILE = "log.txt"

MESSAGE_EFFECTS = [
    "5104841245755180586",  # 🔥
    "5107584321108051014",  # 👍
    "5046509860389126442",  # 🎉
]

# base
BASE_LIMITS = {
    "COOLDOWN": 15,
    "MAX_ARCHIVE_SIZE": 20 * 1024 * 1024,
    "MAX_FILES_IN_MEDIA_GROUP": 10,
    "MAX_CONCURRENT_CONVERSIONS": 5,
    "GROUP_PROCESSING_DELAY": 0.5,
}

# pro
PRO_LIMITS = {
    "COOLDOWN": 15,
    "MAX_ARCHIVE_SIZE": 20 * 1024 * 1024,
    "MAX_FILES_IN_MEDIA_GROUP": 10,
    "MAX_CONCURRENT_CONVERSIONS": 5,
    "GROUP_PROCESSING_DELAY": 0.5,
}