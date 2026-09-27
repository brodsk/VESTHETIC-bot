from fastapi import FastAPI, Request, Depends
from fastapi.responses import PlainTextResponse, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import html
import urllib.request
import urllib.parse
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

app = FastAPI()
security = HTTPBasic()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xtxqslzublggqhctmjoa.supabase.co").rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ADMIN_PANEL_USER = os.environ.get("ADMIN_PANEL_USER", "admin")
ADMIN_PANEL_PASSWORD = os.environ.get("ADMIN_PANEL_PASSWORD", "")

ADMIN_IDS = [625577962]
MANAGER_ID = 8965656829
MANAGER_USERNAME = "VESTHETIC_manager"
STAFF_IDS = list(dict.fromkeys(ADMIN_IDS + [MANAGER_ID]))
CRM_ACTOR_ID = ADMIN_IDS[0] if ADMIN_IDS else MANAGER_ID
CRM_TIMEZONE = ZoneInfo("Europe/Bratislava")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

STATUS_ORDER = ["new", "progress", "contacted", "interview", "registration", "active", "reject"]
STATUS_LABELS = {
    "new": "⚪ Новая",
    "progress": "🟡 В работе",
    "contacted": "💬 Связались",
    "interview": "🎙 Интервью",
    "registration": "📝 Регистрация",
    "active": "🟢 Активна",
    "accept": "🟢 Принята",
    "reject": "🔴 Отклонена",
}
STATUS_TEXTS = {
    "ru": {
        "progress": "Заявка взята в работу.",
        "contacted": "Менеджер связался с вами.",
        "interview": "Следующий этап — интервью с менеджером.",
        "registration": "Мы переходим к регистрации на платформе.",
        "active": "Ваша заявка одобрена, и вы можете переходить к работе.",
        "accept": "Заявка принята.",
        "reject": "Заявка отклонена.",
    },
    "ua": {
        "progress": "Заявку взято в роботу.",
        "contacted": "Менеджер зв'язався з вами.",
        "interview": "Наступний етап — інтерв'ю з менеджером.",
        "registration": "Ми переходимо до реєстрації на платформі.",
        "active": "Вашу заявку схвалено, і ви можете переходити до роботи.",
        "accept": "Заявку прийнято.",
        "reject": "Заявку відхилено.",
    },
    "sk": {
        "progress": "Žiadosť je v spracovaní.",
        "contacted": "Manažér vás kontaktoval.",
        "interview": "Ďalším krokom je rozhovor s manažérom.",
        "registration": "Prechádzame k registrácii na platforme.",
        "active": "Vaša žiadosť bola schválená a môžete prejsť k práci.",
        "accept": "Žiadosť bola prijatá.",
        "reject": "Žiadosť bola zamietnutá.",
    },
    "en": {
        "progress": "Your application is now in progress.",
        "contacted": "A manager has contacted you.",
        "interview": "The next step is an interview with the manager.",
        "registration": "We are moving to platform registration.",
        "active": "Your application has been approved and you can move on to work.",
        "accept": "Application accepted.",
        "reject": "Application rejected.",
    },
}

