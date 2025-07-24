import asyncio
import os

key = b"1cK1a5UF2tU8*G2lW#&%"

def decrypt_bpc_to_zip_bytes(bpc_bytes: bytes) -> bytes:
    return bytes(bpc_bytes[i] ^ key[i % len(key)] for i in range(len(bpc_bytes)))

async def async_convert_bpc_to_zip(bpc_bytes: bytes) -> bytes:
    zip_data = await asyncio.to_thread(decrypt_bpc_to_zip_bytes, bpc_bytes)
    return zip_data

async def async_convert_and_save_bpc(bpc_bytes: bytes, filename: str, output_folder: str = None) -> tuple[bytes, str]:
    zip_data = await async_convert_bpc_to_zip(bpc_bytes)
    zip_filename = filename.replace(".bpc", ".zip")
    return zip_data, zip_filename

def write_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)
