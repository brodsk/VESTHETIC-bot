from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import html, json, os, secrets, urllib.parse, urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

app = FastAPI()
security = HTTPBasic()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xtxqslzublggqhctmjoa.supabase.co").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
ADMIN_USER = os.getenv("ADMIN_PANEL_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PANEL_PASSWORD", "")
CRON_SECRET = os.getenv("CRON_SECRET", "")
ADMIN_IDS = [625577962]
MANAGER_ID = 8965656829
TZ = ZoneInfo("Europe/Bratislava")
TG = f"https://api.telegram.org/bot{BOT_TOKEN}"

STATUSES = ["new", "progress", "contacted", "interview", "registration", "active", "reject"]
LABELS = {
    "new": "⚪ Новая", "progress": "🟡 В работе", "contacted": "💬 Связались",
    "interview": "🎙 Интервью", "registration": "📝 Регистрация",
    "active": "🟢 Активна", "reject": "🔴 Отклонена",
}
TEXT = {
    "ru": {
        "welcome":"<b>VESTHETIC | Digital Talent Agency</b>\n\nМы помогаем совершеннолетним онлайн-креаторам строить карьеру на международных платформах.\n\n18+ only • Voluntary • Global",
        "about":"<b>VESTHETIC</b>\n\nDigital Talent Agency для взрослых онлайн-креаторов.\n\n<b>Модель:</b> 75% creator / 25% VESTHETIC",
        "terms":"<b>Условия</b>\n\n• Только 18+\n• Участие добровольное\n• 75% дохода — creator\n• 25% — VESTHETIC\n\nНе отправляйте документы или банковские данные через Telegram.",
        "faq":"<b>FAQ</b>\n\nОпыт не обязателен. Можно работать из дома. Участие только для совершеннолетних.",
        "apply":"<b>Заявка</b>\n\nЗаполнение займёт несколько минут. Продолжая, вы подтверждаете, что вам 18+ и участие добровольное.",
        "age":"Вам уже исполнилось 18 лет?",
        "name":"Как вас зовут или какой псевдоним хотите использовать?",
        "country":"В какой стране вы сейчас находитесь?",
        "languages":"Какими языками вы владеете?",
        "experience":"Есть ли опыт работы на подобных платформах?",
        "equipment":"Какое оборудование есть? Например: телефон, ПК, камера, свет.",
        "schedule":"Сколько времени в день или неделю готовы уделять работе?",
        "contact":"Укажите Telegram-контакт для связи с менеджером.",
        "source":"Откуда вы узнали о VESTHETIC?",
        "thanks":"<b>Заявка отправлена ✅</b>\n\nМенеджер VESTHETIC рассмотрит её и свяжется с вами.",
        "no":"К сожалению, VESTHETIC работает только с совершеннолетними.",
        "manager":"<b>Менеджер VESTHETIC</b>\n\n@VESTHETIC_manager",
        "language_prompt":"Выберите язык:",
        "save_error":"Не удалось сохранить заявку. Попробуйте ещё раз."
    },
    "en": {
        "welcome":"<b>VESTHETIC | Digital Talent Agency</b>\n\nWe help adult online creators build careers on international platforms.\n\n18+ only • Voluntary • Global",
        "about":"<b>VESTHETIC</b>\n\nDigital Talent Agency for adult online creators.\n\n<b>Model:</b> 75% creator / 25% VESTHETIC",
        "terms":"<b>Terms</b>\n\n• 18+ only\n• Voluntary participation\n• 75% creator\n• 25% VESTHETIC\n\nDo not send documents or banking details through Telegram.",
        "faq":"<b>FAQ</b>\n\nNo experience is required. Work can be done from home. Adults only.",
        "apply":"<b>Application</b>\n\nIt takes a few minutes. By continuing, you confirm you are 18+ and participating voluntarily.",
        "age":"Are you 18 or older?",
        "name":"What is your name or preferred pseudonym?",
        "country":"Which country are you currently in?",
        "languages":"Which languages do you speak?",
        "experience":"Do you have experience on similar platforms?",
        "equipment":"What equipment do you have? For example: phone, PC, camera, lighting.",
        "schedule":"How much time per day or week can you dedicate?",
        "contact":"Provide a Telegram contact for the manager.",
        "source":"How did you hear about VESTHETIC?",
        "thanks":"<b>Application submitted ✅</b>\n\nA VESTHETIC manager will review it and contact you.",
        "no":"VESTHETIC works only with adults.",
        "manager":"<b>VESTHETIC Manager</b>\n\n@VESTHETIC_manager",
        "language_prompt":"Choose your language:",
        "save_error":"Could not save the application. Please try again."
    },
    "sk": {
        "welcome":"<b>VESTHETIC | Digital Talent Agency</b>\n\nPomáhame dospelým online tvorcom budovať kariéru na medzinárodných platformách.\n\nIba 18+ • Dobrovoľné • Globálne",
        "about":"<b>VESTHETIC</b>\n\nDigitálna talentová agentúra pre dospelých online tvorcov.\n\n<b>Model:</b> 75 % creator / 25 % VESTHETIC",
        "terms":"<b>Podmienky</b>\n\n• Iba 18+\n• Dobrovoľná účasť\n• 75 % príjmu — creator\n• 25 % — VESTHETIC\n\nNeposielajte dokumenty ani bankové údaje cez Telegram.",
        "faq":"<b>FAQ</b>\n\nSkúsenosti nie sú potrebné. Pracovať môžete z domu. Účasť je len pre dospelých.",
        "apply":"<b>Žiadosť</b>\n\nVyplnenie trvá niekoľko minút. Pokračovaním potvrdzujete, že máte 18+ a účasť je dobrovoľná.",
        "age":"Máte už 18 rokov?",
        "name":"Ako sa voláte alebo aký pseudonym chcete používať?",
        "country":"V ktorej krajine sa momentálne nachádzate?",
        "languages":"Akými jazykmi hovoríte?",
        "experience":"Máte skúsenosti s podobnými platformami?",
        "equipment":"Aké vybavenie máte? Napríklad telefón, PC, kamera, osvetlenie.",
        "schedule":"Koľko času denne alebo týždenne môžete venovať práci?",
        "contact":"Uveďte Telegram kontakt, na ktorom vás môže manažér kontaktovať.",
        "source":"Ako ste sa dozvedeli o VESTHETIC?",
        "thanks":"<b>Žiadosť bola odoslaná ✅</b>\n\nManažér VESTHETIC ju posúdi a bude vás kontaktovať.",
        "no":"VESTHETIC spolupracuje iba s dospelými.",
        "manager":"<b>Manažér VESTHETIC</b>\n\n@VESTHETIC_manager",
        "language_prompt":"Vyberte si jazyk:",
        "save_error":"Žiadosť sa nepodarilo uložiť. Skúste to znova."
    },
    "ua": {
        "welcome":"<b>VESTHETIC | Digital Talent Agency</b>\n\nМи допомагаємо повнолітнім онлайн-креаторам будувати кар'єру на міжнародних платформах.\n\nТільки 18+ • Добровільно • Глобально",
        "about":"<b>VESTHETIC</b>\n\nDigital Talent Agency для дорослих онлайн-креаторів.\n\n<b>Модель:</b> 75% creator / 25% VESTHETIC",
        "terms":"<b>Умови</b>\n\n• Тільки 18+\n• Участь добровільна\n• 75% доходу — creator\n• 25% — VESTHETIC\n\nНе надсилайте документи або банківські дані через Telegram.",
        "faq":"<b>FAQ</b>\n\nДосвід не обов'язковий. Можна працювати з дому. Участь лише для повнолітніх.",
        "apply":"<b>Заявка</b>\n\nЗаповнення займе кілька хвилин. Продовжуючи, ви підтверджуєте, що вам 18+ і участь добровільна.",
        "age":"Вам уже виповнилося 18 років?",
        "name":"Як вас звати або який псевдонім ви хочете використовувати?",
        "country":"У якій країні ви зараз перебуваєте?",
        "languages":"Якими мовами ви володієте?",
        "experience":"Чи маєте ви досвід роботи на подібних платформах?",
        "equipment":"Яке обладнання у вас є? Наприклад: телефон, ПК, камера, освітлення.",
        "schedule":"Скільки часу на день або тиждень ви готові приділяти роботі?",
        "contact":"Вкажіть Telegram-контакт для зв'язку з менеджером.",
        "source":"Як ви дізналися про VESTHETIC?",
        "thanks":"<b>Заявку надіслано ✅</b>\n\nМенеджер VESTHETIC розгляне її та зв'яжеться з вами.",
        "no":"На жаль, VESTHETIC працює лише з повнолітніми.",
        "manager":"<b>Менеджер VESTHETIC</b>\n\n@VESTHETIC_manager",
        "language_prompt":"Оберіть мову:",
        "save_error":"Не вдалося зберегти заявку. Спробуйте ще раз."
    },
}
def sb(method, path, payload=None, query=None):
    if not SUPABASE_KEY: return None
    url=f"{SUPABASE_URL}/rest/v1/{path}"
    if query: url += "?" + urllib.parse.urlencode(query)
    headers={"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json"}
    if method=="POST": headers["Prefer"]="return=representation"
    if method in ("PATCH","PUT"): headers["Prefer"]="return=representation"
    try:
        body=json.dumps(payload,ensure_ascii=False).encode() if payload is not None else None
        req=urllib.request.Request(url,data=body,headers=headers,method=method)
        with urllib.request.urlopen(req,timeout=5) as r:
            raw=r.read().decode()
            return json.loads(raw) if raw else []
    except Exception as e:
        print("SUPABASE:",repr(e)); return None