TEXTS = {
    "ru": {
        "welcome": "<b>VESTHETIC | Digital Talent Agency</b>\n\nМы помогаем совершеннолетним онлайн-креаторам строить и развивать карьеру на международных платформах.\n\n18+ only • Voluntary • Global",
        "about": "<b>VESTHETIC</b>\n\nDigital Talent Agency для взрослых онлайн-креаторов.\n\n<b>Модель:</b> 75% creator / 25% VESTHETIC\n\nПлатформы:\n• BongaCams\n• Stripchat\n• Chaturbate",
        "terms": "<b>Условия</b>\n\n• Только 18+\n• Участие исключительно добровольное\n• 75% дохода получает creator\n• 25% — VESTHETIC\n\nМы не запрашиваем паспорта, банковские данные или интимные материалы через Telegram.",
        "faq": "<b>FAQ</b>\n\n<b>Нужен ли опыт?</b>\nНет, можно начать с нуля.\n\n<b>Можно работать из дома?</b>\nДа.\n\n<b>Возраст?</b>\nСтрого 18+.",
        "apply_start": "<b>Заявка в VESTHETIC</b>\n\nЗаполнение займёт несколько минут.\n\nПродолжая, вы подтверждаете, что вам 18 лет или больше и вы действуете добровольно.",
        "age": "Вам уже исполнилось 18 лет?",
        "age_no": "К сожалению, VESTHETIC работает только с совершеннолетними.",
        "name": "Как вас зовут или какой псевдоним вы хотели бы использовать?",
        "country": "В какой стране вы сейчас находитесь?",
        "languages": "Какими языками вы владеете?",
        "experience": "Есть ли у вас опыт работы на подобных платформах?",
        "equipment": "Какое оборудование у вас есть? Например: телефон, ПК, камера, свет.",
        "schedule": "Сколько времени в день или неделю вы готовы уделять работе?",
        "contact": "Укажите Telegram-контакт для связи с менеджером.",
        "source": "Откуда вы узнали о VESTHETIC?",
        "thanks": "<b>Заявка отправлена ✅</b>\n\nСпасибо! Менеджер VESTHETIC рассмотрит вашу заявку и свяжется с вами.",
        "manager": "<b>Менеджер VESTHETIC</b>\n\nСвязаться: @VESTHETIC_manager",
    },
    "ua": {
        "welcome": "<b>VESTHETIC | Digital Talent Agency</b>\n\nМи допомагаємо повнолітнім онлайн-креаторам розвивати кар'єру на міжнародних платформах.\n\n18+ only • Voluntary • Global",
        "about": "<b>VESTHETIC</b>\n\nDigital Talent Agency для дорослих онлайн-креаторів.\n\n<b>Модель:</b> 75% creator / 25% VESTHETIC\n\nПлатформи:\n• BongaCams\n• Stripchat\n• Chaturbate",
        "terms": "<b>Умови</b>\n\n• Тільки 18+\n• Участь виключно добровільна\n• 75% доходу отримує creator\n• 25% — VESTHETIC",
        "faq": "<b>FAQ</b>\n\n<b>Чи потрібен досвід?</b>\nНі, можна почати з нуля.\n\n<b>Можна працювати з дому?</b>\nТак.\n\n<b>Вік?</b>\nСтрого 18+.",
        "apply_start": "<b>Заявка в VESTHETIC</b>\n\nЗаповнення займе кілька хвилин.\n\nПродовжуючи, ви підтверджуєте, що вам 18 років або більше та дієте добровільно.",
        "age": "Вам вже виповнилося 18 років?",
        "age_no": "На жаль, VESTHETIC працює лише з повнолітніми.",
        "name": "Як вас звати або який псевдонім ви хотіли б використовувати?",
        "country": "У якій країні ви зараз перебуваєте?",
        "languages": "Якими мовами ви володієте?",
        "experience": "Чи маєте ви досвід роботи на подібних платформах?",
        "equipment": "Яке обладнання у вас є? Наприклад: телефон, ПК, камера, світло.",
        "schedule": "Скільки часу на день або тиждень ви можете приділяти роботі?",
        "contact": "Вкажіть Telegram-контакт для зв'язку з менеджером.",
        "source": "Звідки ви дізналися про VESTHETIC?",
        "thanks": "<b>Заявку надіслано ✅</b>\n\nДякуємо! Менеджер VESTHETIC розгляне вашу заявку та зв'яжеться з вами.",
        "manager": "<b>Менеджер VESTHETIC</b>\n\nЗв'язатися: @VESTHETIC_manager",
    },
    "sk": {
        "welcome": "<b>VESTHETIC | Digital Talent Agency</b>\n\nPomáhame dospelým online tvorcom budovať a rozvíjať kariéru na medzinárodných platformách.\n\n18+ only • Voluntary • Global",
        "about": "<b>VESTHETIC</b>\n\nDigital Talent Agency pre dospelých online tvorcov.\n\n<b>Model:</b> 75% creator / 25% VESTHETIC\n\nPlatformy:\n• BongaCams\n• Stripchat\n• Chaturbate",
        "terms": "<b>Podmienky</b>\n\n• Iba 18+\n• Účasť je dobrovoľná\n• 75% príjmu dostáva creator\n• 25% — VESTHETIC",
        "faq": "<b>FAQ</b>\n\n<b>Je potrebná prax?</b>\nNie, môžete začať od nuly.\n\n<b>Dá sa pracovať z domu?</b>\nÁno.\n\n<b>Vek?</b>\nStriktne 18+.",
        "apply_start": "<b>Žiadosť do VESTHETIC</b>\n\nVyplnenie potrvá niekoľko minút.\n\nPokračovaním potvrdzujete, že máte 18 rokov alebo viac a konáte dobrovoľne.",
        "age": "Máte už 18 rokov?",
        "age_no": "VESTHETIC spolupracuje iba s plnoletými osobami.",
        "name": "Ako sa voláte alebo aký pseudonym chcete používať?",
        "country": "V ktorej krajine sa teraz nachádzate?",
        "languages": "Akými jazykmi hovoríte?",
        "experience": "Máte skúsenosti s podobnými platformami?",
        "equipment": "Aké vybavenie máte? Napríklad telefón, PC, kamera, svetlo.",
        "schedule": "Koľko času denne alebo týždenne môžete venovať práci?",
        "contact": "Uveďte Telegram kontakt pre manažéra.",
        "source": "Ako ste sa dozvedeli o VESTHETIC?",
        "thanks": "<b>Žiadosť odoslaná ✅</b>\n\nĎakujeme! Manažér VESTHETIC vašu žiadosť posúdi a ozve sa vám.",
        "manager": "<b>Manažér VESTHETIC</b>\n\nKontakt: @VESTHETIC_manager",
    },
    "en": {
        "welcome": "<b>VESTHETIC | Digital Talent Agency</b>\n\nWe help adult online creators build and develop their careers on international platforms.\n\n18+ only • Voluntary • Global",
        "about": "<b>VESTHETIC</b>\n\nDigital Talent Agency for adult online creators.\n\n<b>Model:</b> 75% creator / 25% VESTHETIC\n\nPlatforms:\n• BongaCams\n• Stripchat\n• Chaturbate",
        "terms": "<b>Terms</b>\n\n• 18+ only\n• Participation is voluntary\n• Creator receives 75%\n• VESTHETIC receives 25%",
        "faq": "<b>FAQ</b>\n\n<b>Is experience required?</b>\nNo, you can start from zero.\n\n<b>Can I work from home?</b>\nYes.\n\n<b>Age?</b>\nStrictly 18+.",
        "apply_start": "<b>VESTHETIC application</b>\n\nIt takes a few minutes.\n\nBy continuing, you confirm that you are 18 or older and participating voluntarily.",
        "age": "Are you 18 years old or older?",
        "age_no": "VESTHETIC works only with adults.",
        "name": "What is your name or preferred pseudonym?",
        "country": "Which country are you currently in?",
        "languages": "Which languages do you speak?",
        "experience": "Do you have experience on similar platforms?",
        "equipment": "What equipment do you have? For example: phone, PC, camera, lighting.",
        "schedule": "How much time per day or week can you dedicate to the work?",
        "contact": "Provide a Telegram contact for the manager.",
        "source": "How did you hear about VESTHETIC?",
        "thanks": "<b>Application submitted ✅</b>\n\nThank you! A VESTHETIC manager will review your application and contact you.",
        "manager": "<b>VESTHETIC Manager</b>\n\nContact: @VESTHETIC_manager",
    },
}


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
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else []
    except Exception as exc:
        print("Supabase API error:", exc)
        return None


def load_user(chat_id, username=None):
    rows = supabase_request("GET", "bot_users", query={
        "telegram_chat_id": f"eq.{chat_id}", "select": "*", "limit": "1"
    })
    if isinstance(rows, list) and rows:
        row = rows[0]
        try:
            draft = row.get("application_draft") or {}
            if isinstance(draft, str):
                draft = json.loads(draft)
        except Exception:
            draft = {}
        return {"lang": row.get("language") or "en", "state": row.get("state"), "application": draft if isinstance(draft, dict) else {}}
    user = {"lang": "en", "state": None, "application": {}}
    save_user(chat_id, username, user)
    return user


