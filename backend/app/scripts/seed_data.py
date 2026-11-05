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
]