def tg(method,data=None):
    if not BOT_TOKEN: return None
    try:
        body=urllib.parse.urlencode(data or {}).encode()
        req=urllib.request.Request(f"{TG}/{method}",data=body)
        with urllib.request.urlopen(req,timeout=5) as r: return json.loads(r.read().decode())
    except Exception as e:
        print("TELEGRAM:",repr(e)); return None

def send(chat,text,markup=None):
    d={"chat_id":chat,"text":text,"parse_mode":"HTML"}
    if markup: d["reply_markup"]=json.dumps(markup,ensure_ascii=False)
    return tg("sendMessage",d)

def answer(cid,text=""): return tg("answerCallbackQuery",{"callback_query_id":cid,"text":text})

def edit(chat,mid,text,markup=None):
    d={"chat_id":chat,"message_id":mid,"text":text,"parse_mode":"HTML"}
    if markup: d["reply_markup"]=json.dumps(markup,ensure_ascii=False)
    return tg("editMessageText",d)

def kb_lang():
    return {"inline_keyboard":[[
        {"text":"🇷🇺 Русский","callback_data":"lang_ru"},{"text":"🇺🇦 Українська","callback_data":"lang_ua"}],
        [{"text":"🇸🇰 Slovenčina","callback_data":"lang_sk"},{"text":"🇬🇧 English","callback_data":"lang_en"}]]}

