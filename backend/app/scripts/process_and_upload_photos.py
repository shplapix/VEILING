import asyncio
import io
from pathlib import Path

from PIL import Image

from app.core.s3 import s3_service

SOURCE_DIR = Path(r"C:\Users\malim\.gemini\antigravity\brain\f37ae63f-93ab-4e4e-a9db-1d26a0b0e76c")
FRONTEND_PUBLIC = Path(r"frontend\public\lots")

IMAGE_MAP = {
    "raf_simons_aw01_riot": "raf_simons_aw01_riot_bomber_1793905809309.jpg",
    "helmut_lang_aw99_astro": "helmut_lang_aw99_astro_front_1793905871762.jpg",
    "margiela_artisanal_painted": "margiela_artisanal_painted_front_1793905886954.jpg",
    "undercover_85_denim": "undercover_85_denim_front_1793905901314.jpg",
    "rick_owens_moody_exploder": "rick_owens_moody_exploder_front_1793905918315.jpg",
    "yohji_yamamoto_dandies_knit": "yohji_yamamoto_dandies_knit_front_1793905876355.jpg",
    "dior_homme_aw04_napoleon": "dior_homme_aw04_napoleon_front_1793905891226.jpg",
    "number_nine_aw05_hybrid": "number_nine_aw05_hybrid_front_1793905909074.jpg",
    "issey_miyake_aw96_parachute": "issey_miyake_aw96_parachute_front_1793905926470.jpg",
    "undercover_aw02_witches": "undercover_aw02_witches_front_1793905881551.jpg",
    "cdg_aw94_offbeat_humor": "cdg_aw94_offbeat_humor_front_1793905898868.jpg",
    "ccp_2010_titanium_leather": "ccp_2010_titanium_leather_front_1793905914536.jpg",
    "junya_watanabe_ss02_poem": "junya_watanabe_ss02_poem_front_1793905931022.jpg",
}


async def main() -> None:
    FRONTEND_PUBLIC.mkdir(parents=True, exist_ok=True)
    await s3_service.ensure_bucket_exists()

    uploaded_results: dict[str, list[dict[str, str]]] = {}

    for slug, source_filename in IMAGE_MAP.items():
        source_path = SOURCE_DIR / source_filename
        if not source_path.exists():
            print(f"Warning: {source_path} does not exist!")
            continue

        print(f"Processing {slug} from {source_filename}...")
        img = Image.open(source_path).convert("RGB")
        w, h = img.size

        front_io = io.BytesIO()
        img.save(front_io, format="JPEG", quality=95)
        front_bytes = front_io.getvalue()
        front_file = f"{slug}_front.jpg"
        (FRONTEND_PUBLIC / front_file).write_bytes(front_bytes)

        crop_w, crop_h = int(w * 0.55), int(h * 0.55)
        left = (w - crop_w) // 2
        top = int(h * 0.22)
        detail_img = img.crop((left, top, left + crop_w, top + crop_h))
        detail_io = io.BytesIO()
        detail_img.save(detail_io, format="JPEG", quality=95)
        detail_bytes = detail_io.getvalue()
        detail_file = f"{slug}_detail.jpg"
        (FRONTEND_PUBLIC / detail_file).write_bytes(detail_bytes)

        macro_w, macro_h = int(w * 0.38), int(h * 0.38)
        m_left = int(w * 0.30)
        m_top = int(h * 0.32)
        macro_img = img.crop((m_left, m_top, m_left + macro_w, m_top + macro_h))
        macro_io = io.BytesIO()
        macro_img.save(macro_io, format="JPEG", quality=95)
        macro_bytes = macro_io.getvalue()
        macro_file = f"{slug}_macro.jpg"
        (FRONTEND_PUBLIC / macro_file).write_bytes(macro_bytes)

        front_key, front_url = await s3_service.upload_image(
            file_data=front_bytes,
            content_type="image/jpeg",
            prefix=f"lots/{slug}_front.jpg",
        )
        detail_key, detail_url = await s3_service.upload_image(
            file_data=detail_bytes,
            content_type="image/jpeg",
            prefix=f"lots/{slug}_detail.jpg",
        )
        macro_key, macro_url = await s3_service.upload_image(
            file_data=macro_bytes,
            content_type="image/jpeg",
            prefix=f"lots/{slug}_macro.jpg",
        )

        uploaded_results[slug] = [
            {
                "filename": front_file,
                "url": front_url,
                "caption": "Фронтальний архівний ракурс експонату",
            },
            {
                "filename": detail_file,
                "url": detail_url,
                "caption": "Деталь крою, фурнітури та фактури матеріалу",
            },
            {
                "filename": macro_file,
                "url": macro_url,
                "caption": "Макро-ракурс структури полотна та автентичних швів",
            },
        ]
        print(f"Uploaded {slug}: front={front_url}")

    print(f"\nAll done! Processed {len(uploaded_results)} lots.")


if __name__ == "__main__":
    asyncio.run(main())
