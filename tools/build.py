"""Generate the static site into docs/.

python tools/build.py          preview: noindex everywhere, robots disallow (GitHub Pages copy)
python tools/build.py --prod   real domain: indexable, sitemap.xml
"""
import html
import json
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(HERE, "docs")
DATA = os.path.join(HERE, "data")
IMG = os.path.join(DOCS, "assets", "img")
PROD = "--prod" in sys.argv
SITE = "https://citybikensk.ru"
PHONE, PHONE_T = "+79137585571", "+7 913-758-55-71"
PHONE2, PHONE2_T = "+79134571708", "+7 913-457-17-08"
WA, TG, VK = "https://wa.me/79137585571", "https://t.me/mr_org54", "https://vk.com/citybikensk"
FLAMP = "https://novosibirsk.flamp.ru/firm/city_bike_veloservis-70000001022322607"
GIS = "https://2gis.ru/novosibirsk/firm/70000001022322607/tab/reviews"
ADDR = "Новосибирск, Вокзальная магистраль, 3"
HOURS = "Ежедневно с 11:00 до 20:00, кроме воскресенья"
e = html.escape


def load(n):
    with open(os.path.join(DATA, n), encoding="utf-8") as f:
        return json.load(f)


PRICES, PRODUCTS, CATALOG, DIAG = load("prices.json"), load("products.json"), load("catalog.json"), load("diag.json")
NAV = [("veloservice", "Велосервис"), ("electroservice", "Электросервис"), ("akb", "Сборка АКБ"), ("ecustom", "Электрификация"), ("catalog", "Витрина"), ("jobpaint", "Реставрация"), ("sovets", "Диагност"), ("oplata", "Как купить"), ("o_nas", "О нас"), ("contact", "Контакты")]


def img(b, name, alt, sizes="100vw", eager=False, w=800):
    """Responsive picture from <name>-800/-1600.webp; width and height prevent layout shift."""
    big = os.path.join(IMG, f"{name}-1600.webp")
    small = os.path.join(IMG, f"{name}-800.webp")
    src = big if not os.path.exists(small) else small
    with Image.open(src) as im:
        iw, ih = im.size
    srcset = f"{b}assets/img/{name}-800.webp {iw}w"
    if os.path.exists(big):
        with Image.open(big) as im:
            if im.size[0] > iw:
                srcset += f", {b}assets/img/{name}-1600.webp {im.size[0]}w"
    load_attr = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img src="{b}assets/img/{name}-800.webp" srcset="{srcset}" sizes="{sizes}" width="{iw}" height="{ih}" alt="{e(alt)}" {load_attr}>'


def faq_html(items):
    return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items) + "</div>"


def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


BUSINESS = {
    "@context": "https://schema.org", "@type": "BicycleStore", "name": "CITY BIKE", "url": SITE + "/", "telephone": PHONE, "foundingDate": "2012",
    "address": {"@type": "PostalAddress", "streetAddress": "Вокзальная магистраль, 3", "addressLocality": "Новосибирск", "addressCountry": "RU"},
    "openingHoursSpecification": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "11:00", "closes": "20:00"},
    "sameAs": [VK, FLAMP, GIS.rsplit("/tab", 1)[0]], "description": "Ремонт и обслуживание велосипедов, электровелосипедов и электромото, электрификация, сборка аккумуляторов, запчасти и реставрация в Новосибирске.",
}


def page(slug, title, descr, body, ld=None, extra_head=""):
    b = "../" if slug else ""
    ld_all = [BUSINESS] + (ld or [])
    robots = "" if PROD else '<meta name="robots" content="noindex,nofollow">'
    nav = "".join(f'<a href="{b}{s}/"{" aria-current=page" if s == slug else ""}>{t}</a>' for s, t in NAV)
    links = "".join(f'<a href="{b}{s}/">{t}</a>' for s, t in NAV[:6])
    url = f"{SITE}/{slug}" if slug else SITE + "/"
    doc = f"""<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(descr)}">{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="CITY BIKE"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(descr)}"><meta property="og:image" content="{SITE}/assets/img/neon-1600.webp"><meta property="og:locale" content="ru_RU">
<meta name="theme-color" content="#0a090d">
<link rel="icon" href="{b}favicon.png" type="image/png"><link rel="apple-touch-icon" href="{b}apple-touch-icon.png">
<link rel="preload" href="{b}assets/fonts/oswald-cyrillic-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{b}assets/site.css?v=3">{extra_head}
<script type="application/ld+json">{json.dumps(ld_all, ensure_ascii=False)}</script>
</head><body>
<header class="top"><div class="wrap top-in">
<a class="brand" href="{b or './'}" aria-label="CITY BIKE, на главную"><img src="{b}assets/img/astro-dark.png" width="180" height="162" alt=""><span><i>City</i> <b>Bike</b></span></a>
<nav class="nav" aria-label="Разделы">{nav}</nav>
<a class="top-tel" href="tel:{PHONE}">{PHONE_T}</a>
<button class="burger" type="button" aria-label="Меню" aria-expanded="false">Меню</button>
</div></header>
<main>{body}</main>
<footer class="foot"><div class="wrap foot-g">
<div><h3>CITY BIKE</h3><p>Вело- и электросервис, электрификация и сборка аккумуляторов. Новосибирск, с 2012 года.</p><p>{ADDR} (цоколь, въезд со двора).<br>{HOURS}.</p></div>
<div><h3>Разделы</h3>{links}</div>
<div><h3>Связь</h3><a href="tel:{PHONE}">{PHONE_T} (Евгений)</a><a href="tel:{PHONE2}">{PHONE2_T} (Максим)</a><a href="{WA}" rel="noopener">WhatsApp</a><a href="{TG}" rel="noopener">Telegram</a><a href="{VK}" rel="noopener">ВКонтакте</a><a href="{GIS}" rel="noopener">Отзывы в 2ГИС</a><a href="{FLAMP}" rel="noopener">Отзывы на Флампе</a></div>
</div><div class="wrap"><p style="margin-top:24px">ИП Пирожинский Е. С., ИНН 540702499534, ОГРНИП 317547600040776<br>ePN</p></div></footer>
<nav class="act" aria-label="Быстрая связь"><a href="tel:{PHONE}">Позвонить</a><a href="{WA}" rel="noopener">WhatsApp</a><a href="{TG}" rel="noopener">Telegram</a></nav>
<script src="{b}assets/site.js?v=3" defer></script>
</body></html>
"""
    d = os.path.join(DOCS, slug) if slug else DOCS
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    return slug


def hero(b, photo, alt, kick, h1, lead, buttons, small=True, aside=""):
    """kick is a quiet tag in the top corner (city, section), not a line above the headline."""
    cls = "hero page-hero" if small else "hero"
    side = f'<div class="hero-side">{aside}</div>' if aside else ""
    return f'<section class="{cls}">{img(b, photo, alt, "(max-width:760px) 200vw,100vw", eager=True)}<p class="geo">{kick}</p><div class="wrap{" with-side" if aside else ""}"><div><h1>{h1}</h1><p class="lead">{lead}</p><div class="btns">{buttons}</div></div>{side}</div></section>'


def burst(href, top, main, sub=""):
    """Comic 'BAM' star that links to the battery calculator."""
    return f'<a class="burst" href="{href}"><span><small>{top}</small><b>{main}</b>{f"<small>{sub}</small>" if sub else ""}</span></a>'