def kb_main(lang):
    labels={"ru":["ℹ️ О VESTHETIC","📋 Условия","❓ FAQ","🚀 Подать заявку","👤 Менеджер","🌐 Язык"],
            "en":["ℹ️ About","📋 Terms","❓ FAQ","🚀 Apply","👤 Manager","🌐 Language"],
            "sk":["ℹ️ O VESTHETIC","📋 Podmienky","❓ FAQ","🚀 Žiadosť","👤 Manažér","🌐 Jazyk"],
            "ua":["ℹ️ Про VESTHETIC","📋 Умови","❓ FAQ","🚀 Подати заявку","👤 Менеджер","🌐 Мова"]}
    acts=["about","terms","faq","apply","manager","language"]
    return {"inline_keyboard":[[{"text":a,"callback_data":b}] for a,b in zip(labels.get(lang,labels["en"]),acts)]}

def user_get(chat,username):
    rows=sb("GET","bot_users",query={"telegram_chat_id":f"eq.{chat}","select":"*","limit":"1"})
    if rows:
        u=rows[0]; draft=u.get("application_draft") or {}
        if isinstance(draft,str):
            try: draft=json.loads(draft)
            except: draft={}
        return {"lang":u.get("language") or "en","state":u.get("state"),"application":draft}
    u={"lang":"en","state":None,"application":{}}
    user_save(chat,username,u); return u

def user_save(chat,username,u):
    payload={"telegram_chat_id":chat,"telegram_username":username,
        "language":u.get("lang","en"),"state":u.get("state"),"application_draft":u.get("application",{})}
    updated=sb("PATCH","bot_users",payload,{"telegram_chat_id":f"eq.{chat}","select":"*"})
    if updated:
        return updated
    return sb("POST","bot_users",payload)

