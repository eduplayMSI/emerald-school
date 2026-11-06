"""
P14_service_furniture.py — EMERALD-SCARLATE NORDESTE
Mobiliário para Cozinha, Refeitório e Apoio.
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
    
    coll_name = "P14_SERVICE_FURNITURE"
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
# 2. CONSTRUTORES BÁSICOS
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

# ============================================================ #
# 3. MOBILIÁRIO ESPECÍFICO
# ============================================================ #
def build_upper_cabinet(name, x, y, z, w, d, h, coll):
    """Armário aéreo (parede) para cozinha."""
    wood = get_mat("EM_M_door_wood", (0.4, 0.3, 0.2))
    make_box(name, (x, y, z + h/2 + 1.5), (w, d, h), wood, coll, collider=False)

def build_prep_table(name, x, y, z, w, d, h, coll):
    """Mesa de preparo em inox."""
    inox = get_mat("EM_M_column_concrete", (0.8, 0.8, 0.8))
    # Tampo
    make_box(name + "_TOP", (x, y, z + h - 0.02), (w, d, 0.04), inox, coll, collider=True)
    # Pernas
    lw = 0.05
    make_box(name + "_L1", (x - w/2 + lw, y - d/2 + lw, z + h/2), (lw, lw, h), inox, coll)
    make_box(name + "_L2", (x + w/2 - lw, y - d/2 + lw, z + h/2), (lw, lw, h), inox, coll)
    make_box(name + "_L3", (x - w/2 + lw, y + d/2 - lw, z + h/2), (lw, lw, h), inox, coll)
    make_box(name + "_L4", (x + w/2 - lw, y + d/2 - lw, z + h/2), (lw, lw, h), inox, coll)
    # Prateleira inferior
    make_box(name + "_SHELF", (x, y, z + 0.15), (w - 0.1, d - 0.1, 0.03), inox, coll)

def build_serving_counter(name, x, y, z, w, d, h, coll):
    """Balcão de distribuição do refeitório."""
    stone = get_mat("EM_M_floor_ceramic_grey", (0.7, 0.7, 0.7))
    base = get_mat("EM_M_door_wood", (0.5, 0.4, 0.3))
    # Base
    make_box(name + "_BASE", (x, y, z + h/2 - 0.05), (w, d, h - 0.1), base, coll, collider=True)
    # Tampo (granito/cerâmica)
    make_box(name + "_TOP", (x, y, z + h - 0.02), (w + 0.1, d + 0.1, 0.04), stone, coll)
    # Proteção de vidro (sneeze guard)
    glass = get_mat("EM_M_glass_window", (0.8, 0.9, 0.9))
    make_box(name + "_GLASS", (x, y - 0.1, z + h + 0.3), (w - 0.2, 0.02, 0.4), glass, coll)

def build_cafe_chair(name, x, y, z, coll):
    """Cadeira infantil para o refeitório."""
    wood = get_mat("EM_M_door_wood", (0.6, 0.5, 0.3))
    make_box(name + "_SEAT", (x, y, z + 0.35), (0.35, 0.35, 0.04), wood, coll, collider=True)
    make_box(name + "_BACK", (x, y + 0.15, z + 0.55), (0.35, 0.04, 0.4), wood, coll)
    lw = 0.04
    make_box(name + "_L1", (x - 0.15, y - 0.15, z + 0.17), (lw, lw, 0.35), wood, coll)
    make_box(name + "_L2", (x + 0.15, y - 0.15, z + 0.17), (lw, lw, 0.35), wood, coll)
    make_box(name + "_L3", (x - 0.15, y + 0.15, z + 0.17), (lw, lw, 0.35), wood, coll)
    make_box(name + "_L4", (x + 0.15, y + 0.15, z + 0.17), (lw, lw, 0.35), wood, coll)

def build_storage_shelf(name, x, y, z, w, d, h, coll):
    """Estante de metal para apoio."""
    metal = get_mat("EM_M_roof_metal", (0.6, 0.6, 0.6))
    # Estrutura
    make_box(name + "_L", (x - w/2, y, z + h/2), (0.03, d, h), metal, coll, collider=True)
    make_box(name + "_R", (x + w/2, y, z + h/2), (0.03, d, h), metal, coll)
    make_box(name + "_B", (x, y + d/2, z + h/2), (w, 0.02, h), metal, coll)
    # Prateleiras
    for i in range(1, 4):
        make_box(f"{name}_S{i}", (x, y, z + (i * h / 4)), (w - 0.06, d - 0.02, 0.02), metal, coll)

# ============================================================ #
# 4. POSICIONAMENTO
# ============================================================ #
def populate_kitchen(coll):
    # Cozinha: X 19-24, Y -4.9 a -0.9
    # Armários aéreos na parede do fundo (Y = -4.85)
    build_upper_cabinet("FURN_KITCHEN_UPPER_CAB_1", 20.0, -4.85, 0, 1.5, 0.35, 0.7, coll)
    build_upper_cabinet("FURN_KITCHEN_UPPER_CAB_2", 22.5, -4.85, 0, 1.5, 0.35, 0.7, coll)
    
    # Mesa de preparo no centro (X = 21.5, Y = -3.0)
    build_prep_table("FURN_KITCHEN_PREP_TABLE", 21.5, -3.0, 0, 2.0, 0.8, 0.9, coll)
    
    # Estante de apoio na parede leste (X = 23.85, Y = -2.5)
    build_storage_shelf("FURN_KITCHEN_SHELF", 23.6, -2.5, 0, 0.4, 1.5, 2.0, coll)

def populate_cafe(coll):
    # Refeitório: X 24-32, Y -6.9 a -0.9
    # O P08 já colocou 2 mesas (X=27, Y=-4.5 e -2.0) e 3 bancos.
    # Vamos adicionar um Balcão de Distribuição na parede Leste (X=31.5)
    build_serving_counter("FURN_CAFE_SERVING_COUNTER", 31.5, -3.5, 0, 0.8, 3.0, 0.9, coll)
    
    # Adicionar 4 cadeiras infantis para complementar as mesas
    build_cafe_chair("FURN_CAFE_CHAIR_1", 25.8, -4.5, 0, coll)
    build_cafe_chair("FURN_CAFE_CHAIR_2", 28.2, -4.5, 0, coll)
    build_cafe_chair("FURN_CAFE_CHAIR_3", 25.8, -2.0, 0, coll)
    build_cafe_chair("FURN_CAFE_CHAIR_4", 28.2, -2.0, 0, coll)

def populate_multiuso(coll):
    # Multiuso: X 29-37, Y -6.9 a -0.9
    # Armário de apoio na parede Leste (X = 36.5)
    wood = get_mat("EM_M_door_wood", (0.5, 0.4, 0.3))
    make_box("FURN_MULTI_CABINET", (36.5, -3.9, 0.9), (0.5, 1.2, 1.8), wood, coll, collider=True)

# ============================================================ #
# 5. EXPORTAÇÃO
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
    print(f"[P14] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    coll = setup_collection()
    populate_kitchen(coll)
    populate_cafe(coll)
    populate_multiuso(coll)
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P14] Blend salvo. Mobiliário de serviço concluído.")