def save_user(chat_id, username, user):
    return supabase_request("POST", "bot_users", {
        "telegram_chat_id": chat_id,
        "telegram_username": username,
        "language": user.get("lang", "en"),
        "state": user.get("state"),
        "application_draft": user.get("application", {}),
    }, {"select": "*"})


def create_application(chat_id, username, data):
    rows = supabase_request("POST", "applications", {
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
        "status_changed_by_telegram_id": None,
        "internal_notes": "",
    }, {"select": "*"})
    return rows[0] if isinstance(rows, list) and rows else None


def get_application(app_id):
    rows = supabase_request("GET", "applications", query={
        "id": f"eq.{app_id}", "select": "*", "limit": "1"
    })
    return rows[0] if isinstance(rows, list) and rows else None


def get_applications(limit=1000):
    rows = supabase_request("GET", "applications", query={
        "select": "*", "order": "created_at.desc", "limit": str(limit)
    })
    return rows if isinstance(rows, list) else []


def get_application_history(app_id):
    rows = supabase_request("GET", "application_status_history", query={
        "application_id": f"eq.{app_id}", "select": "*", "order": "created_at.asc"
    })
    return rows if isinstance(rows, list) else []


def update_application_status(app_id, status, actor_id):
    app = get_application(app_id)
    if not app:
        return None
    if app.get("status") == status:
        return app
    rows = supabase_request("PATCH", "applications", {
        "status": status,
        "status_changed_by_telegram_id": actor_id,
    }, {"id": f"eq.{app_id}", "select": "*"})
    return rows[0] if isinstance(rows, list) and rows else None


def append_internal_note(app_id, note, actor_id):
    app = get_application(app_id)
    if not app:
        return None
    note = note.strip()
    if not note:
        return app
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"[{stamp}] {actor_id}: {note}"
    existing = (app.get("internal_notes") or "").strip()
    combined = f"{existing}\n{entry}".strip()
    rows = supabase_request("PATCH", "applications", {
        "internal_notes": combined,
    }, {"id": f"eq.{app_id}", "select": "*"})
    return rows[0] if isinstance(rows, list) and rows else None


def update_follow_up(app_id, next_action, next_action_at):
    parsed_at = parse_follow_up_local(next_action_at)
    if next_action_at and parsed_at is None:
        return None
    rows = supabase_request("PATCH", "applications", {
        "next_action": next_action.strip(),
        "next_action_at": parsed_at,
    }, {"id": f"eq.{app_id}", "select": "*"})
    return rows[0] if isinstance(rows, list) and rows else None


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
        [{"text": "🇸🇰 Slovenčina", "callback_data": "lang_sk"}, {"text": "🇬🇧 English", "callback_data": "lang_en"}],
    ]}


def main_keyboard(lang):
    labels = {
        "ru": ["ℹ️ О VESTHETIC", "📋 Условия", "❓ FAQ", "🚀 Подать заявку", "👤 Связаться с менеджером", "🌐 Язык"],
        "ua": ["ℹ️ Про VESTHETIC", "📋 Умови", "❓ FAQ", "🚀 Подати заявку", "👤 Зв'язатися з менеджером", "🌐 Мова"],
        "sk": ["ℹ️ O VESTHETIC", "📋 Podmienky", "❓ FAQ", "🚀 Poslať žiadosť", "👤 Kontaktovať manažéra", "🌐 Jazyk"],
        "en": ["ℹ️ About VESTHETIC", "📋 Terms", "❓ FAQ", "🚀 Apply", "👤 Contact manager", "🌐 Language"],
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
        [{"text": "🟡 В работу", "callback_data": f"status_progress_{app_id}"},
         {"text": "💬 Связались", "callback_data": f"status_contacted_{app_id}"}],
        [{"text": "🎙 Интервью", "callback_data": f"status_interview_{app_id}"},
         {"text": "📝 Регистрация", "callback_data": f"status_registration_{app_id}"}],
        [{"text": "🟢 Активна", "callback_data": f"status_active_{app_id}"},
         {"text": "🔴 Отказ", "callback_data": f"status_reject_{app_id}"}],
    ]}


def status_label(status):
    return STATUS_LABELS.get(status, "⚪ Новая")


def status_text(status, lang="ru"):
    return STATUS_TEXTS.get(lang, STATUS_TEXTS["en"]).get(status, "Application status updated.")


def safe(value):
    return html.escape(str(value if value not in (None, "") else "-"))


def parse_follow_up_local(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=CRM_TIMEZONE)
        return dt.astimezone(timezone.utc).isoformat()
    except ValueError:
        return None


def format_follow_up_local(value):
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(CRM_TIMEZONE).strftime("%Y-%m-%dT%H:%M")
    except ValueError:
        return str(value)[:16]


def follow_up_state(value):
    if not value:
        return "none"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local = dt.astimezone(CRM_TIMEZONE)
        now = datetime.now(timezone.utc).astimezone(CRM_TIMEZONE)
        if local < now:
            return "overdue"
        if local.date() == now.date():
            return "today"
        return "planned"
    except ValueError:
        return "none"


def follow_up_badge(value):
    state = follow_up_state(value)
    if state == "overdue":
        return "<span class='follow overdue'>🔴 Просрочено</span>"
    if state == "today":
        return "<span class='follow today'>🟡 Сегодня</span>"
    if state == "planned":
        return "<span class='follow planned'>⚪ Запланировано</span>"
    return "<span class='muted'>—</span>"


