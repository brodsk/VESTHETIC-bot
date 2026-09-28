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
        "welcome":"<b>VESTHETIC | Digital Talent Agency</b>\n\nVESTHETIC помогает совершеннолетним онлайн-креаторам развивать карьеру на международных платформах. Мы берём на себя организационную часть, коммуникацию и сопровождение, чтобы creator мог сосредоточиться на своей работе.\n\n<b>18+ only • Voluntary • Global</b>\n\nУчастие добровольное. Условия и формат сотрудничества обсуждаются индивидуально после рассмотрения заявки.",        "about":"<b>VESTHETIC</b>\n\nVESTHETIC — Digital Talent Agency для взрослых онлайн-креаторов, которые хотят работать системно и развиваться на международном рынке.\n\nМы помогаем с организацией рабочего процесса, коммуникацией и сопровождением. Конкретный формат работы зависит от платформ, задач и договорённостей с creator.\n\n<b>Модель сотрудничества:</b> 75% creator / 25% VESTHETIC.\n\nНаша цель — выстроить понятный и профессиональный процесс, в котором creator понимает условия, формат работы и дальнейшие шаги.",        "terms":"<b>Условия сотрудничества</b>\n\n<b>Возраст</b>\nК сотрудничеству допускаются только совершеннолетние — 18+.\n\n<b>Добровольность</b>\nУчастие добровольное. Вы сами принимаете решение о начале и продолжении сотрудничества.\n\n<b>Доход</b>\nБазовая модель распределения: 75% дохода получает creator, 25% — VESTHETIC. Конкретные условия могут обсуждаться до начала сотрудничества.\n\n<b>Формат работы</b>\nРабота может выполняться удалённо. График и рабочие условия согласовываются индивидуально.\n\n<b>Конфиденциальность</b>\nНе отправляйте документы, банковские данные, пароли или другие чувствительные данные через Telegram. Если такие данные понадобятся на официальном этапе оформления, менеджер отдельно объяснит безопасный порядок их передачи.",        "faq":"<b>FAQ</b>\n\n<b>Кто может подать заявку?</b>\nТолько совершеннолетние — 18+.\n\n<b>Нужен ли опыт?</b>\nНет. Опыт работы на подобных платформах не обязателен.\n\n<b>Где можно работать?</b>\nРаботать можно из дома или из другого удобного для вас места.\n\n<b>Какое оборудование нужно?</b>\nНа старте достаточно телефона или ПК. Дополнительное оборудование зависит от выбранного формата работы.\n\n<b>Какой график?</b>\nГрафик согласовывается индивидуально с учётом вашей доступности.\n\n<b>Как распределяется доход?</b>\n75% получает creator, 25% — VESTHETIC.\n\n<b>Есть ли обучение?</b>\nМенеджер расскажет о процессе и следующих шагах после рассмотрения заявки.\n\n<b>Как подать заявку?</b>\nНажмите «Подать заявку» в меню и заполните короткую анкету.\n\n<b>Что происходит после заявки?</b>\nЗаявку рассматривает менеджер VESTHETIC, после чего связывается с вами.\n\n<b>Безопасны ли мои данные?</b>\nНе отправляйте документы или банковские данные через Telegram.\n\nЕсли остались вопросы — свяжитесь с менеджером VESTHETIC.",        "apply":"<b>Заявка в VESTHETIC</b>\n\nЗаполнение анкеты займёт несколько минут. Нам нужна базовая информация о вас, вашем опыте и доступности, чтобы менеджер мог оценить подходящий формат сотрудничества.\n\nПеред началом подтвердите, что вам уже исполнилось 18 лет и участие добровольное.",        "age":"Вам уже исполнилось 18 лет?",
        "name":"<b>1/8 — Имя</b>\n\nКак вас зовут или какой рабочий псевдоним вы хотели бы использовать?",        "country":"<b>2/8 — Страна</b>\n\nВ какой стране вы сейчас находитесь? Укажите страну проживания или фактического нахождения.",        "languages":"<b>3/8 — Языки</b>\n\nКакими языками вы владеете и на каком уровне? Например: русский — свободно, английский — B2.",        "experience":"<b>4/8 — Опыт</b>\n\nЕсть ли у вас опыт работы на онлайн-платформах, создания контента, стриминга или другой похожей деятельности? Если опыта нет — так и напишите.",        "equipment":"<b>5/8 — Оборудование</b>\n\nКакое оборудование у вас есть? Укажите телефон, ПК или ноутбук, камеру, микрофон, освещение и другое оборудование.",        "schedule":"<b>6/8 — График</b>\n\nСколько времени вы реально готовы уделять работе? Укажите примерное количество часов в день или неделю и удобное время.",        "contact":"<b>7/8 — Контакт</b>\n\nУкажите Telegram-контакт, по которому менеджер сможет связаться с вами. Можно отправить @username.",        "source":"<b>8/8 — Источник</b>\n\nГде вы впервые увидели VESTHETIC: Telegram, Instagram, TikTok, рекомендация, поиск или другой источник?",        "thanks":"<b>Заявка отправлена ✅</b>\n\nСпасибо за интерес к VESTHETIC. Менеджер рассмотрит вашу заявку и свяжется с вами, если будет подходящий формат сотрудничества.\n\nСледите за сообщениями в Telegram.",        "no":"<b>VESTHETIC — 18+</b>\n\nМы рассматриваем заявки только от совершеннолетних. Если вам ещё нет 18 лет, подать заявку сейчас нельзя.",        "manager":"<b>Менеджер VESTHETIC</b>\n\nЕсли у вас есть вопрос до подачи заявки или нужна дополнительная информация, свяжитесь с менеджером.\n\n@VESTHETIC_manager",        "language_prompt":"Выберите язык:",
        "save_error":"Не удалось сохранить заявку. Попробуйте ещё раз."
    },
    "en": {
        "welcome":"<b>VESTHETIC | Digital Talent Agency</b>\n\nVESTHETIC helps adult online creators build and develop their careers on international platforms. We handle the organizational side, communication and support so creators can focus on their work.\n\n<b>18+ only • Voluntary • Global</b>\n\nParticipation is voluntary. The cooperation terms and format are discussed individually after an application is reviewed.",        "about":"<b>VESTHETIC</b>\n\nVESTHETIC is a Digital Talent Agency for adult online creators who want to work professionally and develop in the international market.\n\nWe provide support with organization, workflow, communication and ongoing coordination. The exact format depends on the platforms, tasks and individual agreement with the creator.\n\n<b>Cooperation model:</b> 75% creator / 25% VESTHETIC.\n\nOur goal is to create a clear and professional process where every creator understands the terms, workflow and next steps.",        "terms":"<b>Cooperation Terms</b>\n\n<b>Age</b>\nOnly adults aged 18+ can apply.\n\n<b>Voluntary participation</b>\nParticipation is voluntary. You decide whether to start and continue the cooperation.\n\n<b>Income</b>\nThe standard revenue model is 75% to the creator and 25% to VESTHETIC. Specific terms can be discussed before cooperation begins.\n\n<b>Work format</b>\nWork can be performed remotely. Schedule and working conditions are agreed individually.\n\n<b>Privacy</b>\nDo not send documents, banking details, passwords or other sensitive information through Telegram. If such information is required during official onboarding, a manager will explain the secure way to provide it.",        "faq":"<b>FAQ</b>\n\n<b>Who can apply?</b>\nAdults only — 18+.\n\n<b>Do I need experience?</b>\nNo. Previous experience on similar platforms is not required.\n\n<b>Where can I work?</b>\nYou can work from home or another location that is convenient for you.\n\n<b>What equipment do I need?</b>\nA phone or PC is enough to get started. Additional equipment depends on the chosen work format.\n\n<b>What is the schedule?</b>\nYour schedule is agreed individually based on your availability.\n\n<b>How is the income split?</b>\n75% goes to the creator, 25% to VESTHETIC.\n\n<b>Is training provided?</b>\nA manager will explain the process and next steps after reviewing your application.\n\n<b>How do I apply?</b>\nTap «Apply» in the menu and complete the short application.\n\n<b>What happens after I apply?</b>\nA VESTHETIC manager reviews your application and then contacts you.\n\n<b>Are my data safe?</b>\nDo not send documents or banking details through Telegram.\n\nIf you have more questions, contact the VESTHETIC manager.",        "apply":"<b>VESTHETIC Application</b>\n\nThe application takes a few minutes. We ask for basic information about you, your experience and availability so a manager can assess a suitable cooperation format.\n\nBefore starting, confirm that you are 18 or older and that participation is voluntary.",        "age":"Are you 18 or older?",
        "name":"<b>1/8 — Name</b>\n\nWhat is your name or preferred working pseudonym?",        "country":"<b>2/8 — Country</b>\n\nWhich country are you currently in? Please provide your country of residence or current location.",        "languages":"<b>3/8 — Languages</b>\n\nWhich languages do you speak and at what level? For example: Russian — fluent, English — B2.",        "experience":"<b>4/8 — Experience</b>\n\nDo you have experience with online platforms, content creation, streaming or similar work? If not, simply say so.",        "equipment":"<b>5/8 — Equipment</b>\n\nWhat equipment do you have? Please mention your phone, PC or laptop, camera, microphone, lighting and other equipment.",        "schedule":"<b>6/8 — Schedule</b>\n\nHow much time can you realistically dedicate to the work? Give an approximate number of hours per day or week and your preferred hours.",        "contact":"<b>7/8 — Contact</b>\n\nProvide a Telegram contact where a manager can reach you. You can send your @username.",        "source":"<b>8/8 — Source</b>\n\nWhere did you first discover VESTHETIC: Telegram, Instagram, TikTok, a recommendation, search or another source?",        "thanks":"<b>Application submitted ✅</b>\n\nThank you for your interest in VESTHETIC. A manager will review your application and contact you if there is a suitable cooperation format.\n\nPlease watch your Telegram messages.",        "no":"<b>VESTHETIC — 18+</b>\n\nWe only review applications from adults. If you are under 18, you cannot apply at this time.",        "manager":"<b>VESTHETIC Manager</b>\n\nIf you have a question before applying or need additional information, contact the manager.\n\n@VESTHETIC_manager",        "language_prompt":"Choose your language:",
        "save_error":"Could not save the application. Please try again."
    },
    "sk": {
        "welcome":"<b>VESTHETIC | Digital Talent Agency</b>\n\nVESTHETIC pomáha dospelým online tvorcom budovať a rozvíjať kariéru na medzinárodných platformách. Zabezpečujeme organizačnú stránku, komunikáciu a podporu, aby sa tvorca mohol sústrediť na svoju prácu.\n\n<b>Iba 18+ • Dobrovoľné • Globálne</b>\n\nÚčasť je dobrovoľná. Podmienky a forma spolupráce sa dohodnú individuálne po posúdení žiadosti.",        "about":"<b>VESTHETIC</b>\n\nVESTHETIC je Digital Talent Agency pre dospelých online tvorcov, ktorí chcú pracovať profesionálne a rozvíjať sa na medzinárodnom trhu.\n\nPomáhame s organizáciou práce, komunikáciou, pracovným procesom a priebežnou podporou. Konkrétna forma závisí od platforiem, úloh a individuálnej dohody s creatorom.\n\n<b>Model spolupráce:</b> 75 % creator / 25 % VESTHETIC.\n\nNaším cieľom je vytvoriť jasný a profesionálny proces, v ktorom creator rozumie podmienkam, spôsobu práce a ďalším krokom.",        "terms":"<b>Podmienky spolupráce</b>\n\n<b>Vek</b>\nŽiadosť môžu podať iba dospelé osoby vo veku 18+.\n\n<b>Dobrovoľnosť</b>\nÚčasť je dobrovoľná. O začatí aj pokračovaní spolupráce rozhodujete sami.\n\n<b>Príjem</b>\nZákladný model rozdelenia príjmu je 75 % pre creatora a 25 % pre VESTHETIC. Konkrétne podmienky je možné dohodnúť pred začiatkom spolupráce.\n\n<b>Forma práce</b>\nPráca môže prebiehať na diaľku. Rozvrh a pracovné podmienky sa dohodnú individuálne.\n\n<b>Ochrana údajov</b>\nNeposielajte dokumenty, bankové údaje, heslá ani iné citlivé informácie cez Telegram. Ak budú takéto údaje potrebné počas oficiálneho nástupu, manažér vám vysvetlí bezpečný spôsob ich odovzdania.",        "faq":"<b>FAQ</b>\n\n<b>Kto môže podať žiadosť?</b>\nIba dospelí — 18+.\n\n<b>Potrebujem skúsenosti?</b>\nNie. Predchádzajúce skúsenosti s podobnými platformami nie sú potrebné.\n\n<b>Kde môžem pracovať?</b>\nPracovať môžete z domu alebo z iného miesta, ktoré vám vyhovuje.\n\n<b>Aké vybavenie potrebujem?</b>\nNa začiatok stačí telefón alebo PC. Ďalšie vybavenie závisí od zvoleného formátu práce.\n\n<b>Aký je pracovný čas?</b>\nRozvrh sa dohodne individuálne podľa vašich možností.\n\n<b>Ako sa delí príjem?</b>\n75 % dostáva creator, 25 % VESTHETIC.\n\n<b>Je k dispozícii školenie?</b>\nManažér vám po posúdení žiadosti vysvetlí proces a ďalšie kroky.\n\n<b>Ako podať žiadosť?</b>\nV menu stlačte «Žiadosť» a vyplňte krátky formulár.\n\n<b>Čo sa stane po odoslaní žiadosti?</b>\nManažér VESTHETIC žiadosť posúdi a následne vás kontaktuje.\n\n<b>Sú moje údaje v bezpečí?</b>\nNeposielajte dokumenty ani bankové údaje cez Telegram.\n\nAk máte ďalšie otázky, kontaktujte manažéra VESTHETIC.",        "apply":"<b>Žiadosť do VESTHETIC</b>\n\nVyplnenie žiadosti trvá niekoľko minút. Potrebujeme základné informácie o vás, vašich skúsenostiach a dostupnosti, aby manažér mohol posúdiť vhodnú formu spolupráce.\n\nPred začiatkom potvrďte, že máte 18 rokov alebo viac a účasť je dobrovoľná.",        "age":"Máte už 18 rokov?",
        "name":"<b>1/8 — Meno</b>\n\nAko sa voláte alebo aký pracovný pseudonym chcete používať?",        "country":"<b>2/8 — Krajina</b>\n\nV ktorej krajine sa momentálne nachádzate? Uveďte krajinu pobytu alebo aktuálne miesto.",        "languages":"<b>3/8 — Jazyky</b>\n\nAkými jazykmi hovoríte a na akej úrovni? Napríklad: ruština — plynule, angličtina — B2.",        "experience":"<b>4/8 — Skúsenosti</b>\n\nMáte skúsenosti s online platformami, tvorbou obsahu, streamovaním alebo podobnou prácou? Ak nie, jednoducho to uveďte.",        "equipment":"<b>5/8 — Vybavenie</b>\n\nAké vybavenie máte? Uveďte telefón, PC alebo notebook, kameru, mikrofón, osvetlenie a ďalšie vybavenie.",        "schedule":"<b>6/8 — Časový rozvrh</b>\n\nKoľko času môžete reálne venovať práci? Uveďte približný počet hodín denne alebo týždenne a čas, ktorý vám vyhovuje.",        "contact":"<b>7/8 — Kontakt</b>\n\nUveďte Telegram kontakt, na ktorom vás môže manažér kontaktovať. Môžete poslať svoje @username.",        "source":"<b>8/8 — Zdroj</b>\n\nKde ste prvýkrát videli VESTHETIC: Telegram, Instagram, TikTok, odporúčanie, vyhľadávanie alebo iný zdroj?",        "thanks":"<b>Žiadosť bola odoslaná ✅</b>\n\nĎakujeme za váš záujem o VESTHETIC. Manažér žiadosť posúdi a bude vás kontaktovať, ak bude k dispozícii vhodná forma spolupráce.\n\nSledujte prosím správy v Telegrame.",        "no":"<b>VESTHETIC — 18+</b>\n\nPosudzujeme iba žiadosti od plnoletých osôb. Ak ešte nemáte 18 rokov, momentálne sa nemôžete prihlásiť.",        "manager":"<b>Manažér VESTHETIC</b>\n\nAk máte otázku pred podaním žiadosti alebo potrebujete ďalšie informácie, kontaktujte manažéra.\n\n@VESTHETIC_manager",        "language_prompt":"Vyberte si jazyk:",
        "save_error":"Žiadosť sa nepodarilo uložiť. Skúste to znova."
    },
    "ua": {
        "welcome":"<b>VESTHETIC | Digital Talent Agency</b>\n\nVESTHETIC допомагає повнолітнім онлайн-креаторам будувати та розвивати кар’єру на міжнародних платформах. Ми беремо на себе організаційну частину, комунікацію та супровід, щоб creator міг зосередитися на своїй роботі.\n\n<b>Тільки 18+ • Добровільно • Глобально</b>\n\nУчасть добровільна. Умови та формат співпраці обговорюються індивідуально після розгляду заявки.",        "about":"<b>VESTHETIC</b>\n\nVESTHETIC — Digital Talent Agency для повнолітніх онлайн-креаторів, які хочуть професійно працювати та розвиватися на міжнародному ринку.\n\nМи допомагаємо з організацією роботи, комунікацією, робочим процесом і супроводом. Конкретний формат залежить від платформ, завдань та індивідуальної домовленості з creator.\n\n<b>Модель співпраці:</b> 75% creator / 25% VESTHETIC.\n\nНаша мета — створити зрозумілий і професійний процес, у якому creator розуміє умови, формат роботи та наступні кроки.",        "terms":"<b>Умови співпраці</b>\n\n<b>Вік</b>\nПодати заявку можуть лише повнолітні — 18+.\n\n<b>Добровільність</b>\nУчасть добровільна. Ви самостійно вирішуєте, чи починати та продовжувати співпрацю.\n\n<b>Дохід</b>\nБазова модель розподілу доходу: 75% отримує creator, 25% — VESTHETIC. Конкретні умови можна обговорити до початку співпраці.\n\n<b>Формат роботи</b>\nРобота може виконуватися дистанційно. Графік і робочі умови узгоджуються індивідуально.\n\n<b>Конфіденційність</b>\nНе надсилайте документи, банківські дані, паролі чи іншу конфіденційну інформацію через Telegram. Якщо такі дані знадобляться на офіційному етапі оформлення, менеджер окремо пояснить безпечний спосіб їх передачі.",        "faq":"<b>FAQ</b>\n\n<b>Хто може подати заявку?</b>\nТільки повнолітні — 18+.\n\n<b>Чи потрібен досвід?</b>\nНі. Попередній досвід роботи на подібних платформах не обов’язковий.\n\n<b>Де можна працювати?</b>\nМожна працювати з дому або з іншого зручного для вас місця.\n\n<b>Яке обладнання потрібне?</b>\nДля початку достатньо телефона або ПК. Додаткове обладнання залежить від обраного формату роботи.\n\n<b>Який графік?</b>\nГрафік узгоджується індивідуально з урахуванням вашої доступності.\n\n<b>Як розподіляється дохід?</b>\n75% отримує creator, 25% — VESTHETIC.\n\n<b>Чи є навчання?</b>\nПісля розгляду заявки менеджер пояснить процес і наступні кроки.\n\n<b>Як подати заявку?</b>\nНатисніть «Подати заявку» в меню та заповніть коротку анкету.\n\n<b>Що відбувається після подання заявки?</b>\nМенеджер VESTHETIC розгляне заявку та зв’яжеться з вами.\n\n<b>Чи безпечні мої дані?</b>\nНе надсилайте документи або банківські дані через Telegram.\n\nЯкщо у вас залишилися питання — зв’яжіться з менеджером VESTHETIC.",        "apply":"<b>Заявка до VESTHETIC</b>\n\nЗаповнення анкети займе кілька хвилин. Нам потрібна базова інформація про вас, ваш досвід і доступність, щоб менеджер міг оцінити відповідний формат співпраці.\n\nПеред початком підтвердьте, що вам уже виповнилося 18 років і участь добровільна.",        "age":"Вам уже виповнилося 18 років?",
        "name":"<b>1/8 — Ім’я</b>\n\nЯк вас звати або який робочий псевдонім ви хотіли б використовувати?",        "country":"<b>2/8 — Країна</b>\n\nУ якій країні ви зараз перебуваєте? Вкажіть країну проживання або фактичного перебування.",        "languages":"<b>3/8 — Мови</b>\n\nЯкими мовами ви володієте та на якому рівні? Наприклад: російська — вільно, англійська — B2.",        "experience":"<b>4/8 — Досвід</b>\n\nЧи маєте досвід роботи на онлайн-платформах, створення контенту, стримінгу або іншої подібної роботи? Якщо ні — просто напишіть про це.",        "equipment":"<b>5/8 — Обладнання</b>\n\nЯке обладнання у вас є? Вкажіть телефон, ПК або ноутбук, камеру, мікрофон, освітлення та інше обладнання.",        "schedule":"<b>6/8 — Графік</b>\n\nСкільки часу ви реально готові приділяти роботі? Вкажіть приблизну кількість годин на день або тиждень та зручний для вас час.",        "contact":"<b>7/8 — Контакт</b>\n\nВкажіть Telegram-контакт, за яким менеджер зможе з вами зв’язатися. Можна надіслати @username.",        "source":"<b>8/8 — Джерело</b>\n\nДе ви вперше побачили VESTHETIC: Telegram, Instagram, TikTok, рекомендація, пошук або інше джерело?",        "thanks":"<b>Заявку надіслано ✅</b>\n\nДякуємо за інтерес до VESTHETIC. Менеджер розгляне вашу заявку та зв’яжеться з вами, якщо буде відповідний формат співпраці.\n\nБудь ласка, стежте за повідомленнями в Telegram.",        "no":"<b>VESTHETIC — 18+</b>\n\nМи розглядаємо лише заявки від повнолітніх. Якщо вам ще немає 18 років, наразі подати заявку неможливо.",        "manager":"<b>Менеджер VESTHETIC</b>\n\nЯкщо у вас є запитання перед поданням заявки або потрібна додаткова інформація, зв’яжіться з менеджером.\n\n@VESTHETIC_manager",        "language_prompt":"Оберіть мову:",
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

def notify_candidate_status(app_data, status):
    chat=app_data.get("telegram_chat_id")
    if not chat:
        return
    user=user_get(chat, app_data.get("telegram_username"))
    lang=user.get("lang") or "en"
    status_names={
        "ru":{"new":"⚪ Новая","progress":"🟡 В работе","contacted":"💬 Связались","interview":"🎙 Интервью","registration":"📝 Регистрация","active":"🟢 Активна","reject":"🔴 Отклонена"},
        "en":{"new":"⚪ New","progress":"🟡 In progress","contacted":"💬 Contacted","interview":"🎙 Interview","registration":"📝 Registration","active":"🟢 Active","reject":"🔴 Declined"},
        "sk":{"new":"⚪ Nová","progress":"🟡 V procese","contacted":"💬 Kontaktovaný","interview":"🎙 Pohovor","registration":"📝 Registrácia","active":"🟢 Aktívna","reject":"🔴 Zamietnutá"},
        "ua":{"new":"⚪ Нова","progress":"🟡 В роботі","contacted":"💬 Зв’язалися","interview":"🎙 Співбесіда","registration":"📝 Реєстрація","active":"🟢 Активна","reject":"🔴 Відхилена"}
    }
    names=status_names.get(lang,status_names["en"])
    label=names.get(status,status)
    messages={
        "ru":f"<b>Статус вашей заявки изменён</b>\n\nНовый статус: <b>{label}</b>",
        "en":f"<b>Your application status has changed</b>\n\nNew status: <b>{label}</b>",
        "sk":f"<b>Stav vašej žiadosti sa zmenil</b>\n\nNový stav: <b>{label}</b>",
        "ua":f"<b>Статус вашої заявки змінено</b>\n\nНовий статус: <b>{label}</b>"
    }
    send(chat,messages.get(lang,messages["en"]),kb_main(lang))

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
    before=app_get(i)
    r=sb("PATCH","applications",{"status":s,"status_changed_by_telegram_id":MANAGER_ID},{"id":f"eq.{i}","select":"*"})
    if r:
        after=r[0] if isinstance(r,list) and r else (app_get(i) or before)
        if before and before.get("status") != s:
            notify_candidate_status(after, s)
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
