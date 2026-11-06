"""
P15_playground.py — EMERALD-SCARLATE NORDESTE
Expansão do parque infantil com gangorra, casinha, túnel e painel sensorial.
"""
import bpy
import bmesh
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
    
    coll_name = "P15_PLAYGROUND"
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
def make_box(name, center, size, mat, coll, collider=False, rot=(0,0,0)):
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
    o.rotation_euler = rot
    o.data.materials.append(mat)
    coll.objects.link(o)
    
    mod = o.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = 0.02
    mod.segments = 2

    if collider:
        c = make_box("COLLIDER_" + name, center, size, get_mat("EM_invisible"), bpy.data.collections.get("EMERALD_GENERATED_COLLIDERS"), rot=rot)
        c.display_type = "WIRE"
        c.hide_render = True
        
    return o

def build_seesaw(name, x, y, z, coll):
    metal = get_mat("EM_M_roof_metal", (0.6, 0.6, 0.6))
    plastic = get_mat("EM_M_playground_equipment", (0.2, 0.6, 0.8))
    # Base (Fulcro)
    make_box(name + "_BASE", (x, y, z + 0.25), (0.3, 0.3, 0.5), metal, coll, collider=True)
    # Tábua inclinada (rotacionada 15 graus)
    make_box(name + "_BEAM", (x, y, z + 0.55), (0.1, 2.5, 0.05), plastic, coll, collider=True, rot=(math.radians(15), 0, 0))
    # Assentos
    make_box(name + "_SEAT_1", (x, y - 1.2, z + 0.4), (0.3, 0.4, 0.05), plastic, coll)
    make_box(name + "_SEAT_2", (x, y + 1.2, z + 0.7), (0.3, 0.4, 0.05), plastic, coll)
    # Pegadores
    make_box(name + "_HANDLE_1", (x, y - 1.0, z + 0.7), (0.05, 0.05, 0.3), metal, coll)
    make_box(name + "_HANDLE_2", (x, y + 1.0, z + 1.0), (0.05, 0.05, 0.3), metal, coll)

def build_playhouse(name, x, y, z, coll):
    wood = get_mat("EM_M_door_wood", (0.6, 0.4, 0.2))
    roof_mat = get_mat("EM_M_roof_terracotta", (0.7, 0.3, 0.2))
    # Piso da casinha
    make_box(name + "_FLOOR", (x, y, z + 0.05), (1.6, 1.6, 0.1), wood, coll)
    # Paredes laterais (deixando a frente aberta)
    make_box(name + "_WALL_L", (x - 0.75, y, z + 0.75), (0.1, 1.6, 1.4), wood, coll, collider=True)
    make_box(name + "_WALL_R", (x + 0.75, y, z + 0.75), (0.1, 1.6, 1.4), wood, coll, collider=True)
    make_box(name + "_WALL_B", (x, y + 0.75, z + 0.75), (1.6, 0.1, 1.4), wood, coll, collider=True)
    # Telhado de duas águas (simplificado)
    make_box(name + "_ROOF_L", (x - 0.4, y, z + 1.6), (1.0, 1.8, 0.1), roof_mat, coll, rot=(0, math.radians(-35), 0))
    make_box(name + "_ROOF_R", (x + 0.4, y, z + 1.6), (1.0, 1.8, 0.1), roof_mat, coll, rot=(0, math.radians(35), 0))
    # Janelas (buracos na parede)
    make_box(name + "_WINDOW", (x - 0.75, y + 0.4, z + 0.9), (0.1, 0.3, 0.3), get_mat("EM_M_glass_window"), coll)

def build_tunnel(name, x, y, z, coll):
    concrete = get_mat("EM_M_column_concrete", (0.8, 0.8, 0.8))
    # Túnel feito com blocos curvos (simulando um arco)
    for i in range(5):
        angle = math.radians(-40 + i * 20)
        # Deslocamento em X e Z baseado no arco
        dx = math.sin(angle) * 0.5
        dz = math.cos(angle) * 0.5
        make_box(f"{name}_SEG_{i}", (x + dx, y, z + 0.6 + dz), (0.2, 1.2, 0.2), concrete, coll, collider=True, rot=(0, -angle, 0))

def build_sensory_panel(name, x, y, z, coll):
    metal = get_mat("EM_M_roof_metal", (0.6, 0.6, 0.6))
    # Frame de metal
    make_box(name + "_FRAME", (x, y, z + 0.6), (0.05, 0.8, 1.2), metal, coll, collider=True)
    # Elementos sensoriais coloridos
    colors = [(0.8, 0.2, 0.2), (0.2, 0.8, 0.2), (0.2, 0.2, 0.8), (0.8, 0.8, 0.2)]
    for i, c in enumerate(colors):
        mat = get_mat(f"EM_SENSORY_{i}", c)
        make_box(f"{name}_ITEM_{i}", (x + 0.05, y, z + 0.2 + i*0.25), (0.05, 0.2, 0.2), mat, coll)

def build_rubber_pad(name, x, y, z, w, d, coll):
    rubber = get_mat("EM_M_patio_rubber", (0.7, 0.3, 0.3))
    make_box(name, (x, y, z + 0.02), (w, d, 0.04), rubber, coll, collider=False)

# ============================================================ #
# 3. POSICIONAMENTO
# ============================================================ #
def populate_playground(coll):
    # Área do parque: X: 4 a 12, Y: 16 a 20
    # Z base = -0.02 (nível da areia)
    base_z = -0.02
    
    # 1. Piso emborrachado sob o balanço e a gangorra
    build_rubber_pad("PLAY_RUBBER_PAD_01", 8.0, 17.0, base_z, 4.0, 3.0, coll)
    
    # 2. Gangorra (Seesaw) no centro-sul
    build_seesaw("PLAY_SEESAW_01", 8.0, 17.0, base_z, coll)
    
    # 3. Casinha (Playhouse) no fundo (norte)
    build_playhouse("PLAY_PLAYHOUSE_01", 8.0, 19.5, base_z, coll)
    
    # 4. Túnel de concreto a oeste (próximo ao escorregador)
    build_tunnel("PLAY_TUNNEL_01", 6.0, 16.5, base_z, coll)
    
    # 5. Painel sensorial a leste (próximo ao balanço)
    build_sensory_panel("PLAY_SENSORY_01", 11.5, 16.5, base_z, coll)

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
    print(f"[P15] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    coll = setup_collection()
    populate_playground(coll)
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P15] Blend salvo. Parque infantil expandido.")