def contact_cta(b, title="Опишите проблему. Подскажем сразу"):
    return f"""<section class="sec"><div class="wrap"><div class="sec-head"><h2>{title}</h2><p class="lead">{ADDR}, цоколь, въезд со двора. {HOURS}.</p></div>
<div class="btns"><a class="btn" href="tel:{PHONE}">Позвонить мастеру</a><a class="btn alt" href="{WA}?text={e('Здравствуйте! Хочу записаться на сервис.')}" rel="noopener">Написать в WhatsApp</a><a class="btn ghost" href="{TG}" rel="noopener">Telegram</a></div></div></section>"""


# The workshop video from the old Tilda velo page (VK video of the CITY BIKE community).
VK_VIDEO = "https://vkvideo.ru/video_ext.php?oid=-163575429&id=456239296&hd=2"


def video_sec(kick, title):
    return f'<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><p class="kick">{kick}</p><h2>{title}</h2></div><div class="video"><iframe src="{VK_VIDEO}" title="Видео из мастерской CITY BIKE" loading="lazy" allow="autoplay; encrypted-media; fullscreen; picture-in-picture; screen-wake-lock" allowfullscreen></iframe></div><p class="mut" style="margin-top:10px">Больше видео в <a href="{VK}" rel="noopener">группе ВКонтакте</a>.</p></div></section>'


def price_list(groups):
    out = ['<div class="price-tools"><input id="price-q" type="search" placeholder="Найти работу: цепь, спицы, прокачка..." aria-label="Поиск по прайсу"></div>']
    for g in groups:
        rows = "".join(f"<div><dt>{e(n)}</dt><dd>{e(p + ' ₽' if re.search(r'[0-9]$', p) and not p.startswith('+') else p)}</dd></div>" for n, p in g["rows"])
        out.append(f'<details class="pl"><summary>{e(g["title"])}</summary><dl class="pl-rows">{rows}</dl></details>')
    out.append('<p id="price-empty" class="empty">Такой работы в прайсе нет. Позвоните мастеру, подскажем.</p>')
    return "".join(out)


# ---------- catalog ----------
ALIASES = CATALOG["aliases"]
FIX = {"Вилки-Амортизаторы": "Вилки и амортизаторы", "Кассеты, трещётки": "Кассеты и трещотки", "Колеса в сборе": "Колёса в сборе", "Седла и штыри": "Сёдла и штыри", "Системы и звезды": "Системы и звёзды"}
GROUP_OF = {s: g["slug"] for g in CATALOG["groups"] for s in g["subs"]}


def sub_of(p):
    for c in p["cats"]:
        c = FIX.get(c, ALIASES.get(c, c))
        if c in GROUP_OF:
            return c
    return None


BY_SUB = {}
for p in PRODUCTS:
    BY_SUB.setdefault(sub_of(p), []).append(p)
assert None not in BY_SUB, [p["title"] for p in BY_SUB.get(None, [])]


def stock(p):
    q = str(p["qty"])
    return f"В наличии: {q} шт." if q.isdigit() and int(q) > 0 else "Наличие уточняйте"


def price_fmt(n):
    return f"{n:,}".replace(",", " ") + " ₽"


def card(b, p):
    imgs = ",".join(f"{b}assets/img/{n}-800.webp" for n in p["imgs"])
    first = p["imgs"][0] if p["imgs"] else None
    old = f"<s>{price_fmt(p['old'])}</s>" if p["old"] else ""
    pic = f'<img src="{b}assets/img/{first}-800.webp" width="800" height="800" alt="{e(p["title"])}" loading="lazy" decoding="async">' if first else ""
    st = stock(p)
    return f"""<article class="card" data-q="{e(p['title'] + ' ' + p['text'])}" data-title="{e(p['title'])}" data-text="{e(p['text'])}" data-price="{p['price']}" data-stock="{e(st)}" data-imgs="{imgs}">
<button class="card-img" type="button" data-open aria-label="Подробнее: {e(p['title'])}">{pic}</button>
<div class="card-b"><h3>{e(p['title'])}</h3><span class="badge{'' if st.startswith('В') else ' ask'}">{st}</span><div class="pr">{price_fmt(p['price'])}{old}</div>
<div class="card-a"><button class="btn sm ghost" type="button" data-pick="{p['id']}" data-title="{e(p['title'])}" data-price="{p['price']}" aria-pressed="false">+ В подборку</button>
<a class="btn sm" href="{WA}?text={e('Здравствуйте! Интересует: ' + p['title'] + '. Есть в наличии?')}" rel="noopener">Спросить</a></div></div></article>"""


def example(sub):
    return f"""<article class="card ex" data-q="{e(sub)}"><div class="card-img">{e(sub)}</div><div class="card-b"><span class="tag">ПРИМЕР</span><h3>Пример товара: {e(sub)}</h3><p>Образец карточки для самостоятельного заполнения: фото, название, цена и наличие.</p><div class="pr">Цена</div></div></article>"""


DIALOGS = f"""<dialog id="product" aria-label="Товар"><button class="dlg-x" type="button" aria-label="Закрыть">×</button><div class="dlg-gal"></div><div class="dlg-b"><h2></h2><p class="disp hl dlg-price" style="font-size:28px;margin:0"></p><p class="badge dlg-stock"></p><p class="dlg-text"></p><div class="btns"><a class="btn dlg-wa" rel="noopener">Спросить в WhatsApp</a><a class="btn alt dlg-tg" rel="noopener">Спросить в Telegram</a><a class="btn ghost" href="tel:{PHONE}">Позвонить</a></div></div></dialog>
<dialog id="picks" aria-label="Подборка"><button class="dlg-x" type="button" aria-label="Закрыть">×</button><div class="dlg-b"><h2>Ваша подборка</h2><p class="mut">Это не заказ и не оплата. Отправьте список мастеру: он проверит наличие и забронирует.</p><div id="pick-list"></div><p id="pick-sum" class="disp hl" style="font-size:24px;margin:16px 0"></p><div class="btns"><a id="pick-wa" class="btn" rel="noopener">Отправить в WhatsApp</a><a id="pick-tg" class="btn alt" rel="noopener">Отправить в Telegram</a><button id="pick-clear" class="btn ghost" type="button">Очистить</button></div></div></dialog>
<button class="btn pick-bar" type="button">Подборка</button>"""

STEPS = f"""<ol class="steps"><li><b>Выберите</b>Смотрите ассортимент, цены и наличие. Добавляйте всё нужное в подборку.</li><li><b>Отправьте мастеру</b>Подборка уходит одним сообщением в WhatsApp или Telegram. Подскажем совместимость и забронируем.</li><li><b>Заберите</b>В мастерской на Вокзальной магистрали, 3 или доставкой: СДЭК, Энергия, Почта России.</li></ol>"""


def group_cards(b, g):
    if len(g["subs"]) > 1:
        # Many small subsections read better as one grid: each example tile already names its subsection.
        cards = "".join("".join(card(b, p) for p in BY_SUB.get(s, [])) or example(s) for s in g["subs"])
        return f'<section class="cat-block"><div class="grid">{cards}</div></section>'
    out = []
    for sub in g["subs"]:
        items = BY_SUB.get(sub, [])
        cards = "".join(card(b, p) for p in items) or example(sub)
        head = f'<h2 class="cat-sub" id="s-{e(re.sub(r"[^а-яёa-z0-9]+", "-", sub.lower()))}" style="font-size:clamp(24px,3.4vw,38px)">{e(sub)}</h2>' if len(g["subs"]) > 1 else ""
        out.append(f'<section class="cat-block">{head}<div class="grid">{cards}</div></section>')
    return "".join(out)