def manager_markup(i):
    return {"inline_keyboard":[[
        {"text":"🟢 Принять","callback_data":f"mgr_accept_{i}"},
        {"text":"🟡 В работе","callback_data":f"mgr_progress_{i}"},
        {"text":"🔴 Отклонить","callback_data":f"mgr_reject_{i}"}
    ]]}

def notify_candidate(app_data, action):
    chat=app_data.get("telegram_chat_id")
    if not chat:
        return
    user=user_get(chat, app_data.get("telegram_username"))
    lang=user.get("lang") or "en"
    messages={
        "ru":{
            "accept":"<b>Ваша заявка принята! 🟢</b>\n\nСпасибо за заявку. Менеджер VESTHETIC свяжется с вами и расскажет о следующих шагах.",
            "progress":"<b>Ваша заявка взята в работу! 🟡</b>\n\nМенеджер VESTHETIC уже рассматривает вашу заявку и свяжется с вами в ближайшее время.",
            "reject":"<b>Ваша заявка отклонена 🔴</b>\n\nСпасибо за интерес к VESTHETIC. Желаем вам успехов!"
        },
        "en":{
            "accept":"<b>Your application has been accepted! 🟢</b>\n\nThank you for applying. A VESTHETIC manager will contact you with the next steps.",
            "progress":"<b>Your application is now in progress! 🟡</b>\n\nA VESTHETIC manager is reviewing your application and will contact you soon.",
            "reject":"<b>Your application has been declined 🔴</b>\n\nThank you for your interest in VESTHETIC. We wish you all the best!"
        },
        "sk":{
            "accept":"<b>Vaša žiadosť bola prijatá! 🟢</b>\n\nĎakujeme za vašu žiadosť. Manažér VESTHETIC vás bude kontaktovať s ďalšími krokmi.",
            "progress":"<b>Vaša žiadosť je v procese! 🟡</b>\n\nManažér VESTHETIC ju práve posudzuje a čoskoro vás bude kontaktovať.",
            "reject":"<b>Vaša žiadosť bola zamietnutá 🔴</b>\n\nĎakujeme za váš záujem o VESTHETIC."
        },
        "ua":{
            "accept":"<b>Вашу заявку прийнято! 🟢</b>\n\nДякуємо за заявку. Менеджер VESTHETIC зв’яжеться з вами щодо наступних кроків.",
            "progress":"<b>Вашу заявку взято в роботу! 🟡</b>\n\nМенеджер VESTHETIC вже розглядає вашу заявку і скоро зв’яжеться з вами.",
            "reject":"<b>Вашу заявку відхилено 🔴</b>\n\nДякуємо за інтерес до VESTHETIC."
        }
    }
    send(chat,messages.get(lang,messages["en"])[action],kb_main(lang))

def application_create(chat,username,d):
    rows=sb("POST","applications",{"telegram_chat_id":chat,"telegram_username":username,
        "name":d.get("name"),"age_confirmed":True,"country":d.get("country"),
        "languages":d.get("languages"),"experience":d.get("experience"),"equipment":d.get("equipment"),
        "schedule":d.get("schedule"),"contact":d.get("contact"),"source":d.get("source"),
        "status":"new","status_changed_by_telegram_id":None,"internal_notes":""})
    if not rows:
        return None
    a=rows[0]
    msg=(
        "<b>🆕 Новая заявка VESTHETIC</b>\n\n"
        f"<b>Имя:</b> {esc(d.get('name'))}\n"
        f"<b>Страна:</b> {esc(d.get('country'))}\n"
        f"<b>Языки:</b> {esc(d.get('languages'))}\n"
        f"<b>Опыт:</b> {esc(d.get('experience'))}\n"
        f"<b>Оборудование:</b> {esc(d.get('equipment'))}\n"
        f"<b>График:</b> {esc(d.get('schedule'))}\n"
        f"<b>Контакт:</b> {esc(d.get('contact'))}\n"
        f"<b>Источник:</b> {esc(d.get('source'))}\n"
        f"<b>Заявка:</b> #{esc(a.get('id'))}"
    )
    send(MANAGER_ID,msg,manager_markup(a.get("id")))
    return a

def app_get(i):
    r=sb("GET","applications",query={"id":f"eq.{i}","select":"*","limit":"1"}); return r[0] if r else None

def apps():
    r=sb("GET","applications",query={"select":"*","order":"created_at.desc","limit":"1000"}); return r or []

