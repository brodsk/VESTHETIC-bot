import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = [
    int(x.strip())
    for x in os.environ.get("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]
MANAGER_USERNAME = os.environ.get("MANAGER_USERNAME", "VESTHETIC_manager")

# Temporary in-memory storage.
# For production, replace this with Supabase/Postgres.
applications = {}
user_states = {}

TEXTS = {
    "ru": {
        "choose": "Выберите язык:",
        "welcome": (
            "💎 VESTHETIC | Digital Talent Agency\n\n"
            "Мы работаем с совершеннолетними онлайн-креаторами "
            "по всему миру.\n\n"
            "Выберите действие:"
        ),
        "about": (
            "💎 О VESTHETIC\n\n"
            "VESTHETIC помогает совершеннолетним онлайн-креаторам "
            "запускаться и развиваться на международных платформах.\n\n"
            "Работа добровольная, удалённая и с гибким графиком."
        ),
        "terms": (
            "💰 Условия\n\n"
            "Creator: 75%\n"
            "VESTHETIC: 25%\n\n"
            "Точные выплаты зависят от платформы и условий "
            "сотрудничества. Все условия согласовываются заранее."
        ),
        "faq": (
            "❓ FAQ\n\n"
            "• 18+ обязательно.\n"
            "• Опыт не обязателен.\n"
            "• Можно работать из дома.\n"
            "• График выбираете вы.\n"
            "• Мы помогаем с запуском и настройкой.\n\n"
            "Не отправляйте сюда паспорт, банковские данные "
            "или интимные материалы."
        ),
        "apply": (
            "📝 Начинаем короткую заявку.\n\n"
            "Отвечайте на вопросы по одному.\n\n"
            "Не отправляйте паспорт, банковские данные или "
            "другие документы. Проверка личности выполняется "
            "через официальные процедуры платформ."
        ),
        "name": "Как вас зовут или какой псевдоним использовать?",
        "age": "Подтверждаете, что вам 18 лет или больше?",
        "country": "В какой стране вы сейчас находитесь?",
        "languages": "Какие языки вы знаете?",
        "experience": "Есть ли у вас опыт работы онлайн-креатором/моделью?",
        "equipment": "Какое оборудование у вас есть?",
        "schedule": "Какой график вам удобен?",
        "contact": "Ваш Telegram username для связи с менеджером (например @username):",
        "source": "Где вы узнали о VESTHETIC?",
        "done": (
            "✅ Заявка получена.\n\n"
            "Менеджер VESTHETIC свяжется с вами после рассмотрения."
        ),
        "noage": "Для сотрудничества с VESTHETIC требуется возраст 18+.",
        "cancel": "Заявка отменена. Вы вернулись в главное меню.",
        "manager": f"👩‍💼 Менеджер: @{MANAGER_USERNAME}",
    },

    "ua": {
        "choose": "Оберіть мову:",
        "welcome": (
            "💎 VESTHETIC | Digital Talent Agency\n\n"
            "Ми працюємо з повнолітніми онлайн-креаторами "
            "з усього світу.\n\n"
            "Оберіть дію:"
        ),
        "about": (
            "💎 Про VESTHETIC\n\n"
            "VESTHETIC допомагає повнолітнім онлайн-креаторам "
            "запускатися та розвиватися на міжнародних платформах.\n\n"
            "Робота добровільна, віддалена та з гнучким графіком."
        ),
        "terms": (
            "💰 Умови\n\n"
            "Creator: 75%\n"
            "VESTHETIC: 25%\n\n"
            "Точні виплати залежать від платформи та умов "
            "співпраці. Усі умови погоджуються заздалегідь."
        ),
        "faq": (
            "❓ FAQ\n\n"
            "• 18+ обов'язково.\n"
            "• Досвід не обов'язковий.\n"
            "• Можна працювати з дому.\n"
            "• Графік обираєте ви.\n"
            "• Ми допомагаємо із запуском.\n\n"
            "Не надсилайте сюди паспорт, банківські дані "
            "або інтимні матеріали."
        ),
        "apply": (
            "📝 Починаємо коротку заявку.\n\n"
            "Відповідайте на запитання по одному.\n\n"
            "Не надсилайте паспорт, банківські дані або документи."
        ),
        "name": "Як вас звати або який псевдонім використовувати?",
        "age": "Підтверджуєте, що вам 18 років або більше?",
        "country": "У якій країні ви зараз перебуваєте?",
        "languages": "Які мови ви знаєте?",
        "experience": "Чи маєте ви досвід роботи онлайн-креатором/моделлю?",
        "equipment": "Яке обладнання у вас є?",
        "schedule": "Який графік вам зручний?",
        "contact": "Ваш Telegram username для зв'язку з менеджером (наприклад @username):",
        "source": "Де ви дізналися про VESTHETIC?",
        "done": "✅ Заявку отримано.\n\nМенеджер VESTHETIC зв'яжеться з вами після розгляду.",
        "noage": "Для співпраці з VESTHETIC необхідно мати 18+.",
        "cancel": "Заявку скасовано. Ви повернулися до головного меню.",
        "manager": f"👩‍💼 Менеджер: @{MANAGER_USERNAME}",
    },

    "sk": {
        "choose": "Vyberte jazyk:",
        "welcome": (
            "💎 VESTHETIC | Digital Talent Agency\n\n"
            "Spolupracujeme s plnoletými online tvorcami "
            "z celého sveta.\n\n"
            "Vyberte možnosť:"
        ),
        "about": (
            "💎 O VESTHETIC\n\n"
            "VESTHETIC pomáha plnoletým online tvorcom "
            "začať a rozvíjať sa na medzinárodných platformách.\n\n"
            "Spolupráca je dobrovoľná, na diaľku a s flexibilným časom."
        ),
        "terms": (
            "💰 Podmienky\n\n"
            "Creator: 75%\n"
            "VESTHETIC: 25%\n\n"
            "Presné podmienky závisia od platformy a dohody."
        ),
        "faq": (
            "❓ FAQ\n\n"
            "• 18+ je povinné.\n"
            "• Skúsenosti nie sú potrebné.\n"
            "• Práca z domu.\n"
            "• Flexibilný pracovný čas.\n"
            "• Pomáhame so začiatkom.\n\n"
            "Neposielajte sem pas, bankové údaje ani intímny obsah."
        ),
        "apply": (
            "📝 Začíname krátku žiadosť.\n\n"
            "Odpovedajte na otázky postupne."
        ),
        "name": "Ako sa voláte alebo aký pseudonym chcete používať?",
        "age": "Potvrdzujete, že máte 18 rokov alebo viac?",
        "country": "V ktorej krajine sa momentálne nachádzate?",
        "languages": "Akými jazykmi hovoríte?",
        "experience": "Máte skúsenosti s online tvorbou alebo modelingom?",
        "equipment": "Aké vybavenie máte?",
        "schedule": "Aký pracovný čas vám vyhovuje?",
        "contact": "Váš Telegram username pre kontakt s manažérom (napr. @username):",
        "source": "Ako ste sa dozvedeli o VESTHETIC?",
        "done": "✅ Žiadosť bola prijatá.\n\nManažér VESTHETIC vás bude kontaktovať.",
        "noage": "Pre spoluprácu s VESTHETIC musíte mať 18 rokov alebo viac.",
        "cancel": "Žiadosť bola zrušená. Vrátili ste sa do hlavného menu.",
        "manager": f"👩‍💼 Manažér: @{MANAGER_USERNAME}",
    },

    "en": {
        "choose": "Choose your language:",
        "welcome": (
            "💎 VESTHETIC | Digital Talent Agency\n\n"
            "We work with adult online creators from around the world.\n\n"
            "Choose an option:"
        ),
        "about": (
            "💎 About VESTHETIC\n\n"
            "VESTHETIC helps adult online creators launch and "
            "develop on international platforms.\n\n"
            "Cooperation is voluntary, remote and flexible."
        ),
        "terms": (
            "💰 Terms\n\n"
            "Creator: 75%\n"
            "VESTHETIC: 25%\n\n"
            "Exact payouts depend on the platform and cooperation terms."
        ),
        "faq": (
            "❓ FAQ\n\n"
            "• 18+ required.\n"
            "• No previous experience required.\n"
            "• Work from home.\n"
            "• Flexible schedule.\n"
            "• We help with setup and launch.\n\n"
            "Do not send passports, banking information or intimate material here."
        ),
        "apply": (
            "📝 Let's start a short application.\n\n"
            "Please answer each question one at a time."
        ),
        "name": "What is your name or preferred nickname?",
        "age": "Do you confirm that you are 18 years old or older?",
        "country": "Which country are you currently located in?",
        "languages": "Which languages do you speak?",
        "experience": "Do you have experience as an online creator/model?",
        "equipment": "What equipment do you have?",
        "schedule": "What schedule works for you?",
        "contact": "Your Telegram username for manager contact (for example @username):",
        "source": "How did you hear about VESTHETIC?",
        "done": "✅ Application received.\n\nA VESTHETIC manager will contact you after review.",
        "noage": "You must be 18 or older to work with VESTHETIC.",
        "cancel": "Application cancelled. You are back in the main menu.",
        "manager": f"👩‍💼 Manager: @{MANAGER_USERNAME}",
    },
}


def telegram_api(method, data):
    """Call Telegram Bot API."""
    if not BOT_TOKEN:
        return None

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    encoded = urllib.parse.urlencode(data).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
    }

    if keyboard:
        data["reply_markup"] = json.dumps(
            keyboard,
            ensure_ascii=False
        )

    return telegram_api("sendMessage", data)


def answer_callback(callback_id):
    return telegram_api(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_id
        }
    )


