"""
P19_visual_integrity.py — Operação Visual Integrity
Corrige normais invertidas em toda a escola e resolve Z-fighting de grama/rejunte.
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

def fix_normals_and_zfighting():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("Coleção EMERALD_GENERATED não encontrada.")
    
    fixed_normals = 0
    fixed_zfight = 0

    for obj in root.all_objects:
        if obj.type != 'MESH':
            continue

        # 1. CORREÇÃO DE Z-FIGHTING (Cintilação)
        # Eleva a grama e a terra para não encostarem no terreno
        if obj.name.startswith("P06_GRASS_PATCH") or obj.name.startswith("P06_EARTH"):
            obj.location.z = -0.02 # Antes era -0.04 e -0.045
            
        # Eleva o rejunte (grout) para não encostar no piso
        if obj.name.startswith("P06_GROUT") or obj.name.startswith("P06_PAVE_GRID"):
            obj.location.z += 0.015 # Antes tinha offset de 0.003, agora fica 1.5cm acima
            
        fixed_zfight += 1

        # 2. CORREÇÃO DE NORMAIS (Piso Verde / Transparência)
        me = obj.data
        bm = bmesh.new()
        bm.from_mesh(me)
        
        # Inverte a face se ela estiver apontando para dentro
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        
        bm.to_mesh(me)
        bm.free()
        me.update()
        
        fixed_normals += 1

    print(f"[P19] {fixed_normals} malhas tiveram as normais recalculadas.")
    print(f"[P19] {fixed_zfight} superfícies de detalhe foram elevadas para evitar cintilação.")

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
    print(f"[P19] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    fix_normals_and_zfighting()
    export_final()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P19] Blender salvo. Prossiga para a Etapa Web.")