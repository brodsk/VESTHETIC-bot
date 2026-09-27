from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import html
import urllib.request
import urllib.parse
import json
import os

app = FastAPI()
security = HTTPBasic()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

ADMIN_IDS = [625577962]
MANAGER_ID = 8965656829
MANAGER_USERNAME = "VESTHETIC_manager"
# Staff members allowed to process applications
STAFF_IDS = list(dict.fromkeys(ADMIN_IDS + [MANAGER_ID]))

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ============================================================
# STORAGE
# ============================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xtxqslzublggqhctmjoa.supabase.co").rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ADMIN_PANEL_USER = os.environ.get("ADMIN_PANEL_USER", "admin")
ADMIN_PANEL_PASSWORD = os.environ.get("ADMIN_PANEL_PASSWORD", "")

def load_user(chat_id, username=None):
    rows = supabase_request(
        "GET",
        "bot_users",
        query={
            "telegram_chat_id": f"eq.{chat_id}",
            "select": "*",
            "limit": "1",
        },
    )
    if isinstance(rows, list) and rows:
        row = rows[0]
        try:
            draft = row.get("application_draft") or {}
            if isinstance(draft, str):
                draft = json.loads(draft)
        except Exception:
            draft = {}
        return {
            "lang": row.get("language") or "en",
            "state": row.get("state"),
            "application": draft if isinstance(draft, dict) else {},
        }

    user = {"lang": "en", "state": None, "application": {}}
    save_user(chat_id, username, user)
    return user


def save_user(chat_id, username, user):
    payload = {
        "telegram_chat_id": chat_id,
        "telegram_username": username,
        "language": user.get("lang", "en"),
        "state": user.get("state"),
        "application_draft": user.get("application", {}),
    }
    return supabase_request(
        "POST",
        "bot_users",
        payload,
        {"select": "*"},
    )



def supabase_request(method, path, payload=None, query=None):
    if not SUPABASE_SERVICE_ROLE_KEY:
        print("Supabase error: SUPABASE_SERVICE_ROLE_KEY is not configured")
        return None

    url = f"{SUPABASE_URL}/rest/v1/{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)

    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }

    if method == "POST":
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
    elif method in ("PATCH", "PUT"):
        headers["Prefer"] = "return=representation"

    try:
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method,
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else []

    except Exception as exc:
        print("Supabase API error:", exc)
        return None


def create_application(chat_id, username, data):
    payload = {
        "telegram_chat_id": chat_id,
        "telegram_username": username,
        "name": data.get("name"),
        "age_confirmed": True,
        "country": data.get("country"),
        "languages": data.get("languages"),
        "experience": data.get("experience"),
        "equipment": data.get("equipment"),
        "schedule": data.get("schedule"),
        "contact": data.get("contact"),
        "source": data.get("source"),
        "status": "new",
    }

    rows = supabase_request(
        "POST",
        "applications",
        payload,
        {"select": "*"},
    )

    if isinstance(rows, list) and rows:
        return rows[0]

    return None


def get_application(app_id):
    rows = supabase_request(
        "GET",
        "applications",
        query={
            "id": f"eq.{app_id}",
            "select": "*",
            "limit": "1",
        },
    )
    if isinstance(rows, list) and rows:
        return rows[0]
    return None


def get_application_history(app_id):
    rows = supabase_request(
        "GET",
        "application_status_history",
        query={
            "application_id": f"eq.{app_id}",
            "select": "*",
            "order": "created_at.asc",
        },
    )
    return rows if isinstance(rows, list) else []


