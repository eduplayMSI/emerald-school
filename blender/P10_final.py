"""
P10_final.py — EMERALD-SCARLATE NORDESTE
Consolida materiais, mobiliário e exporta a versão de release.
"""
import bpy
import os

def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        return os.path.dirname(p) if os.path.basename(p).lower() == "blender" else p
    return os.path.join(os.path.expanduser("~"), "Desktop", "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
GLB_OUT = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")

def enforce_materials():
    # Garante que os materiais da biblioteca P07 estão aplicados corretamente
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root: raise RuntimeError("Base EMERALD_GENERATED não encontrada.")
    
    mapped_count = 0
    for obj in root.all_objects:
        if obj.type != 'MESH': continue
        for slot in obj.material_slots:
            if not slot.material: continue
            if slot.material.name.startswith("EM_") and not slot.material.name.startswith("EM_M_"):
                # Mapeamento de emergência caso P07 não tenha rodado
                old = slot.material.name
                if "floor" in old: new = "EM_M_floor_ceramic_beige"
                elif "wall" in old: new = "EM_M_wall_plaster_white"
                else: continue
                
                new_mat = bpy.data.materials.get(new)
                if new_mat:
                    slot.material = new_mat
                    mapped_count += 1
    print(f"[P10] {mapped_count} materiais corrigidos à força no Blender.")

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
        export_apply=True, # IMPORTANTE: Aplica modificadores e escala
        export_animations=False,
        export_lights=True,
        export_extras=True
    )
    print(f"[P10] GLB de Release Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    enforce_materials()
    export_final()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P10] Exportação concluída. Teste no navegador.")