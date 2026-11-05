"""
P09_lighting.py — EMERALD-SCARLATE NORDESTE
Configura iluminação solar e de interiores, e exporta GLB com luzes.
"""
import bpy
import math
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

def setup_lighting():
    # 1. Limpar luzes antigas do Emerald
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("Coleção EMERALD_GENERATED ausente.")
        
    for obj in list(root.all_objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Criar coleção de luzes
    coll_name = "P09_LIGHTING"
    coll = bpy.data.collections.get(coll_name)
    if not coll:
        coll = bpy.data.collections.new(coll_name)
        root.children.link(coll)

    # 3. Sol (Nordeste, 45 graus, luz quente)
    sun_data = bpy.data.lights.new(name="P09_SUN", type='SUN')
    sun_data.energy = 4.5
    sun_data.color = (1.0, 0.95, 0.85)
    sun_data.angle = math.radians(2.0) # Sombras ligeiramente suaves
    
    sun = bpy.data.objects.new(name="P09_SUN", object_data=sun_data)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    coll.objects.link(sun)

    # 4. Luzes de Interior (Simulação de Luminárias LED)
    # Adicionando luzes pontuais em corredor e salas
    rooms = [
        ("FLOOR_CORRIDOR", 15.0, 0.0, 2.7),
        ("SPC_CLASS_01", 4.5, 4.4, 2.8),
        ("SPC_CLASS_02", 11.5, 4.4, 2.8),
        ("SPC_CLASS_03", 18.5, 4.4, 2.8),
        ("SPC_CLASS_04", 25.5, 4.4, 2.8),
        ("SPC_BERC_01", 4.0, -3.9, 2.8),
        ("SPC_BERC_02", 10.0, -3.9, 2.8),
        ("SPC_CAFE", 28.0, -3.9, 2.8)
    ]

    for room_id, x, y, z in rooms:
        light_data = bpy.data.lights.new(name=f"P09_INTERIOR_{room_id}", type='POINT')
        light_data.energy = 150.0  # Watts
        light_data.color = (1.0, 0.95, 0.9) # Branco quente
        light_data.shadow_soft_size = 0.5
        
        light_obj = bpy.data.objects.new(name=f"P09_INTERIOR_{room_id}", object_data=light_data)
        light_obj.location = (x, y, z)
        coll.objects.link(light_obj)

    print(f"[P09] {len(coll.objects)} luzes configuradas no Blender.")

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
        export_apply=False, export_animations=False,
        export_lights=True, # Exporta as luzes via KHR_lights_punctual
        export_extras=True
    )
    print(f"[P09] GLB Exportado: {GLB_OUT} ({count} objetos, luzes incluídas)")

if __name__ == "__main__":
    setup_lighting()
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P09] Blend salvo. Prossiga para a Etapa 4.")