def esc(v): return html.escape(str(v if v is not None else "—"))

def process_message(m):
    chat=m.get("chat",{}).get("id"); text=(m.get("text") or "").strip()
    if not chat: return
    username=m.get("chat",{}).get("username")
    u=user_get(chat,username)
    lang=u["lang"]
    if text.startswith("/start"):
        u={"lang":lang,"state":None,"application":{}}; user_save(chat,username,u)
        send(chat,"<b>VESTHETIC</b>",kb_lang()); return
    state=u.get("state")
    if state and state.startswith("apply_"):
        steps=["apply_name","apply_country","apply_languages","apply_experience","apply_equipment","apply_schedule","apply_contact","apply_source"]
        key=state
        if key=="apply_name": u["application"]["name"]=text
        elif key=="apply_country": u["application"]["country"]=text
        elif key=="apply_languages": u["application"]["languages"]=text
        elif key=="apply_experience": u["application"]["experience"]=text
        elif key=="apply_equipment": u["application"]["equipment"]=text
        elif key=="apply_schedule": u["application"]["schedule"]=text
        elif key=="apply_contact": u["application"]["contact"]=text
        elif key=="apply_source": u["application"]["source"]=text
        idx=steps.index(key)
        if idx==len(steps)-1:
            a=application_create(chat,username,u["application"])
            u={"lang":lang,"state":None,"application":{}}
            user_save(chat,username,u)
            send(chat,TEXT[lang]["thanks"] if a else TEXT[lang]["save_error"],kb_main(lang)); return
        u["state"]=steps[idx+1]; user_save(chat,username,u)
        send(chat,TEXT[lang][steps[idx+1].replace("apply_","")]); return
    if text in ("/help",):
        send(chat,TEXT[lang]["faq"],kb_main(lang))

def process_callback(c):
    chat=c.get("message",{}).get("chat",{}).get("id"); mid=c.get("message",{}).get("message_id")
    data=c.get("data",""); cid=c.get("id")
    if not chat: return
    username=c.get("from",{}).get("username")
    u=user_get(chat,username); lang=u["lang"]
    if data.startswith("lang_"):
        lang=data[5:] if data[5:] in TEXT else "en"; u["lang"]=lang; u["state"]=None; user_save(chat,username,u)
        edit(chat,mid,TEXT[lang]["welcome"],kb_main(lang)); answer(cid); return
    if data=="language": edit(chat,mid,TEXT[lang]["language_prompt"],kb_lang()); answer(cid); return
    if data in ("about","terms","faq","manager"):
        edit(chat,mid,TEXT[lang][data],kb_main(lang)); answer(cid); return
    if data=="apply":
        u["state"]="apply_age"; u["application"]={}; user_save(chat,username,u)
        edit(chat,mid,TEXT[lang]["apply"],{"inline_keyboard":[[{"text":"18+","callback_data":"age_yes"},{"text":"Under 18","callback_data":"age_no"}]]}); answer(cid); return
    if data=="age_no":
        u["state"]=None; user_save(chat,username,u); edit(chat,mid,TEXT[lang]["no"]); answer(cid); return
    if data.startswith("mgr_"):
        parts=data.split("_")
        if len(parts)==3 and str(parts[2]).isdigit():
            i=int(parts[2])
            status_map={"accept":"active","progress":"progress","reject":"reject"}
            action=parts[1]
            if action in status_map:
                sb("PATCH","applications",{"status":status_map[action],"status_changed_by_telegram_id":MANAGER_ID},{"id":f"eq.{i}"})
                labels={"accept":"🟢 Заявка принята","progress":"🟡 Заявка взята в работу","reject":"🔴 Заявка отклонена"}
                answer(cid,labels[action])
                edit(chat,mid, f"<b>{labels[action]}</b>\n\nЗаявка #{i}")
                candidate=app_get(i)
                if candidate:
                    notify_candidate(candidate, action)
        return
    if data=="age_yes":
        u["state"]="apply_name"; u["application"]={"age_confirmed":True}; user_save(chat,username,u)
        edit(chat,mid,TEXT[lang]["name"]); answer(cid); return

@app.post("/api/webhook")
async def webhook(request:Request):
    try:
        update=await request.json()
        if update.get("callback_query"): process_callback(update["callback_query"])
        elif update.get("message"): process_message(update["message"])
        return {"ok":True}
    except Exception as e:
        print("WEBHOOK:",repr(e)); return {"ok":False,"error":str(e)}

