"""
P08_furniture.py — EMERALD-SCARLATE NORDESTE
Gera mobiliário e equipamentos pedagógicos. Idempotente. Exporta GLB.
"""
import bpy
import math
import os

# ============================================================ #
# 0. CAMINHOS
# ============================================================ #
def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        return os.path.dirname(p) if os.path.basename(p).lower() == "blender" else p
    home = os.path.expanduser("~")
    for c in (os.path.join(home, "Desktop", "EMERALD-SCHOOL"),
              os.path.join(home, "Documents", "EMERALD-SCHOOL")):
        if os.path.isdir(c): return c
    return os.path.join(home, "Desktop", "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
GLB_OUT = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")

# ============================================================ #
# 1. PREPARAÇÃO E CLEANUP
# ============================================================ #
def setup_collection():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("Coleção EMERALD_GENERATED não encontrada.")
    
    # Limpa execuções anteriores
    coll = bpy.data.collections.get("P08_FURNITURE")
    if coll:
        for obj in list(coll.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(coll)
    
    # Cria nova
    coll = bpy.data.collections.new("P08_FURNITURE")
    root.children.link(coll)
    return coll

def get_mat(name, fallback_color):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf and "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*fallback_color, 1.0)
    return m

# ============================================================ #
# 2. CONSTRUTORES (Geometria)
# ============================================================ #
def make_box(name, center, size, mat, coll):
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
    o.data.materials.append(mat)
    coll.objects.link(o)
    return o

def build_table(prefix, x, y, z, w, d, h, coll):
    wood = get_mat("EM_M_door_wood", (0.48, 0.33, 0.20))
    # Tampo
    make_box(f"{prefix}_TOP", (x, y, z + h - 0.02), (w, d, 0.04), wood, coll)
    # 4 Pernas
    lw = 0.05
    make_box(f"{prefix}_L1", (x - w/2 + lw, y - d/2 + lw, z + h/2), (lw, lw, h), wood, coll)
    make_box(f"{prefix}_L2", (x + w/2 - lw, y - d/2 + lw, z + h/2), (lw, lw, h), wood, coll)
    make_box(f"{prefix}_L3", (x - w/2 + lw, y + d/2 - lw, z + h/2), (lw, lw, h), wood, coll)
    make_box(f"{prefix}_L4", (x + w/2 - lw, y + d/2 - lw, z + h/2), (lw, lw, h), wood, coll)

def build_chair(prefix, x, y, z, coll):
    wood = get_mat("EM_M_door_wood", (0.48, 0.33, 0.20))
    # Assento
    make_box(f"{prefix}_SEAT", (x, y, z + 0.30), (0.35, 0.35, 0.04), wood, coll)
    # Encosto
    make_box(f"{prefix}_BACK", (x, y - 0.15, z + 0.50), (0.35, 0.04, 0.40), wood, coll)
    # Pernas
    lw = 0.04
    make_box(f"{prefix}_L1", (x - 0.15, y - 0.15, z + 0.15), (lw, lw, 0.30), wood, coll)
    make_box(f"{prefix}_L2", (x + 0.15, y - 0.15, z + 0.15), (lw, lw, 0.30), wood, coll)
    make_box(f"{prefix}_L3", (x - 0.15, y + 0.15, z + 0.15), (lw, lw, 0.30), wood, coll)
    make_box(f"{prefix}_L4", (x + 0.15, y + 0.15, z + 0.15), (lw, lw, 0.30), wood, coll)

def build_shelf(prefix, x, y, z, w, d, h, coll):
    wood = get_mat("EM_M_door_wood", (0.48, 0.33, 0.20))
    # Laterais e fundo
    make_box(f"{prefix}_L", (x - w/2, y, z + h/2), (0.03, d, h), wood, coll)
    make_box(f"{prefix}_R", (x + w/2, y, z + h/2), (0.03, d, h), wood, coll)
    make_box(f"{prefix}_B", (x, y + d/2, z + h/2), (w, 0.03, h), wood, coll)
    # Prateleiras
    for i in range(1, 4):
        make_box(f"{prefix}_S{i}", (x, y, z + (i * h / 4)), (w - 0.06, d - 0.02, 0.03), wood, coll)

def build_crib(prefix, x, y, z, coll):
    wood = get_mat("EM_M_door_wood", (0.48, 0.33, 0.20))
    white = get_mat("EM_M_floor_vinyl_white", (0.95, 0.95, 0.95))
    # Base e colchão
    make_box(f"{prefix}_BASE", (x, y, z + 0.25), (1.30, 0.70, 0.10), wood, coll)
    make_box(f"{prefix}_MAT", (x, y, z + 0.33), (1.25, 0.65, 0.06), white, coll)
    # Grades laterais (simplificado)
    make_box(f"{prefix}_L1", (x - 0.65, y, z + 0.55), (0.05, 0.70, 0.60), wood, coll)
    make_box(f"{prefix}_L2", (x + 0.65, y, z + 0.55), (0.05, 0.70, 0.60), wood, coll)
    make_box(f"{prefix}_F", (x, y - 0.35, z + 0.55), (1.30, 0.05, 0.60), wood, coll)
    make_box(f"{prefix}_Bk", (x, y + 0.35, z + 0.55), (1.30, 0.05, 0.60), wood, coll)

def build_counter(prefix, x, y, z, w, d, h, coll):
    inox = get_mat("EM_M_column_concrete", (0.80, 0.80, 0.80)) # Simulando inox
    make_box(f"{prefix}_MAIN", (x, y, z + h/2), (w, d, h), inox, coll)
    make_box(f"{prefix}_TOP", (x, y, z + h + 0.02), (w, d, 0.04), inox, coll)

# ============================================================ #
# 3. POSICIONAMENTO
# ============================================================ #
def populate_school(coll):
    # ---- SALA 01 a 04 (Mesas e Cadeiras) ----
    # Coordenadas centrais das salas (ver spaces.json)
    # SPC_CLASS_01: X=4.5, Y=4.4
    # SPC_CLASS_02: X=11.5, Y=4.4
    # SPC_CLASS_03: X=18.5, Y=4.4
    # SPC_CLASS_04: X=25.5, Y=4.4
    for i, cx in enumerate([4.5, 11.5, 18.5, 25.5]):
        # Mesa central
        build_table(f"P08_FURN_CLASS0{i+1}_TABLE", cx, 4.4, 0, 1.2, 0.6, 0.5, coll)
        # 4 cadeiras ao redor
        build_chair(f"P08_FURN_CLASS0{i+1}_CHAIR_1", cx, 4.4 - 0.5, 0, coll)
        build_chair(f"P08_FURN_CLASS0{i+1}_CHAIR_2", cx, 4.4 + 0.5, 0, coll)
        build_chair(f"P08_FURN_CLASS0{i+1}_CHAIR_3", cx - 0.8, 4.4, 0, coll)
        build_chair(f"P08_FURN_CLASS0{i+1}_CHAIR_4", cx + 0.8, 4.4, 0, coll)
        # Estante na parede norte (Y = 7.5)
        build_shelf(f"P08_FURN_CLASS0{i+1}_SHELF", cx, 7.5, 0, 0.8, 0.3, 1.2, coll)

    # ---- BERÇÁRIO 01 e 02 ----
    # BERC_01: X=4, Y=-3.9
    # BERC_02: X=10, Y=-3.9
    for i, cx in enumerate([4.0, 10.0]):
        # 2 berços na parede norte
        build_crib(f"P08_FURN_BERC0{i+1}_CRIB_1", cx - 0.8, -6.0, 0, coll)
        build_crib(f"P08_FURN_BERC0{i+1}_CRIB_2", cx + 0.8, -6.0, 0, coll)
        # Estante
        build_shelf(f"P08_FURN_BERC0{i+1}_SHELF", cx, -1.5, 0, 1.0, 0.3, 0.8, coll)

    # ---- COZINHA ----
    # KITCHEN: X=21.5, Y=-2.9
    build_counter("P08_FURN_KITCHEN_COUNTER_1", 21.5, -4.5, 0, 4.0, 0.6, 0.9, coll)
    build_counter("P08_FURN_KITCHEN_COUNTER_2", 19.5, -2.9, 0, 0.6, 3.0, 0.9, coll)

    # ---- REFEITÓRIO ----
    # CAFE: X=28, Y=-3.9
    # 2 mesas longas
    build_table("P08_FURN_CAFE_TABLE_1", 27, -4.5, 0, 2.4, 0.8, 0.55, coll)
    build_table("P08_FURN_CAFE_TABLE_2", 27, -2.0, 0, 2.4, 0.8, 0.55, coll)
    # Bancos (simplificados como blocos)
    wood = get_mat("EM_M_door_wood", (0.48, 0.33, 0.20))
    make_box("P08_FURN_CAFE_BENCH_1", (27, -5.2, 0.22), (2.4, 0.3, 0.44), wood, coll)
    make_box("P08_FURN_CAFE_BENCH_2", (27, -3.3, 0.22), (2.4, 0.3, 0.44), wood, coll)
    make_box("P08_FURN_CAFE_BENCH_3", (27, -1.2, 0.22), (2.4, 0.3, 0.44), wood, coll)

    # ---- MULTIUSO ----
    # MULTI: X=33, Y=-3.9
    build_shelf("P08_FURN_MULTI_SHELF_1", 32, -6.0, 0, 1.5, 0.4, 0.9, coll)
    build_shelf("P08_FURN_MULTI_SHELF_2", 35, -6.0, 0, 1.5, 0.4, 0.9, coll)
    build_table("P08_FURN_MULTI_TABLE", 33, -3.0, 0, 1.2, 0.6, 0.45, coll)

# ============================================================ #
# 4. EXPORTAÇÃO
# ============================================================ #
def export_glb():
    for o in bpy.context.selected_objects: o.select_set(False)
    root = bpy.data.collections.get("EMERALD_GENERATED")
    EXCLUDE = ("MARKER_SPHERE_", "OBSTACLE_SPHERE_", "HAZARD_SPHERE_", "ROUTE_RIBBON_")
    count = 0
    for o in root.all_objects:
        if o.type not in {"MESH", "EMPTY"}: continue
        if any(o.name.startswith(p) for p in EXCLUDE): continue
        o.select_set(True)
        count += 1
    
    bpy.ops.export_scene.gltf(
        filepath=GLB_OUT, export_format="GLB", 
        use_selection=True, export_yup=True, 
        export_apply=False, export_animations=False
    )
    print(f"[P08] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    coll = setup_collection()
    populate_school(coll)
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P08] Blend salvo. Mobiliário concluído.")