def update_application_status(app_id, status):
    rows = supabase_request(
        "PATCH",
        "applications",
        {"status": status},
        {
            "id": f"eq.{app_id}",
            "select": "*",
        },
    )
    if isinstance(rows, list) and rows:
        return rows[0]
    return None


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
        "welcome": "<b>VESTHETIC | Digital Talent Agency</b>\n\nМы помогаем совершеннолетним онлайн-креаторам строить и развивать карьеру на международных платформах.\n\n18+ only • Voluntary • Global",
        "about": "<b>VESTHETIC</b>\n\nDigital Talent Agency для взрослых онлайн-креаторов.\n\n<b>Модель:</b> 75% creator / 25% VESTHETIC\n\nПлатформы:\n• BongaCams\n• Stripchat\n• Chaturbate",
        "terms": "<b>Условия</b>\n\n• Только 18+\n• Участие исключительно добровольное\n• 75% дохода получает creator\n• 25% — VESTHETIC\n\nМы не запрашиваем паспорта, банковские данные или интимные материалы через Telegram.",
        "faq": "<b>FAQ</b>\n\n<b>Нужен ли опыт?</b>\nНет, можно начать с нуля.\n\n<b>Можно работать из дома?</b>\nДа.\n\n<b>Возраст?</b>\nСтрого 18+.",
        "apply_start": "<b>Заявка в VESTHETIC</b>\n\nЗаполнение займёт несколько минут.\n\nПродолжая, вы подтверждаете, что вам 18 лет или больше и вы действуете добровольно.",
        "age": "Вам уже исполнилось 18 лет?", "age_no": "К сожалению, VESTHETIC работает только с совершеннолетними.",
        "name": "Как вас зовут или какой псевдоним вы хотели бы использовать?", "country": "В какой стране вы сейчас находитесь?",
        "languages": "Какими языками вы владеете?", "experience": "Есть ли у вас опыт работы на подобных платформах?",
        "equipment": "Какое оборудование у вас есть? Например: телефон, ПК, камера, свет.",
        "schedule": "Сколько времени в день или неделю вы готовы уделять работе?", "contact": "Укажите Telegram-контакт для связи с менеджером.",
        "source": "Откуда вы узнали о VESTHETIC?", "thanks": "<b>Заявка отправлена ✅</b>\n\nСпасибо! Менеджер VESTHETIC рассмотрит вашу заявку и свяжется с вами.",
        "manager": "<b>Менеджер VESTHETIC</b>\n\nСвязаться: @VESTHETIC_manager"
    },
    "ua": {
        "welcome": "<b>VESTHETIC | Digital Talent Agency</b>\n\nМи допомагаємо повнолітнім онлайн-креаторам розвивати кар'єру на міжнародних платформах.\n\n18+ only • Voluntary • Global",
        "about": "<b>VESTHETIC</b>\n\nDigital Talent Agency для дорослих онлайн-креаторів.\n\n<b>Модель:</b> 75% creator / 25% VESTHETIC\n\nПлатформи:\n• BongaCams\n• Stripchat\n• Chaturbate",
        "terms": "<b>Умови</b>\n\n• Тільки 18+\n• Участь виключно добровільна\n• 75% доходу отримує creator\n• 25% — VESTHETIC\n\nМи не запитуємо паспорти, банківські дані чи інтимні матеріали через Telegram.",
        "faq": "<b>FAQ</b>\n\n<b>Чи потрібен досвід?</b>\nНі, можна почати з нуля.\n\n<b>Можна працювати з дому?</b>\nТак.\n\n<b>Вік?</b>\nСтрого 18+.",
        "apply_start": "<b>Заявка в VESTHETIC</b>\n\nЗаповнення займе кілька хвилин.\n\nПродовжуючи, ви підтверджуєте, що вам 18 років або більше та дієте добровільно.",
        "age": "Вам вже виповнилося 18 років?", "age_no": "На жаль, VESTHETIC працює лише з повнолітніми.",
        "name": "Як вас звати або який псевдонім ви хотіли б використовувати?", "country": "У якій країні ви зараз перебуваєте?",
        "languages": "Якими мовами ви володієте?", "experience": "Чи маєте ви досвід роботи на подібних платформах?",
        "equipment": "Яке обладнання у вас є? Наприклад: телефон, ПК, камера, світло.",
        "schedule": "Скільки часу на день або тиждень ви готові приділяти роботі?", "contact": "Вкажіть Telegram-контакт для зв'язку з менеджером.",
        "source": "Звідки ви дізналися про VESTHETIC?", "thanks": "<b>Заявку надіслано ✅</b>\n\nДякуємо! Менеджер VESTHETIC розгляне вашу заявку та зв'яжеться з вами.",
        "manager": "<b>Менеджер VESTHETIC</b>\n\nЗв'язатися: @VESTHETIC_manager"
    },
    "sk": {
        "welcome": "<b>VESTHETIC | Digital Talent Agency</b>\n\nPomáhame dospelým online tvorcom budovať a rozvíjať kariéru na medzinárodných platformách.\n\n18+ only • Voluntary • Global",
        "about": "<b>VESTHETIC</b>\n\nDigital Talent Agency pre dospelých online tvorcov.\n\n<b>Model:</b> 75% creator / 25% VESTHETIC\n\nPlatformy:\n• BongaCams\n• Stripchat\n• Chaturbate",
        "terms": "<b>Podmienky</b>\n\n• Iba 18+\n• Účasť je dobrovoľná\n• 75% príjmu dostáva creator\n• 25% — VESTHETIC\n\nCez Telegram nepožadujeme pasy, bankové údaje ani intímne materiály.",
        "faq": "<b>FAQ</b>\n\n<b>Je potrebná prax?</b>\nNie, môžete začať od nuly.\n\n<b>Dá sa pracovať z domu?</b>\nÁno.\n\n<b>Vek?</b>\nStriktne 18+.",
        "apply_start": "<b>Žiadosť do VESTHETIC</b>\n\nVyplnenie potrvá niekoľko minút.\n\nPokračovaním potvrdzujete, že máte 18 rokov alebo viac a konáte dobrovoľne.",
        "age": "Máte už 18 rokov?", "age_no": "VESTHETIC spolupracuje iba s plnoletými osobami.",
        "name": "Ako sa voláte alebo aký pseudonym chcete používať?", "country": "V ktorej krajine sa teraz nachádzate?",
        "languages": "Akými jazykmi hovoríte?", "experience": "Máte skúsenosti s podobnými platformami?",
        "equipment": "Aké vybavenie máte? Napríklad telefón, PC, kamera, svetlo.",
        "schedule": "Koľko času denne alebo týždenne môžete venovať práci?", "contact": "Uveďte Telegram kontakt pre manažéra.",
        "source": "Ako ste sa dozvedeli o VESTHETIC?", "thanks": "<b>Žiadosť odoslaná ✅</b>\n\nĎakujeme! Manažér VESTHETIC vašu žiadosť posúdi a ozve sa vám.",
        "manager": "<b>Manažér VESTHETIC</b>\n\nKontakt: @VESTHETIC_manager"
    },
    "en": {
        "welcome": "<b>VESTHETIC | Digital Talent Agency</b>\n\nWe help adult online creators build and develop their careers on international platforms.\n\n18+ only • Voluntary • Global",
        "about": "<b>VESTHETIC</b>\n\nDigital Talent Agency for adult online creators.\n\n<b>Model:</b> 75% creator / 25% VESTHETIC\n\nPlatforms:\n• BongaCams\n• Stripchat\n• Chaturbate",
        "terms": "<b>Terms</b>\n\n• 18+ only\n• Participation is voluntary\n• Creator receives 75%\n• VESTHETIC receives 25%\n\nWe do not request passports, banking details or intimate material through Telegram.",
        "faq": "<b>FAQ</b>\n\n<b>Is experience required?</b>\nNo, you can start from zero.\n\n<b>Can I work from home?</b>\nYes.\n\n<b>Age?</b>\nStrictly 18+.",
        "apply_start": "<b>VESTHETIC application</b>\n\nIt takes a few minutes.\n\nBy continuing, you confirm that you are 18 or older and participating voluntarily.",
        "age": "Are you 18 years old or older?", "age_no": "VESTHETIC works only with adults.",
        "name": "What is your name or preferred pseudonym?", "country": "Which country are you currently in?",
        "languages": "Which languages do you speak?", "experience": "Do you have experience on similar platforms?",
        "equipment": "What equipment do you have? For example: phone, PC, camera, lighting.",
        "schedule": "How much time per day or week can you dedicate to the work?", "contact": "Provide a Telegram contact for the manager.",
        "source": "How did you hear about VESTHETIC?", "thanks": "<b>Application submitted ✅</b>\n\nThank you! A VESTHETIC manager will review your application and contact you.",
        "manager": "<b>VESTHETIC Manager</b>\n\nContact: @VESTHETIC_manager"
    }
}

