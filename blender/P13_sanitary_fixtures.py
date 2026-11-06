"""
P13_sanitary_fixtures.py — EMERALD-SCARLATE NORDESTE
Modela instalações sanitárias, cozinha e bebedouros.
"""
import bpy
import math
import os

def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        return os.path.dirname(p) if os.path.basename(p).lower() == "blender" else p
    home = os.path.expanduser("~")
    return os.path.join(home, "Desktop", "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
GLB_OUT = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")

# ============================================================ #
# 1. SETUP E MATERIAIS
# ============================================================ #
def setup_collection():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("Coleção EMERALD_GENERATED não encontrada.")
    
    coll_name = "P13_SANITARY"
    coll = bpy.data.collections.get(coll_name)
    if coll:
        for obj in list(coll.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(coll)
    
    coll = bpy.data.collections.new(coll_name)
    root.children.link(coll)
    return coll

def get_mat(name, fallback_color=(0.8, 0.8, 0.8)):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf and "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*fallback_color, 1.0)
    return m

# ============================================================ #
# 2. CONSTRUTORES
# ============================================================ #
def make_box(name, center, size, mat, coll, collider=False):
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
    
    mod = o.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = 0.01
    mod.segments = 2

    if collider:
        c = make_box("COLLIDER_" + name, center, size, get_mat("EM_invisible"), bpy.data.collections.get("EMERALD_GENERATED_COLLIDERS"))
        c.display_type = "WIRE"
        c.hide_render = True
        
    return o

def build_toilet(name, x, y, z, coll):
    white = get_mat("EM_M_floor_vinyl_white", (0.95, 0.95, 0.95))
    # Vaso (Base)
    make_box(name + "_BOWL", (x, y, z + 0.15), (0.35, 0.45, 0.30), white, coll, collider=True)
    # Caixa Acoplada
    make_box(name + "_TANK", (x, y + 0.20, z + 0.45), (0.35, 0.15, 0.40), white, coll)
    # Assento
    make_box(name + "_SEAT", (x, y - 0.05, z + 0.32), (0.38, 0.45, 0.04), white, coll)

def build_sink(name, x, y, z, coll):
    white = get_mat("EM_M_floor_vinyl_white", (0.95, 0.95, 0.95))
    metal = get_mat("EM_M_roof_metal", (0.7, 0.7, 0.7))
    # Cuba
    make_box(name + "_BASIN", (x, y, z + 0.40), (0.40, 0.30, 0.15), white, coll, collider=True)
    # Torneira
    make_box(name + "_FAUCET", (x, y + 0.10, z + 0.55), (0.04, 0.15, 0.15), metal, coll)

def build_mirror(name, x, y, z, coll):
    glass = get_mat("EM_M_glass_window", (0.7, 0.8, 0.9))
    make_box(name, (x, y, z + 0.6), (0.5, 0.02, 0.6), glass, coll)

def build_partition(name, x, y, z, coll):
    wood = get_mat("EM_M_door_wood", (0.4, 0.3, 0.2))
    make_box(name, (x, y, z + 1.0), (0.05, 1.0, 2.0), wood, coll, collider=True)

def build_kitchen_sink(name, x, y, z, coll):
    inox = get_mat("EM_M_column_concrete", (0.8, 0.8, 0.8))
    # Tanque industrial
    make_box(name + "_TANK", (x, y, z + 0.45), (1.0, 0.6, 0.90), inox, coll, collider=True)
    # Cuba afundada (visual)
    make_box(name + "_BASIN", (x, y, z + 0.85), (0.8, 0.4, 0.02), get_mat("EM_M_drain", (0.3, 0.3, 0.3)), coll)

def build_fountain(name, x, y, z, coll):
    metal = get_mat("EM_M_roof_metal", (0.7, 0.7, 0.7))
    base = get_mat("EM_M_column_concrete", (0.6, 0.6, 0.6))
    # Base
    make_box(name + "_BASE", (x, y, z + 0.4), (0.4, 0.4, 0.8), base, coll, collider=True)
    # Cuba infantil
    make_box(name + "_CUBAS", (x, y - 0.2, z + 0.7), (0.3, 0.1, 0.05), metal, coll)
    # Cuba adulto
    make_box(name + "_CUBA", (x, y - 0.2, z + 1.0), (0.3, 0.1, 0.05), metal, coll)

# ============================================================ #
# 3. POSICIONAMENTO
# ============================================================ #
def populate_wc(coll, base_x):
    # Banheiro 01: base_x = 13.0 (limites X: 13-16, Y: -3.4 a -0.9)
    # Banheiro 02: base_x = 16.0 (limites X: 16-19, Y: -3.4 a -0.9)
    
    # 1. Vasos no fundo (Y = -3.2) - Apontando para +Y
    build_toilet(f"FIX_WC_TOILET_1", base_x + 0.8, -3.2, 0, coll)
    build_toilet(f"FIX_WC_TOILET_2", base_x + 2.2, -3.2, 0, coll)
    
    # 2. Divisória entre os vasos (X = base_x + 1.5)
    build_partition(f"FIX_WC_PARTITION", base_x + 1.5, -3.0, 0, coll)
    
    # 3. Pias na parede esquerda (X = base_x + 0.2, Y = -1.8)
    # Como a parede esquerda é X=base_x, as pias ficam de frente para +X
    build_sink(f"FIX_WC_SINK_1", base_x + 0.25, -2.0, 0, coll)
    build_sink(f"FIX_WC_SINK_2", base_x + 0.25, -1.4, 0, coll)
    
    # 4. Espelhos acima das pias
    build_mirror(f"FIX_WC_MIRROR_1", base_x + 0.15, -2.0, 0, coll)
    build_mirror(f"FIX_WC_MIRROR_2", base_x + 0.15, -1.4, 0, coll)

def populate_kitchen(coll):
    # Cozinha: X 19-24, Y -4.9 a -0.9
    # Fundo em Y = -4.7 (perto da parede)
    build_kitchen_sink("FIX_KITCHEN_SINK", 19.5, -4.6, 0, coll)
    
    # Fogão (visual simplificado)
    inox = get_mat("EM_M_column_concrete", (0.8, 0.8, 0.8))
    make_box("FIX_KITCHEN_STOVE", (21.5, -4.6, 0.45), (1.0, 0.6, 0.90), inox, coll, collider=True)
    
    # Geladeira
    make_box("FIX_KITCHEN_FRIDGE", (23.0, -4.5, 0.9), (0.8, 0.7, 1.8), inox, coll, collider=True)

def populate_corridor(coll):
    # Bebedouro no corredor (X = 10, Y = -0.6 - perto da parede, longe da porta)
    build_fountain("FIX_FOUNTAIN_CORRIDOR", 10.0, -0.6, 0, coll)

# ============================================================ #
# 4. EXPORTAÇÃO
# ============================================================ #
def export_glb():
    for o in bpy.context.selected_objects: o.select_set(False)
    root = bpy.data.collections.get("EMERALD_GENERATED")
    EXCLUDE = ("MARKER_SPHERE_", "OBSTACLE_SPHERE_", "HAZARD_SPHERE_", "ROUTE_RIBBON_")
    
    count = 0
    for o in root.all_objects:
        if o.type not in {"MESH", "EMPTY", "LIGHT"}: continue
        if any(o.name.startswith(p) for p in EXCLUDE): continue
        o.select_set(True)
        count += 1
        
    bpy.ops.export_scene.gltf(
        filepath=GLB_OUT, export_format="GLB", 
        use_selection=True, export_yup=True, 
        export_apply=True,
        export_animations=False,
        export_lights=True,
        export_extras=True
    )
    print(f"[P13] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    coll = setup_collection()
    populate_wc(coll, 13.0) # WC 01
    populate_wc(coll, 16.0) # WC 02
    populate_kitchen(coll)
    populate_corridor(coll)
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P13] Blend salvo. Instalações sanitárias concluídas.")