def edit_message(chat_id, message_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    }

    if keyboard:
        data["reply_markup"] = json.dumps(
            keyboard,
            ensure_ascii=False
        )

    return telegram_api("editMessageText", data)


def main_menu(lang):
    labels = {
        "ru": [
            ["💎 О VESTHETIC", "💰 Условия"],
            ["❓ FAQ", "📝 Подать заявку"],
            ["👩‍💼 Менеджер", "🌐 Язык"],
        ],
        "ua": [
            ["💎 Про VESTHETIC", "💰 Умови"],
            ["❓ FAQ", "📝 Подати заявку"],
            ["👩‍💼 Менеджер", "🌐 Мова"],
        ],
        "sk": [
            ["💎 O VESTHETIC", "💰 Podmienky"],
            ["❓ FAQ", "📝 Žiadosť"],
            ["👩‍💼 Manažér", "🌐 Jazyk"],
        ],
        "en": [
            ["💎 About VESTHETIC", "💰 Terms"],
            ["❓ FAQ", "📝 Apply"],
            ["👩‍💼 Manager", "🌐 Language"],
        ],
    }

    return {
        "keyboard": labels.get(lang, labels["en"]),
        "resize_keyboard": True,
        "is_persistent": True,
    }


def language_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🇷🇺 Русский", "callback_data": "lang:ru"},
                {"text": "🇺🇦 Українська", "callback_data": "lang:ua"},
            ],
            [
                {"text": "🇸🇰 Slovenčina", "callback_data": "lang:sk"},
                {"text": "🇬🇧 English", "callback_data": "lang:en"},
            ],
        ]
    }


