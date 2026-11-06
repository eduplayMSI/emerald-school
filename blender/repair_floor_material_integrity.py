"""
repair_floor_material_integrity.py — Operação Floor Restore Final
Força os materiais corretos E recalcula as normais das faces (inverte o piso).
"""
import bpy
import bmesh
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

FLOOR_MAP = {
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
    "FLOOR_PATIO":        "EM_M_patio_rubber"
}

def fix_normals_and_materials():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("Coleção EMERALD_GENERATED não encontrada.")
    
    repaired_count = 0
    for obj_name, mat_name in FLOOR_MAP.items():
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
            
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(mat_name)
            mat.use_nodes = True
            
        # 1. Força o Material
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        if len(obj.material_slots) == 0:
            obj.material_slots.link(obj.data.materials[0])
        obj.material_slots[0].material = mat
        
        # 2. Recalcula as normais (faz as faces apontarem para cima)
        me = obj.data
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        me.update()
        
        repaired_count += 1
        print(f"[RESTORE] ✓ {obj_name} (Normais Corrigidas) → {mat_name}")

    print(f"[RESTORE] {repaired_count} pisos reparados e com normais corrigidas.")

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
        export_lights=True,
        export_extras=True
    )
    print(f"[RESTORE] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    fix_normals_and_materials()
    export_final()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[RESTORE] Blender salvo. O piso agora está sólido.")