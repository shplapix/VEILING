import struct
import zlib
from typing import Literal

PatternType = Literal[
    "camo",
    "metallic",
    "painted",
    "distressed",
    "leather",
    "knit",
    "hardware",
    "straps",
    "tag",
    "plain",
]


def _clamp(val: int) -> int:
    return max(0, min(255, val))


def generate_png_image(
    width: int = 400,
    height: int = 400,
    primary_color: tuple[int, int, int] = (20, 20, 20),
    secondary_color: tuple[int, int, int] = (40, 40, 40),
    pattern_type: PatternType | str = "plain",
) -> bytes:
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data))

    p_r, p_g, p_b = primary_color
    s_r, s_g, s_b = secondary_color

    rows: list[bytes] = []

    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            if pattern_type == "camo":
                factor = ((x * 7 + y * 13) ^ (x * 3 + y * 5)) % 100
                if factor < 45:
                    r, g, b = p_r, p_g, p_b
                elif factor < 80:
                    r, g, b = s_r, s_g, s_b
                else:
                    mid_r = (p_r + s_r) // 2 + 15
                    mid_g = (p_g + s_g) // 2 + 10
                    mid_b = (p_b + s_b) // 2 + 5
                    r, g, b = _clamp(mid_r), _clamp(mid_g), _clamp(mid_b)
            elif pattern_type == "metallic":
                grad = ((x + y * 2) % 60) - 30
                r = _clamp(p_r + grad)
                g = _clamp(p_g + grad)
                b = _clamp(p_b + grad)
            elif pattern_type == "painted":
                crackle = ((x * 19) ^ (y * 23)) % 100
                if crackle < 65:
                    r, g, b = p_r, p_g, p_b
                else:
                    r, g, b = s_r, s_g, s_b
            elif pattern_type == "distressed":
                stitch = (x % 30 < 2) or (y % 40 < 2)
                if stitch and (((x + y) // 10) % 2 == 0):
                    r, g, b = s_r, s_g, s_b
                else:
                    slub = (x % 5 == 0) * 8
                    r = _clamp(p_r + slub)
                    g = _clamp(p_g + slub)
                    b = _clamp(p_b + slub)
            elif pattern_type == "leather":
                grain = ((x * 11 + y * 17) % 19) - 9
                r = _clamp(p_r + grain)
                g = _clamp(p_g + grain)
                b = _clamp(p_b + grain)
            elif pattern_type == "knit":
                rib = 15 if (x // 8) % 2 == 0 else -10
                course = 8 if (y // 4) % 2 == 0 else -5
                r = _clamp(p_r + rib + course)
                g = _clamp(p_g + rib + course)
                b = _clamp(p_b + rib + course)
            elif pattern_type == "hardware":
                zipper = abs(x - (width // 2))
                if zipper < 4:
                    r, g, b = (220, 220, 225)
                elif zipper < 14 and (y % 8 < 4):
                    r, g, b = s_r, s_g, s_b
                else:
                    r, g, b = p_r, p_g, p_b
            elif pattern_type == "straps":
                webbing = 12 if (y % 6 < 3) else -8
                r = _clamp(p_r + webbing)
                g = _clamp(p_g + webbing)
                b = _clamp(p_b + webbing)
            elif pattern_type == "tag":
                margin = (
                    x > width * 0.15 and x < width * 0.85 and y > height * 0.2 and y < height * 0.8
                )
                text_line = margin and (y % 20 < 4) and (x < width * 0.75)
                if text_line:
                    r, g, b = s_r, s_g, s_b
                elif margin:
                    r, g, b = p_r, p_g, p_b
                else:
                    r, g, b = 235, 235, 235
            else:
                grid = ((x // 25) + (y // 25)) % 2 == 0
                r, g, b = (p_r, p_g, p_b) if grid else (s_r, s_g, s_b)

            row.extend((r, g, b))
        rows.append(bytes(row))

    raw_payload = b"".join(rows)
    idat_data = zlib.compress(raw_payload, level=6)
    idat_crc = struct.pack(">I", zlib.crc32(b"IDAT" + idat_data))
    iend_crc = struct.pack(">I", zlib.crc32(b"IEND"))

    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", len(ihdr_data))
        + b"IHDR"
        + ihdr_data
        + ihdr_crc
        + struct.pack(">I", len(idat_data))
        + b"IDAT"
        + idat_data
        + idat_crc
        + struct.pack(">I", 0)
        + b"IEND"
        + iend_crc
    )
