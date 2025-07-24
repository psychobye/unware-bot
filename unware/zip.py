import asyncio
import os

key = b"1cK1a5UF2tU8*G2lW#&%"

def write_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)

def encrypt_zip_to_bpc_bytes(zip_bytes: bytes) -> bytes:
    return bytes(zip_bytes[i] ^ key[i % len(key)] for i in range(len(zip_bytes)))

async def async_convert_zip_to_bpc(zip_bytes: bytes) -> bytes:
    return await asyncio.to_thread(encrypt_zip_to_bpc_bytes, zip_bytes)

async def async_convert_and_save_zip(zip_bytes: bytes, filename: str, output_folder: str = None) -> tuple[bytes, str]:
    bpc_data = await async_convert_zip_to_bpc(zip_bytes)
    bpc_filename = filename.replace(".zip", ".bpc")
    if output_folder:
        path = os.path.join(output_folder, bpc_filename)
        await asyncio.to_thread(write_file, path, bpc_data)
    return bpc_data, bpc_filename