@app.get("/")
async def root(): return {"service":"VESTHETIC","ok":True}

@app.get("/api")
async def api_root(): return {"service":"VESTHETIC","ok":True}

@app.get("/api/health")
async def health(): return {"ok":True,"supabase":bool(SUPABASE_KEY),"telegram":bool(BOT_TOKEN)}

def auth(c):
    return secrets.compare_digest(c.username or "",ADMIN_USER) and secrets.compare_digest(c.password or "",ADMIN_PASSWORD)

@app.get("/admin",response_class=HTMLResponse)
async def admin(c:HTTPBasicCredentials=Depends(security)):
    if not auth(c): return HTMLResponse("Нет доступа",401,headers={"WWW-Authenticate":"Basic"})
    rows=apps(); counts={s:sum(1 for a in rows if a.get("status")==s) for s in STATUSES}
    trs=[]
    for a in rows:
        i=a.get("id"); status=a.get("status","new")
        trs.append(f"<tr><td>#{esc(i)}</td><td><a href='/admin/application/{esc(i)}'>{esc(a.get('name'))}</a></td><td>{esc(a.get('country'))}</td><td>{esc(a.get('languages'))}</td><td>{esc(a.get('status'))}</td><td>{esc(a.get('created_at'))}</td></tr>")
    stats=" ".join(f"<span class='stat'><b>{counts[s]}</b> {LABELS[s]}</span>" for s in STATUSES)
    return HTMLResponse(f"""<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>
<title>VESTHETIC — CRM</title><style>
body{{font-family:system-ui;background:#0b0b0b;color:#eee;max-width:1200px;margin:auto;padding:24px}}a{{color:#fff}}.stats{{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}}.stat,table{{background:#151515;border:1px solid #292929;border-radius:10px;padding:10px}}table{{width:100%;border-collapse:collapse;padding:0}}td,th{{padding:11px;border-bottom:1px solid #292929;text-align:left}}tr:last-child td{{border:0}}@media(max-width:700px){{body{{padding:12px;font-size:14px}}table{{font-size:12px}}th:nth-child(4),td:nth-child(4),th:nth-child(6),td:nth-child(6){{display:none}}}}
</style><h1>VESTHETIC <small>CRM</small></h1><div class=stats>{stats}</div>
<table><tr><th>ID</th><th>Имя</th><th>Страна</th><th>Языки</th><th>Статус</th><th>Создана</th></tr>{''.join(trs) or '<tr><td colspan=6>Заявок пока нет</td></tr>'}</table>""")

@app.get("/admin/application/{i}",response_class=HTMLResponse)
async def detail(i:int,c:HTTPBasicCredentials=Depends(security)):
    if not auth(c): return HTMLResponse("Нет доступа",401,headers={"WWW-Authenticate":"Basic"})
    a=app_get(i)
    if not a: return HTMLResponse("Не найдено",404)
    buttons=" ".join(f"<button name=status value='{s}'>{LABELS[s]}</button>" for s in STATUSES if s!="new")
    return HTMLResponse(f"""<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Заявка #{i}</title><style>body{{font-family:system-ui;background:#0b0b0b;color:#eee;max-width:900px;margin:auto;padding:20px}}a{{color:#fff}}.card{{background:#151515;border:1px solid #292929;border-radius:12px;padding:16px;margin:12px 0}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}.item{{padding:9px;border-bottom:1px solid #292929}}button,textarea{{font:inherit;background:#222;color:#fff;border:1px solid #333;border-radius:8px;padding:10px}}textarea{{width:100%;min-height:100px}}@media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}</style>
<a href=/admin>← CRM</a><h1>Заявка #{i}</h1><div class=card><div class=grid>
{''.join(f"<div class=item><b>{esc(k)}</b><br>{esc(v)}</div>" for k,v in [("Имя",a.get("name")),("Страна",a.get("country")),("Языки",a.get("languages")),("Опыт",a.get("experience")),("Оборудование",a.get("equipment")),("График",a.get("schedule")),("Контакт",a.get("contact")),("Источник",a.get("source")),("Telegram",a.get("telegram_username")),("Создана",a.get("created_at")),("Статус",LABELS.get(a.get("status"),a.get("status")))])}
</div></div><div class=card><form method=post action=/admin/status><input type=hidden name=id value={i}>{buttons}</form>
<form method=post action=/admin/delete style="margin-top:12px"><input type=hidden name=id value={i}><button type=submit>🗑 Удалить заявку</button></form></div>
<div class=card><h2>Внутренние заметки</h2><pre>{esc(a.get("internal_notes") or "—")}</pre><form method=post action=/admin/note><input type=hidden name=id value={i}><textarea name=note required></textarea><br><button>＋ Добавить заметку</button></form></div>""")

