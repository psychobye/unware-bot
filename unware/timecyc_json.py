import json

time_labels = [
    "Midnight",
    "5AM",
    "6AM",
    "7AM",
    "Midday",
    "7PM",
    "8PM",
    "10PM"
]

def build_timecyc_line(entry):
    parts = []
    parts.append(" ".join(str(x) for x in entry["AmbientRGB"]))
    parts.append(" ".join(str(x) for x in entry["AmbientPhysicalRGB"]))
    parts.append(" ".join(str(x) for x in entry["DirectionalRGB"]))
    parts.append(" ".join(str(x) for x in entry["SkyTopRGB"]))
    parts.append(" ".join(str(x) for x in entry["SkyBottomRGB"]))
    parts.append(" ".join(str(x) for x in entry["SunCoreRGB"]))
    parts.append(" ".join(str(x) for x in entry["SunCoronaRGB"]))
    
    parts.append(f"{entry['SunSize']:.2f} {entry['SpriteSize']:.2f} {entry['SpriteBrght']:.2f}")
    parts.append(f"{entry['Shad']} {entry['LightShad']} {entry['PoleShad']}")
    parts.append(f"{entry['FarClip']:.2f} {entry['FogStart']:.2f} {entry['LightGnd']:.2f}")
    parts.append(" ".join(str(x) for x in entry["FluffyBottomRGB"]))
    parts.append(" ".join(str(x) for x in entry["CloudRGB"]))
    parts.append(" ".join(f"{int(x) if isinstance(x, float) and x.is_integer() else f'{x:.2f}'}" for x in entry["WaterRGBA"]))
    parts.append(f"{entry['PostFX1ARGB'][0]} {entry['PostFX1ARGB'][1]} {entry['PostFX1ARGB'][2]} {entry['PostFX1ARGB'][3]}")
    parts.append(f"{entry['PostFX2ARGB'][0]} {entry['PostFX2ARGB'][1]} {entry['PostFX2ARGB'][2]} {entry['PostFX2ARGB'][3]}")
    parts.append(str(entry["Shad"]))
    return "\t".join(parts)

def json_to_dat(json_bytes: bytes) -> bytes:
    json_data = json.loads(json_bytes)
    lines = []
    lines.append("; Amb         Amb_Obj    Dir         Sky top     Sky bot     SunCore     SunCorona   SunSz   SprSz   SprBght  Shdw  LightShd  PoleShd  FarClp  FogSt  LightOnGround  LowCloudsRGB  BottomCloudRGB  WaterRGBA        Alpha1    RGB1        Alpha2    RGB2        CloudAlpha")
    lines.append("")
    for i, entry in enumerate(json_data[0]):
        if i < len(time_labels):
            lines.append(f"; {time_labels[i]}")
        else:
            lines.append("; UnknownTime")
        lines.append(build_timecyc_line(entry))
    return ("\n".join(lines) + "\n").encode("utf-8")
