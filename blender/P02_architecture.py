"""
P02_architecture.py — EMERALD-SCARLATE NORDESTE
Reexecuta o gerador do P01 com refinamentos arquitetônicos do P02.
Uso: abrir no Text Editor do Blender 5.2 LTS e executar (Alt+P).
"""
import bpy, math, os

# ---------- Resolução segura do PROJECT_ROOT (patched P01) ----------
def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        if os.path.basename(p).lower() == "blender":
            return os.path.dirname(p)
        return p
    env = os.environ.get("EMERALD_ROOT")
    if env and os.path.isdir(env):
        return env
    home = os.path.expanduser("~")
    for c in (
        os.path.join(home, "Desktop", "EMERALD-SCHOOL"),
        os.path.join(home, "Documents", "EMERALD-SCHOOL"),
        os.path.join(home, "OneDrive", "Desktop", "EMERALD-SCHOOL"),
        os.path.join(home, "OneDrive", "Documents", "EMERALD-SCHOOL"),
        os.path.join(home, "EMERALD-SCHOOL"),
    ):
        if os.path.isdir(c):
            return c
    desktop = os.path.join(home, "Desktop")
    return os.path.join(desktop if os.path.isdir(desktop) else home, "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
print(f"[EMERALD] PROJECT_ROOT = {PROJECT_ROOT}")
GLB_OUT   = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")
for d in (os.path.dirname(GLB_OUT), os.path.dirname(BLEND_OUT)):
    os.makedirs(d, exist_ok=True)

WALL_T   = 0.15
DOOR_W   = 0.90
DOOR_H   = 2.10
WIN_SILL = 0.90
WIN_TOP  = 2.10
ROOT_NAME = "EMERALD_GENERATED"

# ---------- Pré-verificações ----------
def check_environment():
    v = bpy.app.version
    print(f"[EMERALD] Blender {v[0]}.{v[1]}.{v[2]}")
    if v[0] < 5 or (v[0] == 5 and v[1] < 2):
        raise RuntimeError("Blender 5.2+ exigido.")
    if not hasattr(bpy.ops.export_scene, "gltf"):
        raise RuntimeError("Habilite Preferences → Add-ons → glTF 2.0.")
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    if rna is None:
        raise RuntimeError("Operador glTF sem RNA.")
    print("[EMERALD] Exportador glTF OK.")

# ---------- Cleanup idempotente ----------
def cleanup():
    coll = bpy.data.collections.get(ROOT_NAME)
    if coll:
        for obj in list(coll.all_objects):
            try: bpy.data.objects.remove(obj, do_unlink=True)
            except Exception: pass
        for sub in list(coll.children_recursive):
            try: bpy.data.collections.remove(sub)
            except Exception: pass
        try: bpy.data.collections.remove(coll)
        except Exception: pass
    for m in list(bpy.data.materials):
        if m.name.startswith("EM_"):
            try: bpy.data.materials.remove(m)
            except Exception: pass
    print("[EMERALD] Cleanup OK.")

# ---------- Materiais ----------
_MATS = {}
def mat(name, rgb, rough=0.8, metal=0.0, alpha=1.0):
    if name in _MATS: return _MATS[name]
    m = bpy.data.materials.new(f"EM_{name}")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out: nt.links.new(bsdf.outputs[0], out.inputs[0])
    def _s(k, v):
        if k in bsdf.inputs: bsdf.inputs[k].default_value = v
    _s("Base Color", (*rgb, 1.0)); _s("Roughness", rough); _s("Metallic", metal)
    if alpha < 1.0:
        _s("Alpha", alpha); m.blend_method = "BLEND"
    _MATS[name] = m
    return m

MATS = {
    "floor_beige":  lambda: mat("floor_beige",  (0.86,0.80,0.70), 0.55),
    "floor_class":  lambda: mat("floor_class",  (0.82,0.72,0.55), 0.65),
    "floor_berc":   lambda: mat("floor_berc",   (0.99,0.99,0.99), 0.65),
    "floor_wc":     lambda: mat("floor_wc",     (0.62,0.64,0.66), 0.55),
    "floor_cafe":   lambda: mat("floor_cafe",   (0.75,0.80,0.82), 0.55),
    "wall_yellow":  lambda: mat("wall_yellow",  (0.96,0.82,0.25), 0.85),
    "wall_white":   lambda: mat("wall_white",   (0.97,0.97,0.97), 0.85),
    "wall_blue":    lambda: mat("wall_blue",    (0.52,0.76,0.91), 0.85),
    "wall_rose":    lambda: mat("wall_rose",    (0.96,0.72,0.69), 0.85),
    "wall_green":   lambda: mat("wall_green",   (0.32,0.75,0.50), 0.85),
    "wall_wc":      lambda: mat("wall_wc",      (0.92,0.94,0.95), 0.35),
    "roof_tile":    lambda: mat("roof_tile",    (0.72,0.26,0.20), 0.75),
    "roof_metal":   lambda: mat("roof_metal",   (0.78,0.78,0.80), 0.45, 0.6),
    "column":       lambda: mat("column",       (0.90,0.90,0.90), 0.55),
    "column_accent":lambda: mat("column_accent",(0.95,0.55,0.20), 0.65),
    "door_wood":    lambda: mat("door_wood",    (0.52,0.36,0.22), 0.70),
    "door_frame":   lambda: mat("door_frame",   (0.92,0.92,0.92), 0.60),
    "door_metal":   lambda: mat("door_metal",   (0.55,0.60,0.65), 0.40, 0.7),
    "glass":        lambda: mat("glass",        (0.72,0.86,0.95), 0.05, 0.0, 0.35),
    "ground":       lambda: mat("ground",       (0.55,0.68,0.35), 0.95),
    "patio_rubber": lambda: mat("patio_rubber", (0.78,0.30,0.28), 0.85),
    "invisible":    lambda: mat("invisible",    (1.00,0.00,1.00), 1.0),
}

# ---------- Coleções ----------
ROOT_COLL = None
SUBS = {}
def init_collections():
    global ROOT_COLL
    ROOT_COLL = bpy.data.collections.get(ROOT_NAME) or bpy.data.collections.new(ROOT_NAME)
    if ROOT_COLL.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(ROOT_COLL)
    for n in ["SITE","FLOORS","WALLS","DOORS","WINDOWS","ROOFS","STRUCTURE","COLLIDERS","CAMERAS","LIGHTING"]:
        full = f"{ROOT_NAME}_{n}"
        c = bpy.data.collections.get(full) or bpy.data.collections.new(full)
        if c.name not in ROOT_COLL.children:
            ROOT_COLL.children.link(c)
        SUBS[n] = c

# ---------- Helpers geométricos ----------
def make_box(name, center, size, material, collection):
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
             (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    me = bpy.data.meshes.new(name + "_mesh"); me.from_pydata(verts,[],faces); me.update()
    o = bpy.data.objects.new(name, me); o.location = center
    o.data.materials.append(material); collection.objects.link(o)
    return o

def make_mesh_data(name, verts, faces, material, collection, loc=(0,0,0)):
    me = bpy.data.meshes.new(name + "_mesh"); me.from_pydata(verts,[],faces); me.update()
    o = bpy.data.objects.new(name, me); o.location = loc
    o.data.materials.append(material); collection.objects.link(o)
    return o

def add_collider(name, center, size):
    o = make_box(name, center, size, MATS["invisible"](), SUBS["COLLIDERS"])
    o.display_type = "WIRE"; o.hide_render = True
    return o

# ---------- Muros com aberturas ----------
DOORS_CREATED = []

def build_wall_along_x(name, x1, x2, y, height, openings):
    wall_mat = MATS["wall_yellow"]()
    sorted_ops = sorted(openings, key=lambda o: o["pos"])
    cursor, idx = x1, 0
    for op in sorted_ops:
        op_start = x1 + op["pos"] - op["width"]/2
        op_end   = x1 + op["pos"] + op["width"]/2
        if op_start > cursor + 1e-4:
            w = op_start - cursor; cx = (cursor + op_start)/2
            make_box(f"{name}_S{idx}", (cx, y, height/2), (w, WALL_T, height),
                     wall_mat, SUBS["WALLS"])
            add_collider(f"COLLIDER_{name}_S{idx}", (cx, y, height/2), (w, WALL_T, height))
        cx_op = (op_start + op_end)/2
        if op["type"] == "door":
            header_h = height - DOOR_H
            if header_h > 1e-3:
                make_box(f"{name}_HDR{idx}", (cx_op, y, (DOOR_H + height)/2),
                         (op["width"], WALL_T, header_h), wall_mat, SUBS["WALLS"])
            DOORS_CREATED.append({
                "id": f"{name}_D{idx}",
                "hinge_x": op_start, "hinge_y": y,
                "leaf_w": op["width"], "swing": op.get("swing", 1),
            })
        elif op["type"] == "window":
            if WIN_SILL > 1e-3:
                make_box(f"{name}_SILL{idx}", (cx_op, y, WIN_SILL/2),
                         (op["width"], WALL_T, WIN_SILL), wall_mat, SUBS["WALLS"])
            hdr = height - WIN_TOP
            if hdr > 1e-3:
                make_box(f"{name}_WHDR{idx}", (cx_op, y, (WIN_TOP+height)/2),
                         (op["width"], WALL_T, hdr), wall_mat, SUBS["WALLS"])
            make_box(f"{name}_GLASS{idx}", (cx_op, y, (WIN_SILL+WIN_TOP)/2),
                     (op["width"]-0.10, 0.02, (WIN_TOP-WIN_SILL)-0.10),
                     MATS["glass"](), SUBS["WINDOWS"])
            add_collider(f"COLLIDER_{name}_WIN{idx}", (cx_op, y, height/2),
                         (op["width"], WALL_T, height))
        cursor = op_end; idx += 1
    if cursor < x2 - 1e-4:
        w = x2 - cursor; cx = (cursor + x2)/2
        make_box(f"{name}_SEND", (cx, y, height/2), (w, WALL_T, height),
                 wall_mat, SUBS["WALLS"])
        add_collider(f"COLLIDER_{name}_SEND", (cx, y, height/2), (w, WALL_T, height))

def build_wall_along_y(name, y1, y2, x, height, openings):
    wall_mat = MATS["wall_yellow"]()
    sorted_ops = sorted(openings, key=lambda o: o["pos"])
    cursor, idx = y1, 0
    for op in sorted_ops:
        op_start = y1 + op["pos"] - op["width"]/2
        op_end   = y1 + op["pos"] + op["width"]/2
        if op_start > cursor + 1e-4:
            w = op_start - cursor; cy = (cursor + op_start)/2
            make_box(f"{name}_S{idx}", (x, cy, height/2), (WALL_T, w, height),
                     wall_mat, SUBS["WALLS"])
            add_collider(f"COLLIDER_{name}_S{idx}", (x, cy, height/2), (WALL_T, w, height))
        cy_op = (op_start + op_end)/2
        if op["type"] == "window":
            make_box(f"{name}_SILL{idx}", (x, cy_op, WIN_SILL/2),
                     (WALL_T, op["width"], WIN_SILL), wall_mat, SUBS["WALLS"])
            hdr = height - WIN_TOP
            if hdr > 1e-3:
                make_box(f"{name}_WHDR{idx}", (x, cy_op, (WIN_TOP+height)/2),
                         (WALL_T, op["width"], hdr), wall_mat, SUBS["WALLS"])
            make_box(f"{name}_GLASS{idx}", (x, cy_op, (WIN_SILL+WIN_TOP)/2),
                     (0.02, op["width"]-0.10, (WIN_TOP-WIN_SILL)-0.10),
                     MATS["glass"](), SUBS["WINDOWS"])
            add_collider(f"COLLIDER_{name}_WIN{idx}", (x, cy_op, height/2),
                         (WALL_T, op["width"], height))
        elif op["type"] == "door":
            hdr = height - DOOR_H
            if hdr > 1e-3:
                make_box(f"{name}_HDR{idx}", (x, cy_op, (DOOR_H+height)/2),
                         (WALL_T, op["width"], hdr), wall_mat, SUBS["WALLS"])
        cursor = op_end; idx += 1
    if cursor < y2 - 1e-4:
        w = y2 - cursor; cy = (cursor + y2)/2
        make_box(f"{name}_SEND", (x, cy, height/2), (WALL_T, w, height),
                 wall_mat, SUBS["WALLS"])
        add_collider(f"COLLIDER_{name}_SEND", (x, cy, height/2), (WALL_T, w, height))

# ---------- Portas ----------
def build_door_frame(door_id, hinge_x, hinge_y, leaf_w, along_x, height):
    """Batente visível (só estética)."""
    frame_mat = MATS["door_frame"]()
    ft = 0.06
    cx = hinge_x + leaf_w/2
    if along_x:
        # montantes
        for sx in (hinge_x, hinge_x + leaf_w):
            make_box(f"FRAME_{door_id}_{int(sx*100)}",
                     (sx, hinge_y, (DOOR_H + ft)/2),
                     (ft, WALL_T + 0.02, DOOR_H + ft),
                     frame_mat, SUBS["DOORS"])
        make_box(f"FRAME_{door_id}_TOP",
                 (cx, hinge_y, DOOR_H + ft/2),
                 (leaf_w + ft*2, WALL_T + 0.02, ft),
                 frame_mat, SUBS["DOORS"])

def build_door_leaf(door_id, hinge_x, hinge_y, leaf_w, swing, along_x=True, height=3.0):
    build_door_frame(door_id, hinge_x, hinge_y, leaf_w, along_x, height)

    pivot = bpy.data.objects.new(f"DOOR_PIVOT_{door_id}", None)
    pivot.empty_display_type = "ARROWS"; pivot.empty_display_size = 0.4
    pivot.location = (hinge_x, hinge_y, 0.0)
    SUBS["DOORS"].objects.link(pivot)
    pivot["emerald_kind"] = "door_pivot"
    pivot["emerald_swing"] = float(swing)
    pivot["emerald_door_id"] = door_id

    leaf = make_box(f"DOOR_LEAF_{door_id}", (0,0,0),
                    (leaf_w, 0.05, DOOR_H - 0.05),
                    MATS["door_wood"](), SUBS["DOORS"])
    leaf.location = (leaf_w/2, 0, (DOOR_H - 0.05)/2)
    leaf.parent = pivot

    coll = add_collider(f"COLLIDER_DOOR_{door_id}",
                        (hinge_x + leaf_w/2, hinge_y, (DOOR_H - 0.05)/2),
                        (leaf_w, 0.20, DOOR_H - 0.05))
    coll["emerald_kind"] = "door_collider"
    coll["emerald_door_id"] = door_id

# ---------- Salas ----------
ROOMS = [
    ("SPC_CLASS_01",  1,  8,  0.9,  7.9, 3.0, "S", "floor_class", "wall_blue"),
    ("SPC_CLASS_02",  8, 15,  0.9,  7.9, 3.0, "S", "floor_class", "wall_blue"),
    ("SPC_CLASS_03", 15, 22,  0.9,  7.9, 3.0, "S", "floor_class", "wall_blue"),
    ("SPC_CLASS_04", 22, 29,  0.9,  7.9, 3.0, "S", "floor_class", "wall_blue"),
    ("SPC_MULTI",    29, 37,  0.9,  6.9, 3.0, "S", "floor_class", "wall_green"),
    ("SPC_BERC_01",   1,  7, -6.9, -0.9, 3.0, "N", "floor_berc",  "wall_rose"),
    ("SPC_BERC_02",   7, 13, -6.9, -0.9, 3.0, "N", "floor_berc",  "wall_rose"),
    ("SPC_WC_01",    13, 16, -3.4, -0.9, 2.8, "N", "floor_wc",    "wall_wc"),
    ("SPC_WC_02",    16, 19, -3.4, -0.9, 2.8, "N", "floor_wc",    "wall_wc"),
    ("SPC_KITCHEN",  19, 24, -4.9, -0.9, 3.0, "N", "floor_wc",    "wall_wc"),
    ("SPC_CAFE",     24, 32, -6.9, -0.9, 3.0, "N", "floor_cafe",  "wall_green"),
]

def build_rooms():
    first_x = {"N": None, "S": None}
    for rid, x1, x2, y1, y2, h, corr, fmat, _w in ROOMS:
        make_box(f"FLOOR_{rid}", ((x1+x2)/2, (y1+y2)/2, -0.05),
                 (x2-x1, y2-y1, 0.10), MATS[fmat](), SUBS["FLOORS"])

        cx_door = (x1 + x2)/2
        win_w = min(2.0, (x2-x1)*0.5)

        if corr == "S":
            build_wall_along_x(f"WALL_{rid}_S", x1, x2, y1, h,
                               [{"type":"door","pos":cx_door-x1,"width":DOOR_W,"swing":+1}])
            build_wall_along_x(f"WALL_{rid}_N", x1, x2, y2, h,
                               [{"type":"window","pos":cx_door-x1,"width":win_w}])
        else:
            build_wall_along_x(f"WALL_{rid}_N", x1, x2, y2, h,
                               [{"type":"door","pos":cx_door-x1,"width":DOOR_W,"swing":-1}])
            build_wall_along_x(f"WALL_{rid}_S", x1, x2, y1, h,
                               [{"type":"window","pos":cx_door-x1,"width":win_w}])

        # paredes leste/oeste (com janelas nas exteriores)
        west_ext = (first_x[corr] is None)
        if west_ext:
            build_wall_along_y(f"WALL_{rid}_W", y1, y2, x1, h,
                               [{"type":"window","pos":(y1+y2)/2-y1,
                                 "width":min(1.4, (y2-y1)*0.4)}])
            first_x[corr] = rid
        else:
            build_wall_along_y(f"WALL_{rid}_W", y1, y2, x1, h, [])

        # Leste: exterior só para o ÚLTIMO da fileira
        is_last = rid in ("SPC_MULTI", "SPC_CAFE")
        if is_last:
            build_wall_along_y(f"WALL_{rid}_E", y1, y2, x2, h,
                               [{"type":"window","pos":(y1+y2)/2-y1,
                                 "width":min(1.4, (y2-y1)*0.4)}])
        else:
            build_wall_along_y(f"WALL_{rid}_E", y1, y2, x2, h, [])

# ---------- Corredor ----------
def build_corridor():
    make_box("FLOOR_CORRIDOR", (19, 0, -0.05), (36, 1.8, 0.10),
             MATS["floor_beige"](), SUBS["FLOORS"])
    make_box("CEIL_CORRIDOR", (19, 0, 2.85), (36, 1.8, 0.10),
             MATS["wall_white"](), SUBS["ROOFS"])

# ---------- Pátio ----------
def build_patio():
    px1, px2 = 2.0, 14.0
    py1, py2 = 8.5, 14.5
    make_box("FLOOR_PATIO", ((px1+px2)/2, (py1+py2)/2, -0.05),
             (px2-px1, py2-py1, 0.10), MATS["patio_rubber"](), SUBS["FLOORS"])
    col_h = 3.5
    for i, (cx, cy) in enumerate([
        (px1+0.2, py1+0.2), (px2-0.2, py1+0.2),
        (px1+0.2, py2-0.2), (px2-0.2, py2-0.2),
        ((px1+px2)/2, py1+0.2), ((px1+px2)/2, py2-0.2)]):
        make_box(f"COLUMN_PATIO_{i+1:02d}", (cx, cy, col_h/2),
                 (0.20, 0.20, col_h), MATS["column"](), SUBS["STRUCTURE"])
        add_collider(f"COLLIDER_COL_PATIO_{i+1:02d}",
                     (cx, cy, col_h/2), (0.20, 0.20, col_h))
    make_box("ROOF_PATIO", ((px1+px2)/2, (py1+py2)/2, col_h + 0.10),
             (px2-px1+0.4, py2-py1+0.4, 0.10), MATS["glass"](), SUBS["ROOFS"])

# ---------- Telhado ----------
def build_roof():
    xmin, xmax = 0.5, 37.5
    y_s, y_n = -8.4, 9.4
    z_eave = 3.10
    y_ridge, z_ridge = 0.5, 4.50
    t = 0.15
    mr = MATS["roof_tile"]()

    v_s = [(xmin,y_s,z_eave),(xmax,y_s,z_eave),(xmax,y_ridge,z_ridge),(xmin,y_ridge,z_ridge),
           (xmin,y_s,z_eave-t),(xmax,y_s,z_eave-t),(xmax,y_ridge,z_ridge-t),(xmin,y_ridge,z_ridge-t)]
    f = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    make_mesh_data("ROOF_SOUTH", v_s, f, mr, SUBS["ROOFS"])

    v_n = [(xmin,y_ridge,z_ridge),(xmax,y_ridge,z_ridge),(xmax,y_n,z_eave),(xmin,y_n,z_eave),
           (xmin,y_ridge,z_ridge-t),(xmax,y_ridge,z_ridge-t),(xmax,y_n,z_eave-t),(xmin,y_n,z_eave-t)]
    make_mesh_data("ROOF_NORTH", v_n, f, mr, SUBS["ROOFS"])

    make_box("ROOF_RIDGE", ((xmin+xmax)/2, y_ridge, z_ridge),
             (xmax-xmin, 0.20, 0.10), mr, SUBS["ROOFS"])

# ---------- P02: Pórtico de entrada + Marquise ----------
def build_entrance_portico():
    """Pórtico na face oeste (x=1), sobre a abertura do corredor (y=0).
       Dois pilares (y=-2.2 e y=+2.2) + lintel + marquise plana."""
    px = -0.3                # ligeiramente à frente da fachada
    col_h = 3.6
    pillar_w = 0.35
    for i, cy in enumerate([-2.2, 2.2]):
        make_box(f"COLUMN_ENTRY_{i+1:02d}", (px, cy, col_h/2),
                 (pillar_w, pillar_w, col_h),
                 MATS["column_accent"](), SUBS["STRUCTURE"])
        add_collider(f"COLLIDER_COL_ENTRY_{i+1:02d}",
                     (px, cy, col_h/2), (pillar_w, pillar_w, col_h))
    # Lintel (viga superior)
    make_box("BEAM_ENTRY", (px, 0, col_h + 0.15),
             (pillar_w + 0.05, 4.9, 0.30),
             MATS["column_accent"](), SUBS["STRUCTURE"])
    # Marquise plana, estendendo 2.8m para fora
    make_box("MARQUISE_ENTRY", (px - 1.4, 0, col_h + 0.35),
             (3.2, 5.2, 0.12), MATS["roof_metal"](), SUBS["ROOFS"])
    # Colunas extras da marquise (lado externo)
    for i, cy in enumerate([-2.2, 2.2]):
        make_box(f"COLUMN_MARQ_{i+1:02d}", (px - 2.8, cy, col_h/2),
                 (pillar_w, pillar_w, col_h),
                 MATS["column_accent"](), SUBS["STRUCTURE"])
        add_collider(f"COLLIDER_COL_MARQ_{i+1:02d}",
                     (px - 2.8, cy, col_h/2), (pillar_w, pillar_w, col_h))

# ---------- Site ----------
def build_site():
    make_box("SITE_TERRAIN", (19, 0, -0.10), (120, 100, 0.10),
             MATS["ground"](), SUBS["SITE"])
    # Calçada de entrada (mais larga no P02)
    make_box("SITE_ENTRY_W", (-3.5, 0, -0.08), (9, 4.4, 0.06),
             MATS["floor_beige"](), SUBS["SITE"])

# ---------- Câmeras / luzes ----------
def build_cameras_and_lights():
    cd = bpy.data.cameras.new("CAM_EXTERNAL"); cd.lens = 35
    c = bpy.data.objects.new("CAM_EXTERNAL", cd)
    c.location = (-25, -25, 18)
    c.rotation_euler = (math.radians(60), 0, math.radians(-45))
    SUBS["CAMERAS"].objects.link(c)

    cd2 = bpy.data.cameras.new("CAM_INTERNAL"); cd2.lens = 24
    c2 = bpy.data.objects.new("CAM_INTERNAL", cd2)
    c2.location = (1.0, 0, 1.7)
    c2.rotation_euler = (math.radians(90), 0, math.radians(90))
    SUBS["CAMERAS"].objects.link(c2)
    bpy.context.scene.camera = c

    sd = bpy.data.lights.new("SUN_NORDESTE", type="SUN")
    sd.energy = 3.5; sd.color = (1.0, 0.957, 0.878)
    s = bpy.data.objects.new("SUN_NORDESTE", sd)
    s.location = (30, 40, 50)
    s.rotation_euler = (math.radians(45), 0, math.radians(30))
    SUBS["LIGHTING"].objects.link(s)

    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = w; w.use_nodes = True
    bg = next((n for n in w.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg:
        bg.inputs["Color"].default_value = (0.75, 0.85, 0.95, 1.0)
        bg.inputs["Strength"].default_value = 1.0

# ---------- Exportação ----------
def export_glb():
    for o in bpy.context.selected_objects:
        o.select_set(False)
    count = 0
    for o in ROOT_COLL.all_objects:
        if o.type in {"MESH", "EMPTY"}:
            o.select_set(True); count += 1
    if count == 0:
        raise RuntimeError("Nada para exportar.")
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    supported = {p.identifier for p in rna.properties}
    kw = dict(filepath=GLB_OUT, export_format="GLB",
              use_selection=True, export_yup=True,
              export_apply=False, export_animations=False)
    if "export_extras" in supported:    kw["export_extras"] = True
    if "export_materials" in supported: kw["export_materials"] = "EXPORT"
    if "export_cameras" in supported:   kw["export_cameras"] = False
    if "export_lights" in supported:    kw["export_lights"] = False
    bpy.ops.export_scene.gltf(**kw)
    if not os.path.exists(GLB_OUT) or os.path.getsize(GLB_OUT) == 0:
        raise RuntimeError("GLB não gerado.")
    size_mb = os.path.getsize(GLB_OUT) / (1024*1024)
    print(f"[EMERALD] GLB: {GLB_OUT} ({size_mb:.2f} MB, {count} objetos)")

# ---------- MAIN ----------
def main():
    check_environment()
    cleanup()
    init_collections()
    build_site()
    build_corridor()
    build_rooms()
    build_patio()
    build_roof()
    build_entrance_portico()          # NOVO P02
    build_cameras_and_lights()

    # Folhas + batentes
    for d in DOORS_CREATED:
        build_door_leaf(d["id"], d["hinge_x"], d["hinge_y"],
                        d["leaf_w"], d["swing"], along_x=True, height=3.0)
    print(f"[EMERALD] Portas criadas: {len(DOORS_CREATED)}")

    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[EMERALD] Blend salvo: {BLEND_OUT}")
    print("[EMERALD] P02 concluído.")

if __name__ == "__main__":
    main()