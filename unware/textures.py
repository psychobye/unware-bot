from struct import unpack_from
from .dff import dff, types as rw_types

def scan_textures_by_chunks(path):
    model = dff()
    with open(path, "rb") as f:
        model.data = f.read()
    model.pos = 0
    textures = []

    while model.pos < len(model.data):
        ch = model.read_chunk()
        if ch.type == rw_types["Clump"]:
            cl_end = model.pos + ch.size
            break
        model._read(ch.size)
    else:
        return []

    while model.pos < cl_end:
        gl = model.read_chunk()
        if gl.type == rw_types["Geometry List"]:
            gl_end = model.pos + gl.size
            st = model.read_chunk()
            model._read(st.size)
            while model.pos < gl_end:
                g = model.read_chunk()
                if g.type == rw_types["Geometry"]:
                    g_end = model.pos + g.size
                    while model.pos < g_end:
                        ml = model.read_chunk()
                        if ml.type == rw_types["Material List"]:
                            ml_end = model.pos + ml.size
                            sc = model.read_chunk()
                            if sc.type == rw_types["Struct"]:
                                mat_cnt = unpack_from('<I', model.data, model._read(4))[0]
                                for _ in range(mat_cnt):
                                    model._read(4)
                            else:
                                model._read(sc.size)
                            while model.pos < ml_end:
                                m = model.read_chunk()
                                if m.type == rw_types["Material"]:
                                    m_end = model.pos + m.size
                                    hdr = model.read_chunk()
                                    model._read(hdr.size)
                                    while model.pos < m_end:
                                        t = model.read_chunk()
                                        if t.type == rw_types["Texture"]:
                                            t_end = model.pos + t.size
                                            while model.pos < t_end:
                                                sub = model.read_chunk()
                                                if sub.type == rw_types["String"]:
                                                    raw = model.raw(sub.size)
                                                    name = raw.split(b'\x00', 1)[0].decode('utf-8', errors='ignore')
                                                    if name:
                                                        textures.append(name)
                                                else:
                                                    model._read(sub.size)
                                            model.pos = t_end
                                        else:
                                            model._read(t.size)
                                else:
                                    model._read(m.size)
                        else:
                            model._read(ml.size)
                else:
                    model._read(g.size)
        else:
            model._read(gl.size)

    return textures
