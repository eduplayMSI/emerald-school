"""
P01_school.py — EMERALD-SCARLATE NORDESTE
Gerador procedural do CMEI base (Blender 5.2 LTS).
Uso: abrir no Text Editor do Blender e executar (Run Script),
      ou: blender -b --python P01_school.py
"""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector

# -------------------------------------------------------------- #
# 0. CONFIGURAÇÃO
# -------------------------------------------------------------- #
# -------------------------------------------------------------- #
# 0. CONFIGURAÇÃO — resolução segura do diretório raiz
# -------------------------------------------------------------- #
def resolve_project_root():
    """Retorna a raiz do projeto de forma segura (sem cair em Program Files)."""
    # 1) .blend já salvo?  Usa a pasta acima de blender/
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        if os.path.basename(p).lower() == "blender":
            return os.path.dirname(p)
        return p

    # 2) Override por variável de ambiente (útil para CI)
    env = os.environ.get("EMERALD_ROOT")
    if env and os.path.isdir(env):
        return env

    # 3) Locais comuns do usuário (Desktop/Documents, incluindo OneDrive)
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Desktop", "EMERALD-SCHOOL"),
        os.path.join(home, "Documents", "EMERALD-SCHOOL"),
        os.path.join(home, "OneDrive", "Desktop", "EMERALD-SCHOOL"),
        os.path.join(home, "OneDrive", "Documents", "EMERALD-SCHOOL"),
        os.path.join(home, "EMERALD-SCHOOL"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c

    # 4) Fallback: cria em Desktop (ou home se Desktop não existir)
    desktop = os.path.join(home, "Desktop")
    base = desktop if os.path.isdir(desktop) else home
    return os.path.join(base, "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
print(f"[EMERALD] PROJECT_ROOT = {PROJECT_ROOT}")

GLB_OUT   = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")

for d in (os.path.dirname(GLB_OUT), os.path.dirname(BLEND_OUT)):
    try:
        os.makedirs(d, exist_ok=True)
    except PermissionError as e:
        raise RuntimeError(
            f"Sem permissão para criar '{d}'.\n"
            f"Solução 1: salve o .blend como 'EMERALD-SCHOOL/blender/EMERALD_SCHOOL.blend' e rode novamente.\n"
            f"Solução 2: defina a variável de ambiente EMERALD_ROOT para o caminho do projeto.\n"
            f"Erro original: {e}"
        )

# Constantes arquitetônicas
WALL_T   = 0.15
DOOR_W   = 0.90
DOOR_H   = 2.10
WIN_SILL = 0.90
WIN_TOP  = 2.10

# -------------------------------------------------------------- #
# 1. PRÉ-VERIFICAÇÕES
# -------------------------------------------------------------- #
def check_environment():
    ver = bpy.app.version
    print(f"[EMERALD] Blender {ver[0]}.{ver[1]}.{ver[2]}")
    if ver[0] < 5 or (ver[0] == 5 and ver[1] < 2):
        raise RuntimeError(f"Blender 5.2+ exigido. Encontrado: {ver}")
    if not hasattr(bpy.ops.export_scene, "gltf"):
        raise RuntimeError(
            "Exportador glTF indisponível. Habilite em "
            "Preferences → Add-ons → Import-Export: glTF 2.0"
        )
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    if rna is None:
        raise RuntimeError("Operador gltf sem RNA type — ambiente inconsistente.")
    print("[EMERALD] Exportador glTF OK.")

# -------------------------------------------------------------- #
# 2. LIMPEZA IDEMPOTENTE
# -------------------------------------------------------------- #
ROOT_NAME = "EMERALD_GENERATED"

def cleanup():
    coll = bpy.data.collections.get(ROOT_NAME)
    if coll:
        for obj in list(coll.all_objects):
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except Exception:
                pass
        # Remover sub-coleções
        for sub in list(coll.children_recursive):
            try:
                bpy.data.collections.remove(sub)
            except Exception:
                pass
        try:
            bpy.data.collections.remove(coll)
        except Exception:
            pass
    # Remover órfãos de materiais criados
    for m in list(bpy.data.materials):
        if m.name.startswith("EM_"):
            try:
                bpy.data.materials.remove(m)
            except Exception:
                pass
    print("[EMERALD] Cleanup OK.")

# -------------------------------------------------------------- #
# 3. MATERIAIS
# -------------------------------------------------------------- #
_MATS = {}
def mat(name, rgb, rough=0.8, metal=0.0, alpha=1.0):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(f"EM_{name}")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out:
            nt.links.new(bsdf.outputs[0], out.inputs[0])
    def _set(sock, val):
        if sock in bsdf.inputs:
            bsdf.inputs[sock].default_value = val
    _set("Base Color", (*rgb, 1.0))
    _set("Roughness", rough)
    _set("Metallic", metal)
    if alpha < 1.0:
        _set("Alpha", alpha)
        m.blend_method = "BLEND"
    _MATS[name] = m
    return m

MATS = {
    "floor_beige":   lambda: mat("floor_beige",   (0.86, 0.80, 0.70), 0.55),
    "floor_class":   lambda: mat("floor_class",   (0.82, 0.72, 0.55), 0.65),
    "floor_berc":    lambda: mat("floor_berc",    (0.99, 0.99, 0.99), 0.65),
    "floor_wc":      lambda: mat("floor_wc",      (0.62, 0.64, 0.66), 0.55),
    "floor_cafe":    lambda: mat("floor_cafe",    (0.75, 0.80, 0.82), 0.55),
    "wall_yellow":   lambda: mat("wall_yellow",   (0.96, 0.82, 0.25), 0.85),
    "wall_white":    lambda: mat("wall_white",    (0.97, 0.97, 0.97), 0.85),
    "wall_blue":     lambda: mat("wall_blue",     (0.52, 0.76, 0.91), 0.85),
    "wall_rose":     lambda: mat("wall_rose",     (0.96, 0.72, 0.69), 0.85),
    "wall_green":    lambda: mat("wall_green",    (0.32, 0.75, 0.50), 0.85),
    "wall_wc":       lambda: mat("wall_wc",       (0.92, 0.94, 0.95), 0.35),
    "roof_tile":     lambda: mat("roof_tile",     (0.72, 0.26, 0.20), 0.75),
    "roof_metal":    lambda: mat("roof_metal",    (0.78, 0.78, 0.80), 0.45, 0.6),
    "column":        lambda: mat("column",        (0.90, 0.90, 0.90), 0.55),
    "door_wood":     lambda: mat("door_wood",     (0.52, 0.36, 0.22), 0.70),
    "door_metal":    lambda: mat("door_metal",    (0.55, 0.60, 0.65), 0.40, 0.7),
    "glass":         lambda: mat("glass",         (0.72, 0.86, 0.95), 0.05, 0.0, 0.35),
    "ground":        lambda: mat("ground",        (0.55, 0.68, 0.35), 0.95),
    "patio_rubber":  lambda: mat("patio_rubber",  (0.78, 0.30, 0.28), 0.85),
    "invisible":     lambda: mat("invisible",     (1.00, 0.00, 1.00), 1.0),
}

# -------------------------------------------------------------- #
# 4. COLEÇÕES
# -------------------------------------------------------------- #
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

# -------------------------------------------------------------- #
# 5. HELPERS GEOMÉTRICOS
# -------------------------------------------------------------- #
def make_box(name, center, size, material, collection):
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [
        (-hx,-hy,-hz),( hx,-hy,-hz),( hx, hy,-hz),(-hx, hy,-hz),
        (-hx,-hy, hz),( hx,-hy, hz),( hx, hy, hz),(-hx, hy, hz),
    ]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    m = bpy.data.meshes.new(name + "_mesh")
    m.from_pydata(verts, [], faces)
    m.update()
    o = bpy.data.objects.new(name, m)
    o.location = center
    o.data.materials.append(material)
    collection.objects.link(o)
    return o

def make_mesh_data(name, verts, faces, material, collection, loc=(0,0,0)):
    m = bpy.data.meshes.new(name + "_mesh")
    m.from_pydata(verts, [], faces)
    m.update()
    o = bpy.data.objects.new(name, m)
    o.location = loc
    o.data.materials.append(material)
    collection.objects.link(o)
    return o

def add_collider(name, center, size):
    """Cria uma caixa invisível de colisão."""
    o = make_box(name, center, size, MATS["invisible"](), SUBS["COLLIDERS"])
    o.display_type = "WIRE"
    o.hide_render = True
    return o

# -------------------------------------------------------------- #
# 6. MUROS COM ABERTURAS
# -------------------------------------------------------------- #
DOORS_CREATED = []  # (id, hinge_x, hinge_y, leaf_w, swing)

def build_wall_along_x(name, x1, x2, y, height, openings):
    """Muro paralelo ao eixo X. openings = [{type,pos,width,swing?}]."""
    wall_mat = MATS["wall_yellow"]()
    sorted_ops = sorted(openings, key=lambda o: o["pos"])
    cursor = x1
    idx = 0
    for op in sorted_ops:
        op_start = x1 + op["pos"] - op["width"]/2
        op_end   = x1 + op["pos"] + op["width"]/2
        # Segmento sólido antes da abertura
        if op_start > cursor + 1e-4:
            w = op_start - cursor
            cx = (cursor + op_start)/2
            make_box(f"{name}_S{idx}", (cx, y, height/2), (w, WALL_T, height),
                     wall_mat, SUBS["WALLS"])
            add_collider(f"COLLIDER_{name}_S{idx}", (cx, y, height/2), (w, WALL_T, height))
        cx_op = (op_start + op_end)/2
        if op["type"] == "door":
            header_h = height - DOOR_H
            if header_h > 1e-3:
                make_box(f"{name}_HDR{idx}", (cx_op, y, (DOOR_H + height)/2),
                         (op["width"], WALL_T, header_h), wall_mat, SUBS["WALLS"])
            swing = op.get("swing", 1)
            DOORS_CREATED.append({
                "id": f"{name}_D{idx}",
                "hinge_x": op_start,
                "hinge_y": y,
                "leaf_w": op["width"],
                "swing": swing,
            })
        elif op["type"] == "window":
            if WIN_SILL > 1e-3:
                make_box(f"{name}_SILL{idx}", (cx_op, y, WIN_SILL/2),
                         (op["width"], WALL_T, WIN_SILL), wall_mat, SUBS["WALLS"])
            header_h = height - WIN_TOP
            if header_h > 1e-3:
                make_box(f"{name}_WHDR{idx}", (cx_op, y, (WIN_TOP + height)/2),
                         (op["width"], WALL_T, header_h), wall_mat, SUBS["WALLS"])
            make_box(f"{name}_GLASS{idx}", (cx_op, y, (WIN_SILL + WIN_TOP)/2),
                     (op["width"]-0.10, 0.02, (WIN_TOP-WIN_SILL)-0.10),
                     MATS["glass"](), SUBS["WINDOWS"])
            # Colisor full-height na abertura da janela
            add_collider(f"COLLIDER_{name}_WIN{idx}", (cx_op, y, height/2),
                         (op["width"], WALL_T, height))
        cursor = op_end
        idx += 1
    if cursor < x2 - 1e-4:
        w = x2 - cursor
        cx = (cursor + x2)/2
        make_box(f"{name}_SEND", (cx, y, height/2), (w, WALL_T, height),
                 wall_mat, SUBS["WALLS"])
        add_collider(f"COLLIDER_{name}_SEND", (cx, y, height/2), (w, WALL_T, height))

def build_wall_along_y(name, y1, y2, x, height, openings):
    """Muro paralelo ao eixo Y."""
    wall_mat = MATS["wall_yellow"]()
    sorted_ops = sorted(openings, key=lambda o: o["pos"])
    cursor = y1
    idx = 0
    for op in sorted_ops:
        op_start = y1 + op["pos"] - op["width"]/2
        op_end   = y1 + op["pos"] + op["width"]/2
        if op_start > cursor + 1e-4:
            w = op_start - cursor
            cy = (cursor + op_start)/2
            make_box(f"{name}_S{idx}", (x, cy, height/2), (WALL_T, w, height),
                     wall_mat, SUBS["WALLS"])
            add_collider(f"COLLIDER_{name}_S{idx}", (x, cy, height/2), (WALL_T, w, height))
        cy_op = (op_start + op_end)/2
        if op["type"] == "window":
            make_box(f"{name}_SILL{idx}", (x, cy_op, WIN_SILL/2),
                     (WALL_T, op["width"], WIN_SILL), wall_mat, SUBS["WALLS"])
            header_h = height - WIN_TOP
            if header_h > 1e-3:
                make_box(f"{name}_WHDR{idx}", (x, cy_op, (WIN_TOP + height)/2),
                         (WALL_T, op["width"], header_h), wall_mat, SUBS["WALLS"])
            make_box(f"{name}_GLASS{idx}", (x, cy_op, (WIN_SILL + WIN_TOP)/2),
                     (0.02, op["width"]-0.10, (WIN_TOP-WIN_SILL)-0.10),
                     MATS["glass"](), SUBS["WINDOWS"])
            add_collider(f"COLLIDER_{name}_WIN{idx}", (x, cy_op, height/2),
                         (WALL_T, op["width"], height))
        elif op["type"] == "door":
            header_h = height - DOOR_H
            if header_h > 1e-3:
                make_box(f"{name}_HDR{idx}", (x, cy_op, (DOOR_H + height)/2),
                         (WALL_T, op["width"], header_h), wall_mat, SUBS["WALLS"])
        cursor = op_end
        idx += 1
    if cursor < y2 - 1e-4:
        w = y2 - cursor
        cy = (cursor + y2)/2
        make_box(f"{name}_SEND", (x, cy, height/2), (WALL_T, w, height),
                 wall_mat, SUBS["WALLS"])
        add_collider(f"COLLIDER_{name}_SEND", (x, cy, height/2), (WALL_T, w, height))

# -------------------------------------------------------------- #
# 7. PORTAS (PIVÔ + FOLHA)
# -------------------------------------------------------------- #
def build_door_leaf(door_id, hinge_x, hinge_y, leaf_w, swing):
    pivot = bpy.data.objects.new(f"DOOR_PIVOT_{door_id}", None)
    pivot.empty_display_type = "ARROWS"
    pivot.empty_display_size = 0.4
    pivot.location = (hinge_x, hinge_y, 0.0)
    SUBS["DOORS"].objects.link(pivot)
    # metadados
    pivot["emerald_kind"]  = "door_pivot"
    pivot["emerald_swing"] = float(swing)

    leaf = make_box(f"DOOR_LEAF_{door_id}", (0,0,0), (leaf_w, 0.05, DOOR_H - 0.05),
                    MATS["door_wood"](), SUBS["DOORS"])
    leaf.location = (leaf_w/2, 0, (DOOR_H - 0.05)/2)
    leaf.parent = pivot

    # collider na posição "porta fechada"
    coll = add_collider(f"COLLIDER_DOOR_{door_id}",
                        (hinge_x + leaf_w/2, hinge_y, (DOOR_H - 0.05)/2),
                        (leaf_w, 0.20, DOOR_H - 0.05))
    coll["emerald_kind"] = "door_collider"
    coll["emerald_door_id"] = door_id

# -------------------------------------------------------------- #
# 8. ROOMS
# -------------------------------------------------------------- #
ROOMS = [
    # id, x1, x2, y1, y2, height, corr_side, floor_mat, wall_trim_mat
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
    first_x_in_row = {"N": None, "S": None}
    for rid, x1, x2, y1, y2, h, corr, fmat, wmat in ROOMS:
        # Piso
        make_box(f"FLOOR_{rid}",
                 ((x1+x2)/2, (y1+y2)/2, -0.05),
                 (x2-x1, y2-y1, 0.10),
                 MATS[fmat](), SUBS["FLOORS"])
        # Paredes
        cx_door = (x1 + x2)/2
        win_w = min(2.0, (x2-x1)*0.5)
        if corr == "S":
            # Corredor está em y1; parede sul com porta
            build_wall_along_x(f"WALL_{rid}_S", x1, x2, y1, h,
                               [{"type":"door","pos":cx_door - x1,
                                 "width":DOOR_W,"swing":+1}])
            # Parede norte com janela
            build_wall_along_x(f"WALL_{rid}_N", x1, x2, y2, h,
                               [{"type":"window","pos":cx_door - x1,"width":win_w}])
        else:  # corr == "N"
            build_wall_along_x(f"WALL_{rid}_N", x1, x2, y2, h,
                               [{"type":"door","pos":cx_door - x1,
                                 "width":DOOR_W,"swing":-1}])
            build_wall_along_x(f"WALL_{rid}_S", x1, x2, y1, h,
                               [{"type":"window","pos":cx_door - x1,"width":win_w}])
        # Paredes leste/oeste (evita duplicação)
        if first_x_in_row[corr] is None:
            # primeira sala da fileira -> parede oeste exterior
            build_wall_along_y(f"WALL_{rid}_W", y1, y2, x1, h, [])
            first_x_in_row[corr] = rid
        # parede leste sempre (é partição com vizinho OU exterior)
        build_wall_along_y(f"WALL_{rid}_E", y1, y2, x2, h, [])

# -------------------------------------------------------------- #
# 9. CORREDOR
# -------------------------------------------------------------- #
def build_corridor():
    # Piso do corredor
    make_box("FLOOR_CORRIDOR", (19, 0, -0.05), (36, 1.8, 0.10),
             MATS["floor_beige"](), SUBS["FLOORS"])
    # Forro do corredor (laje sob o telhado)
    make_box("CEIL_CORRIDOR", (19, 0, 2.85), (36, 1.8, 0.10),
             MATS["wall_white"](), SUBS["ROOFS"])
    # Iluminação (dummy empties para o manifesto)
    for i, x in enumerate([3, 11, 19, 27, 35]):
        e = bpy.data.objects.new(f"LIGHT_EMPTY_CORRIDOR_{i+1:02d}", None)
        e.location = (x, 0, 2.7)
        SUBS["LIGHTING"].objects.link(e)

# -------------------------------------------------------------- #
# 10. PÁTIO COBERTO
# -------------------------------------------------------------- #
def build_patio():
    px1, px2 = 2.0, 14.0
    py1, py2 = 8.5, 14.5
    # Piso
    make_box("FLOOR_PATIO", ((px1+px2)/2, (py1+py2)/2, -0.05),
             (px2-px1, py2-py1, 0.10), MATS["patio_rubber"](), SUBS["FLOORS"])
    # Colunas
    col_h = 3.5
    for i, (cx, cy) in enumerate([(px1+0.2, py1+0.2), (px2-0.2, py1+0.2),
                                   (px1+0.2, py2-0.2), (px2-0.2, py2-0.2),
                                   ((px1+px2)/2, py1+0.2), ((px1+px2)/2, py2-0.2)]):
        make_box(f"COLUMN_PATIO_{i+1:02d}", (cx, cy, col_h/2),
                 (0.20, 0.20, col_h), MATS["column"](), SUBS["STRUCTURE"])
        add_collider(f"COLLIDER_COL_PATIO_{i+1:02d}",
                     (cx, cy, col_h/2), (0.20, 0.20, col_h))
    # Cobertura (laje translúcida simulada em vidro azul)
    make_box("ROOF_PATIO", ((px1+px2)/2, (py1+py2)/2, col_h + 0.10),
             (px2-px1+0.4, py2-py1+0.4, 0.10), MATS["glass"](), SUBS["ROOFS"])

# -------------------------------------------------------------- #
# 11. TELHADO PRINCIPAL (DUAS ÁGUAS)
# -------------------------------------------------------------- #
def build_roof():
    xmin, xmax = 0.5, 37.5
    y_s, y_n   = -8.4, 9.4
    z_eave     = 3.10
    y_ridge, z_ridge = 0.5, 4.50
    t = 0.15
    mat_roof = MATS["roof_tile"]()

    # Face sul
    v_s = [
        (xmin, y_s, z_eave), (xmax, y_s, z_eave),
        (xmax, y_ridge, z_ridge), (xmin, y_ridge, z_ridge),
        (xmin, y_s, z_eave - t), (xmax, y_s, z_eave - t),
        (xmax, y_ridge, z_ridge - t), (xmin, y_ridge, z_ridge - t),
    ]
    f_s = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    make_mesh_data("ROOF_SOUTH", v_s, f_s, mat_roof, SUBS["ROOFS"])

    # Face norte
    v_n = [
        (xmin, y_ridge, z_ridge), (xmax, y_ridge, z_ridge),
        (xmax, y_n, z_eave), (xmin, y_n, z_eave),
        (xmin, y_ridge, z_ridge - t), (xmax, y_ridge, z_ridge - t),
        (xmax, y_n, z_eave - t), (xmin, y_n, z_eave - t),
    ]
    f_n = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    make_mesh_data("ROOF_NORTH", v_n, f_n, mat_roof, SUBS["ROOFS"])

    # Cumeeira
    make_box("ROOF_RIDGE", ((xmin+xmax)/2, y_ridge, z_ridge),
             (xmax-xmin, 0.20, 0.10), mat_roof, SUBS["ROOFS"])

# -------------------------------------------------------------- #
# 12. SÍTIO
# -------------------------------------------------------------- #
def build_site():
    make_box("SITE_TERRAIN", (19, 0, -0.10), (120, 100, 0.10),
             MATS["ground"](), SUBS["SITE"])
    # Calçada de entrada oeste
    make_box("SITE_ENTRY_W", (-3, 0, -0.08), (6, 3.0, 0.06),
             MATS["floor_beige"](), SUBS["SITE"])

# -------------------------------------------------------------- #
# 13. CÂMERAS E LUZ
# -------------------------------------------------------------- #
def build_cameras_and_lights():
    # Câmera externa
    cam_ext_data = bpy.data.cameras.new("CAM_EXTERNAL")
    cam_ext_data.lens = 35
    cam_ext = bpy.data.objects.new("CAM_EXTERNAL", cam_ext_data)
    cam_ext.location = (-25, -25, 18)
    cam_ext.rotation_euler = (math.radians(60), 0, math.radians(-45))
    SUBS["CAMERAS"].objects.link(cam_ext)

    # Câmera interna
    cam_int_data = bpy.data.cameras.new("CAM_INTERNAL")
    cam_int_data.lens = 24
    cam_int = bpy.data.objects.new("CAM_INTERNAL", cam_int_data)
    cam_int.location = (1.0, 0, 1.7)
    cam_int.rotation_euler = (math.radians(90), 0, math.radians(90))
    SUBS["CAMERAS"].objects.link(cam_int)

    bpy.context.scene.camera = cam_ext

    # Sol
    sun_d = bpy.data.lights.new("SUN_NORDESTE", type="SUN")
    sun_d.energy = 3.5
    sun_d.color = (1.0, 0.957, 0.878)
    sun = bpy.data.objects.new("SUN_NORDESTE", sun_d)
    sun.location = (30, 40, 50)
    sun.rotation_euler = (math.radians(45), 0, math.radians(30))
    SUBS["LIGHTING"].objects.link(sun)

    # Ambiente hemisférico
    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = next((n for n in w.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg:
        bg.inputs["Color"].default_value = (0.75, 0.85, 0.95, 1.0)
        bg.inputs["Strength"].default_value = 1.0

# -------------------------------------------------------------- #
# 14. EXPORTAÇÃO
# -------------------------------------------------------------- #
def export_glb():
    # Selecionar tudo sob EMERALD_GENERATED (exceto câmeras e luzes)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    count = 0
    for o in ROOT_COLL.all_objects:
        if o.type in {"MESH", "EMPTY"}:
            o.select_set(True)
            count += 1
    if count == 0:
        raise RuntimeError("Nada para exportar.")
    # Verificar parâmetros suportados
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    supported = {p.identifier for p in rna.properties}
    kwargs = dict(
        filepath=GLB_OUT,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=False,
        export_animations=False,
    )
    if "export_extras" in supported:
        kwargs["export_extras"] = True
    if "export_materials" in supported:
        kwargs["export_materials"] = "EXPORT"
    if "export_cameras" in supported:
        kwargs["export_cameras"] = False
    if "export_lights" in supported:
        kwargs["export_lights"] = False

    bpy.ops.export_scene.gltf(**kwargs)

    if not os.path.exists(GLB_OUT) or os.path.getsize(GLB_OUT) == 0:
        raise RuntimeError("GLB não foi gerado.")

    size_mb = os.path.getsize(GLB_OUT) / (1024*1024)
    print(f"[EMERALD] GLB exportado: {GLB_OUT} ({size_mb:.2f} MB, {count} objetos)")
    if size_mb > 25:
        print(f"[EMERALD][AVISO] GLB excede 25MB ({size_mb:.2f}MB).")

# -------------------------------------------------------------- #
# 15. MAIN
# -------------------------------------------------------------- #
def main():
    check_environment()
    cleanup()
    init_collections()
    build_site()
    build_corridor()
    build_rooms()
    build_patio()
    build_roof()
    build_cameras_and_lights()
    # Construir folhas de porta (após todos os DOORS_CREATED coletados)
    for d in DOORS_CREATED:
        build_door_leaf(d["id"], d["hinge_x"], d["hinge_y"], d["leaf_w"], d["swing"])
    print(f"[EMERALD] Portas criadas: {len(DOORS_CREATED)}")
    # Exportar
    export_glb()
    # Salvar .blend
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[EMERALD] Blend salvo: {BLEND_OUT}")
    print("[EMERALD] P01 concluído com sucesso.")

if __name__ == "__main__":
    main()