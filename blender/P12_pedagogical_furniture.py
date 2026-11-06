"""
P12_pedagogical_furniture.py — EMERALD-SCARLATE NORDESTE
Adiciona mobiliário pedagógico às salas, berçários e multiuso.
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
# 1. SETUP E CLEANUP
# ============================================================ #
def setup_collection():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("Coleção EMERALD_GENERATED não encontrada.")
    
    # Limpa execuções anteriores para manter a idempotência
    coll = bpy.data.collections.get("P12_PEDAGOGICAL_FURNITURE")
    if coll:
        for obj in list(coll.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(coll)
    
    coll = bpy.data.collections.new("P12_PEDAGOGICAL_FURNITURE")
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
    
    # Arredondar levemente as bordas (Bevel Modifier)
    mod = o.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = 0.02
    mod.segments = 2

    if collider:
        c = make_box("COLLIDER_" + name, center, size, get_mat("EM_invisible"), bpy.data.collections.get("EMERALD_GENERATED_COLLIDERS"))
        c.display_type = "WIRE"
        c.hide_render = True
        
    return o

# ============================================================ #
# 3. MOBILIÁRIO ESPECÍFICO
# ============================================================ #
def create_panel(name, x, y, z, w, h, coll):
    mat = get_mat("EM_M_playground_equipment", (0.2, 0.6, 0.8)) # Azul
    make_box(name, (x, y, z + h/2), (w, 0.05, h), mat, coll, collider=False)

def create_rug(name, x, y, w, d, coll):
    mat = get_mat("EM_M_floor_ceramic_cafe", (0.8, 0.8, 0.8)) # Cinza claro
    make_box(name, (x, y, 0.01), (w, d, 0.02), mat, coll, collider=False)

def create_cubby(name, x, y, z, w, d, h, coll):
    wood = get_mat("EM_M_door_wood", (0.48, 0.33, 0.20))
    # Estrutura externa
    make_box(name + "_FRAME", (x, y, z + h/2), (w, d, h), wood, coll, collider=True)
    # Furos (simulados por caixas internas escuras)
    inner = get_mat("EM_M_column_concrete", (0.2, 0.2, 0.2))
    cols = 2
    rows = 3
    for c in range(cols):
        for r in range(rows):
            cx = x - w/2 + w/(cols*2) + c*(w/cols)
            cz = z + h/(rows*2) + r*(h/rows)
            make_box(f"{name}_HOLE_{c}_{r}", (cx, y - d/2 + 0.05, cz), (w/cols - 0.05, 0.02, h/rows - 0.05), inner, coll)

def create_changing_table(name, x, y, z, coll):
    wood = get_mat("EM_M_door_wood", (0.48, 0.33, 0.20))
    white = get_mat("EM_M_floor_vinyl_white", (0.95, 0.95, 0.95))
    # Base
    make_box(name + "_BASE", (x, y, z + 0.4), (1.2, 0.6, 0.8), wood, coll, collider=True)
    # Colchonete
    make_box(name + "_MAT", (x, y, z + 0.82), (1.1, 0.5, 0.05), white, coll)

def create_armchair(name, x, y, z, coll):
    fabric = get_mat("EM_M_wall_sun_yellow", (0.9, 0.8, 0.3))
    make_box(name + "_SEAT", (x, y, z + 0.2), (0.8, 0.8, 0.4), fabric, coll, collider=True)
    make_box(name + "_BACK", (x, y + 0.35, z + 0.5), (0.8, 0.1, 0.6), fabric, coll)
    make_box(name + "_ARM_L", (x - 0.4, y, z + 0.35), (0.1, 0.8, 0.3), fabric, coll)
    make_box(name + "_ARM_R", (x + 0.4, y, z + 0.35), (0.1, 0.8, 0.3), fabric, coll)

def create_book_display(name, x, y, z, coll):
    wood = get_mat("EM_M_door_wood", (0.48, 0.33, 0.20))
    # Estrutura inclinada (simplificada)
    make_box(name + "_FRAME", (x, y, z + 0.45), (1.0, 0.4, 0.9), wood, coll, collider=True)
    # Prateleira frontal
    make_box(name + "_SHELF", (x, y - 0.2, z + 0.3), (0.9, 0.1, 0.05), wood, coll)

def create_cushion(name, x, y, z, coll):
    mat = get_mat("EM_M_patio_rubber", (0.7, 0.3, 0.3)) # Vermelho
    make_box(name, (x, y, z + 0.1), (0.5, 0.5, 0.2), mat, coll, collider=False)

# ============================================================ #
# 4. POSICIONAMENTO
# ============================================================ #
def populate_classrooms(coll):
    # Salas 01 a 04
    # Coordenadas Blender (X, Y). Centro da sala: X=4.5, 11.5, 18.5, 25.5; Y=4.4.
    # A porta fica em Y=0.9 (parede sul), fundo da sala em Y=7.9.
    for i, cx in enumerate([4.5, 11.5, 18.5, 25.5]):
        # 1. Painel Pedagógico na parede Norte (Y=7.85)
        create_panel(f"FURN_CLASS0{i+1}_PANEL", cx, 7.85, 1.2, 3.0, 1.5, coll)
        
        # 2. Tapete de Leitura no centro-fundo (longe da mesa e da porta)
        create_rug(f"FURN_CLASS0{i+1}_RUG", cx, 6.0, 2.5, 2.0, coll)
        
        # 3. Escaninho na parede Oeste (X=1.1) ou Leste (X=7.9)
        # Vamos colocar na parede Leste, perto do fundo
        create_cubby(f"FURN_CLASS0{i+1}_CUBBY", cx + 3.0, 6.5, 0, 1.2, 0.4, 1.0, coll)

def populate_nursery(coll):
    # Berçários 01 e 02
    # Centro: X=4.0, 10.0; Y=-3.9.
    # A porta fica em Y=0.9 (parede norte), fundo em Y=-6.9.
    for i, cx in enumerate([4.0, 10.0]):
        # 1. Trocador na parede Oeste (X=1.1)
        create_changing_table(f"FURN_BERC0{i+1}_CHANGER", cx - 2.5, -5.0, 0, coll)
        
        # 2. Poltrona no canto Leste (X=6.5, Y=-5.5)
        create_armchair(f"FURN_BERC0{i+1}_ARMCHAIR", cx + 2.0, -5.5, 0, coll)
        
        # 3. Tapete de Estimulação no centro
        create_rug(f"FURN_BERC0{i+1}_RUG", cx, -3.0, 2.0, 2.0, coll)

def populate_multiuso(coll):
    # Multiuso: Centro: X=33.0, Y=-3.9. Fundo: Y=-6.9.
    # 1. Expositor de livros na parede Norte (Y=-6.85)
    create_book_display("FURN_MULTI_DISPLAY_01", 31.0, -6.7, 0, coll)
    create_book_display("FURN_MULTI_DISPLAY_02", 35.0, -6.7, 0, coll)
    
    # 2. Almofadas no chão para leitura
    create_cushion("FURN_MULTI_CUSHION_01", 32.0, -4.0, 0, coll)
    create_cushion("FURN_MULTI_CUSHION_02", 33.0, -3.5, 0, coll)
    create_cushion("FURN_MULTI_CUSHION_03", 34.0, -4.5, 0, coll)

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
        export_apply=True, # IMPORTANTE: Aplica os modificadores Bevel
        export_animations=False,
        export_lights=True,
        export_extras=True
    )
    print(f"[P12] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    coll = setup_collection()
    populate_classrooms(coll)
    populate_nursery(coll)
    populate_multiuso(coll)
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P12] Blend salvo. Mobiliário pedagógico instalado.")