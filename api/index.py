from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import urllib.request
import urllib.parse
import json
import os

app = FastAPI()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

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

def notify_admins(app_id, data):
    text = (
        f"<b>NEW VESTHETIC APPLICATION #{app_id}</b>\n"
        f"Name: {data.get('name','-')}\nAge: {data.get('age','-')}\nCountry: {data.get('country','-')}\n"
        f"Languages: {data.get('languages','-')}\nExperience: {data.get('experience','-')}\n"
        f"Equipment: {data.get('equipment','-')}\nSchedule: {data.get('schedule','-')}\n"
        f"Telegram: {data.get('contact','-')}\nSource: {data.get('source','-')}"
    )
    recipients = list(dict.fromkeys(ADMIN_IDS + [MANAGER_ID]))
    for recipient_id in recipients:
        send_message(recipient_id, text, admin_keyboard(app_id))

def process_message(message):
    global next_application_id
    user_id = message.get("chat", {}).get("id")
    if not user_id:
        return
    text = message.get("text", "").strip()
    u = users.setdefault(user_id, {"lang": "en", "state": None, "application": {}})
    lang = u["lang"]

    if text.startswith("/start"):
        u["state"] = None
        send_message(user_id, "Choose your language / Выберите язык:", language_keyboard())
        return

    state = u.get("state")
    order = ["name", "country", "languages", "experience", "equipment", "schedule", "contact", "source"]
    if state and state.startswith("apply_") and state != "apply_age":
        field = state[6:]
        u["application"][field] = text
        if field in order and order.index(field) < len(order) - 1:
            nxt = order[order.index(field) + 1]
            u["state"] = "apply_" + nxt
            send_message(user_id, TEXTS[lang][nxt])
        elif field == "source":
            app_id = next_application_id
            next_application_id += 1
            applications[app_id] = dict(u["application"])
            notify_admins(app_id, applications[app_id])
            u["state"] = None
            send_message(user_id, TEXTS[lang]["thanks"], main_keyboard(lang))
        return

    send_message(user_id, TEXTS[lang]["welcome"], main_keyboard(lang))

def process_callback(query):
    user_id = query.get("from", {}).get("id")
    data = query.get("data", "")
    callback_id = query.get("id")
    if not user_id:
        return
    u = users.setdefault(user_id, {"lang": "en", "state": None, "application": {}})
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
        send_message(user_id, TEXTS[lang]["age_no"], main_keyboard(lang))
    elif data.startswith("status_") and user_id in ADMIN_IDS:
        parts = data.split("_")
        if len(parts) == 3:
            try:
                app_id = int(parts[2])
                if app_id in applications:
                    applications[app_id]["status"] = parts[1]
                    answer_callback(callback_id, f"Status: {parts[1]}")
            except ValueError:
                pass

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