def age_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Да / Yes", "callback_data": "age:yes"},
                {"text": "❌ Нет / No", "callback_data": "age:no"},
            ]
        ]
    }


def admin_keyboard(app_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🟢 Accept",
                    "callback_data": f"status:{app_id}:accepted"
                },
                {
                    "text": "🟡 In progress",
                    "callback_data": f"status:{app_id}:in_progress"
                },
            ],
            [
                {
                    "text": "🔴 Reject",
                    "callback_data": f"status:{app_id}:rejected"
                }
            ]
        ]
    }


def get_lang(user_id):
    state = user_states.get(user_id)

    if state and state.get("lang"):
        return state["lang"]

    return None


def start_application(user_id, lang):
    user_states[user_id] = {
        "lang": lang,
        "step": "name",
        "application": {}
    }

    send_message(
        user_id,
        TEXTS[lang]["apply"]
    )

    send_message(
        user_id,
        TEXTS[lang]["name"]
    )


def process_application_text(user_id, text):
    state = user_states.get(user_id)

    if not state:
        return False

    step = state.get("step")
    lang = state.get("lang")
    app = state.get("application")

    if step == "name":
        app["name"] = text
        state["step"] = "country"

        send_message(
            user_id,
            TEXTS[lang]["country"]
        )
        return True

    if step == "country":
        app["country"] = text
        state["step"] = "languages"

        send_message(
            user_id,
            TEXTS[lang]["languages"]
        )
        return True

    if step == "languages":
        app["languages"] = text
        state["step"] = "experience"

        send_message(
            user_id,
            TEXTS[lang]["experience"]
        )
        return True

    if step == "experience":
        app["experience"] = text
        state["step"] = "equipment"

        send_message(
            user_id,
            TEXTS[lang]["equipment"]
        )
        return True

    if step == "equipment":
        app["equipment"] = text
        state["step"] = "schedule"

        send_message(
            user_id,
            TEXTS[lang]["schedule"]
        )
        return True

    if step == "schedule":
        app["schedule"] = text
        state["step"] = "contact"

        send_message(
            user_id,
            TEXTS[lang]["contact"]
        )
        return True

    if step == "contact":
        app["contact"] = text
        state["step"] = "source"

        send_message(
            user_id,
            TEXTS[lang]["source"]
        )
        return True

    if step == "source":
        app["source"] = text

        application_id = len(applications) + 1

        applications[application_id] = {
            "id": application_id,
            "created_at": datetime.utcnow().isoformat(),
            "telegram_id": user_id,
            "name": app.get("name", ""),
            "country": app.get("country", ""),
            "languages": app.get("languages", ""),
            "experience": app.get("experience", ""),
            "equipment": app.get("equipment", ""),
            "schedule": app.get("schedule", ""),
            "contact": app.get("contact", ""),
            "source": app.get("source", ""),
            "status": "new",
            "language": lang,
        }

        send_message(
            user_id,
            TEXTS[lang]["done"],
            main_menu(lang)
        )

        notify_admins(applications[application_id])

        del user_states[user_id]

        return True

    return False


