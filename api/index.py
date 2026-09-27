from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import urllib.request
import urllib.parse
import json

app = FastAPI()

# ============================================================
# VESTHETIC SETTINGS
# ============================================================
# Vercel-compatible entrypoint
handler = app


# ============================================================
# VESTHETIC SETTINGS
# ============================================================

BOT_TOKEN = "8861881318:AAGobv6YMBoBgvX-Xrtx94W-iIK21RQvYBQ"

ADMIN_IDS = [625577962]
MANAGER_ID = 8965656829
MANAGER_USERNAME = "VESTHETIC_manager"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ============================================================
# TEMPORARY STORAGE
# ============================================================

users = {}
applications = {}
next_application_id = 1


# ============================================================
# TELEGRAM API
# ============================================================

def telegram(method, data=None):
    try:
        url = f"{TELEGRAM_API}/{method}"

        if data:
            encoded = urllib.parse.urlencode(data).encode("utf-8")
            request = urllib.request.Request(url, data=encoded)
        else:
            request = urllib.request.Request(url)

        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except Exception as e:
        print("Telegram API error:", e)
        return None


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    if reply_markup is not None:
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


# ============================================================
# KEYBOARDS
# ============================================================

def language_keyboard():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🇷🇺 Русский",
                    "callback_data": "lang_ru"
                },
                {
                    "text": "🇺🇦 Українська",
                    "callback_data": "lang_ua"
                },
            ],
            [
                {
                    "text": "🇸🇰 Slovenčina",
                    "callback_data": "lang_sk"
                },
                {
                    "text": "🇬🇧 English",
                    "callback_data": "lang_en"
                },
            ],
        ]
    }


def main_keyboard(lang):
    buttons = {
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

    rows = buttons.get(lang, buttons["en"])

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
            [
                {
                    "text": text,
                    "callback_data": "home"
                }
            ]
        ]
    }


def age_keyboard(lang):
    if lang == "ru":
        yes = "✅ Да"
        no = "❌ Нет"
    elif lang == "ua":
        yes = "✅ Так"
        no = "❌ Ні"
    elif lang == "sk":
        yes = "✅ Áno"
        no = "❌ Nie"
    else:
        yes = "✅ Yes"
        no = "❌ No"

    return {
        "inline_keyboard": [
            [
                {
                    "text": yes,
                    "callback_data": "age_yes"
                },
                {
                    "text": no,
                    "callback_data": "age_no"
                },
            ]
        ]
    }


def admin_keyboard(app_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🟢 Accept",
                    "callback_data": f"status_accept_{app_id}"
                },
                {
                    "text": "🟡 In progress",
                    "callback_data": f"status_progress_{app_id}"
                },
            ],
            [
                {
                    "text": "🔴 Reject",
                    "callback_data": f"status_reject_{app_id}"
                }
            ],
        ]
    }


# ============================================================
# TEXTS
# ============================================================

TEXTS = {

    "ru": {
        "welcome":
            "<b>VESTHETIC | Digital Talent Agency</b>\n\n"
            "Мы помогаем совершеннолетним онлайн-креаторам "
            "строить и развивать карьеру на международных "
            "платформах.\n\n"
            "18+ only • Voluntary • Global",

        "about":
            "<b>VESTHETIC</b>\n\n"
            "Digital Talent Agency для взрослых онлайн-креаторов.\n\n"
            "Мы помогаем с регистрацией, стартом, развитием "
            "и организацией работы на международных платформах.\n\n"
            "<b>Модель:</b> 75% creator / 25% VESTHETIC\n\n"
            "Платформы:\n"
            "• BongaCams\n"
            "• Stripchat\n"
            "• Chaturbate",

        "terms":
            "<b>Условия</b>\n\n"
            "• Только 18+\n"
            "• Участие исключительно добровольное\n"
            "• 75% дохода получает creator\n"
            "• 25% — VESTHETIC\n"
            "• Работа ведётся через международные платформы\n\n"
            "Мы не запрашиваем паспорта, банковские данные "
            "или интимные материалы через Telegram.",

        "faq":
            "<b>FAQ</b>\n\n"
            "<b>Сколько можно зарабатывать?</b>\n"
            "Доход зависит от платформы, активности, графика "
            "и аудитории. Фиксированный доход не гарантируется.\n\n"
            "<b>Нужен ли опыт?</b>\n"
            "Нет. Можно начать с нуля.\n\n"
            "<b>Можно работать из дома?</b>\n"
            "Да.\n\n"
            "<b>Возраст?</b>\n"
            "Строго 18+.",

        "apply_start":
            "<b>Заявка в VESTHETIC</b>\n\n"
            "Заполнение займёт несколько минут.\n\n"
            "Продолжая, вы подтверждаете, что вам 18 лет "
            "или больше и вы действуете добровольно.",

        "age":
            "Вам уже исполнилось 18 лет?",

        "age_no":
            "К сожалению, VESTHETIC работает только "
            "с совершеннолетними.",

        "name":
            "Как вас зовут или какой псевдоним вы хотели "
            "бы использовать?",

        "country":
            "В какой стране вы сейчас находитесь?",

        "languages":
            "Какими языками вы владеете?",

        "experience":
            "Есть ли у вас опыт работы на подобных платформах?",

        "equipment":
            "Какое оборудование у вас есть? "
            "Например: телефон, ПК, камера, свет.",

        "schedule":
            "Сколько времени в день или неделю вы готовы "
            "уделять работе?",

        "contact":
            "Укажите Telegram-контакт для связи с менеджером.",

        "source":
            "Откуда вы узнали о VESTHETIC?",

        "thanks":
            "<b>Заявка отправлена ✅</b>\n\n"
            "Спасибо! Менеджер VESTHETIC рассмотрит вашу заявку "
            "и свяжется с вами.",

        "manager":
            "<b>Менеджер VESTHETIC</b>\n\n"
            f"Связаться: @{MANAGER_USERNAME}",
    },

    "ua": {
        "welcome":
            "<b>VESTHETIC | Digital Talent Agency</b>\n\n"
            "Ми допомагаємо повнолітнім онлайн-креаторам "
            "розвивати кар'єру на міжнародних платформах.\n\n"
            "18+ only • Voluntary • Global",

        "about":
            "<b>VESTHETIC</b>\n\n"
            "Digital Talent Agency для дорослих онлайн-креаторів.\n\n"
            "<b>Модель:</b> 75% creator / 25% VESTHETIC\n\n"
            "Платформи:\n"
            "• BongaCams\n"
            "• Stripchat\n"
            "• Chaturbate",

        "terms":
            "<b>Умови</b>\n\n"
            "• Тільки 18+\n"
            "• Участь виключно добровільна\n"
            "• 75% доходу отримує creator\n"
            "• 25% — VESTHETIC\n\n"
            "Ми не запитуємо паспорти, банківські дані "
            "чи інтимні матеріали через Telegram.",

        "faq":
            "<b>FAQ</b>\n\n"
            "<b>Чи потрібен досвід?</b>\n"
            "Ні, можна почати з нуля.\n\n"
            "<b>Можна працювати з дому?</b>\n"
            "Так.\n\n"
            "<b>Вік?</b>\n"
            "Строго 18+.",

        "apply_start":
            "<b>Заявка в VESTHETIC</b>\n\n"
            "Заповнення займе кілька хвилин.\n\n"
            "Продовжуючи, ви підтверджуєте