def chips(b, current):
    items = [("catalog", "Вся витрина")] + [(g["slug"], g["title"]) for g in CATALOG["groups"]]
    return '<nav class="chips" aria-label="Разделы витрины">' + "".join(f'<a class="chip" href="{b}{s}/"{" aria-current=page" if s == current else ""}>{e(t)}</a>' for s, t in items) + "</nav>"


SEARCH = '<input id="cat-q" type="search" placeholder="Поиск: контроллер, 48V, фара..." aria-label="Поиск по витрине"><p id="cat-empty" class="empty">Здесь не нашлось, но это не весь ассортимент. Спросите мастера: многое есть в мастерской и под заказ.</p>'
NOT_ALL = f'<p class="note">На сайте показана часть ассортимента, полный список ведётся в мастерской. Не нашли нужное? <a href="{WA}" rel="noopener">Спросите в WhatsApp</a>.</p>'

# ---------- FAQ ----------
FAQ_GENERAL = [
    ("Сколько стоит обслуживание велосипеда в Новосибирске?", "В CITY BIKE три пакета ТО: Express за 3 500 ₽, сезонное за 5 000 ₽ и комплексное за 7 300 ₽. Предварительная цена определяется после диагностики и зависит от сложности работ."),
    ("Сколько времени занимает ремонт?", "Обычно от 1 до 3 дней. Срочные работы без очереди стоят на 30% дороже."),
    ("Диагностика платная?", "На сайте заявлена бесплатная диагностика. Сложная диагностика неисправности электросистемы в прайсе указана от 500 ₽."),
    ("Можно ли сделать электровелосипед из моего велосипеда?", "Да. Установим наш или ваш комплект под ключ: сборка колеса, установка, подключение и настройка контроллера. Цена от 8 000 ₽ без стоимости комплекта. Конфигурацию можно прикинуть в калькуляторе."),
    ("Вы ремонтируете электросамокаты и аккумуляторы?", "Да. Ремонтируем электровелосипеды, электромото и электросамокаты: моторы, контроллеры, проводку и Li-ion АКБ, включая замер ёмкости, балансировку и замену BMS."),
    ("Можно собрать аккумулятор под мой байк?", "Да. Собираем Li-ion аккумуляторы под ваш транспорт, габариты и нужные характеристики, из наших или ваших элементов. Работа от 10 000 ₽, конфигурацию можно прикинуть в калькуляторе."),
    ("Можно купить товар на сайте?", "Онлайн-оплаты на сайте нет. Соберите подборку и отправьте её мастеру в WhatsApp или Telegram: он уточнит наличие и забронирует товар."),
    ("Как можно оплатить?", "Наличными, картой, переводом или через СБП, по счёту с ИП или ООО. Есть рассрочка и кредит."),
    ("Вы отправляете заказы в другие города?", "Да, в день заказа после полной предоплаты: СДЭК, Энергия или Почта России. Сумму и сроки доставки сообщит менеджер."),
    ("Где вы находитесь и как работаете?", f"{ADDR}, цоколь, въезд со двора, есть удобная парковка. {HOURS}. Перед приездом лучше позвонить: {PHONE_T}."),
]
FAQ_VELO = [
    ("Что входит в комплексное ТО велосипеда?", "Ревизия каретки, рулевого стакана и втулок, чистка трансмиссии и переключателей, чистка и смазка линий переключения и тормозов, протяжка спиц, регулировка скоростей и тормозов, шиномонтаж с балансировкой и протяжка навесных элементов. Цена 7 300 ₽."),
    ("Сколько стоит заменить камеру или заклеить прокол?", "Заклейка одного прокола 350 ₽, шиномонтаж с заменой камеры 350 ₽."),
    ("Сколько стоит убрать восьмёрку на колесе?", "Правка биения: слабая и средняя 500 ₽, сильная 800 ₽. Протяжка спиц одного колеса 550 ₽."),
    ("Сколько стоит прокачка гидравлических тормозов?", "На одну сторону: 750 ₽ для минерального масла и 600 ₽ для DOT."),
    ("Вы собираете велосипед из коробки?", "Да. Сборка и настройка обычного велосипеда из коробки 2 500 ₽, электровелосипеда 5 500 ₽."),
    ("Сколько стоит перебрать вилку?", "Эластомерная вилка 1 100 ₽, пружинно-масляная от 2 200 ₽, воздушно-масляная от 6 000 ₽."),
]
FAQ_ELECTRO = [
    ("Сколько стоит обслуживание мотор-колеса?", "Сезонное обслуживание от 4 500 ₽: полный разбор, чистка, замена смазки, обслуживание подшипников и герметизация мотора."),
    ("Мотор утонул или заклинил. Можно восстановить?", "Да. Капитальный ремонт ржавого, утонувшего или заклинившего мотора от 4 500 ₽. Точную цену скажем после разбора."),
    ("Можно починить аккумулятор электровелосипеда?", "Да: замер ёмкости от 1 000 ₽ за 10 Ач, балансировка от 1 000 ₽, замена неисправной ячейки от 2 000 ₽, замена BMS от 2 500 ₽."),
    ("Можно собрать аккумулятор на заказ?", "Да. Собираем Li-ion АКБ под ваш транспорт, габариты и характеристики, из наших или ваших элементов. Работа от 10 000 ₽."),
    ("Что значит ошибка на дисплее электровелосипеда?", "Частые коды E-06 — E-10 расшифрованы в нашем онлайн-диагносте. Там же описаны типичные симптомы и как их проверить."),
]
FAQ_CUSTOM = [
    ("Что такое электрификация велосипеда?", "Это установка мотора и аккумулятора на ваш привычный велосипед. Быстрый и выгодный способ превратить его в ежедневный транспорт."),
    ("Сколько стоит электрифицировать велосипед?", "Установка комплекта под ключ от 8 000 ₽, комплекты на витрине. Посчитать полную конфигурацию можно в калькуляторе."),
    ("Можно поставить мой комплект?", "Да, устанавливаем как наш, так и ваш комплект."),
    ("Как подобрать комплект?", "Инженеры подберут комплект под ваш велосипед и задачи или соберут его индивидуально. Звоните Евгению или Максиму."),
]

# ---------- pages ----------
b = "../"
built = []

svc_tiles = [
    ("veloservice", "master", "Ремонт велосипедов", "Комплексное ТО, обслуживание"),
    ("electroservice", "el-board", "Ремонт электро", "Электровелосипеды, мото, самокаты: моторы, контроллеры, проводка"),
    ("akb", "akb-build", "Сборка аккумуляторов", "Li-ion АКБ под ваш байк и ваши характеристики"),
    ("ecustom", "eb-red-tan", "Электрификация", "Установка электроники на ваш велосипед"),
    ("catalog", "ebike-graffiti", "Витрина", "Электровелосипеды, комплекты, запчасти"),
    ("jobpaint", "frame-blue", "Реставрация", "Покраска, сборка на заказ, кастом"),
]


def tiles(pfx):
    return '<div class="tiles">' + "".join(f'<a class="tile" href="{pfx}{s}/">{img(pfx, ph, t, "(min-width:960px) 33vw,(min-width:600px) 50vw,100vw")}<div><h3>{t}</h3><p>{d}</p></div></a>' for s, ph, t, d in svc_tiles) + "</div>"


