from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import urllib.request
import urllib.parse
import json

app = FastAPI()

# =========================
# VESTHETIC BOT SETTINGS
# =========================

BOT_TOKEN = "8861881318:AAGobv6YMBoBgvX-Xrtx94W-iIK21RQvYBQ"

ADMIN_IDS = [625577962]
MANAGER_ID = 8965656829
MANAGER_USERNAME = "VESTHETIC_manager"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Temporary in-memory storage
users = {}
applications = {}
next_application_id = 1


# =========================
# TELEGRAM API
# =========================

def telegram(method, data=None):
    try:
        url = f"{TELEGRAM_API}/{method}"

        if data:
            encoded = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(url, data=encoded)
        else:
            req = urllib.request.Request(url)

        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    except Exception as e:
        print("Telegram API error:", e)
        return None


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    return telegram("sendMessage", data)


def answer_callback(callback_id, text=""):
    return telegram(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_id,
            "text": text,
        },
    )


# =========================
# KEYBOARDS
# =========================

def language_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🇷🇺 Русский", "callback_data": "lang_ru"},
                {"text": "🇺🇦 Українська", "callback_data": "lang_ua"},
            ],
            [
                {"text": "🇸🇰 Slovenčina", "callback_data": "lang_sk"},
                {"text": "🇬🇧 English", "callback_data": "lang_en"},
            ],
        ]
    }


def main_keyboard(lang):
    labels = {
        "ru": [
            ("ℹ️ О VESTHETIC", "about"),
            ("📋 Условия", "terms"),
            ("❓ FAQ", "faq"),
            ("🚀 Подать заявку", "apply"),
            ("👤 Связаться с менеджером", "manager"),
            ("🌐 Язык", "language"),
        ],
        "ua": [
            ("ℹ️ Про VESTHETIC", "about"),
            ("📋 Умови", "terms"),
            ("❓ FAQ", "faq"),
            ("🚀 Подати заявку", "apply"),
            ("👤 Зв'язатися з менеджером", "manager"),
            ("🌐 Мова", "language"),
        ],
        "sk": [
            ("ℹ️ O VESTHETIC", "about"),
            ("📋 Podmienky", "terms"),
            ("❓ FAQ", "faq"),
            ("🚀 Poslať žiadosť", "apply"),
            ("👤 Kontaktovať manažéra", "manager"),
            ("🌐 Jazyk", "language"),
        ],
        "en": [
            ("ℹ️ About VESTHETIC", "about"),
            ("📋 Terms", "terms"),
            ("❓ FAQ", "faq"),
            ("🚀 Apply", "apply"),
            ("👤 Contact manager", "manager"),
            ("🌐 Language", "language"),
        ],
    }

    rows = labels.get(lang, labels["en"])

    return {
        "inline_keyboard": [
            [{"text": rows[0][0], "callback_data": rows[0][1]}],
            [{"text": rows[1][0], "callback_data": rows[1][1]}],
            [{"text": rows[2][0], "callback_data": rows[2][1]}],
            [{"text": rows[3][0], "callback_data": rows[3][1]}],
            [{"text": rows[4][0], "callback_data": rows[4][1]}],
            [{"text": rows[5][0], "callback_data": rows[5][1]}],
        ]
    }


def back_keyboard(lang):
    text = {
        "ru": "◀️ Назад",
        "ua": "◀️ Назад",
        "sk": "◀️ Späť",
        "en": "◀️ Back",
    }.get(lang, "◀️ Back")

    return {
        "inline_keyboard": [
            [{"text": text, "callback_data": "home"}]
        ]
    }


# =========================
# TEXTS
# =========================

TEXTS = {
    "ru": {
        "welcome": (
            "<b>VESTHETIC | Digital Talent Agency</b>\n\n"
            "Мы помогаем совершеннолетним онлайн-креаторам "
            "строить и развивать карьеру на международных платформах.\n\n"
            "18+ only • Voluntary • Global"
        ),
        "about": (
            "<b>VESTHETIC</b>\n\n"
            "Digital Talent Agency для взрослых онлайн-креаторов.\