async def form(request):
    raw=await request.body(); return urllib.parse.parse_qs(raw.decode(),keep_blank_values=True)

@app.post("/admin/status")
async def status(request:Request,c:HTTPBasicCredentials=Depends(security)):
    if not auth(c): return PlainTextResponse("Нет доступа",401)
    f=await form(request); i=int(f.get("id",["0"])[0]); s=f.get("status",[""])[0]
    if s not in STATUSES: return PlainTextResponse("Недопустимый статус",400)
    r=sb("PATCH","applications",{"status":s,"status_changed_by_telegram_id":MANAGER_ID},{"id":f"eq.{i}","select":"*"})
    return RedirectResponse(f"/admin/application/{i}",303) if r else PlainTextResponse("Ошибка обновления",500)

@app.post("/admin/delete")
async def delete_request(request:Request,c:HTTPBasicCredentials=Depends(security)):
    if not auth(c): return PlainTextResponse("Нет доступа",401)
    f=await form(request); i=int(f.get("id",["0"])[0]); a=app_get(i)
    if not a: return PlainTextResponse("Не найдено",404)
    return HTMLResponse(f"""<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Удаление заявки #{i}</title><style>body{{font-family:system-ui;background:#0b0b0b;color:#eee;max-width:700px;margin:auto;padding:20px}}.card{{background:#151515;border:1px solid #292929;border-radius:12px;padding:20px;margin:20px 0}}button,a{{font:inherit;background:#222;color:#fff;border:1px solid #333;border-radius:8px;padding:10px 14px;text-decoration:none;display:inline-block}}.danger{{background:#441515;border-color:#662020}}</style>
<div class=card><h1>Удалить заявку #{i}?</h1><p><b>{esc(a.get("name") or "Без имени")}</b> — {esc(a.get("country") or "—")}</p><p>Это действие удалит заявку из CRM.</p>
<form method=post action=/admin/delete-confirm><input type=hidden name=id value={i}><button class=danger type=submit>Да, удалить</button> <a href=/admin/application/{i}>Отмена</a></form></div>""")

@app.post("/admin/note")
async def note(request:Request,c:HTTPBasicCredentials=Depends(security)):
    if not auth(c): return PlainTextResponse("Нет доступа",401)
    f=await form(request); i=int(f.get("id",["0"])[0]); note=f.get("note",[""])[0].strip(); a=app_get(i)
    if not a: return PlainTextResponse("Не найдено",404)
    old=(a.get("internal_notes") or "").strip(); stamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    value=(old+"\n" if old else "")+f"[{stamp}] {MANAGER_ID}: {note}"
    r=sb("PATCH","applications",{"internal_notes":value},{"id":f"eq.{i}","select":"*"})
    return RedirectResponse(f"/admin/application/{i}",303) if r else PlainTextResponse("Ошибка обновления",500)

@app.post("/admin/delete-confirm")
async def delete_confirm(request:Request,c:HTTPBasicCredentials=Depends(security)):
    if not auth(c): return PlainTextResponse("Нет доступа",401)
    f=await form(request); i=int(f.get("id",["0"])[0])
    r=sb("DELETE","applications",query={"id":f"eq.{i}"})
    if r is None: return PlainTextResponse("Ошибка удаления",500)
    return RedirectResponse("/admin",303)

@app.get("/api/cron/followups")
async def followups(request:Request):
    if not CRON_SECRET or not secrets.compare_digest(request.headers.get("authorization",""),f"Bearer {CRON_SECRET}"):
        return PlainTextResponse("Нет доступа",401)
    return {"ok":True,"message":"Follow-up worker disabled in clean rebuild"}

@app.get("/api/webhook")
async def webhook_get(): return {"ok":True,"method":"POST only"}

@app.get("/robots.txt")
async def robots(): return PlainTextResponse("User-agent: *\nDisallow: /admin")