TAPE = '<div class="tape" aria-hidden="true"><div>' + "".join(f"<span>{t}</span>" for t in ["Велосервис", "Электросервис", "Сборка аккумуляторов", "Бесплатная диагностика", "Сроки 1–3 дня", "Гарантия на работу", "Электрификация", "Консультация мастера", "Реставрация", "Сборка на заказ", "С 2012 года"] * 3) + "</div></div>"

home = hero("", "bench", "Мастер за верстаком мастерской CITY BIKE", "Новосибирск · с 2012", "Вело&shy;сервис <span class=hl>и</span> электро&shy;сервис", "Мастерская полного цикла: от точной диагностики до кастомной сборки. Велосипеды, электробайки, электромото, самокаты и аккумуляторы.", f'<a class="btn" href="tel:{PHONE}">Записаться на сервис</a><a class="btn alt" href="ecustom/">Электрифицировать велосипед</a><a class="btn ghost" href="akb/">Собрать аккумулятор</a>', small=False, aside=burst("calc/", "Собери свой", "аккумулятор!", "калькулятор →"))
home += TAPE
home += f"""<section class="sec"><div class="wrap"><div class="facts"><div class="fact"><b>0 ₽</b>Бесплатная диагностика</div><div class="fact"><b>1–3 дня</b>Регламентированные сроки ремонта</div><div class="fact"><b>от 3 500 ₽</b>Пакеты ТО</div><div class="fact"><b>Li-ion</b>Собираем аккумуляторы под заказ</div></div></div></section>
<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><p class="kick">Что делаем</p><h2>Всё, что крутится</h2></div>{tiles('')}</div></section>
<section class="sec-alt"><div class="wrap split"><div>{img('', 'el-board', 'Мастер CITY BIKE проверяет плату под лупой', '(min-width:960px) 50vw,100vw')}</div><div><p class="kick">Сломалось</p><h2>Что случилось с байком?</h2><p class="lead" style="margin-top:12px">Хрустит мотор, дисплей показывает ошибку, байк гаснет в горку. Онлайн-диагност расскажет, что это и как проверить самому.</p><div class="btns"><a class="btn" href="sovets/">Открыть диагност</a><a class="btn ghost" href="calc/">Калькулятор комплекта</a></div></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><p class="kick">Сервис</p><h2>Пакеты ТО</h2></div>{'<div class="pack">' + ''.join(f'<article><h3>{n}</h3><div class="price">{p}</div><p class="mut" style="margin:0">{d}</p></article>' for n, p, d in [('Express ТО', '3 500 ₽', 'Чистка цепи, протяжка спиц, регулировка скоростей и тормозов, шиномонтаж.'), ('Сезонное ТО', '5 000 ₽', 'То же плюс ревизия кареточного узла и чистка всей трансмиссии.'), ('Комплексное ТО', '7 300 ₽', 'Полная ревизия: каретка, рулевой стакан, втулки, все линии и навесные элементы.')]) + '</div>'}<div class="btns" style="margin-top:20px"><a class="btn" href="veloservice/">Полный прайс</a></div></div></section>
<section class="sec-alt"><div class="wrap split rev"><div>{img('', 'evgeny', 'Мастерская CITY BIKE', '(min-width:960px) 50vw,100vw')}</div><div><p class="kick">Мастерская</p><h2>Делают райдеры для райдеров</h2><p class="lead" style="margin-top:12px">Мы сами катаемся: стрит, фристайл, электробайки каждый день. Поэтому знаем, что байк переживает на самом деле и как он должен работать. В команде механики, инженеры, электронщики, маляры и токари.</p><a class="gis" href="{GIS}" rel="noopener" style="margin-top:22px;width:fit-content"><b>5,0</b><span>★★★★★</span><small>143 оценки · отзывы в 2ГИС →</small></a><div class="btns"><a class="btn ghost" href="o_nas/">О мастерской</a></div></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><p class="kick">Витрина</p><h2>Заходите как в мастерскую</h2><p class="lead" style="margin-top:12px">Без корзины и онлайн-оплаты. Смотрите, что есть, собирайте подборку и отправляйте мастеру одним сообщением.</p></div>{STEPS}<div class="btns" style="margin-top:20px"><a class="btn" href="catalog/">Смотреть витрину</a></div></div></section>
<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><p class="kick">Вопросы</p><h2>Спрашивают чаще всего</h2></div>{faq_html(FAQ_GENERAL)}</div></section>"""
home += contact_cta("")
built.append(page("", "Ремонт велосипедов и электровелосипедов в Новосибирске — CITY BIKE", "Велосервис CITY BIKE в Новосибирске с 2012 года: ремонт и ТО велосипедов от 3 500 ₽, электровелосипеды, электрификация, запчасти, реставрация. Вокзальная магистраль, 3.", home, [faq_ld(FAQ_GENERAL)]))

velo_packs = [
    ("Express ТО", "3 500 ₽", ["Чистка цепи", "Протяжка спиц (переднее, заднее колесо)", "Регулировка скоростей", "Регулировка тормозов", "Шиномонтаж, балансировка"]),
    ("Сезонное ТО", "5 000 ₽", ["Ревизия кареточного узла", "Чистка трансмиссии (цепь, кассета, система)", "Протяжка спиц (переднее, заднее колесо)", "Регулировка скоростей", "Регулировка тормозов", "Шиномонтаж, балансировка"]),
    ("Комплексное ТО", "7 300 ₽", ["Ревизия кареточного узла", "Ревизия рулевого стакана", "Ревизия втулок (передняя, задняя)", "Чистка трансмиссии (цепь, кассета, система)", "Чистка переключателей скоростей", "Чистка, смазка линий переключения скоростей", "Чистка, смазка тормозных линий", "Протяжка спиц (переднее, заднее колесо)", "Регулировка скоростей", "Регулировка тормозов", "Шиномонтаж, балансировка", "Протяжка всех навесных элементов"]),
]
NOTE = '<p class="note">Предварительная цена определяется после диагностики и зависит от сложности работ.</p>'
velo = hero(b, "master", "Мастер за работой в велосервисе CITY BIKE", "Велосервис · Новосибирск", "Ремонт велосипедов", "Приемлемые цены, гарантия качества ремонта и большой выбор запчастей. Бесплатно проконсультируем по обслуживанию вашего байка.", f'<a class="btn" href="tel:{PHONE}">Записаться на сервис</a><a class="btn ghost" href="#prices">Смотреть прайс</a>')
velo += TAPE + f"""<section class="sec"><div class="wrap"><div class="sec-head"><h2>Пакеты ТО</h2></div><div class="pack">{''.join(f'<article><h3>{n}</h3><div class="price">{p}</div><ol>{"".join(f"<li>{x}</li>" for x in items)}</ol></article>' for n, p, items in velo_packs)}</div></div></section>
{video_sec("Как мы работаем", "Заглянуть в мастерскую")}
<section class="sec" id="prices" style="padding-top:0"><div class="wrap"><div class="sec-head"><h2>Прайс на работы</h2></div>{NOTE}{price_list(PRICES['veloservice'])}</div></section>
<section class="sec-alt"><div class="wrap"><div class="gal">{img(b, 'hub', 'Разобранная втулка на верстаке', '(min-width:960px) 25vw,50vw')}{img(b, 'spokes', 'Мастер настраивает задний переключатель', '(min-width:960px) 25vw,50vw')}{img(b, 'truing', 'Мастер правит колесо на станке', '(min-width:960px) 25vw,50vw')}{img(b, 'rim', 'Правка обода велосипедного колеса', '(min-width:960px) 25vw,50vw')}{img(b, 'groupset', 'Навесное оборудование велосипеда', '(min-width:960px) 25vw,50vw')}{img(b, 'flatlay', 'Детали велосипеда разложены для ревизии', '(min-width:960px) 25vw,50vw')}</div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><h2>Вопросы о ремонте</h2></div>{faq_html(FAQ_VELO)}</div></section>""" + contact_cta(b)
built.append(page("veloservice", "Ремонт велосипедов в Новосибирске: цены на ТО и работы — CITY BIKE", "Ремонт и обслуживание велосипедов в Новосибирске: ТО от 3 500 ₽, правка колёс, прокачка тормозов, переборка вилок. Полный прайс, сроки от 1 до 3 дней.", velo, [faq_ld(FAQ_VELO)]))