def notify_admins(app):
    text = (
        "📥 НОВАЯ ЗАЯВКА VESTHETIC\n\n"
        f"ID: #{app['id']}\n"
        f"Дата: {app['created_at']}\n\n"
        f"👤 Имя/псевдоним: {app['name']}\n"
        f"🌍 Страна: {app['country']}\n"
        f"🗣 Языки: {app['languages']}\n"
        f"💻 Опыт: {app['experience']}\n"
        f"🖥 Оборудование: {app['equipment']}\n"
        f"🕐 График: {app['schedule']}\n"
        f"📱 Контакт: {app['contact']}\n"
        f"📣 Источник: {app['source']}\n\n"
        f"Статус: {app['status']}"
    )

    for admin_id in ADMIN_IDS:
        send_message(
            admin_id,
            text,
            admin_keyboard(app["id"])
        )


def handle_callback(callback):
    callback_id = callback.get("id")
    data = callback.get("data", "")
    message = callback.get("message", {})
    chat = message.get("chat", {})
    user = callback.get("from", {})

    chat_id = chat.get("id")
    user_id = user.get("id")

    answer_callback(callback_id)

    if data.startswith("lang:"):
        lang = data.split(":", 1)[1]

        user_states[user_id] = {
            "lang": lang,
            "step": None,
            "application": {}
        }

        send_message(
            chat_id,
            TEXTS[lang]["welcome"],
            main_menu(lang)
        )

        return

    if data == "age:yes":
        state = user_states.get(user_id)

        if not state:
            return

        lang = state.get("lang", "en")

        state["application"]["age_confirmed"] = True
        state["step"] = "country"

        send_message(
            chat_id,
            TEXTS[lang]["country"]
        )

        return

    if data == "age:no":
        lang = get_lang(user_id) or "en"

        user_states.pop(user_id, None)

        send_message(
            chat_id,
            TEXTS[lang]["noage"],
            main_menu(lang)
        )

        return

    if data.startswith("status:"):
        parts = data.split(":")

        if len(parts) != 3:
            return

        try:
            app_id = int(parts[1])
        except ValueError:
            return

        new_status = parts[2]

        if app_id not in applications:
            return

        app = applications[app_id]

        if new_status == "accepted":
            app["status"] = "accepted"
            status_text = "🟢 ACCEPTED"
        elif new_status == "in_progress":
            app["status"] = "in_progress"
            status_text = "🟡 IN PROGRESS"
        elif new_status == "rejected":
            app["status"] = "rejected"
            status_text = "🔴 REJECTED"
        else:
            return

        new_text = (
            "📥 ЗАЯВКА VESTHETIC\n\n"
            f"ID: #{app['id']}\n"
            f"👤 {app['name']}\n"
            f"🌍 {app['country']}\n"
            f"🗣 {app['languages']}\n"
            f"💻 {app['experience']}\n"
            f"🖥 {app['equipment']}\n"
            f"🕐 {app['schedule']}\n"
            f"📱 {app['contact']}\n"
            f"📣 {app['source']}\n\n"
            f"Статус: {status_text}"
        )

        edit_message(
            chat_id,
            message.get("message_id"),
            new_text,
            admin_keyboard(app_id)
        )

        return


