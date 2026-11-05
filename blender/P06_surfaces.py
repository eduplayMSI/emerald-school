"""
P06_surfaces.py — EMERALD-SCARLATE NORDESTE
Refinamento incremental de pisos internos, terreno, grama, pavimentação,
transições e drenagem. NÃO reconstrói a escola.

Pré-requisito: blender/EMERALD_SCHOOL.blend já gerado por P03_accessibility.py
Uso: Blender 5.2 LTS → Text Editor → Alt+P
"""
import bpy
import bmesh
import math
import os

# ============================================================ #
# 0. RESOLUÇÃO DE CAMINHOS
# ============================================================ #
def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        return os.path.dirname(p) if os.path.basename(p).lower() == "blender" else p
    env = os.environ.get("EMERALD_ROOT")
    if env and os.path.isdir(env):
        return env
    home = os.path.expanduser("~")
    for c in (os.path.join(home, "Desktop", "EMERALD-SCHOOL"),
              os.path.join(home, "Documents", "EMERALD-SCHOOL"),
              os.path.join(home, "OneDrive", "Desktop", "EMERALD-SCHOOL"),
              os.path.join(home, "EMERALD-SCHOOL")):
        if os.path.isdir(c):
            return c
    d = os.path.join(home, "Desktop")
    return os.path.join(d if os.path.isdir(d) else home, "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
GLB_OUT   = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")
print(f"[EMERALD][P06] PROJECT_ROOT = {PROJECT_ROOT}")
for d in (os.path.dirname(GLB_OUT), os.path.dirname(BLEND_OUT)):
    os.makedirs(d, exist_ok=True)

# ============================================================ #
# 1. PRÉ-VERIFICAÇÕES
# ============================================================ #
def check_environment():
    v = bpy.app.version
    print(f"[EMERALD][P06] Blender {v[0]}.{v[1]}.{v[2]}")
    if v[0] < 5 or (v[0] == 5 and v[1] < 2):
        raise RuntimeError("Blender 5.2+ exigido.")
    if not hasattr(bpy.ops.export_scene, "gltf"):
        raise RuntimeError("Habilite Preferences → Add-ons → glTF 2.0.")
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    if rna is None:
        raise RuntimeError("Operador glTF sem RNA.")
    print("[EMERALD][P06] Exportador glTF OK.")

def verify_p03_base():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if root is None:
        raise RuntimeError(
            "Base P03 ausente: coleção 'EMERALD_GENERATED' não encontrada.\n"
            "Execute primeiro blender/P03_accessibility.py em um .blend novo."
        )
    for obj_name in ("SITE_TERRAIN", "FLOOR_CORRIDOR"):
        if not bpy.data.objects.get(obj_name):
            raise RuntimeError(
                f"Base P03 incompleta: objeto '{obj_name}' ausente.\n"
                "Execute blender/P03_accessibility.py e salve o .blend antes de P06."
            )
    print("[EMERALD][P06] Base P03 detectada (SITE_TERRAIN + FLOOR_CORRIDOR).")

# ============================================================ #
# 2. CLEANUP + COLEÇÕES
# ============================================================ #
P06_COLL_NAME = "P06_SURFACES"
P06_COLL = None
P06_SUBS = {}

def cleanup_p06():
    for coll in list(bpy.data.collections):
        if coll.name == P06_COLL_NAME or coll.name.startswith(P06_COLL_NAME + "_"):
            for obj in list(coll.all_objects):
                try: bpy.data.objects.remove(obj, do_unlink=True)
                except Exception: pass
            try: bpy.data.collections.remove(coll)
            except Exception: pass
    for m in list(bpy.data.materials):
        if m.name.startswith("P06_"):
            try: bpy.data.materials.remove(m)
            except Exception: pass
    print("[EMERALD][P06] Cleanup P06 OK.")

def init_p06_collections():
    global P06_COLL, P06_SUBS
    root = bpy.data.collections.get("EMERALD_GENERATED")
    P06_COLL = bpy.data.collections.new(P06_COLL_NAME)
    root.children.link(P06_COLL)
    for name in ("INTERNAL_FLOORS", "EXTERNAL_GROUND", "PAVING",
                 "TRANSITIONS", "DRAINAGE", "SKIRTING", "DECOR"):
        sub = bpy.data.collections.new(f"{P06_COLL_NAME}_{name}")
        P06_COLL.children.link(sub)
        P06_SUBS[name] = sub
    print(f"[EMERALD][P06] Coleções P06: {list(P06_SUBS)}")

# ============================================================ #
# 3. MATERIAIS
# ============================================================ #
_P06_MATS = {}
def p06_mat(name, rgb, rough=0.85, metal=0.0):
    if name in _P06_MATS:
        return _P06_MATS[name]
    m = bpy.data.materials.new(f"P06_{name}")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out: nt.links.new(bsdf.outputs[0], out.inputs[0])
    def _s(k, v):
        if k in bsdf.inputs: bsdf.inputs[k].default_value = v
    _s("Base Color", (*rgb, 1.0))
    _s("Roughness", rough)
    _s("Metallic", metal)
    _P06_MATS[name] = m
    return m

MATS = {
    "grout":      lambda: p06_mat("grout",      (0.55, 0.50, 0.45), 0.95),
    "skirt":      lambda: p06_mat("skirt",      (0.72, 0.66, 0.58), 0.80),
    "grass_a":    lambda: p06_mat("grass_a",    (0.52, 0.65, 0.32), 0.95),
    "grass_b":    lambda: p06_mat("grass_b",    (0.60, 0.72, 0.40), 0.95),
    "grass_c":    lambda: p06_mat("grass_c",    (0.44, 0.56, 0.27), 0.95),
    "earth":      lambda: p06_mat("earth",      (0.62, 0.52, 0.40), 0.95),
    "drain":      lambda: p06_mat("drain",      (0.38, 0.38, 0.42), 0.50, 0.4),
    "pave_line":  lambda: p06_mat("pave_line",  (0.55, 0.52, 0.50), 0.85),
    "threshold":  lambda: p06_mat("threshold",  (0.78, 0.72, 0.62), 0.55, 0.1),
    "bush":       lambda: p06_mat("bush",       (0.28, 0.48, 0.24), 0.90),
}

# ============================================================ #
# 4. HELPERS GEOMÉTRICOS
# ============================================================ #
def make_p06_box(name, center, size, material, collection):
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
             (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    o.location = center
    o.data.materials.append(material)
    collection.objects.link(o)
    return o

def make_p06_sphere(name, center, radius, material, collection, segs=10, rings=7):
    me = bpy.data.meshes.new(name + "_mesh")
    verts = []; faces = []
    for i in range(rings + 1):
        phi = (i / rings) * math.pi
        for j in range(segs):
            theta = (j / segs) * 2 * math.pi
            verts.append((
                radius * math.sin(phi) * math.cos(theta),
                radius * math.sin(phi) * math.sin(theta),
                radius * math.cos(phi),
            ))
    for i in range(rings):
        for j in range(segs):
            a = i * segs + j
            b = i * segs + (j + 1) % segs
            c = (i + 1) * segs + j
            d = (i + 1) * segs + (j + 1) % segs
            faces.append((a, b, d, c))
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    o.location = center
    o.data.materials.append(material)
    collection.objects.link(o)
    return o

def get_bbox(obj_name, include_top=False):
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return None
    cx, cy, cz = obj.location
    sx, sy, sz = obj.dimensions
    x1, x2 = cx - sx/2, cx + sx/2
    y1, y2 = cy - sy/2, cy + sy/2
    if include_top:
        return (x1, x2, y1, y2, cz + sz/2)
    return (x1, x2, y1, y2)

# ============================================================ #
# 5. PISOS INTERNOS — GROUT LINES
# ============================================================ #
# Salas com revestimento cerâmico (tiles). Berçários (vinílico) NÃO entram.
TILE_ROOMS = {
    "SPC_CLASS_01": 0.60, "SPC_CLASS_02": 0.60,
    "SPC_CLASS_03": 0.60, "SPC_CLASS_04": 0.60,
    "SPC_MULTI":    0.60,
    "SPC_WC_01":    0.30, "SPC_WC_02":    0.30,
    "SPC_KITCHEN":  0.30,
    "SPC_CAFE":     0.60,
}
CORRIDOR_TILE = 0.60

def build_grout_mesh(name, bbox, top_z, tile_size, collection):
    """Cria grade de juntas em um único mesh (via bmesh) — 1 draw call por ambiente."""
    x1, x2, y1, y2 = bbox
    inset = 0.06
    x1i, x2i, y1i, y2i = x1+inset, x2-inset, y1+inset, y2-inset
    if x2i <= x1i or y2i <= y1i:
        return None
    z = top_z + 0.003
    w = 0.008
    me = bpy.data.meshes.new(f"{name}_mesh")
    bm = bmesh.new()
    # linhas verticais (x constante)
    x = x1i + tile_size
    while x < x2i - 0.001:
        xm, xp = x - w/2, x + w/2
        v1 = bm.verts.new((xm, y1i, z))
        v2 = bm.verts.new((xp, y1i, z))
        v3 = bm.verts.new((xp, y2i, z))
        v4 = bm.verts.new((xm, y2i, z))
        bm.faces.new((v1, v2, v3, v4))
        x += tile_size
    # linhas horizontais (y constante)
    y = y1i + tile_size
    while y < y2i - 0.001:
        ym, yp = y - w/2, y + w/2
        v1 = bm.verts.new((x1i, ym, z))
        v2 = bm.verts.new((x2i, ym, z))
        v3 = bm.verts.new((x2i, yp, z))
        v4 = bm.verts.new((x1i, yp, z))
        bm.faces.new((v1, v2, v3, v4))
        y += tile_size
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(MATS["grout"]())
    collection.objects.link(o)
    return o

def build_internal_floor_tiles():
    count = 0
    for room_id, tile_size in TILE_ROOMS.items():
        bbox = get_bbox(f"FLOOR_{room_id}", include_top=True)
        if bbox is None:
            print(f"[EMERALD][P06] FLOOR_{room_id} ausente — pulando.")
            continue
        x1, x2, y1, y2, top_z = bbox
        o = build_grout_mesh(f"P06_GROUT_{room_id}", (x1, x2, y1, y2),
                             top_z, tile_size, P06_SUBS["INTERNAL_FLOORS"])
        if o: count += 1
    # Corredor
    bbox = get_bbox("FLOOR_CORRIDOR", include_top=True)
    if bbox:
        x1, x2, y1, y2, top_z = bbox
        o = build_grout_mesh("P06_GROUT_FLOOR_CORRIDOR", (x1, x2, y1, y2),
                             top_z, CORRIDOR_TILE, P06_SUBS["INTERNAL_FLOORS"])
        if o: count += 1
    print(f"[EMERALD][P06] Grout lines: {count} ambientes (1 mesh cada).")

# ============================================================ #
# 6. RODAPÉ (SKIRTING)
# ============================================================ #
def build_skirting():
    h, t = 0.10, 0.02
    mat = MATS["skirt"]()
    count = 0
    for room_id in list(TILE_ROOMS) + ["SPC_BERC_01", "SPC_BERC_02"]:
        bbox = get_bbox(f"FLOOR_{room_id}")
        if bbox is None: continue
        x1, x2, y1, y2 = bbox
        cx, cy = (x1+x2)/2, (y1+y2)/2
        m = f"P06_SKIRT_{room_id}"
        make_p06_box(f"{m}_N", (cx, y2 - t/2, h/2), (x2-x1-2*t, t, h), mat, P06_SUBS["SKIRTING"])
        make_p06_box(f"{m}_S", (cx, y1 + t/2, h/2), (x2-x1-2*t, t, h), mat, P06_SUBS["SKIRTING"])
        make_p06_box(f"{m}_E", (x2 - t/2, cy, h/2), (t, y2-y1-2*t, h), mat, P06_SUBS["SKIRTING"])
        make_p06_box(f"{m}_W", (x1 + t/2, cy, h/2), (t, y2-y1-2*t, h), mat, P06_SUBS["SKIRTING"])
        count += 4
    print(f"[EMERALD][P06] Rodapé: {count} segmentos.")

# ============================================================ #
# 7. SOLEIRAS / THRESHOLDS
# ============================================================ #
def build_door_thresholds():
    mat = MATS["threshold"]()
    count = 0
    for piv in bpy.data.objects:
        if not piv.name.startswith("DOOR_PIVOT_"): continue
        door_id = piv.name.replace("DOOR_PIVOT_", "")
        hx, hy, _ = piv.location
        leaf = next((c for c in piv.children if c.name.startswith("DOOR_LEAF_")), None)
        if leaf is None: continue
        leaf_w = leaf.dimensions.x
        make_p06_box(f"P06_THRESH_{door_id}",
                     (hx + leaf_w/2, hy, 0.005),
                     (leaf_w, 0.15, 0.01),
                     mat, P06_SUBS["TRANSITIONS"])
        count += 1
    print(f"[EMERALD][P06] Soleiras: {count} portas.")

# ============================================================ #
# 8. GRAMA — VARIAÇÃO DE TONS
# ============================================================ #
def build_grass_patches():
    # Patches grandes, sem sobreposição, longe de ROUTE_007 (x∈[0,2], y∈[0,8.5])
    patches = [
        ("P06_GRASS_PATCH_01", (-20,  20, 12, 10), "grass_b"),
        ("P06_GRASS_PATCH_02", (-20, -10, 12, 10), "grass_c"),
        ("P06_GRASS_PATCH_03", ( 50,  15, 14, 12), "grass_a"),
        ("P06_GRASS_PATCH_04", ( 50, -15, 14, 12), "grass_c"),
        ("P06_GRASS_PATCH_05", ( 20,  25, 24,  8), "grass_b"),
        ("P06_GRASS_PATCH_06", ( 20, -18, 24,  8), "grass_a"),
    ]
    for name, (cx, cy, sx, sy), mat_key in patches:
        make_p06_box(name, (cx, cy, -0.04), (sx, sy, 0.02),
                     MATS[mat_key](), P06_SUBS["EXTERNAL_GROUND"])
    print(f"[EMERALD][P06] Grama: {len(patches)} patches (tons variados).")

def build_earth_patches():
    # Pequenas manchas de terra batida nos acessos externos — NÃO na rota 007
    patches = [
        ("P06_EARTH_01", (-2.5, 0,   1.5, 1.2)),
        ("P06_EARTH_02", (38.5, -5.5, 1.2, 2.0)),
        ("P06_EARTH_03", (1.0, 15.5, 2.0, 1.0)),
    ]
    for name, (cx, cy, sx, sy) in patches:
        make_p06_box(name, (cx, cy, -0.045), (sx, sy, 0.02),
                     MATS["earth"](), P06_SUBS["EXTERNAL_GROUND"])
    print(f"[EMERALD][P06] Terra batida: {len(patches)} manchas.")

# ============================================================ #
# 9. PAVIMENTAÇÃO DA CALÇADA
# ============================================================ #
def refine_paving_calcada():
    bbox = get_bbox("SITE_ENTRY_W", include_top=True)
    if bbox is None:
        print("[EMERALD][P06] SITE_ENTRY_W ausente — pulando.")
        return
    x1, x2, y1, y2, top_z = bbox
    build_grout_mesh("P06_PAVE_GRID_ENTRY_W", (x1, x2, y1, y2),
                     top_z, 0.60, P06_SUBS["PAVING"])
    print("[EMERALD][P06] Calçada: grade de juntas adicionada.")

# ============================================================ #
# 10. DRENAGEM
# ============================================================ #
def build_drainage():
    mat = MATS["drain"]()
    # Canaleta sul (exterior da parede sul do bloco)
    make_p06_box("P06_DRAIN_S", (19, -7.15, 0.005), (37, 0.20, 0.02),
                 mat, P06_SUBS["DRAINAGE"])
    # Extensão SE — canaleta que contorna o canto sudeste
    make_p06_box("P06_DRAIN_SE", (37.4, -3.5, 0.005), (0.20, 7.3, 0.02),
                 mat, P06_SUBS["DRAINAGE"])
    print("[EMERALD][P06] Drenagem: 2 canaletas exteriores.")

# ============================================================ #
# 11. VEGETAÇÃO
# ============================================================ #
def build_bushes():
    # Arbustos — longe de ROUTE_007 (x∈[0,2], y∈[0,8.5])
    positions = [
        ("P06_BUSH_01", ( 1.5, 15.0)),
        ("P06_BUSH_02", (14.5, 15.0)),
        ("P06_BUSH_03", (-3.0, -3.0)),
        ("P06_BUSH_04", (38.0,  3.0)),
    ]
    for name, (cx, cy) in positions:
        make_p06_sphere(name, (cx, cy, 0.30), 0.40,
                        MATS["bush"](), P06_SUBS["DECOR"])
    print(f"[EMERALD][P06] Vegetação: {len(positions)} arbustos.")

# ============================================================ #
# 12. EXPORTAÇÃO
# ============================================================ #
def export_glb():
    for o in bpy.context.selected_objects:
        o.select_set(False)
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if root is None:
        raise RuntimeError("EMERALD_GENERATED ausente na exportação.")
    EXCLUDE = ("MARKER_SPHERE_", "OBSTACLE_SPHERE_", "HAZARD_SPHERE_", "ROUTE_RIBBON_")
    count = 0
    for o in root.all_objects:
        if o.type not in {"MESH", "EMPTY"}: continue
        if any(o.name.startswith(p) for p in EXCLUDE): continue
        o.select_set(True)
        count += 1
    if count == 0:
        raise RuntimeError("Nada para exportar.")
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    sup = {p.identifier for p in rna.properties}
    kw = dict(filepath=GLB_OUT, export_format="GLB", use_selection=True,
              export_yup=True, export_apply=False, export_animations=False)
    if "export_extras" in sup: kw["export_extras"] = True
    if "export_materials" in sup: kw["export_materials"] = "EXPORT"
    if "export_cameras" in sup: kw["export_cameras"] = False
    if "export_lights" in sup: kw["export_lights"] = False
    bpy.ops.export_scene.gltf(**kw)
    if not os.path.exists(GLB_OUT) or os.path.getsize(GLB_OUT) == 0:
        raise RuntimeError("GLB não gerado.")
    size_mb = os.path.getsize(GLB_OUT) / (1024 * 1024)
    print(f"[EMERALD][P06] GLB exportado: {GLB_OUT} ({size_mb:.2f} MB, {count} objetos)")

# ============================================================ #
# 13. MAIN
# ============================================================ #
def main():
    check_environment()
    verify_p03_base()
    cleanup_p06()
    init_p06_collections()
    build_internal_floor_tiles()
    build_skirting()
    build_door_thresholds()
    build_grass_patches()
    build_earth_patches()
    refine_paving_calcada()
    build_drainage()
    build_bushes()
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[EMERALD][P06] Blend salvo: {BLEND_OUT}")
    print("[EMERALD][P06] Concluído. Reexporte e teste em localhost:8000.")

if __name__ == "__main__":
    main()