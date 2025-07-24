import os
import struct
import asyncio
from config import DFF_PATH

os.makedirs(DFF_PATH, exist_ok=True)

def ror32(x, r):
    return ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF

def tea_decrypt_block(data, key, rounds=8):
    delta = 0x61C88647
    for offset in range(0, len(data), 8):
        v0, v1 = struct.unpack_from('<II', data, offset)
        sum_val = (-delta * rounds) & 0xFFFFFFFF
        for _ in range(rounds):
            v1 = (v1 - ((v0 + sum_val) ^ (key[3] + (v0 >> 5)) ^ (key[2] + (v0 << 4)))) & 0xFFFFFFFF
            new_sum = (sum_val + v1) & 0xFFFFFFFF
            sum_val = (sum_val + delta) & 0xFFFFFFFF
            v0 = (v0 - (new_sum ^ (key[0] + (v1 << 4)) ^ (key[1] + (v1 >> 5)))) & 0xFFFFFFFF
        struct.pack_into('<II', data, offset, v0, v1)

def decrypt_mod_to_dff(mod_bytes):
    magic, length, num_blocks = struct.unpack_from('<III', mod_bytes, 0)
    if magic != 0xAB921033:
        raise ValueError("invalid .mod file")
    base_key = [0x6ED9EE7A, 0x930C666B, 0x930E166B, 0x4709EE79]
    key = [ror32(k ^ 0x12913AFB, 19) for k in base_key]
    data = bytearray(mod_bytes)
    offset = 28
    for i in range(num_blocks):
        block = data[offset : offset + 0x800]
        tea_decrypt_block(block, key, rounds=8)
        data[offset : offset + 0x800] = block
        offset += 0x800
    return bytes(data[28 : 28 + length])

def convert_mod_to_dff_bytes(mod_bytes: bytes, filename: str) -> tuple[bytes, str]:
    dff_data = decrypt_mod_to_dff(mod_bytes)
    dff_filename = filename.replace(".mod", ".dff")
    return dff_data, dff_filename

def write_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)

async def async_convert_and_save(mod_bytes: bytes, filename: str, output_folder: str = None) -> tuple[bytes, str]:
    dff_data, dff_filename = await asyncio.to_thread(convert_mod_to_dff_bytes, mod_bytes, filename)
    return dff_data, dff_filename
    