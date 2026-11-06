"""
P21_lighting_fixtures.py — EMERALD-SCARLATE NORDESTE
Cria luminárias físicas e gera o manifesto de luzes para o Three.js.
"""
import bpy
import os
import json

def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        return os.path.dirname(p) if os.path.basename(p).lower() == "blender" else p
    home = os.path.expanduser("~")
    return os.path.join(home, "Desktop", "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
GLB_OUT = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")
JSON_OUT = os.path.join(PROJECT_ROOT, "data", "lighting_manifest.json")

# ============================================================ #
# 1. SETUP E MATERIAIS
# ============================================================ #
def setup_collection():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("Coleção EMERALD_GENERATED não encontrada.")
    
    coll_name = "P21_LIGHT_FIXTURES"
    coll = bpy.data.collections.get(coll_name)
    if coll:
        for obj in list(coll.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(coll)
    
    coll = bpy.data.collections.new(coll_name)
    root.children.link(coll)
    return coll

def get_mat(name, color, rough=0.5, metal=0.0, emission_color=None, emission_strength=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Roughness"].default_value = rough
            bsdf.inputs["Metallic"].default_value = metal
            if emission_color:
                bsdf.inputs["Emission Color"].default_value = (*emission_color, 1.0)
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m

# ============================================================ #
# 2. CONSTRUTOR DE LUMINÁRIA
# ============================================================ #
def build_fixture(name, x, y, z, width, depth, fixture_type, coll, manifest_list):
    frame_mat = get_mat("EM_M_LIGHT_FRAME", (0.3, 0.3, 0.3), rough=0.4, metal=0.8)
    diff_mat = get_mat("EM_M_LIGHT_DIFFUSER", (0.9, 0.9, 0.9), rough=0.2, 
                       emission_color=(1.0, 0.95, 0.85), emission_strength=5.0)
    
    # Geometria da Luminária (Frame + Difusor)
    if fixture_type == "panel":
        # Moldura
        make_box(f"{name}_FRAME", (x, y, z), (width, depth, 0.05), frame_mat, coll)
        # Difusor (Ligeiramente abaixo para não conflitar)
        make_box(f"{name}_DIFFUSER", (x, y, z - 0.026), (width - 0.02, depth - 0.02, 0.01), diff_mat, coll)
        light_type = "area"
        intensity = width * depth * 30 # Intensidade baseada na área
    elif fixture_type == "tube":
        # Tubo cilíndrico (representado por caixa achatada)
        make_box(f"{name}_FRAME", (x, y, z), (width, depth, 0.08), frame_mat, coll)
        make_box(f"{name}_DIFFUSER", (x, y, z - 0.041), (width - 0.05, depth - 0.02, 0.01), diff_mat, coll)
        light_type = "point"
        intensity = 80

    # Adiciona ao Manifesto JSON
    manifest_list.append({
        "id": name,
        "type": light_type,
        "pos": [x, -y, z - 0.1], # Conversão Blender(X,Y,Z) -> Web(X,Z,-Y)
        "color": "#FFF2D9",
        "intensity": intensity,
        "distance": 8.0 if light_type == "point" else 6.0,
        "castShadow": False # Desativado para performance, exceto se especificado
    })

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

# ============================================================ #
# 3. POSICIONAMENTO E MANIFESTO
# ============================================================ #
def populate_lights(coll):
    manifest = []
    
    # Corredor (X: 1 a 37, Y: 0). Espaçamento de 5m. Z = 2.75 (abaixo do teto de 2.85)
    for i, x in enumerate([3, 8, 13, 18, 23, 28, 33]):
        build_fixture(f"LIGHT_CORR_{i+1:02d}", x, 0, 2.75, 0.2, 1.2, "tube", coll, manifest)
        
    # Salas de Aula (X: 4.5, 11.5, 18.5, 25.5. Y: 4.4. Z: 2.9)
    for i, x in enumerate([4.5, 11.5, 18.5, 25.5]):
        build_fixture(f"LIGHT_CLASS_{i+1:02d}", x, 4.4, 2.9, 1.2, 1.2, "panel", coll, manifest)
        
    # Berçários (X: 4.0, 10.0. Y: -3.9. Z: 2.9)
    for i, x in enumerate([4.0, 10.0]):
        build_fixture(f"LIGHT_BERC_{i+1:02d}", x, -3.9, 2.9, 1.2, 1.2, "panel", coll, manifest)

    # Multiuso (X: 33.0. Y: -3.9)
    build_fixture("LIGHT_MULTI_01", 33.0, -3.9, 2.9, 1.5, 1.5, "panel", coll, manifest)

    # Refeitório (X: 27.0, 30.0. Y: -3.9)
    for i, x in enumerate([26.0, 29.0]):
        build_fixture(f"LIGHT_CAFE_{i+1:02d}", x, -3.9, 2.9, 1.5, 1.5, "panel", coll, manifest)

    # Cozinha (X: 21.5. Y: -2.9)
    build_fixture("LIGHT_KITCHEN_01", 21.5, -2.9, 2.9, 1.0, 1.0, "panel", coll, manifest)

    # Sanitários (X: 14.5, 17.5. Y: -2.1. Z: 2.7)
    for i, x in enumerate([14.5, 17.5]):
        build_fixture(f"LIGHT_WC_{i+1:02d}", x, -2.1, 2.7, 0.5, 0.5, "panel", coll, manifest)

    # Área Externa (Pátio Coberto) - Z=3.4
    build_fixture("LIGHT_PATIO_01", 8.0, 11.5, 3.4, 2.0, 1.0, "panel", coll, manifest)

    # Salva o manifesto
    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump({"lights": manifest}, f, indent=2)
    print(f"[P21] {len(manifest)} luminárias criadas e manifesto exportado.")

# ============================================================ #
# 4. EXPORTAÇÃO
# ============================================================ #
def export_final():
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
        export_lights=True, # Exporta as luzes do Blender (se houver)
        export_extras=True
    )
    print(f"[P21] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    coll = setup_collection()
    populate_lights(coll)
    export_final()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P21] Blender salvo. Prossiga para a Etapa Web.")