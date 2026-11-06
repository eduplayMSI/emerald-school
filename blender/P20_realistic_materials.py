"""
P20_realistic_materials.py — EMERALD-SCARLATE NORDESTE
Redesenho da paleta cromática e aplicação de materiais PBR realistas.
"""
import bpy
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
# 1. DEFINIÇÃO DA BIBLIOTECA DE MATERIAIS PBR
# ============================================================ #
MATERIAL_LIBRARY = {
    "EM_M_WALL_INTERIOR_MAIN":  {"color": (0.90, 0.87, 0.79, 1.0), "rough": 0.9, "metal": 0.0},
    "EM_M_WALL_INTERIOR_ACCENT":{"color": (0.64, 0.71, 0.62, 1.0), "rough": 0.9, "metal": 0.0},
    "EM_M_WALL_EXTERNAL":       {"color": (0.82, 0.78, 0.72, 1.0), "rough": 0.85,"metal": 0.0},
    "EM_M_FLOOR_INTERIOR_CERAMIC":{"color": (0.72, 0.72, 0.72, 1.0), "rough": 0.45,"metal": 0.0},
    "EM_M_FLOOR_INTERIOR_WOOD": {"color": (0.55, 0.42, 0.30, 1.0), "rough": 0.65,"metal": 0.0},
    "EM_M_FLOOR_INTERIOR_VINYL":{"color": (0.88, 0.88, 0.85, 1.0), "rough": 0.55,"metal": 0.0},
    "EM_M_FLOOR_INTERIOR_WC":   {"color": (0.49, 0.52, 0.54, 1.0), "rough": 0.45,"metal": 0.0},
    "EM_M_FLOOR_INTERIOR_CAFE": {"color": (0.65, 0.65, 0.65, 1.0), "rough": 0.55,"metal": 0.0},
    "EM_M_FLOOR_EXTERNAL":      {"color": (0.60, 0.60, 0.58, 1.0), "rough": 0.85,"metal": 0.0},
    "EM_M_PATIO_RUBBER":        {"color": (0.55, 0.30, 0.28, 1.0), "rough": 0.9, "metal": 0.0},
    "EM_M_GRASS":               {"color": (0.33, 0.48, 0.26, 1.0), "rough": 0.95,"metal": 0.0},
    "EM_M_BASEBOARD":           {"color": (0.35, 0.35, 0.35, 1.0), "rough": 0.7, "metal": 0.0},
    "EM_M_THRESHOLD":           {"color": (0.94, 0.95, 0.96, 1.0), "rough": 0.35,"metal": 0.0},
    "EM_M_DOOR_WOOD":           {"color": (0.37, 0.24, 0.15, 1.0), "rough": 0.7, "metal": 0.0},
    "EM_M_DOOR_FRAME":          {"color": (0.92, 0.92, 0.92, 1.0), "rough": 0.5, "metal": 0.0},
    "EM_M_WINDOW_GLASS":        {"color": (0.36, 0.47, 0.52, 1.0), "rough": 0.1, "metal": 0.8}, # Vidro espelhado P19
    "EM_M_CEILING":             {"color": (0.95, 0.95, 0.95, 1.0), "rough": 0.9, "metal": 0.0},
    "EM_M_ROOF_TERRACOTTA":     {"color": (0.60, 0.35, 0.25, 1.0), "rough": 0.8, "metal": 0.0},
    "EM_M_CONCRETE":            {"color": (0.75, 0.75, 0.72, 1.0), "rough": 0.85,"metal": 0.0},
    "EM_M_GROUT":               {"color": (0.60, 0.60, 0.60, 1.0), "rough": 0.9, "metal": 0.0}
}