el_packs = [
    ("Электрификация", "от 8 000 ₽", "Установка нашего или вашего комплекта под ключ: сборка колеса, установка элементов, подключение, настройка контроллера."),
    ("Обслуживание мотор-колеса", "от 4 500 ₽", "Сезонное обслуживание: полный разбор, чистка, замена смазки, подшипники, герметизация."),
    ("Сборка велосипеда под заказ", "от 8 000 ₽", "Соберём под ваши параметры: подберём и найдём комплектующие, выполним конечную сборку."),
    ("Сборка аккумулятора", "от 10 000 ₽", "Индивидуальная сборка АКБ под ваш велосипед, мото или самокат и нужные характеристики. Из наших или ваших элементов."),
]


def gal(pfx, items):
    return '<div class="gal">' + "".join(img(pfx, n, a, "(min-width:960px) 25vw,50vw") for n, a in items) + "</div>"


EL_WORK = [("el-board", "Проверка платы под лупой"), ("motor-stator", "Статор мотор-колеса на ревизии"), ("akb-bms", "Подключение BMS к сборке аккумулятора"), ("motor-gears", "Замена шестерён редуктора"),
           ("el-hall", "Замена датчиков Холла"), ("motor-open", "Вскрытый мотор перед чисткой"), ("motor-press", "Распрессовка мотора"), ("gears", "Новые шестерни для мотор-колёс"),
           ("motor-hand", "Обмотка статора, проверка"), ("motor-parts", "Разобранный мотор: подшипники и шестерни"), ("akb-wires", "Проводка балансировки аккумулятора"), ("motor-shaft", "Ось и статор мотора")]
EL_MOTO = [("emoto-black", "Электромотоцикл после обслуживания"), ("emoto-stealth", "Электромото в мастерской"), ("emoto-white", "Электрический эндуро у мастерской"), ("eb-moto-style", "Электробайк в мото-стиле")]

el = hero(b, "motor-open2", "Разобранное мотор-колесо в CITY BIKE", "Электросервис · Новосибирск", "Ремонт электро&shy;велосипедов и мото", "Электровелосипеды, электромото, самокаты и моноколёса. Диагностика электроники, датчики Холла и фазные провода, контроллеры, проводка, аккумуляторы. Устранение поломки от 1 до 3 дней.", f'<a class="btn" href="tel:{PHONE}">Позвонить мастеру</a><a class="btn alt" href="../sovets/">Онлайн-диагност</a>', aside=burst("../calc/", "Собери свой", "аккумулятор!", "калькулятор →"))
el += TAPE + f"""<section class="sec"><div class="wrap"><div class="sec-head"><h2>Топ услуг</h2></div><div class="pack top4">{''.join(f'<article><h3>{n}</h3><div class="price">{p}</div><p class="mut" style="margin:0">{d}</p></article>' for n, p, d in el_packs)}</div></div></section>
<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><h2>Прайс на работы</h2></div>{NOTE}{price_list(PRICES['electroservice'])}</div></section>
<section class="sec-alt"><div class="wrap"><div class="sec-head"><p class="kick">Из мастерской</p><h2>Наши работы</h2></div>{gal(b, EL_WORK)}</div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><p class="kick">Не только велосипеды</p><h2>Электромото тоже к нам</h2><p class="lead" style="margin-top:12px">Обслуживаем и ремонтируем электромотоциклы и тяжёлые электробайки: мотор, контроллер, проводка, аккумулятор.</p></div>{gal(b, EL_MOTO)}</div></section>
<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><h2>Вопросы об электросервисе</h2></div>{faq_html(FAQ_ELECTRO)}</div></section>""" + contact_cta(b)
built.append(page("electroservice", "Ремонт электровелосипедов, электромото и самокатов в Новосибирске — CITY BIKE", "Ремонт электровелосипедов, электромотоциклов и электросамокатов в Новосибирске: моторы от 4 500 ₽, контроллеры, проводка, Li-ion АКБ, сборка аккумуляторов от 10 000 ₽. Полный прайс.", el, [faq_ld(FAQ_ELECTRO)]))

FAQ_AKB = [
    ("Сколько стоит собрать аккумулятор?", "Работа по сборке от 10 000 ₽. Итоговая цена зависит от напряжения, ёмкости, ячеек и BMS: прикиньте конфигурацию в калькуляторе или позвоните мастеру."),
    ("Можно собрать из моих элементов?", "Да, соберём из ваших или из наших. Ваши ячейки сначала проверим: ёмкость, внутреннее сопротивление, подбор в параллели."),
    ("Под какой транспорт собираете?", "Электровелосипеды, электромото, самокаты, моноколёса и другие проекты. Подгоняем под габариты рамы или штатного корпуса."),
    ("Что с гарантией?", "На сборку даём гарантию. Сроки и условия мастер скажет, когда согласуете конфигурацию."),
]
akb_steps = [("Задача", "Транспорт, напряжение, нужный запас хода и габариты места под батарею."), ("Конфигурация", "Подбираем ячейки, схему и BMS. Можно прикинуть в калькуляторе."), ("Сборка", "Контактная сварка, балансировка, проверка на стенде."), ("Выдача", "Отдаём с замером ёмкости и рекомендациями по зарядке.")]
akb = hero(b, "akb-boxes2", "Новые Li-ion ячейки для сборки аккумуляторов", "Сборка АКБ · Новосибирск", "Сборка аккумуляторов на заказ", "Индивидуальная сборка Li-ion АКБ под ваш велосипед, мото или самокат, ваши габариты и характеристики. Из наших или ваших элементов, на своём сварочном и тестовом оборудовании.", f'<a class="btn" href="../calc/">Рассчитать в калькуляторе</a><a class="btn alt" href="{WA}?text={e("Здравствуйте! Хочу собрать аккумулятор.")}" rel="noopener">Обсудить с мастером</a>', aside=burst("../calc/", "от", "10 000 ₽", "работа"))
akb += TAPE + f"""<section class="sec"><div class="wrap"><div class="sec-head"><p class="kick">Новое направление</p><h2>Как собираем</h2></div><ol class="steps four">{''.join(f'<li><b>{t}</b>{d}</li>' for t, d in akb_steps)}</ol></div></section>
<section class="sec-alt"><div class="wrap"><div class="sec-head"><h2>Из мастерской</h2></div>{gal(b, [("akb-build", "Сборка аккумулятора на столе мастера"), ("akb-tall", "Высокая сборка из 21700 ячеек"), ("akb-pack", "Аккумулятор в сборке перед упаковкой"), ("akb-bms", "BMS на собранном аккумуляторе"), ("akb-pink", "Секции аккумулятора"), ("akb-cells", "Ячейки после контактной сварки"), ("akb-build2", "Сборка с балансировочными проводами"), ("akb-cells-blue", "Li-ion ячейки"), ("akb-boxes", "Партия новых ячеек")])}</div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><h2>Прайс на работы с АКБ</h2></div>{NOTE}{price_list([g for g in PRICES['electroservice'] if 'аккумул' in g['title'].lower()])}</div></section>
<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><h2>Вопросы о сборке</h2></div>{faq_html(FAQ_AKB)}</div></section>""" + contact_cta(b, "Расскажите, что собираем")
built.append(page("akb", "Сборка аккумулятора для электровелосипеда на заказ в Новосибирске — CITY BIKE", "Соберём Li-ion аккумулятор под ваш электровелосипед, электромото или самокат: ваши габариты и характеристики, наши или ваши элементы. Работа от 10 000 ₽.", akb, [faq_ld(FAQ_AKB)]))