def timeline_items(app_data, history):
    items = []
    notes = str(app_data.get("internal_notes") or "").strip()
    for raw in notes.splitlines():
        line = raw.strip()
        if not line:
            continue
        stamp = None
        body = line
        if line.startswith("[") and "]" in line:
            stamp_text, body = line[1:].split("]", 1)
            try:
                stamp = datetime.strptime(stamp_text.strip(), "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
            except ValueError:
                stamp = None
        items.append({"kind": "note", "dt": stamp, "title": "Внутренняя заметка", "body": body.strip(), "actor": ""})
    for item in history:
        raw_dt = item.get("created_at")
        try:
            dt = datetime.fromisoformat(str(raw_dt).replace("Z", "+00:00")) if raw_dt else None
        except ValueError:
            dt = None
        items.append({
            "kind": "status",
            "dt": dt,
            "title": f"Статус: {status_label(item.get('new_status'))}",
            "body": f"{status_label(item.get('old_status')) if item.get('old_status') else '—'} → {status_label(item.get('new_status'))}",
            "actor": str(item.get("changed_by_telegram_id") or "Система"),
        })
    items.sort(key=lambda x: x.get("dt") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return items


def application_text(app_id, data):
    return (
        f"<b>ЗАЯВКА VESTHETIC #{app_id}</b>\n"
        f"👤 Имя: {safe(data.get('name'))}\n"
        f"🔞 Возраст: {'18+ подтверждён' if data.get('age_confirmed') else '-'}\n"
        f"🌍 Страна: {safe(data.get('country'))}\n"
        f"🗣 Языки: {safe(data.get('languages'))}\n"
        f"💼 Опыт: {safe(data.get('experience'))}\n"
        f"🖥 Оборудование: {safe(data.get('equipment'))}\n"
        f"🕐 График: {safe(data.get('schedule'))}\n"
        f"📱 Telegram: {safe(data.get('contact'))}\n"
        f"📣 Источник: {safe(data.get('source'))}\n\n"
        f"<b>Статус:</b> {status_label(data.get('status', 'new'))}"
    )


def notify_candidate(app_id, data, status):
    candidate_id = data.get("telegram_chat_id")
    if not candidate_id:
        return
    user = load_user(candidate_id)
    lang = user.get("lang", "en")
    send_message(candidate_id, f"<b>VESTHETIC</b>\n\n{status_text(status, lang)}")


def notify_admins(app_id, data):
    text = application_text(app_id, data).replace("<b>ЗАЯВКА", "<b>НОВАЯ ЗАЯВКА", 1)
    for recipient_id in list(dict.fromkeys(ADMIN_IDS + [MANAGER_ID])):
        send_message(recipient_id, text, admin_keyboard(app_id))


def process_message(message):
    user_id = message.get("chat", {}).get("id")
    if not user_id:
        return
    text = message.get("text", "").strip()
    username = message.get("chat", {}).get("username")
    u = load_user(user_id, username)
    lang = u["lang"]

    if text.startswith("/start"):
        u["state"] = None
        u["application"] = {}
        save_user(user_id, username, u)
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
            app_data = create_application(user_id, username, u["application"])
            if app_data is None:
                send_message(user_id, TEXTS[lang]["thanks"] + "\n\n⚠️ Не удалось сохранить заявку. Попробуйте ещё раз позже.", main_keyboard(lang))
                u["state"] = None
                save_user(user_id, username, u)
                return
            notify_admins(app_data["id"], app_data)
            u["state"] = None
            u["application"] = {}
            save_user(user_id, username, u)
            send_message(user_id, TEXTS[lang]["thanks"], main_keyboard(lang))
        else:
            save_user(user_id, username, u)
        return

    send_message(user_id, TEXTS[lang]["welcome"], main_keyboard(lang))


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
            return
        status = parts[1]
        try:
            app_id = int(parts[2])
        except ValueError:
            return
        if status not in STATUS_ORDER or status == "new":
            return
        app_data = get_application(app_id)
        if not app_data:
            answer_callback(callback_id, "Application not found")
            return
        updated = update_application_status(app_id, status, user_id)
        if updated is None:
            answer_callback(callback_id, "Database update failed")
            return
        answer_callback(callback_id, status_text(status, "ru"))
        message = query.get("message", {})
        if message.get("chat", {}).get("id") and message.get("message_id"):
            edit_message(message["chat"]["id"], message["message_id"], application_text(app_id, updated), {"inline_keyboard": []})
        notify_candidate(app_id, updated, status)
        staff_notice = f"<b>Заявка #{app_id} обновлена</b>\nСтатус: {status_label(status)}\nИзменил: {user_id}"
        for staff_id in STAFF_IDS:
            if staff_id != user_id:
                send_message(staff_id, staff_notice)

    save_user(user_id, username, u)


def require_admin(credentials: HTTPBasicCredentials):
    if not ADMIN_PANEL_PASSWORD:
        return False
    return secrets.compare_digest(credentials.username, ADMIN_PANEL_USER) and secrets.compare_digest(credentials.password, ADMIN_PANEL_PASSWORD)


def counts_for(apps):
    counts = {key: 0 for key in STATUS_ORDER}
    counts["accept"] = 0
    for app_data in apps:
        key = app_data.get("status", "new")
        counts[key] = counts.get(key, 0) + 1
    return counts


def dashboard_html(apps):
    counts = counts_for(apps)
    countries = sorted({str(a.get("country") or "").strip() for a in apps if str(a.get("country") or "").strip()})
    sources = {}
    for a in apps:
        source = str(a.get("source") or "Не указан").strip() or "Не указан"
        sources[source] = sources.get(source, 0) + 1
    source_rows = "".join(
        f"<tr><td>{html.escape(k)}</td><td><b>{v}</b></td></tr>"
        for k, v in sorted(sources.items(), key=lambda x: (-x[1], x[0].lower()))
    ) or "<tr><td colspan='2' class='muted'>Нет данных</td></tr>"

    source_stats = {}
    for a in apps:
        source = str(a.get("source") or "Не указан").strip() or "Не указан"
        if source not in source_stats:
            source_stats[source] = {key: 0 for key in ["new", "contacted", "interview", "registration", "active", "reject"]}
        status = a.get("status", "new")
        if status == "accept":
            status = "active"
        if status in source_stats[source]:
            source_stats[source][status] += 1
    source_conversion_rows = ""
    for source, vals in sorted(source_stats.items(), key=lambda x: (-sum(x[1].values()), x[0].lower())):
        total = sum(vals.values())
        contacted = vals["contacted"] + vals["interview"] + vals["registration"] + vals["active"]
        interview = vals["interview"] + vals["registration"] + vals["active"]
        registered = vals["registration"] + vals["active"]
        active = vals["active"]
        pct = lambda n: f"{(n / total * 100):.0f}%" if total else "0%"
        source_conversion_rows += (
            f"<tr><td>{html.escape(source)}</td><td>{total}</td><td>{contacted} ({pct(contacted)})</td>"
            f"<td>{interview} ({pct(interview)})</td><td>{registered} ({pct(registered)})</td><td>{active} ({pct(active)})</td></tr>"
        )
    source_conversion_rows = source_conversion_rows or "<tr><td colspan='6' class='muted'>Нет данных</td></tr>"

    followup_counts = {"overdue": 0, "today": 0, "planned": 0, "none": 0}
    for a in apps:
        followup_counts[follow_up_state(a.get("next_action_at"))] += 1

    rows = []
    for a in apps:
        app_id = a.get("id")
        status = a.get("status", "new")
        username = a.get("telegram_username")
        contact = a.get("contact") or username
        contact_link = f"<a href='https://t.me/{html.escape(str(contact).lstrip('@'))}' target='_blank'>Telegram</a>" if contact and not str(contact).startswith("+") else "-"
        quick_statuses = {
            "new": ["progress", "contacted"],
            "progress": ["contacted", "interview"],
            "contacted": ["interview"],
            "interview": ["registration"],
            "registration": ["active"],
            "active": [],
            "reject": [],
        }.get(status, [])
        quick_buttons = "".join(
            f"<form method='post' action='/admin/status'><input type='hidden' name='id' value='{app_id}'><button class='quick-btn' name='status' value='{s}' title='{status_label(s)}'>{'💬' if s == 'contacted' else '🎙' if s == 'interview' else '📝' if s == 'registration' else '🟢' if s == 'active' else '🟡'}</button></form>"
            for s in quick_statuses
        )
        rows.append(f"""
<tr data-status="{safe(status)}" data-country="{safe(a.get('country'))}" data-followup="{follow_up_state(a.get('next_action_at'))}">
<td><b>#{app_id}</b></td><td>{safe(a.get('name'))}</td><td>{safe(a.get('country'))}</td>
<td>{safe(a.get('languages'))}</td><td>{safe(a.get('experience'))}</td><td>{safe(a.get('schedule'))}</td>
<td class="badge">{status_label(status)}</td><td>{contact_link}</td>
<td><b>{safe(a.get('next_action') or '—')}</b><br>{follow_up_badge(a.get('next_action_at'))}</td>
<td><div class='quick-actions'>{quick_buttons}<a class='quick-btn' href='/admin/application/{app_id}#followup' title='Follow-up'>📅</a><a class='link' href='/admin/application/{app_id}'>Подробнее</a></div></td>
</tr>""")

    country_options = "".join(f'<option value="{html.escape(c, quote=True)}">{html.escape(c)}</option>' for c in countries)
    cards = [
        ("Всего", len(apps)), ("⚪ Новые", counts.get("new", 0)), ("🟡 В работе", counts.get("progress", 0)),
        ("💬 Связались", counts.get("contacted", 0)), ("🎙 Интервью", counts.get("interview", 0)),
        ("📝 Регистрация", counts.get("registration", 0)), ("🟢 Активны", counts.get("active", 0) + counts.get("accept", 0)),
        ("🔴 Отклонены", counts.get("reject", 0)), ("🔴 Просрочены", followup_counts["overdue"]),
        ("🟡 На сегодня", followup_counts["today"]),
    ]
    stat_html = "".join(f"<div class='stat'><span>{label}</span><b>{value}</b></div>" for label, value in cards)

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VESTHETIC CRM</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0b0b0b;color:#eee;margin:0;padding:28px;min-height:100vh}}
body>h1,body>p,body>.stats,body>.analytics,body>.toolbar,body>.wrap{{max-width:1600px;margin-left:auto;margin-right:auto}}
h1{{letter-spacing:.08em;margin-top:0}}.wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{width:100%;border-collapse:collapse;min-width:1250px}}th,td{{padding:11px;border-bottom:1px solid #292929;text-align:left;vertical-align:top}}
th{{color:#888;font-size:11px;text-transform:uppercase;white-space:nowrap}}
button,select,input,textarea{{border:0;border-radius:9px;padding:10px 11px;background:#181818;color:#fff;font:inherit}}
button{{cursor:pointer}}a{{color:#fff}}.link{{text-decoration:none;background:#222;padding:7px 9px;border-radius:8px;display:inline-block}}
.quick-actions{{display:flex;align-items:center;gap:5px;flex-wrap:wrap}}
.quick-actions form{{margin:0}}
.quick-btn{{display:inline-flex;align-items:center;justify-content:center;min-width:36px;height:36px;padding:6px;border:1px solid #303030;background:#171717;border-radius:8px;text-decoration:none}}
.quick-btn:hover{{background:#252525}}
.badge{{font-weight:700}}.muted{{color:#888}}.toolbar{{display:flex;gap:10px;flex-wrap:wrap;margin:18px auto}}
.toolbar input{{min-width:280px;flex:1}}.toolbar select{{min-width:170px}}
.stats{{display:grid;grid-template-columns:repeat(8,minmax(110px,1fr));gap:10px;margin-top:18px;margin-bottom:18px}}
.stat{{background:#111;border:1px solid #292929;border-radius:12px;padding:12px 15px;min-width:0}}
.stat span{{color:#999;font-size:12px}}.stat b{{display:block;font-size:21px;margin-top:4px}}.analytics{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:18px auto}}
.card{{background:#111;border:1px solid #292929;border-radius:14px;padding:18px}}
.action-center{{margin:18px auto;max-width:1600px}}
.action-head{{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:14px}}
.action-head h2{{margin:0 0 4px}}.action-head p{{margin:0}}
.action-total{{text-align:right;background:#181818;border:1px solid #292929;border-radius:12px;padding:8px 14px;min-width:80px}}
.action-total b{{display:block;font-size:22px}}.action-total span{{font-size:11px;color:#888}}
.action-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}
.action-card{{display:flex;flex-direction:column;gap:3px;text-decoration:none;background:#151515;border:1px solid #292929;border-radius:12px;padding:14px;transition:.15s}}
.action-card:hover{{background:#1b1b1b;transform:translateY(-1px)}}
.action-card b{{font-size:24px}}.action-card span{{font-weight:700}}.action-card small{{color:#777}}
.action-card.overdue b{{color:#ff6b6b}}.action-card.today b{{color:#ffd166}}.action-card.planned b{{color:#aaa}}
.analytics table{{min-width:0}}

@media(max-width:1100px){{
  body{{padding:20px}}
   .stats{{grid-template-columns:repeat(4,1fr)}}
  .action-grid{{grid-template-columns:repeat(2,1fr)}}
}}

@media(max-width:700px){{
  body{{padding:14px 12px;font-size:14px}}
  .action-head{{align-items:flex-start}}
  .action-grid{{grid-template-columns:1fr 1fr;gap:7px}}
  .action-card{{padding:11px}}
  .action-card b{{font-size:20px}}
  .action-card small{{font-size:10px}}
  h1{{font-size:25px;margin-bottom:6px}}
  .stats{{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}}
  .stat{{padding:10px 12px}}.stat b{{font-size:19px}}
  .analytics{{grid-template-columns:1fr;gap:12px;margin:12px auto}}
  .card{{padding:14px;border-radius:12px}}
  .toolbar{{display:grid;grid-template-columns:1fr;gap:8px;margin:12px auto}}
  .toolbar input,.toolbar select{{width:100%;min-width:0}}
  .wrap{{overflow:visible}}
  #applications{{min-width:0;width:100%}}
  #applications thead{{display:none}}
  #applications tbody,#applications tr,#applications td{{display:block;width:100%}}
  #applications tr{{background:#111;border:1px solid #292929;border-radius:12px;margin-bottom:10px;padding:8px}}
  #applications td{{border:0;border-bottom:1px solid #242424;padding:8px 6px;min-height:36px}}
  #applications td:last-child{{border-bottom:0}}
  #applications td::before{{display:block;color:#777;font-size:10px;text-transform:uppercase;margin-bottom:3px}}
  #applications td:nth-child(1)::before{{content:"ID"}}
  #applications td:nth-child(2)::before{{content:"Имя"}}
  #applications td:nth-child(3)::before{{content:"Страна"}}
  #applications td:nth-child(4)::before{{content:"Языки"}}
  #applications td:nth-child(5)::before{{content:"Опыт"}}
  #applications td:nth-child(6)::before{{content:"График"}}
  #applications td:nth-child(7)::before{{content:"Статус"}}
  #applications td:nth-child(8)::before{{content:"Контакт"}}
  #applications td:nth-child(9)::before{{content:"Следующее действие"}}
  #applications td:nth-child(10)::before{{content:"Карточка"}}
  #applications .quick-actions{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}}
  #applications .quick-actions .quick-btn{{width:100%;min-height:42px}}
  #applications .quick-actions .link{{grid-column:1 / -1;width:100%;text-align:center;padding:9px}}
  .analytics table{{min-width:0}}
  .analytics th,.analytics td{{padding:8px}}
}}
</style></head><body>
<h1>VESTHETIC <span class="muted">CRM</span></h1>
<p class="muted">Recruitment pipeline • 1 manager</p>
<div class="stats">{stat_html}</div>
<div class="card action-center">
<div class="action-head"><div><h2>Сегодня</h2><p class="muted">Что нужно сделать по кандидатам прямо сейчас</p></div><div class="action-total"><b>{followup_counts["overdue"] + followup_counts["today"]}</b><span>задач</span></div></div>
<div class="action-grid">
<a class="action-card overdue" href="#applications" data-quick-filter="overdue"><b>🔴 {followup_counts["overdue"]}</b><span>Просрочено</span><small>Требуют внимания</small></a>
<a class="action-card today" href="#applications" data-quick-filter="today"><b>🟡 {followup_counts["today"]}</b><span>На сегодня</span><small>Запланированные действия</small></a>
<a class="action-card planned" href="#applications" data-quick-filter="planned"><b>⚪ {followup_counts["planned"]}</b><span>Запланировано</span><small>Будущие follow-up</small></a>
<a class="action-card empty" href="#applications" data-quick-filter="none"><b>—</b><span>Без follow-up</span><small>Кандидаты без следующего шага</small></a>
</div></div>
<div class="analytics">
<div class="card"><h2>Воронка</h2><p class="muted">Новые → работа → контакт → интервью → регистрация → активна</p>
<p>Новых: <b>{counts.get("new",0)}</b> · В работе: <b>{counts.get("progress",0)}</b> · Активны: <b>{counts.get("active",0)+counts.get("accept",0)}</b></p></div>
<div class="card"><h2>Источники</h2><div style="overflow:auto"><table><thead><tr><th>Источник</th><th>Заявки</th></tr></thead><tbody>{source_rows}</tbody></table></div></div>
<div class="card"><h2>Конверсия по источникам</h2><p class="muted">Доля от всех заявок источника, дошедших до этапа.</p><div style="overflow:auto"><table><thead><tr><th>Источник</th><th>Всего</th><th>Контакт</th><th>Интервью</th><th>Регистрация</th><th>Активна</th></tr></thead><tbody>{source_conversion_rows}</tbody></table></div></div>
</div>
<div class="toolbar">
<input id="search" type="search" placeholder="Поиск по имени, стране, языкам, ID...">
<select id="statusFilter"><option value="">Все статусы</option>
<option value="new">Новые</option><option value="progress">В работе</option><option value="contacted">Связались</option>
<option value="interview">Интервью</option><option value="registration">Регистрация</option><option value="active">Активна</option><option value="reject">Отклонена</option></select>
<select id="countryFilter"><option value="">Все страны</option>{country_options}</select>
<select id="followupFilter"><option value="">Все follow-up</option><option value="overdue">🔴 Просрочены</option><option value="today">🟡 На сегодня</option><option value="planned">⚪ Запланированы</option><option value="none">Без follow-up</option></select>
</div>
<div class="wrap"><table id="applications"><thead><tr>
<th>ID</th><th>Имя</th><th>Страна</th><th>Языки</th><th>Опыт</th><th>График</th><th>Статус</th><th>Контакт</th><th>Следующее действие</th><th>Карточка</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<script>
function filterRows(){{
const q=document.getElementById('search').value.toLowerCase().trim(), s=document.getElementById('statusFilter').value, c=document.getElementById('countryFilter').value.toLowerCase(), f=document.getElementById('followupFilter').value;
document.querySelectorAll('#applications tbody tr').forEach(row=>{{
const okQ=!q||row.innerText.toLowerCase().includes(q), okS=!s||row.dataset.status===s, okC=!c||row.dataset.country.toLowerCase()===c, okF=!f||row.dataset.followup===f;
row.style.display=okQ&&okS&&okC&&okF?'':'none';
}});
}}
document.getElementById('search').addEventListener('input',filterRows);
document.getElementById('statusFilter').addEventListener('change',filterRows);
document.getElementById('countryFilter').addEventListener('change',filterRows);
document.getElementById('followupFilter').addEventListener('change',filterRows);
document.querySelectorAll('[data-quick-filter]').forEach(link=>{
  link.addEventListener('click',()=>{
    document.getElementById('followupFilter').value=link.dataset.quickFilter;
    filterRows();
  });
});
</script></body></html>"""


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(credentials: HTTPBasicCredentials = Depends(security)):
    if not require_admin(credentials):
        return HTMLResponse("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
    return HTMLResponse(dashboard_html(get_applications(1000)))


@app.get("/admin/application/{app_id}", response_class=HTMLResponse)
async def admin_application_detail(app_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    if not require_admin(credentials):
        return HTMLResponse("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
    a = get_application(app_id)
    if not a:
        return HTMLResponse("<h1>Заявка не найдена</h1><p><a href='/admin'>← К заявкам</a></p>", status_code=404)

    history = get_application_history(app_id)
    notes = html.escape(str(a.get("internal_notes") or ""))
    timeline = timeline_items(a, history)
    timeline_rows = ""
    for item in timeline:
        dt = item.get("dt")
        dt_text = dt.astimezone(CRM_TIMEZONE).strftime("%d.%m.%Y %H:%M") if dt else "—"
        actor = html.escape(item.get("actor") or "")
        kind = "📝" if item["kind"] == "note" else "🔄"
        actor_html = f"<div class='muted'>ID: {actor}</div>" if actor else ""
        timeline_rows += f"<div class='timeline-item'><div class='timeline-head'><b>{kind} {html.escape(item['title'])}</b><span class='muted'>{dt_text}</span></div><div>{html.escape(item['body'])}</div>{actor_html}</div>"
    timeline_rows = timeline_rows or "<div class='muted'>Пока нет событий.</div>"
    username = a.get("telegram_username")
    telegram_link = f"<a href='https://t.me/{html.escape(str(username))}' target='_blank'>@{html.escape(str(username))}</a>" if username else "-"
    history_rows = ""
    for item in history:
        actor = item.get("changed_by_telegram_id")
        actor_text = html.escape(str(actor)) if actor else "Система"
        history_rows += f"<tr><td>{safe(item.get('created_at'))}</td><td>{status_label(item.get('old_status')) if item.get('old_status') else '—'}</td><td>{status_label(item.get('new_status'))}</td><td>{actor_text}</td></tr>"
    history_rows = history_rows or "<tr><td colspan='4' class='muted'>История пока пуста</td></tr>"

    buttons = "".join(
        f"<button name='status' value='{s}'>{status_label(s)}</button>"
        for s in ["progress", "contacted", "interview", "registration", "active", "reject"]
    )

    return HTMLResponse(f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Заявка #{app_id} — VESTHETIC CRM</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0b0b0b;color:#eee;margin:0 auto;padding:28px;max-width:1200px}}
a{{color:#fff}}.muted{{color:#888}}.card{{background:#111;border:1px solid #292929;border-radius:14px;padding:20px;margin:18px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}}.item{{border-bottom:1px solid #292929;padding:10px 0;overflow-wrap:anywhere}}
.label{{display:block;color:#888;font-size:11px;text-transform:uppercase;margin-bottom:4px}}
button{{border:0;border-radius:8px;padding:10px 12px;margin:4px;cursor:pointer;background:#222;color:#fff;font:inherit}}
textarea{{width:100%;box-sizing:border-box;min-height:130px;border:0;border-radius:10px;padding:12px;background:#181818;color:#fff;font:inherit;resize:vertical}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #292929;text-align:left;vertical-align:top}}
.notes{{white-space:pre-wrap;background:#0d0d0d;border-radius:10px;padding:12px;margin-bottom:12px;overflow-wrap:anywhere}}
.timeline{{display:flex;flex-direction:column;gap:8px}}
.timeline-item{{background:#0d0d0d;border:1px solid #242424;border-radius:10px;padding:12px;overflow-wrap:anywhere}}
.timeline-head{{display:flex;justify-content:space-between;gap:12px;margin-bottom:7px}}
.follow{{display:inline-block;font-size:11px;padding:2px 7px;border-radius:999px;background:#1a1a1a;margin-top:4px}}
.overdue{{color:#ff6b6b}}.today{{color:#ffd166}}.planned{{color:#aaa}}
.followup{{display:grid;grid-template-columns:2fr 1fr auto;gap:8px}}.followup input{{border:0;border-radius:9px;padding:10px;background:#181818;color:#fff;font:inherit}}
@media(max-width:700px){{.followup{{grid-template-columns:1fr}}}}

@media(max-width:700px){{
  body{{padding:14px 12px;font-size:14px}}
  h1{{font-size:24px}}
  .card{{padding:14px;margin:12px 0;border-radius:12px}}
  .grid{{grid-template-columns:1fr;gap:0}}
  .item{{padding:9px 0}}
  .funnel{{display:grid;grid-template-columns:1fr 1fr;gap:6px}}
  .funnel button{{margin:0;width:100%;min-height:44px}}
  .notes{{font-size:13px}}
  .history{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
  .history table{{min-width:560px}}
}}
</style></head><body>
<p><a href="/admin">← К заявкам</a></p><h1>Заявка #{app_id}</h1>
<div class="card"><div class="grid">
<div class="item"><span class="label">Имя / псевдоним</span>{safe(a.get("name"))}</div>
<div class="item"><span class="label">Telegram</span>{telegram_link}</div>
<div class="item"><span class="label">Telegram ID</span>{safe(a.get("telegram_chat_id"))}</div>
<div class="item"><span class="label">Возраст</span>{'18+ подтверждён' if a.get('age_confirmed') else 'Не подтверждён'}</div>
<div class="item"><span class="label">Страна</span>{safe(a.get("country"))}</div>
<div class="item"><span class="label">Языки</span>{safe(a.get("languages"))}</div>
<div class="item"><span class="label">Опыт</span>{safe(a.get("experience"))}</div>
<div class="item"><span class="label">Оборудование</span>{safe(a.get("equipment"))}</div>
<div class="item"><span class="label">График</span>{safe(a.get("schedule"))}</div>
<div class="item"><span class="label">Контакт</span>{safe(a.get("contact"))}</div>
<div class="item"><span class="label">Источник</span>{safe(a.get("source"))}</div>
<div class="item"><span class="label">Создана</span>{safe(a.get("created_at"))}</div>
<div class="item"><span class="label">Обновлена</span>{safe(a.get("updated_at"))}</div>
<div class="item"><span class="label">Статус</span><b>{status_label(a.get("status","new"))}</b></div>
<div class="item"><span class="label">Следующее действие</span>{safe(a.get("next_action") or "Не задано")}</div>
<div class="item"><span class="label">Дата следующего действия</span>{safe(format_follow_up_local(a.get("next_action_at")) or "Не задана")}<br>{follow_up_badge(a.get("next_action_at"))}</div>
</div></div>

<div class="card"><h2>Воронка</h2><form class="funnel" method="post" action="/admin/status"><input type="hidden" name="id" value="{app_id}">{buttons}</form></div>

<div class="card" id="followup"><h2>Следующее действие</h2>
<form method="post" action="/admin/follow-up" class="followup">
<input type="hidden" name="id" value="{app_id}">
<input name="next_action" value="{safe(a.get("next_action") or "")}" placeholder="Написать кандидату / назначить интервью / регистрация..." required>
<input type="datetime-local" name="next_action_at" value="{safe(format_follow_up_local(a.get("next_action_at")))}">
<button type="submit">Сохранить follow-up</button>
</form></div>

<div class="card"><h2>Внутренние заметки</h2>
<div class="notes">{notes or 'Пока нет заметок.'}</div>
<form method="post" action="/admin/note"><input type="hidden" name="id" value="{app_id}">
<textarea name="note" placeholder="Например: опыт 2 года, ждём документы, договорились на интервью..."></textarea>
<br><button type="submit">＋ Добавить заметку</button></form></div>

<div class="card"><h2>Лента кандидата</h2><div class="timeline">{timeline_rows}</div></div>

<div class="card"><h2>История статусов</h2><div class="history"><table>
<thead><tr><th>Дата</th><th>Было</th><th>Стало</th><th>Изменил</th></tr></thead><tbody>{history_rows}</tbody></table></div></div>
</body></html>""")


@app.post("/admin/status")
async def admin_status(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    if not require_admin(credentials):
        return PlainTextResponse("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
    try:
        raw = await request.body()
        form = urllib.parse.parse_qs(raw.decode("utf-8"), keep_blank_values=True)
        app_id = int((form.get("id") or [""])[0])
        status = (form.get("status") or [""])[0]
        if status not in STATUS_ORDER or status == "new":
            return PlainTextResponse("Invalid status", status_code=400)
        updated = update_application_status(app_id, status, CRM_ACTOR_ID)
        if updated is None:
            return PlainTextResponse("Application not found or update failed", status_code=404)
        notify_candidate(app_id, updated, status)
        return RedirectResponse(f"/admin/application/{app_id}", status_code=303)
    except Exception as exc:
        print("Admin status error:", repr(exc))
        return PlainTextResponse(f"Admin status error: {exc}", status_code=500)


@app.post("/admin/follow-up")
async def admin_follow_up(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    if not require_admin(credentials):
        return PlainTextResponse("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
    try:
        raw = await request.body()
        form = urllib.parse.parse_qs(raw.decode("utf-8"), keep_blank_values=True)
        app_id = int((form.get("id") or [""])[0])
        next_action = (form.get("next_action") or [""])[0]
        next_action_at = (form.get("next_action_at") or [""])[0]
        updated = update_follow_up(app_id, next_action, next_action_at)
        if updated is None:
            return PlainTextResponse("Application not found or follow-up save failed", status_code=404)
        return RedirectResponse(f"/admin/application/{app_id}", status_code=303)
    except Exception as exc:
        print("Admin follow-up error:", repr(exc))
        return PlainTextResponse(f"Admin follow-up error: {exc}", status_code=500)


@app.post("/admin/note")
async def admin_note(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    if not require_admin(credentials):
        return PlainTextResponse("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
    try:
        raw = await request.body()
        form = urllib.parse.parse_qs(raw.decode("utf-8"), keep_blank_values=True)
        app_id = int((form.get("id") or [""])[0])
        note = (form.get("note") or [""])[0]
        updated = append_internal_note(app_id, note, CRM_ACTOR_ID)
        if updated is None:
            return PlainTextResponse("Application not found or note save failed", status_code=404)
        return RedirectResponse(f"/admin/application/{app_id}", status_code=303)
    except Exception as exc:
        print("Admin note error:", repr(exc))
        return PlainTextResponse(f"Admin note error: {exc}", status_code=500)


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