def telegram(method, data=None):
    try:
        encoded = urllib.parse.urlencode(data or {}).encode("utf-8")
        req = urllib.request.Request(f"{TELEGRAM_API}/{method}", data=encoded if data is not None else None)
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print("Telegram API error:", exc)
        return None

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    return telegram("sendMessage", data)

def answer_callback(callback_id, text=""):
    return telegram("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})

def edit_message(chat_id, message_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    return telegram("editMessageText", data)

def language_keyboard():
    return {"inline_keyboard": [
        [{"text": "🇷🇺 Русский", "callback_data": "lang_ru"}, {"text": "🇺🇦 Українська", "callback_data": "lang_ua"}],
        [{"text": "🇸🇰 Slovenčina", "callback_data": "lang_sk"}, {"text": "🇬🇧 English", "callback_data": "lang_en"}]
    ]}

def main_keyboard(lang):
    labels = {
        "ru": ["ℹ️ О VESTHETIC", "📋 Условия", "❓ FAQ", "🚀 Подать заявку", "👤 Связаться с менеджером", "🌐 Язык"],
        "ua": ["ℹ️ Про VESTHETIC", "📋 Умови", "❓ FAQ", "🚀 Подати заявку", "👤 Зв'язатися з менеджером", "🌐 Мова"],
        "sk": ["ℹ️ O VESTHETIC", "📋 Podmienky", "❓ FAQ", "🚀 Poslať žiadosť", "👤 Kontaktovať manažéra", "🌐 Jazyk"],
        "en": ["ℹ️ About VESTHETIC", "📋 Terms", "❓ FAQ", "🚀 Apply", "👤 Contact manager", "🌐 Language"]
    }
    keys = ["about", "terms", "faq", "apply", "manager", "language"]
    return {"inline_keyboard": [[{"text": t, "callback_data": k}] for t, k in zip(labels.get(lang, labels["en"]), keys)]}

def back_keyboard(lang):
    label = {"ru": "◀️ Назад", "ua": "◀️ Назад", "sk": "◀️ Späť", "en": "◀️ Back"}.get(lang, "◀️ Back")
    return {"inline_keyboard": [[{"text": label, "callback_data": "home"}]]}

def age_keyboard(lang):
    yes, no = {"ru": ("✅ Да", "❌ Нет"), "ua": ("✅ Так", "❌ Ні"), "sk": ("✅ Áno", "❌ Nie"), "en": ("✅ Yes", "❌ No")}.get(lang, ("✅ Yes", "❌ No"))
    return {"inline_keyboard": [[{"text": yes, "callback_data": "age_yes"}, {"text": no, "callback_data": "age_no"}]]}

def admin_keyboard(app_id):
    return {"inline_keyboard": [
        [{"text": "🟢 Accept", "callback_data": f"status_accept_{app_id}"}, {"text": "🟡 In progress", "callback_data": f"status_progress_{app_id}"}],
        [{"text": "🔴 Reject", "callback_data": f"status_reject_{app_id}"}]
    ]}

def status_label(status):
    return {
        "accept": "🟢 Принята",
        "progress": "🟡 В работе",
        "reject": "🔴 Отклонена",
    }.get(status, "⚪ Новая")


def status_text(status, lang="ru"):
    texts = {
        "ru": {"accept": "Заявка принята.", "progress": "Заявка взята в работу.", "reject": "Заявка отклонена."},
        "ua": {"accept": "Заявку прийнято.", "progress": "Заявку взято в роботу.", "reject": "Заявку відхилено."},
        "sk": {"accept": "Žiadosť bola prijatá.", "progress": "Žiadosť je v spracovaní.", "reject": "Žiadosť bola zamietnutá."},
        "en": {"accept": "Application accepted.", "progress": "Application is now in progress.", "reject": "Application rejected."},
    }
    fallback = {
        "ru": "Статус заявки обновлён.",
        "ua": "Статус заявки оновлено.",
        "sk": "Stav žiadosti bol aktualizovaný.",
        "en": "Application status updated.",
    }
    return texts.get(lang, texts["en"]).get(status, fallback.get(lang, fallback["en"]))


def application_text(app_id, data):
    return (
        f"<b>ЗАЯВКА VESTHETIC #{app_id}</b>\n"
        f"👤 Имя: {data.get('name','-')}\n"
        f"🔞 Возраст: {'18+ подтверждён' if data.get('age_confirmed') else '-'}\n"
        f"🌍 Страна: {data.get('country','-')}\n"
        f"🗣 Языки: {data.get('languages','-')}\n"
        f"💼 Опыт: {data.get('experience','-')}\n"
        f"🖥 Оборудование: {data.get('equipment','-')}\n"
        f"🕐 График: {data.get('schedule','-')}\n"
        f"📱 Telegram: {data.get('contact','-')}\n"
        f"📣 Источник: {data.get('source','-')}\n\n"
        f"<b>Статус:</b> {status_label(data.get('status','new'))}"
    )


def notify_candidate(app_id, data, status):
    candidate_id = data.get("telegram_chat_id")
    if not candidate_id:
        return

    user = load_user(candidate_id)
    lang = user.get("lang", "en")
    send_message(candidate_id, f"<b>VESTHETIC</b>\n\n{status_text(status, lang)}")


def notify_admins(app_id, data):
    text = (
        f"<b>НОВАЯ ЗАЯВКА VESTHETIC #{app_id}</b>\n"
        f"👤 Имя: {data.get('name','-')}\n"
        f"🔞 Возраст: {'18+ подтверждён' if data.get('age_confirmed') else '-'}\n"
        f"🌍 Страна: {data.get('country','-')}\n"
        f"🗣 Языки: {data.get('languages','-')}\n"
        f"💼 Опыт: {data.get('experience','-')}\n"
        f"🖥 Оборудование: {data.get('equipment','-')}\n"
        f"🕐 График: {data.get('schedule','-')}\n"
        f"📱 Telegram: {data.get('contact','-')}\n"
        f"📣 Источник: {data.get('source','-')}\n\n"
        f"<b>Статус:</b> {status_label(data.get('status','new'))}"
    )
    recipients = list(dict.fromkeys(ADMIN_IDS + [MANAGER_ID]))
    for recipient_id in recipients:
        send_message(recipient_id, text, admin_keyboard(app_id))

def process_message(message):
    user_id = message.get("chat", {}).get("id")
    if not user_id:
        return

    text = message.get("text", "").strip()
    chat = message.get("chat", {})
    username = chat.get("username")

    u = load_user(user_id, username)
    lang = u["lang"]

    if text.startswith("/start"):
        u["state"] = None
        u["application"] = {}
        save_user(user_id, username, u)
        send_message(
            user_id,
            "Choose your language / Выберите язык:",
            language_keyboard(),
        )
        return

    state = u.get("state")
    order = [
        "name",
        "country",
        "languages",
        "experience",
        "equipment",
        "schedule",
        "contact",
        "source",
    ]

    if state and state.startswith("apply_") and state != "apply_age":
        field = state[6:]
        u["application"][field] = text

        if field in order and order.index(field) < len(order) - 1:
            nxt = order[order.index(field) + 1]
            u["state"] = "apply_" + nxt
            send_message(user_id, TEXTS[lang][nxt])

        elif field == "source":
            app = create_application(user_id, username, u["application"])

            if app is None:
                send_message(
                    user_id,
                    "Произошла ошибка при сохранении заявки. Пожалуйста, попробуйте ещё раз позже.",
                    main_keyboard(lang),
                )
                u["state"] = None
                return

            app_id = app["id"]
            notify_admins(app_id, app)

            u["state"] = None
            u["application"] = {}

            send_message(
                user_id,
                TEXTS[lang]["thanks"],
                main_keyboard(lang),
            )
        return

    send_message(
        user_id,
        TEXTS[lang]["welcome"],
        main_keyboard(lang),
    )


def process_callback(query):
    user_id = query.get("from", {}).get("id")
    data = query.get("data", "")
    callback_id = query.get("id")

    if not user_id:
        return

    username = query.get("from", {}).get("username")
    u = load_user(user_id, username)
    lang = u["lang"]

    answer_callback(callback_id)

    if data.startswith("lang_"):
        lang = data[5:] if data[5:] in TEXTS else "en"
        u["lang"] = lang
        u["state"] = None
        send_message(user_id, TEXTS[lang]["welcome"], main_keyboard(lang))

    elif data == "home":
        u["state"] = None
        send_message(user_id, TEXTS[lang]["welcome"], main_keyboard(lang))

    elif data == "language":
        send_message(user_id, "Choose language / Выберите язык:", language_keyboard())

    elif data in ("about", "terms", "faq", "manager"):
        send_message(user_id, TEXTS[lang][data], back_keyboard(lang))

    elif data == "apply":
        u["application"] = {}
        u["state"] = "apply_age"
        send_message(user_id, TEXTS[lang]["apply_start"], age_keyboard(lang))

    elif data == "age_yes":
        u["application"]["age"] = "18+ confirmed"
        u["state"] = "apply_name"
        send_message(user_id, TEXTS[lang]["name"])

    elif data == "age_no":
        u["state"] = None
        u["application"] = {}
        send_message(user_id, TEXTS[lang]["age_no"], main_keyboard(lang))

    elif data.startswith("status_") and user_id in STAFF_IDS:
        parts = data.split("_")
        if len(parts) != 3:
            answer_callback(callback_id, "Invalid action")
            return

        try:
            app_id = int(parts[2])
        except ValueError:
            answer_callback(callback_id, "Invalid application ID")
            return

        status = parts[1]
        if status not in ("accept", "progress", "reject"):
            answer_callback(callback_id, "Invalid status")
            return

        app = get_application(app_id)
        if app is None:
            answer_callback(callback_id, "Application not found")
            return

        updated = update_application_status(app_id, status)
        if updated is None:
            answer_callback(callback_id, "Database update failed")
            return

        app = updated
        answer_callback(callback_id, status_text(status, "ru"))

        message = query.get("message", {})
        message_chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")

        if message_chat_id and message_id:
            edit_message(
                message_chat_id,
                message_id,
                application_text(app_id, app),
                {"inline_keyboard": []},
            )

        notify_candidate(app_id, app, status)

        staff_notice = (
            f"<b>Заявка #{app_id} обновлена</b>\n"
            f"Статус: {status_label(status)}\n"
            f"Изменил: {user_id}"
        )

        for staff_id in STAFF_IDS:
            if staff_id != user_id:
                send_message(staff_id, staff_notice)

    save_user(user_id, username, u)



def require_admin(credentials: HTTPBasicCredentials):
    if not ADMIN_PANEL_PASSWORD:
        return False
    return (
        secrets.compare_digest(credentials.username, ADMIN_PANEL_USER)
        and secrets.compare_digest(credentials.password, ADMIN_PANEL_PASSWORD)
    )


def dashboard_html(apps):
    rows = []
    for app in apps:
        app_id = app.get("id")
        status = app.get("status", "new")
        label = status_label(status)
        rows.append(f"""
        <tr>
          <td><b>#{app_id}</b></td>
          <td>{html.escape(str(app.get("name") or "-"))}</td>
          <td>{html.escape(str(app.get("country") or "-"))}</td>
          <td>{html.escape(str(app.get("languages") or "-"))}</td>
          <td>{html.escape(str(app.get("experience") or "-"))}</td>
          <td>{html.escape(str(app.get("schedule") or "-"))}</td>
          <td>{label}</td>
          <td>
            <a href="/admin/application/{app_id}" style="display:inline-block;margin-right:8px;color:#fff;text-decoration:none;background:#222;border-radius:8px;padding:7px 9px">Подробнее</a>
            <form method="post" action="/admin/status" style="display:inline">
              <input type="hidden" name="id" value="{app_id}">
              <button name="status" value="accept">🟢</button>
              <button name="status" value="progress">🟡</button>
              <button name="status" value="reject">🔴</button>
            </form>
          </td>
        </tr>""")
    return """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VESTHETIC CRM</title>
<style>
body{font-family:system-ui;background:#0b0b0b;color:#eee;margin:0;padding:24px}
h1{letter-spacing:.08em}.wrap{overflow:auto}table{width:100%;border-collapse:collapse;min-width:1050px}
th,td{padding:12px;border-bottom:1px solid #292929;text-align:left}th{color:#999;font-size:12px;text-transform:uppercase}
button{border:0;border-radius:8px;padding:7px 9px;margin-right:4px;cursor:pointer;background:#222;color:#fff}
.badge{font-weight:700}.muted{color:#888}
</style></head><body>
<h1>VESTHETIC <span class="muted">CRM</span></h1>
<p class="muted">Заявки</p><div class="wrap"><table>
<thead><tr><th>ID</th><th>Имя</th><th>Страна</th><th>Языки</th><th>Опыт</th><th>График</th><th>Статус</th><th>Действия</th></tr></thead>
<tbody>""" + "".join(rows) + """</tbody></table></div></body></html>"""


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(credentials: HTTPBasicCredentials = __import__("fastapi").Depends(security)):
    if not require_admin(credentials):
        return HTMLResponse("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
    apps = supabase_request(
        "GET",
        "applications",
        query={"select":"*","order":"created_at.desc","limit":"100"},
    ) or []
    return HTMLResponse(dashboard_html(apps))


@app.get("/admin/application/{app_id}", response_class=HTMLResponse)
async def admin_application_detail(app_id: int, credentials: HTTPBasicCredentials = __import__("fastapi").Depends(security)):
    if not require_admin(credentials):
        return HTMLResponse("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})

    app = get_application(app_id)
    if app is None:
        return HTMLResponse("<h1>Заявка не найдена</h1><p><a href='/admin'>← К заявкам</a></p>", status_code=404)

    history = get_application_history(app_id)

    def val(key, fallback="-"):
        value = app.get(key)
        return html.escape(str(value if value not in (None, "") else fallback))

    status = status_label(app.get("status", "new"))
    created_at = val("created_at")
    updated_at = val("updated_at")
    username = app.get("telegram_username")
    telegram_username = f"@{html.escape(str(username))}" if username else "-"
    age = "18+ подтверждён" if app.get("age_confirmed") else "Не подтверждён"

    history_rows = []
    for item in history:
        old_status = status_label(item.get("old_status", "new")) if item.get("old_status") else "—"
        new_status = status_label(item.get("new_status", "new"))
        changed_by = item.get("changed_by_telegram_id")
        changed_by_text = html.escape(str(changed_by)) if changed_by else "Система"
        created = html.escape(str(item.get("created_at") or "-"))
        history_rows.append(
            f"<tr><td>{created}</td><td>{old_status}</td><td>{new_status}</td><td>{changed_by_text}</td></tr>"
        )

    history_html = "".join(history_rows) or "<tr><td colspan='4' class='muted'>История пока пуста</td></tr>"

    return HTMLResponse(f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Заявка #{app_id} — VESTHETIC CRM</title>
<style>
body{{font-family:system-ui;background:#0b0b0b;color:#eee;margin:0;padding:24px;max-width:1100px;margin:auto}}
h1{{letter-spacing:.04em}}a{{color:#fff}}.muted{{color:#888}}
.card{{background:#111;border:1px solid #292929;border-radius:14px;padding:20px;margin:18px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}}
.item{{border-bottom:1px solid #292929;padding:10px 0}}.label{{display:block;color:#888;font-size:12px;text-transform:uppercase;margin-bottom:4px}}
.badge{{font-weight:700}}table{{width:100%;border-collapse:collapse}}th,td{{padding:11px;border-bottom:1px solid #292929;text-align:left}}
button{{border:0;border-radius:8px;padding:8px 10px;margin-right:5px;cursor:pointer;background:#222;color:#fff}}
</style></head><body>
<p><a href="/admin">← К заявкам</a></p>
<h1>Заявка #{app_id}</h1>

<div class="card">
  <div class="grid">
    <div class="item"><span class="label">Имя / псевдоним</span>{val("name")}</div>
    <div class="item"><span class="label">Telegram username</span>{telegram_username}</div>
    <div class="item"><span class="label">Telegram ID</span>{val("telegram_chat_id")}</div>
    <div class="item"><span class="label">Возраст</span>{age}</div>
    <div class="item"><span class="label">Страна</span>{val("country")}</div>
    <div class="item"><span class="label">Языки</span>{val("languages")}</div>
    <div class="item"><span class="label">Опыт</span>{val("experience")}</div>
    <div class="item"><span class="label">Оборудование</span>{val("equipment")}</div>
    <div class="item"><span class="label">График</span>{val("schedule")}</div>
    <div class="item"><span class="label">Контакт</span>{val("contact")}</div>
    <div class="item"><span class="label">Источник</span>{val("source")}</div>
    <div class="item"><span class="label">Создана</span>{created_at}</div>
    <div class="item"><span class="label">Обновлена</span>{updated_at}</div>
    <div class="item"><span class="label">Текущий статус</span><span class="badge">{status}</span></div>
  </div>
</div>

<div class="card">
  <h2>Изменить статус</h2>
  <form method="post" action="/admin/status">
    <input type="hidden" name="id" value="{app_id}">
    <button name="status" value="accept">🟢 Принять</button>
    <button name="status" value="progress">🟡 В работу</button>
    <button name="status" value="reject">🔴 Отклонить</button>
  </form>
</div>

<div class="card">
  <h2>История статусов</h2>
  <div style="overflow:auto"><table>
    <thead><tr><th>Дата</th><th>Было</th><th>Стало</th><th>Изменил</th></tr></thead>
    <tbody>{history_html}</tbody>
  </table></div>
</div>
</body></html>""")



@app.post("/admin/status")
async def admin_status(request: Request, credentials: HTTPBasicCredentials = __import__("fastapi").Depends(security)):
    if not require_admin(credentials):
        return PlainTextResponse("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})

    try:
        raw = await request.body()
        form = urllib.parse.parse_qs(raw.decode("utf-8"), keep_blank_values=True)
        app_id_raw = (form.get("id") or [""])[0]
        status = (form.get("status") or [""])[0]

        try:
            app_id = int(app_id_raw)
        except (TypeError, ValueError):
            return PlainTextResponse("Invalid application ID", status_code=400)

        if status not in ("accept", "progress", "reject"):
            return PlainTextResponse("Invalid status", status_code=400)

        updated = update_application_status(app_id, status)
        if updated is None:
            return PlainTextResponse("Application not found or update failed", status_code=404)

        notify_candidate(app_id, updated, status)
        return RedirectResponse("/admin", status_code=303)

    except Exception as exc:
        print("Admin status error:", repr(exc))
        return PlainTextResponse(f"Admin status error: {exc}", status_code=500)


@app.get("/api")
async def api_root():
    return {"status": "ok", "service": "VESTHETIC"}

@app.get("/api/health")
async def health():
    return {"ok": True}

@app.post("/api/webhook")
async def webhook(request: Request):
    try:
        update = await request.json()
        if update.get("callback_query"):
            process_callback(update["callback_query"])
        elif update.get("message"):
            process_message(update["message"])
        return {"ok": True}
    except Exception as exc:
        print("Webhook error:", exc)
        return {"ok": False, "error": str(exc)}