cust = hero(b, "eb-orange-fat", "Электрофэтбайк, собранный в CITY BIKE", "Электрификация · Новосибирск", "Электрификация велосипедов под ключ", "Быстро, с гарантией и только качественное, проверенное оборудование. Новый уровень вашего велосипеда.", '<a class="btn" href="../calc/">Посчитать конфигурацию</a><a class="btn alt" href="../mkcomplects/">Комплекты</a>')
cust += TAPE + f"""<section class="sec"><div class="wrap split"><div><p class="kick">Что это</p><h2>Ваш байк, но с мотором</h2><p class="lead" style="margin-top:12px">Электрификация — это установка надёжного мотора и аккумулятора на ваш привычный байк. Самый быстрый и выгодный способ превратить обычный велосипед в ежедневного помощника.</p></div>{img(b, 'ebike-teal', 'Электрифицированный велосипед CITY BIKE', '(min-width:960px) 50vw,100vw')}</div></section>
<section class="sec" style="padding-top:0"><div class="wrap"><div class="pack" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))"><article><h3>Свобода от усталости</h3><p class="mut" style="margin:8px 0 0">В гору и против ветра больше не нужно тяжело крутить. Вы едете быстрее и дальше.</p></article><article><h3>Город без границ</h3><p class="mut" style="margin:8px 0 0">Забудьте о пробках, душных автобусах и поиске парковки.</p></article><article><h3>Экономия</h3><p class="mut" style="margin:8px 0 0">Обслуживание в десятки раз дешевле содержания авто, а полный заряд стоит копейки.</p></article><article><h3>Дальние маршруты</h3><p class="mut" style="margin:8px 0 0">Длинные и сложные дороги становятся любимыми маршрутами для прогулок.</p></article></div></div></section>
<section class="sec-alt"><div class="wrap"><div class="sec-head"><h2>Что собираем</h2></div>{gal(b, [("eb-red-tan", "Красный электровелосипед на светлых покрышках"), ("eb-black-fat", "Чёрный электрофэтбайк"), ("eb-orange-fat", "Электрофэтбайк с оранжевыми ободами"), ("eb-teal-fat", "Бирюзовый электрофэтбайк с кофром"), ("eb-red-fat", "Красный электрофэтбайк"), ("etrike", "Электротрицикл с корзиной"), ("eb-fat-gold", "Электрофэтбайк с золотой вилкой"), ("eb-black-mtb", "Электрифицированный горный велосипед"), ("eb-red-close", "Аккумулятор на раме, крупный план"), ("eb-fat-black", "Электрофэтбайк в стиле мото"), ("eb-black-mtb2", "Горный электровелосипед зимой"), ("eb-red-tan2", "Красный электровелосипед, вид сбоку")])}<div class="btns" style="margin-top:12px"><a class="btn" href="../calc/">Калькулятор</a><a class="btn ghost" href="../ebikes/">Готовые электровелосипеды</a></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><h2>Вопросы об электрификации</h2></div>{faq_html(FAQ_CUSTOM)}</div></section>""" + contact_cta(b, "Расскажите про свой байк")
built.append(page("ecustom", "Электрификация велосипеда в Новосибирске под ключ — CITY BIKE", "Переделаем ваш велосипед в электровелосипед: комплект, установка и настройка под ключ от 8 000 ₽. Калькулятор конфигурации, гарантия, Новосибирск.", cust, [faq_ld(FAQ_CUSTOM)]))

paint_gal = "".join(img(b, n, a, "(min-width:960px) 25vw,50vw") for n, a in [("orange", "Оранжевый велосипед после реставрации"), ("neon", "Неоновая рама с индивидуальной покраской"), ("orange-basket", "Деталь оранжевого велосипеда с корзиной"), ("frame-blue", "Покрашенная рама и вилка"), ("orange-v", "Оранжевая рама, крупный план"), ("blue-girl", "Голубой велосипед после реставрации"), ("retro-red", "Отреставрированный красный ретро-велосипед"), ("orange-brake", "Тормоз оранжевого велосипеда"), ("retro-blue", "Голубой ретро-велосипед"), ("orange-drop", "Перо рамы и спицы, крупный план"), ("retro-fold", "Отреставрированный складной велосипед"), ("teal-saddle", "Седло и бирюзовая рама"), ("orange-lever", "Покраска рамы, крупный план"), ("retro-pink", "Велосипед с индивидуальной покраской")])
paint = hero(b, "frame-blue", "Рама после покраски в CITY BIKE", "Реставрация · Новосибирск", "Покраска и реставрация велосипедов", "Все проекты и стоимость обсуждаются индивидуально. Цена и сроки зависят от сложности работы.", f'<a class="btn" href="{WA}?text={e("Здравствуйте! Хочу обсудить реставрацию велосипеда.")}" rel="noopener">Обсудить проект</a><a class="btn ghost" href="tel:{PHONE}">Позвонить</a>')
paint += TAPE + f"""<section class="sec"><div class="wrap"><div class="pack" style="grid-template-columns:repeat(auto-fit,minmax(260px,1fr))"><article><h3>Индивидуальная покраска</h3><ul style="margin-top:10px"><li>Подготовка велосипеда к покраске</li><li>Разработка дизайна и согласование</li></ul></article><article><h3>Реставрационные работы</h3><ul style="margin-top:10px"><li>Поиск необходимых запчастей</li><li>Ремонтные и сварочные работы</li></ul></article></div></div></section>
<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><h2>Наши работы</h2><p class="lead" style="margin-top:10px">Мы всегда готовы решить даже самые сложные задачи.</p></div><div class="gal">{paint_gal}</div></div></section>""" + contact_cta(b, "Запишите байк на реставрацию")
built.append(page("jobpaint", "Реставрация и покраска велосипедов в Новосибирске — CITY BIKE", "Покраска рам и реставрация велосипедов в Новосибирске: разработка дизайна, поиск запчастей, сварочные работы. Примеры работ CITY BIKE.", paint))

# catalog
head = f'<section class="sec" style="padding-bottom:0"><div class="wrap"><p class="kick">Витрина CITY BIKE</p>'
all_cards = head + f'<h1 style="font-size:clamp(38px,7vw,84px)">Витрина</h1><p class="lead" style="margin:12px 0 18px">Без корзины и онлайн-оплаты: смотрите ассортимент, собирайте подборку и отправляйте её мастеру одним сообщением.</p>{chips(b, "catalog")}{SEARCH}</div></section><section class="sec" style="padding-top:28px"><div class="wrap">{STEPS}{NOT_ALL}'
for g in CATALOG["groups"]:
    all_cards += f'<section class="cat-block"><h2 style="margin:40px 0 14px"><a href="{b}{g["slug"]}/" style="text-decoration:none">{e(g["title"])}</a></h2>{group_cards(b, g)}</section>'
