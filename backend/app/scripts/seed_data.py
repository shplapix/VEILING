from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.models.enums import LotCategory, LotStatus


@dataclass(frozen=True)
class SeedImageSpec:
    filename: str
    sort_order: int
    caption: str
    primary_color: tuple[int, int, int] = (20, 20, 20)
    secondary_color: tuple[int, int, int] = (40, 40, 40)
    pattern_type: str = "plain"


@dataclass(frozen=True)
class ArchiveExhibit:
    title: str
    brand: str
    designer: str
    season: str
    year: int
    collection_name: str | None
    category: LotCategory
    subcategory: str
    tagged_size: str
    fits_like: str
    measurements: dict[str, Any]
    materials: dict[str, Any]
    condition_rating: int
    condition_details: str
    country_of_origin: str
    provenance_notes: str | None
    seller_location: str
    shipping_notes: str
    start_price: Decimal
    floor_price: Decimal
    step_amount: Decimal
    interval_seconds: int
    status: LotStatus
    images: list[SeedImageSpec] = field(default_factory=list)


ARCHIVE_EXHIBITS: list[ArchiveExhibit] = [
    ArchiveExhibit(
        title='Бомбер Raf Simons AW01 "Riot! Riot! Riot!" Camo Bomber',
        brand="Raf Simons",
        designer="Raf Simons",
        season="Autumn/Winter",
        year=2001,
        collection_name="Riot! Riot! Riot!",
        category=LotCategory.OUTERWEAR,
        subcategory="Військовий бомбер",
        tagged_size="50",
        fits_like="Oversized L",
        measurements={
            "pit_to_pit": 68.0,
            "length": 71.0,
            "shoulders": 56.0,
            "sleeve": 65.0,
            "hem": 52.0,
        },
        materials={
            "outer": "100% виварена бавовна у камуфляжі Woodland з вінтажним вимиванням",
            "lining": "100% стьобаний поліамід з термопрокладкою",
            "patches": "Автентичні нашивки Manic Street Preachers з фотографіями Річі Едвардса",
            "hardware": "Металеві блискавки Raccagni",
        },
        condition_rating=9,
        condition_details=(
            "Музейний стан архівного збереження. Оригінальне фабричне вінтажне "
            "состарювання камуфляжного полотна без дефектів. Текстильні нашивки надійно "
            "зафіксовані, бічні та нарукавні кишені зберегли геометрію."
        ),
        country_of_origin="Зроблено в Бельгії",
        provenance_notes=(
            "Головний експонат показу AW01-02 'Riot! Riot! Riot!'. Отримано з приватної "
            "антверпенської колекції раннього періоду бренду. Один з найрідкісніших "
            "артефактів чоловічої архівної моди."
        ),
        seller_location="Амстердам, Нідерланди",
        shipping_notes=(
            "Застрахована кур'єрська доставка в музейному боксі з опломбуванням та "
            "персональним трекінгом (3–5 днів)."
        ),
        start_price=Decimal("180000.00"),
        floor_price=Decimal("120000.00"),
        step_amount=Decimal("1500.00"),
        interval_seconds=45,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="raf_simons_aw01_riot_front.jpg",
                sort_order=0,
                caption="Фронтальний архівний ракурс бомбера з автентичними нашивками",
            ),
            SeedImageSpec(
                filename="raf_simons_aw01_riot_detail.jpg",
                sort_order=1,
                caption="Макро-ракурс вивареного бавовняного твілу та фактури нашивок",
            ),
            SeedImageSpec(
                filename="raf_simons_aw01_riot_macro.jpg",
                sort_order=2,
                caption="Деталь металевої блискавки Raccagni та нарукавної кишені патронташа",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Мотокуртка Helmut Lang AW99 Astro Biker Jacket",
        brand="Helmut Lang",
        designer="Helmut Lang",
        season="Autumn/Winter",
        year=1999,
        collection_name="Seance de Travail",
        category=LotCategory.OUTERWEAR,
        subcategory="Астро-куртка",
        tagged_size="48",
        fits_like="Slim M",
        measurements={
            "pit_to_pit": 53.0,
            "length": 64.0,
            "shoulders": 47.0,
            "sleeve": 66.0,
            "hem": 50.0,
        },
        materials={
            "outer": "100% балістичний бавовняний канвас зі смоляним просоченням",
            "collar": "100% знімне хутро стриженої натуральної овчини",
            "lining": "100% віскозне жакардове полотно",
            "straps": "Внутрішні еластичні плечові стропи bondage straps",
            "hardware": "Масивні італійські блискавки Lampo",
        },
        condition_rating=9,
        condition_details=(
            "Виняткова схоронність. Покриття канвасу без заломів, знімний комір з "
            "натуральної овчини чистий і м'який, внутрішні бандажні стропи пружні, "
            "замки Lampo працюють ідеально."
        ),
        country_of_origin="Зроблено в Італії",
        provenance_notes=(
            "Культовий експонат з показу AW1999 'Seance de Travail'. Збережено оригінальний "
            "фірмовий ярлик Helmut Lang New York міланського періоду виробництва."
        ),
        seller_location="Відень, Австрія",
        shipping_notes="Застрахована кур'єрська доставка по Європі та Україні (3–5 робочих днів).",
        start_price=Decimal("140000.00"),
        floor_price=Decimal("90000.00"),
        step_amount=Decimal("1200.00"),
        interval_seconds=50,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="helmut_lang_aw99_astro_front.jpg",
                sort_order=0,
                caption="Фронтальний вигляд Astro Biker Jacket з коміром з натуральної овчини",
            ),
            SeedImageSpec(
                filename="helmut_lang_aw99_astro_detail.jpg",
                sort_order=1,
                caption="Внутрішні бандажні стропи bondage straps та текстура балістичного канвасу",
            ),
            SeedImageSpec(
                filename="helmut_lang_aw99_astro_macro.jpg",
                sort_order=2,
                caption="Масивні металеві блискавки Lampo та автентична строчка ліктів",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Джинси Maison Martin Margiela Artisanal Painted Denim 1990s",
        brand="Maison Margiela",
        designer="Martin Margiela",
        season="Spring/Summer",
        year=1998,
        collection_name="Artisanal Line 0",
        category=LotCategory.BOTTOMS,
        subcategory="Денім ручної роботи",
        tagged_size="W30 L32",
        fits_like="Regular Straight W30",
        measurements={
            "waist": 40.0,
            "length": 106.0,
            "inseam": 81.0,
            "rise": 28.5,
            "hem": 20.0,
        },
        materials={
            "outer": "100% вінтажний денім Levi's 501 1970-х років",
            "treatment": "Ручне нашарування білої емалі bianco bianchetto з ефектом кракелюру",
            "hardware": "Оригінальні окислені латунні заклепки та ґудзики-болти",
            "stitches": "4 автентичні білі діагональні стібки на задній кокетці",
        },
        condition_rating=8,
        condition_details=(
            "Ідеальна патина для лінійки Artisanal. Природні тріщини та лущення білої фарби "
            "відкривають темно-синій денім під нею, створюючи унікальний музейний характер."
        ),
        country_of_origin="Зроблено у Франції",
        provenance_notes=(
            "Виріб ручної роботи паризького ательє Margiela на Rue Saint-Maur (Лінія 0). "
            "Кожна пара створювалася вручну на основі селекційного вінтажу."
        ),
        seller_location="Париж, Франція",
        shipping_notes="Застрахована кур'єрська доставка по Європі та Україні (3–5 робочих днів).",
        start_price=Decimal("98000.00"),
        floor_price=Decimal("62000.00"),
        step_amount=Decimal("850.00"),
        interval_seconds=40,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="margiela_artisanal_painted_front.jpg",
                sort_order=0,
                caption="Фронтальний ракурс джинсів з нашаруванням фарби bianco bianchetto",
            ),
            SeedImageSpec(
                filename="margiela_artisanal_painted_detail.jpg",
                sort_order=1,
                caption="Макро-ракурс вінтажного кракелюру та відлущування білої емалі",
            ),
            SeedImageSpec(
                filename="margiela_artisanal_painted_macro.jpg",
                sort_order=2,
                caption="Фірмові білі стібки ручної роботи Maison Martin Margiela",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Джинси Undercover 85 Denim AW05 "Arts & Crafts"',
        brand="Undercover",
        designer="Jun Takahashi",
        season="Autumn/Winter",
        year=2005,
        collection_name="Arts & Crafts",
        category=LotCategory.BOTTOMS,
        subcategory="Деконструйований денім",
        tagged_size="2 (Medium)",
        fits_like="Slim Tapered W31",
        measurements={
            "waist": 41.0,
            "length": 105.0,
            "inseam": 80.0,
            "rise": 26.5,
            "hem": 18.5,
        },
        materials={
            "outer": "100% японський селвідж денім Kurabo щільністю 14 унцій",
            "patchwork": "Шкіряні заплати, ручний шов нитками сашіко sashiko, металеві люверси",
            "hardware": "Кастомні ґудзики Undercover з гравіюванням",
        },
        condition_rating=9,
        condition_details=(
            "Експонат у винятковому стані. Ручна вишивка у вигляді хрестів та фірмові "
            "розрізи цілісні, шкіряні вставки на задніх кишенях еластичні без розтріскувань."
        ),
        country_of_origin="Зроблено в Японії",
        provenance_notes=(
            "Легендарна модель '85' з колекції AW05 'Arts & Crafts'. Вершина японської "
            "деконструктивної майстерності Джуна Такахаші, культовий зразок світового стрітвіру."
        ),
        seller_location="Токіо, Японія",
        shipping_notes=(
            "Міжнародна експрес-доставка кур'єром з повним страхуванням та трекінгом (4–6 днів)."
        ),
        start_price=Decimal("115000.00"),
        floor_price=Decimal("75000.00"),
        step_amount=Decimal("950.00"),
        interval_seconds=55,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="undercover_85_denim_front.jpg",
                sort_order=0,
                caption="Фронтальний вигляд Undercover 85 з детальним дистресом колін",
            ),
            SeedImageSpec(
                filename="undercover_85_denim_detail.jpg",
                sort_order=1,
                caption="Деталь ручних швів сашіко та вишитих хрестів майстра",
            ),
            SeedImageSpec(
                filename="undercover_85_denim_macro.jpg",
                sort_order=2,
                caption="Шкіряні заплати та фурнітура кишень японського селвіджу",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Шкіряний бомбер Rick Owens AW14 "Moody" Exploder',
        brand="Rick Owens",
        designer="Rick Owens",
        season="Autumn/Winter",
        year=2014,
        collection_name="Moody",
        category=LotCategory.OUTERWEAR,
        subcategory="Шкіряний бомбер",
        tagged_size="50 (IT)",
        fits_like="Regular L",
        measurements={
            "pit_to_pit": 56.0,
            "length": 68.0,
            "shoulders": 46.0,
            "sleeve": 72.0,
            "hem": 48.0,
        },
        materials={
            "outer": "100% текстурована мита шкіра ягняти blistered lambskin",
            "lining": "100% органічна бавовна та шовкове купро в рукавах",
            "cuffs": "100% щільна вовняна резинка",
            "hardware": "Масивна геометрична металева блискавка Raccagni",
        },
        condition_rating=9,
        condition_details=(
            "Ідеальний стан шкіри. Фірмова пухирчаста текстура шкіри глибокого "
            "чорного кольору Carbon Black, геометрія високого коміра-стійки повністю "
            "тримає форму."
        ),
        country_of_origin="Зроблено в Італії",
        provenance_notes=(
            "Подіумний експонат колекції AW14 'Moody'. Придбано у Парижі в бутику "
            "Palais Royal. Комплектується фірмовим тканинним чохлом Rick Owens."
        ),
        seller_location="Берлін, Німеччина",
        shipping_notes="Застрахована кур'єрська доставка по Європі та Україні (3–5 робочих днів).",
        start_price=Decimal("76000.00"),
        floor_price=Decimal("48000.00"),
        step_amount=Decimal("650.00"),
        interval_seconds=45,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="rick_owens_moody_exploder_front.jpg",
                sort_order=0,
                caption="Фронтальний ракурс шкіряного бомбера з високим коміром-стійкою",
            ),
            SeedImageSpec(
                filename="rick_owens_moody_exploder_detail.jpg",
                sort_order=1,
                caption="Макро-ракурс пухирчастої фактури шкіри blistered lamb",
            ),
            SeedImageSpec(
                filename="rick_owens_moody_exploder_macro.jpg",
                sort_order=2,
                caption="Масивна асиметрична металева блискавка Raccagni",
            ),
        ],
    ),
    ArchiveExhibit(
        title='В\'язаний светр Yohji Yamamoto Pour Homme AW02 "Dandies"',
        brand="Yohji Yamamoto",
        designer="Yohji Yamamoto",
        season="Autumn/Winter",
        year=2002,
        collection_name="Dandies & Vagabonds",
        category=LotCategory.TOPS,
        subcategory="В'язаний оверсайз светр",
        tagged_size="3",
        fits_like="Draped Oversized L-XL",
        measurements={
            "pit_to_pit": 64.0,
            "length": 76.0,
            "shoulders": 58.0,
            "sleeve": 62.0,
            "hem": 58.0,
        },
        materials={
            "outer": "85% шерсть перуанської альпаки, 15% тонка мериносова вовна",
            "details": "Ручне зшивання геометричних панелей відкритими вовняними петлями",
            "collar": "Асиметричний м'який драпірований комір",
        },
        condition_rating=9,
        condition_details=(
            "Виняткова якість збереження натурального волокна альпаки. Повна відсутність "
            "скочування чи деформації в'язки. Зберігався виключно у кедровому музейному кейсі."
        ),
        country_of_origin="Зроблено в Японії",
        provenance_notes=(
            "Знахідка з легендарного показу Pour Homme AW2002 'Dandies & Vagabonds'. "
            "Передано з приватної колекції куратора японського текстилю з Кіото."
        ),
        seller_location="Кіото, Японія",
        shipping_notes=(
            "Застрахована міжнародна кур'єрська доставка з пломбою автентичності (3–5 днів)."
        ),
        start_price=Decimal("54000.00"),
        floor_price=Decimal("35000.00"),
        step_amount=Decimal("450.00"),
        interval_seconds=60,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="yohji_yamamoto_dandies_knit_front.jpg",
                sort_order=0,
                caption="Фронтальний вигляд светра з драпірованим асиметричним коміром",
            ),
            SeedImageSpec(
                filename="yohji_yamamoto_dandies_knit_detail.jpg",
                sort_order=1,
                caption="Макро-ракурс об'ємного плетіння перуанської альпаки",
            ),
            SeedImageSpec(
                filename="yohji_yamamoto_dandies_knit_macro.jpg",
                sort_order=2,
                caption="Автентичні відкриті ручні стібки на плечових стиках",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Оксамитовий мундир Dior Homme AW04 Napoleon Officer Jacket",
        brand="Dior Homme",
        designer="Hedi Slimane",
        season="Autumn/Winter",
        year=2004,
        collection_name="Victim of the Crime",
        category=LotCategory.OUTERWEAR,
        subcategory="Військовий мундир",
        tagged_size="48 (IT)",
        fits_like="Ultra Slim 48",
        measurements={
            "pit_to_pit": 49.0,
            "length": 69.0,
            "shoulders": 43.0,
            "sleeve": 67.0,
            "hem": 48.0,
        },
        materials={
            "outer": "100% вовняний кашемір преміум класу та шовковий оксамит",
            "braiding": "Автентичні золоті гусарські галуни ручного плетіння bullion wire",
            "lining": "100% чорний шовковий жакард Dior Homme з логотипом бджоли",
            "buttons": "Позолочені геральдичні ґудзики з гравіюванням орла",
        },
        condition_rating=9,
        condition_details=(
            "Колекційний екземпляр музейної цінності з легендарного показу Еді "
            "Слімана AW04 'Victim of the Crime'. "
            "Золоте шиття не потьмяніло, оксамит на комірі та лацканах "
            "збережений у первозданному вигляді."
        ),
        country_of_origin="Зроблено у Франції",
        provenance_notes=(
            "Придбано на аукціоні приватної колекції в Парижі. Один з "
            "найвизначніших силуетів революції "
            "чоловічої моди початку 2000-х."
        ),
        seller_location="Париж, Франція",
        shipping_notes=(
            "Спеціалізована застрахована кур'єрська доставка у захисному "
            "гардеробному кофрі Dior Homme (3–4 дні)."
        ),
        start_price=Decimal("165000.00"),
        floor_price=Decimal("105000.00"),
        step_amount=Decimal("1400.00"),
        interval_seconds=50,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="dior_homme_aw04_napoleon_front.jpg",
                sort_order=0,
                caption="Фронтальний вигляд гусарського мундира з золотими галунами bullion wire",
            ),
            SeedImageSpec(
                filename="dior_homme_aw04_napoleon_detail.jpg",
                sort_order=1,
                caption="Макро-ракурс вишитих золотих галунів та позолочених геральдичних ґудзиків",
            ),
            SeedImageSpec(
                filename="dior_homme_aw04_napoleon_macro.jpg",
                sort_order=2,
                caption="Фактура чорного шовкового оксамиту та манжет мундира",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Гібридна фланелева парка Number (N)ine AW05 "The High Streets"',
        brand="Number (N)ine",
        designer="Takahiro Miyashita",
        season="Autumn/Winter",
        year=2005,
        collection_name="The High Streets",
        category=LotCategory.OUTERWEAR,
        subcategory="Гібридна парка",
        tagged_size="3 (Large)",
        fits_like="Relaxed Boxy L",
        measurements={
            "pit_to_pit": 62.0,
            "length": 78.0,
            "shoulders": 54.0,
            "sleeve": 65.0,
            "hem": 60.0,
        },
        materials={
            "outer": "100% важка шотландська бавовняна фланель у тіньову клітинку shadow plaid",
            "hood": "Важка вафельна термо-бавовна щільністю 420 г/м²",
            "details": (
                "Шовкова вишивка фірмового мотиву сліз-сердець tribal tear "
                "heart, вінтажний дистрес країв"
            ),
            "hardware": "Подвійні латунні блискавки riri",
        },
        condition_rating=9,
        condition_details=(
            "Винятковий стан культового гранж-експонату Такахіро Міяшіти. Фабричний "
            "дистрес збережено без додаткових "
            "пошкоджень, вафельний капюшон чистий, блискавки riri ходять м'яко."
        ),
        country_of_origin="Зроблено в Японії",
        provenance_notes=(
            "Культовий айтем з показу AW05 'The High Streets'. Документована "
            "покупка у флагманському бутику "
            "Number (N)ine в районі Аояма, Токіо."
        ),
        seller_location="Токіо, Японія",
        shipping_notes=(
            "Міжнародна експрес-доставка кур'єром з повним страхуванням та трекінгом (4–5 днів)."
        ),
        start_price=Decimal("88000.00"),
        floor_price=Decimal("54000.00"),
        step_amount=Decimal("750.00"),
        interval_seconds=45,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="number_nine_aw05_hybrid_front.jpg",
                sort_order=0,
                caption=(
                    "Фронтальний вигляд гібридної парки з комбінацією фланелі та термо-капюшона"
                ),
            ),
            SeedImageSpec(
                filename="number_nine_aw05_hybrid_detail.jpg",
                sort_order=1,
                caption="Деталь вишивки сліз-сердець tribal tear heart та фактури фланелі",
            ),
            SeedImageSpec(
                filename="number_nine_aw05_hybrid_macro.jpg",
                sort_order=2,
                caption="Латунні масивні замки riri та фабричний мікро-дистрес манжетів",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Тактичний парашутний бомбер Issey Miyake Men AW96 "Parachute"',
        brand="Issey Miyake",
        designer="Issey Miyake",
        season="Autumn/Winter",
        year=1996,
        collection_name="Parachute Cargo",
        category=LotCategory.OUTERWEAR,
        subcategory="Парашутний бомбер",
        tagged_size="M (JP)",
        fits_like="Boxy M-L",
        measurements={
            "pit_to_pit": 63.0,
            "length": 66.0,
            "shoulders": 55.0,
            "sleeve": 61.0,
            "hem": 54.0,
        },
        materials={
            "outer": (
                "100% надміцний балістичний парашутний нейлон з "
                "водовідштовхувальним тефлоновим просоченням"
            ),
            "straps": "Армовані стропи безпеки з D-подібними кільцями з анодованого алюмінію",
            "hardware": "16 прихованих японських блискавок YKK Vislon та тактичні фіксатори",
            "lining": "Дихаюча сітка coolmax",
        },
        condition_rating=9,
        condition_details=(
            "Рідкісний зразок авангардного японського мілітарі-текстилю "
            "середини 90-х. Нейлонова тканина "
            "без зачіпок та плям, уся складна система кишень та строп повністю комплектна."
        ),
        country_of_origin="Зроблено в Японії",
        provenance_notes=(
            "Експонат з приватної колекції індустріального дизайну в Осаці. Один "
            "з найбільш цитованих зразків "
            "раннього функціоналізму Іссея Міяке."
        ),
        seller_location="Осака, Японія",
        shipping_notes=(
            "Застрахована міжнародна кур'єрська доставка в антистатичному кофрі (4–6 днів)."
        ),
        start_price=Decimal("125000.00"),
        floor_price=Decimal("82000.00"),
        step_amount=Decimal("1100.00"),
        interval_seconds=55,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="issey_miyake_aw96_parachute_front.jpg",
                sort_order=0,
                caption=(
                    "Фронтальний вигляд парашутного бомбера у фірмовому кольорі оливкового нейлону"
                ),
            ),
            SeedImageSpec(
                filename="issey_miyake_aw96_parachute_detail.jpg",
                sort_order=1,
                caption="Деталь інтегрованих строп безпеки та анодованих D-кілець",
            ),
            SeedImageSpec(
                filename="issey_miyake_aw96_parachute_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс переплетення ripstop нейлону та кишень на рукаві",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Шовковий оксамитовий сукаджан Undercover AW02 "Witches"',
        brand="Undercover",
        designer="Jun Takahashi",
        season="Autumn/Winter",
        year=2002,
        collection_name="Witches / 魔女 (Majyo)",
        category=LotCategory.OUTERWEAR,
        subcategory="Двосторонній сукаджан",
        tagged_size="Medium",
        fits_like="Relaxed M",
        measurements={
            "pit_to_pit": 57.0,
            "length": 65.0,
            "shoulders": 48.0,
            "sleeve": 64.0,
            "hem": 46.0,
        },
        materials={
            "side_a": "100% смарагдовий шовковий оксамит з рельєфною вишивкою",
            "side_b": "100% перлинно-кремовий шовковий атлас duchesse satin",
            "embroidery": "Шовкова гладь високої щільності з мотивами магічних символів та хрестів",
            "ribbing": "100% вовняна смугаста резинка",
        },
        condition_rating=9,
        condition_details=(
            "Музейна якість зберігання. Оксамит не має затертостей, шовковий атлас "
            "зворотного боку чистий без зачіпок. "
            "Оригінальний двосторонній бігунок YKK плавно перекидається."
        ),
        country_of_origin="Зроблено в Японії",
        provenance_notes=(
            "Подіумний зразок першого паризького показу Джуна Такахаші AW02 'Witches'. "
            "Шедевр японського ремісничого кутюру."
        ),
        seller_location="Токіо, Японія",
        shipping_notes=(
            "Застрахована міжнародна кур'єрська доставка з пломбою автентичності (4–6 днів)."
        ),
        start_price=Decimal("92000.00"),
        floor_price=Decimal("58000.00"),
        step_amount=Decimal("800.00"),
        interval_seconds=40,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="undercover_aw02_witches_front.jpg",
                sort_order=0,
                caption="Фронтальний ракурс смарагдового шовкового оксамитового сукаджана",
            ),
            SeedImageSpec(
                filename="undercover_aw02_witches_detail.jpg",
                sort_order=1,
                caption="Деталь вишивки шовком високої щільності магічної відьми та кісток",
            ),
            SeedImageSpec(
                filename="undercover_aw02_witches_macro.jpg",
                sort_order=2,
                caption="Текстура шовкового оксамиту та атласних реглан-рукавів",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Вовняний жакет Comme des Garçons Homme Plus AW94 "Offbeat Humor"',
        brand="Comme des Garçons",
        designer="Rei Kawakubo",
        season="Autumn/Winter",
        year=1994,
        collection_name="Offbeat Humor",
        category=LotCategory.OUTERWEAR,
        subcategory="Деконструйований жакет",
        tagged_size="M",
        fits_like="Relaxed Tailored M",
        measurements={
            "pit_to_pit": 55.0,
            "length": 75.0,
            "shoulders": 48.0,
            "sleeve": 63.0,
            "hem": 54.0,
        },
        materials={
            "outer": "100% виварена японська вовна boiled wool у комбінації з твідом Harris Tweed",
            "construction": "Відкриті шви навиворіт, асиметричний крій лацканів, необроблені краї",
            "lining": "Часткова шовкова купро-підкладка",
        },
        condition_rating=9,
        condition_details=(
            "Зразок ранньої концептуальної деконструкції Рей Кавакубо. Структура "
            "валяної вовни ідеально зберігла "
            "щільність та текстуру без кошлатості."
        ),
        country_of_origin="Зроблено в Японії",
        provenance_notes=(
            "Експонат придбано у Токіо в Comme des Garçons Aoyama. Комплектується "
            "оригінальними архівними запасними ґудзиками."
        ),
        seller_location="Лондон, Велика Британія",
        shipping_notes="Застрахована експрес-доставка кур'єром у захисному чохлі (3–5 днів).",
        start_price=Decimal("82000.00"),
        floor_price=Decimal("52000.00"),
        step_amount=Decimal("700.00"),
        interval_seconds=45,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="cdg_aw94_offbeat_humor_front.jpg",
                sort_order=0,
                caption="Фронтальний ракурс деконструйованого жакета з відкритими швами навиворіт",
            ),
            SeedImageSpec(
                filename="cdg_aw94_offbeat_humor_detail.jpg",
                sort_order=1,
                caption="Деталь необробленого зрізу лацкана та текстури вивареної японської вовни",
            ),
            SeedImageSpec(
                filename="cdg_aw94_offbeat_humor_macro.jpg",
                sort_order=2,
                caption="Асиметричне розташування ґудзиків та фактура твідового переплетення",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Шкіряна куртка Carol Christian Poell 2010 Titanium "Dead-End"',
        brand="Carol Christian Poell",
        designer="Carol Christian Poell",
        season="Autumn/Winter",
        year=2010,
        collection_name="Dead-End",
        category=LotCategory.OUTERWEAR,
        subcategory="Протезна шкіряна куртка",
        tagged_size="48",
        fits_like="Sculptural 48",
        measurements={
            "pit_to_pit": 51.0,
            "length": 67.0,
            "shoulders": 45.0,
            "sleeve": 70.0,
            "hem": 48.0,
        },
        materials={
            "leather": "100% кінська шкіра CUL-PTC/010 (object-dyed blistered cordovan)",
            "prosthetics": "Титанові ліктьові шарніри медичного класу, вживлені між шарами шкіри",
            "hardware": "Масивна лита фурнітура зі срібла 925 проби та сталі",
        },
        condition_rating=10,
        condition_details=(
            "Новий стан архівної схоронності (Unworn Archive). Шкіра жорстка, "
            "тримає скульптурну анатомічну форму "
            "людського тіла, титанові шарніри функціонують ідеально."
        ),
        country_of_origin="Зроблено в Італії",
        provenance_notes=(
            "Спеціальне кураторське замовлення міланської студії CCP на Via Scarlatti. "
            "Комплектується фірмовим мішком для рису, "
            "металевим тегом та вішаком."
        ),
        seller_location="Мілан, Італія",
        shipping_notes="Спеціалізована броньована доставка з температурним контролем (3–5 днів).",
        start_price=Decimal("210000.00"),
        floor_price=Decimal("145000.00"),
        step_amount=Decimal("1800.00"),
        interval_seconds=60,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="ccp_2010_titanium_leather_front.jpg",
                sort_order=0,
                caption=(
                    "Скульптурний фронтальний ракурс куртки з кінської шкіри з анатомічним силуетом"
                ),
            ),
            SeedImageSpec(
                filename="ccp_2010_titanium_leather_detail.jpg",
                sort_order=1,
                caption="Деталь вживленого титанового ліктьового шарніра медичного призначення",
            ),
            SeedImageSpec(
                filename="ccp_2010_titanium_leather_macro.jpg",
                sort_order=2,
                caption=(
                    "Макро-ракурс забарвленої в готовому виробі шкіри кордован з "
                    "пухирчастою фактурою"
                ),
            ),
        ],
    ),
    ArchiveExhibit(
        title='Селвідж джинси Junya Watanabe MAN SS02 "Poem" Denim',
        brand="Junya Watanabe",
        designer="Junya Watanabe",
        season="Spring/Summer",
        year=2002,
        collection_name="Poem Collection",
        category=LotCategory.BOTTOMS,
        subcategory="Поетичний денім",
        tagged_size="M (W32 L32)",
        fits_like="Straight Leg W32",
        measurements={
            "waist": 42.0,
            "length": 104.0,
            "inseam": 79.0,
            "rise": 28.0,
            "hem": 21.0,
        },
        materials={
            "denim": (
                "100% японський селвідж денім глибокого синього кольору Dark "
                "Indigo з червоною кромкою"
            ),
            "print": "Шовкотрафаретний друк золотисто-жовтою фарбою строф любовної поезії",
            "hardware": "Мідні заклепки та ґудзики Junya Watanabe MAN",
        },
        condition_rating=9,
        condition_details=(
            "Один з найбільш упізнаваних предметів початку 2000-х. Текст поеми "
            "чіткий без стирань чи тріщин, "
            "денім зберіг первинну суху текстуру сирого селвіджу."
        ),
        country_of_origin="Зроблено в Японії",
        provenance_notes=(
            "Подіумний експонат показу Junya Watanabe MAN SS2002. Отримано з приватної колекції "
            "лондонського колекціонера японської моди."
        ),
        seller_location="Лондон, Велика Британія",
        shipping_notes="Застрахована кур'єрська доставка з персональним трекінгом (3–5 днів).",
        start_price=Decimal("68000.00"),
        floor_price=Decimal("42000.00"),
        step_amount=Decimal("600.00"),
        interval_seconds=40,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="junya_watanabe_ss02_poem_front.jpg",
                sort_order=0,
                caption="Фронтальний ракурс селвідж деніму з шовкотрафаретним принтом поеми",
            ),
            SeedImageSpec(
                filename="junya_watanabe_ss02_poem_detail.jpg",
                sort_order=1,
                caption="Макро-ракурс золотисто-жовтого тексту поезії на сирому японському денімі",
            ),
            SeedImageSpec(
                filename="junya_watanabe_ss02_poem_macro.jpg",
                sort_order=2,
                caption="Деталь мідних брендованих заклепок та червоної кромки selvedge",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Військова парка Walter Van Beirendonck AW95 "Wild & Lethal Trash" Alien Parka',
        brand="Walter Van Beirendonck",
        designer="Walter Van Beirendonck",
        season="Autumn/Winter",
        year=1995,
        collection_name="Wild & Lethal Trash",
        category=LotCategory.OUTERWEAR,
        subcategory="Технічна парка",
        tagged_size="50",
        fits_like="Oversized L",
        measurements={
            "pit_to_pit": 66.0,
            "length": 86.0,
            "shoulders": 54.0,
            "sleeve": 66.0,
        },
        materials={
            "shell": "100% прогумований технічний нейлон Ripstop з голографічним покриттям W&LT",
            "lining": "Стьобана термопідкладка з неопреновими вставками",
        },
        condition_rating=9,
        condition_details=(
            "Ідеальний архівний стан збереження. Голографічний блиск покриття "
            "збережено рівномірно по всій довжині полотна."
        ),
        country_of_origin="Зроблено в Італії",
        provenance_notes=(
            "Оригінальний подіумний експонат показу W&LT AW1995 у Парижі. "
            "Збережено у приватній колекції Брюсселя."
        ),
        seller_location="Антверпен, Бельгія",
        shipping_notes="Застрахована музейна кур'єрська доставка з персональним супроводом (3–5 днів).",
        start_price=Decimal("110000.00"),
        floor_price=Decimal("70000.00"),
        step_amount=Decimal("1000.00"),
        interval_seconds=45,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="walter_wlt_aw95_alien_front.jpg",
                sort_order=0,
                caption="Фронтальний ракурс неонової голографічної парки з логотипом Puk-Puk",
            ),
            SeedImageSpec(
                filename="walter_wlt_aw95_alien_detail.jpg",
                sort_order=1,
                caption="Деталь голографічного термопокриття та масивних гумових патчів W&LT",
            ),
            SeedImageSpec(
                filename="walter_wlt_aw95_alien_macro.jpg",
                sort_order=2,
                caption="Макро-структура водовідштовхувального нейлону ріпстоп з металевою ниткою",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Худі без рукавів Raf Simons SS02 "Woe Onto Those" Sleeveless Hoodie',
        brand="Raf Simons",
        designer="Raf Simons",
        season="Spring/Summer",
        year=2002,
        collection_name="Woe Onto Those Who Spit On The Fear Generation",
        category=LotCategory.TOPS,
        subcategory="Архівне худі",
        tagged_size="One Size",
        fits_like="Oversized XL",
        measurements={
            "pit_to_pit": 68.0,
            "length": 74.0,
            "shoulders": 56.0,
            "sleeve": 24.0,
        },
        materials={
            "fleece": "100% важкий вибілений французький футер french terry щільністю 480 г/м²",
            "print": "Шовкотрафаретний принт антивоєнного маніфесту графітовим пігментом",
        },
        condition_rating=9,
        condition_details=(
            "Культовий експонат колекції SS02. Фабричне состарювання горловини "
            "та краю капюшона без сторонніх дефектів."
        ),
        country_of_origin="Зроблено в Бельгії",
        provenance_notes=(
            "Придбано на аукціоні ранніх робіт Рафа Сімонса в Генті. "
            "Повний архівний комплект сертифікатів автентичності."
        ),
        seller_location="Брюссель, Бельгія",
        shipping_notes="Спеціальна захищена експрес-доставка у вакуумному чохлі (2–4 дні).",
        start_price=Decimal("95000.00"),
        floor_price=Decimal("62000.00"),
        step_amount=Decimal("800.00"),
        interval_seconds=50,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="raf_simons_ss02_woe_front.jpg",
                sort_order=0,
                caption="Фронтальний оверсайз-силует білого худі без рукавів з капюшоном-куполом",
            ),
            SeedImageSpec(
                filename="raf_simons_ss02_woe_detail.jpg",
                sort_order=1,
                caption="Макро-ракурс графічного маніфесту показу SS02 та вінтажних потертостей",
            ),
            SeedImageSpec(
                filename="raf_simons_ss02_woe_macro.jpg",
                sort_order=2,
                caption="Деталь необробленого зрізу пройми рукава та важкого бавовняного плетіння",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Архівна туніка Alexander McQueen SS99 "No. 13" Spray Silhouette',
        brand="Alexander McQueen",
        designer="Alexander McQueen",
        season="Spring/Summer",
        year=1999,
        collection_name="No. 13",
        category=LotCategory.TOPS,
        subcategory="Подіумна туніка",
        tagged_size="40 IT",
        fits_like="Slim M",
        measurements={
            "pit_to_pit": 48.0,
            "length": 92.0,
            "shoulders": 42.0,
            "sleeve": 58.0,
        },
        materials={
            "cotton": "100% багатошаровий бавовняний муслін найтоншого ручного плетіння",
            "pigment": "Акриловий балонний розпил неоново-жовтого та чорного пігментів",
        },
        condition_rating=10,
        condition_details=(
            "Музейний студійний експонат без ознак носіння. "
            "Пігментний розпил зберіг повну яскравість і первинний контраст."
        ),
        country_of_origin="Зроблено у Великій Британії",
        provenance_notes=(
            "Походить із приватної студійної колекції лондонського стиліста "
            "показу Alexander McQueen SS99 No. 13."
        ),
        seller_location="Лондон, Велика Британія",
        shipping_notes="Музейна застрахована кур'єрська доставка у дерев'яному кейсі (3–5 днів).",
        start_price=Decimal("160000.00"),
        floor_price=Decimal("105000.00"),
        step_amount=Decimal("1200.00"),
        interval_seconds=55,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="mcqueen_ss99_no13_front.jpg",
                sort_order=0,
                caption="Фронтальний ракурс білої муслінової туніки з робототехнічним розпилом фарби",
            ),
            SeedImageSpec(
                filename="mcqueen_ss99_no13_detail.jpg",
                sort_order=1,
                caption="Деталь хаотичного нанесення чорного та неонового пігменту на подолі",
            ),
            SeedImageSpec(
                filename="mcqueen_ss99_no13_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс невагомого бавовняного полотна з автентичним внутрішнім ярликом",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Сітчастий лонгслів Jean Paul Gaultier AW95 "Cyber Dot" Op-Art Top',
        brand="Jean Paul Gaultier",
        designer="Jean Paul Gaultier",
        season="Autumn/Winter",
        year=1995,
        collection_name="Cyber Collection",
        category=LotCategory.TOPS,
        subcategory="Сітчастий лонгслів",
        tagged_size="M",
        fits_like="Stretchy M",
        measurements={
            "pit_to_pit": 46.0,
            "length": 64.0,
            "shoulders": 40.0,
            "sleeve": 62.0,
        },
        materials={
            "mesh": "100% ультраеластичний поліамід з оптичним кібернетичним принтом кіл",
            "finish": "Тонка обробка швів делікатним оверлоком шовковою ниткою",
        },
        condition_rating=9,
        condition_details=(
            "Еластичність сітки повністю збережена, без затяжок "
            "чи деформацій оптичних кіл геометричного візерунка."
        ),
        country_of_origin="Зроблено в Італії",
        provenance_notes=(
            "Оригінальний реліз легендарної лінійки JPG Cyber 1995 року "
            "з паризького вінтажного бутика на Rue Cambon."
        ),
        seller_location="Париж, Франція",
        shipping_notes="Застрахована експрес-доставка у фірмовому пакуванні (2–4 дні).",
        start_price=Decimal("75000.00"),
        floor_price=Decimal("48000.00"),
        step_amount=Decimal("650.00"),
        interval_seconds=40,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="jpg_aw95_cyber_front.jpg",
                sort_order=0,
                caption="Фронтальний вигляд оп-арт лонгсліва з кібернетичними оптичними точками",
            ),
            SeedImageSpec(
                filename="jpg_aw95_cyber_detail.jpg",
                sort_order=1,
                caption="Деталь анатомічної ілюзії рельєфу тіла створеної оптичною графікою",
            ),
            SeedImageSpec(
                filename="jpg_aw95_cyber_macro.jpg",
                sort_order=2,
                caption="Макро-структура мікросітки поліаміду та шовкового внутрішнього ярлика JPG",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Мілітарі парка Dries Van Noten AW14 Back-Zip Military Parka",
        brand="Dries Van Noten",
        designer="Dries Van Noten",
        season="Autumn/Winter",
        year=2014,
        collection_name="Rave & Military",
        category=LotCategory.OUTERWEAR,
        subcategory="Архівна парка",
        tagged_size="48",
        fits_like="Relaxed 48",
        measurements={
            "pit_to_pit": 62.0,
            "length": 94.0,
            "shoulders": 52.0,
            "sleeve": 66.0,
        },
        materials={
            "cotton": "100% щільна водовідштовхувальна бавовняна саржа глибокого оливкового кольору",
            "hardware": "Масивні металеві блискавки Lampo вздовж усієї лінії спини та рукавів",
        },
        condition_rating=9,
        condition_details=(
            "Відмінний стан збереження. Блискавки спинки працюють плавно, "
            "фурнітура з антикорозійним чорнінням без оксидації."
        ),
        country_of_origin="Зроблено в Бельгії",
        provenance_notes=(
            "Один із найбажаніших предметів показу Дріса Ван Нотена AW14 "
            "з антверпенського флагмана бренду Het Modepaleis."
        ),
        seller_location="Антверпен, Бельгія",
        shipping_notes="Кур'єрська доставка з персональним номером відстеження (3–5 днів).",
        start_price=Decimal("85000.00"),
        floor_price=Decimal("54000.00"),
        step_amount=Decimal("750.00"),
        interval_seconds=45,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="dries_aw14_backzip_front.jpg",
                sort_order=0,
                caption="Фронтальний класичний мілітарі-силует парки M-51 у трактуванні Dries Van Noten",
            ),
            SeedImageSpec(
                filename="dries_aw14_backzip_detail.jpg",
                sort_order=1,
                caption="Деталь розстібної центральної металевої блискавки по всій лінії спинки",
            ),
            SeedImageSpec(
                filename="dries_aw14_backzip_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс щільного діагонального саржевого плетіння тканини оливкового відтінку",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Скульптурний жилет Craig Green SS15 Wood Sculpture Vest",
        brand="Craig Green",
        designer="Craig Green",
        season="Spring/Summer",
        year=2015,
        collection_name="Silent Sculptures",
        category=LotCategory.TOPS,
        subcategory="Скульптурний жилет",
        tagged_size="M/L",
        fits_like="Adjustable M-L",
        measurements={
            "pit_to_pit": 54.0,
            "length": 68.0,
            "shoulders": 46.0,
            "sleeve": 15.0,
        },
        materials={
            "canvas": "100% виварена бавовняна парусина з довгими стрічками-фіксаторами",
            "wood": "Поліровані вручну дерев'яні конструктивні планки з натуральної вільхи",
        },
        condition_rating=10,
        condition_details=(
            "Музейна інсталяційна кондиція. Дерев'яні елементи без тріщин "
            "чи дефектів, бавовняні зав'язки цілісні."
        ),
        country_of_origin="Зроблено у Великій Британії",
        provenance_notes=(
            "Оригінальний подіумний жилет сезону SS15, "
            "що сформував естетичний канон раннього Крейга Гріна."
        ),
        seller_location="Лондон, Велика Британія",
        shipping_notes="Захисна броньована доставка у спеціальному жорсткому контейнері (3–6 днів).",
        start_price=Decimal("92000.00"),
        floor_price=Decimal("58000.00"),
        step_amount=Decimal("850.00"),
        interval_seconds=50,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="craig_green_ss15_wood_front.jpg",
                sort_order=0,
                caption="Фронтальний концептуальний вигляд білого парусинового жилета з дерев'яними планками",
            ),
            SeedImageSpec(
                filename="craig_green_ss15_wood_detail.jpg",
                sort_order=1,
                caption="Деталь фіксації дерев'яної скульптурної рами довгими бавовняними стропами",
            ),
            SeedImageSpec(
                filename="craig_green_ss15_wood_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс шліфованої деревини вільхи та ручних стібків кріплення",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Металізований пуховик Prada Sport AW99 Linea Rossa Puffer",
        brand="Prada Sport",
        designer="Miuccia Prada",
        season="Autumn/Winter",
        year=1999,
        collection_name="Linea Rossa Technical",
        category=LotCategory.OUTERWEAR,
        subcategory="Технічний пуховик",
        tagged_size="50",
        fits_like="Boxy L",
        measurements={
            "pit_to_pit": 64.0,
            "length": 70.0,
            "shoulders": 54.0,
            "sleeve": 67.0,
        },
        materials={
            "nylon": "100% дзеркально-металізований нейлон з водовідштовхувальною мембраною",
            "down": "90% натуральний білий гусячий пух, 10% добірне перо високого ступеня очищення",
        },
        condition_rating=9,
        condition_details=(
            "Рідкісний сріблястий нейлон без заломів і потертостей, "
            "культовий латексний червоний логотип Linea Rossa на зап'ясті в ідеалі."
        ),
        country_of_origin="Зроблено в Італії",
        provenance_notes=(
            "Еталонний зразок технічного мінімалізму Prada кінця 1990-х "
            "із міланського приватного сховища спортивної спадщини."
        ),
        seller_location="Мілан, Італія",
        shipping_notes="Страхована експрес-доставка у спеціальному чохлі Linea Rossa (3–5 днів).",
        start_price=Decimal("115000.00"),
        floor_price=Decimal("76000.00"),
        step_amount=Decimal("1100.00"),
        interval_seconds=45,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="prada_sport_aw99_puffer_front.jpg",
                sort_order=0,
                caption="Фронтальний ракурс сріблястого пуховика з характерним дзеркальним відблиском",
            ),
            SeedImageSpec(
                filename="prada_sport_aw99_puffer_detail.jpg",
                sort_order=1,
                caption="Деталь червоного латексного лейбла Prada Linea Rossa на правому манжеті",
            ),
            SeedImageSpec(
                filename="prada_sport_aw99_puffer_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс мембранного покриття та брендованого бігунка блискавки Prada riri",
            ),
        ],
    ),
    ArchiveExhibit(
        title='Бондажні штани Helmut Lang SS04 "Bondage" Multi-Strap Cargo',
        brand="Helmut Lang",
        designer="Helmut Lang",
        season="Spring/Summer",
        year=2004,
        collection_name="Bondage Flight Collection",
        category=LotCategory.BOTTOMS,
        subcategory="Бондажні карго",
        tagged_size="48 (W32)",
        fits_like="Slim Straight W32",
        measurements={
            "waist": 42.0,
            "length": 106.0,
            "inseam": 81.0,
            "hem": 20.0,
        },
        materials={
            "twill": "100% легка військова бавовняна саржа кольору графіт",
            "straps": "Нейлонові еластичні ремені-бондажі з матовими карабінами D-ring",
        },
        condition_rating=9,
        condition_details=(
            "Усі автентичні внутрішні та зовнішні еластичні ремені зберегли "
            "початкову пружність, фурнітура повністю оригінальна."
        ),
        country_of_origin="Зроблено в Італії",
        provenance_notes=(
            "Останній великий весняно-літній показ самого Гельмута Ланга "
            "перед відходом із власного дому моди."
        ),
        seller_location="Відень, Австрія",
        shipping_notes="Швидка застрахована кур'єрська доставка по всій Європі (2–4 дні).",
        start_price=Decimal("88000.00"),
        floor_price=Decimal("55000.00"),
        step_amount=Decimal("800.00"),
        interval_seconds=40,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="helmut_lang_ss04_bondage_front.jpg",
                sort_order=0,
                caption="Фронтальний вигляд темно-графітових штанів з перехресними бондажними стропами",
            ),
            SeedImageSpec(
                filename="helmut_lang_ss04_bondage_detail.jpg",
                sort_order=1,
                caption="Деталь регульованих карабінів та кріплень еластичних стрічок під коліном",
            ),
            SeedImageSpec(
                filename="helmut_lang_ss04_bondage_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс фактури військової саржі та чорного шкіряного патча Helmut Lang",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Шкіряні черевики Boris Bidjan Saberi SS16 Object-Dyed Boots",
        brand="Boris Bidjan Saberi",
        designer="Boris Bidjan Saberi",
        season="Spring/Summer",
        year=2016,
        collection_name="Post-Human Nomad",
        category=LotCategory.FOOTWEAR,
        subcategory="Авангардні черевики",
        tagged_size="43",
        fits_like="True to size 43",
        measurements={
            "sole_length": 31.0,
            "sole_width": 11.5,
            "shaft_height": 22.0,
            "heel_height": 3.5,
        },
        materials={
            "leather": "100% кінська шкіра рослинного дублення з фарбуванням у готовому виробі",
            "sole": "Багатошарова шкіряна підошва з гумовою профілактикою Vibram",
        },
        condition_rating=9,
        condition_details=(
            "Глибоке нерівномірне оксидне фарбування, підошва практично "
            "без слідів зносу, оригінальні вощені довгі шнурки."
        ),
        country_of_origin="Зроблено в Іспанії",
        provenance_notes=(
            "Ручна робота ательє Boris Bidjan Saberi у Барселоні "
            "з персональним підписом та номером майстра."
        ),
        seller_location="Барселона, Іспанія",
        shipping_notes="Застрахована експрес-доставка у важкій фірмовій коробці BBS (3–5 днів).",
        start_price=Decimal("98000.00"),
        floor_price=Decimal("64000.00"),
        step_amount=Decimal("900.00"),
        interval_seconds=50,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="bbs_ss16_boots_front.jpg",
                sort_order=0,
                caption="Профільний ракурс авангардних шкіряних черевиків з анатомічною колодкою",
            ),
            SeedImageSpec(
                filename="bbs_ss16_boots_detail.jpg",
                sort_order=1,
                caption="Деталь оксидного нерівномірного фарбування та срібних наконечників шнурків .925",
            ),
            SeedImageSpec(
                filename="bbs_ss16_boots_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс товстої кінської шкіри з масляним фінішем та прошивки Goodyear",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Артизанальний пробковий клатч Maison Margiela SS99 Cork Bag",
        brand="Maison Margiela",
        designer="Martin Margiela",
        season="Spring/Summer",
        year=1999,
        collection_name="Ligne 0 Artisanal",
        category=LotCategory.ACCESSORIES,
        subcategory="Артизанальний клатч",
        tagged_size="One Size",
        fits_like="Medium Clutch",
        measurements={
            "length": 32.0,
            "width": 18.0,
            "depth": 7.0,
            "strap_drop": 25.0,
        },
        materials={
            "cork": "100% натуральна пресована кора португальського коркового дуба ручного збирання",
            "leather": "Внутрішня підкладка з найтоншої білої шкіри ягняти ручного фарбування",
        },
        condition_rating=10,
        condition_details=(
            "Бездоганна колекційна схоронність артефакту лінії 0 Artisanal "
            "з фірмовими чотирма білими стібками на звороті."
        ),
        country_of_origin="Зроблено у Франції",
        provenance_notes=(
            "Створено вручну в паризькому ательє на Rue Saint-Maur "
            "для показу кутюрної лінії сезону SS1999."
        ),
        seller_location="Париж, Франція",
        shipping_notes="Особлива дбайлива доставка в амортизаційному музейному кейсі (2–4 дні).",
        start_price=Decimal("125000.00"),
        floor_price=Decimal("82000.00"),
        step_amount=Decimal("1100.00"),
        interval_seconds=45,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="margiela_ss99_cork_front.jpg",
                sort_order=0,
                caption="Фронтальний вигляд клатча з фактурної пресованої кори коркового дуба",
            ),
            SeedImageSpec(
                filename="margiela_ss99_cork_detail.jpg",
                sort_order=1,
                caption="Деталь чотирьох білих знакових стібків Maison Martin Margiela на зворотному боці",
            ),
            SeedImageSpec(
                filename="margiela_ss99_cork_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс пористої структури натурального корка та білої шкіряної підкладки",
            ),
        ],
    ),
    ArchiveExhibit(
        title="Шкіряний жилет Chrome Hearts Vintage Silver Cross Dagger Vest",
        brand="Chrome Hearts",
        designer="Richard Stark",
        season="Autumn/Winter",
        year=1998,
        collection_name="Custom Leather Vault",
        category=LotCategory.OUTERWEAR,
        subcategory="Шкіряний жилет",
        tagged_size="L",
        fits_like="Tailored L",
        measurements={
            "pit_to_pit": 56.0,
            "length": 62.0,
            "shoulders": 44.0,
            "sleeve": 12.0,
        },
        materials={
            "leather": "100% важка зерниста коров'яча шкіра найвищого ґатунку heavyweight steerhide",
            "silver": "Фурнітура та хрести ручного лиття зі срібла 925 проби Sterling Silver",
        },
        condition_rating=9,
        condition_details=(
            "Шкіра набула благородної вінтажної патини, усі срібні деталі "
            "з автентичними таврами лос-анджелеської майстерні без пошкоджень."
        ),
        country_of_origin="Зроблено в США",
        provenance_notes=(
            "Індивідуальне замовлення в майстерні Chrome Hearts у Голлівуді "
            "кінця 1990-х років. Повний комплект документів."
        ),
        seller_location="Лос-Анджелес, США",
        shipping_notes="Застрахована броньована міжнародна кур'єрська доставка (3–6 днів).",
        start_price=Decimal("195000.00"),
        floor_price=Decimal("135000.00"),
        step_amount=Decimal("1500.00"),
        interval_seconds=60,
        status=LotStatus.DRAFT,
        images=[
            SeedImageSpec(
                filename="chrome_hearts_vest_front.jpg",
                sort_order=0,
                caption="Фронтальний силует важкого шкіряного жилета зі срібними ґудзиками-хрестами",
            ),
            SeedImageSpec(
                filename="chrome_hearts_vest_detail.jpg",
                sort_order=1,
                caption="Деталь масивного срібного бігунка у формі кинджала Dagger на бічній кишені",
            ),
            SeedImageSpec(
                filename="chrome_hearts_vest_macro.jpg",
                sort_order=2,
                caption="Макро-ракурс зернистої бичачої шкіри та шовкової підкладки з монограмами CH",
            ),
        ],
    ),
]
