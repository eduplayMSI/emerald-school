"""
P07_fix_floors.py — Força os materiais corretos nos pisos e reexporta o GLB.
"""
import bpy
import os

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

# Materiais corretos por ambiente
FLOOR_MATERIALS = {
    "FLOOR_CORRIDOR":     "EM_M_floor_ceramic_beige",
    "FLOOR_SPC_CLASS_01": "EM_M_floor_wood_ceramic",
    "FLOOR_SPC_CLASS_02": "EM_M_floor_wood_ceramic",
    "FLOOR_SPC_CLASS_03": "EM_M_floor_wood_ceramic",
    "FLOOR_SPC_CLASS_04": "EM_M_floor_wood_ceramic",
    "FLOOR_SPC_MULTI":    "EM_M_floor_wood_ceramic",
    "FLOOR_SPC_BERC_01":  "EM_M_floor_vinyl_white",
    "FLOOR_SPC_BERC_02":  "EM_M_floor_vinyl_white",
    "FLOOR_SPC_WC_01":    "EM_M_floor_ceramic_grey",
    "FLOOR_SPC_WC_02":    "EM_M_floor_ceramic_grey",
    "FLOOR_SPC_KITCHEN":  "EM_M_floor_ceramic_grey",
    "FLOOR_SPC_CAFE":     "EM_M_floor_ceramic_cafe",
    "FLOOR_PATIO":        "EM_M_patio_rubber",
}

def fix_materials():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("EMERALD_GENERATED ausente.")
        
    for obj_name, mat_name in FLOOR_MATERIALS.items():
        obj = bpy.data.objects.get(obj_name)
        mat = bpy.data.materials.get(mat_name)
        
        if not obj:
            print(f"[FIX] Objeto {obj_name} não encontrado.")
            continue
        if not mat:
            print(f"[FIX] Material {mat_name} não encontrado. Criando...")
            mat = bpy.data.materials.new(mat_name)
            mat.use_nodes = True
            
        # Limpa materiais antigos da malha e aplica o novo
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        
        # Força a substituição também no slot do objeto (garante a exportação)
        if obj.material_slots:
            obj.material_slots[0].material = mat
        else:
            obj.material_slots.link(obj.data.materials[0])
            
        print(f"[FIX] {obj_name} → {mat_name}")

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
    bpy.ops.export_scene.gltf(filepath=GLB_OUT, export_format="GLB", use_selection=True, export_yup=True)
    print(f"[FIX] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    fix_materials()
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[FIX] Blender salvo. Prossiga para a etapa Web.")