all_cards += "</div></section>" + DIALOGS
built.append(page("catalog", "Запчасти, аккумуляторы и электровелосипеды: витрина — CITY BIKE Новосибирск", "Ассортимент CITY BIKE в Новосибирске: электровелосипеды, мотор-колёса, Li-ion АКБ, велозапчасти и аксессуары. Цены, наличие и бронирование через мессенджер.", all_cards))
for g in CATALOG["groups"]:
    body = f'<section class="sec" style="padding-bottom:0"><div class="wrap"><p class="kick">Витрина</p><h1 style="font-size:clamp(36px,6.6vw,76px)">{e(g["title"])}</h1><p class="lead" style="margin:12px 0 18px">{e(g["lead"])}</p>{chips(b, g["slug"])}{SEARCH}</div></section><section class="sec" style="padding-top:24px"><div class="wrap">{NOT_ALL}{group_cards(b, g)}<div style="margin-top:36px">{STEPS}</div></div></section>' + DIALOGS
    built.append(page(g["slug"], g["seo"] + " — CITY BIKE", g["descr"], body))

# how to buy: a four-panel comic strip, drawn inline so it needs no image files
_S = 'fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"'
COMIC = [
    ("Выбрали", "Смотрите витрину и складывайте нужное в подборку.",
     f'<svg viewBox="0 0 120 90" aria-hidden="true"><rect x="22" y="14" width="76" height="50" rx="4" {_S}/><path d="M10 72h100" {_S}/><path d="M34 30h22M34 40h34M34 50h16" {_S}/><circle cx="82" cy="38" r="9" fill="var(--green)"/><path d="M78 38l3 3 6-6" stroke="#06120a" stroke-width="3" fill="none"/></svg>'),
    ("Написали", "Подборка уходит мастеру одним сообщением. Он проверит наличие и совместимость.",
     f'<svg viewBox="0 0 120 90" aria-hidden="true"><path d="M14 16h58a6 6 0 0 1 6 6v24a6 6 0 0 1-6 6H38l-14 12V52H14a6 6 0 0 1-6-6V22a6 6 0 0 1 6-6z" {_S}/><path d="M48 40h56a6 6 0 0 1 6 6v18a6 6 0 0 1-6 6h-6v12L86 70H48a6 6 0 0 1-6-6V46a6 6 0 0 1 6-6z" fill="var(--purple)" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/><path d="M22 30h40M22 40h26" {_S}/><circle cx="62" cy="56" r="3" fill="#fff"/><circle cx="76" cy="56" r="3" fill="#fff"/><circle cx="90" cy="56" r="3" fill="#fff"/></svg>'),
    ("Оплатили", "Наличными, картой, переводом, СБП, по счёту. Есть рассрочка.",
     f'<svg viewBox="0 0 120 90" aria-hidden="true"><rect x="16" y="22" width="70" height="44" rx="6" {_S}/><path d="M16 36h70" stroke="currentColor" stroke-width="8"/><path d="M26 54h18" {_S}/><circle cx="92" cy="58" r="18" fill="var(--green)"/><text x="92" y="66" text-anchor="middle" font-family="Oswald,sans-serif" font-weight="700" font-size="22" fill="#06120a">₽</text></svg>'),
    ("Забрали", "В мастерской на Вокзальной магистрали, 3 или доставкой: СДЭК, Энергия, Почта России.",
     f'<svg viewBox="0 0 120 90" aria-hidden="true"><path d="M20 34l30-14 30 14v34L50 82 20 68z" {_S}/><path d="M20 34l30 14 30-14M50 48v34" {_S}/><path d="M35 27l30 14" stroke="var(--green)" stroke-width="5" stroke-linecap="round"/><path d="M88 52h20M98 42l10 10-10 10" stroke="var(--green)" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'),
]
COMIC_HTML = '<ol class="comic">' + "".join(f'<li><span class="n">{i}</span>{svg}<b>{t}</b><p>{d}</p></li>' for i, (t, d, svg) in enumerate(COMIC, 1)) + "</ol>"
buy = f"""<section class="sec"><div class="wrap"><p class="kick">Как купить</p><h1 style="font-size:clamp(38px,7vw,84px);margin-bottom:24px">Доставка и оплата</h1>{COMIC_HTML}
<div class="pack" style="margin-top:24px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))"><article><h3>Заказ</h3><p class="mut" style="margin:10px 0 0">Для уточнения наличия и резервирования свяжитесь с нами любым удобным способом.</p></article><article><h3>Оплата</h3><ul style="margin-top:10px"><li>Наличными</li><li>Картой</li><li>Переводом с карты на карту, СБП</li><li>По счёту с ИП или ООО</li><li>Рассрочка и кредит</li></ul></article><article><h3>Самовывоз</h3><p class="mut" style="margin:10px 0 0">{ADDR}. {HOURS}. Предварительно позвоните или напишите в WhatsApp: {PHONE_T}.</p></article><article><h3>Доставка</h3><p class="mut" style="margin:10px 0 0">Отправляем в день заказа после полной предоплаты: СДЭК, Энергия или Почта России. Сумму и сроки сообщит менеджер.</p></article></div></div></section>"""
built.append(page("oplata", "Как купить: оплата и доставка — CITY BIKE Новосибирск", "Как заказать в CITY BIKE: бронирование через мессенджер, оплата наличными, картой, СБП, рассрочка. Самовывоз в Новосибирске или доставка СДЭК, Энергией, Почтой России.", buy))

# Short excerpts of real 2GIS reviews (checked 2026-11-07), name shortened to first name + initial.
REVIEWS = [
    ("Ольга К.", "август 2025", "До этого объездили много сервисов, но никто не брался. Ребята всё внимательно посмотрели, объяснили, не навязывая лишнего, отремонтировали буквально за 1–2 дня."),
    ("Алексей О.", "январь 2026", "Порадовала бесплатная диагностика, всё чётко расписали по ремонту и обозначили стоимость. Велосипед работает как часы."),
    ("Дмитрий", "март 2026", "Говорят всегда всё прямо, как и есть, не пытаясь обмануть на копейку."),
    ("Михаил Д.", "апрель 2024", "Оставлял на электрификацию свой Трек, перекраску рамы и замену комплектующих. Команда профи, сроки соблюдены."),
    ("Аня Ш.", "сентябрь 2025", "Мне уже 2 года помогают с любыми велозадачами. А ещё ребята такие душевные."),
    ("Павел М.", "май 2025", "Запчасти всегда есть в наличии. Ремонт делают в короткие сжатые сроки."),
]
REV_HTML = f"""<section class="sec" style="padding-top:0"><div class="wrap"><div class="rev-head"><div><p class="kick">Отзывы</p><h2>Что говорят в 2ГИС</h2></div><a class="gis" href="{GIS}" rel="noopener"><b>5,0</b><span>★★★★★</span><small>143 оценки · 2ГИС</small></a></div>
<div class="revs">{''.join(f'<figure class="rev"><span class="stars" aria-label="5 из 5">★★★★★</span><blockquote>{e(t)}</blockquote><figcaption><b>{e(n)}</b> · {d}</figcaption></figure>' for n, d, t in REVIEWS)}</div>
<div class="btns" style="margin-top:18px"><a class="btn alt" href="{GIS}" rel="noopener">Все отзывы в 2ГИС</a><a class="btn ghost" href="{FLAMP}" rel="noopener">Отзывы на Флампе</a></div></div></section>"""