def handle_message(message):
    chat = message.get("chat", {})
    user = message.get("from", {})

    chat_id = chat.get("id")
    user_id = user.get("id")
    text = message.get("text", "")

    if not chat_id or not user_id:
        return

    if text == "/start":
        user_states.pop(user_id, None)

        send_message(
            chat_id,
            "🌐 Choose your language / Выберите язык / Оберіть мову / Vyberte jazyk:",
            language_keyboard()
        )

        return

    if text == "/cancel":
        lang = get_lang(user_id) or "en"

        user_states.pop(user_id, None)

        send_message(
            chat_id,
            TEXTS[lang]["cancel"],
            main_menu(lang)
        )

        return

    lang = get_lang(user_id)

    if not lang:
        send_message(
            chat_id,
            "🌐 Choose your language:",
            language_keyboard()
        )
        return

    state = user_states.get(user_id)

    if state and state.get("step"):
        process_application_text(user_id, text)
        return

    # Main menu
    if text in [
        "💎 О VESTHETIC",
        "💎 Про VESTHETIC",
        "💎 O VESTHETIC",
        "💎 About VESTHETIC"
    ]:
        send_message(
            chat_id,
            TEXTS[lang]["about"],
            main_menu(lang)
        )
        return

    if text in [
        "💰 Условия",
        "💰 Умови",
        "💰 Podmienky",
        "💰 Terms"
    ]:
        send_message(
            chat_id,
            TEXTS[lang]["terms"],
            main_menu(lang)
        )
        return

    if text == "❓ FAQ":
        send_message(
            chat_id,
            TEXTS[lang]["faq"],
            main_menu(lang)
        )
        return

    if text in [
        "📝 Подать заявку",
        "📝 Подати заявку",
        "📝 Žiadosť",
        "📝 Apply"
    ]:
        user_states[user_id] = {
            "lang": lang,
            "step": "name",
            "application": {}
        }

        send_message(
            chat_id,
            TEXTS[lang]["apply"]
        )

        send_message(
            chat_id,
            TEXTS[lang]["name"]
        )

        return

    if text in [
        "👩‍💼 Менеджер",
        "👩‍💼 Manager",
        "👩‍💼 Manažer",
        "👩‍💼 Manažér"
    ]:
        send_message(
            chat_id,
            TEXTS[lang]["manager"],
            main_menu(lang)
        )
        return

    if text in [
        "🌐 Язык",
        "🌐 Мова",
        "🌐 Jazyk",
        "🌐 Language"
    ]:
        send_message(
            chat_id,
            TEXTS[lang]["choose"],
            language_keyboard()
        )
        return

    send_message(
        chat_id,
        TEXTS[lang]["welcome"],
        main_menu(lang)
    )


def handler(request):
    """
    Vercel Python serverless function entry point.
    """

    if request.method == "GET":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/plain; charset=utf-8"
            },
            "body": "VESTHETIC bot is running."
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {
                "Content-Type": "text/plain; charset=utf-8"
            },
            "body": "Method Not Allowed"
        }

    try:
        body = request.body

        if isinstance(body, bytes):
            body = body.decode("utf-8")

        update = json.loads(body)

        if "callback_query" in update:
            handle_callback(update["callback_query"])

        elif "message" in update:
            handle_message(update["message"])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "ok": True
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "ok": False,
                "error": str(e)
            })
        }
