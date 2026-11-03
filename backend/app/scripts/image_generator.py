import struct
import zlib


def generate_png_image(
    width: int = 400,
    height: int = 400,
    primary_color: tuple[int, int, int] = (20, 20, 20),
    secondary_color: tuple[int, int, int] = (40, 40, 40),
    pattern_type: str = "plain",
) -> bytes:
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data))

    p_r, p_g, p_b = primary_color
    s_r, s_g, s_b = secondary_color
    rows: list[bytes] = []

    for y in range(height):
        row = bytearray([0])
        for x in range(width):
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