about = hero(b, "evgeny", "Мастерская CITY BIKE", "С 2012 года", "Мастерская CITY BIKE", "Вся наша команда катается сама: стрит, фристайл, электробайки каждый день. Поэтому мы как никто понимаем, как байк должен работать и чего от него ждать.", f'<a class="btn" href="tel:{PHONE}">Позвонить</a><a class="btn alt" href="{GIS}" rel="noopener">Отзывы в 2ГИС</a>')
about += TAPE + f"""<section class="sec"><div class="wrap split"><div><h2>Команда под любую задачу</h2><p class="lead" style="margin-top:12px">Сити Байк основан в 2012 году. В команде мастера-механики, инженеры, электронщики, маляры и токари, и все они райдеры.</p><p class="lead">Чиним, обслуживаем и собираем велосипеды, электробайки, электромото и аккумуляторы. Решаем задачи и любителя покататься по выходным, и профессионального райдера.</p></div>{img(b, 'master', 'Мастер за работой в CITY BIKE', '(min-width:960px) 50vw,100vw')}</div></section>
{video_sec("Видео", "Мастерская изнутри")}
{REV_HTML}
<section class="sec" style="padding-top:0"><div class="wrap">{gal(b, [("truing", "Правка колеса"), ("el-board", "Проверка платы"), ("akb-build", "Сборка аккумулятора"), ("spokes", "Настройка переключателя"), ("motor-stator", "Ревизия мотор-колеса"), ("eb-red-tan", "Электровелосипед после сборки"), ("bench", "Рабочее место мастера"), ("emoto-black", "Электромото у мастерской")])}</div></section>""" + contact_cta(b, "Приезжайте в мастерскую")
built.append(page("o_nas", "О велосервисе CITY BIKE в Новосибирске: мастера с 2012 года", "CITY BIKE в Новосибирске с 2012 года: мастера-механики, инженеры, электронщики, маляры и токари. Ремонт всех типов велосипедов и электровелосипеды.", about))

contact = f"""<section class="sec"><div class="wrap"><p class="kick">Контакты</p><h1 style="font-size:clamp(38px,7vw,84px);margin-bottom:24px">Приезжайте</h1><div class="contact"><dl>
<dt>Адрес</dt><dd>{ADDR} (цоколь)</dd><dd class="mut" style="font-weight:600;font-size:15px">Въезд со двора. Есть удобная парковка.</dd>
<dt>Режим работы</dt><dd>{HOURS}</dd>
<dt>Евгений</dt><dd><a href="tel:{PHONE}">{PHONE_T}</a></dd>
<dt>Максим</dt><dd><a href="tel:{PHONE2}">{PHONE2_T}</a></dd>
<dt>Написать</dt><dd><div class="btns" style="margin-top:8px"><a class="btn sm" href="{WA}" rel="noopener">WhatsApp</a><a class="btn sm alt" href="{TG}" rel="noopener">Telegram</a><a class="btn sm ghost" href="{VK}" rel="noopener">ВКонтакте</a></div></dd>
</dl><iframe class="map" title="CITY BIKE на карте" loading="lazy" src="https://yandex.ru/map-widget/v1/?text=%D0%9D%D0%BE%D0%B2%D0%BE%D1%81%D0%B8%D0%B1%D0%B8%D1%80%D1%81%D0%BA%2C%20%D0%92%D0%BE%D0%BA%D0%B7%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F%20%D0%BC%D0%B0%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D0%BB%D1%8C%203&z=16"></iframe></div></div></section>"""
built.append(page("contact", "Контакты велосервиса CITY BIKE: Вокзальная магистраль, 3, Новосибирск", f"CITY BIKE: {ADDR}, цоколь, въезд со двора. {HOURS}. Телефон {PHONE_T}, WhatsApp, Telegram.", contact))

CATS = {"motor": "Мотор-колесо", "control": "Контроллер и газ", "akb": "Аккумулятор", "display": "Дисплей"}
diag_cards = ""
for d in DIAG:
    secs = "".join(f"<h4>{e(s['label'])}</h4>" + "".join(f"<p>{e(l)}</p>" for l in s["lines"]) for s in d["sections"])
    diag_cards += f'<article class="diag" data-cat="{d["cat"]}" data-kw="{e(d["kw"])}"><div class="cat">{CATS[d["cat"]]}</div><h3>{e(d["title"])}</h3>{secs}</article>'
diag_faq = [(d["title"], " ".join(l for s in d["sections"] for l in s["lines"])) for d in DIAG]
filters = '<button class="chip on" type="button" data-diag="all">Все проблемы</button>' + "".join(f'<button class="chip" type="button" data-diag="{k}">{v}</button>' for k, v in [("motor", "Мотор"), ("akb", "Аккумулятор"), ("control", "Контроллер и газ"), ("display", "Дисплей")])
diag = f"""<section class="sec"><div class="wrap" style="max-width:860px"><p class="kick">Онлайн-диагност</p><h1 style="font-size:clamp(36px,6.6vw,76px);margin-bottom:14px">Что случилось с электро&shy;велосипедом?</h1><p class="lead">Введите симптом, звук или код ошибки.</p><input id="diag-q" type="search" placeholder="Например: хрустит, ошибка, ручка газа, дёргается" aria-label="Поиск симптома"><div class="chips" style="margin-top:10px">{filters}</div>{diag_cards}<p id="diag-empty" class="empty">Такого симптома пока нет. Позвоните мастеру, разберёмся.</p></div></section>""" + contact_cta(b, "Не разобрались? Привозите")
built.append(page("sovets", "Неисправности электровелосипеда: онлайн-диагност и коды ошибок — CITY BIKE", "Почему хрустит мотор, байк выключается в горку, не работает ручка газа. Симптомы, причины, проверка и расшифровка ошибок E-06 — E-10.", diag, [faq_ld(diag_faq)]))

with open(os.path.join(DATA, "calc_widget.html"), encoding="utf-8") as f:
    widget = f.read()
calc = f"""<section class="sec" style="padding-bottom:24px"><div class="wrap"><p class="kick">Калькулятор</p><h1 style="font-size:clamp(36px,6.6vw,76px);margin-bottom:12px">Соберите свой электро&shy;велосипед</h1><p class="lead">Выберите конфигурацию: калькулятор посчитает стоимость и прогноз запаса хода.</p></div></section><div class="wrap" style="padding-bottom:48px">{widget}</div>""" + contact_cta(b, "Собрали? Покажите мастеру")
built.append(page("calc", "Калькулятор электровелосипеда: расчёт комплекта и цены — CITY BIKE", "Подберите мотор, контроллер и аккумулятор, узнайте стоимость и прогноз запаса хода. Калькулятор электровелосипеда от CITY BIKE, Новосибирск.", calc))

# robots, sitemap, 404
with open(os.path.join(DOCS, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(f"User-agent: *\nDisallow:\nSitemap: {SITE}/sitemap.xml\n" if PROD else "User-agent: *\nDisallow: /\n")
sm = os.path.join(DOCS, "sitemap.xml")
if PROD:
    with open(sm, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}/{s}</loc></url>\n" for s in built) + "</urlset>\n")
elif os.path.exists(sm):
    os.remove(sm)
open(os.path.join(DOCS, ".nojekyll"), "w").close()
print("pages", len(built), "preview" if not PROD else "PROD", "examples", sum(1 for g in CATALOG["groups"] for s in g["subs"] if s not in BY_SUB), "products placed", sum(len(v) for v in BY_SUB.values()))
