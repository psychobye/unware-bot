import json
import re

def dat_to_json(dat_bytes: bytes) -> bytes:
    text = dat_bytes.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    data_entries = []
    current_block = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith(";") or line.startswith("//"):
            continue
        current_block.append(line)
    
    for line in current_block:
        parts = re.split(r"\s+", line)
        if len(parts) < 49:
            print(f"[warn] short line ({len(parts)} parts), skipping: {line}")
            continue

        entry = {}

        def to_int_list(start, count):
            return list(map(int, parts[start:start+count]))

        def to_float_list(start, count):
            return list(map(float, parts[start:start+count]))

        entry["AmbientRGB"]       = to_int_list(0, 3)
        entry["AmbientPhysicalRGB"] = to_int_list(3, 3)
        entry["DirectionalRGB"]   = to_int_list(6, 3)
        entry["SkyTopRGB"]        = to_int_list(9, 3)
        entry["SkyBottomRGB"]     = to_int_list(12, 3)
        entry["SunCoreRGB"]       = to_int_list(15, 3)
        entry["SunCoronaRGB"]     = to_int_list(18, 3)

        entry["SunSize"]          = float(parts[21])
        entry["SpriteSize"]       = float(parts[22])
        entry["SpriteBrght"]      = float(parts[23])

        entry["Shad"]             = int(parts[24])
        entry["LightShad"]        = int(parts[25])
        entry["PoleShad"]         = int(parts[26])

        entry["FarClip"]          = float(parts[27])
        entry["FogStart"]         = float(parts[28])
        entry["LightGnd"]         = float(parts[29])

        entry["FluffyBottomRGB"]  = to_int_list(30, 3)
        entry["CloudRGB"]         = to_int_list(33, 3)

        entry["WaterRGBA"]        = to_float_list(36, 4)

        entry["PostFX1ARGB"]      = to_int_list(40, 4)
        entry["PostFX2ARGB"]      = to_int_list(44, 4)

        data_entries.append(entry)

    result_json = json.dumps([data_entries], indent=2)
    return result_json.encode("utf-8")