# ============================================================ #
# 2. ATUALIZAÇÃO E CRIAÇÃO DOS MATERIAIS
# ============================================================ #
def create_or_update_materials():
    for name, props in MATERIAL_LIBRARY.items():
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if not bsdf:
            bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
            out = next((n for n in mat.node_tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
            if out: mat.node_tree.links.new(bsdf.outputs[0], out.inputs[0])

        bsdf.inputs["Base Color"].default_value = props["color"]
        bsdf.inputs["Roughness"].default_value = props["rough"]
        bsdf.inputs["Metallic"].default_value = props["metal"]
        bsdf.inputs["Alpha"].default_value = 1.0
        
        mat.blend_method = "OPAQUE"
        mat.use_backface_culling = False
        
    print(f"[P20] {len(MATERIAL_LIBRARY)} materiais PBR criados/atualizados.")

# ============================================================ #
# 3. MAPEAMENTO E APLICAÇÃO AOS OBJETOS
# ============================================================ #
def apply_materials_to_school():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("Coleção EMERALD_GENERATED não encontrada.")
    
    applied = 0
    
    for obj in root.all_objects:
        if obj.type != 'MESH': continue
        name = obj.name
        
        target_mat_name = None
        
        # Mapeamento Lógico
        if name.startswith("WALL_"):
            # Paredes dos berçários e multiuso ganham a cor de destaque (Sage)
            if "BERC" in name or "MULTI" in name:
                target_mat_name = "EM_M_WALL_INTERIOR_ACCENT"
            else:
                target_mat_name = "EM_M_WALL_INTERIOR_MAIN"
                
        elif name.startswith("FLOOR_CORRIDOR"):
            target_mat_name = "EM_M_FLOOR_INTERIOR_CERAMIC"
        elif name.startswith("FLOOR_SPC_CLASS") or name.startswith("FLOOR_SPC_MULTI"):
            target_mat_name = "EM_M_FLOOR_INTERIOR_WOOD"
        elif name.startswith("FLOOR_SPC_BERC"):
            target_mat_name = "EM_M_FLOOR_INTERIOR_VINYL"
        elif name.startswith("FLOOR_SPC_WC") or name.startswith("FLOOR_SPC_KITCHEN"):
            target_mat_name = "EM_M_FLOOR_INTERIOR_WC"
        elif name.startswith("FLOOR_SPC_CAFE"):
            target_mat_name = "EM_M_FLOOR_INTERIOR_CAFE"
        elif name.startswith("FLOOR_PATIO") or name.startswith("SITE_ENTRY"):
            target_mat_name = "EM_M_PATIO_RUBBER" if "PATIO" in name else "EM_M_FLOOR_EXTERNAL"
        elif name.startswith("SITE_TERRAIN") or name.startswith("P06_GRASS"):
            target_mat_name = "EM_M_GRASS"
            
        elif name.startswith("P06_GROUT"):
            target_mat_name = "EM_M_GROUT"
        elif name.startswith("P06_SKIRT"):
            target_mat_name = "EM_M_BASEBOARD"
        elif name.startswith("P06_THRESH"):
            target_mat_name = "EM_M_THRESHOLD"
            
        elif name.startswith("DOOR_LEAF"):
            target_mat_name = "EM_M_DOOR_WOOD"
        elif name.startswith("FRAME_"):
            target_mat_name = "EM_M_DOOR_FRAME"
        elif name.endswith("_GLASS") or name.startswith("WINDOW"):
            target_mat_name = "EM_M_WINDOW_GLASS"
            
        elif name.startswith("CEIL_"):
            target_mat_name = "EM_M_CEILING"
        elif name.startswith("ROOF_"):
            target_mat_name = "EM_M_ROOF_TERRACOTTA"
        elif name.startswith("COLUMN_") or name.startswith("BEAM_"):
            target_mat_name = "EM_M_CONCRETE"

        # Aplicação
        if target_mat_name:
            mat = bpy.data.materials.get(target_mat_name)
            if mat:
                if len(obj.data.materials) > 0:
                    for i in range(len(obj.data.materials)):
                        obj.data.materials[i] = mat
                else:
                    obj.data.materials.append(mat)
                applied += 1
                
    print(f"[P20] Materiais aplicados a {applied} objetos.")

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
        export_lights=True,
        export_extras=True
    )
    print(f"[P20] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    create_or_update_materials()
    apply_materials_to_school()
    export_final()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P20] Blend salvo. Paleta natural aplicada.")