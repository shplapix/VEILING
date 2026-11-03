from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.models.enums import LotCategory, LotStatus


@dataclass(frozen=True)
class SeedImageSpec:
    filename: str
    sort_order: int
    caption: str
    primary_color: tuple[int, int, int]
    secondary_color: tuple[int, int, int]
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
            "patches": ("Автентичні нашивки Manic Street Preachers з фотографіями Річі Едвардса"),
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
        interval_seconds=60,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="raf_simons_aw01_riot_camo_front.png",
                sort_order=0,
                caption="Фронтальний архівний ракурс бомбера з автентичними нашивками",
                primary_color=(58, 68, 48),
                secondary_color=(38, 44, 32),
                pattern_type="camo",
            ),
            SeedImageSpec(
                filename="raf_simons_aw01_riot_camo_texture.png",
                sort_order=1,
                caption="Макро-ракурс вивареного бавовняного твілу та фактури тканини",
                primary_color=(72, 82, 58),
                secondary_color=(45, 52, 36),
                pattern_type="camo",
            ),
            SeedImageSpec(
                filename="raf_simons_aw01_riot_camo_hardware.png",
                sort_order=2,
                caption="Деталь металевої блискавки Raccagni та нарукавної кишені патронташа",
                primary_color=(80, 80, 80),
                secondary_color=(50, 50, 50),
                pattern_type="hardware",
            ),
            SeedImageSpec(
                filename="raf_simons_aw01_riot_camo_tag.png",
                sort_order=3,
                caption="Автентична ткана бірка Raf Simons Autumn-Winter 2001-2002",
                primary_color=(230, 230, 225),
                secondary_color=(20, 20, 20),
                pattern_type="tag",
            ),
            SeedImageSpec(
                filename="raf_simons_aw01_riot_camo_back.png",
                sort_order=4,
                caption="Вигляд зі спинки з архітектурним оверсайз кроєм",
                primary_color=(55, 65, 45),
                secondary_color=(35, 42, 30),
                pattern_type="camo",
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
        interval_seconds=60,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="helmut_lang_aw99_astro_front.png",
                sort_order=0,
                caption="Фронтальний вигляд Astro Biker Jacket з коміром з овчини",
                primary_color=(215, 218, 222),
                secondary_color=(170, 175, 180),
                pattern_type="metallic",
            ),
            SeedImageSpec(
                filename="helmut_lang_aw99_astro_straps.png",
                sort_order=1,
                caption="Внутрішні бандажні стропи bondage straps та підкладка",
                primary_color=(40, 42, 45),
                secondary_color=(25, 26, 28),
                pattern_type="straps",
            ),
            SeedImageSpec(
                filename="helmut_lang_aw99_astro_hardware.png",
                sort_order=2,
                caption="Масивні металеві блискавки Lampo на кишенях та рукавах",
                primary_color=(190, 192, 195),
                secondary_color=(120, 122, 125),
                pattern_type="hardware",
            ),
            SeedImageSpec(
                filename="helmut_lang_aw99_astro_tag.png",
                sort_order=3,
                caption="Оригінальний фабричний ярлик Helmut Lang New York AW1999",
                primary_color=(245, 245, 245),
                secondary_color=(15, 15, 15),
                pattern_type="tag",
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
        interval_seconds=60,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="margiela_artisanal_painted_denim_front.png",
                sort_order=0,
                caption="Фронтальний ракурс джинсів з нашаруванням фарби bianco bianchetto",
                primary_color=(240, 240, 242),
                secondary_color=(35, 55, 95),
                pattern_type="painted",
            ),
            SeedImageSpec(
                filename="margiela_artisanal_painted_denim_crackle.png",
                sort_order=1,
                caption="Макро-ракурс вінтажного кракелюру та відлущування фарби",
                primary_color=(235, 235, 238),
                secondary_color=(45, 65, 105),
                pattern_type="painted",
            ),
            SeedImageSpec(
                filename="margiela_artisanal_painted_denim_stitches.png",
                sort_order=2,
                caption="Фірмові 4 білі стібки ручної роботи Maison Martin Margiela",
                primary_color=(30, 45, 80),
                secondary_color=(255, 255, 255),
                pattern_type="stitches",
            ),
            SeedImageSpec(
                filename="margiela_artisanal_painted_denim_tag.png",
                sort_order=3,
                caption="Текстильна бирка Artisanal Line 0 з круглим маркуванням",
                primary_color=(250, 250, 250),
                secondary_color=(20, 20, 20),
                pattern_type="tag",
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
        interval_seconds=60,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="undercover_85_denim_front.png",
                sort_order=0,
                caption="Фронтальний вигляд Undercover 85 з детальним дистресом колін",
                primary_color=(45, 50, 58),
                secondary_color=(25, 28, 32),
                pattern_type="distressed",
            ),
            SeedImageSpec(
                filename="undercover_85_denim_sashiko.png",
                sort_order=1,
                caption="Деталь ручних швів сашіко та вишитих хрестів",
                primary_color=(50, 55, 62),
                secondary_color=(200, 200, 205),
                pattern_type="distressed",
            ),
            SeedImageSpec(
                filename="undercover_85_denim_leather_patch.png",
                sort_order=2,
                caption="Шкіряні заплати та фурнітура на задніх кишенях",
                primary_color=(32, 28, 25),
                secondary_color=(60, 50, 42),
                pattern_type="leather",
            ),
            SeedImageSpec(
                filename="undercover_85_denim_tag.png",
                sort_order=3,
                caption="Автентична ткана бірка Undercover Jun Takahashi AW05",
                primary_color=(235, 235, 235),
                secondary_color=(10, 10, 10),
                pattern_type="tag",
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
        interval_seconds=60,
        status=LotStatus.ACTIVE,
        images=[
            SeedImageSpec(
                filename="rick_owens_moody_exploder_front.png",
                sort_order=0,
                caption="Фронтальний ракурс шкіряного бомбера з високим коміром",
                primary_color=(22, 22, 24),
                secondary_color=(12, 12, 14),
                pattern_type="leather",
            ),
            SeedImageSpec(
                filename="rick_owens_moody_exploder_texture.png",
                sort_order=1,
                caption="Макро-ракурс пухирчастої фактури шкіри blistered lamb",
                primary_color=(28, 28, 30),
                secondary_color=(16, 16, 18),
                pattern_type="leather",
            ),
            SeedImageSpec(
                filename="rick_owens_moody_exploder_hardware.png",
                sort_order=2,
                caption="Масивна асиметрична металева блискавка Raccagni",
                primary_color=(140, 140, 145),
                secondary_color=(70, 70, 75),
                pattern_type="hardware",
            ),
            SeedImageSpec(
                filename="rick_owens_moody_exploder_tag.png",
                sort_order=3,
                caption="Подіумна бірка Rick Owens AW14 Moody з кодом моделі",
                primary_color=(240, 240, 240),
                secondary_color=(15, 15, 15),
                pattern_type="tag",
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
                filename="yohji_yamamoto_dandies_knit_front.png",
                sort_order=0,
                caption="Фронтальний вигляд светра з драпірованим асиметричним коміром",
                primary_color=(34, 34, 38),
                secondary_color=(20, 20, 24),
                pattern_type="knit",
            ),
            SeedImageSpec(
                filename="yohji_yamamoto_dandies_knit_weave.png",
                sort_order=1,
                caption="Макро-ракурс об'ємного плетіння перуанської альпаки",
                primary_color=(42, 42, 46),
                secondary_color=(26, 26, 30),
                pattern_type="knit",
            ),
            SeedImageSpec(
                filename="yohji_yamamoto_dandies_knit_tag.png",
                sort_order=2,
                caption="Автентична ткана бирка Yohji Yamamoto Pour Homme AW2002",
                primary_color=(245, 245, 245),
                secondary_color=(10, 10, 10),
                pattern_type="tag",
            ),
        ],
    ),
]
