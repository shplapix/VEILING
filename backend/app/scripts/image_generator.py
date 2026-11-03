import struct
import zlib
from typing import Literal

PatternType = Literal[
    "camo",
    "metallic",
    "painted",
    "stitches",
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
    p_bytes = bytes((p_r, p_g, p_b))
    s_bytes = bytes((s_r, s_g, s_b))

    rows: list[bytes] = []

    if pattern_type == "camo":
        mid_r = _clamp((p_r + s_r) // 2 + 15)
        mid_g = _clamp((p_g + s_g) // 2 + 10)
        mid_b = _clamp((p_b + s_b) // 2 + 5)
        m_bytes = bytes((mid_r, mid_g, mid_b))
        for y in range(height):
            row = bytearray([0])
            for x in range(width):
                factor = ((x * 7 + y * 13) ^ (x * 3 + y * 5)) % 100
                if factor < 45:
                    row.extend(p_bytes)
                elif factor < 80:
                    row.extend(s_bytes)
                else:
                    row.extend(m_bytes)
            rows.append(bytes(row))
    elif pattern_type == "metallic":
        for y in range(height):
            row = bytearray([0])
            for x in range(width):
                grad = ((x + y * 2) % 60) - 30
                row.extend((_clamp(p_r + grad), _clamp(p_g + grad), _clamp(p_b + grad)))
            rows.append(bytes(row))
    elif pattern_type == "painted":
        for y in range(height):
            row = bytearray([0])
            for x in range(width):
                crackle = ((x * 19) ^ (y * 23)) % 100
                row.extend(p_bytes if crackle < 65 else s_bytes)
            rows.append(bytes(row))
    elif pattern_type == "stitches":
        y_tl_min, y_tl_max = int(height * 0.28), int(height * 0.31)
        y_bl_min, y_bl_max = int(height * 0.50), int(height * 0.53)
        x_left_min, x_left_max = int(width * 0.30), int(width * 0.38)
        x_right_min, x_right_max = int(width * 0.62), int(width * 0.70)
        for y in range(height):
            row = bytearray([0])
            in_top_band = y_tl_min <= y <= y_tl_max
            in_bot_band = y_bl_min <= y <= y_bl_max
            for x in range(width):
                is_stitch = (in_top_band or in_bot_band) and (
                    (x_left_min <= x <= x_left_max) or (x_right_min <= x <= x_right_max)
                )
                if is_stitch:
                    row.extend(s_bytes)
                else:
                    slub = ((x * 3 + y * 7) % 17) - 8
                    row.extend((_clamp(p_r + slub), _clamp(p_g + slub), _clamp(p_b + slub)))
            rows.append(bytes(row))
    elif pattern_type == "distressed":
        for y in range(height):
            row = bytearray([0])
            for x in range(width):
                stitch = (x % 30 < 2) or (y % 40 < 2)
                if stitch and (((x + y) // 10) % 2 == 0):
                    row.extend(s_bytes)
                else:
                    slub = (x % 5 == 0) * 8
                    row.extend((_clamp(p_r + slub), _clamp(p_g + slub), _clamp(p_b + slub)))
            rows.append(bytes(row))
    elif pattern_type == "leather":
        for y in range(height):
            row = bytearray([0])
            for x in range(width):
                grain = ((x * 11 + y * 17) % 19) - 9
                row.extend((_clamp(p_r + grain), _clamp(p_g + grain), _clamp(p_b + grain)))
            rows.append(bytes(row))
    elif pattern_type == "knit":
        for y in range(height):
            row = bytearray([0])
            course = 8 if (y // 4) % 2 == 0 else -5
            for x in range(width):
                rib = 15 if (x // 8) % 2 == 0 else -10
                total = rib + course
                row.extend((_clamp(p_r + total), _clamp(p_g + total), _clamp(p_b + total)))
            rows.append(bytes(row))
    elif pattern_type == "hardware":
        center_x = width // 2
        zipper_metal = bytes((220, 220, 225))
        for y in range(height):
            row = bytearray([0])
            y_teeth = y % 8 < 4
            for x in range(width):
                zipper = abs(x - center_x)
                if zipper < 4:
                    row.extend(zipper_metal)
                elif zipper < 14 and y_teeth:
                    row.extend(s_bytes)
                else:
                    row.extend(p_bytes)
            rows.append(bytes(row))
    elif pattern_type == "straps":
        for y in range(height):
            row = bytearray([0])
            webbing = 12 if (y % 6 < 3) else -8
            c_bytes = bytes((_clamp(p_r + webbing), _clamp(p_g + webbing), _clamp(p_b + webbing)))
            row.extend(c_bytes * width)
            rows.append(bytes(row))
    elif pattern_type == "tag":
        bg_bytes = bytes((235, 235, 235))
        x_min, x_max = int(width * 0.15), int(width * 0.85)
        y_min, y_max = int(height * 0.2), int(height * 0.8)
        text_max = int(width * 0.75)
        for y in range(height):
            row = bytearray([0])
            in_y_margin = y_min < y < y_max
            is_text_y = in_y_margin and (y % 20 < 4)
            for x in range(width):
                in_x_margin = x_min < x < x_max
                if in_y_margin and in_x_margin:
                    if is_text_y and x < text_max:
                        row.extend(s_bytes)
                    else:
                        row.extend(p_bytes)
                else:
                    row.extend(bg_bytes)
            rows.append(bytes(row))
    else:
        for y in range(height):
            row = bytearray([0])
            grid_y = (y // 25) % 2
            for x in range(width):
                grid = ((x // 25) + grid_y) % 2 == 0
                row.extend(p_bytes if grid else s_bytes)
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
